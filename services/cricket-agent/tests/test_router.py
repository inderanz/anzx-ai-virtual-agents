"""
Tests for cricket agent router functionality
"""

import pytest
import json
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from agent.router import IntentRouter, get_router
from agent.llm_agent import MockLLMAgent
from agent.prompt import format_response, format_fixture_date, format_ladder_position


class TestIntentRouter:
    """Test intent router functionality"""
    
    @pytest.fixture
    def mock_router(self):
        """Create a mock router instance"""
        with patch('agent.router.get_settings') as mock_get_settings, \
             patch('agent.router.get_vector_client') as mock_get_vector_client, \
             patch('agent.router.initialize_playhq_client') as mock_init_playhq:
            
            # Mock settings
            mock_settings = Mock()
            mock_settings.gcp_project = "test-project"
            mock_settings.vertex_location = "us-central1"
            mock_get_settings.return_value = mock_settings
            
            # Mock vector client
            mock_vector_client = Mock()
            mock_vector_client.query.return_value = ["Mock RAG result"]
            mock_get_vector_client.return_value = mock_vector_client
            
            # Mock PlayHQ client
            mock_playhq_client = AsyncMock()
            mock_init_playhq.return_value = mock_playhq_client
            
            router = IntentRouter()
            router.llm_agent = MockLLMAgent()
            return router
    
    def test_router_initialization(self, mock_router):
        """Test router initialization"""
        assert mock_router.settings is not None
        assert mock_router.vector_client is not None
        assert mock_router.llm_agent is not None
        assert len(mock_router.intent_patterns) == 6
    
    def test_intent_patterns(self, mock_router):
        """Test intent pattern matching"""
        # Test player team intent
        text = "Which team player John Smith is part of?"
        result = mock_router._detect_intent(text)
        assert result["intent"] == "player_team"
        assert "player" in result["entities"]
        
        # Test player last runs intent
        text = "How many runs did John Smith score in last match?"
        result = mock_router._detect_intent(text)
        assert result["intent"] == "player_last_runs"
        assert "player" in result["entities"]
        
        # Test fixtures list intent
        text = "List all fixtures for Caroline Springs Blue U10"
        result = mock_router._detect_intent(text)
        assert result["intent"] == "fixtures_list"
        assert "team" in result["entities"]
        
        # Test ladder position intent
        text = "Where are Caroline Springs Blue U10 on the ladder?"
        result = mock_router._detect_intent(text)
        assert result["intent"] == "ladder_position"
        assert "team" in result["entities"]
        
        # Test next fixture intent
        text = "Next fixture for Caroline Springs Blue U10"
        result = mock_router._detect_intent(text)
        assert result["intent"] == "next_fixture"
        assert "team" in result["entities"]
        
        # Test roster list intent
        text = "List all players for Caroline Springs Blue U10"
        result = mock_router._detect_intent(text)
        assert result["intent"] == "roster_list"
        assert "team" in result["entities"]
    
    def test_entity_extraction(self, mock_router):
        """Test entity extraction from regex matches"""
        # Test player entity extraction
        import re
        pattern = r"which team.*player\s+(\w+).*is\s+part\s+of"
        match = re.search(pattern, "which team player John Smith is part of")
        entities = mock_router._extract_entities_from_match(match, "player_team")
        assert entities["player"] == "John Smith"
        
        # Test team entity extraction
        pattern = r"list.*fixtures.*(\w+.*\w+)"
        match = re.search(pattern, "list fixtures for Caroline Springs Blue U10")
        entities = mock_router._extract_entities_from_match(match, "fixtures_list")
        assert entities["team"] == "Caroline Springs Blue U10"
    
    def test_team_name_normalization(self, mock_router):
        """Test team name normalization"""
        # Test common variations
        assert mock_router._normalize_team_name("blue 10s") == "Caroline Springs Blue U10"
        assert mock_router._normalize_team_name("blue u10") == "Caroline Springs Blue U10"
        assert mock_router._normalize_team_name("white 10s") == "Caroline Springs White U10"
        assert mock_router._normalize_team_name("white u10") == "Caroline Springs White U10"
        
        # Test unknown team
        assert mock_router._normalize_team_name("unknown team") == "unknown team"
    
    @pytest.mark.asyncio
    async def test_route_query_success(self, mock_router):
        """Test successful query routing"""
        result = await mock_router.route_query(
            text="Which team player John Smith is part of?",
            source="web"
        )
        
        assert "answer" in result
        assert "meta" in result
        assert result["meta"]["intent"] == "player_team"
        assert result["meta"]["source"] == "web"
        assert "request_id" in result["meta"]
    
    @pytest.mark.asyncio
    async def test_route_query_with_team_hint(self, mock_router):
        """Test query routing with team hint"""
        result = await mock_router.route_query(
            text="How many runs did John Smith score?",
            source="web",
            team_hint="Caroline Springs Blue U10"
        )
        
        assert "answer" in result
        assert "meta" in result
        assert result["meta"]["intent"] == "player_last_runs"
        assert "team" in result["meta"]["entities"]
    
    @pytest.mark.asyncio
    async def test_route_query_error_handling(self, mock_router):
        """Test query routing error handling"""
        # Mock an error in the router
        with patch.object(mock_router, '_detect_intent', side_effect=Exception("Test error")):
            result = await mock_router.route_query(
                text="Test query",
                source="web"
            )
            
            assert "answer" in result
            assert "error" in result["meta"]
            assert "I'm sorry" in result["answer"]
    
    def test_cache_functionality(self, mock_router):
        """Test caching functionality"""
        # Test cache miss
        cache_key = "test_key"
        result = mock_router._get_from_cache(cache_key)
        assert result is None
        
        # Test cache set and get
        test_response = {"answer": "test", "meta": {"intent": "test"}}
        mock_router._cache_response(cache_key, test_response)
        
        cached_result = mock_router._get_from_cache(cache_key)
        assert cached_result == test_response
    
    def test_rag_query(self, mock_router):
        """Test RAG query functionality"""
        # Mock vector client query
        mock_router.vector_client.query.return_value = ["Mock result 1", "Mock result 2"]
        
        # Test RAG query
        entities = {"team": "Caroline Springs Blue U10"}
        results = mock_router._query_rag("test query", entities)
        
        assert len(results) == 2
        assert "Mock result 1" in results
        assert "Mock result 2" in results
    
    def test_team_id_lookup(self, mock_router):
        """Test team ID lookup from name"""
        # Mock settings with team data
        mock_settings = Mock()
        mock_team = Mock()
        mock_team.name = "Caroline Springs Blue U10"
        mock_team.team_id = "team-123"
        mock_settings.ids_bundle.teams = [mock_team]
        
        with patch('agent.router.get_settings', return_value=mock_settings):
            team_id = mock_router._get_team_id_from_name("Caroline Springs Blue U10")
            assert team_id == "team-123"
            
            # Test unknown team
            team_id = mock_router._get_team_id_from_name("Unknown Team")
            assert team_id is None


class TestHandlerFunctions:
    """Test individual handler functions"""
    
    @pytest.fixture
    def mock_router(self):
        """Create a mock router for handler testing"""
        with patch('agent.router.get_settings') as mock_get_settings, \
             patch('agent.router.get_vector_client') as mock_get_vector_client, \
             patch('agent.router.initialize_playhq_client') as mock_init_playhq:
            
            mock_settings = Mock()
            mock_get_settings.return_value = mock_settings
            
            mock_vector_client = Mock()
            mock_get_vector_client.return_value = mock_vector_client
            
            mock_playhq_client = AsyncMock()
            mock_init_playhq.return_value = mock_playhq_client
            
            router = IntentRouter()
            router.llm_agent = MockLLMAgent()
            return router
    
    @pytest.mark.asyncio
    async def test_player_team_handler(self, mock_router):
        """Test player team handler"""
        entities = {"player": "John Smith"}
        rag_results = ["Team: Caroline Springs Blue U10\nPlayer: John Smith"]
        
        result = await mock_router._handle_player_team(entities, rag_results)
        
        assert "John Smith" in result
        assert "Caroline Springs Blue U10" in result
    
    @pytest.mark.asyncio
    async def test_player_last_runs_handler(self, mock_router):
        """Test player last runs handler"""
        entities = {"player": "John Smith"}
        rag_results = ["John Smith: 45 runs (30 balls)"]
        
        result = await mock_router._handle_player_last_runs(entities, rag_results)
        
        assert "John Smith" in result
        assert "runs" in result
    
    @pytest.mark.asyncio
    async def test_fixtures_list_handler(self, mock_router):
        """Test fixtures list handler"""
        entities = {"team": "Caroline Springs Blue U10"}
        rag_results = []
        
        # Mock PlayHQ client
        mock_playhq_client = AsyncMock()
        mock_playhq_client.get_team_fixtures.return_value = [
            {
                "id": "fixture-1",
                "date": "2025-10-15T09:00:00Z",
                "opponent": "Melbourne CC",
                "venue": "Home Ground",
                "status": "scheduled"
            }
        ]
        
        with patch('agent.router.initialize_playhq_client', return_value=mock_playhq_client):
            result = await mock_router._handle_fixtures_list(entities, rag_results)
            
            assert "Caroline Springs Blue U10" in result
            assert "fixtures" in result.lower()
    
    @pytest.mark.asyncio
    async def test_ladder_position_handler(self, mock_router):
        """Test ladder position handler"""
        entities = {"team": "Caroline Springs Blue U10"}
        rag_results = []
        
        # Mock PlayHQ client
        mock_playhq_client = AsyncMock()
        mock_playhq_client.get_ladder.return_value = [
            {
                "team_id": "team-123",
                "position": 2,
                "points": 12,
                "matches_played": 5,
                "matches_won": 3,
                "matches_lost": 2
            }
        ]
        
        with patch('agent.router.initialize_playhq_client', return_value=mock_playhq_client):
            result = await mock_router._handle_ladder_position(entities, rag_results)
            
            assert "Caroline Springs Blue U10" in result
            assert "position" in result.lower()
    
    @pytest.mark.asyncio
    async def test_next_fixture_handler(self, mock_router):
        """Test next fixture handler"""
        entities = {"team": "Caroline Springs Blue U10"}
        rag_results = []
        
        # Mock PlayHQ client
        mock_playhq_client = AsyncMock()
        mock_playhq_client.get_team_fixtures.return_value = [
            {
                "id": "fixture-1",
                "date": "2025-10-15T09:00:00Z",
                "opponent": "Melbourne CC",
                "venue": "Home Ground",
                "status": "scheduled"
            }
        ]
        
        with patch('agent.router.initialize_playhq_client', return_value=mock_playhq_client):
            result = await mock_router._handle_next_fixture(entities, rag_results)
            
            assert "Caroline Springs Blue U10" in result
            assert "next fixture" in result.lower()
    
    @pytest.mark.asyncio
    async def test_roster_list_handler(self, mock_router):
        """Test roster list handler"""
        entities = {"team": "Caroline Springs Blue U10"}
        rag_results = []
        
        # Mock PlayHQ client
        mock_playhq_client = AsyncMock()
        mock_playhq_client.get_team_fixtures.return_value = [
            {
                "id": "fixture-1",
                "status": "completed"
            }
        ]
        mock_playhq_client.get_game_summary.return_value = {
            "players": [
                {"name": "John Smith", "team_id": "team-123"},
                {"name": "Sarah Jones", "team_id": "team-123"}
            ]
        }
        
        with patch('agent.router.initialize_playhq_client', return_value=mock_playhq_client):
            result = await mock_router._handle_roster_list(entities, rag_results)
            
            assert "Caroline Springs Blue U10" in result
            assert "roster" in result.lower()


class TestPromptFormatting:
    """Test prompt formatting functions"""
    
    def test_format_response(self):
        """Test response formatting"""
        answer = "Test answer"
        meta = {"intent": "test", "latency_ms": 100}
        
        result = format_response(answer, meta)
        
        assert result["answer"] == answer
        assert result["meta"] == meta
    
    def test_format_fixture_date(self):
        """Test fixture date formatting"""
        # Test valid date
        date_str = "2025-10-15T09:00:00Z"
        formatted = format_fixture_date(date_str)
        
        assert "Oct" in formatted
        assert "2025" in formatted
        
        # Test invalid date
        invalid_date = "invalid-date"
        formatted = format_fixture_date(invalid_date)
        assert formatted == invalid_date
        
        # Test empty date
        formatted = format_fixture_date("")
        assert formatted == "TBD"
    
    def test_format_ladder_position(self):
        """Test ladder position formatting"""
        result = format_ladder_position(
            position=2,
            team_name="Caroline Springs Blue U10",
            points=12,
            played=5,
            won=3,
            lost=2
        )
        
        assert "Caroline Springs Blue U10" in result
        assert "2" in result
        assert "12" in result
        assert "5" in result
        assert "3" in result
        assert "2" in result


class TestRouterIntegration:
    """Test router integration"""
    
    @pytest.mark.asyncio
    async def test_get_router(self):
        """Test router instance creation"""
        router = get_router()
        assert isinstance(router, IntentRouter)
        
        # Test singleton behavior
        router2 = get_router()
        assert router is router2
    
    @pytest.mark.asyncio
    async def test_end_to_end_query(self):
        """Test end-to-end query processing"""
        with patch('agent.router.get_settings') as mock_get_settings, \
             patch('agent.router.get_vector_client') as mock_get_vector_client, \
             patch('agent.router.initialize_playhq_client') as mock_init_playhq:
            
            # Mock settings
            mock_settings = Mock()
            mock_settings.gcp_project = "test-project"
            mock_settings.vertex_location = "us-central1"
            mock_get_settings.return_value = mock_settings
            
            # Mock vector client
            mock_vector_client = Mock()
            mock_vector_client.query.return_value = ["Mock RAG result"]
            mock_get_vector_client.return_value = mock_vector_client
            
            # Mock PlayHQ client
            mock_playhq_client = AsyncMock()
            mock_playhq_client.get_team_fixtures.return_value = []
            mock_init_playhq.return_value = mock_playhq_client
            
            router = get_router()
            router.llm_agent = MockLLMAgent()
            
            result = await router.route_query(
                text="Which team player John Smith is part of?",
                source="web"
            )
            
            assert "answer" in result
            assert "meta" in result
            assert result["meta"]["intent"] == "player_team"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
