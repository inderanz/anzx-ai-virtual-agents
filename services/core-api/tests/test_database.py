"""
Tests for database models and operations
"""

import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import uuid

from app.models.database import Base
from app.models.user import (
    Organization, User, Assistant, KnowledgeSource, 
    Document, Conversation, Message, Subscription, AuditLog
)
from app.utils.database import VectorSearchUtils, DatabaseUtils


# Test database setup
TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture
def db_engine():
    """Create test database engine"""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    return engine


@pytest.fixture
def db_session(db_engine):
    """Create test database session"""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def sample_organization(db_session):
    """Create sample organization for testing"""
    org = Organization(
        name="Test Organization",
        description="Test organization for unit tests",
        region="AU",
        subscription_plan="pro"
    )
    db_session.add(org)
    db_session.commit()
    return org


@pytest.fixture
def sample_user(db_session, sample_organization):
    """Create sample user for testing"""
    user = User(
        firebase_uid="test-user-123",
        email="test@example.com",
        display_name="Test User",
        organization_id=sample_organization.id,
        role="admin",
        privacy_consent=True,
        email_verified=True
    )
    db_session.add(user)
    db_session.commit()
    return user


class TestOrganizationModel:
    """Test Organization model"""
    
    def test_create_organization(self, db_session):
        """Test creating an organization"""
        org = Organization(
            name="Test Org",
            description="Test description",
            region="AU",
            subscription_plan="freemium"
        )
        
        db_session.add(org)
        db_session.commit()
        
        assert org.id is not None
        assert org.name == "Test Org"
        assert org.region == "AU"
        assert org.subscription_plan == "freemium"
        assert org.subscription_status == "active"
        assert org.monthly_message_limit == 1000
        assert org.created_at is not None
    
    def test_organization_relationships(self, db_session, sample_organization):
        """Test organization relationships"""
        # Add user
        user = User(
            firebase_uid="test-123",
            email="test@example.com",
            organization_id=sample_organization.id
        )
        db_session.add(user)
        
        # Add assistant
        assistant = Assistant(
            name="Test Assistant",
            type="support",
            organization_id=sample_organization.id
        )
        db_session.add(assistant)
        
        db_session.commit()
        
        # Test relationships
        assert len(sample_organization.users) == 1
        assert len(sample_organization.assistants) == 1
        assert sample_organization.users[0].email == "test@example.com"
        assert sample_organization.assistants[0].name == "Test Assistant"


class TestUserModel:
    """Test User model"""
    
    def test_create_user(self, db_session, sample_organization):
        """Test creating a user"""
        user = User(
            firebase_uid="test-user-456",
            email="user@example.com",
            display_name="Test User",
            organization_id=sample_organization.id,
            role="user",
            privacy_consent=True
        )
        
        db_session.add(user)
        db_session.commit()
        
        assert user.id is not None
        assert user.firebase_uid == "test-user-456"
        assert user.email == "user@example.com"
        assert user.role == "user"
        assert user.is_active is True
        assert user.login_count == 0
        assert user.privacy_consent is True
    
    def test_user_organization_relationship(self, db_session, sample_user, sample_organization):
        """Test user-organization relationship"""
        assert sample_user.organization_id == sample_organization.id
        assert sample_user.organization.name == sample_organization.name


class TestAssistantModel:
    """Test Assistant model"""
    
    def test_create_assistant(self, db_session, sample_organization):
        """Test creating an assistant"""
        assistant = Assistant(
            name="Support Bot",
            description="Customer support assistant",
            type="support",
            organization_id=sample_organization.id,
            system_prompt="You are a helpful assistant",
            is_active=True,
            deployment_status="deployed"
        )
        
        db_session.add(assistant)
        db_session.commit()
        
        assert assistant.id is not None
        assert assistant.name == "Support Bot"
        assert assistant.type == "support"
        assert assistant.is_active is True
        assert assistant.deployment_status == "deployed"
        assert assistant.version == "1.0.0"
        assert assistant.total_conversations == 0


class TestKnowledgeSourceModel:
    """Test KnowledgeSource model"""
    
    def test_create_knowledge_source(self, db_session, sample_organization):
        """Test creating a knowledge source"""
        source = KnowledgeSource(
            name="FAQ Document",
            description="Frequently asked questions",
            type="file",
            organization_id=sample_organization.id,
            status="completed",
            chunk_count=10
        )
        
        db_session.add(source)
        db_session.commit()
        
        assert source.id is not None
        assert source.name == "FAQ Document"
        assert source.type == "file"
        assert source.status == "completed"
        assert source.chunk_count == 10
        assert source.embedding_model == "text-embedding-004"


class TestDocumentModel:
    """Test Document model"""
    
    def test_create_document(self, db_session, sample_organization):
        """Test creating a document chunk"""
        # Create knowledge source first
        source = KnowledgeSource(
            name="Test Source",
            type="text",
            organization_id=sample_organization.id
        )
        db_session.add(source)
        db_session.flush()
        
        # Create document
        doc = Document(
            knowledge_source_id=source.id,
            content="This is a test document chunk",
            chunk_index=0,
            token_count=6,
            metadata={"section": "introduction"}
        )
        
        db_session.add(doc)
        db_session.commit()
        
        assert doc.id is not None
        assert doc.content == "This is a test document chunk"
        assert doc.chunk_index == 0
        assert doc.token_count == 6
        assert doc.metadata["section"] == "introduction"


class TestConversationModel:
    """Test Conversation model"""
    
    def test_create_conversation(self, db_session, sample_organization, sample_user):
        """Test creating a conversation"""
        # Create assistant
        assistant = Assistant(
            name="Test Assistant",
            type="support",
            organization_id=sample_organization.id
        )
        db_session.add(assistant)
        db_session.flush()
        
        # Create conversation
        conversation = Conversation(
            title="Test Conversation",
            organization_id=sample_organization.id,
            user_id=sample_user.id,
            assistant_id=assistant.id,
            channel="widget",
            status="active"
        )
        
        db_session.add(conversation)
        db_session.commit()
        
        assert conversation.id is not None
        assert conversation.title == "Test Conversation"
        assert conversation.channel == "widget"
        assert conversation.status == "active"
        assert conversation.message_count == 0
        assert conversation.total_tokens == 0


class TestMessageModel:
    """Test Message model"""
    
    def test_create_message(self, db_session, sample_organization, sample_user):
        """Test creating a message"""
        # Create assistant and conversation
        assistant = Assistant(
            name="Test Assistant",
            type="support",
            organization_id=sample_organization.id
        )
        db_session.add(assistant)
        db_session.flush()
        
        conversation = Conversation(
            organization_id=sample_organization.id,
            user_id=sample_user.id,
            assistant_id=assistant.id
        )
        db_session.add(conversation)
        db_session.flush()
        
        # Create message
        message = Message(
            conversation_id=conversation.id,
            content="Hello, how can I help you?",
            role="assistant",
            model="gpt-4",
            tokens_input=10,
            tokens_output=8,
            latency_ms=1500
        )
        
        db_session.add(message)
        db_session.commit()
        
        assert message.id is not None
        assert message.content == "Hello, how can I help you?"
        assert message.role == "assistant"
        assert message.model == "gpt-4"
        assert message.tokens_input == 10
        assert message.tokens_output == 8
        assert message.latency_ms == 1500


class TestSubscriptionModel:
    """Test Subscription model"""
    
    def test_create_subscription(self, db_session, sample_organization):
        """Test creating a subscription"""
        subscription = Subscription(
            organization_id=sample_organization.id,
            stripe_customer_id="cus_test123",
            stripe_subscription_id="sub_test123",
            plan="pro",
            status="active",
            usage_counters={"messages": 100, "tokens": 10000}
        )
        
        db_session.add(subscription)
        db_session.commit()
        
        assert subscription.organization_id == sample_organization.id
        assert subscription.stripe_customer_id == "cus_test123"
        assert subscription.plan == "pro"
        assert subscription.status == "active"
        assert subscription.usage_counters["messages"] == 100


class TestAuditLogModel:
    """Test AuditLog model"""
    
    def test_create_audit_log(self, db_session, sample_user, sample_organization):
        """Test creating an audit log entry"""
        log = AuditLog(
            event_type="USER_LOGIN",
            action="user_login_success",
            outcome="success",
            user_id=sample_user.id,
            organization_id=sample_organization.id,
            ip_address="192.168.1.1",
            details={"provider": "firebase"},
            risk_level="low"
        )
        
        db_session.add(log)
        db_session.commit()
        
        assert log.id is not None
        assert log.event_type == "USER_LOGIN"
        assert log.action == "user_login_success"
        assert log.outcome == "success"
        assert log.user_id == sample_user.id
        assert log.risk_level == "low"
        assert log.details["provider"] == "firebase"


class TestDatabaseUtils:
    """Test database utility functions"""
    
    def test_get_table_stats(self, db_session, sample_organization, sample_user):
        """Test getting table statistics"""
        # Note: This test is limited in SQLite, but tests the function structure
        stats = DatabaseUtils.get_table_stats(db_session)
        
        # Should return a dictionary with some stats
        assert isinstance(stats, dict)
        # In a real PostgreSQL environment, this would have actual counts


if __name__ == "__main__":
    pytest.main([__file__])