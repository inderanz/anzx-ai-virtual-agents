"""
Unit tests for database models
"""

import pytest
from datetime import datetime
from sqlalchemy.exc import IntegrityError

from app.models.user import User, Organization, Assistant, Conversation, Message, KnowledgeSource


@pytest.mark.unit
class TestOrganizationModel:
    """Test Organization model functionality"""
    
    def test_create_organization(self, db_session):
        """Test creating a new organization"""
        org = Organization(
            id="test_org_001",
            name="Test Organization",
            domain="test.com",
            subscription_tier="professional",
            is_active=True
        )
        
        db_session.add(org)
        db_session.commit()
        
        # Verify organization was created
        saved_org = db_session.query(Organization).filter_by(id="test_org_001").first()
        assert saved_org is not None
        assert saved_org.name == "Test Organization"
        assert saved_org.domain == "test.com"
        assert saved_org.subscription_tier == "professional"
        assert saved_org.is_active is True
        assert saved_org.created_at is not None
    
    def test_organization_unique_constraints(self, db_session):
        """Test organization unique constraints"""
        # Create first organization
        org1 = Organization(
            id="test_org_001",
            name="Test Organization",
            domain="test.com"
        )
        db_session.add(org1)
        db_session.commit()
        
        # Try to create organization with same domain
        org2 = Organization(
            id="test_org_002",
            name="Another Organization",
            domain="test.com"  # Same domain should fail
        )
        db_session.add(org2)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_organization_relationships(self, db_session, sample_organization):
        """Test organization relationships"""
        # Create users for the organization
        user1 = User(
            id="user_001",
            email="user1@test.com",
            name="User 1",
            organization_id=sample_organization.id
        )
        user2 = User(
            id="user_002",
            email="user2@test.com",
            name="User 2",
            organization_id=sample_organization.id
        )
        
        db_session.add_all([user1, user2])
        db_session.commit()
        
        # Test relationship
        db_session.refresh(sample_organization)
        assert len(sample_organization.users) == 2
        assert user1 in sample_organization.users
        assert user2 in sample_organization.users


@pytest.mark.unit
class TestUserModel:
    """Test User model functionality"""
    
    def test_create_user(self, db_session, sample_organization):
        """Test creating a new user"""
        user = User(
            id="test_user_001",
            email="test@example.com",
            name="Test User",
            organization_id=sample_organization.id,
            role="admin",
            is_active=True
        )
        
        db_session.add(user)
        db_session.commit()
        
        # Verify user was created
        saved_user = db_session.query(User).filter_by(id="test_user_001").first()
        assert saved_user is not None
        assert saved_user.email == "test@example.com"
        assert saved_user.name == "Test User"
        assert saved_user.role == "admin"
        assert saved_user.is_active is True
        assert saved_user.organization_id == sample_organization.id
    
    def test_user_email_unique(self, db_session, sample_organization):
        """Test user email uniqueness"""
        # Create first user
        user1 = User(
            id="user_001",
            email="test@example.com",
            name="User 1",
            organization_id=sample_organization.id
        )
        db_session.add(user1)
        db_session.commit()
        
        # Try to create user with same email
        user2 = User(
            id="user_002",
            email="test@example.com",  # Same email should fail
            name="User 2",
            organization_id=sample_organization.id
        )
        db_session.add(user2)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_user_organization_relationship(self, db_session, sample_user, sample_organization):
        """Test user-organization relationship"""
        assert sample_user.organization == sample_organization
        assert sample_user in sample_organization.users


@pytest.mark.unit
class TestAssistantModel:
    """Test Assistant model functionality"""
    
    def test_create_assistant(self, db_session, sample_organization):
        """Test creating a new assistant"""
        assistant = Assistant(
            id="test_assistant_001",
            name="Test Assistant",
            type="support",
            organization_id=sample_organization.id,
            configuration={
                "model": "gemini-1.5-pro",
                "temperature": 0.7,
                "capabilities": ["communication", "technical"]
            },
            is_active=True
        )
        
        db_session.add(assistant)
        db_session.commit()
        
        # Verify assistant was created
        saved_assistant = db_session.query(Assistant).filter_by(id="test_assistant_001").first()
        assert saved_assistant is not None
        assert saved_assistant.name == "Test Assistant"
        assert saved_assistant.type == "support"
        assert saved_assistant.configuration["model"] == "gemini-1.5-pro"
        assert "communication" in saved_assistant.configuration["capabilities"]
    
    def test_assistant_configuration_json(self, db_session, sample_assistant):
        """Test assistant configuration JSON handling"""
        # Update configuration
        new_config = {
            "model": "gemini-1.5-flash",
            "temperature": 0.5,
            "max_tokens": 1000,
            "capabilities": ["communication", "billing"]
        }
        
        sample_assistant.configuration = new_config
        db_session.commit()
        
        # Verify configuration was saved correctly
        db_session.refresh(sample_assistant)
        assert sample_assistant.configuration["model"] == "gemini-1.5-flash"
        assert sample_assistant.configuration["temperature"] == 0.5
        assert sample_assistant.configuration["max_tokens"] == 1000


@pytest.mark.unit
class TestConversationModel:
    """Test Conversation model functionality"""
    
    def test_create_conversation(self, db_session, sample_user, sample_assistant):
        """Test creating a new conversation"""
        conversation = Conversation(
            id="test_conv_001",
            user_id=sample_user.id,
            assistant_id=sample_assistant.id,
            channel="chat",
            status="active",
            metadata={"source": "web_widget"}
        )
        
        db_session.add(conversation)
        db_session.commit()
        
        # Verify conversation was created
        saved_conv = db_session.query(Conversation).filter_by(id="test_conv_001").first()
        assert saved_conv is not None
        assert saved_conv.user_id == sample_user.id
        assert saved_conv.assistant_id == sample_assistant.id
        assert saved_conv.channel == "chat"
        assert saved_conv.status == "active"
        assert saved_conv.metadata["source"] == "web_widget"
    
    def test_conversation_relationships(self, db_session, sample_conversation, sample_user, sample_assistant):
        """Test conversation relationships"""
        assert sample_conversation.user == sample_user
        assert sample_conversation.assistant == sample_assistant
    
    def test_conversation_status_transitions(self, db_session, sample_conversation):
        """Test conversation status transitions"""
        # Test valid status transitions
        valid_statuses = ["active", "paused", "completed", "escalated"]
        
        for status in valid_statuses:
            sample_conversation.status = status
            db_session.commit()
            
            db_session.refresh(sample_conversation)
            assert sample_conversation.status == status


@pytest.mark.unit
class TestMessageModel:
    """Test Message model functionality"""
    
    def test_create_message(self, db_session, sample_conversation):
        """Test creating a new message"""
        message = Message(
            id="test_msg_001",
            conversation_id=sample_conversation.id,
            role="user",
            content="Hello, I need help with my account",
            metadata={"timestamp": datetime.now().isoformat()}
        )
        
        db_session.add(message)
        db_session.commit()
        
        # Verify message was created
        saved_msg = db_session.query(Message).filter_by(id="test_msg_001").first()
        assert saved_msg is not None
        assert saved_msg.conversation_id == sample_conversation.id
        assert saved_msg.role == "user"
        assert saved_msg.content == "Hello, I need help with my account"
        assert "timestamp" in saved_msg.metadata
    
    def test_message_conversation_relationship(self, db_session, sample_message, sample_conversation):
        """Test message-conversation relationship"""
        assert sample_message.conversation == sample_conversation
        assert sample_message in sample_conversation.messages
    
    def test_message_ordering(self, db_session, sample_conversation):
        """Test message ordering by created_at"""
        # Create multiple messages
        messages = []
        for i in range(3):
            msg = Message(
                id=f"msg_{i}",
                conversation_id=sample_conversation.id,
                role="user" if i % 2 == 0 else "assistant",
                content=f"Message {i}"
            )
            messages.append(msg)
            db_session.add(msg)
        
        db_session.commit()
        
        # Query messages ordered by created_at
        ordered_messages = db_session.query(Message)\
            .filter_by(conversation_id=sample_conversation.id)\
            .order_by(Message.created_at)\
            .all()
        
        assert len(ordered_messages) == 4  # 3 new + 1 from fixture
        # Verify ordering (newer messages should come after older ones)
        for i in range(len(ordered_messages) - 1):
            assert ordered_messages[i].created_at <= ordered_messages[i + 1].created_at


@pytest.mark.unit
class TestKnowledgeSourceModel:
    """Test KnowledgeSource model functionality"""
    
    def test_create_knowledge_source(self, db_session, sample_organization):
        """Test creating a new knowledge source"""
        knowledge_source = KnowledgeSource(
            id="test_ks_001",
            name="Test Knowledge Base",
            type="document",
            organization_id=sample_organization.id,
            configuration={
                "source_url": "https://example.com/docs",
                "sync_frequency": "daily",
                "file_types": ["pdf", "docx", "txt"]
            },
            is_active=True
        )
        
        db_session.add(knowledge_source)
        db_session.commit()
        
        # Verify knowledge source was created
        saved_ks = db_session.query(KnowledgeSource).filter_by(id="test_ks_001").first()
        assert saved_ks is not None
        assert saved_ks.name == "Test Knowledge Base"
        assert saved_ks.type == "document"
        assert saved_ks.configuration["source_url"] == "https://example.com/docs"
        assert "pdf" in saved_ks.configuration["file_types"]
    
    def test_knowledge_source_organization_relationship(self, db_session, sample_organization):
        """Test knowledge source-organization relationship"""
        ks = KnowledgeSource(
            id="test_ks_002",
            name="Test KB",
            type="url",
            organization_id=sample_organization.id,
            configuration={}
        )
        
        db_session.add(ks)
        db_session.commit()
        
        # Test relationship
        assert ks.organization == sample_organization
        db_session.refresh(sample_organization)
        assert ks in sample_organization.knowledge_sources