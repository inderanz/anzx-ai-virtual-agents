"""
API Integration Tests
Tests all API endpoints with real database and service interactions
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock

from app.models.user import User, Organization, Assistant, Conversation, Message


class TestAuthenticationEndpoints:
    """Test authentication and user management endpoints"""
    
    def test_register_user(self, test_client: TestClient, test_user_data):
        """Test user registration endpoint"""
        with patch('app.services.auth_service.firebase_auth') as mock_auth:
            mock_auth.create_user.return_value = {"uid": "test_uid"}
            
            response = test_client.post("/api/v1/auth/register", json=test_user_data)
            
            assert response.status_code == 201
            data = response.json()
            assert data["email"] == test_user_data["email"]
            assert "id" in data
    
    def test_login_user(self, test_client: TestClient):
        """Test user login endpoint"""
        login_data = {
            "email": "test@example.com",
            "password": "testpassword"
        }
        
        with patch('app.services.auth_service.firebase_auth') as mock_auth:
            mock_auth.sign_in_with_email_and_password.return_value = {
                "idToken": "test_token",
                "localId": "test_uid"
            }
            
            response = test_client.post("/api/v1/auth/login", json=login_data)
            
            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
            assert data["token_type"] == "bearer"
    
    def test_get_current_user(self, test_client: TestClient, auth_headers, test_db_session):
        """Test get current user endpoint"""
        # Create test user in database
        user = User(
            id="test_uid",
            email="test@example.com",
            full_name="Test User"
        )
        test_db_session.add(user)
        test_db_session.commit()
        
        with patch('app.services.auth_service.verify_token') as mock_verify:
            mock_verify.return_value = {"uid": "test_uid"}
            
            response = test_client.get("/api/v1/auth/me", headers=auth_headers)
            
            assert response.status_code == 200
            data = response.json()
            assert data["email"] == "test@example.com"


class TestOrganizationEndpoints:
    """Test organization management endpoints"""
    
    def test_create_organization(self, test_client: TestClient, auth_headers, test_organization_data, test_db_session):
        """Test organization creation endpoint"""
        # Create test user
        user = User(
            id="test_uid",
            email="test@example.com",
            full_name="Test User"
        )
        test_db_session.add(user)
        test_db_session.commit()
        
        with patch('app.services.auth_service.verify_token') as mock_verify:
            mock_verify.return_value = {"uid": "test_uid"}
            
            response = test_client.post(
                "/api/v1/organizations",
                json=test_organization_data,
                headers=auth_headers
            )
            
            assert response.status_code == 201
            data = response.json()
            assert data["name"] == test_organization_data["name"]
            assert "id" in data
    
    def test_get_organizations(self, test_client: TestClient, auth_headers, test_db_session):
        """Test get organizations endpoint"""
        # Create test user and organization
        user = User(
            id="test_uid",
            email="test@example.com",
            full_name="Test User"
        )
        org = Organization(
            name="Test Organization",
            domain="test.com",
            owner_id="test_uid"
        )
        test_db_session.add(user)
        test_db_session.add(org)
        test_db_session.commit()
        
        with patch('app.services.auth_service.verify_token') as mock_verify:
            mock_verify.return_value = {"uid": "test_uid"}
            
            response = test_client.get("/api/v1/organizations", headers=auth_headers)
            
            assert response.status_code == 200
            data = response.json()
            assert len(data) >= 1
            assert data[0]["name"] == "Test Organization"


class TestAssistantEndpoints:
    """Test assistant management endpoints"""
    
    def test_create_assistant(self, test_client: TestClient, auth_headers, test_assistant_data, test_db_session):
        """Test assistant creation endpoint"""
        # Create test user and organization
        user = User(
            id="test_uid",
            email="test@example.com",
            full_name="Test User"
        )
        org = Organization(
            name="Test Organization",
            domain="test.com",
            owner_id="test_uid"
        )
        test_db_session.add(user)
        test_db_session.add(org)
        test_db_session.commit()
        
        with patch('app.services.auth_service.verify_token') as mock_verify, \
             patch('app.services.assistant_factory.assistant_factory') as mock_factory:
            
            mock_verify.return_value = {"uid": "test_uid"}
            mock_factory.create_assistant = AsyncMock(return_value=type('MockAssistant', (), {
                'assistant_id': 'test_assistant',
                'type': 'support'
            })())
            
            response = test_client.post(
                f"/api/v1/organizations/{org.id}/assistants",
                json=test_assistant_data,
                headers=auth_headers
            )
            
            assert response.status_code == 201
            data = response.json()
            assert data["name"] == test_assistant_data["name"]
            assert data["type"] == test_assistant_data["type"]
    
    def test_get_assistants(self, test_client: TestClient, auth_headers, test_db_session):
        """Test get assistants endpoint"""
        # Create test data
        user = User(
            id="test_uid",
            email="test@example.com",
            full_name="Test User"
        )
        org = Organization(
            name="Test Organization",
            domain="test.com",
            owner_id="test_uid"
        )
        assistant = Assistant(
            name="Test Assistant",
            type="support",
            organization_id=org.id,
            is_active=True
        )
        test_db_session.add(user)
        test_db_session.add(org)
        test_db_session.add(assistant)
        test_db_session.commit()
        
        with patch('app.services.auth_service.verify_token') as mock_verify:
            mock_verify.return_value = {"uid": "test_uid"}
            
            response = test_client.get(
                f"/api/v1/organizations/{org.id}/assistants",
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert len(data) >= 1
            assert data[0]["name"] == "Test Assistant"


class TestConversationEndpoints:
    """Test conversation management endpoints"""
    
    def test_create_conversation(self, test_client: TestClient, auth_headers, test_conversation_data, test_db_session):
        """Test conversation creation endpoint"""
        # Create test data
        user = User(
            id="test_uid",
            email="test@example.com",
            full_name="Test User"
        )
        org = Organization(
            name="Test Organization",
            domain="test.com",
            owner_id="test_uid"
        )
        assistant = Assistant(
            name="Test Assistant",
            type="support",
            organization_id=org.id,
            is_active=True
        )
        test_db_session.add(user)
        test_db_session.add(org)
        test_db_session.add(assistant)
        test_db_session.commit()
        
        conversation_data = {
            **test_conversation_data,
            "assistant_id": assistant.id
        }
        
        with patch('app.services.auth_service.verify_token') as mock_verify:
            mock_verify.return_value = {"uid": "test_uid"}
            
            response = test_client.post(
                f"/api/v1/organizations/{org.id}/conversations",
                json=conversation_data,
                headers=auth_headers
            )
            
            assert response.status_code == 201
            data = response.json()
            assert data["title"] == test_conversation_data["title"]
            assert data["channel"] == test_conversation_data["channel"]
    
    def test_send_message(self, test_client: TestClient, auth_headers, test_db_session, mock_external_services):
        """Test sending message endpoint"""
        # Create test data
        user = User(
            id="test_uid",
            email="test@example.com",
            full_name="Test User"
        )
        org = Organization(
            name="Test Organization",
            domain="test.com",
            owner_id="test_uid"
        )
        assistant = Assistant(
            name="Test Assistant",
            type="support",
            organization_id=org.id,
            is_active=True
        )
        conversation = Conversation(
            title="Test Conversation",
            assistant_id=assistant.id,
            user_id="test_uid",
            organization_id=org.id
        )
        test_db_session.add(user)
        test_db_session.add(org)
        test_db_session.add(assistant)
        test_db_session.add(conversation)
        test_db_session.commit()
        
        message_data = {
            "content": "Hello, I need help",
            "role": "user"
        }
        
        with patch('app.services.auth_service.verify_token') as mock_verify, \
             patch('app.services.vertex_ai_service.vertex_ai_service') as mock_vertex:
            
            mock_verify.return_value = {"uid": "test_uid"}
            mock_vertex.generate_response = AsyncMock(
                return_value=mock_external_services["vertex_ai"]["generate_response"]
            )
            
            response = test_client.post(
                f"/api/v1/conversations/{conversation.id}/messages",
                json=message_data,
                headers=auth_headers
            )
            
            assert response.status_code == 201
            data = response.json()
            assert data["content"] == message_data["content"]
            assert data["role"] == message_data["role"]


class TestKnowledgeEndpoints:
    """Test knowledge management endpoints"""
    
    def test_upload_document(self, test_client: TestClient, auth_headers, test_db_session):
        """Test document upload endpoint"""
        # Create test data
        user = User(
            id="test_uid",
            email="test@example.com",
            full_name="Test User"
        )
        org = Organization(
            name="Test Organization",
            domain="test.com",
            owner_id="test_uid"
        )
        test_db_session.add(user)
        test_db_session.add(org)
        test_db_session.commit()
        
        # Mock file upload
        files = {
            "file": ("test.txt", b"Test document content", "text/plain")
        }
        
        with patch('app.services.auth_service.verify_token') as mock_verify, \
             patch('app.services.knowledge_service.process_document') as mock_process:
            
            mock_verify.return_value = {"uid": "test_uid"}
            mock_process.return_value = {
                "document_id": "doc_123",
                "status": "processed",
                "chunks": 5
            }
            
            response = test_client.post(
                f"/api/v1/organizations/{org.id}/knowledge/documents",
                files=files,
                headers={"Authorization": auth_headers["Authorization"]}
            )
            
            assert response.status_code == 201
            data = response.json()
            assert "document_id" in data
            assert data["status"] == "processed"
    
    def test_search_knowledge(self, test_client: TestClient, auth_headers, test_db_session):
        """Test knowledge search endpoint"""
        # Create test data
        user = User(
            id="test_uid",
            email="test@example.com",
            full_name="Test User"
        )
        org = Organization(
            name="Test Organization",
            domain="test.com",
            owner_id="test_uid"
        )
        test_db_session.add(user)
        test_db_session.add(org)
        test_db_session.commit()
        
        search_data = {
            "query": "test search query",
            "limit": 10
        }
        
        with patch('app.services.auth_service.verify_token') as mock_verify, \
             patch('app.services.knowledge_service.search_knowledge') as mock_search:
            
            mock_verify.return_value = {"uid": "test_uid"}
            mock_search.return_value = {
                "results": [
                    {
                        "content": "Test result content",
                        "score": 0.95,
                        "source": "test.txt"
                    }
                ],
                "total": 1
            }
            
            response = test_client.post(
                f"/api/v1/organizations/{org.id}/knowledge/search",
                json=search_data,
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "results" in data
            assert len(data["results"]) >= 1


class TestBillingEndpoints:
    """Test billing and subscription endpoints"""
    
    def test_create_subscription(self, test_client: TestClient, auth_headers, test_db_session, mock_external_services):
        """Test subscription creation endpoint"""
        # Create test data
        user = User(
            id="test_uid",
            email="test@example.com",
            full_name="Test User"
        )
        org = Organization(
            name="Test Organization",
            domain="test.com",
            owner_id="test_uid"
        )
        test_db_session.add(user)
        test_db_session.add(org)
        test_db_session.commit()
        
        subscription_data = {
            "plan": "professional",
            "payment_method": "pm_test123"
        }
        
        with patch('app.services.auth_service.verify_token') as mock_verify, \
             patch('app.services.stripe_service.stripe_service') as mock_stripe:
            
            mock_verify.return_value = {"uid": "test_uid"}
            mock_stripe.create_customer = AsyncMock(
                return_value=mock_external_services["stripe"]["create_customer"]
            )
            mock_stripe.create_subscription = AsyncMock(
                return_value=mock_external_services["stripe"]["create_subscription"]
            )
            
            response = test_client.post(
                f"/api/v1/organizations/{org.id}/billing/subscription",
                json=subscription_data,
                headers=auth_headers
            )
            
            assert response.status_code == 201
            data = response.json()
            assert data["plan"] == subscription_data["plan"]
            assert "subscription_id" in data
    
    def test_get_usage_metrics(self, test_client: TestClient, auth_headers, test_db_session):
        """Test usage metrics endpoint"""
        # Create test data
        user = User(
            id="test_uid",
            email="test@example.com",
            full_name="Test User"
        )
        org = Organization(
            name="Test Organization",
            domain="test.com",
            owner_id="test_uid"
        )
        test_db_session.add(user)
        test_db_session.add(org)
        test_db_session.commit()
        
        with patch('app.services.auth_service.verify_token') as mock_verify, \
             patch('app.services.usage_service.get_usage_metrics') as mock_usage:
            
            mock_verify.return_value = {"uid": "test_uid"}
            mock_usage.return_value = {
                "api_requests": 1500,
                "tokens_used": 50000,
                "conversations": 25,
                "period": "current_month"
            }
            
            response = test_client.get(
                f"/api/v1/organizations/{org.id}/billing/usage",
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "api_requests" in data
            assert "tokens_used" in data
            assert data["period"] == "current_month"


class TestHealthEndpoints:
    """Test health and status endpoints"""
    
    def test_health_check(self, test_client: TestClient):
        """Test health check endpoint"""
        response = test_client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
    
    def test_readiness_check(self, test_client: TestClient):
        """Test readiness check endpoint"""
        with patch('app.utils.database.engine') as mock_engine:
            mock_engine.execute.return_value = True
            
            response = test_client.get("/ready")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "ready"
            assert "services" in data