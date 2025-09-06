"""
Integration tests for API endpoints
"""

import pytest
from unittest.mock import patch, AsyncMock
from fastapi import status
import asyncio

from app.models.user import User, Organization, Assistant, Conversation


@pytest.mark.integration
class TestAuthenticationFlow:
    """Test complete authentication flow"""
    
    @patch('app.utils.auth.verify_firebase_token')
    def test_complete_auth_flow(self, mock_verify, client, db_session):
        """Test complete authentication flow from login to protected endpoints"""
        # Setup test data
        org = Organization(
            id="auth_test_org",
            name="Auth Test Organization",
            domain="authtest.com",
            subscription_tier="professional"
        )
        db_session.add(org)
        
        user = User(
            id="firebase_uid_auth_test",
            email="authtest@example.com",
            name="Auth Test User",
            organization_id=org.id,
            role="admin"
        )
        db_session.add(user)
        db_session.commit()
        
        # Mock Firebase token verification
        mock_verify.return_value = {
            "uid": "firebase_uid_auth_test",
            "email": "authtest@example.com",
            "email_verified": True
        }
        
        # Step 1: Login
        login_response = client.post(
            "/auth/login",
            json={"firebase_token": "valid_test_token"}
        )
        
        assert login_response.status_code == status.HTTP_200_OK
        login_data = login_response.json()
        assert "access_token" in login_data
        assert login_data["user"]["email"] == "authtest@example.com"
        
        # Step 2: Use token for protected endpoint
        auth_headers = {
            "Authorization": f"Bearer {login_data['access_token']}",
            "Content-Type": "application/json"
        }
        
        # Test accessing protected endpoint
        with patch('app.services.assistant_service.get_organization_assistants') as mock_assistants:
            mock_assistants.return_value = []
            
            protected_response = client.get("/assistants", headers=auth_headers)
            assert protected_response.status_code == status.HTTP_200_OK
        
        # Step 3: Logout
        logout_response = client.post("/auth/logout", headers=auth_headers)
        assert logout_response.status_code == status.HTTP_200_OK
    
    def test_invalid_token_flow(self, client):
        """Test authentication with invalid token"""
        # Try to access protected endpoint without token
        response = client.get("/assistants")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # Try with invalid token
        invalid_headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/assistants", headers=invalid_headers)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.integration
class TestConversationFlow:
    """Test complete conversation flow"""
    
    @patch('app.utils.auth.verify_firebase_token')
    def test_complete_conversation_flow(self, mock_verify, client, db_session):
        """Test complete conversation flow from creation to completion"""
        # Setup test data
        org = Organization(
            id="conv_flow_org",
            name="Conversation Flow Org",
            domain="convflow.com"
        )
        db_session.add(org)
        
        user = User(
            id="conv_flow_user",
            email="convflow@example.com",
            name="Conversation Flow User",
            organization_id=org.id
        )
        db_session.add(user)
        
        assistant = Assistant(
            id="conv_flow_assistant",
            name="Flow Test Assistant",
            type="support",
            organization_id=org.id,
            configuration={"model": "gemini-1.5-pro"}
        )
        db_session.add(assistant)
        db_session.commit()
        
        # Mock authentication
        mock_verify.return_value = {
            "uid": "conv_flow_user",
            "email": "convflow@example.com",
            "email_verified": True
        }
        
        # Login to get token
        login_response = client.post(
            "/auth/login",
            json={"firebase_token": "valid_token"}
        )
        auth_headers = {
            "Authorization": f"Bearer {login_response.json()['access_token']}",
            "Content-Type": "application/json"
        }
        
        # Step 1: Create conversation
        with patch('app.services.conversation_service.conversation_service.create_conversation') as mock_create:
            mock_conversation = Conversation(
                id="test_conv_flow",
                user_id=user.id,
                assistant_id=assistant.id,
                channel="chat",
                status="active"
            )
            mock_create.return_value = mock_conversation
            
            conv_response = client.post(
                "/conversations",
                json={
                    "assistant_id": assistant.id,
                    "channel": "chat",
                    "metadata": {"source": "integration_test"}
                },
                headers=auth_headers
            )
            
            assert conv_response.status_code == status.HTTP_201_CREATED
            conv_data = conv_response.json()
            conversation_id = conv_data["id"]
        
        # Step 2: Send messages
        with patch('app.services.conversation_service.conversation_service.add_message') as mock_add, \
             patch('app.services.conversation_service.conversation_service.process_message') as mock_process:
            
            mock_add.return_value = {
                "id": "msg_1",
                "conversation_id": conversation_id,
                "role": "user",
                "content": "Hello, I need help"
            }
            
            mock_process.return_value = {
                "response": "Hello! I'm here to help. What can I assist you with?",
                "metadata": {"assistant_type": "support"}
            }
            
            message_response = client.post(
                f"/conversations/{conversation_id}/messages",
                json={
                    "content": "Hello, I need help",
                    "metadata": {"timestamp": "2024-01-01T12:00:00Z"}
                },
                headers=auth_headers
            )
            
            assert message_response.status_code == status.HTTP_201_CREATED
            message_data = message_response.json()
            assert "user_message" in message_data
            assert "assistant_response" in message_data
        
        # Step 3: Get conversation history
        with patch('app.services.conversation_service.conversation_service.get_conversation_history') as mock_history:
            mock_history.return_value = [
                {
                    "id": "msg_1",
                    "role": "user",
                    "content": "Hello, I need help",
                    "created_at": "2024-01-01T12:00:00Z"
                },
                {
                    "id": "msg_2",
                    "role": "assistant",
                    "content": "Hello! I'm here to help. What can I assist you with?",
                    "created_at": "2024-01-01T12:00:01Z"
                }
            ]
            
            history_response = client.get(
                f"/conversations/{conversation_id}/messages",
                headers=auth_headers
            )
            
            assert history_response.status_code == status.HTTP_200_OK
            history_data = history_response.json()
            assert len(history_data) == 2
        
        # Step 4: Update conversation status
        with patch('app.services.conversation_service.conversation_service.update_conversation_status') as mock_update:
            mock_update.return_value = Conversation(
                id=conversation_id,
                user_id=user.id,
                assistant_id=assistant.id,
                channel="chat",
                status="completed"
            )
            
            status_response = client.patch(
                f"/conversations/{conversation_id}",
                json={"status": "completed"},
                headers=auth_headers
            )
            
            assert status_response.status_code == status.HTTP_200_OK
            status_data = status_response.json()
            assert status_data["status"] == "completed"


@pytest.mark.integration
class TestAssistantManagement:
    """Test assistant management flow"""
    
    @patch('app.utils.auth.verify_firebase_token')
    def test_assistant_crud_flow(self, mock_verify, client, db_session):
        """Test complete CRUD flow for assistants"""
        # Setup test data
        org = Organization(
            id="assistant_crud_org",
            name="Assistant CRUD Org",
            domain="assistantcrud.com"
        )
        db_session.add(org)
        
        user = User(
            id="assistant_crud_user",
            email="assistantcrud@example.com",
            name="Assistant CRUD User",
            organization_id=org.id,
            role="admin"
        )
        db_session.add(user)
        db_session.commit()
        
        # Mock authentication
        mock_verify.return_value = {
            "uid": "assistant_crud_user",
            "email": "assistantcrud@example.com",
            "email_verified": True
        }
        
        # Login
        login_response = client.post(
            "/auth/login",
            json={"firebase_token": "valid_token"}
        )
        auth_headers = {
            "Authorization": f"Bearer {login_response.json()['access_token']}",
            "Content-Type": "application/json"
        }
        
        # Step 1: Create assistant
        with patch('app.services.assistant_service.create_assistant') as mock_create:
            new_assistant = Assistant(
                id="new_assistant_123",
                name="Test Assistant",
                type="support",
                organization_id=org.id,
                configuration={
                    "model": "gemini-1.5-pro",
                    "temperature": 0.7,
                    "capabilities": ["communication", "technical"]
                },
                is_active=True
            )
            mock_create.return_value = new_assistant
            
            create_response = client.post(
                "/assistants",
                json={
                    "name": "Test Assistant",
                    "type": "support",
                    "configuration": {
                        "model": "gemini-1.5-pro",
                        "temperature": 0.7,
                        "capabilities": ["communication", "technical"]
                    }
                },
                headers=auth_headers
            )
            
            assert create_response.status_code == status.HTTP_201_CREATED
            create_data = create_response.json()
            assistant_id = create_data["id"]
        
        # Step 2: Get assistants
        with patch('app.services.assistant_service.get_organization_assistants') as mock_get:
            mock_get.return_value = [new_assistant]
            
            get_response = client.get("/assistants", headers=auth_headers)
            assert get_response.status_code == status.HTTP_200_OK
            get_data = get_response.json()
            assert len(get_data) == 1
            assert get_data[0]["name"] == "Test Assistant"
        
        # Step 3: Update assistant
        with patch('app.services.assistant_service.update_assistant') as mock_update:
            updated_assistant = Assistant(
                id=assistant_id,
                name="Updated Test Assistant",
                type="support",
                organization_id=org.id,
                configuration={
                    "model": "gemini-1.5-flash",
                    "temperature": 0.5
                },
                is_active=True
            )
            mock_update.return_value = updated_assistant
            
            update_response = client.put(
                f"/assistants/{assistant_id}",
                json={
                    "name": "Updated Test Assistant",
                    "configuration": {
                        "model": "gemini-1.5-flash",
                        "temperature": 0.5
                    }
                },
                headers=auth_headers
            )
            
            assert update_response.status_code == status.HTTP_200_OK
            update_data = update_response.json()
            assert update_data["name"] == "Updated Test Assistant"
        
        # Step 4: Delete assistant
        with patch('app.services.assistant_service.delete_assistant') as mock_delete:
            mock_delete.return_value = True
            
            delete_response = client.delete(
                f"/assistants/{assistant_id}",
                headers=auth_headers
            )
            
            assert delete_response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.integration
class TestKnowledgeManagement:
    """Test knowledge management flow"""
    
    @patch('app.utils.auth.verify_firebase_token')
    def test_knowledge_upload_and_search_flow(self, mock_verify, client, db_session):
        """Test complete knowledge upload and search flow"""
        # Setup test data
        org = Organization(
            id="knowledge_flow_org",
            name="Knowledge Flow Org",
            domain="knowledgeflow.com"
        )
        db_session.add(org)
        
        user = User(
            id="knowledge_flow_user",
            email="knowledgeflow@example.com",
            name="Knowledge Flow User",
            organization_id=org.id
        )
        db_session.add(user)
        db_session.commit()
        
        # Mock authentication
        mock_verify.return_value = {
            "uid": "knowledge_flow_user",
            "email": "knowledgeflow@example.com",
            "email_verified": True
        }
        
        # Login
        login_response = client.post(
            "/auth/login",
            json={"firebase_token": "valid_token"}
        )
        auth_headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}
        
        # Step 1: Create knowledge source
        with patch('app.services.knowledge_service.create_knowledge_source') as mock_create_source:
            mock_create_source.return_value = {
                "id": "ks_test_123",
                "name": "Test Knowledge Source",
                "type": "document",
                "status": "active"
            }
            
            source_response = client.post(
                "/knowledge/sources",
                json={
                    "name": "Test Knowledge Source",
                    "type": "document",
                    "configuration": {
                        "auto_sync": True,
                        "file_types": ["pdf", "docx", "txt"]
                    }
                },
                headers=auth_headers
            )
            
            assert source_response.status_code == status.HTTP_201_CREATED
            source_data = source_response.json()
            knowledge_source_id = source_data["id"]
        
        # Step 2: Upload document
        with patch('app.services.knowledge_service.process_document') as mock_process:
            mock_process.return_value = {
                "id": "doc_test_123",
                "filename": "test_document.pdf",
                "status": "processing",
                "chunks_created": 0
            }
            
            # Mock file upload
            files = {"file": ("test_document.pdf", b"fake pdf content", "application/pdf")}
            data = {"knowledge_source_id": knowledge_source_id}
            
            upload_response = client.post(
                "/knowledge/upload",
                files=files,
                data=data,
                headers={"Authorization": auth_headers["Authorization"]}
            )
            
            assert upload_response.status_code == status.HTTP_201_CREATED
            upload_data = upload_response.json()
            assert upload_data["filename"] == "test_document.pdf"
        
        # Step 3: Search knowledge
        with patch('app.services.knowledge_service.search_knowledge') as mock_search:
            mock_search.return_value = {
                "results": [
                    {
                        "content": "This is relevant content from the document",
                        "score": 0.95,
                        "source": "test_document.pdf",
                        "metadata": {"page": 1, "chunk_id": "chunk_1"}
                    },
                    {
                        "content": "Another relevant piece of content",
                        "score": 0.87,
                        "source": "test_document.pdf",
                        "metadata": {"page": 2, "chunk_id": "chunk_2"}
                    }
                ],
                "total": 2
            }
            
            search_response = client.post(
                "/knowledge/search",
                json={
                    "query": "How do I reset my password?",
                    "limit": 5,
                    "knowledge_source_ids": [knowledge_source_id]
                },
                headers=auth_headers
            )
            
            assert search_response.status_code == status.HTTP_200_OK
            search_data = search_response.json()
            assert len(search_data["results"]) == 2
            assert search_data["results"][0]["score"] == 0.95


@pytest.mark.integration
class TestWebhookIntegration:
    """Test webhook integration"""
    
    def test_stripe_webhook_integration(self, client):
        """Test Stripe webhook processing"""
        webhook_payload = {
            "id": "evt_test_webhook",
            "object": "event",
            "type": "invoice.payment_succeeded",
            "data": {
                "object": {
                    "id": "in_test_123",
                    "customer": "cus_test_123",
                    "amount_paid": 2000,
                    "currency": "usd",
                    "status": "paid"
                }
            }
        }
        
        with patch('app.services.stripe_service.stripe_service.handle_webhook') as mock_handle:
            mock_handle.return_value = {
                "status": "processed",
                "event_type": "invoice.payment_succeeded",
                "customer_id": "cus_test_123"
            }
            
            response = client.post(
                "/webhooks/stripe",
                json=webhook_payload,
                headers={
                    "stripe-signature": "test_signature",
                    "content-type": "application/json"
                }
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["status"] == "processed"
    
    def test_agent_space_webhook_integration(self, client):
        """Test Agent Space webhook processing"""
        webhook_payload = {
            "type": "conversation.completed",
            "agent_id": "agent_test_123",
            "conversation_id": "conv_test_123",
            "timestamp": "2024-01-01T12:00:00Z",
            "data": {
                "resolution": "resolved",
                "satisfaction_score": 4.5,
                "duration_minutes": 15
            }
        }
        
        with patch('app.services.agent_space_service.handle_webhook') as mock_handle:
            mock_handle.return_value = {
                "status": "processed",
                "conversation_updated": True
            }
            
            response = client.post(
                "/webhooks/agent-space",
                json=webhook_payload,
                headers={
                    "x-agent-space-signature": "test_signature",
                    "content-type": "application/json"
                }
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["status"] == "processed"


@pytest.mark.integration
class TestErrorHandlingIntegration:
    """Test error handling in integration scenarios"""
    
    def test_cascading_error_handling(self, client, auth_headers):
        """Test how errors cascade through the system"""
        # Test database connection error
        with patch('app.utils.database.get_db') as mock_db:
            mock_db.side_effect = Exception("Database connection failed")
            
            response = client.get("/conversations", headers=auth_headers)
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    
    def test_external_service_failure_handling(self, client, auth_headers):
        """Test handling of external service failures"""
        # Test Vertex AI service failure
        with patch('app.services.vertex_ai_service.vertex_ai_service.generate_response') as mock_vertex:
            mock_vertex.side_effect = Exception("Vertex AI service unavailable")
            
            # This would be called during message processing
            # The exact endpoint depends on your implementation
            response = client.post(
                "/conversations/test_conv/messages",
                json={"content": "Test message"},
                headers=auth_headers
            )
            
            # Should handle gracefully, not crash
            assert response.status_code in [status.HTTP_500_INTERNAL_SERVER_ERROR, status.HTTP_503_SERVICE_UNAVAILABLE]
    
    def test_rate_limiting_integration(self, client, auth_headers):
        """Test rate limiting behavior"""
        # Make multiple rapid requests
        responses = []
        for i in range(10):
            response = client.get("/assistants", headers=auth_headers)
            responses.append(response)
        
        # At least some requests should succeed
        success_count = sum(1 for r in responses if r.status_code == status.HTTP_200_OK)
        assert success_count > 0
        
        # If rate limiting is implemented, some might be rate limited
        rate_limited_count = sum(1 for r in responses if r.status_code == status.HTTP_429_TOO_MANY_REQUESTS)
        # This assertion depends on whether rate limiting is actually implemented
        # assert rate_limited_count >= 0