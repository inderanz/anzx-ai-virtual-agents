"""
Tests for authentication system
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from main import app
from app.auth.jwt_handler import jwt_handler
from app.auth.firebase import firebase_auth


client = TestClient(app)


class TestJWTHandler:
    """Test JWT token handling"""
    
    def test_create_access_token(self):
        """Test JWT access token creation"""
        token = jwt_handler.create_access_token(
            user_id="test-user-123",
            email="test@example.com",
            organization_id="org-123",
            roles=["user"]
        )
        
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_verify_valid_token(self):
        """Test JWT token verification with valid token"""
        token = jwt_handler.create_access_token(
            user_id="test-user-123",
            email="test@example.com",
            organization_id="org-123",
            roles=["user"]
        )
        
        payload = jwt_handler.verify_token(token)
        
        assert payload["sub"] == "test-user-123"
        assert payload["email"] == "test@example.com"
        assert payload["org_id"] == "org-123"
        assert payload["roles"] == ["user"]
        assert payload["type"] == "access"
    
    def test_verify_invalid_token(self):
        """Test JWT token verification with invalid token"""
        with pytest.raises(Exception):
            jwt_handler.verify_token("invalid-token")
    
    def test_create_refresh_token(self):
        """Test refresh token creation"""
        token = jwt_handler.create_refresh_token("test-user-123")
        
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_verify_refresh_token(self):
        """Test refresh token verification"""
        token = jwt_handler.create_refresh_token("test-user-123")
        user_id = jwt_handler.verify_refresh_token(token)
        
        assert user_id == "test-user-123"


class TestAuthEndpoints:
    """Test authentication API endpoints"""
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] in ["healthy", "unhealthy"]
        assert data["service"] == "core-api"
        assert "checks" in data
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "ANZx.ai Core API"
        assert data["status"] == "healthy"
        assert data["version"] == "1.0.0"
    
    @patch('app.auth.firebase.firebase_auth.verify_token')
    @patch('app.models.database.get_db')
    def test_login_endpoint_user_not_found(self, mock_db, mock_verify_token):
        """Test login endpoint when user not found"""
        # Mock Firebase token verification
        mock_verify_token.return_value = {
            "uid": "firebase-uid-123",
            "email": "test@example.com",
            "email_verified": True,
            "name": "Test User",
            "picture": None,
            "provider": "google.com"
        }
        
        # Mock database session
        mock_session = Mock()
        mock_session.query.return_value.filter.return_value.first.return_value = None
        mock_db.return_value = mock_session
        
        response = client.post("/api/v1/auth/login", json={
            "firebase_token": "mock-firebase-token"
        })
        
        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]
    
    def test_protected_endpoint_without_token(self):
        """Test protected endpoint without authentication token"""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 403  # No authorization header
    
    def test_protected_endpoint_with_invalid_token(self):
        """Test protected endpoint with invalid token"""
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid-token"}
        )
        assert response.status_code == 401


class TestFirebaseAuth:
    """Test Firebase authentication integration"""
    
    @patch('firebase_admin.auth.verify_id_token')
    async def test_verify_token_success(self, mock_verify):
        """Test successful Firebase token verification"""
        mock_verify.return_value = {
            "uid": "firebase-uid-123",
            "email": "test@example.com",
            "email_verified": True,
            "name": "Test User",
            "picture": "https://example.com/photo.jpg",
            "firebase": {"sign_in_provider": "google.com"}
        }
        
        result = await firebase_auth.verify_token("mock-token")
        
        assert result["uid"] == "firebase-uid-123"
        assert result["email"] == "test@example.com"
        assert result["email_verified"] is True
        assert result["provider"] == "google.com"
    
    @patch('firebase_admin.auth.verify_id_token')
    async def test_verify_token_invalid(self, mock_verify):
        """Test Firebase token verification with invalid token"""
        from firebase_admin.auth import InvalidIdTokenError
        mock_verify.side_effect = InvalidIdTokenError("Invalid token")
        
        with pytest.raises(Exception):
            await firebase_auth.verify_token("invalid-token")


if __name__ == "__main__":
    pytest.main([__file__])