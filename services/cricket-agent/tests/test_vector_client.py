"""
Unit tests for vector client
Tests vector operations, filtering, batching, and delta upserts
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from agent.tools.vector_client import VectorClient, MockVectorClient, get_vector_client


class TestVectorClient:
    """Test vector client functionality"""
    
    def test_mock_client_initialization(self):
        """Test mock client initialization"""
        client = MockVectorClient("test-project", "us-central1")
        
        assert client.project_id == "test-project"
        assert client.location == "us-central1"
        assert client.embedding_model == "text-embedding-005"
        assert len(client.content_hashes) == 0
        assert len(client.documents) == 0
        assert len(client.queries) == 0
    
    def test_content_hash_generation(self):
        """Test content hash generation for delta detection"""
        client = MockVectorClient("test-project")
        
        doc1 = {
            "id": "test-1",
            "text": "Test content",
            "metadata": {"type": "test", "team_id": "team-1"}
        }
        
        doc2 = {
            "id": "test-1",
            "text": "Test content",
            "metadata": {"type": "test", "team_id": "team-1"}
        }
        
        doc3 = {
            "id": "test-1",
            "text": "Different content",
            "metadata": {"type": "test", "team_id": "team-1"}
        }
        
        hash1 = client._generate_content_hash(doc1)
        hash2 = client._generate_content_hash(doc2)
        hash3 = client._generate_content_hash(doc3)
        
        # Same content should generate same hash
        assert hash1 == hash2
        
        # Different content should generate different hash
        assert hash1 != hash3
    
    def test_should_upsert_delta_logic(self):
        """Test delta upsert logic"""
        client = MockVectorClient("test-project")
        
        doc = {
            "id": "test-1",
            "text": "Test content",
            "metadata": {"type": "test"}
        }
        
        # First time should upsert
        assert client._should_upsert(doc) == True
        
        # Same content should not upsert
        assert client._should_upsert(doc) == False
        
        # Modified content should upsert
        doc["text"] = "Modified content"
        assert client._should_upsert(doc) == True
    
    def test_upsert_documents(self):
        """Test document upserting"""
        client = MockVectorClient("test-project")
        
        docs = [
            {
                "id": "doc-1",
                "text": "First document",
                "metadata": {"type": "test", "team_id": "team-1"}
            },
            {
                "id": "doc-2", 
                "text": "Second document",
                "metadata": {"type": "test", "team_id": "team-2"}
            }
        ]
        
        # Upsert documents
        client.upsert(docs)
        
        # Check documents were stored
        assert len(client.documents) == 2
        assert "doc-1" in client.documents
        assert "doc-2" in client.documents
        
        # Check content hashes were stored
        assert len(client.content_hashes) == 2
        assert "doc-1" in client.content_hashes
        assert "doc-2" in client.content_hashes
    
    def test_upsert_delta_filtering(self):
        """Test that unchanged documents are filtered out"""
        client = MockVectorClient("test-project")
        
        docs = [
            {
                "id": "doc-1",
                "text": "First document",
                "metadata": {"type": "test"}
            }
        ]
        
        # First upsert
        client.upsert(docs)
        assert len(client.documents) == 1
        
        # Same content should not be upserted again
        client.upsert(docs)
        assert len(client.documents) == 1  # Still only 1 document
        
        # Modified content should be upserted
        docs[0]["text"] = "Modified document"
        client.upsert(docs)
        assert len(client.documents) == 1  # Still 1 document, but updated
    
    def test_query_without_filters(self):
        """Test querying without filters"""
        client = MockVectorClient("test-project")
        
        # Add some documents
        docs = [
            {
                "id": "doc-1",
                "text": "First document",
                "metadata": {"type": "test", "team_id": "team-1"}
            },
            {
                "id": "doc-2",
                "text": "Second document", 
                "metadata": {"type": "test", "team_id": "team-2"}
            }
        ]
        client.upsert(docs)
        
        # Query without filters
        results = client.query("test query", k=5)
        
        # Should return all documents
        assert len(results) == 2
        assert "doc-1" in results
        assert "doc-2" in results
        
        # Check query was logged
        assert len(client.queries) == 1
        assert client.queries[0]["text"] == "test query"
        assert client.queries[0]["k"] == 5
        assert client.queries[0]["filters"] is None
    
    def test_query_with_filters(self):
        """Test querying with metadata filters"""
        client = MockVectorClient("test-project")
        
        # Add documents with different metadata
        docs = [
            {
                "id": "doc-1",
                "text": "Team 1 document",
                "metadata": {"type": "fixture", "team_id": "team-1", "season_id": "season-1"}
            },
            {
                "id": "doc-2",
                "text": "Team 2 document",
                "metadata": {"type": "fixture", "team_id": "team-2", "season_id": "season-1"}
            },
            {
                "id": "doc-3",
                "text": "Team 1 ladder",
                "metadata": {"type": "ladder", "team_id": "team-1", "season_id": "season-1"}
            }
        ]
        client.upsert(docs)
        
        # Query with team filter
        results = client.query("test", filters={"team_id": "team-1"})
        assert len(results) == 2
        assert "doc-1" in results
        assert "doc-3" in results
        assert "doc-2" not in results
        
        # Query with type filter
        results = client.query("test", filters={"type": "fixture"})
        assert len(results) == 2
        assert "doc-1" in results
        assert "doc-2" in results
        assert "doc-3" not in results
        
        # Query with multiple filters
        results = client.query("test", filters={"team_id": "team-1", "type": "fixture"})
        assert len(results) == 1
        assert "doc-1" in results
    
    def test_query_limit(self):
        """Test query result limit"""
        client = MockVectorClient("test-project")
        
        # Add many documents
        docs = [
            {
                "id": f"doc-{i}",
                "text": f"Document {i}",
                "metadata": {"type": "test"}
            }
            for i in range(10)
        ]
        client.upsert(docs)
        
        # Query with limit
        results = client.query("test", k=3)
        assert len(results) == 3
        
        # Query with higher limit
        results = client.query("test", k=5)
        assert len(results) == 5
    
    def test_get_stats(self):
        """Test getting client statistics"""
        client = MockVectorClient("test-project")
        
        # Add some documents and queries
        docs = [
            {"id": "doc-1", "text": "Test", "metadata": {"type": "test"}},
            {"id": "doc-2", "text": "Test", "metadata": {"type": "test"}}
        ]
        client.upsert(docs)
        client.query("test query")
        
        stats = client.get_stats()
        
        assert stats["total_documents"] == 2
        assert stats["total_queries"] == 1
        assert stats["project_id"] == "test-project"
        assert stats["location"] == "us-central1"
        assert stats["embedding_model"] == "text-embedding-005"
    
    def test_clear_cache(self):
        """Test clearing content hash cache"""
        client = MockVectorClient("test-project")
        
        # Add documents
        docs = [{"id": "doc-1", "text": "Test", "metadata": {"type": "test"}}]
        client.upsert(docs)
        
        # Check cache has content
        assert len(client.content_hashes) == 1
        
        # Clear cache
        client.clear_cache()
        
        # Check cache is empty
        assert len(client.content_hashes) == 0


class TestVectorClientIntegration:
    """Test vector client integration with configuration"""
    
    @patch('agent.tools.vector_client.get_settings')
    def test_get_vector_client_test_mode(self, mock_get_settings):
        """Test getting vector client in test mode"""
        mock_settings = Mock()
        mock_settings.app_env = "test"
        mock_settings.gcp_project = "test-project"
        mock_settings.vertex_location = "us-central1"
        mock_get_settings.return_value = mock_settings
        
        client = get_vector_client()
        
        assert isinstance(client, MockVectorClient)
        assert client.project_id == "test-project"
        assert client.location == "us-central1"
    
    @patch('agent.tools.vector_client.get_settings')
    def test_get_vector_client_production_mode(self, mock_get_settings):
        """Test getting vector client in production mode"""
        mock_settings = Mock()
        mock_settings.app_env = "prod"
        mock_settings.gcp_project = "prod-project"
        mock_settings.vertex_location = "us-central1"
        mock_get_settings.return_value = mock_settings
        
        with patch('agent.tools.vector_client.VectorClient') as mock_vector_client:
            client = get_vector_client()
            mock_vector_client.assert_called_once_with(
                project_id="prod-project",
                location="us-central1"
            )


class TestVectorClientBatching:
    """Test vector client batching functionality"""
    
    def test_large_batch_upsert(self):
        """Test upserting large batch of documents"""
        client = MockVectorClient("test-project")
        
        # Create large batch
        docs = [
            {
                "id": f"doc-{i}",
                "text": f"Document {i} content",
                "metadata": {"type": "test", "team_id": f"team-{i % 5}"}
            }
            for i in range(150)  # Larger than typical batch size
        ]
        
        # Upsert should handle large batches
        client.upsert(docs)
        
        # All documents should be stored
        assert len(client.documents) == 150
        assert len(client.content_hashes) == 150
    
    def test_mixed_content_upsert(self):
        """Test upserting mixed content types"""
        client = MockVectorClient("test-project")
        
        docs = [
            {
                "id": "fixture-1",
                "text": "Caroline Springs Blue vs White - Saturday 2pm",
                "metadata": {"type": "fixture", "team_id": "team-1", "season_id": "season-1"}
            },
            {
                "id": "ladder-1", 
                "text": "Ladder: 1. Blue (4-0), 2. White (3-1)",
                "metadata": {"type": "ladder", "season_id": "season-1", "grade_id": "grade-1"}
            },
            {
                "id": "roster-1",
                "text": "Team Blue: John Smith, Jane Doe, Bob Wilson",
                "metadata": {"type": "roster", "team_id": "team-1", "season_id": "season-1"}
            }
        ]
        
        client.upsert(docs)
        
        # All documents should be stored
        assert len(client.documents) == 3
        
        # Query by type
        fixture_results = client.query("fixtures", filters={"type": "fixture"})
        assert len(fixture_results) == 1
        assert "fixture-1" in fixture_results
        
        # Query by team
        team_results = client.query("team", filters={"team_id": "team-1"})
        assert len(team_results) == 2  # fixture and roster
        assert "fixture-1" in team_results
        assert "roster-1" in team_results


class TestVectorClientEdgeCases:
    """Test vector client edge cases"""
    
    def test_empty_docs_upsert(self):
        """Test upserting empty document list"""
        client = MockVectorClient("test-project")
        
        # Should not raise error
        client.upsert([])
        
        assert len(client.documents) == 0
        assert len(client.content_hashes) == 0
    
    def test_none_docs_upsert(self):
        """Test upserting None document list"""
        client = MockVectorClient("test-project")
        
        # Should not raise error
        client.upsert(None)
        
        assert len(client.documents) == 0
    
    def test_doc_without_id(self):
        """Test document without ID"""
        client = MockVectorClient("test-project")
        
        docs = [
            {
                "text": "Document without ID",
                "metadata": {"type": "test"}
            }
        ]
        
        # Should handle gracefully
        client.upsert(docs)
        
        # Document should be stored with generated ID or handled appropriately
        # This depends on implementation details
    
    def test_query_empty_store(self):
        """Test querying empty vector store"""
        client = MockVectorClient("test-project")
        
        results = client.query("test query")
        
        assert len(results) == 0
    
    def test_query_with_invalid_filters(self):
        """Test querying with invalid filter values"""
        client = MockVectorClient("test-project")
        
        # Add a document
        docs = [{"id": "doc-1", "text": "Test", "metadata": {"type": "test"}}]
        client.upsert(docs)
        
        # Query with filters that don't match
        results = client.query("test", filters={"team_id": "nonexistent"})
        
        # Should return empty results
        assert len(results) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
