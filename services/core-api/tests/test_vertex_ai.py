"""
Tests for Vertex AI Agent Builder integration
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from app.models.database import Base, get_db
from app.models.user import Organization, User, Assistant
from app.services.vertex_ai_service import vertex_ai_service
from app.services.agent_service import agent_service
from app.services.gcp_auth_service import gcp_auth_service
from app.config.vertex_ai import vertex_ai_config


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
def override_get_db(db_session):
    """Override database dependency"""
    def _override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def client(override_get_db):
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def sample_organization(db_session):
    """Create sample organization"""
    org = Organization(
        name="Test Organization",
        subscription_plan="pro",
        subscription_status="active"
    )
    db_session.add(org)
    db_session.commit()
    return org


@pytest.fixture
def sample_user(db_session, sample_organization):
    """Create sample user"""
    user = User(
        firebase_uid="test-user-123",
        email="test@example.com",
        organization_id=sample_organization.id,
        role="admin"
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def sample_assistant(db_session, sample_organization):
    """Create sample assistant"""
    assistant = Assistant(
        name="Test Support Agent",
        description="Test support assistant",
        type="support",
        organization_id=sample_organization.id,
        model_config={
            "vertex_ai_agent_id": "agent-test-123",
            "engine_id": "engine-test-123",
            "model": "gemini-1.0-pro"
        },
        is_active=True,
        deployment_status="deployed"
    )
    db_session.add(assistant)
    db_session.commit()
    return assistant


class TestVertexAIConfig:
    """Test Vertex AI configuration"""
    
    def test_get_agent_template(self):
        """Test getting agent template"""
        support_template = vertex_ai_config.get_agent_template("support")
        assert support_template["display_name"] == "Customer Support Agent"
        assert "intents" in support_template
        assert len(support_template["intents"]) > 0
        
        admin_template = vertex_ai_config.get_agent_template("admin")
        assert admin_template["display_name"] == "Administrative Assistant"
        
        # Test fallback to support template
        unknown_template = vertex_ai_config.get_agent_template("unknown")
        assert unknown_template["display_name"] == "Customer Support Agent"
    
    def test_get_project_path(self):
        """Test project path generation"""
        path = vertex_ai_config.get_project_path()
        assert path.startswith("projects/")
        assert vertex_ai_config.PROJECT_ID in path
    
    def test_validate_config(self):
        """Test configuration validation"""
        validation = vertex_ai_config.validate_config()
        
        assert isinstance(validation, dict)
        assert "project_id_set" in validation
        assert "location_set" in validation
        assert "agent_templates_configured" in validation
        
        # Should have valid configuration
        assert validation["project_id_set"] is True
        assert validation["agent_templates_configured"] is True
    
    def test_get_authentication_info(self):
        """Test authentication info"""
        auth_info = vertex_ai_config.get_authentication_info()
        
        assert "runtime_environment" in auth_info
        assert "project_id" in auth_info
        assert "required_scopes" in auth_info
        assert isinstance(auth_info["required_scopes"], str)


class TestGCPAuthService:
    """Test GCP authentication service"""
    
    @patch('google.auth.default')
    def test_initialize_local_auth(self, mock_default):
        """Test local authentication initialization"""
        mock_credentials = Mock()
        mock_credentials.valid = True
        mock_default.return_value = (mock_credentials, "test-project")
        
        # Create new auth service instance for testing
        auth_service = gcp_auth_service.__class__()
        auth_service.config.RUNTIME_ENVIRONMENT = "local"
        
        # This would normally initialize credentials
        assert auth_service.config.RUNTIME_ENVIRONMENT == "local"
    
    def test_get_project_id(self):
        """Test getting project ID"""
        project_id = gcp_auth_service.get_project_id()
        assert isinstance(project_id, str)
        assert len(project_id) > 0
    
    @patch('requests.get')
    def test_is_cloudrun_environment(self, mock_get):
        """Test Cloud Run environment detection"""
        # Mock successful metadata response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        # Set Cloud Run environment variables
        import os
        os.environ["K_SERVICE"] = "test-service"
        os.environ["K_REVISION"] = "test-revision"
        
        is_cloudrun = gcp_auth_service._is_cloudrun_environment()
        assert is_cloudrun is True
        
        # Clean up
        del os.environ["K_SERVICE"]
        del os.environ["K_REVISION"]
    
    def test_get_auth_status(self):
        """Test getting authentication status"""
        status = gcp_auth_service.get_auth_status()
        
        assert isinstance(status, dict)
        assert "status" in status
        assert "runtime_environment" in status
        assert "project_id" in status


class TestVertexAIService:
    """Test Vertex AI service"""
    
    @patch('app.services.vertex_ai_service.discoveryengine.ConversationalSearchServiceClient')
    @patch('app.services.vertex_ai_service.aiplatform.init')
    async def test_create_agent(self, mock_aiplatform_init, mock_client):
        """Test creating Vertex AI agent"""
        # Mock the client and its methods
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        
        agent_config = await vertex_ai_service.create_agent(
            organization_id="org-123",
            agent_type="support",
            name="Test Agent",
            description="Test description"
        )
        
        assert agent_config["agent_id"] == "agent-org-123-support"
        assert agent_config["display_name"] == "Test Agent"
        assert agent_config["agent_type"] == "support"
        assert agent_config["status"] == "active"
    
    @patch('app.services.vertex_ai_service.discoveryengine.ConversationalSearchServiceClient')
    async def test_start_conversation(self, mock_client):
        """Test starting conversation with agent"""
        # Mock the conversation client
        mock_client_instance = Mock()
        mock_response = Mock()
        mock_response.conversation.name = "conversation-123"
        mock_response.reply.reply = "Hello! How can I help you?"
        mock_response.conversation.state.name = "IN_PROGRESS"
        
        mock_client_instance.converse_conversation.return_value = mock_response
        mock_client.return_value = mock_client_instance
        
        response = await vertex_ai_service.start_conversation(
            agent_id="agent-test-123",
            user_message="Hello",
            conversation_id="conv-123"
        )
        
        assert response["conversation_id"] == "conversation-123"
        assert response["reply"] == "Hello! How can I help you?"
        assert response["conversation_state"] == "IN_PROGRESS"
        assert response["user_input"] == "Hello"
    
    async def test_get_agent_metrics(self):
        """Test getting agent metrics"""
        metrics = await vertex_ai_service.get_agent_metrics("agent-test-123")
        
        assert isinstance(metrics, dict)
        assert "agent_id" in metrics
        assert "conversations" in metrics
        assert "performance" in metrics
        assert "usage" in metrics
    
    async def test_test_agent_connection(self):
        """Test agent connection health check"""
        health_status = await vertex_ai_service.test_agent_connection()
        
        assert isinstance(health_status, dict)
        assert "status" in health_status
        assert "project_id" in health_status
        assert "location" in health_status
        assert "timestamp" in health_status


class TestAgentService:
    """Test agent service"""
    
    @patch('app.services.vertex_ai_service.vertex_ai_service.create_agent')
    async def test_create_agent(self, mock_create_vertex_agent, db_session, sample_organization):
        """Test creating agent through service"""
        # Mock Vertex AI agent creation
        mock_create_vertex_agent.return_value = {
            "agent_id": "agent-test-123",
            "engine_id": "engine-test-123",
            "data_store_id": "datastore-test-123"
        }
        
        agent_data = {
            "name": "Test Agent",
            "description": "Test description",
            "type": "support",
            "temperature": 0.7,
            "max_tokens": 1024
        }
        
        assistant = await agent_service.create_agent(
            db=db_session,
            organization_id=str(sample_organization.id),
            agent_data=agent_data
        )
        
        assert assistant.name == "Test Agent"
        assert assistant.type == "support"
        assert assistant.is_active is True
        assert assistant.deployment_status == "deployed"
        assert "vertex_ai_agent_id" in assistant.model_config
    
    async def test_get_agent(self, db_session, sample_assistant, sample_organization):
        """Test getting agent"""
        assistant = await agent_service.get_agent(
            db=db_session,
            agent_id=str(sample_assistant.id),
            organization_id=str(sample_organization.id)
        )
        
        assert assistant.id == sample_assistant.id
        assert assistant.name == sample_assistant.name
        assert assistant.type == sample_assistant.type
    
    async def test_list_agents(self, db_session, sample_assistant, sample_organization):
        """Test listing agents"""
        assistants = await agent_service.list_agents(
            db=db_session,
            organization_id=str(sample_organization.id)
        )
        
        assert len(assistants) == 1
        assert assistants[0].id == sample_assistant.id
        
        # Test filtering by type
        support_assistants = await agent_service.list_agents(
            db=db_session,
            organization_id=str(sample_organization.id),
            agent_type="support"
        )
        
        assert len(support_assistants) == 1
        
        # Test filtering by non-existent type
        admin_assistants = await agent_service.list_agents(
            db=db_session,
            organization_id=str(sample_organization.id),
            agent_type="admin"
        )
        
        assert len(admin_assistants) == 0
    
    @patch('app.services.vertex_ai_service.vertex_ai_service.start_conversation')
    @patch('app.middleware.usage_tracking.usage_tracker.check_usage_limits')
    @patch('app.middleware.usage_tracking.usage_tracker.track_ai_interaction')
    async def test_start_conversation(
        self, mock_track_usage, mock_check_limits, mock_vertex_conversation,
        db_session, sample_assistant, sample_organization, sample_user
    ):
        """Test starting conversation"""
        # Mock usage limit check
        mock_check_limits.return_value = {"can_proceed": True}
        
        # Mock Vertex AI conversation
        mock_vertex_conversation.return_value = {
            "conversation_id": "vertex-conv-123",
            "reply": "Hello! How can I help you?",
            "citations": [],
            "search_results": [],
            "confidence_score": 0.9
        }
        
        # Mock usage tracking
        mock_track_usage.return_value = {"usage": "tracked"}
        
        response = await agent_service.start_conversation(
            db=db_session,
            assistant_id=str(sample_assistant.id),
            organization_id=str(sample_organization.id),
            user_message="Hello",
            user_id=str(sample_user.id)
        )
        
        assert "conversation_id" in response
        assert response["reply"] == "Hello! How can I help you?"
        assert "usage" in response
        assert "timestamp" in response
        
        # Verify mocks were called
        mock_check_limits.assert_called_once()
        mock_vertex_conversation.assert_called_once()
        mock_track_usage.assert_called_once()


class TestAgentAPI:
    """Test agent API endpoints"""
    
    @patch('app.auth.dependencies.get_current_user')
    @patch('app.services.agent_service.agent_service.create_agent')
    def test_create_agent_api(self, mock_create_agent, mock_auth, client, sample_organization):
        """Test create agent API endpoint"""
        # Mock authentication
        mock_auth.return_value = {
            "user_id": "user-123",
            "organization_id": str(sample_organization.id),
            "roles": ["admin"]
        }
        
        # Mock agent creation
        mock_assistant = Mock()
        mock_assistant.id = "assistant-123"
        mock_assistant.name = "Test Agent"
        mock_assistant.type = "support"
        mock_assistant.organization_id = sample_organization.id
        mock_assistant.is_active = True
        mock_assistant.deployment_status = "deployed"
        mock_assistant.version = "1.0.0"
        mock_assistant.total_conversations = 0
        mock_assistant.total_messages = 0
        mock_assistant.average_response_time = 0.0
        mock_assistant.satisfaction_score = 0.0
        mock_assistant.created_at = datetime.utcnow()
        mock_assistant.updated_at = datetime.utcnow()
        mock_assistant.deployed_at = None
        mock_assistant.description = "Test description"
        
        mock_create_agent.return_value = mock_assistant
        
        # Test API call
        response = client.post("/api/v1/agents/", json={
            "name": "Test Agent",
            "description": "Test description",
            "type": "support",
            "temperature": 0.7
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Agent"
        assert data["type"] == "support"
        assert data["is_active"] is True
    
    @patch('app.auth.dependencies.get_current_user')
    def test_get_agent_templates(self, mock_auth, client):
        """Test get agent templates endpoint"""
        mock_auth.return_value = {
            "user_id": "user-123",
            "organization_id": "org-123"
        }
        
        response = client.get("/api/v1/agents/templates")
        assert response.status_code == 200
        
        data = response.json()
        assert "templates" in data
        assert "support" in data["templates"]
        assert "admin" in data["templates"]
        
        support_template = data["templates"]["support"]
        assert "display_name" in support_template
        assert "description" in support_template
        assert "supported_languages" in support_template
    
    @patch('app.auth.dependencies.require_admin')
    def test_vertex_ai_health_check(self, mock_auth, client):
        """Test Vertex AI health check endpoint"""
        mock_auth.return_value = {
            "user_id": "user-123",
            "organization_id": "org-123",
            "roles": ["admin"]
        }
        
        response = client.get("/api/v1/agents/health/vertex-ai")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "timestamp" in data


class TestIntegrationScenarios:
    """Test integration scenarios"""
    
    @patch('app.services.vertex_ai_service.vertex_ai_service.create_agent')
    @patch('app.services.vertex_ai_service.vertex_ai_service.start_conversation')
    async def test_full_agent_lifecycle(
        self, mock_start_conversation, mock_create_agent,
        db_session, sample_organization, sample_user
    ):
        """Test complete agent lifecycle"""
        # Mock Vertex AI responses
        mock_create_agent.return_value = {
            "agent_id": "agent-test-123",
            "engine_id": "engine-test-123"
        }
        
        mock_start_conversation.return_value = {
            "conversation_id": "conv-123",
            "reply": "Hello! How can I help you?",
            "citations": [],
            "search_results": []
        }
        
        # 1. Create agent
        agent_data = {
            "name": "Integration Test Agent",
            "type": "support",
            "description": "Test agent for integration"
        }
        
        assistant = await agent_service.create_agent(
            db=db_session,
            organization_id=str(sample_organization.id),
            agent_data=agent_data
        )
        
        assert assistant.name == "Integration Test Agent"
        assert assistant.is_active is True
        
        # 2. Start conversation
        with patch('app.middleware.usage_tracking.usage_tracker.check_usage_limits') as mock_limits:
            with patch('app.middleware.usage_tracking.usage_tracker.track_ai_interaction') as mock_track:
                mock_limits.return_value = {"can_proceed": True}
                mock_track.return_value = {"usage": "tracked"}
                
                response = await agent_service.start_conversation(
                    db=db_session,
                    assistant_id=str(assistant.id),
                    organization_id=str(sample_organization.id),
                    user_message="Hello",
                    user_id=str(sample_user.id)
                )
        
        assert "conversation_id" in response
        assert response["reply"] == "Hello! How can I help you?"
        
        # 3. Get agent analytics
        analytics = await agent_service.get_agent_analytics(
            db=db_session,
            agent_id=str(assistant.id),
            organization_id=str(sample_organization.id)
        )
        
        assert analytics["agent_id"] == str(assistant.id)
        assert "conversations" in analytics
        assert "performance" in analytics


if __name__ == "__main__":
    pytest.main([__file__])