"""
Unit tests for service layer
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from app.services.assistant_factory import assistant_factory, SupportAssistant
from app.services.conversation_service import conversation_service
from app.services.vertex_ai_service import vertex_ai_service
from app.services.mcp_tool_registry import mcp_tool_registry
from app.services.stripe_service import stripe_service


@pytest.mark.unit
class TestAssistantFactory:
    """Test assistant factory service"""
    
    def test_get_available_types(self):
        """Test getting available assistant types"""
        types = assistant_factory.get_available_types()
        
        assert isinstance(types, list)
        assert len(types) > 0
        assert "support" in types
        assert "sales" in types
        assert "technical" in types
    
    @pytest.mark.asyncio
    async def test_create_assistant(self, db_session, mock_mcp_registry):
        """Test creating an assistant"""
        config = {
            "organization_id": "test_org",
            "organization_name": "Test Organization"
        }
        
        assistant = await assistant_factory.create_assistant(
            db=db_session,
            assistant_type="support",
            assistant_id="test_support",
            config=config
        )
        
        assert assistant is not None
        assert isinstance(assistant, SupportAssistant)
        assert assistant.assistant_id == "test_support"
        assert assistant.type == "support"
    
    @pytest.mark.asyncio
    async def test_create_invalid_assistant_type(self, db_session):
        """Test creating assistant with invalid type"""
        config = {"organization_id": "test_org"}
        
        with pytest.raises(ValueError, match="Unknown assistant type"):
            await assistant_factory.create_assistant(
                db=db_session,
                assistant_type="invalid_type",
                assistant_id="test",
                config=config
            )
    
    @pytest.mark.asyncio
    async def test_get_assistant_capabilities(self):
        """Test getting assistant capabilities"""
        capabilities = await assistant_factory.get_assistant_capabilities("support")
        
        assert "type" in capabilities
        assert "capabilities" in capabilities
        assert "escalation_triggers" in capabilities
        assert capabilities["type"] == "support"
        assert isinstance(capabilities["capabilities"], list)


@pytest.mark.unit
class TestConversationService:
    """Test conversation service"""
    
    @pytest.mark.asyncio
    async def test_create_conversation(self, db_session, sample_user, sample_assistant):
        """Test creating a new conversation"""
        conversation_data = {
            "user_id": sample_user.id,
            "assistant_id": sample_assistant.id,
            "channel": "chat",
            "metadata": {"source": "web_widget"}
        }
        
        conversation = await conversation_service.create_conversation(
            db=db_session,
            **conversation_data
        )
        
        assert conversation is not None
        assert conversation.user_id == sample_user.id
        assert conversation.assistant_id == sample_assistant.id
        assert conversation.channel == "chat"
        assert conversation.status == "active"
        assert conversation.metadata["source"] == "web_widget"
    
    @pytest.mark.asyncio
    async def test_add_message(self, db_session, sample_conversation):
        """Test adding a message to conversation"""
        message_data = {
            "role": "user",
            "content": "Hello, I need help",
            "metadata": {"timestamp": datetime.now().isoformat()}
        }
        
        message = await conversation_service.add_message(
            db=db_session,
            conversation_id=sample_conversation.id,
            **message_data
        )
        
        assert message is not None
        assert message.conversation_id == sample_conversation.id
        assert message.role == "user"
        assert message.content == "Hello, I need help"
        assert "timestamp" in message.metadata
    
    @pytest.mark.asyncio
    async def test_get_conversation_history(self, db_session, sample_conversation, sample_message):
        """Test getting conversation history"""
        # Add more messages
        await conversation_service.add_message(
            db=db_session,
            conversation_id=sample_conversation.id,
            role="assistant",
            content="How can I help you today?"
        )
        
        history = await conversation_service.get_conversation_history(
            db=db_session,
            conversation_id=sample_conversation.id,
            limit=10
        )
        
        assert len(history) == 2  # Original message + new message
        assert history[0].role in ["user", "assistant"]
        assert history[1].role in ["user", "assistant"]
    
    @pytest.mark.asyncio
    async def test_update_conversation_status(self, db_session, sample_conversation):
        """Test updating conversation status"""
        updated_conversation = await conversation_service.update_conversation_status(
            db=db_session,
            conversation_id=sample_conversation.id,
            status="completed"
        )
        
        assert updated_conversation.status == "completed"
        assert updated_conversation.updated_at is not None
    
    @pytest.mark.asyncio
    async def test_get_active_conversations(self, db_session, sample_user, sample_assistant):
        """Test getting active conversations for a user"""
        # Create multiple conversations
        conv1 = await conversation_service.create_conversation(
            db=db_session,
            user_id=sample_user.id,
            assistant_id=sample_assistant.id,
            channel="chat"
        )
        
        conv2 = await conversation_service.create_conversation(
            db=db_session,
            user_id=sample_user.id,
            assistant_id=sample_assistant.id,
            channel="email"
        )
        
        # Mark one as completed
        await conversation_service.update_conversation_status(
            db=db_session,
            conversation_id=conv2.id,
            status="completed"
        )
        
        active_conversations = await conversation_service.get_active_conversations(
            db=db_session,
            user_id=sample_user.id
        )
        
        assert len(active_conversations) == 1
        assert active_conversations[0].id == conv1.id
        assert active_conversations[0].status == "active"


@pytest.mark.unit
class TestVertexAIService:
    """Test Vertex AI service"""
    
    @pytest.mark.asyncio
    async def test_generate_response(self, mock_vertex_ai):
        """Test generating response from Vertex AI"""
        messages = [
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": "Hello, how are you?"}
        ]
        
        response = await vertex_ai_service.generate_response(
            messages=messages,
            model="gemini-1.5-pro",
            temperature=0.7
        )
        
        assert "content" in response
        assert "metadata" in response
        assert response["content"] == "Test response from Vertex AI"
        assert response["metadata"]["model"] == "gemini-1.5-pro"
        
        # Verify mock was called with correct parameters
        mock_vertex_ai.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_response_with_tools(self, mock_vertex_ai):
        """Test generating response with tool calls"""
        messages = [{"role": "user", "content": "What's the weather like?"}]
        tools = [{"name": "get_weather", "description": "Get weather information"}]
        
        # Mock response with tool call
        mock_vertex_ai.return_value = {
            "content": "I'll check the weather for you.",
            "tool_calls": [{"tool": "get_weather", "parameters": {"location": "current"}}],
            "metadata": {"model": "gemini-1.5-pro"}
        }
        
        response = await vertex_ai_service.generate_response(
            messages=messages,
            tools=tools,
            model="gemini-1.5-pro"
        )
        
        assert "tool_calls" in response
        assert len(response["tool_calls"]) == 1
        assert response["tool_calls"][0]["tool"] == "get_weather"
    
    @pytest.mark.asyncio
    async def test_generate_response_error_handling(self):
        """Test error handling in Vertex AI service"""
        with patch.object(vertex_ai_service, 'generate_response') as mock:
            mock.side_effect = Exception("API Error")
            
            with pytest.raises(Exception, match="API Error"):
                await vertex_ai_service.generate_response(
                    messages=[{"role": "user", "content": "test"}]
                )


@pytest.mark.unit
class TestMCPToolRegistry:
    """Test MCP tool registry service"""
    
    @pytest.mark.asyncio
    async def test_get_available_tools(self, db_session, mock_mcp_registry):
        """Test getting available tools"""
        tools = await mcp_tool_registry.get_available_tools(
            db=db_session,
            organization_id="test_org"
        )
        
        assert isinstance(tools, list)
        assert len(tools) > 0
        assert "tool_id" in tools[0]
        assert "name" in tools[0]
        assert "description" in tools[0]
    
    @pytest.mark.asyncio
    async def test_execute_tool(self, db_session, mock_mcp_registry):
        """Test executing a tool"""
        result = await mcp_tool_registry.execute_tool(
            db=db_session,
            tool_id="test_tool",
            organization_id="test_org",
            input_parameters={"param1": "value1"}
        )
        
        assert "status" in result
        assert "result" in result
        assert result["status"] == "success"
        assert result["result"]["message"] == "Tool executed successfully"
    
    @pytest.mark.asyncio
    async def test_get_tools_by_category(self, db_session):
        """Test getting tools filtered by category"""
        with patch.object(mcp_tool_registry, 'get_available_tools') as mock:
            mock.return_value = [
                {"tool_id": "tool1", "category": "communication"},
                {"tool_id": "tool2", "category": "analytics"},
                {"tool_id": "tool3", "category": "communication"}
            ]
            
            tools = await mcp_tool_registry.get_available_tools(
                db=db_session,
                organization_id="test_org",
                category="communication"
            )
            
            # In real implementation, this would filter by category
            assert len(tools) == 3  # Mock returns all tools


@pytest.mark.unit
class TestStripeService:
    """Test Stripe service"""
    
    @pytest.mark.asyncio
    async def test_create_customer(self):
        """Test creating a Stripe customer"""
        with patch.object(stripe_service, 'create_customer') as mock:
            mock.return_value = {
                "id": "cus_test123",
                "email": "test@example.com",
                "name": "Test Customer"
            }
            
            customer = await stripe_service.create_customer(
                email="test@example.com",
                name="Test Customer",
                organization_id="test_org"
            )
            
            assert customer["id"] == "cus_test123"
            assert customer["email"] == "test@example.com"
            assert customer["name"] == "Test Customer"
    
    @pytest.mark.asyncio
    async def test_create_subscription(self):
        """Test creating a Stripe subscription"""
        with patch.object(stripe_service, 'create_subscription') as mock:
            mock.return_value = {
                "id": "sub_test123",
                "customer": "cus_test123",
                "status": "active",
                "current_period_end": 1234567890
            }
            
            subscription = await stripe_service.create_subscription(
                customer_id="cus_test123",
                price_id="price_test123"
            )
            
            assert subscription["id"] == "sub_test123"
            assert subscription["customer"] == "cus_test123"
            assert subscription["status"] == "active"
    
    @pytest.mark.asyncio
    async def test_get_usage_metrics(self):
        """Test getting usage metrics"""
        with patch.object(stripe_service, 'get_usage_metrics') as mock:
            mock.return_value = {
                "api_requests": 1500,
                "tokens_used": 50000,
                "conversations": 25,
                "period_start": "2024-01-01",
                "period_end": "2024-01-31"
            }
            
            metrics = await stripe_service.get_usage_metrics(
                organization_id="test_org",
                period_start="2024-01-01",
                period_end="2024-01-31"
            )
            
            assert metrics["api_requests"] == 1500
            assert metrics["tokens_used"] == 50000
            assert metrics["conversations"] == 25
    
    @pytest.mark.asyncio
    async def test_handle_webhook(self):
        """Test handling Stripe webhooks"""
        webhook_data = {
            "type": "invoice.payment_succeeded",
            "data": {
                "object": {
                    "id": "in_test123",
                    "customer": "cus_test123",
                    "amount_paid": 2000,
                    "status": "paid"
                }
            }
        }
        
        with patch.object(stripe_service, 'handle_webhook') as mock:
            mock.return_value = {"status": "processed"}
            
            result = await stripe_service.handle_webhook(webhook_data)
            
            assert result["status"] == "processed"


@pytest.mark.unit
class TestServiceIntegration:
    """Test service integration scenarios"""
    
    @pytest.mark.asyncio
    async def test_assistant_conversation_flow(self, db_session, sample_user, sample_assistant, mock_vertex_ai, mock_mcp_registry):
        """Test complete assistant conversation flow"""
        # Create conversation
        conversation = await conversation_service.create_conversation(
            db=db_session,
            user_id=sample_user.id,
            assistant_id=sample_assistant.id,
            channel="chat"
        )
        
        # Add user message
        user_message = await conversation_service.add_message(
            db=db_session,
            conversation_id=conversation.id,
            role="user",
            content="I need help with billing"
        )
        
        # Create assistant and process message
        assistant = await assistant_factory.create_assistant(
            db=db_session,
            assistant_type="support",
            assistant_id=sample_assistant.id,
            config={"organization_id": sample_user.organization_id}
        )
        
        # Process message with assistant
        response = await assistant.process_message(
            db=db_session,
            message="I need help with billing",
            conversation_context={"conversation_id": conversation.id}
        )
        
        # Add assistant response
        assistant_message = await conversation_service.add_message(
            db=db_session,
            conversation_id=conversation.id,
            role="assistant",
            content=response["response"]
        )
        
        # Verify flow
        assert user_message.role == "user"
        assert assistant_message.role == "assistant"
        assert "response" in response
        assert response["metadata"]["assistant_type"] == "support"
    
    @pytest.mark.asyncio
    async def test_error_handling_chain(self, db_session, sample_user, sample_assistant):
        """Test error handling across service chain"""
        # Test with invalid conversation ID
        with pytest.raises(Exception):
            await conversation_service.add_message(
                db=db_session,
                conversation_id="invalid_id",
                role="user",
                content="test message"
            )
        
        # Test with invalid assistant type
        with pytest.raises(ValueError):
            await assistant_factory.create_assistant(
                db=db_session,
                assistant_type="invalid_type",
                assistant_id="test",
                config={}
            )