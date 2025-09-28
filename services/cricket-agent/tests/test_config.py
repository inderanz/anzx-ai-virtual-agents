"""
Unit tests for Cricket Agent Configuration
Tests Secret Manager integration, validation, and security guards
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.config import (
    Settings, IDsBundle, TeamInfo, read_secret, get_settings,
    is_private_mode, get_playhq_headers, get_cscc_team_ids,
    get_cscc_org_id, get_cscc_season_id, get_cscc_grade_id
)

# Mock data for testing
MOCK_IDS_BUNDLE_JSON = json.dumps({
    "tenant": "ca",
    "org_id": "org-123",
    "season_id": "season-456",
    "grade_id": "grade-789",
    "teams": [
        {"name": "Caroline Springs Blue U10", "team_id": "team-001"},
        {"name": "Caroline Springs White U10", "team_id": "team-002"}
    ]
})

MOCK_SECRET_VALUE = "mock-secret-value"
MOCK_PROJECT_ID = "test-project-123"

class TestSettings:
    """Test Settings model validation"""
    
    def test_default_settings(self):
        """Test default settings values"""
        settings = Settings()
        
        assert settings.app_env == "dev"
        assert settings.port == 8080
        assert settings.region == "australia-southeast1"
        assert settings.vertex_location == "australia-southeast1"
        assert settings.vertex_model == "gemini-1.5-flash"
        assert settings.embed_model == "text-embedding-005"
        assert settings.playhq_mode == "public"
        assert settings.vector_backend == "vertex_rag"
    
    def test_playhq_mode_validation(self):
        """Test PlayHQ mode validation"""
        # Valid modes
        settings = Settings(playhq_mode="public")
        assert settings.playhq_mode == "public"
        
        settings = Settings(playhq_mode="private")
        assert settings.playhq_mode == "private"
        
        # Invalid mode
        with pytest.raises(ValueError, match="playhq_mode must be"):
            Settings(playhq_mode="invalid")
    
    def test_vector_backend_validation(self):
        """Test vector backend validation"""
        # Valid backends
        for backend in ["vertex_rag", "knowledge_service", "redis", "pgvector"]:
            settings = Settings(vector_backend=backend)
            assert settings.vector_backend == backend
        
        # Invalid backend
        with pytest.raises(ValueError, match="vector_backend must be one of"):
            Settings(vector_backend="invalid")

class TestIDsBundle:
    """Test IDs bundle schema validation"""
    
    def test_valid_ids_bundle(self):
        """Test valid IDs bundle"""
        bundle_data = {
            "tenant": "ca",
            "org_id": "org-123",
            "season_id": "season-456",
            "grade_id": "grade-789",
            "teams": [
                {"name": "Team A", "team_id": "team-001"},
                {"name": "Team B", "team_id": "team-002"}
            ]
        }
        
        bundle = IDsBundle(**bundle_data)
        
        assert bundle.tenant == "ca"
        assert bundle.org_id == "org-123"
        assert bundle.season_id == "season-456"
        assert bundle.grade_id == "grade-789"
        assert len(bundle.teams) == 2
        assert bundle.teams[0].name == "Team A"
        assert bundle.teams[0].team_id == "team-001"
    
    def test_invalid_ids_bundle_missing_fields(self):
        """Test IDs bundle with missing required fields"""
        with pytest.raises(Exception):  # Pydantic validation error
            IDsBundle(**{"tenant": "ca"})  # Missing required fields
    
    def test_invalid_ids_bundle_empty_teams(self):
        """Test IDs bundle with empty teams"""
        bundle_data = {
            "tenant": "ca",
            "org_id": "org-123",
            "season_id": "season-456",
            "grade_id": "grade-789",
            "teams": []
        }
        
        bundle = IDsBundle(**bundle_data)
        assert len(bundle.teams) == 0

class TestReadSecret:
    """Test secret reading functionality"""
    
    @patch('app.config.secretmanager.SecretManagerServiceClient')
    def test_read_secret_from_secret_manager(self, mock_client_class):
        """Test reading secret from Secret Manager"""
        # Setup mock
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_response = Mock()
        mock_response.payload.data.decode.return_value = MOCK_SECRET_VALUE
        mock_client.access_secret_version.return_value = mock_response
        
        # Test
        secret_ref = f"projects/{MOCK_PROJECT_ID}/secrets/TEST_SECRET/versions/latest"
        result = read_secret(secret_ref)
        
        assert result == MOCK_SECRET_VALUE
        mock_client.access_secret_version.assert_called_once_with(
            request={"name": secret_ref}
        )
    
    def test_read_secret_raw_value(self):
        """Test reading raw secret value for local dev"""
        raw_value = "raw-secret-value"
        result = read_secret(raw_value)
        
        assert result == raw_value
    
    def test_read_secret_none(self):
        """Test reading None secret"""
        result = read_secret(None)
        assert result is None
    
    @patch('app.config.secretmanager.SecretManagerServiceClient')
    def test_read_secret_secret_manager_error(self, mock_client_class):
        """Test Secret Manager error handling"""
        # Setup mock to raise exception
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.access_secret_version.side_effect = Exception("Secret not found")
        
        # Test
        secret_ref = f"projects/{MOCK_PROJECT_ID}/secrets/MISSING_SECRET/versions/latest"
        
        with pytest.raises(ValueError, match="Failed to load secret"):
            read_secret(secret_ref)

class TestGetSettings:
    """Test settings resolution and validation"""
    
    @patch('app.config.read_secret')
    def test_get_settings_public_mode_success(self, mock_read_secret):
        """Test successful settings resolution for public mode"""
        # Setup mocks
        mock_read_secret.side_effect = [
            "api-key-123",  # PlayHQ API key
            MOCK_IDS_BUNDLE_JSON,  # IDs bundle
            "internal-token-456"  # Internal token
        ]
        
        # Create settings with secret references
        settings = Settings(
            playhq_mode="public",
            secret_playhq_api_key="projects/test/secrets/API_KEY/versions/latest",
            secret_ids_bundle="projects/test/secrets/IDS_BUNDLE/versions/latest",
            secret_internal_token="projects/test/secrets/INTERNAL_TOKEN/versions/latest"
        )
        
        # Mock the global settings
        with patch('app.config._settings', None):
            with patch('app.config.Settings', return_value=settings):
                result = get_settings()
        
        assert result.playhq_mode == "public"
        assert result.playhq_api_key == "api-key-123"
        assert result.internal_token == "internal-token-456"
        assert result.ids_bundle is not None
        assert result.ids_bundle.tenant == "ca"
    
    @patch('app.config.read_secret')
    def test_get_settings_private_mode_success(self, mock_read_secret):
        """Test successful settings resolution for private mode"""
        # Setup mocks
        mock_read_secret.side_effect = [
            "api-key-123",  # PlayHQ API key
            MOCK_IDS_BUNDLE_JSON,  # IDs bundle
            "internal-token-456",  # Internal token
            "private-token-789"  # Private token
        ]
        
        # Create settings with secret references
        settings = Settings(
            playhq_mode="private",
            secret_playhq_api_key="projects/test/secrets/API_KEY/versions/latest",
            secret_ids_bundle="projects/test/secrets/IDS_BUNDLE/versions/latest",
            secret_internal_token="projects/test/secrets/INTERNAL_TOKEN/versions/latest",
            secret_playhq_private_token="projects/test/secrets/PRIVATE_TOKEN/versions/latest"
        )
        
        # Mock the global settings
        with patch('app.config._settings', None):
            with patch('app.config.Settings', return_value=settings):
                result = get_settings()
        
        assert result.playhq_mode == "private"
        assert result.playhq_private_token == "private-token-789"
    
    @patch('app.config.read_secret')
    def test_get_settings_missing_required_secret(self, mock_read_secret):
        """Test settings validation with missing required secret"""
        # Setup mocks - missing PlayHQ API key
        mock_read_secret.side_effect = [
            None,  # PlayHQ API key missing
            MOCK_IDS_BUNDLE_JSON,  # IDs bundle
            "internal-token-456"  # Internal token
        ]
        
        settings = Settings(
            playhq_mode="public",
            secret_playhq_api_key=None,  # Missing required secret
            secret_ids_bundle="projects/test/secrets/IDS_BUNDLE/versions/latest",
            secret_internal_token="projects/test/secrets/INTERNAL_TOKEN/versions/latest"
        )
        
        # Mock the global settings
        with patch('app.config._settings', None):
            with patch('app.config.Settings', return_value=settings):
                with pytest.raises(ValueError, match="SECRET_PLAYHQ_API_KEY is required"):
                    get_settings()
    
    @patch('app.config.read_secret')
    def test_get_settings_invalid_ids_bundle(self, mock_read_secret):
        """Test settings validation with invalid IDs bundle"""
        # Setup mocks
        mock_read_secret.side_effect = [
            "api-key-123",  # PlayHQ API key
            "invalid-json",  # Invalid IDs bundle JSON
            "internal-token-456"  # Internal token
        ]
        
        settings = Settings(
            playhq_mode="public",
            secret_playhq_api_key="projects/test/secrets/API_KEY/versions/latest",
            secret_ids_bundle="projects/test/secrets/IDS_BUNDLE/versions/latest",
            secret_internal_token="projects/test/secrets/INTERNAL_TOKEN/versions/latest"
        )
        
        # Mock the global settings
        with patch('app.config._settings', None):
            with patch('app.config.Settings', return_value=settings):
                with pytest.raises(ValueError, match="Invalid IDs bundle JSON"):
                    get_settings()

class TestHelperFunctions:
    """Test helper functions"""
    
    def test_is_private_mode(self):
        """Test private mode detection"""
        with patch('app.config.get_settings') as mock_get_settings:
            # Test private mode
            mock_settings = Mock()
            mock_settings.playhq_mode = "private"
            mock_get_settings.return_value = mock_settings
            
            assert is_private_mode() == True
            
            # Test public mode
            mock_settings.playhq_mode = "public"
            assert is_private_mode() == False
    
    def test_get_playhq_headers(self):
        """Test PlayHQ headers generation"""
        with patch('app.config.get_settings') as mock_get_settings:
            mock_settings = Mock()
            mock_settings.playhq_api_key = "api-key-123"
            mock_settings.ids_bundle = Mock()
            mock_settings.ids_bundle.tenant = "ca"
            mock_get_settings.return_value = mock_settings
            
            headers = get_playhq_headers()
            
            assert headers["x-api-key"] == "api-key-123"
            assert headers["x-phq-tenant"] == "ca"
            assert headers["Content-Type"] == "application/json"
            assert headers["Accept"] == "application/json"
    
    def test_get_cscc_team_ids(self):
        """Test CSCC team IDs retrieval"""
        with patch('app.config.get_settings') as mock_get_settings:
            mock_settings = Mock()
            mock_settings.ids_bundle = Mock()
            mock_settings.ids_bundle.teams = [
                Mock(team_id="team-001"),
                Mock(team_id="team-002")
            ]
            mock_get_settings.return_value = mock_settings
            
            team_ids = get_cscc_team_ids()
            
            assert team_ids == ["team-001", "team-002"]
    
    def test_get_cscc_org_id(self):
        """Test CSCC organization ID retrieval"""
        with patch('app.config.get_settings') as mock_get_settings:
            mock_settings = Mock()
            mock_settings.ids_bundle = Mock()
            mock_settings.ids_bundle.org_id = "org-123"
            mock_get_settings.return_value = mock_settings
            
            org_id = get_cscc_org_id()
            
            assert org_id == "org-123"
    
    def test_get_cscc_season_id(self):
        """Test CSCC season ID retrieval"""
        with patch('app.config.get_settings') as mock_get_settings:
            mock_settings = Mock()
            mock_settings.ids_bundle = Mock()
            mock_settings.ids_bundle.season_id = "season-456"
            mock_get_settings.return_value = mock_settings
            
            season_id = get_cscc_season_id()
            
            assert season_id == "season-456"
    
    def test_get_cscc_grade_id(self):
        """Test CSCC grade ID retrieval"""
        with patch('app.config.get_settings') as mock_get_settings:
            mock_settings = Mock()
            mock_settings.ids_bundle = Mock()
            mock_settings.ids_bundle.grade_id = "grade-789"
            mock_get_settings.return_value = mock_settings
            
            grade_id = get_cscc_grade_id()
            
            assert grade_id == "grade-789"

class TestSecurityGuards:
    """Test security guardrails"""
    
    def test_no_secret_logging(self):
        """Test that secrets are not logged"""
        with patch('app.config.logger') as mock_logger:
            with patch('app.config.secretmanager.SecretManagerServiceClient'):
                # This should not log the actual secret value
                read_secret("projects/test/secrets/API_KEY/versions/latest")
                
                # Check that only secret reference is logged, not the value
                mock_logger.info.assert_called()
                logged_message = mock_logger.info.call_args[0][0]
                assert "projects/test/secrets/API_KEY/versions/latest" in logged_message
                assert "mock-secret-value" not in logged_message
    
    def test_private_mode_guard(self):
        """Test private mode guard for PII stripping"""
        with patch('app.config.get_settings') as mock_get_settings:
            # Test private mode
            mock_settings = Mock()
            mock_settings.playhq_mode = "private"
            mock_get_settings.return_value = mock_settings
            
            assert is_private_mode() == True
            
            # Test public mode
            mock_settings.playhq_mode = "public"
            assert is_private_mode() == False

if __name__ == "__main__":
    pytest.main([__file__])
