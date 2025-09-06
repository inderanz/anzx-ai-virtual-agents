"""
Conversation Management Tests
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.services.conversation_service import ConversationService
from app.services.conversation_context import ConversationContextManager, ConversationContext
from app.models.user import Organization, User, Assistant, Conversation, Message


class TestConversationService:
    """Test conversation service functionality"""
    
    @pytest.fixture
    def conversation_service(self):
        return ConversationService()
    
    @pytest.fixture
    def mock_db(self):
        return Mock(spec=Session)
    
    @pytest.fixture
    def sample_organization(self):
        org = Mock(spec=Organization)
        org.id = "test-org-id"
        org.name = "Test Organization"
        return org
    
    @pytest.fixture
    def sample_assistant(self):
        assistant = Mock(spec=Assistant)
        assistant.id = "test-assistant-id"
        assistant.name = "Test Assistant"
        assistant.type = "support"
        assistant.organization_id = "test-org-id"
        return assistant
    
    @pytest.fixture
    def sample_user(self):
        user = Mock(spec=User)
        user.id = "test-user-id"
        user.email = "test@example.com"
        user.display_name = "Test User"
        return user
    
    @pytest.fixture
    def sample_conversation(self):
        conv = Mock(spec=Conversation)
        conv.id = "test-conv-id"
        conv.title = "Test Conversation"
        conv.status = "active"
        conv.message_count = 5
        conv.total_tokens = 1000
        conv.total_cost = 0.05
        conv.created_at = datetime.utcnow()
        conv.updated_at = datetime.utcnow()
        conv.metadata = {"channel": "web"}
        conv.user_id = "test-user-id"
        conv.assistant_id = "test-assistant-id"
        conv.organization_id = "test-org-id"
        return conv
    
    @pytest.mark.asyncio
    async def test_create_conversation_success(self, conversation_service, mock_db, sample_organization, sample_assistant):
        """Test successful conversation creation"""
        # Mock database queries
        mock_db.query.return_value.filter.return_value.first.side_effect = [sample_organization, sample_assistant]
        
        # Mock conversation creation
        mock_conversation = Mock(spec=Conversation)
        mock_conversation.id = "new-conv-id"
        mock_conversation.title = "New Conversation"
        mock_conversation.status = "active"
        mock_conversation.created_at = datetime.utcnow()
        
        with patch('app.models.user.Conversation') as mock_conv_class:
            mock_conv_class.return_value = mock_conversation
            
            result = await conversation_service.create_conversation(
                db=mock_db,
                organization_id="test-org-id",
                assistant_id="test-assistant-id",
                user_id="test-user-id",
                title="Test Conversation",
                channel="web"
            )
            
            assert result["conversation_id"] == "new-conv-id"
            assert result["title"] == "New Conversation"
            assert result["status"] == "active"
            assert result["channel"] == "web"
            mock_db.add.assert_called_once()
            mock_db.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_conversation_organization_not_found(self, conversation_service, mock_db):
        """Test conversation creation with non-existent organization"""
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        with pytest.raises(Exception) as exc_info:
            await conversation_service.create_conversation(
                db=mock_db,
                organization_id="nonexistent-org",
                assistant_id="test-assistant-id"
            )
        
        assert "Organization not found" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_get_conversations_with_filters(self, conversation_service, mock_db, sample_conversation, sample_assistant):
        """Test getting conversations with filters"""
        mock_db.query.return_value.filter.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [sample_conversation]
        mock_db.query.return_value.filter.return_value.first.return_value = sample_assistant
        
        with patch.object(conversation_service, '_format_conversation') as mock_format:
            mock_format.return_value = {
                "conversation_id": "test-conv-id",
                "title": "Test Conversation",
                "status": "active"
            }
            
            result = await conversation_service.get_conversations(
                db=mock_db,
                organization_id="test-org-id",
                status="active",
                channel="web",
                limit=10
            )
            
            assert len(result) == 1
            assert result[0]["conversation_id"] == "test-conv-id"
            mock_format.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_conversation(self, conversation_service, mock_db, sample_conversation):
        """Test conversation update"""
        mock_db.query.return_value.filter.return_value.first.return_value = sample_conversation
        
        updates = {
            "title": "Updated Title",
            "status": "resolved",
            "metadata": {"new_field": "value"}
        }
        
        result = await conversation_service.update_conversation(
            db=mock_db,
            conversation_id="test-conv-id",
            organization_id="test-org-id",
            updates=updates
        )
        
        assert result["conversation_id"] == "test-conv-id"
        assert sample_conversation.title == "Updated Title"
        assert sample_conversation.status == "resolved"
        mock_db.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_escalate_conversation(self, conversation_service, mock_db, sample_conversation):
        """Test conversation escalation"""
        mock_db.query.return_value.filter.return_value.first.return_value = sample_conversation
        
        with patch.object(conversation_service, '_send_escalation_notification') as mock_notify:
            mock_notify.return_value = None
            
            result = await conversation_service.escalate_conversation(
                db=mock_db,
                conversation_id="test-conv-id",
                organization_id="test-org-id",
                escalation_reason="Customer requested human agent"
            )
            
            assert result["conversation_id"] == "test-conv-id"
            assert result["status"] == "escalated"
            assert sample_conversation.status == "escalated"
            mock_notify.assert_called_once()
            mock_db.add.assert_called_once()  # For escalation message
            mock_db.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_route_conversation(self, conversation_service, mock_db, sample_conversation, sample_assistant):
        """Test conversation routing"""
        target_assistant = Mock(spec=Assistant)
        target_assistant.id = "target-assistant-id"
        target_assistant.name = "Target Assistant"
        target_assistant.type = "technical"
        
        mock_db.query.return_value.filter.return_value.first.side_effect = [sample_conversation, target_assistant]
        
        result = await conversation_service.route_conversation(
            db=mock_db,
            conversation_id="test-conv-id",
            organization_id="test-org-id",
            target_assistant_id="target-assistant-id",
            routing_reason="Technical expertise required"
        )
        
        assert result["conversation_id"] == "test-conv-id"
        assert result["routed_to"]["assistant_id"] == "target-assistant-id"
        assert sample_conversation.assistant_id == "target-assistant-id"
        mock_db.add.assert_called_once()  # For routing message
        mock_db.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_archive_conversation(self, conversation_service, mock_db, sample_conversation):
        """Test conversation archiving"""
        mock_db.query.return_value.filter.return_value.first.return_value = sample_conversation
        
        result = await conversation_service.archive_conversation(
            db=mock_db,
            conversation_id="test-conv-id",
            organization_id="test-org-id",
            archive_reason="Issue resolved"
        )
        
        assert result["conversation_id"] == "test-conv-id"
        assert result["status"] == "archived"
        assert sample_conversation.status == "archived"
        mock_db.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_conversation_analytics(self, conversation_service, mock_db):
        """Test conversation analytics"""
        # Mock conversations
        conv1 = Mock(spec=Conversation)
        conv1.status = "active"
        conv1.message_count = 5
        conv1.total_cost = 0.05
        conv1.metadata = {"channel": "web"}
        
        conv2 = Mock(spec=Conversation)
        conv2.status = "resolved"
        conv2.message_count = 8
        conv2.total_cost = 0.08
        conv2.metadata = {"channel": "email"}
        
        mock_db.query.return_value.filter.return_value.all.return_value = [conv1, conv2]
        
        # Mock messages for satisfaction
        mock_db.query.return_value.filter.return_value.all.return_value = []
        
        result = await conversation_service.get_conversation_analytics(
            db=mock_db,
            organization_id="test-org-id"
        )
        
        assert result["totals"]["conversations"] == 2
        assert result["totals"]["messages"] == 13
        assert result["totals"]["cost_aud"] == 0.13
        assert result["breakdowns"]["by_status"]["active"] == 1
        assert result["breakdowns"]["by_status"]["resolved"] == 1
        assert result["breakdowns"]["by_channel"]["web"] == 1
        assert result["breakdowns"]["by_channel"]["email"] == 1


class TestConversationContextManager:
    """Test conversation context manager"""
    
    @pytest.fixture
    def context_manager(self):
        return ConversationContextManager()
    
    @pytest.fixture
    def mock_db(self):
        return Mock(spec=Session)
    
    @pytest.fixture
    def sample_conversation(self):
        conv = Mock(spec=Conversation)
        conv.id = "test-conv-id"
        conv.assistant_id = "test-assistant-id"
        conv.organization_id = "test-org-id"
        conv.user_id = "test-user-id"
        conv.metadata = {
            "channel": "web",
            "context": {
                "current_topic": "billing",
                "user_intent": "question",
                "conversation_stage": "information_gathering",
                "key_facts": ["User has billing issue"],
                "mentioned_entities": {"email": "test@example.com"},
                "context_version": 1
            }
        }
        return conv
    
    @pytest.mark.asyncio
    async def test_get_context_from_database(self, context_manager, mock_db, sample_conversation):
        """Test getting context from database"""
        mock_db.query.return_value.filter.return_value.first.return_value = sample_conversation
        
        context = await context_manager.get_context(mock_db, "test-conv-id")
        
        assert context is not None
        assert context.conversation_id == "test-conv-id"
        assert context.current_topic == "billing"
        assert context.user_intent == "question"
        assert context.conversation_stage == "information_gathering"
        assert "User has billing issue" in context.key_facts
        assert context.mentioned_entities["email"] == "test@example.com"
    
    @pytest.mark.asyncio
    async def test_get_context_from_cache(self, context_manager, mock_db):
        """Test getting context from cache"""
        # Create a context and add to cache
        context = ConversationContext(
            conversation_id="test-conv-id",
            assistant_id="test-assistant-id",
            organization_id="test-org-id",
            user_id="test-user-id",
            channel="web"
        )
        
        context_manager.context_cache["test-conv-id"] = (context, datetime.utcnow())
        
        # Get context (should come from cache)
        cached_context = await context_manager.get_context(mock_db, "test-conv-id")
        
        assert cached_context == context
        # Database should not be queried
        mock_db.query.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_update_context(self, context_manager, mock_db, sample_conversation):
        """Test context updates"""
        mock_db.query.return_value.filter.return_value.first.return_value = sample_conversation
        
        # Get initial context
        context = await context_manager.get_context(mock_db, "test-conv-id")
        initial_version = context.context_version
        
        # Update context
        updates = {
            "current_topic": "technical",
            "user_intent": "problem"
        }
        
        success = await context_manager.update_context(mock_db, "test-conv-id", updates)
        
        assert success is True
        
        # Verify updates
        updated_context = await context_manager.get_context(mock_db, "test-conv-id")
        assert updated_context.current_topic == "technical"
        assert updated_context.user_intent == "problem"
        assert updated_context.context_version > initial_version
    
    @pytest.mark.asyncio
    async def test_analyze_message_for_context(self, context_manager, mock_db, sample_conversation):
        """Test message analysis for context extraction"""
        mock_db.query.return_value.filter.return_value.first.return_value = sample_conversation
        
        # Analyze user message
        user_message = "I have a problem with my order #12345. My email is user@example.com and I'm very frustrated."
        
        updates = await context_manager.analyze_message_for_context(
            db=mock_db,
            conversation_id="test-conv-id",
            message=user_message,
            role="user"
        )
        
        # Check extracted information
        assert "mentioned_entities" in updates
        assert updates["mentioned_entities"]["email"] == "user@example.com"
        assert updates["mentioned_entities"]["order_number"] == "12345"
        
        assert updates["user_intent"] == "problem"
        
        assert "escalation_triggers" in updates
        assert any("frustrated" in trigger for trigger in updates["escalation_triggers"])
    
    @pytest.mark.asyncio
    async def test_should_escalate(self, context_manager, mock_db, sample_conversation):
        """Test escalation decision logic"""
        # Modify conversation to have escalation triggers
        sample_conversation.metadata["context"]["escalation_triggers"] = [
            "User mentioned: frustrated",
            "User mentioned: not helpful",
            "User mentioned: speak to human"
        ]
        sample_conversation.message_count = 25  # Long conversation
        
        mock_db.query.return_value.filter.return_value.first.return_value = sample_conversation
        
        should_escalate, reasons = await context_manager.should_escalate(mock_db, "test-conv-id")
        
        assert should_escalate is True
        assert len(reasons) >= 2  # Multiple escalation triggers + long conversation
        assert any("escalation triggers" in reason for reason in reasons)
        assert any("Long conversation" in reason for reason in reasons)
    
    @pytest.mark.asyncio
    async def test_get_context_summary(self, context_manager, mock_db, sample_conversation):
        """Test context summary generation"""
        mock_db.query.return_value.filter.return_value.first.return_value = sample_conversation
        
        summary = await context_manager.get_context_summary(mock_db, "test-conv-id")
        
        assert "Current topic: billing" in summary
        assert "User intent: question" in summary
        assert "Conversation stage: information_gathering" in summary
        assert "Key facts:" in summary
        assert "Mentioned:" in summary
    
    def test_extract_entities(self, context_manager):
        """Test entity extraction"""
        message = "My email is john@example.com and my phone is 555-123-4567. Order number is ABC123456."
        
        entities = context_manager._extract_entities(message)
        
        assert entities["email"] == "john@example.com"
        assert entities["phone"] == "555-123-4567"
        assert entities["order_number"] == "ABC123456"
    
    def test_detect_intent(self, context_manager):
        """Test intent detection"""
        test_cases = [
            ("What is my account balance?", "question"),
            ("I have a problem with my order", "problem"),
            ("Can you help me cancel my subscription?", "cancel"),
            ("This service is terrible", "complaint"),
            ("You guys are amazing!", "compliment")
        ]
        
        for message, expected_intent in test_cases:
            intent = context_manager._detect_intent(message)
            assert intent == expected_intent
    
    def test_detect_escalation_triggers(self, context_manager):
        """Test escalation trigger detection"""
        message = "I'm very frustrated and want to speak to a human agent. This is not helpful at all."
        
        triggers = context_manager._detect_escalation_triggers(message)
        
        assert len(triggers) >= 3  # frustrated, speak to human, not helpful
        assert any("frustrated" in trigger for trigger in triggers)
        assert any("speak to human" in trigger for trigger in triggers)
        assert any("not helpful" in trigger for trigger in triggers)
    
    def test_cleanup_expired_contexts(self, context_manager):
        """Test cleanup of expired contexts"""
        # Add some contexts to cache
        old_time = datetime.utcnow() - timedelta(hours=3)  # Expired
        recent_time = datetime.utcnow() - timedelta(minutes=30)  # Not expired
        
        context1 = ConversationContext("conv1", "asst1", "org1", "user1", "web")
        context2 = ConversationContext("conv2", "asst2", "org1", "user1", "web")
        
        context_manager.context_cache["conv1"] = (context1, old_time)
        context_manager.context_cache["conv2"] = (context2, recent_time)
        
        # Cleanup
        context_manager.cleanup_expired_contexts()
        
        # Check that expired context was removed
        assert "conv1" not in context_manager.context_cache
        assert "conv2" in context_manager.context_cache


if __name__ == "__main__":
    pytest.main([__file__])