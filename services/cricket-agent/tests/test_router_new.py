"""
Tests for cricket agent router functionality
"""

import pytest
import json
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from agent.router import IntentRouter, get_router
from app.config import Settings, IDsBundle, TeamInfo


class TestIntentRouter:
    """Test intent router functionality"""
    
    @pytest.fixture
    def mock_settings(self):
        """Mock settings for testing"""
        settings = Settings(
            app_env="test",
            gcp_project="test-project",
            vertex_location="us-central1",
            playhq_mode="public",
            secret_internal_token="test-token",
            secret_playhq_api_key="test-api-key",
            secret_ids_bundle="test-ids-bundle",
            ids_bundle=IDsBundle(
                tenant="ca",
                org_id="org-1",
                season_id="season-1",
                grade_id="grade-1",
                teams=[
                    TeamInfo(name="Caroline Springs Blue U10", team_id="team-blue-1"),
                    TeamInfo(name="Caroline Springs White U10", team_id="team-white-2"),
                ]
            )
        )
        return settings
    
    @pytest.fixture
    def mock_router(self, mock_settings):
        """Create a mock router instance"""
        with patch('agent.router.get_settings', return_value=mock_settings), \
             patch('agent.router.get_cscc_team_ids', return_value=["team-blue-1", "team-white-2"]), \
             patch('agent.router.get_cscc_org_id', return_value="org-1"), \
             patch('agent.router.get_cscc_season_id', return_value="season-1"), \
             patch('agent.router.get_cscc_grade_id', return_value="grade-1"), \
             patch('agent.router.is_private_mode', return_value=False), \
             patch('agent.tools.vector_client.get_vector_client') as mock_get_vector_client, \
             patch('agent.tools.playhq.initialize_playhq_client') as mock_init_playhq, \
             patch('agent.llm_agent.LLMAgent') as mock_llm_agent_class:
            
            # Mock vector client
            mock_vector_client = Mock()
            mock_vector_client.query.return_value = ["Mock RAG result"]
            mock_get_vector_client.return_value = mock_vector_client
            
            # Mock PlayHQ client
            mock_playhq_client = AsyncMock()
            mock_init_playhq.return_value = mock_playhq_client
            
            # Mock LLM agent
            mock_llm_agent = Mock()
            mock_llm_agent.classify_intent = AsyncMock(return_value='{"intent": "general_query", "entities": {}}')
            mock_llm_agent.summarise = AsyncMock(return_value="Mock summary")
            mock_llm_agent_class.return_value = mock_llm_agent
            
            router = IntentRouter()
            router.vector_client = mock_vector_client
            router.playhq_client = mock_playhq_client
            router.llm_agent = mock_llm_agent
            return router, mock_vector_client, mock_playhq_client, mock_llm_agent
    
    def test_router_initialization(self, mock_router):
        """Test router initialization"""
        router, _, _, _ = mock_router
        assert router.settings is not None
        assert router.vector_client is not None
        assert router.llm_agent is not None
        assert len(router.intents) == 7  # 6 canonical + general_query
        assert len(router.handlers) == 7
    
    @pytest.mark.asyncio
    async def test_regex_player_team_intent(self, mock_router):
        """Test regex detection of player team intent"""
        router, _, _, _ = mock_router
        text = "Which team player John Doe is part of?"
        intent, entities = await router._detect_intent(text, None)
        assert intent == "player_team"
        assert entities["player_name"] == "John Doe"
    
    @pytest.mark.asyncio
    async def test_regex_player_last_runs_intent(self, mock_router):
        """Test regex detection of player last runs intent"""
        router, _, _, _ = mock_router
        text = "How many runs did Jane Smith score in last match?"
        intent, entities = await router._detect_intent(text, None)
        assert intent == "player_last_runs"
        assert entities["player_name"] == "Jane Smith"
    
    @pytest.mark.asyncio
    async def test_regex_fixtures_list_intent(self, mock_router):
        """Test regex detection of fixtures list intent"""
        router, _, _, _ = mock_router
        text = "Under WRJCA 2025/26 for Caroline Springs Blue 10s, list all fixtures"
        intent, entities = await router._detect_intent(text, None)
        assert intent == "fixtures_list"
        assert entities["team_name"] == "Caroline Springs Blue 10s"
    
    @pytest.mark.asyncio
    async def test_regex_ladder_position_intent(self, mock_router):
        """Test regex detection of ladder position intent"""
        router, _, _, _ = mock_router
        text = "Where are Caroline Springs Blue 10s on the ladder?"
        intent, entities = await router._detect_intent(text, None)
        assert intent == "ladder_position"
        assert entities["team_name"] == "Caroline Springs Blue 10s"
    
    @pytest.mark.asyncio
    async def test_regex_next_fixture_intent(self, mock_router):
        """Test regex detection of next fixture intent"""
        router, _, _, _ = mock_router
        text = "For Caroline Springs White 10s, next fixture venue and start time?"
        intent, entities = await router._detect_intent(text, None)
        assert intent == "next_fixture"
        assert entities["team_name"] == "Caroline Springs White 10s"
    
    @pytest.mark.asyncio
    async def test_regex_roster_list_intent(self, mock_router):
        """Test regex detection of roster list intent"""
        router, _, _, _ = mock_router
        text = "For Caroline Springs White 10s, list all players"
        intent, entities = await router._detect_intent(text, None)
        assert intent == "roster_list"
        assert entities["team_name"] == "Caroline Springs White 10s"
    
    @pytest.mark.asyncio
    async def test_llm_fallback_intent(self, mock_router):
        """Test LLM fallback for intent classification"""
        router, _, _, mock_llm_agent = mock_router
        mock_llm_agent.classify_intent.return_value = json.dumps({
            "intent": "general_query",
            "entities": {"topic": "cricket rules"}
        })
        text = "Tell me about cricket rules"
        intent, entities = await router._detect_intent(text, None)
        assert intent == "general_query"
        assert entities["topic"] == "cricket rules"
        mock_llm_agent.classify_intent.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_team_id_resolution(self, mock_router):
        """Test team name to ID resolution"""
        router, _, _, _ = mock_router
        team_id = await router._resolve_team_id("Caroline Springs Blue U10")
        assert team_id == "team-blue-1"
        
        team_id = await router._resolve_team_id("Unknown Team")
        assert team_id is None
    
    @pytest.mark.asyncio
    async def test_player_team_handler_rag_hit(self, mock_router):
        """Test player team handler with RAG hit"""
        router, mock_vector_client, _, mock_llm_agent = mock_router
        mock_vector_client.query.return_value = ["Team: Caroline Springs Blue U10, Player: John Doe"]
        mock_llm_agent.summarise.return_value = "Team: Caroline Springs Blue U10"
        
        result = await router._player_team_handler("Which team is John Doe in?", {"player_name": "John Doe"})
        assert "Caroline Springs Blue U10" in result["answer"]
        mock_vector_client.query.assert_called_once()
        mock_llm_agent.summarise.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_player_team_handler_playhq_fallback(self, mock_router):
        """Test player team handler with PlayHQ fallback"""
        router, mock_vector_client, mock_playhq_client, _ = mock_router
        mock_vector_client.query.return_value = []  # RAG miss
        
        mock_playhq_client.get_team_roster.side_effect = [
            {"id": "roster-blue", "teamId": "team-blue-1", "players": [{"id": "p1", "name": "John Doe"}]},
            {"id": "roster-white", "teamId": "team-white-2", "players": [{"id": "p2", "name": "Jane Smith"}]}
        ]
        
        result = await router._player_team_handler("Which team is John Doe in?", {"player_name": "John Doe"})
        assert "Caroline Springs Blue U10" in result["answer"]
        mock_playhq_client.get_team_roster.assert_called()
    
    @pytest.mark.asyncio
    async def test_fixtures_list_handler_success(self, mock_router):
        """Test fixtures list handler success"""
        router, _, mock_playhq_client, _ = mock_router
        mock_playhq_client.get_team_fixtures.return_value = [
            {"id": "f1", "status": "SCHEDULED", "date": "2025-10-12T10:00:00Z", "venue": "Venue A", "homeTeam": {"name": "Team A"}, "awayTeam": {"name": "Caroline Springs Blue U10"}},
            {"id": "f2", "status": "COMPLETED", "date": "2025-10-05T10:00:00Z", "venue": "Venue B", "homeTeam": {"name": "Caroline Springs Blue U10"}, "awayTeam": {"name": "Team B"}, "result": "Won by 10 runs"}
        ]
        
        result = await router._fixtures_list_handler("List all fixtures for Caroline Springs Blue U10", {"team_name": "Caroline Springs Blue U10"})
        assert "Upcoming Fixtures" in result["answer"]
        assert "Last Completed Fixtures" in result["answer"]
        assert "Venue A" in result["answer"]
        assert "Won by 10 runs" in result["answer"]
    
    @pytest.mark.asyncio
    async def test_ladder_position_handler_success(self, mock_router):
        """Test ladder position handler success"""
        router, _, mock_playhq_client, _ = mock_router
        mock_playhq_client.get_ladder.return_value = [
            {"teamId": "team-blue-1", "teamName": "Caroline Springs Blue U10", "position": 1, "points": 10, "matchesPlayed": 5, "matchesWon": 4, "matchesLost": 1}
        ]
        
        result = await router._ladder_position_handler("Where are Caroline Springs Blue U10 on the ladder?", {"team_name": "Caroline Springs Blue U10"})
        assert "1st position" in result["answer"]
        assert "Points 10" in result["answer"]
        assert "As of" in result["answer"]
    
    @pytest.mark.asyncio
    async def test_next_fixture_handler_success(self, mock_router):
        """Test next fixture handler success"""
        router, _, mock_playhq_client, _ = mock_router
        mock_playhq_client.get_team_fixtures.return_value = [
            {"id": "f1", "status": "COMPLETED", "date": "2025-10-05T10:00:00Z", "venue": "Venue A", "homeTeam": {"name": "Team A"}, "awayTeam": {"name": "Caroline Springs Blue U10"}},
            {"id": "f2", "status": "SCHEDULED", "date": "2025-10-12T10:00:00Z", "venue": "Next Venue", "homeTeam": {"name": "Caroline Springs Blue U10"}, "awayTeam": {"name": "Next Opponent"}},
            {"id": "f3", "status": "SCHEDULED", "date": "2025-10-19T10:00:00Z", "venue": "Later Venue", "homeTeam": {"name": "Later Opponent"}, "awayTeam": {"name": "Caroline Springs Blue U10"}}
        ]
        
        result = await router._next_fixture_handler("Next fixture for Caroline Springs Blue U10?", {"team_name": "Caroline Springs Blue U10"})
        assert "Next Opponent" in result["answer"]
        assert "Next Venue" in result["answer"]
        assert "on" in result["answer"]  # Date formatting
    
    @pytest.mark.asyncio
    async def test_roster_list_handler_success(self, mock_router):
        """Test roster list handler success"""
        router, _, mock_playhq_client, _ = mock_router
        mock_playhq_client.get_team_roster.return_value = {
            "id": "roster-blue", "teamId": "team-blue-1",
            "players": [
                {"id": "p1", "name": "John Doe", "email": "john@example.com", "roles": ["Captain"]},
                {"id": "p2", "name": "Jane Smith", "phone": "1234567890", "roles": ["Player"]}
            ]
        }
        
        result = await router._roster_list_handler("List players for Caroline Springs Blue U10", {"team_name": "Caroline Springs Blue U10"})
        assert "John Doe" in result["answer"]
        assert "Jane Smith" in result["answer"]
        assert "john@example.com" not in result["answer"]  # PII stripped
        assert "1234567890" not in result["answer"]  # PII stripped
        assert "Captain" not in result["answer"]  # Roles stripped in public mode
    
    @pytest.mark.asyncio
    async def test_general_query_handler_rag_hit(self, mock_router):
        """Test general query handler with RAG hit"""
        router, mock_vector_client, _, mock_llm_agent = mock_router
        mock_vector_client.query.return_value = ["Snippet about cricket rules."]
        mock_llm_agent.summarise.return_value = "Cricket rules are complex..."
        
        result = await router._general_query_handler("Tell me about cricket rules", {})
        assert "Cricket rules are complex" in result["answer"]
        assert result["meta"]["rag_hit"] is True
        mock_vector_client.query.assert_called_once()
        mock_llm_agent.summarise.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_general_query_handler_rag_miss(self, mock_router):
        """Test general query handler with RAG miss"""
        router, mock_vector_client, _, mock_llm_agent = mock_router
        mock_vector_client.query.return_value = []  # RAG miss
        
        result = await router._general_query_handler("Tell me about something obscure", {})
        assert "I don't have enough information" in result["answer"]
        assert result["meta"]["rag_hit"] is False
        mock_vector_client.query.assert_called_once()
        mock_llm_agent.summarise.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_cache_functionality(self, mock_router):
        """Test caching functionality"""
        router, _, _, _ = mock_router
        router.cache_ttl_seconds = 1  # Short TTL for testing
        
        # First call - populate cache
        await router.route_query("Which team player John Doe is part of?", "web")
        
        # Second call - should hit cache
        result = await router.route_query("Which team player John Doe is part of?", "web")
        
        assert result["meta"]["cache_hit"] is True
        assert result["meta"]["latency_ms"] < 100  # Should be very fast
    
    @pytest.mark.asyncio
    async def test_route_query_success(self, mock_router):
        """Test successful query routing"""
        router, _, _, _ = mock_router
        result = await router.route_query("Which team player John Doe is part of?", "web")
        
        assert "answer" in result
        assert "meta" in result
        assert result["meta"]["intent"] == "player_team"
        assert result["meta"]["entities"]["player_name"] == "John Doe"
        assert result["meta"]["cache_hit"] is False
    
    @pytest.mark.asyncio
    async def test_route_query_with_team_hint(self, mock_router):
        """Test query routing with team hint"""
        router, _, _, _ = mock_router
        result = await router.route_query("List all players", "web", "Caroline Springs Blue U10")
        
        assert "answer" in result
        assert "meta" in result
        assert result["meta"]["entities"]["team_name"] == "Caroline Springs Blue U10"
    
    @pytest.mark.asyncio
    async def test_route_query_error_handling(self, mock_router):
        """Test error handling in query routing"""
        router, _, _, _ = mock_router
        # This should not raise an exception
        result = await router.route_query("", "web")
        assert "answer" in result


class TestRouterIntegration:
    """Test router integration"""
    
    def test_get_router_singleton(self):
        """Test router singleton pattern"""
        router1 = get_router()
        router2 = get_router()
        assert router1 is router2  # Should be the same instance
