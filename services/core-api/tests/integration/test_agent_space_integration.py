"""
Agent Space Integration Tests
Tests integration with Google Agent Space and Vertex AI Agent Builder
"""

import pytest
from unittest.mock import patch, AsyncMock, Mock
from sqlalchemy.orm import Session

from app.services.agent_space_connector_manager import agent_space_connector_manager
from app.services.hybrid_agent_orchestrator import hybrid_agent_orchestrator
from app.models.user import Organization, Assistant


class TestAgentSpaceConnectorManager:
    """Test Agent Space connector management"""
    
    @pytest.mark.asyncio
    async def test_initialize_agent(self, test_db_session: Session):
        """Test initializing an Agent Space agent"""
        # Create test organization
        org = Organization(
            name="Test Organization",
            domain="test.com",
            owner_id="test_user"
        )
        test_db_session.add(org)
        test_db_session.commit()
        
        agent_config = {
            "agent_type": "support",
            "connectors": ["gmail", "google_calendar"],
            "capabilities": ["email_management", "calendar_scheduling"],
            "tools": ["send_email", "create_calendar_event"]
        }
        
        with patch('app.services.agent_space_connector_manager.vertex_ai_client') as mock_client:
            mock_client.create_agent.return_value = {
                "name": "projects/test/locations/us-central1/agents/agent123",
                "displayName": "Test Support Agent",
                "defaultLanguageCode": "en"
            }
            
            result = await agent_space_connector_manager.initialize_agent(
                db=test_db_session,
                agent_id="test_agent",
                config=agent_config
            )
            
            assert result["status"] == "success"
            assert "agent_name" in result
            assert result["agent_type"] == "support"
    
    @pytest.mark.asyncio
    async def test_configure_connectors(self, test_db_session: Session):
        """Test configuring Google service connectors"""
        connector_config = {
            "gmail": {
                "scopes": ["https://www.googleapis.com/auth/gmail.readonly"],
                "credentials": "test_credentials"
            },
            "google_calendar": {
                "scopes": ["https://www.googleapis.com/auth/calendar"],
                "credentials": "test_credentials"
            }
        }
        
        with patch('app.services.agent_space_connector_manager.google_auth') as mock_auth:
            mock_auth.configure_connector.return_value = {
                "status": "configured",
                "connector_id": "conn_123"
            }
            
            result = await agent_space_connector_manager.configure_connectors(
                db=test_db_session,
                agent_id="test_agent",
                connectors=connector_config
            )
            
            assert result["status"] == "success"
            assert len(result["configured_connectors"]) == 2
    
    @pytest.mark.asyncio
    async def test_process_message_with_agent_space(self, test_db_session: Session):
        """Test processing message through Agent Space"""
        message = "Schedule a meeting with John tomorrow at 2pm"
        context = {
            "conversation_id": "conv_123",
            "user_id": "user_123",
            "organization_id": "org_123"
        }
        
        with patch('app.services.agent_space_connector_manager.vertex_ai_client') as mock_client:
            mock_client.converse.return_value = {
                "response": {
                    "text": "I've scheduled a meeting with John for tomorrow at 2pm. Calendar invite sent.",
                    "actions": [
                        {
                            "type": "calendar_event_created",
                            "event_id": "event_123",
                            "participants": ["john@example.com"]
                        }
                    ]
                }
            }
            
            result = await agent_space_connector_manager.process_message(
                db=test_db_session,
                agent_id="test_agent",
                message=message,
                context=context
            )
            
            assert result["response"] is not None
            assert "actions" in result
            assert len(result["actions"]) == 1
    
    @pytest.mark.asyncio
    async def test_connector_health_monitoring(self, test_db_session: Session):
        """Test connector health monitoring"""
        with patch('app.services.agent_space_connector_manager.google_auth') as mock_auth:
            mock_auth.check_connector_health.return_value = {
                "gmail": {"status": "healthy", "last_check": "2024-01-15T10:00:00Z"},
                "google_calendar": {"status": "error", "error": "Authentication expired"}
            }
            
            result = await agent_space_connector_manager.check_connector_health(
                db=test_db_session,
                agent_id="test_agent"
            )
            
            assert "gmail" in result
            assert "google_calendar" in result
            assert result["gmail"]["status"] == "healthy"
            assert result["google_calendar"]["status"] == "error"
    
    @pytest.mark.asyncio
    async def test_connector_failover(self, test_db_session: Session):
        """Test automatic connector failover"""
        with patch('app.services.agent_space_connector_manager.google_auth') as mock_auth, \
             patch('app.services.agent_space_connector_manager.vertex_ai_service') as mock_vertex:
            
            # Simulate connector failure
            mock_auth.send_email.side_effect = Exception("Gmail connector failed")
            
            # Fallback to Vertex AI
            mock_vertex.generate_response = AsyncMock(return_value={
                "content": "I'll help you with that email request.",
                "metadata": {"fallback": True}
            })
            
            result = await agent_space_connector_manager.process_message(
                db=test_db_session,
                agent_id="test_agent",
                message="Send an email to john@example.com",
                context={"fallback_enabled": True}
            )
            
            assert result["response"] is not None
            assert result["metadata"]["fallback"] is True


class TestHybridAgentOrchestrator:
    """Test hybrid agent orchestration between Agent Space and custom workflows"""
    
    @pytest.mark.asyncio
    async def test_register_workflow(self, test_db_session: Session):
        """Test registering custom LangGraph workflow"""
        workflow_config = {
            "workflow_id": "content_generation",
            "workflow_type": "content_processing",
            "steps": [
                {"step_id": "analyze", "type": "analysis"},
                {"step_id": "generate", "type": "generation"},
                {"step_id": "review", "type": "quality_check"}
            ],
            "tools": ["content_analyzer", "content_generator", "quality_checker"]
        }
        
        result = await hybrid_agent_orchestrator.register_workflow(
            db=test_db_session,
            workflow_config=workflow_config
        )
        
        assert result["status"] == "registered"
        assert result["workflow_id"] == "content_generation"
    
    @pytest.mark.asyncio
    async def test_route_to_agent_space(self, test_db_session: Session):
        """Test routing request to Agent Space"""
        request = {
            "message": "Schedule a meeting with the team",
            "context": {"assistant_type": "admin"},
            "capabilities_required": ["calendar_management"]
        }
        
        with patch('app.services.hybrid_agent_orchestrator.agent_space_connector_manager') as mock_manager:
            mock_manager.process_message = AsyncMock(return_value={
                "response": "Meeting scheduled for tomorrow at 10am",
                "actions": [{"type": "calendar_event", "event_id": "evt_123"}]
            })
            
            result = await hybrid_agent_orchestrator.route_request(
                db=test_db_session,
                request=request
            )
            
            assert result["routing_decision"] == "agent_space"
            assert result["response"] is not None
    
    @pytest.mark.asyncio
    async def test_route_to_custom_workflow(self, test_db_session: Session):
        """Test routing request to custom LangGraph workflow"""
        request = {
            "message": "Create a blog post about AI trends",
            "context": {"assistant_type": "content"},
            "capabilities_required": ["content_generation"]
        }
        
        # Register workflow first
        workflow_config = {
            "workflow_id": "content_generation",
            "workflow_type": "content_processing",
            "steps": [{"step_id": "generate", "type": "generation"}],
            "tools": ["content_generator"]
        }
        await hybrid_agent_orchestrator.register_workflow(test_db_session, workflow_config)
        
        with patch('app.services.hybrid_agent_orchestrator.langgraph_executor') as mock_executor:
            mock_executor.execute_workflow = AsyncMock(return_value={
                "generated_content": "AI trends are shaping the future...",
                "metadata": {"workflow": "content_generation"}
            })
            
            result = await hybrid_agent_orchestrator.route_request(
                db=test_db_session,
                request=request
            )
            
            assert result["routing_decision"] == "custom_workflow"
            assert result["generated_content"] is not None
    
    @pytest.mark.asyncio
    async def test_cross_agent_communication(self, test_db_session: Session):
        """Test communication between Agent Space and custom workflows"""
        # Simulate a complex request requiring both systems
        request = {
            "message": "Create a marketing email and schedule it to be sent tomorrow",
            "context": {"assistant_type": "content"},
            "capabilities_required": ["content_generation", "email_scheduling"]
        }
        
        with patch('app.services.hybrid_agent_orchestrator.langgraph_executor') as mock_workflow, \
             patch('app.services.hybrid_agent_orchestrator.agent_space_connector_manager') as mock_agent_space:
            
            # First: Generate content with custom workflow
            mock_workflow.execute_workflow = AsyncMock(return_value={
                "generated_content": "Marketing email content...",
                "metadata": {"workflow": "content_generation"}
            })
            
            # Second: Schedule email with Agent Space
            mock_agent_space.process_message = AsyncMock(return_value={
                "response": "Email scheduled for tomorrow at 9am",
                "actions": [{"type": "email_scheduled", "schedule_id": "sched_123"}]
            })
            
            result = await hybrid_agent_orchestrator.execute_multi_step_request(
                db=test_db_session,
                request=request
            )
            
            assert result["steps_completed"] == 2
            assert "generated_content" in result
            assert "email_scheduled" in [action["type"] for action in result["actions"]]
    
    @pytest.mark.asyncio
    async def test_shared_context_management(self, test_db_session: Session):
        """Test shared context management across systems"""
        context = {
            "conversation_id": "conv_123",
            "user_preferences": {"timezone": "PST", "language": "en"},
            "organization_settings": {"brand_voice": "professional"}
        }
        
        # Store context
        await hybrid_agent_orchestrator.store_shared_context(
            db=test_db_session,
            context_id="conv_123",
            context=context
        )
        
        # Retrieve context
        retrieved_context = await hybrid_agent_orchestrator.get_shared_context(
            db=test_db_session,
            context_id="conv_123"
        )
        
        assert retrieved_context["user_preferences"]["timezone"] == "PST"
        assert retrieved_context["organization_settings"]["brand_voice"] == "professional"
    
    @pytest.mark.asyncio
    async def test_workflow_execution_monitoring(self, test_db_session: Session):
        """Test monitoring workflow execution performance"""
        workflow_id = "test_workflow"
        
        with patch('app.services.hybrid_agent_orchestrator.performance_monitor') as mock_monitor:
            mock_monitor.start_execution.return_value = "exec_123"
            mock_monitor.end_execution.return_value = {
                "execution_time": 1.5,
                "tokens_used": 150,
                "success": True
            }
            
            result = await hybrid_agent_orchestrator.execute_workflow(
                db=test_db_session,
                workflow_id=workflow_id,
                input_data={"test": "data"}
            )
            
            assert "execution_metrics" in result
            assert result["execution_metrics"]["success"] is True


class TestAgentSpaceErrorHandling:
    """Test error handling and recovery for Agent Space integration"""
    
    @pytest.mark.asyncio
    async def test_agent_space_timeout_handling(self, test_db_session: Session):
        """Test handling Agent Space API timeouts"""
        with patch('app.services.agent_space_connector_manager.vertex_ai_client') as mock_client:
            mock_client.converse.side_effect = TimeoutError("Agent Space timeout")
            
            result = await agent_space_connector_manager.process_message(
                db=test_db_session,
                agent_id="test_agent",
                message="Test message",
                context={"timeout_handling": True}
            )
            
            assert result["status"] == "timeout"
            assert "fallback_response" in result
    
    @pytest.mark.asyncio
    async def test_connector_authentication_failure(self, test_db_session: Session):
        """Test handling connector authentication failures"""
        with patch('app.services.agent_space_connector_manager.google_auth') as mock_auth:
            mock_auth.refresh_token.side_effect = Exception("Authentication failed")
            
            result = await agent_space_connector_manager.handle_auth_failure(
                db=test_db_session,
                agent_id="test_agent",
                connector="gmail"
            )
            
            assert result["status"] == "auth_failed"
            assert result["action"] == "reauth_required"
    
    @pytest.mark.asyncio
    async def test_quota_exceeded_handling(self, test_db_session: Session):
        """Test handling API quota exceeded errors"""
        with patch('app.services.agent_space_connector_manager.vertex_ai_client') as mock_client:
            mock_client.converse.side_effect = Exception("Quota exceeded")
            
            result = await agent_space_connector_manager.handle_quota_exceeded(
                db=test_db_session,
                agent_id="test_agent"
            )
            
            assert result["status"] == "quota_exceeded"
            assert result["retry_after"] is not None
    
    @pytest.mark.asyncio
    async def test_graceful_degradation(self, test_db_session: Session):
        """Test graceful degradation when Agent Space is unavailable"""
        with patch('app.services.hybrid_agent_orchestrator.agent_space_connector_manager') as mock_manager, \
             patch('app.services.hybrid_agent_orchestrator.vertex_ai_service') as mock_vertex:
            
            # Simulate Agent Space unavailable
            mock_manager.process_message.side_effect = Exception("Service unavailable")
            
            # Fallback to Vertex AI
            mock_vertex.generate_response = AsyncMock(return_value={
                "content": "I'm currently operating in limited mode but can still help you.",
                "metadata": {"degraded_mode": True}
            })
            
            request = {
                "message": "Help me with scheduling",
                "context": {"assistant_type": "admin"},
                "fallback_enabled": True
            }
            
            result = await hybrid_agent_orchestrator.route_request(
                db=test_db_session,
                request=request
            )
            
            assert result["routing_decision"] == "fallback"
            assert result["metadata"]["degraded_mode"] is True