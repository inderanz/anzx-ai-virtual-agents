"""
Tests for PlayHQ webhook functionality
"""

import pytest
import json
import hmac
import hashlib
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from app.main import app
from app.webhook_models import WebhookEventType, WebhookRequest
from app.config import get_settings

class TestWebhookSignature:
    """Test webhook signature verification"""
    
    def test_valid_signature(self):
        """Test valid webhook signature"""
        from app.webhook_handler import verify_webhook_signature
        
        payload = b'{"test": "data"}'
        secret = "test_secret"
        signature = hmac.new(secret.encode('utf-8'), payload, hashlib.sha256).hexdigest()
        
        assert verify_webhook_signature(payload, signature, secret) is True
    
    def test_invalid_signature(self):
        """Test invalid webhook signature"""
        from app.webhook_handler import verify_webhook_signature
        
        payload = b'{"test": "data"}'
        secret = "test_secret"
        invalid_signature = "invalid_signature"
        
        assert verify_webhook_signature(payload, invalid_signature, secret) is False
    
    def test_malformed_signature(self):
        """Test malformed signature handling"""
        from app.webhook_handler import verify_webhook_signature
        
        payload = b'{"test": "data"}'
        secret = "test_secret"
        malformed_signature = "not_a_hex_string"
        
        assert verify_webhook_signature(payload, malformed_signature, secret) is False

class TestWebhookEndpoints:
    """Test webhook endpoints"""
    
    @pytest.fixture
    def client(self):
        """Test client"""
        return TestClient(app)
    
    @pytest.fixture
    def mock_settings_private(self):
        """Mock settings for private mode"""
        with patch('app.main.get_settings') as mock:
            settings = Mock()
            settings.playhq_mode = "private"
            settings.playhq_webhook_secret = "test_secret"
            mock.return_value = settings
            yield settings
    
    @pytest.fixture
    def mock_settings_public(self):
        """Mock settings for public mode"""
        with patch('app.main.get_settings') as mock:
            settings = Mock()
            settings.playhq_mode = "public"
            mock.return_value = settings
            yield settings
    
    def test_webhook_public_mode_forbidden(self, client, mock_settings_public):
        """Test webhook endpoint is forbidden in public mode"""
        response = client.post("/webhooks/playhq", json={"test": "data"})
        assert response.status_code == 403
        assert "Webhook mode not enabled" in response.json()["detail"]
    
    def test_webhook_missing_signature(self, client, mock_settings_private):
        """Test webhook with missing signature"""
        response = client.post("/webhooks/playhq", json={"test": "data"})
        assert response.status_code == 400
        assert "Missing webhook signature" in response.json()["detail"]
    
    def test_webhook_invalid_signature(self, client, mock_settings_private):
        """Test webhook with invalid signature"""
        headers = {"X-PlayHQ-Signature": "invalid_signature"}
        response = client.post("/webhooks/playhq", json={"test": "data"}, headers=headers)
        assert response.status_code == 401
        assert "Invalid webhook signature" in response.json()["detail"]
    
    def test_webhook_invalid_payload(self, client, mock_settings_private):
        """Test webhook with invalid payload"""
        payload = b'{"invalid": "json"'
        secret = "test_secret"
        signature = hmac.new(secret.encode('utf-8'), payload, hashlib.sha256).hexdigest()
        headers = {"X-PlayHQ-Signature": signature}
        
        response = client.post("/webhooks/playhq", data=payload, headers=headers)
        assert response.status_code == 400
        assert "Invalid webhook payload" in response.json()["detail"]
    
    @patch('app.webhook_handler.get_vector_client')
    def test_webhook_fixture_update(self, mock_vector_client, client, mock_settings_private):
        """Test fixture update webhook"""
        # Mock vector client
        mock_vc = Mock()
        mock_vector_client.return_value = mock_vc
        
        # Create valid webhook payload
        payload_data = {
            "event_type": "fixture_update",
            "timestamp": "2025-09-28T10:00:00Z",
            "data": {
                "fixture_id": "fixture_123",
                "team_id": "team_123",
                "season_id": "season_123",
                "grade_id": "grade_123",
                "status": "scheduled",
                "venue": "Test Ground",
                "start_time": "2025-09-28T10:00:00Z",
                "opponent": "Opponent Team"
            }
        }
        
        payload = json.dumps(payload_data).encode('utf-8')
        secret = "test_secret"
        signature = hmac.new(secret.encode('utf-8'), payload, hashlib.sha256).hexdigest()
        headers = {"X-PlayHQ-Signature": signature}
        
        response = client.post("/webhooks/playhq", data=payload, headers=headers)
        
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        assert result["processed_count"] == 1
        assert "Processed 1 records" in result["message"]
        
        # Verify vector client was called
        mock_vc.upsert.assert_called_once()
    
    @patch('app.webhook_handler.get_vector_client')
    def test_webhook_scorecard_update(self, mock_vector_client, client, mock_settings_private):
        """Test scorecard update webhook"""
        # Mock vector client
        mock_vc = Mock()
        mock_vector_client.return_value = mock_vc
        
        # Create valid webhook payload
        payload_data = {
            "event_type": "scorecard_update",
            "timestamp": "2025-09-28T10:00:00Z",
            "data": {
                "fixture_id": "fixture_123",
                "team_id": "team_123",
                "season_id": "season_123",
                "grade_id": "grade_123",
                "is_completed": True,
                "batting_summary": {"runs": 150, "wickets": 5},
                "bowling_summary": {"overs": 20, "runs": 120},
                "score": "150/5",
                "overs": "20.0"
            }
        }
        
        payload = json.dumps(payload_data).encode('utf-8')
        secret = "test_secret"
        signature = hmac.new(secret.encode('utf-8'), payload, hashlib.sha256).hexdigest()
        headers = {"X-PlayHQ-Signature": signature}
        
        response = client.post("/webhooks/playhq", data=payload, headers=headers)
        
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        assert result["processed_count"] == 1
        
        # Verify vector client was called
        mock_vc.upsert.assert_called_once()
    
    @patch('app.webhook_handler.get_vector_client')
    def test_webhook_ladder_update(self, mock_vector_client, client, mock_settings_private):
        """Test ladder update webhook"""
        # Mock vector client
        mock_vc = Mock()
        mock_vector_client.return_value = mock_vc
        
        # Create valid webhook payload
        payload_data = {
            "event_type": "ladder_update",
            "timestamp": "2025-09-28T10:00:00Z",
            "data": {
                "grade_id": "grade_123",
                "season_id": "season_123",
                "team_id": "team_123",
                "position": 1,
                "points": 20,
                "played": 5,
                "won": 4,
                "lost": 1
            }
        }
        
        payload = json.dumps(payload_data).encode('utf-8')
        secret = "test_secret"
        signature = hmac.new(secret.encode('utf-8'), payload, hashlib.sha256).hexdigest()
        headers = {"X-PlayHQ-Signature": signature}
        
        response = client.post("/webhooks/playhq", data=payload, headers=headers)
        
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        assert result["processed_count"] == 1
        
        # Verify vector client was called
        mock_vc.upsert.assert_called_once()
    
    @patch('app.webhook_handler.get_vector_client')
    def test_webhook_roster_update(self, mock_vector_client, client, mock_settings_private):
        """Test roster update webhook"""
        # Mock vector client
        mock_vc = Mock()
        mock_vector_client.return_value = mock_vc
        
        # Create valid webhook payload
        payload_data = {
            "event_type": "roster_update",
            "timestamp": "2025-09-28T10:00:00Z",
            "data": {
                "team_id": "team_123",
                "season_id": "season_123",
                "grade_id": "grade_123",
                "players": [
                    {"name": "Player 1", "position": "batsman"},
                    {"name": "Player 2", "position": "bowler"}
                ]
            }
        }
        
        payload = json.dumps(payload_data).encode('utf-8')
        secret = "test_secret"
        signature = hmac.new(secret.encode('utf-8'), payload, hashlib.sha256).hexdigest()
        headers = {"X-PlayHQ-Signature": signature}
        
        response = client.post("/webhooks/playhq", data=payload, headers=headers)
        
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        assert result["processed_count"] == 1
        
        # Verify vector client was called
        mock_vc.upsert.assert_called_once()
    
    @patch('app.webhook_handler.get_vector_client')
    def test_webhook_processing_error(self, mock_vector_client, client, mock_settings_private):
        """Test webhook processing error"""
        # Mock vector client to raise exception
        mock_vc = Mock()
        mock_vc.upsert.side_effect = Exception("Vector store error")
        mock_vector_client.return_value = mock_vc
        
        # Create valid webhook payload
        payload_data = {
            "event_type": "fixture_update",
            "timestamp": "2025-09-28T10:00:00Z",
            "data": {
                "fixture_id": "fixture_123",
                "team_id": "team_123",
                "season_id": "season_123",
                "grade_id": "grade_123",
                "status": "scheduled"
            }
        }
        
        payload = json.dumps(payload_data).encode('utf-8')
        secret = "test_secret"
        signature = hmac.new(secret.encode('utf-8'), payload, hashlib.sha256).hexdigest()
        headers = {"X-PlayHQ-Signature": signature}
        
        response = client.post("/webhooks/playhq", data=payload, headers=headers)
        
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is False
        assert result["processed_count"] == 0
        assert len(result["errors"]) > 0
        assert "Vector store error" in result["errors"][0]

class TestWebhookModels:
    """Test webhook models"""
    
    def test_webhook_request_validation(self):
        """Test webhook request model validation"""
        valid_data = {
            "event_type": "fixture_update",
            "timestamp": "2025-09-28T10:00:00Z",
            "data": {
                "fixture_id": "fixture_123",
                "team_id": "team_123"
            }
        }
        
        request = WebhookRequest(**valid_data)
        assert request.event_type == WebhookEventType.FIXTURE_UPDATE
        assert request.timestamp is not None
        assert request.data["fixture_id"] == "fixture_123"
    
    def test_webhook_response_creation(self):
        """Test webhook response model creation"""
        from app.webhook_models import WebhookResponse
        
        response = WebhookResponse(
            success=True,
            message="Test message",
            processed_count=1,
            errors=[]
        )
        
        assert response.success is True
        assert response.message == "Test message"
        assert response.processed_count == 1
        assert len(response.errors) == 0
