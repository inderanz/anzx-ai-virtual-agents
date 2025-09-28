"""
Integration tests for sync job with vector client
Tests vector upserts, delta logic, and metadata filtering
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from jobs.sync import CricketDataSync, get_sync_instance, run_sync_job
from agent.tools.vector_client import MockVectorClient


class TestSyncVectorIntegration:
    """Test sync job integration with vector client"""
    
    def test_sync_initialization(self):
        """Test sync job initialization with vector client"""
        with patch('jobs.sync.get_settings') as mock_get_settings, \
             patch('jobs.sync.get_cscc_team_ids') as mock_get_team_ids, \
             patch('jobs.sync.get_cscc_org_id') as mock_get_org_id, \
             patch('jobs.sync.get_cscc_season_id') as mock_get_season_id, \
             patch('jobs.sync.get_cscc_grade_id') as mock_get_grade_id, \
             patch('jobs.sync.get_vector_client') as mock_get_vector_client:
            
            # Mock settings
            mock_settings = Mock()
            mock_settings.app_env = "test"
            mock_get_settings.return_value = mock_settings
            
            # Mock IDs
            mock_get_team_ids.return_value = ["team-1", "team-2"]
            mock_get_org_id.return_value = "org-1"
            mock_get_season_id.return_value = "season-1"
            mock_get_grade_id.return_value = "grade-1"
            
            # Mock vector client
            mock_vector_client = MockVectorClient("test-project")
            mock_get_vector_client.return_value = mock_vector_client
            
            # Initialize sync
            sync = CricketDataSync()
            
            # Check initialization
            assert sync.cscc_team_ids == ["team-1", "team-2"]
            assert sync.cscc_org_id == "org-1"
            assert sync.cscc_season_id == "season-1"
            assert sync.cscc_grade_id == "grade-1"
            assert isinstance(sync.vector_client, MockVectorClient)
            assert sync.sync_stats["vector_upserts"] == 0
    
    @pytest.mark.asyncio
    async def test_sync_all_with_vector_upserts(self):
        """Test full sync with vector upserts"""
        with patch('jobs.sync.get_settings') as mock_get_settings, \
             patch('jobs.sync.get_cscc_team_ids') as mock_get_team_ids, \
             patch('jobs.sync.get_cscc_org_id') as mock_get_org_id, \
             patch('jobs.sync.get_cscc_season_id') as mock_get_season_id, \
             patch('jobs.sync.get_cscc_grade_id') as mock_get_grade_id, \
             patch('jobs.sync.get_vector_client') as mock_get_vector_client, \
             patch('jobs.sync.initialize_playhq_client') as mock_init_client:
            
            # Mock settings and IDs
            mock_settings = Mock()
            mock_settings.app_env = "test"
            mock_get_settings.return_value = mock_settings
            mock_get_team_ids.return_value = ["team-1"]
            mock_get_org_id.return_value = "org-1"
            mock_get_season_id.return_value = "season-1"
            mock_get_grade_id.return_value = "grade-1"
            
            # Mock vector client
            mock_vector_client = MockVectorClient("test-project")
            mock_get_vector_client.return_value = mock_vector_client
            
            # Mock PlayHQ client
            mock_playhq_client = AsyncMock()
            mock_playhq_client.get_seasons.return_value = [{"id": "season-1", "name": "2024 Season"}]
            mock_playhq_client.get_grades.return_value = [{"id": "grade-1", "name": "U10"}]
            mock_playhq_client.get_teams.return_value = [{"id": "team-1", "name": "Caroline Springs Blue"}]
            mock_playhq_client.get_team_fixtures.return_value = []
            mock_playhq_client.get_ladder.return_value = []
            mock_playhq_client.get_games.return_value = []
            mock_playhq_client.get_team_roster.return_value = None
            mock_playhq_client.close.return_value = None
            mock_init_client.return_value = mock_playhq_client
            
            # Initialize sync
            sync = CricketDataSync()
            
            # Run sync
            result = await sync.sync_all()
            
            # Check result
            assert result["status"] == "success"
            assert "duration_seconds" in result
            assert "stats" in result
            
            # Check vector upserts were called
            assert sync.sync_stats["vector_upserts"] > 0
            assert len(mock_vector_client.documents) > 0
    
    @pytest.mark.asyncio
    async def test_sync_teams_with_vector_upsert(self):
        """Test team sync with vector upsert"""
        with patch('jobs.sync.get_settings') as mock_get_settings, \
             patch('jobs.sync.get_cscc_team_ids') as mock_get_team_ids, \
             patch('jobs.sync.get_cscc_org_id') as mock_get_org_id, \
             patch('jobs.sync.get_cscc_season_id') as mock_get_season_id, \
             patch('jobs.sync.get_cscc_grade_id') as mock_get_grade_id, \
             patch('jobs.sync.get_vector_client') as mock_get_vector_client, \
             patch('jobs.sync.initialize_playhq_client') as mock_init_client:
            
            # Mock settings and IDs
            mock_settings = Mock()
            mock_get_settings.return_value = mock_settings
            mock_get_team_ids.return_value = ["team-1"]
            mock_get_org_id.return_value = "org-1"
            mock_get_season_id.return_value = "season-1"
            mock_get_grade_id.return_value = "grade-1"
            
            # Mock vector client
            mock_vector_client = MockVectorClient("test-project")
            mock_get_vector_client.return_value = mock_vector_client
            
            # Mock PlayHQ client
            mock_playhq_client = AsyncMock()
            mock_playhq_client.get_seasons.return_value = [{"id": "season-1", "name": "2024 Season"}]
            mock_playhq_client.get_grades.return_value = [{"id": "grade-1", "name": "U10"}]
            mock_playhq_client.get_teams.return_value = [{"id": "team-1", "name": "Caroline Springs Blue"}]
            mock_playhq_client.close.return_value = None
            mock_init_client.return_value = mock_playhq_client
            
            # Initialize sync
            sync = CricketDataSync()
            
            # Run team sync
            await sync.sync_teams()
            
            # Check vector upserts
            assert sync.sync_stats["teams_updated"] > 0
            assert sync.sync_stats["vector_upserts"] > 0
            
            # Check documents were stored with correct metadata
            team_docs = [doc for doc in mock_vector_client.documents.values() 
                        if doc.get("metadata", {}).get("type") == "team"]
            assert len(team_docs) > 0
            
            # Check metadata structure
            for doc in team_docs:
                metadata = doc["metadata"]
                assert "team_id" in metadata
                assert "season_id" in metadata
                assert "grade_id" in metadata
                assert "type" in metadata
                assert "date" in metadata
    
    @pytest.mark.asyncio
    async def test_sync_fixtures_with_vector_upsert(self):
        """Test fixture sync with vector upsert"""
        with patch('jobs.sync.get_settings') as mock_get_settings, \
             patch('jobs.sync.get_cscc_team_ids') as mock_get_team_ids, \
             patch('jobs.sync.get_cscc_org_id') as mock_get_org_id, \
             patch('jobs.sync.get_cscc_season_id') as mock_get_season_id, \
             patch('jobs.sync.get_cscc_grade_id') as mock_get_grade_id, \
             patch('jobs.sync.get_vector_client') as mock_get_vector_client, \
             patch('jobs.sync.initialize_playhq_client') as mock_init_client:
            
            # Mock settings and IDs
            mock_settings = Mock()
            mock_get_settings.return_value = mock_settings
            mock_get_team_ids.return_value = ["team-1"]
            mock_get_org_id.return_value = "org-1"
            mock_get_season_id.return_value = "season-1"
            mock_get_grade_id.return_value = "grade-1"
            
            # Mock vector client
            mock_vector_client = MockVectorClient("test-project")
            mock_get_vector_client.return_value = mock_vector_client
            
            # Mock PlayHQ client with fixture data
            mock_playhq_client = AsyncMock()
            mock_playhq_client.get_team_fixtures.return_value = [
                {
                    "id": "fixture-1",
                    "homeTeam": {"id": "team-1", "name": "Caroline Springs Blue"},
                    "awayTeam": {"id": "team-2", "name": "Opponent Team"},
                    "date": "2024-01-20T14:00:00Z",
                    "venue": "Caroline Springs Oval",
                    "status": "scheduled"
                }
            ]
            mock_playhq_client.close.return_value = None
            mock_init_client.return_value = mock_playhq_client
            
            # Initialize sync
            sync = CricketDataSync()
            
            # Run fixture sync
            await sync.sync_fixtures()
            
            # Check vector upserts
            assert sync.sync_stats["fixtures_updated"] > 0
            assert sync.sync_stats["vector_upserts"] > 0
            
            # Check documents were stored with correct metadata
            fixture_docs = [doc for doc in mock_vector_client.documents.values() 
                          if doc.get("metadata", {}).get("type") == "fixture"]
            assert len(fixture_docs) > 0
            
            # Check metadata structure
            for doc in fixture_docs:
                metadata = doc["metadata"]
                assert "team_id" in metadata
                assert "season_id" in metadata
                assert "grade_id" in metadata
                assert "type" in metadata
                assert "date" in metadata
    
    def test_sync_status_with_vector_stats(self):
        """Test sync status includes vector statistics"""
        with patch('jobs.sync.get_settings') as mock_get_settings, \
             patch('jobs.sync.get_cscc_team_ids') as mock_get_team_ids, \
             patch('jobs.sync.get_cscc_org_id') as mock_get_org_id, \
             patch('jobs.sync.get_cscc_season_id') as mock_get_season_id, \
             patch('jobs.sync.get_cscc_grade_id') as mock_get_grade_id, \
             patch('jobs.sync.get_vector_client') as mock_get_vector_client:
            
            # Mock settings and IDs
            mock_settings = Mock()
            mock_settings.app_env = "test"
            mock_settings.playhq_mode = "public"
            mock_settings.vector_backend = "vertex_rag"
            mock_get_settings.return_value = mock_settings
            mock_get_team_ids.return_value = ["team-1"]
            mock_get_org_id.return_value = "org-1"
            mock_get_season_id.return_value = "season-1"
            mock_get_grade_id.return_value = "grade-1"
            
            # Mock vector client
            mock_vector_client = MockVectorClient("test-project")
            mock_get_vector_client.return_value = mock_vector_client
            
            # Initialize sync
            sync = CricketDataSync()
            
            # Get status
            status = sync.get_sync_status()
            
            # Check status structure
            assert "last_sync" in status
            assert "stats" in status
            assert "vector_stats" in status
            assert "cscc_team_ids" in status
            assert "settings" in status
            
            # Check vector stats
            vector_stats = status["vector_stats"]
            assert "total_documents" in vector_stats
            assert "project_id" in vector_stats
            assert "location" in vector_stats
            assert "embedding_model" in vector_stats
            
            # Check settings
            settings = status["settings"]
            assert settings["org_id"] == "org-1"
            assert settings["season_id"] == "season-1"
            assert settings["grade_id"] == "grade-1"
            assert settings["playhq_mode"] == "public"
            assert settings["vector_backend"] == "vertex_rag"


class TestSyncDeltaLogic:
    """Test sync job delta logic with vector client"""
    
    def test_delta_upsert_same_content(self):
        """Test that unchanged content is not upserted"""
        with patch('jobs.sync.get_settings') as mock_get_settings, \
             patch('jobs.sync.get_cscc_team_ids') as mock_get_team_ids, \
             patch('jobs.sync.get_cscc_org_id') as mock_get_org_id, \
             patch('jobs.sync.get_cscc_season_id') as mock_get_season_id, \
             patch('jobs.sync.get_cscc_grade_id') as mock_get_grade_id, \
             patch('jobs.sync.get_vector_client') as mock_get_vector_client:
            
            # Mock settings and IDs
            mock_settings = Mock()
            mock_get_settings.return_value = mock_settings
            mock_get_team_ids.return_value = ["team-1"]
            mock_get_org_id.return_value = "org-1"
            mock_get_season_id.return_value = "season-1"
            mock_get_grade_id.return_value = "grade-1"
            
            # Mock vector client
            mock_vector_client = MockVectorClient("test-project")
            mock_get_vector_client.return_value = mock_vector_client
            
            # Initialize sync
            sync = CricketDataSync()
            
            # First upsert
            docs = [{"id": "doc-1", "text": "Test content", "metadata": {"type": "test"}}]
            sync.vector_client.upsert(docs)
            initial_upserts = sync.sync_stats["vector_upserts"]
            
            # Same content should not be upserted again
            sync.vector_client.upsert(docs)
            final_upserts = sync.sync_stats["vector_upserts"]
            
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
            
            # Mock settings and IDs
            mock_settings = Mock()
            mock_get_settings.return_value = mock_settings
            mock_get_team_ids.return_value = ["team-1"]
            mock_get_org_id.return_value = "org-1"
            mock_get_season_id.return_value = "season-1"
            mock_get_grade_id.return_value = "grade-1"
            
            # Mock vector client
            mock_vector_client = MockVectorClient("test-project")
            mock_get_vector_client.return_value = mock_vector_client
            
            # Initialize sync
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
    """Test sync job error handling with vector client"""
    
    @pytest.mark.asyncio
    async def test_sync_error_handling(self):
        """Test sync error handling"""
        with patch('jobs.sync.get_settings') as mock_get_settings, \
             patch('jobs.sync.get_cscc_team_ids') as mock_get_team_ids, \
             patch('jobs.sync.get_cscc_org_id') as mock_get_org_id, \
             patch('jobs.sync.get_cscc_season_id') as mock_get_season_id, \
             patch('jobs.sync.get_cscc_grade_id') as mock_get_grade_id, \
             patch('jobs.sync.get_vector_client') as mock_get_vector_client:
            
            # Mock settings and IDs
            mock_settings = Mock()
            mock_get_settings.return_value = mock_settings
            mock_get_team_ids.return_value = ["team-1"]
            mock_get_org_id.return_value = "org-1"
            mock_get_season_id.return_value = "season-1"
            mock_get_grade_id.return_value = "grade-1"
            
            # Mock vector client
            mock_vector_client = MockVectorClient("test-project")
            mock_get_vector_client.return_value = mock_vector_client
            
            # Initialize sync
            sync = CricketDataSync()
            
            # Mock PlayHQ client to raise error
            with patch('jobs.sync.initialize_playhq_client') as mock_init_client:
                mock_init_client.side_effect = Exception("PlayHQ connection failed")
                
                # Run sync should handle error gracefully
                result = await sync.sync_all()
                
                # Check error handling
                assert result["status"] == "error"
                assert sync.sync_stats["errors"] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
