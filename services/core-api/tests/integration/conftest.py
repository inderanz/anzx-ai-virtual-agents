"""
Integration Test Configuration
Sets up TestContainers and shared fixtures for integration testing
"""

import pytest
import asyncio
from typing import AsyncGenerator, Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer

from app.main import app
from app.utils.database import get_db, Base
from app.config.settings import get_settings


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def postgres_container():
    """Start PostgreSQL container for integration tests"""
    with PostgresContainer("postgres:15", driver="psycopg2") as postgres:
        # Add pgvector extension
        postgres.exec("apt-get update && apt-get install -y postgresql-15-pgvector")
        yield postgres


@pytest.fixture(scope="session")
def redis_container():
    """Start Redis container for integration tests"""
    with RedisContainer("redis:7-alpine") as redis:
        yield redis


@pytest.fixture(scope="session")
def test_database_url(postgres_container):
    """Get test database URL from container"""
    return postgres_container.get_connection_url()


@pytest.fixture(scope="session")
def test_redis_url(redis_container):
    """Get test Redis URL from container"""
    return f"redis://localhost:{redis_container.get_exposed_port(6379)}"


@pytest.fixture(scope="session")
def test_engine(test_database_url):
    """Create test database engine"""
    engine = create_engine(test_database_url)
    Base.metadata.create_all(bind=engine)
    yield engine
    engine.dispose()


@pytest.fixture(scope="session")
def test_session_factory(test_engine):
    """Create test session factory"""
    return sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture
def test_db_session(test_session_factory):
    """Create test database session"""
    session = test_session_factory()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def test_client(test_db_session, test_redis_url):
    """Create test client with dependency overrides"""
    
    def override_get_db():
        try:
            yield test_db_session
        finally:
            pass
    
    def override_get_settings():
        settings = get_settings()
        settings.redis_url = test_redis_url
        settings.testing = True
        return settings
    
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_settings] = override_get_settings
    
    with TestClient(app) as client:
        yield client
    
    app.dependency_overrides.clear()


@pytest.fixture
def test_user_data():
    """Sample user data for testing"""
    return {
        "email": "test@example.com",
        "full_name": "Test User",
        "organization_name": "Test Organization"
    }


@pytest.fixture
def test_organization_data():
    """Sample organization data for testing"""
    return {
        "name": "Test Organization",
        "domain": "test.com",
        "subscription_tier": "professional"
    }


@pytest.fixture
def test_assistant_data():
    """Sample assistant data for testing"""
    return {
        "name": "Test Assistant",
        "type": "support",
        "description": "Test support assistant",
        "capabilities": ["communication", "technical"],
        "is_active": True
    }


@pytest.fixture
def test_conversation_data():
    """Sample conversation data for testing"""
    return {
        "title": "Test Conversation",
        "channel": "chat",
        "status": "active"
    }


@pytest.fixture
def auth_headers():
    """Mock authentication headers for testing"""
    return {
        "Authorization": "Bearer test_token",
        "Content-Type": "application/json"
    }


@pytest.fixture
def mock_external_services():
    """Mock external service responses"""
    return {
        "vertex_ai": {
            "generate_response": {
                "content": "Test AI response",
                "metadata": {"model": "gemini-1.5-pro", "tokens": 50}
            }
        },
        "stripe": {
            "create_customer": {
                "id": "cus_test123",
                "email": "test@example.com"
            },
            "create_subscription": {
                "id": "sub_test123",
                "status": "active"
            }
        },
        "agent_space": {
            "create_agent": {
                "agent_id": "agent_test123",
                "status": "active"
            },
            "process_message": {
                "response": "Agent Space response",
                "metadata": {"agent_id": "agent_test123"}
            }
        }
    }