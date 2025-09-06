"""
Global pytest configuration and fixtures
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.main import app
from app.utils.database import get_db, Base
from app.models.user import User, Organization, Assistant, Conversation, Message
from app.services.vertex_ai_service import vertex_ai_service
from app.services.mcp_tool_registry import mcp_tool_registry
from app.services.agent_space_connector_manager import agent_space_connector_manager


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def db_session():
    """Create a fresh database session for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db_session):
    """Create a test client with database dependency override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
async def async_client(db_session):
    """Create an async test client."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(app=app, base_url="http://test") as async_test_client:
        yield async_test_client
    app.dependency_overrides.clear()


@pytest.fixture
def mock_vertex_ai():
    """Mock Vertex AI service."""
    with pytest.mock.patch.object(vertex_ai_service, 'generate_response') as mock:
        mock.return_value = {
            "content": "Test response from Vertex AI",
            "metadata": {
                "model": "gemini-1.5-pro",
                "tokens_used": 100
            }
        }
        yield mock


@pytest.fixture
def mock_mcp_registry():
    """Mock MCP tool registry."""
    with pytest.mock.patch.object(mcp_tool_registry, 'get_available_tools') as mock_get, \
         pytest.mock.patch.object(mcp_tool_registry, 'execute_tool') as mock_execute:
        
        mock_get.return_value = [
            {
                "tool_id": "test_tool",
                "name": "Test Tool",
                "description": "A test tool",
                "category": "general"
            }
        ]
        
        mock_execute.return_value = {
            "status": "success",
            "result": {"message": "Tool executed successfully"}
        }
        
        yield {"get_tools": mock_get, "execute_tool": mock_execute}


@pytest.fixture
def mock_agent_space():
    """Mock Agent Space connector manager."""
    with pytest.mock.patch.object(agent_space_connector_manager, 'initialize_agent') as mock_init, \
         pytest.mock.patch.object(agent_space_connector_manager, 'process_message') as mock_process:
        
        mock_init.return_value = {"status": "initialized"}
        mock_process.return_value = {
            "response": "Agent Space response",
            "metadata": {"agent_id": "test_agent"}
        }
        
        yield {"initialize": mock_init, "process": mock_process}


@pytest.fixture
def sample_organization(db_session):
    """Create a sample organization for testing."""
    org = Organization(
        id="test_org_123",
        name="Test Organization",
        domain="test.com",
        subscription_tier="professional",
        is_active=True
    )
    db_session.add(org)
    db_session.commit()
    db_session.refresh(org)
    return org


@pytest.fixture
def sample_user(db_session, sample_organization):
    """Create a sample user for testing."""
    user = User(
        id="test_user_123",
        email="test@test.com",
        name="Test User",
        organization_id=sample_organization.id,
        role="admin",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def sample_assistant(db_session, sample_organization):
    """Create a sample assistant for testing."""
    assistant = Assistant(
        id="test_assistant_123",
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
    db_session.refresh(assistant)
    return assistant


@pytest.fixture
def sample_conversation(db_session, sample_user, sample_assistant):
    """Create a sample conversation for testing."""
    conversation = Conversation(
        id="test_conv_123",
        user_id=sample_user.id,
        assistant_id=sample_assistant.id,
        channel="chat",
        status="active",
        metadata={"test": True}
    )
    db_session.add(conversation)
    db_session.commit()
    db_session.refresh(conversation)
    return conversation


@pytest.fixture
def sample_message(db_session, sample_conversation):
    """Create a sample message for testing."""
    message = Message(
        id="test_msg_123",
        conversation_id=sample_conversation.id,
        role="user",
        content="Test message content",
        metadata={"test": True}
    )
    db_session.add(message)
    db_session.commit()
    db_session.refresh(message)
    return message


@pytest.fixture
def auth_headers():
    """Create authentication headers for testing."""
    return {
        "Authorization": "Bearer test_token",
        "Content-Type": "application/json"
    }


@pytest.fixture
def mock_firebase_auth():
    """Mock Firebase authentication."""
    with pytest.mock.patch('app.utils.auth.verify_firebase_token') as mock:
        mock.return_value = {
            "uid": "test_user_123",
            "email": "test@test.com",
            "email_verified": True
        }
        yield mock


# Utility functions for tests
def create_test_data(db_session, **kwargs):
    """Helper function to create test data."""
    defaults = {
        "organization": {
            "id": "test_org",
            "name": "Test Org",
            "domain": "test.com"
        },
        "user": {
            "id": "test_user",
            "email": "test@test.com",
            "name": "Test User"
        }
    }
    
    # Merge with provided kwargs
    for key, value in kwargs.items():
        if key in defaults:
            defaults[key].update(value)
    
    return defaults


def assert_response_structure(response_data, expected_keys):
    """Assert that response has expected structure."""
    for key in expected_keys:
        assert key in response_data, f"Missing key: {key}"


def assert_database_state(db_session, model, expected_count, **filters):
    """Assert database state matches expectations."""
    query = db_session.query(model)
    for key, value in filters.items():
        query = query.filter(getattr(model, key) == value)
    
    actual_count = query.count()
    assert actual_count == expected_count, f"Expected {expected_count} {model.__name__} records, got {actual_count}"