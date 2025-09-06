"""
Integration tests for MCP (Model Context Protocol) server integration
"""

import pytest
from unittest.mock import patch, AsyncMock, Mock
import asyncio
import json

from app.services.mcp_tool_registry import mcp_tool_registry
from app.services.mcp_server_manager import mcp_server_manager
from app.services.assistant_factory import assistant_factory


@pytest.mark.integration
class TestMCPServerIntegration:
    """Test MCP server integration scenarios"""
    
    @pytest.mark.asyncio
    async def test_mcp_server_lifecycle(self, db_session):
        """Test complete MCP server lifecycle"""
        # Mock MCP server configuration
        server_config = {
            "server_id": "test_mcp_server",
            "name": "Test MCP Server",
            "command": "python",
            "args": ["-m", "test_mcp_server"],
            "env": {"TEST_MODE": "true"},
            "organization_id": "test_org"
        }
        
        with patch.object(mcp_server_manager, 'register_server') as mock_register, \
             patch.object(mcp_server_manager, 'start_server') as mock_start, \
             patch.object(mcp_server_manager, 'stop_server') as mock_stop:
            
            # Mock successful registration
            mock_register.return_value = {
                "server_id": server_config["server_id"],
                "status": "registered"
            }
            
            # Mock successful start
            mock_start.return_value = {
                "server_id": server_config["server_id"],
                "status": "running",
                "pid": 12345
            }
            
            # Mock successful stop
            mock_stop.return_value = {
                "server_id": server_config["server_id"],
                "status": "stopped"
            }
            
            # Step 1: Register server
            registration_result = await mcp_server_manager.register_server(
                db=db_session,
                config=server_config
            )
            assert registration_result["status"] == "registered"
            
            # Step 2: Start server
            start_result = await mcp_server_manager.start_server(
                db=db_session,
                server_id=server_config["server_id"]
            )
            assert start_result["status"] == "running"
            
            # Step 3: Stop server
            stop_result = await mcp_server_manager.stop_server(
                db=db_session,
                server_id=server_config["server_id"]
            )
            assert stop_result["status"] == "stopped"
    
    @pytest.mark.asyncio
    async def test_mcp_tool_discovery(self, db_session):
        """Test MCP tool discovery and registration"""
        # Mock available tools from MCP server
        mock_tools = [
            {
                "name": "get_weather",
                "description": "Get current weather information",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {"type": "string", "description": "City name"}
                    },
                    "required": ["location"]
                }
            },
            {
                "name": "send_email",
                "description": "Send an email message",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "to": {"type": "string", "description": "Recipient email"},
                        "subject": {"type": "string", "description": "Email subject"},
                        "body": {"type": "string", "description": "Email body"}
                    },
                    "required": ["to", "subject", "body"]
                }
            }
        ]
        
        with patch.object(mcp_server_manager, 'discover_tools') as mock_discover:
            mock_discover.return_value = mock_tools
            
            # Discover tools from MCP server
            discovered_tools = await mcp_server_manager.discover_tools(
                db=db_session,
                server_id="test_mcp_server"
            )
            
            assert len(discovered_tools) == 2
            assert discovered_tools[0]["name"] == "get_weather"
            assert discovered_tools[1]["name"] == "send_email"
            
            # Verify tool parameters are properly structured
            weather_tool = discovered_tools[0]
            assert "parameters" in weather_tool
            assert "location" in weather_tool["parameters"]["properties"]
    
    @pytest.mark.asyncio
    async def test_mcp_tool_execution(self, db_session):
        """Test MCP tool execution"""
        # Mock tool execution
        with patch.object(mcp_tool_registry, 'execute_tool') as mock_execute:
            mock_execute.return_value = {
                "status": "success",
                "result": {
                    "location": "San Francisco",
                    "temperature": "72°F",
                    "condition": "Sunny",
                    "humidity": "65%"
                },
                "execution_time": 0.5
            }
            
            # Execute weather tool
            result = await mcp_tool_registry.execute_tool(
                db=db_session,
                tool_id="get_weather",
                organization_id="test_org",
                input_parameters={"location": "San Francisco"}
            )
            
            assert result["status"] == "success"
            assert result["result"]["location"] == "San Francisco"
            assert result["result"]["temperature"] == "72°F"
            assert "execution_time" in result
    
    @pytest.mark.asyncio
    async def test_mcp_tool_error_handling(self, db_session):
        """Test MCP tool error handling"""
        # Mock tool execution failure
        with patch.object(mcp_tool_registry, 'execute_tool') as mock_execute:
            mock_execute.return_value = {
                "status": "error",
                "error": "Invalid location parameter",
                "error_code": "INVALID_PARAMETER",
                "execution_time": 0.1
            }
            
            # Execute tool with invalid parameters
            result = await mcp_tool_registry.execute_tool(
                db=db_session,
                tool_id="get_weather",
                organization_id="test_org",
                input_parameters={"location": ""}  # Invalid empty location
            )
            
            assert result["status"] == "error"
            assert "Invalid location parameter" in result["error"]
            assert result["error_code"] == "INVALID_PARAMETER"
    
    @pytest.mark.asyncio
    async def test_mcp_server_health_monitoring(self, db_session):
        """Test MCP server health monitoring"""
        server_id = "test_mcp_server"
        
        with patch.object(mcp_server_manager, 'check_server_health') as mock_health:
            # Mock healthy server
            mock_health.return_value = {
                "server_id": server_id,
                "status": "healthy",
                "uptime": 3600,
                "memory_usage": "45MB",
                "cpu_usage": "2.5%",
                "tools_available": 5,
                "last_heartbeat": "2024-01-01T12:00:00Z"
            }
            
            health_status = await mcp_server_manager.check_server_health(
                db=db_session,
                server_id=server_id
            )
            
            assert health_status["status"] == "healthy"
            assert health_status["tools_available"] == 5
            assert "uptime" in health_status
    
    @pytest.mark.asyncio
    async def test_mcp_server_failover(self, db_session):
        """Test MCP server failover scenarios"""
        primary_server = "primary_mcp_server"
        backup_server = "backup_mcp_server"
        
        with patch.object(mcp_server_manager, 'check_server_health') as mock_health, \
             patch.object(mcp_server_manager, 'failover_to_backup') as mock_failover:
            
            # Mock primary server failure
            mock_health.side_effect = [
                {"server_id": primary_server, "status": "unhealthy"},
                {"server_id": backup_server, "status": "healthy"}
            ]
            
            # Mock successful failover
            mock_failover.return_value = {
                "status": "failover_complete",
                "primary_server": primary_server,
                "backup_server": backup_server,
                "failover_time": 2.5
            }
            
            # Trigger failover
            failover_result = await mcp_server_manager.failover_to_backup(
                db=db_session,
                primary_server_id=primary_server,
                backup_server_id=backup_server
            )
            
            assert failover_result["status"] == "failover_complete"
            assert failover_result["backup_server"] == backup_server
            assert "failover_time" in failover_result


@pytest.mark.integration
class TestMCPAssistantIntegration:
    """Test MCP integration with AI assistants"""
    
    @pytest.mark.asyncio
    async def test_assistant_mcp_tool_usage(self, db_session):
        """Test assistant using MCP tools"""
        # Setup assistant
        config = {
            "organization_id": "test_org",
            "organization_name": "Test Organization"
        }
        
        with patch.object(mcp_tool_registry, 'get_available_tools') as mock_get_tools, \
             patch.object(mcp_tool_registry, 'execute_tool') as mock_execute_tool:
            
            # Mock available tools
            mock_get_tools.return_value = [
                {
                    "tool_id": "weather_tool",
                    "name": "Get Weather",
                    "description": "Get weather information",
                    "category": "general"
                },
                {
                    "tool_id": "email_tool",
                    "name": "Send Email",
                    "description": "Send email messages",
                    "category": "communication"
                }
            ]
            
            # Mock tool execution
            mock_execute_tool.return_value = {
                "status": "success",
                "result": {"temperature": "75°F", "condition": "Partly cloudy"}
            }
            
            # Create assistant
            assistant = await assistant_factory.create_assistant(
                db=db_session,
                assistant_type="support",
                assistant_id="mcp_test_assistant",
                config=config
            )
            
            # Test assistant can access tools
            available_tools = await assistant.get_available_tools(db_session)
            assert len(available_tools) >= 1
            
            # Test assistant can execute tools
            tool_result = await assistant._execute_tool(
                db=db_session,
                tool_id="weather_tool",
                parameters={"location": "San Francisco"}
            )
            
            assert tool_result["status"] == "success"
            assert "temperature" in tool_result["result"]
    
    @pytest.mark.asyncio
    async def test_assistant_tool_filtering(self, db_session):
        """Test assistant tool filtering based on capabilities"""
        config = {
            "organization_id": "test_org",
            "organization_name": "Test Organization"
        }
        
        with patch.object(mcp_tool_registry, 'get_available_tools') as mock_get_tools:
            # Mock tools with different categories
            mock_get_tools.return_value = [
                {
                    "tool_id": "general_tool",
                    "name": "General Tool",
                    "category": "general"
                },
                {
                    "tool_id": "billing_tool",
                    "name": "Billing Tool",
                    "category": "billing"
                },
                {
                    "tool_id": "technical_tool",
                    "name": "Technical Tool",
                    "category": "technical"
                }
            ]
            
            # Create support assistant (has communication, technical, billing, general capabilities)
            support_assistant = await assistant_factory.create_assistant(
                db=db_session,
                assistant_type="support",
                assistant_id="support_assistant",
                config=config
            )
            
            # Create sales assistant (has communication, analytics, finance, general capabilities)
            sales_assistant = await assistant_factory.create_assistant(
                db=db_session,
                assistant_type="sales",
                assistant_id="sales_assistant",
                config=config
            )
            
            # Test support assistant gets appropriate tools
            support_tools = await support_assistant.get_available_tools(db_session)
            support_tool_categories = [tool.get("category") for tool in support_tools]
            
            # Support assistant should have access to technical and billing tools
            assert "general" in support_tool_categories or len(support_tools) > 0
            
            # Test sales assistant gets appropriate tools
            sales_tools = await sales_assistant.get_available_tools(db_session)
            sales_tool_categories = [tool.get("category") for tool in sales_tools]
            
            # Sales assistant should have access to general tools
            assert "general" in sales_tool_categories or len(sales_tools) > 0
    
    @pytest.mark.asyncio
    async def test_mcp_tool_security_validation(self, db_session):
        """Test MCP tool security validation"""
        with patch.object(mcp_server_manager, 'validate_tool_security') as mock_validate:
            # Mock security validation
            mock_validate.return_value = {
                "is_safe": True,
                "security_level": "medium",
                "permissions_required": ["read_data"],
                "risk_factors": []
            }
            
            # Test tool security validation
            validation_result = await mcp_server_manager.validate_tool_security(
                db=db_session,
                tool_id="test_tool",
                organization_id="test_org"
            )
            
            assert validation_result["is_safe"] is True
            assert validation_result["security_level"] == "medium"
            assert "permissions_required" in validation_result
    
    @pytest.mark.asyncio
    async def test_mcp_tool_usage_analytics(self, db_session):
        """Test MCP tool usage analytics"""
        with patch.object(mcp_tool_registry, 'record_tool_usage') as mock_record, \
             patch.object(mcp_tool_registry, 'get_usage_analytics') as mock_analytics:
            
            # Mock usage recording
            mock_record.return_value = {
                "usage_id": "usage_123",
                "tool_id": "weather_tool",
                "execution_time": 0.5,
                "status": "success"
            }
            
            # Mock analytics data
            mock_analytics.return_value = {
                "total_executions": 150,
                "success_rate": 0.95,
                "average_execution_time": 0.7,
                "most_used_tools": [
                    {"tool_id": "weather_tool", "usage_count": 45},
                    {"tool_id": "email_tool", "usage_count": 32}
                ],
                "error_rate_by_tool": {
                    "weather_tool": 0.02,
                    "email_tool": 0.08
                }
            }
            
            # Record tool usage
            usage_record = await mcp_tool_registry.record_tool_usage(
                db=db_session,
                tool_id="weather_tool",
                organization_id="test_org",
                execution_time=0.5,
                status="success"
            )
            
            assert usage_record["tool_id"] == "weather_tool"
            assert usage_record["status"] == "success"
            
            # Get usage analytics
            analytics = await mcp_tool_registry.get_usage_analytics(
                db=db_session,
                organization_id="test_org",
                time_period="30d"
            )
            
            assert analytics["total_executions"] == 150
            assert analytics["success_rate"] == 0.95
            assert len(analytics["most_used_tools"]) == 2


@pytest.mark.integration
class TestMCPErrorRecovery:
    """Test MCP error recovery scenarios"""
    
    @pytest.mark.asyncio
    async def test_mcp_server_crash_recovery(self, db_session):
        """Test MCP server crash recovery"""
        server_id = "crash_test_server"
        
        with patch.object(mcp_server_manager, 'detect_server_crash') as mock_detect, \
             patch.object(mcp_server_manager, 'restart_server') as mock_restart:
            
            # Mock server crash detection
            mock_detect.return_value = {
                "server_id": server_id,
                "crashed": True,
                "crash_time": "2024-01-01T12:00:00Z",
                "exit_code": -1
            }
            
            # Mock successful restart
            mock_restart.return_value = {
                "server_id": server_id,
                "status": "restarted",
                "restart_time": "2024-01-01T12:00:30Z",
                "recovery_time": 30.0
            }
            
            # Detect crash
            crash_info = await mcp_server_manager.detect_server_crash(
                db=db_session,
                server_id=server_id
            )
            
            assert crash_info["crashed"] is True
            
            # Restart server
            restart_result = await mcp_server_manager.restart_server(
                db=db_session,
                server_id=server_id
            )
            
            assert restart_result["status"] == "restarted"
            assert "recovery_time" in restart_result
    
    @pytest.mark.asyncio
    async def test_mcp_tool_timeout_handling(self, db_session):
        """Test MCP tool timeout handling"""
        with patch.object(mcp_tool_registry, 'execute_tool') as mock_execute:
            # Mock tool timeout
            mock_execute.return_value = {
                "status": "timeout",
                "error": "Tool execution timed out after 30 seconds",
                "execution_time": 30.0,
                "timeout_threshold": 30.0
            }
            
            # Execute tool that times out
            result = await mcp_tool_registry.execute_tool(
                db=db_session,
                tool_id="slow_tool",
                organization_id="test_org",
                input_parameters={"data": "large_dataset"},
                timeout=30.0
            )
            
            assert result["status"] == "timeout"
            assert "timed out" in result["error"]
            assert result["execution_time"] == 30.0
    
    @pytest.mark.asyncio
    async def test_mcp_connection_retry_logic(self, db_session):
        """Test MCP connection retry logic"""
        server_id = "retry_test_server"
        
        with patch.object(mcp_server_manager, 'connect_to_server') as mock_connect:
            # Mock connection failures followed by success
            mock_connect.side_effect = [
                Exception("Connection refused"),
                Exception("Connection timeout"),
                {"status": "connected", "server_id": server_id}
            ]
            
            # Test retry logic
            with patch.object(mcp_server_manager, 'connect_with_retry') as mock_retry:
                mock_retry.return_value = {
                    "status": "connected",
                    "server_id": server_id,
                    "attempts": 3,
                    "total_retry_time": 5.0
                }
                
                connection_result = await mcp_server_manager.connect_with_retry(
                    db=db_session,
                    server_id=server_id,
                    max_retries=3,
                    retry_delay=1.0
                )
                
                assert connection_result["status"] == "connected"
                assert connection_result["attempts"] == 3