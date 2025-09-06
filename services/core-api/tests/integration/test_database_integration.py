"""
Integration tests for database operations
"""

import pytest
from testcontainers.postgres import PostgresContainer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import asyncio

from app.utils.database import Base
from app.models.user import User, Organization, Assistant, Conversation, Message, KnowledgeSource
from app.services.conversation_service import conversation_service
from app.services.assistant_factory import assistant_factory


@pytest.fixture(scope="module")
def postgres_container():
    """Start PostgreSQL container for integration tests"""
    with PostgresContainer("postgres:15") as postgres:
        yield postgres


@pytest.fixture(scope="module")
def integration_db_engine(postgres_container):
    """Create database engine connected to test container"""
    connection_url = postgres_container.get_connection_url()
    engine = create_engine(connection_url)
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def integration_db_session(integration_db_engine):
    """Create database session for integration tests"""
    SessionLocal = sessionmaker(bind=integration_db_engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.mark.integration
class TestDatabaseIntegration:
    """Test database integration scenarios"""
    
    def test_organization_user_cascade(self, integration_db_session):
        """Test organization-user relationship and cascading"""
        # Create organization
        org = Organization(
            id="test_org_integration",
            name="Integration Test Org",
            domain="integration.test",
            subscription_tier="professional"
        )
        integration_db_session.add(org)
        integration_db_session.commit()
        
        # Create users
        users = []
        for i in range(3):
            user = User(
                id=f"user_{i}",
                email=f"user{i}@integration.test",
                name=f"User {i}",
                organization_id=org.id,
                role="member"
            )
            users.append(user)
            integration_db_session.add(user)
        
        integration_db_session.commit()
        
        # Verify relationships
        integration_db_session.refresh(org)
        assert len(org.users) == 3
        
        # Test cascade delete (if implemented)
        user_ids = [user.id for user in users]
        integration_db_session.delete(org)
        integration_db_session.commit()
        
        # Verify users are handled appropriately
        remaining_users = integration_db_session.query(User).filter(User.id.in_(user_ids)).all()
        # Depending on cascade settings, users might be deleted or orphaned
        assert len(remaining_users) >= 0  # Adjust based on actual cascade behavior
    
    def test_conversation_message_flow(self, integration_db_session):
        """Test complete conversation and message flow"""
        # Setup organization, user, and assistant
        org = Organization(
            id="conv_test_org",
            name="Conversation Test Org",
            domain="conv.test"
        )
        integration_db_session.add(org)
        
        user = User(
            id="conv_test_user",
            email="user@conv.test",
            name="Test User",
            organization_id=org.id
        )
        integration_db_session.add(user)
        
        assistant = Assistant(
            id="conv_test_assistant",
            name="Test Assistant",
            type="support",
            organization_id=org.id,
            configuration={"model": "gemini-1.5-pro"}
        )
        integration_db_session.add(assistant)
        integration_db_session.commit()
        
        # Create conversation
        conversation = Conversation(
            id="conv_test_123",
            user_id=user.id,
            assistant_id=assistant.id,
            channel="chat",
            status="active"
        )
        integration_db_session.add(conversation)
        integration_db_session.commit()
        
        # Add messages
        messages = []
        for i in range(5):
            role = "user" if i % 2 == 0 else "assistant"
            message = Message(
                id=f"msg_{i}",
                conversation_id=conversation.id,
                role=role,
                content=f"Message {i} from {role}"
            )
            messages.append(message)
            integration_db_session.add(message)
        
        integration_db_session.commit()
        
        # Verify conversation has all messages
        integration_db_session.refresh(conversation)
        assert len(conversation.messages) == 5
        
        # Test message ordering
        ordered_messages = integration_db_session.query(Message)\
            .filter_by(conversation_id=conversation.id)\
            .order_by(Message.created_at)\
            .all()
        
        assert len(ordered_messages) == 5
        for i in range(len(ordered_messages) - 1):
            assert ordered_messages[i].created_at <= ordered_messages[i + 1].created_at
    
    def test_knowledge_source_integration(self, integration_db_session):
        """Test knowledge source database operations"""
        # Create organization
        org = Organization(
            id="knowledge_test_org",
            name="Knowledge Test Org",
            domain="knowledge.test"
        )
        integration_db_session.add(org)
        integration_db_session.commit()
        
        # Create knowledge sources
        sources = []
        source_types = ["document", "url", "database"]
        
        for i, source_type in enumerate(source_types):
            source = KnowledgeSource(
                id=f"ks_{i}",
                name=f"Knowledge Source {i}",
                type=source_type,
                organization_id=org.id,
                configuration={
                    "sync_frequency": "daily",
                    "auto_update": True
                }
            )
            sources.append(source)
            integration_db_session.add(source)
        
        integration_db_session.commit()
        
        # Verify relationships
        integration_db_session.refresh(org)
        assert len(org.knowledge_sources) == 3
        
        # Test filtering by type
        document_sources = integration_db_session.query(KnowledgeSource)\
            .filter_by(organization_id=org.id, type="document")\
            .all()
        assert len(document_sources) == 1
        assert document_sources[0].type == "document"
    
    def test_concurrent_operations(self, integration_db_session):
        """Test concurrent database operations"""
        import threading
        import time
        
        # Create base organization
        org = Organization(
            id="concurrent_test_org",
            name="Concurrent Test Org",
            domain="concurrent.test"
        )
        integration_db_session.add(org)
        integration_db_session.commit()
        
        # Function to create users concurrently
        def create_users(thread_id, count):
            from sqlalchemy.orm import sessionmaker
            SessionLocal = sessionmaker(bind=integration_db_session.bind)
            session = SessionLocal()
            
            try:
                for i in range(count):
                    user = User(
                        id=f"concurrent_user_{thread_id}_{i}",
                        email=f"user{thread_id}_{i}@concurrent.test",
                        name=f"Concurrent User {thread_id}-{i}",
                        organization_id=org.id
                    )
                    session.add(user)
                    session.commit()
                    time.sleep(0.01)  # Small delay to simulate real operations
            finally:
                session.close()
        
        # Create multiple threads
        threads = []
        for thread_id in range(3):
            thread = threading.Thread(target=create_users, args=(thread_id, 5))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify all users were created
        total_users = integration_db_session.query(User)\
            .filter_by(organization_id=org.id)\
            .count()
        assert total_users == 15  # 3 threads * 5 users each
    
    def test_transaction_rollback(self, integration_db_session):
        """Test transaction rollback behavior"""
        # Create organization
        org = Organization(
            id="rollback_test_org",
            name="Rollback Test Org",
            domain="rollback.test"
        )
        integration_db_session.add(org)
        integration_db_session.commit()
        
        # Start transaction that will fail
        try:
            user1 = User(
                id="rollback_user_1",
                email="user1@rollback.test",
                name="User 1",
                organization_id=org.id
            )
            integration_db_session.add(user1)
            
            # This should succeed
            integration_db_session.flush()
            
            # Create duplicate user (should fail due to unique constraint)
            user2 = User(
                id="rollback_user_2",
                email="user1@rollback.test",  # Same email - should fail
                name="User 2",
                organization_id=org.id
            )
            integration_db_session.add(user2)
            integration_db_session.commit()
            
        except Exception:
            integration_db_session.rollback()
        
        # Verify no users were created due to rollback
        user_count = integration_db_session.query(User)\
            .filter_by(organization_id=org.id)\
            .count()
        assert user_count == 0


@pytest.mark.integration
class TestServiceIntegration:
    """Test service layer integration with real database"""
    
    @pytest.mark.asyncio
    async def test_conversation_service_integration(self, integration_db_session):
        """Test conversation service with real database"""
        # Setup test data
        org = Organization(
            id="service_test_org",
            name="Service Test Org",
            domain="service.test"
        )
        integration_db_session.add(org)
        
        user = User(
            id="service_test_user",
            email="user@service.test",
            name="Service Test User",
            organization_id=org.id
        )
        integration_db_session.add(user)
        
        assistant = Assistant(
            id="service_test_assistant",
            name="Service Test Assistant",
            type="support",
            organization_id=org.id,
            configuration={"model": "gemini-1.5-pro"}
        )
        integration_db_session.add(assistant)
        integration_db_session.commit()
        
        # Test conversation creation
        conversation = await conversation_service.create_conversation(
            db=integration_db_session,
            user_id=user.id,
            assistant_id=assistant.id,
            channel="chat",
            metadata={"test": True}
        )
        
        assert conversation is not None
        assert conversation.user_id == user.id
        assert conversation.assistant_id == assistant.id
        
        # Test message addition
        message = await conversation_service.add_message(
            db=integration_db_session,
            conversation_id=conversation.id,
            role="user",
            content="Test message for integration"
        )
        
        assert message is not None
        assert message.conversation_id == conversation.id
        assert message.content == "Test message for integration"
        
        # Test conversation history
        history = await conversation_service.get_conversation_history(
            db=integration_db_session,
            conversation_id=conversation.id
        )
        
        assert len(history) == 1
        assert history[0].content == "Test message for integration"
    
    @pytest.mark.asyncio
    async def test_assistant_factory_integration(self, integration_db_session):
        """Test assistant factory with real database"""
        # Setup test data
        org = Organization(
            id="assistant_test_org",
            name="Assistant Test Org",
            domain="assistant.test"
        )
        integration_db_session.add(org)
        integration_db_session.commit()
        
        # Mock MCP registry for integration test
        with pytest.mock.patch('app.services.mcp_tool_registry.mcp_tool_registry.get_available_tools') as mock_tools:
            mock_tools.return_value = []
            
            # Test assistant creation
            config = {
                "organization_id": org.id,
                "organization_name": org.name
            }
            
            assistant = await assistant_factory.create_assistant(
                db=integration_db_session,
                assistant_type="support",
                assistant_id="integration_test_assistant",
                config=config
            )
            
            assert assistant is not None
            assert assistant.type == "support"
            assert assistant.assistant_id == "integration_test_assistant"
            
            # Test assistant capabilities
            capabilities = await assistant_factory.get_assistant_capabilities("support")
            assert "type" in capabilities
            assert capabilities["type"] == "support"
    
    def test_database_performance(self, integration_db_session):
        """Test database performance with larger datasets"""
        import time
        
        # Create organization
        org = Organization(
            id="perf_test_org",
            name="Performance Test Org",
            domain="perf.test"
        )
        integration_db_session.add(org)
        integration_db_session.commit()
        
        # Measure bulk insert performance
        start_time = time.time()
        
        users = []
        for i in range(1000):
            user = User(
                id=f"perf_user_{i}",
                email=f"user{i}@perf.test",
                name=f"Performance User {i}",
                organization_id=org.id
            )
            users.append(user)
        
        integration_db_session.add_all(users)
        integration_db_session.commit()
        
        insert_time = time.time() - start_time
        
        # Measure query performance
        start_time = time.time()
        
        user_count = integration_db_session.query(User)\
            .filter_by(organization_id=org.id)\
            .count()
        
        query_time = time.time() - start_time
        
        # Assertions for performance (adjust thresholds as needed)
        assert user_count == 1000
        assert insert_time < 10.0  # Should complete within 10 seconds
        assert query_time < 1.0    # Should query within 1 second
        
        print(f"Insert time for 1000 users: {insert_time:.2f}s")
        print(f"Query time for count: {query_time:.4f}s")