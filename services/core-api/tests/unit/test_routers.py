"""
Unit tests for API routers
"""

import pytest
from unittest.mock import patch, AsyncMock
from fastapi import status

from app.models.user import User, Organization, Assistant, Conversation


@pytest.mark.unit
class TestAuthRouter:
    """Test authentication router endpoints"""
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "healthy"
    
    @patch('app.utils.auth.verify_firebase_token')
    def test_login_success(self, mock_verify, client, db_session, sample_organization):
        """Test successful login"""
        # Mock Firebase token verification
        mock_verify.return_value = {
            "uid": "firebase_uid_123",
            "email": "test@test.com",
            "email_verified": True
        }
        
        # Create user in database
        user = User(
            id="firebase_uid_123",
            email="test@test.com",
            name="Test User",
            organization_id=sample_organization.id
        )
        db_session.add(user)
        db_session.commit()
        
        response = client.post(
            "/auth/login",
            json={"firebase_token": "valid_token"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["user"]["email"] == "test@test.com"
    
    @patch('app.utils.auth.verify_firebase_token')
    def test_login_invalid_token(self, mock_verify, client):
        """Test login with invalid token"""
        mock_verify.side_effect = Exception("Invalid token")
        
        response = client.post(
            "/auth/login",
            json={"firebase_token": "invalid_token"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_logout(self, client, auth_headers):
        """Test logout endpoint"""
        response = client.post("/auth/logout", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["message"] == "Logged out successfully"


@pytest.mark.unit
class TestConversationRouter:
    """Test conversation router endpoints"""
    
    def test_create_conversation(self, client, auth_headers, mock_firebase_auth, sample_user, sample_assistant):
        """Test creating a new conversation"""
        conversation_data = {
            "assistant_id": sample_assistant.id,
            "channel": "chat",
            "metadata": {"source": "web_widget"}
        }
        
        with patch('app.services.conversation_service.conversation_service.create_conversation') as mock_create:
            mock_create.return_value = Conversation(
                id="test_conv_123",
                user_id=sample_user.id,
                assistant_id=sample_assistant.id,
                channel="chat",
                status="active"
            )
            
            response = client.post(
                "/conversations",
                json=conversation_data,
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            assert data["id"] == "test_conv_123"
            assert data["assistant_id"] == sample_assistant.id
            assert data["channel"] == "chat"
    
    def test_get_conversations(self, client, auth_headers, mock_firebase_auth, sample_user):
        """Test getting user conversations"""
        with patch('app.services.conversation_service.conversation_service.get_user_conversations') as mock_get:
            mock_get.return_value = [
                Conversation(
                    id="conv_1",
                    user_id=sample_user.id,
                    assistant_id="assistant_1",
                    channel="chat",
                    status="active"
                ),
                Conversation(
                    id="conv_2",
                    user_id=sample_user.id,
                    assistant_id="assistant_2",
                    channel="email",
                    status="completed"
                )
            ]
            
            response = client.get("/conversations", headers=auth_headers)
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert len(data) == 2
            assert data[0]["id"] == "conv_1"
            assert data[1]["id"] == "conv_2"
    
    def test_send_message(self, client, auth_headers, mock_firebase_auth, sample_conversation, mock_vertex_ai):
        """Test sending a message in conversation"""
        message_data = {
            "content": "Hello, I need help with my account",
            "metadata": {"timestamp": "2024-01-01T12:00:00Z"}
        }
        
        with patch('app.services.conversation_service.conversation_service.add_message') as mock_add, \
             patch('app.services.conversation_service.conversation_service.process_message') as mock_process:
            
            mock_add.return_value = {
                "id": "msg_123",
                "conversation_id": sample_conversation.id,
                "role": "user",
                "content": message_data["content"]
            }
            
            mock_process.return_value = {
                "response": "I'd be happy to help you with your account. What specific issue are you experiencing?",
                "metadata": {"assistant_type": "support"}
            }
            
            response = client.post(
                f"/conversations/{sample_conversation.id}/messages",
                json=message_data,
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            assert "user_message" in data
            assert "assistant_response" in data
            assert data["user_message"]["content"] == message_data["content"]
    
    def test_get_conversation_history(self, client, auth_headers, mock_firebase_auth, sample_conversation):
        """Test getting conversation history"""
        with patch('app.services.conversation_service.conversation_service.get_conversation_history') as mock_history:
            mock_history.return_value = [
                {
                    "id": "msg_1",
                    "role": "user",
                    "content": "Hello",
                    "created_at": "2024-01-01T12:00:00Z"
                },
                {
                    "id": "msg_2",
                    "role": "assistant",
                    "content": "Hi! How can I help you?",
                    "created_at": "2024-01-01T12:00:01Z"
                }
            ]
            
            response = client.get(
                f"/conversations/{sample_conversation.id}/messages",
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert len(data) == 2
            assert data[0]["role"] == "user"
            assert data[1]["role"] == "assistant"


@pytest.mark.unit
class TestAssistantRouter:
    """Test assistant router endpoints"""
    
    def test_get_assistants(self, client, auth_headers, mock_firebase_auth, sample_organization):
        """Test getting organization assistants"""
        with patch('app.services.assistant_service.get_organization_assistants') as mock_get:
            mock_get.return_value = [
                Assistant(
                    id="assistant_1",
                    name="Support Assistant",
                    type="support",
                    organization_id=sample_organization.id,
                    is_active=True
                ),
                Assistant(
                    id="assistant_2",
                    name="Sales Assistant",
                    type="sales",
                    organization_id=sample_organization.id,
                    is_active=True
                )
            ]
            
            response = client.get("/assistants", headers=auth_headers)
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert len(data) == 2
            assert data[0]["name"] == "Support Assistant"
            assert data[1]["name"] == "Sales Assistant"
    
    def test_create_assistant(self, client, auth_headers, mock_firebase_auth, sample_organization):
        """Test creating a new assistant"""
        assistant_data = {
            "name": "Custom Assistant",
            "type": "support",
            "configuration": {
                "model": "gemini-1.5-pro",
                "temperature": 0.7,
                "capabilities": ["communication", "technical"]
            }
        }
        
        with patch('app.services.assistant_service.create_assistant') as mock_create:
            mock_create.return_value = Assistant(
                id="new_assistant_123",
                name=assistant_data["name"],
                type=assistant_data["type"],
                organization_id=sample_organization.id,
                configuration=assistant_data["configuration"],
                is_active=True
            )
            
            response = client.post(
                "/assistants",
                json=assistant_data,
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            assert data["name"] == "Custom Assistant"
            assert data["type"] == "support"
            assert data["configuration"]["model"] == "gemini-1.5-pro"
    
    def test_update_assistant(self, client, auth_headers, mock_firebase_auth, sample_assistant):
        """Test updating an assistant"""
        update_data = {
            "name": "Updated Assistant Name",
            "configuration": {
                "model": "gemini-1.5-flash",
                "temperature": 0.5
            }
        }
        
        with patch('app.services.assistant_service.update_assistant') as mock_update:
            updated_assistant = Assistant(
                id=sample_assistant.id,
                name=update_data["name"],
                type=sample_assistant.type,
                organization_id=sample_assistant.organization_id,
                configuration=update_data["configuration"],
                is_active=True
            )
            mock_update.return_value = updated_assistant
            
            response = client.put(
                f"/assistants/{sample_assistant.id}",
                json=update_data,
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["name"] == "Updated Assistant Name"
            assert data["configuration"]["model"] == "gemini-1.5-flash"
    
    def test_delete_assistant(self, client, auth_headers, mock_firebase_auth, sample_assistant):
        """Test deleting an assistant"""
        with patch('app.services.assistant_service.delete_assistant') as mock_delete:
            mock_delete.return_value = True
            
            response = client.delete(
                f"/assistants/{sample_assistant.id}",
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.unit
class TestKnowledgeRouter:
    """Test knowledge router endpoints"""
    
    def test_upload_document(self, client, auth_headers, mock_firebase_auth):
        """Test uploading a document"""
        with patch('app.services.knowledge_service.process_document') as mock_process:
            mock_process.return_value = {
                "id": "doc_123",
                "filename": "test.pdf",
                "status": "processing",
                "chunks_created": 0
            }
            
            # Mock file upload
            files = {"file": ("test.pdf", b"fake pdf content", "application/pdf")}
            data = {"knowledge_source_id": "ks_123"}
            
            response = client.post(
                "/knowledge/upload",
                files=files,
                data=data,
                headers={"Authorization": auth_headers["Authorization"]}
            )
            
            assert response.status_code == status.HTTP_201_CREATED
            result = response.json()
            assert result["filename"] == "test.pdf"
            assert result["status"] == "processing"
    
    def test_search_knowledge(self, client, auth_headers, mock_firebase_auth):
        """Test searching knowledge base"""
        search_data = {
            "query": "How do I reset my password?",
            "limit": 5,
            "knowledge_source_ids": ["ks_123"]
        }
        
        with patch('app.services.knowledge_service.search_knowledge') as mock_search:
            mock_search.return_value = {
                "results": [
                    {
                        "content": "To reset your password, go to settings...",
                        "score": 0.95,
                        "source": "user_manual.pdf",
                        "metadata": {"page": 15}
                    }
                ],
                "total": 1
            }
            
            response = client.post(
                "/knowledge/search",
                json=search_data,
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert len(data["results"]) == 1
            assert data["results"][0]["score"] == 0.95
    
    def test_get_knowledge_sources(self, client, auth_headers, mock_firebase_auth, sample_organization):
        """Test getting knowledge sources"""
        with patch('app.services.knowledge_service.get_knowledge_sources') as mock_get:
            mock_get.return_value = [
                {
                    "id": "ks_1",
                    "name": "User Manual",
                    "type": "document",
                    "status": "active",
                    "document_count": 5
                },
                {
                    "id": "ks_2",
                    "name": "FAQ Website",
                    "type": "url",
                    "status": "syncing",
                    "document_count": 12
                }
            ]
            
            response = client.get("/knowledge/sources", headers=auth_headers)
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert len(data) == 2
            assert data[0]["name"] == "User Manual"
            assert data[1]["name"] == "FAQ Website"


@pytest.mark.unit
class TestWebhookRouter:
    """Test webhook router endpoints"""
    
    def test_stripe_webhook(self, client):
        """Test Stripe webhook handling"""
        webhook_data = {
            "type": "invoice.payment_succeeded",
            "data": {
                "object": {
                    "id": "in_test123",
                    "customer": "cus_test123",
                    "amount_paid": 2000
                }
            }
        }
        
        with patch('app.services.stripe_service.stripe_service.handle_webhook') as mock_handle:
            mock_handle.return_value = {"status": "processed"}
            
            response = client.post(
                "/webhooks/stripe",
                json=webhook_data,
                headers={"stripe-signature": "test_signature"}
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["status"] == "processed"
    
    def test_agent_space_webhook(self, client):
        """Test Agent Space webhook handling"""
        webhook_data = {
            "type": "conversation.completed",
            "agent_id": "agent_123",
            "conversation_id": "conv_123",
            "data": {
                "resolution": "resolved",
                "satisfaction_score": 4.5
            }
        }
        
        with patch('app.services.agent_space_service.handle_webhook') as mock_handle:
            mock_handle.return_value = {"status": "processed"}
            
            response = client.post(
                "/webhooks/agent-space",
                json=webhook_data,
                headers={"x-agent-space-signature": "test_signature"}
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["status"] == "processed"


@pytest.mark.unit
class TestErrorHandling:
    """Test API error handling"""
    
    def test_404_not_found(self, client):
        """Test 404 error handling"""
        response = client.get("/nonexistent-endpoint")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "detail" in data
    
    def test_422_validation_error(self, client, auth_headers):
        """Test validation error handling"""
        # Send invalid data
        invalid_data = {
            "invalid_field": "invalid_value"
        }
        
        response = client.post(
            "/conversations",
            json=invalid_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert "detail" in data
    
    def test_401_unauthorized(self, client):
        """Test unauthorized access"""
        response = client.get("/conversations")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert "detail" in data
    
    def test_500_internal_server_error(self, client, auth_headers, mock_firebase_auth):
        """Test internal server error handling"""
        with patch('app.services.conversation_service.conversation_service.get_user_conversations') as mock_get:
            mock_get.side_effect = Exception("Database connection failed")
            
            response = client.get("/conversations", headers=auth_headers)
            
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            data = response.json()
            assert "detail" in data