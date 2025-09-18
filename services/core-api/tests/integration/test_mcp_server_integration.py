"""
MCP Server Integration Tests
Tests integration with Model Context Protocol servers and tool execution
"""

import pytest
from unittest.mock import patch, AsyncMock, Mock
from sqlalchemy.orm import Session

from app.services.mcp_server_manager import mcp_server_manager
from app.services.mcp_tool_registry import mcp_tool_registry
from app.models.user import Organization


class TestMCPServerManager:
    """Test MCP server management and lifecycle"""
    
    @pytest.mark.asyncio
    async def test_register_mcp_server(self, test_db_session: Session):
        """Test registering a new MCP server"""
        server_config = {
            "server_id": "stripe_server",
            "name": "Stripe MCP Server",
            "description": "Stripe billing and payment operations",
            "command": "uvx",
            "args": ["stripe-mcp-server@latest"],
            "env": {"STRIPE_API_KEY": "sk_test_123"},
            "capabilities": ["billing", "payments", "subscriptions"],
            "security_level": "high"
        }
        
        result = await mcp_server_manager.register_server(
            db=test_db_session,
            config=server_config
        )
        
        assert result["status"] == "registered"
        assert result["server_id"] == "stripe_server"
        assert "health_check_url" in result
    
    @pytest.mark.asyncio
    async def test_start_mcp_server(self, test_db_session: Session):
        """Test starting an MCP server"""
        server_id = "stripe_server"
        
        with patch('app.services.mcp_server_manager.subprocess') as mock_subprocess:
            mock_process = Mock()
            mock_process.pid = 12345
            mock_process.poll.return_value = None  # Process is running
            mock_subprocess.Popen.return_value = mock_process
            
            result = await mcp_server_manager.start_server(
                db=test_db_session,
                server_id=server_id
            )
            
            assert result["status"] == "started"
            assert result["pid"] == 12345
    
    @pytest.mark.asyncio
    async def test_server_health_monitoring(self, test_db_session: Session):
        """Test MCP server health monitoring"""
        server_id = "stripe_server"
        
        with patch('app.services.mcp_server_manager.httpx') as mock_httpx:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "status": "healthy",
                "tools": ["create_customer", "create_subscription"],
                "uptime": 3600
            }
            mock_httpx.get.return_value = mock_response
            
            result = await mcp_server_manager.check_server_health(
                db=test_db_session,
                server_id=server_id
            )
            
            assert result["status"] == "healthy"
            assert len(result["tools"]) == 2
            assert result["uptime"] == 3600
    
    @pytest.mark.asyncio
    async def test_server_auto_restart(self, test_db_session: Session):
        """Test automatic server restart on failure"""
        server_id = "stripe_server"
        
        with patch('app.services.mcp_server_manager.subprocess') as mock_subprocess, \
             patch('app.services.mcp_server_manager.check_server_health') as mock_health:
            
            # Simulate server failure
            mock_health.return_value = {"status": "unhealthy", "error": "Connection refused"}
            
            # Mock restart
            mock_process = Mock()
            mock_process.pid = 12346
            mock_subprocess.Popen.return_value = mock_process
            
            result = await mcp_server_manager.handle_server_failure(
                db=test_db_session,
                server_id=server_id
            )
            
            assert result["action"] == "restarted"
            assert result["new_pid"] == 12346
    
    @pytest.mark.asyncio
    async def test_server_security_validation(self, test_db_session: Session):
        """Test MCP server security validation"""
        server_config = {
            "server_id": "test_server",
            "command": "python",
            "args": ["-c", "import os; os.system('rm -rf /')"],  # Malicious command
            "security_level": "high"
        }
        
        result = await mcp_server_manager.validate_server_security(
            config=server_config
        )
        
        assert result["valid"] is False
        assert "security_violation" in result["errors"]
    
    @pytest.mark.asyncio
    async def test_server_sandboxing(self, test_db_session: Session):
        """Test MCP server sandboxing and isolation"""
        server_id = "test_server"
        
        with patch('app.services.mcp_server_manager.docker') as mock_docker:
            mock_container = Mock()
            mock_container.id = "container_123"
            mock_docker.containers.run.return_value = mock_container
            
            result = await mcp_server_manager.start_sandboxed_server(
                db=test_db_session,
                server_id=server_id,
                sandbox_config={
                    "memory_limit": "512m",
                    "cpu_limit": "0.5",
                    "network_mode": "none"
                }
            )
            
            assert result["status"] == "sandboxed"
            assert result["container_id"] == "container_123"


class TestMCPToolRegistry:
    """Test MCP tool registry and execution"""
    
    @pytest.mark.asyncio
    async def test_discover_tools(self, test_db_session: Session):
        """Test discovering tools from MCP servers"""
        server_id = "stripe_server"
        
        with patch('app.services.mcp_tool_registry.mcp_client') as mock_client:
            mock_client.list_tools.return_value = {
                "tools": [
                    {
                        "name": "create_customer",
                        "description": "Create a new Stripe customer",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "email": {"type": "string"},
                                "name": {"type": "string"}
                            },
                            "required": ["email"]
                        }
                    },
                    {
                        "name": "create_subscription",
                        "description": "Create a new subscription",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "customer_id": {"type": "string"},
                                "price_id": {"type": "string"}
                            },
                            "required": ["customer_id", "price_id"]
                        }
                    }
                ]
            }
            
            result = await mcp_tool_registry.discover_tools(
                db=test_db_session,
                server_id=server_id
            )
            
            assert len(result["tools"]) == 2
            assert result["tools"][0]["name"] == "create_customer"
            assert "parameters" in result["tools"][0]
    
    @pytest.mark.asyncio
    async def test_execute_tool(self, test_db_session: Session):
        """Test executing an MCP tool"""
        # Create test organization
        org = Organization(
            name="Test Organization",
            domain="test.com",
            owner_id="test_user"
        )
        test_db_session.add(org)
        test_db_session.commit()
        
        tool_id = "stripe_create_customer"
        parameters = {
            "email": "test@example.com",
            "name": "Test Customer"
        }
        
        with patch('app.services.mcp_tool_registry.mcp_client') as mock_client:
            mock_client.call_tool.return_value = {
                "result": {
                    "id": "cus_test123",
                    "email": "test@example.com",
                    "name": "Test Customer",
                    "created": 1642694400
                }
            }
            
            result = await mcp_tool_registry.execute_tool(
                db=test_db_session,
                tool_id=tool_id,
                organization_id=org.id,
                input_parameters=parameters,
                user_id="test_user"
            )
            
            assert result["status"] == "success"
            assert result["result"]["id"] == "cus_test123"
            assert result["result"]["email"] == "test@example.com"
    
    @pytest.mark.asyncio
    async def test_tool_parameter_validation(self, test_db_session: Session):
        """Test tool parameter validation"""
        tool_schema = {
            "name": "create_customer",
            "parameters": {
                "type": "object",
                "properties": {
                    "email": {"type": "string", "format": "email"},
                    "name": {"type": "string", "minLength": 1}
                },
                "required": ["email"]
            }
        }
        
        # Valid parameters
        valid_params = {"email": "test@example.com", "name": "Test User"}
        result = await mcp_tool_registry.validate_parameters(tool_schema, valid_params)
        assert result["valid"] is True
        
        # Invalid parameters - missing required field
        invalid_params = {"name": "Test User"}
        result = await mcp_tool_registry.validate_parameters(tool_schema, invalid_params)
        assert result["valid"] is False
        assert "email" in result["errors"]
        
        # Invalid parameters - wrong format
        invalid_format_params = {"email": "not-an-email", "name": "Test User"}
        result = await mcp_tool_registry.validate_parameters(tool_schema, invalid_format_params)
        assert result["valid"] is False
        assert "format" in str(result["errors"])
    
    @pytest.mark.asyncio
    async def test_tool_execution_caching(self, test_db_session: Session):
        """Test tool result caching"""
        tool_id = "stripe_get_customer"
        parameters = {"customer_id": "cus_test123"}
        cache_key = f"{tool_id}:{hash(str(parameters))}"
        
        with patch('app.services.mcp_tool_registry.redis_client') as mock_redis, \
             patch('app.services.mcp_tool_registry.mcp_client') as mock_client:
            
            # First call - cache miss
            mock_redis.get.return_value = None
            mock_client.call_tool.return_value = {
                "result": {"id": "cus_test123", "email": "test@example.com"}
            }
            
            result1 = await mcp_tool_registry.execute_tool_with_cache(
                db=test_db_session,
                tool_id=tool_id,
                parameters=parameters,
                cache_ttl=300
            )
            
            # Verify result was cached
            mock_redis.setex.assert_called_once()
            
            # Second call - cache hit
            mock_redis.get.return_value = '{"id": "cus_test123", "email": "test@example.com"}'
            
            result2 = await mcp_tool_registry.execute_tool_with_cache(
                db=test_db_session,
                tool_id=tool_id,
                parameters=parameters,
                cache_ttl=300
            )
            
            assert result1["result"] == result2["result"]
            # MCP client should only be called once
            mock_client.call_tool.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_tool_usage_analytics(self, test_db_session: Session):
        """Test tool usage analytics and tracking"""
        org = Organization(
            name="Test Organization",
            domain="test.com",
            owner_id="test_user"
        )
        test_db_session.add(org)
        test_db_session.commit()
        
        tool_id = "stripe_create_customer"
        
        with patch('app.services.mcp_tool_registry.analytics_service') as mock_analytics:
            await mcp_tool_registry.track_tool_usage(
                db=test_db_session,
                tool_id=tool_id,
                organization_id=org.id,
                user_id="test_user",
                execution_time=1.5,
                success=True,
                cost=0.001
            )
            
            mock_analytics.record_event.assert_called_once()
            call_args = mock_analytics.record_event.call_args[1]
            assert call_args["event_type"] == "tool_execution"
            assert call_args["tool_id"] == tool_id
            assert call_args["execution_time"] == 1.5
    
    @pytest.mark.asyncio
    async def test_tool_cost_tracking(self, test_db_session: Session):
        """Test tool execution cost tracking"""
        org = Organization(
            name="Test Organization",
            domain="test.com",
            owner_id="test_user"
        )
        test_db_session.add(org)
        test_db_session.commit()
        
        with patch('app.services.mcp_tool_registry.billing_service') as mock_billing:
            await mcp_tool_registry.track_tool_costs(
                db=test_db_session,
                organization_id=org.id,
                tool_executions=[
                    {"tool_id": "stripe_create_customer", "cost": 0.001},
                    {"tool_id": "gmail_send_email", "cost": 0.0005},
                    {"tool_id": "calendar_create_event", "cost": 0.0002}
                ]
            )
            
            mock_billing.add_usage_charges.assert_called_once()
            call_args = mock_billing.add_usage_charges.call_args[1]
            assert call_args["total_cost"] == 0.0017


class TestMCPServerIntegrations:
    """Test specific MCP server integrations"""
    
    @pytest.mark.asyncio
    async def test_stripe_mcp_integration(self, test_db_session: Session):
        """Test Stripe MCP server integration"""
        with patch('app.services.mcp_tool_registry.mcp_client') as mock_client:
            # Test customer creation
            mock_client.call_tool.return_value = {
                "result": {
                    "id": "cus_test123",
                    "email": "test@example.com",
                    "created": 1642694400
                }
            }
            
            result = await mcp_tool_registry.execute_tool(
                db=test_db_session,
                tool_id="stripe_create_customer",
                organization_id="org_123",
                input_parameters={"email": "test@example.com"},
                user_id="user_123"
            )
            
            assert result["status"] == "success"
            assert result["result"]["id"].startswith("cus_")
    
    @pytest.mark.asyncio
    async def test_xero_mcp_integration(self, test_db_session: Session):
        """Test Xero MCP server integration for Australian accounting"""
        with patch('app.services.mcp_tool_registry.mcp_client') as mock_client:
            # Test invoice creation
            mock_client.call_tool.return_value = {
                "result": {
                    "InvoiceID": "inv_test123",
                    "InvoiceNumber": "INV-001",
                    "Status": "DRAFT",
                    "Total": 100.00,
                    "CurrencyCode": "AUD"
                }
            }
            
            result = await mcp_tool_registry.execute_tool(
                db=test_db_session,
                tool_id="xero_create_invoice",
                organization_id="org_123",
                input_parameters={
                    "contact_id": "contact_123",
                    "line_items": [{"description": "Service", "amount": 100.00}]
                },
                user_id="user_123"
            )
            
            assert result["status"] == "success"
            assert result["result"]["CurrencyCode"] == "AUD"
    
    @pytest.mark.asyncio
    async def test_slack_mcp_integration(self, test_db_session: Session):
        """Test Slack MCP server integration"""
        with patch('app.services.mcp_tool_registry.mcp_client') as mock_client:
            # Test message sending
            mock_client.call_tool.return_value = {
                "result": {
                    "ok": True,
                    "channel": "C1234567890",
                    "ts": "1642694400.123456",
                    "message": {
                        "text": "Hello from AI Assistant!",
                        "user": "U1234567890"
                    }
                }
            }
            
            result = await mcp_tool_registry.execute_tool(
                db=test_db_session,
                tool_id="slack_send_message",
                organization_id="org_123",
                input_parameters={
                    "channel": "#general",
                    "text": "Hello from AI Assistant!"
                },
                user_id="user_123"
            )
            
            assert result["status"] == "success"
            assert result["result"]["ok"] is True
    
    @pytest.mark.asyncio
    async def test_googleapis_genai_toolbox_integration(self, test_db_session: Session):
        """Test googleapis/genai-toolbox MCP integration"""
        with patch('app.services.mcp_tool_registry.mcp_client') as mock_client:
            # Test Google Calendar event creation
            mock_client.call_tool.return_value = {
                "result": {
                    "id": "event_123",
                    "summary": "Team Meeting",
                    "start": {"dateTime": "2024-01-15T14:00:00Z"},
                    "end": {"dateTime": "2024-01-15T15:00:00Z"},
                    "attendees": [{"email": "john@example.com"}]
                }
            }
            
            result = await mcp_tool_registry.execute_tool(
                db=test_db_session,
                tool_id="google_calendar_create_event",
                organization_id="org_123",
                input_parameters={
                    "summary": "Team Meeting",
                    "start_time": "2024-01-15T14:00:00Z",
                    "end_time": "2024-01-15T15:00:00Z",
                    "attendees": ["john@example.com"]
                },
                user_id="user_123"
            )
            
            assert result["status"] == "success"
            assert result["result"]["summary"] == "Team Meeting"


class TestMCPErrorHandling:
    """Test MCP server error handling and recovery"""
    
    @pytest.mark.asyncio
    async def test_server_connection_failure(self, test_db_session: Session):
        """Test handling MCP server connection failures"""
        with patch('app.services.mcp_tool_registry.mcp_client') as mock_client:
            mock_client.call_tool.side_effect = ConnectionError("Connection refused")
            
            result = await mcp_tool_registry.execute_tool(
                db=test_db_session,
                tool_id="stripe_create_customer",
                organization_id="org_123",
                input_parameters={"email": "test@example.com"},
                user_id="user_123"
            )
            
            assert result["status"] == "error"
            assert "connection" in result["error"].lower()
    
    @pytest.mark.asyncio
    async def test_tool_execution_timeout(self, test_db_session: Session):
        """Test handling tool execution timeouts"""
        with patch('app.services.mcp_tool_registry.mcp_client') as mock_client:
            mock_client.call_tool.side_effect = TimeoutError("Tool execution timeout")
            
            result = await mcp_tool_registry.execute_tool_with_timeout(
                db=test_db_session,
                tool_id="slow_tool",
                parameters={},
                timeout=5.0
            )
            
            assert result["status"] == "timeout"
            assert result["timeout_duration"] == 5.0
    
    @pytest.mark.asyncio
    async def test_server_rate_limiting(self, test_db_session: Session):
        """Test handling server rate limiting"""
        with patch('app.services.mcp_tool_registry.mcp_client') as mock_client:
            mock_client.call_tool.side_effect = Exception("Rate limit exceeded")
            
            result = await mcp_tool_registry.handle_rate_limit(
                db=test_db_session,
                server_id="stripe_server",
                retry_after=60
            )
            
            assert result["status"] == "rate_limited"
            assert result["retry_after"] == 60
    
    @pytest.mark.asyncio
    async def test_tool_result_validation(self, test_db_session: Session):
        """Test validation of tool execution results"""
        with patch('app.services.mcp_tool_registry.mcp_client') as mock_client:
            # Invalid result format
            mock_client.call_tool.return_value = {
                "invalid_key": "invalid_result"
            }
            
            result = await mcp_tool_registry.execute_tool_with_validation(
                db=test_db_session,
                tool_id="stripe_create_customer",
                parameters={"email": "test@example.com"},
                expected_schema={
                    "type": "object",
                    "properties": {
                        "result": {"type": "object"}
                    },
                    "required": ["result"]
                }
            )
            
            assert result["status"] == "validation_error"
            assert "schema" in result["error"]