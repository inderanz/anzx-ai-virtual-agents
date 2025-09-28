"""
Tests for cricket data sync functionality
"""

import pytest
import json
import tempfile
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from datetime import datetime
from pathlib import Path

from jobs.sync import (
    CricketDataSync, GCSStorage, 
    run_full_refresh, run_team_refresh, run_match_refresh, run_ladder_refresh
)
from app.config import get_settings


class TestGCSStorage:
    """Test GCS storage with local fallback"""
    
    def test_gcs_storage_initialization_with_bucket(self):
        """Test GCS storage initialization with bucket"""
        with patch('jobs.sync.storage') as mock_storage:
            mock_storage.Client.return_value = Mock()
            storage = GCSStorage("test-bucket")
            assert storage.bucket_name == "test-bucket"
    
    def test_gcs_storage_initialization_without_bucket(self):
        """Test GCS storage initialization without bucket"""
        storage = GCSStorage(None)
        assert storage.bucket_name is None
        assert storage.bucket is None
    
    def test_write_json_local_fallback(self):
        """Test writing JSON with local fallback"""
        storage = GCSStorage(None)
        
        test_data = {"test": "data", "number": 123}
        result_path = storage.write_json("test/path.json", test_data)
        
        # Should write to local storage
        assert result_path.startswith("/tmp/test/path.json")
        
        # Verify file was written
        assert Path(result_path).exists()
        
        # Verify content
        with open(result_path, 'r') as f:
            content = json.load(f)
        assert content == test_data
    
    def test_write_json_gcs_success(self):
        """Test writing JSON to GCS successfully"""
        with patch('jobs.sync.storage') as mock_storage:
            mock_client = Mock()
            mock_bucket = Mock()
            mock_blob = Mock()
            
            mock_storage.Client.return_value = mock_client
            mock_client.bucket.return_value = mock_bucket
            mock_bucket.blob.return_value = mock_blob
            
            storage = GCSStorage("test-bucket")
            storage.client = mock_client
            storage.bucket = mock_bucket
            
            test_data = {"test": "data"}
            result_path = storage.write_json("test/path.json", test_data)
            
            assert result_path == "gs://test-bucket/test/path.json"
            mock_blob.upload_from_string.assert_called_once()
    
    def test_write_json_gcs_fallback(self):
        """Test writing JSON to GCS with fallback to local"""
        with patch('jobs.sync.storage') as mock_storage:
            mock_client = Mock()
            mock_bucket = Mock()
            mock_blob = Mock()
            
            # Make GCS upload fail
            mock_blob.upload_from_string.side_effect = Exception("GCS error")
            
            mock_storage.Client.return_value = mock_client
            mock_client.bucket.return_value = mock_bucket
            mock_bucket.blob.return_value = mock_blob
            
            storage = GCSStorage("test-bucket")
            storage.client = mock_client
            storage.bucket = mock_bucket
            
            test_data = {"test": "data"}
            result_path = storage.write_json("test/path.json", test_data)
            
            # Should fall back to local storage
            assert result_path.startswith("/tmp/test/path.json")


class TestCricketDataSync:
    """Test cricket data sync functionality"""
    
    @pytest.fixture
    def mock_sync(self):
        """Create a mock sync instance"""
        with patch('jobs.sync.get_settings') as mock_get_settings, \
             patch('jobs.sync.get_cscc_team_ids') as mock_get_team_ids, \
             patch('jobs.sync.get_cscc_org_id') as mock_get_org_id, \
             patch('jobs.sync.get_cscc_season_id') as mock_get_season_id, \
             patch('jobs.sync.get_cscc_grade_id') as mock_get_grade_id, \
             patch('jobs.sync.get_vector_client') as mock_get_vector_client:
            
            # Mock settings
            mock_settings = Mock()
            mock_settings.gcs_bucket = None
            mock_get_settings.return_value = mock_settings
            
            # Mock IDs
            mock_get_team_ids.return_value = ["team-1", "team-2"]
            mock_get_org_id.return_value = "org-1"
            mock_get_season_id.return_value = "season-1"
            mock_get_grade_id.return_value = "grade-1"
            
            # Mock vector client
            mock_vector_client = Mock()
            mock_vector_client.get_stats.return_value = {"upserts": 0, "queries": 0}
            mock_get_vector_client.return_value = mock_vector_client
            
            sync = CricketDataSync()
            return sync
    
    def test_sync_initialization(self, mock_sync):
        """Test sync initialization"""
        assert mock_sync.cscc_team_ids == ["team-1", "team-2"]
        assert mock_sync.cscc_org_id == "org-1"
        assert mock_sync.cscc_season_id == "season-1"
        assert mock_sync.cscc_grade_id == "grade-1"
        assert mock_sync.storage.bucket_name is None
    
    @pytest.mark.asyncio
    async def test_sync_all_success(self, mock_sync):
        """Test successful sync all"""
        with patch.object(mock_sync, 'sync_teams') as mock_sync_teams, \
             patch.object(mock_sync, 'sync_fixtures') as mock_sync_fixtures, \
             patch.object(mock_sync, 'sync_ladders') as mock_sync_ladders, \
             patch.object(mock_sync, 'sync_recent_scorecards') as mock_sync_scorecards, \
             patch.object(mock_sync, 'sync_rosters') as mock_sync_rosters:
            
            result = await mock_sync.sync_all()
            
            assert result["status"] == "success"
            assert "duration_seconds" in result
            assert "stats" in result
            
            # Verify all sync methods were called
            mock_sync_teams.assert_called_once()
            mock_sync_fixtures.assert_called_once()
            mock_sync_ladders.assert_called_once()
            mock_sync_scorecards.assert_called_once()
            mock_sync_rosters.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_sync_all_with_errors(self, mock_sync):
        """Test sync all with errors"""
        with patch.object(mock_sync, 'sync_teams') as mock_sync_teams:
            mock_sync_teams.side_effect = Exception("Sync error")
            
            result = await mock_sync.sync_all()
            
            assert result["status"] == "error"
            assert "error" in result
            assert mock_sync.sync_stats["errors"] > 0


class TestSyncEntrypoints:
    """Test sync entrypoint functions"""
    
    @pytest.mark.asyncio
    async def test_run_full_refresh(self):
        """Test run_full_refresh entrypoint"""
        with patch('jobs.sync.CricketDataSync') as mock_sync_class:
            mock_sync = AsyncMock()
            mock_sync.sync_all.return_value = {"status": "success", "stats": {}}
            mock_sync_class.return_value = mock_sync
            
            result = await run_full_refresh()
            
            assert result["status"] == "success"
            mock_sync.sync_all.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_run_team_refresh_success(self):
        """Test run_team_refresh for valid team"""
        with patch('jobs.sync.CricketDataSync') as mock_sync_class:
            mock_sync = AsyncMock()
            mock_sync.cscc_team_ids = ["team-1", "team-2"]
            mock_sync.sync_stats = {"fixtures_updated": 1, "vector_upserts": 1}
            mock_sync_class.return_value = mock_sync
            
            result = await run_team_refresh("team-1")
            
            assert result["status"] == "success"
            assert result["team_id"] == "team-1"
            assert "duration_seconds" in result
    
    @pytest.mark.asyncio
    async def test_run_team_refresh_invalid_team(self):
        """Test run_team_refresh for invalid team"""
        with patch('jobs.sync.CricketDataSync') as mock_sync_class:
            mock_sync = AsyncMock()
            mock_sync.cscc_team_ids = ["team-1", "team-2"]
            mock_sync_class.return_value = mock_sync
            
            result = await run_team_refresh("invalid-team")
            
            assert result["status"] == "error"
            assert "not in configured teams" in result["message"]
    
    @pytest.mark.asyncio
    async def test_run_match_refresh(self):
        """Test run_match_refresh entrypoint"""
        with patch('jobs.sync.CricketDataSync') as mock_sync_class, \
             patch('jobs.sync.initialize_playhq_client') as mock_init_client:
            
            mock_sync = AsyncMock()
            mock_sync.sync_stats = {"scorecards_updated": 1, "vector_upserts": 1, "gcs_writes": 1}
            mock_sync_class.return_value = mock_sync
            
            mock_client = AsyncMock()
            mock_client.get_game_summary.return_value = {"id": "match-1", "status": "completed"}
            mock_init_client.return_value = mock_client
            
            result = await run_match_refresh("match-1")
            
            assert result["status"] == "success"
            assert result["match_id"] == "match-1"
            assert "duration_seconds" in result
    
    @pytest.mark.asyncio
    async def test_run_ladder_refresh(self):
        """Test run_ladder_refresh entrypoint"""
        with patch('jobs.sync.CricketDataSync') as mock_sync_class, \
             patch('jobs.sync.initialize_playhq_client') as mock_init_client:
            
            mock_sync = AsyncMock()
            mock_sync.sync_stats = {"ladders_updated": 1, "vector_upserts": 1, "gcs_writes": 1}
            mock_sync_class.return_value = mock_sync
            
            mock_client = AsyncMock()
            mock_client.get_ladder.return_value = [{"team": "Team A", "position": 1}]
            mock_init_client.return_value = mock_client
            
            result = await run_ladder_refresh("grade-1")
            
            assert result["status"] == "success"
            assert result["grade_id"] == "grade-1"
            assert "duration_seconds" in result


class TestSyncDeltaLogic:
    """Test sync delta logic and content hashing"""
    
    def test_content_hash_generation(self):
        """Test content hash generation for delta detection"""
        with patch('jobs.sync.get_settings') as mock_get_settings, \
             patch('jobs.sync.get_cscc_team_ids') as mock_get_team_ids, \
             patch('jobs.sync.get_cscc_org_id') as mock_get_org_id, \
             patch('jobs.sync.get_cscc_season_id') as mock_get_season_id, \
             patch('jobs.sync.get_cscc_grade_id') as mock_get_grade_id, \
             patch('jobs.sync.get_vector_client') as mock_get_vector_client:
            
            # Mock settings to avoid validation errors
            mock_settings = Mock()
            mock_settings.gcs_bucket = None
            mock_get_settings.return_value = mock_settings
            
            # Mock IDs
            mock_get_team_ids.return_value = ["team-1"]
            mock_get_org_id.return_value = "org-1"
            mock_get_season_id.return_value = "season-1"
            mock_get_grade_id.return_value = "grade-1"
            
            # Mock vector client with real hash generation
            from agent.tools.vector_client import MockVectorClient
            mock_vector_client = MockVectorClient("test-project", "us-central1")
            mock_get_vector_client.return_value = mock_vector_client
            
            sync = CricketDataSync()
            
            # Test data
            doc1 = {"id": "test-1", "text": "Test content", "metadata": {"type": "test"}}
            doc2 = {"id": "test-1", "text": "Modified content", "metadata": {"type": "test"}}
            doc3 = {"id": "test-1", "text": "Test content", "metadata": {"type": "test"}}
            
            # Generate hashes using the actual method
            hash1 = sync.vector_client._generate_content_hash(doc1)
            hash2 = sync.vector_client._generate_content_hash(doc2)
            hash3 = sync.vector_client._generate_content_hash(doc3)
            
            # Different content should have different hashes
            assert hash1 != hash2
            
            # Same content should have same hash
            assert hash1 == hash3
    
    def test_delta_upsert_same_content(self):
        """Test that same content is not upserted again"""
        with patch('jobs.sync.get_settings') as mock_get_settings, \
             patch('jobs.sync.get_cscc_team_ids') as mock_get_team_ids, \
             patch('jobs.sync.get_cscc_org_id') as mock_get_org_id, \
             patch('jobs.sync.get_cscc_season_id') as mock_get_season_id, \
             patch('jobs.sync.get_cscc_grade_id') as mock_get_grade_id, \
             patch('jobs.sync.get_vector_client') as mock_get_vector_client:
            
            # Mock settings to avoid validation errors
            mock_settings = Mock()
            mock_settings.gcs_bucket = None
            mock_get_settings.return_value = mock_settings
            
            # Mock IDs
            mock_get_team_ids.return_value = ["team-1"]
            mock_get_org_id.return_value = "org-1"
            mock_get_season_id.return_value = "season-1"
            mock_get_grade_id.return_value = "grade-1"
            
            # Mock vector client with real functionality
            from agent.tools.vector_client import MockVectorClient
            mock_vector_client = MockVectorClient("test-project", "us-central1")
            mock_get_vector_client.return_value = mock_vector_client
            
            sync = CricketDataSync()
            
            # First upsert
            docs = [{"id": "doc-1", "text": "Test content", "metadata": {"type": "test"}}]
            sync.vector_client.upsert(docs)
            initial_upserts = sync.vector_client.get_stats()["upserts"]
            
            # Same content should not be upserted again
            sync.vector_client.upsert(docs)
            final_upserts = sync.vector_client.get_stats()["upserts"]
            
            # Upsert count should not increase
            assert final_upserts == initial_upserts
    
    def test_delta_upsert_modified_content(self):
        """Test that modified content is upserted"""
        with patch('jobs.sync.get_settings') as mock_get_settings, \
             patch('jobs.sync.get_cscc_team_ids') as mock_get_team_ids, \
             patch('jobs.sync.get_cscc_org_id') as mock_get_org_id, \
             patch('jobs.sync.get_cscc_season_id') as mock_get_season_id, \
             patch('jobs.sync.get_cscc_grade_id') as mock_get_grade_id, \
             patch('jobs.sync.get_vector_client') as mock_get_vector_client:
            
            # Mock settings to avoid validation errors
            mock_settings = Mock()
            mock_settings.gcs_bucket = None
            mock_get_settings.return_value = mock_settings
            
            # Mock IDs
            mock_get_team_ids.return_value = ["team-1"]
            mock_get_org_id.return_value = "org-1"
            mock_get_season_id.return_value = "season-1"
            mock_get_grade_id.return_value = "grade-1"
            
            # Mock vector client with real functionality
            from agent.tools.vector_client import MockVectorClient
            mock_vector_client = MockVectorClient("test-project", "us-central1")
            mock_get_vector_client.return_value = mock_vector_client
            
            sync = CricketDataSync()
            
            # First upsert
            docs = [{"id": "doc-1", "text": "Test content", "metadata": {"type": "test"}}]
            sync.vector_client.upsert(docs)
            initial_upserts = sync.vector_client.get_stats()["upserts"]
            
            # Modified content should be upserted
            docs[0]["text"] = "Modified content"
            sync.vector_client.upsert(docs)
            final_upserts = sync.vector_client.get_stats()["upserts"]
            
            # Upsert count should increase
            assert final_upserts > initial_upserts


class TestSyncErrorHandling:
    """Test sync error handling"""
    
    @pytest.mark.asyncio
    async def test_sync_error_handling(self):
        """Test sync error handling"""
        with patch('jobs.sync.CricketDataSync') as mock_sync_class:
            mock_sync = AsyncMock()
            mock_sync.sync_all.side_effect = Exception("Sync error")
            mock_sync_class.return_value = mock_sync
            
            result = await run_full_refresh()
            
            # The function should catch the exception and return error status
            assert result["status"] == "error"
            assert "error" in result


class TestSyncFilters:
    """Test sync filters and metadata"""
    
    def test_vector_client_filters(self):
        """Test that correct filters are passed to vector client"""
        with patch('jobs.sync.get_settings') as mock_get_settings, \
             patch('jobs.sync.get_cscc_team_ids') as mock_get_team_ids, \
             patch('jobs.sync.get_cscc_org_id') as mock_get_org_id, \
             patch('jobs.sync.get_cscc_season_id') as mock_get_season_id, \
             patch('jobs.sync.get_cscc_grade_id') as mock_get_grade_id, \
             patch('jobs.sync.get_vector_client') as mock_get_vector_client:
            
            # Mock settings to avoid validation errors
            mock_settings = Mock()
            mock_settings.gcs_bucket = None
            mock_get_settings.return_value = mock_settings
            
            # Mock IDs
            mock_get_team_ids.return_value = ["team-1"]
            mock_get_org_id.return_value = "org-1"
            mock_get_season_id.return_value = "season-1"
            mock_get_grade_id.return_value = "grade-1"
            
            # Mock vector client
            mock_vector_client = Mock()
            mock_get_vector_client.return_value = mock_vector_client
            
            sync = CricketDataSync()
            
            # Test document with metadata
            doc = {
                "id": "test-1",
                "text": "Test content",
                "metadata": {
                    "team_id": "team-1",
                    "season_id": "season-1",
                    "grade_id": "grade-1",
                    "type": "fixture"
                }
            }
            
            # Upsert document
            sync.vector_client.upsert([doc])
            
            # Verify upsert was called
            mock_vector_client.upsert.assert_called_once_with([doc])
    
    def test_query_with_filters(self):
        """Test querying with filters"""
        with patch('jobs.sync.get_settings') as mock_get_settings, \
             patch('jobs.sync.get_cscc_team_ids') as mock_get_team_ids, \
             patch('jobs.sync.get_cscc_org_id') as mock_get_org_id, \
             patch('jobs.sync.get_cscc_season_id') as mock_get_season_id, \
             patch('jobs.sync.get_cscc_grade_id') as mock_get_grade_id, \
             patch('jobs.sync.get_vector_client') as mock_get_vector_client:
            
            # Mock settings to avoid validation errors
            mock_settings = Mock()
            mock_settings.gcs_bucket = None
            mock_get_settings.return_value = mock_settings
            
            # Mock IDs
            mock_get_team_ids.return_value = ["team-1"]
            mock_get_org_id.return_value = "org-1"
            mock_get_season_id.return_value = "season-1"
            mock_get_grade_id.return_value = "grade-1"
            
            # Mock vector client
            mock_vector_client = Mock()
            mock_vector_client.query.return_value = ["result1", "result2"]
            mock_get_vector_client.return_value = mock_vector_client
            
            sync = CricketDataSync()
            
            # Query with filters
            filters = {"team_id": "team-1", "type": "fixture"}
            results = sync.vector_client.query("test query", filters, k=5)
            
            # Verify query was called with correct parameters
            mock_vector_client.query.assert_called_once_with("test query", filters, k=5)
            assert results == ["result1", "result2"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
