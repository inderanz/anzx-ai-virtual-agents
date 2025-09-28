"""
PlayHQ API Client
Handles all interactions with PlayHQ public APIs
Implements retries, pagination, and error handling
"""

import asyncio
import time
from typing import Dict, Any, List, Optional, AsyncGenerator
from dataclasses import dataclass
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import logging

from app.config import get_settings, get_playhq_headers

logger = logging.getLogger(__name__)

@dataclass
class PlayHQResponse:
    """PlayHQ API response wrapper"""
    data: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    has_more: bool
    cursor: Optional[str] = None

class PlayHQClient:
    """PlayHQ API client with retry logic and pagination"""
    
    def __init__(self):
        self.settings = get_settings()
        self.headers = get_playhq_headers()
        self.base_url = self.settings.playhq_base_url
        self.timeout = 30.0
        
        # HTTP client with retry configuration
        self.client = httpx.AsyncClient(
            headers=self.headers,
            timeout=self.timeout,
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
        )
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.HTTPStatusError))
    )
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> httpx.Response:
        """Make HTTP request with retry logic"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = await self.client.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                logger.warning(f"Rate limited by PlayHQ API: {e}")
                raise
            elif e.response.status_code >= 500:
                logger.warning(f"PlayHQ API server error: {e}")
                raise
            else:
                logger.error(f"PlayHQ API error: {e}")
                raise
        except httpx.TimeoutException as e:
            logger.warning(f"PlayHQ API timeout: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error calling PlayHQ API: {e}")
            raise
    
    async def get_seasons(self, org_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get seasons for an organization"""
        endpoint = f"/organisations/{org_id}/seasons" if org_id else "/seasons"
        
        try:
            response = await self._make_request("GET", endpoint)
            data = response.json()
            
            # Handle pagination if present
            if isinstance(data, dict) and "data" in data:
                return data["data"]
            elif isinstance(data, list):
                return data
            else:
                return []
                
        except Exception as e:
            logger.error(f"Failed to get seasons: {e}")
            return []
    
    async def get_grades(self, season_id: str) -> List[Dict[str, Any]]:
        """Get grades for a season"""
        endpoint = f"/seasons/{season_id}/grades"
        
        try:
            response = await self._make_request("GET", endpoint)
            data = response.json()
            
            if isinstance(data, dict) and "data" in data:
                return data["data"]
            elif isinstance(data, list):
                return data
            else:
                return []
                
        except Exception as e:
            logger.error(f"Failed to get grades for season {season_id}: {e}")
            return []
    
    async def get_teams(self, grade_id: str) -> List[Dict[str, Any]]:
        """Get teams for a grade"""
        endpoint = f"/grades/{grade_id}/teams"
        
        try:
            response = await self._make_request("GET", endpoint)
            data = response.json()
            
            if isinstance(data, dict) and "data" in data:
                return data["data"]
            elif isinstance(data, list):
                return data
            else:
                return []
                
        except Exception as e:
            logger.error(f"Failed to get teams for grade {grade_id}: {e}")
            return []
    
    async def get_team_fixtures(self, team_id: str, season_id: str) -> List[Dict[str, Any]]:
        """Get fixtures for a team in a season"""
        endpoint = f"/teams/{team_id}/fixtures"
        params = {"season": season_id}
        
        try:
            # Handle pagination
            all_fixtures = []
            cursor = None
            
            while True:
                if cursor:
                    params["cursor"] = cursor
                
                response = await self._make_request("GET", endpoint, params=params)
                data = response.json()
                
                if isinstance(data, dict):
                    fixtures = data.get("data", [])
                    all_fixtures.extend(fixtures)
                    
                    # Check for more pages
                    metadata = data.get("metadata", {})
                    if not metadata.get("hasMore", False):
                        break
                    cursor = metadata.get("cursor")
                else:
                    break
            
            return all_fixtures
            
        except Exception as e:
            logger.error(f"Failed to get fixtures for team {team_id}: {e}")
            return []
    
    async def get_game_summary(self, game_id: str) -> Optional[Dict[str, Any]]:
        """Get summary for a specific game"""
        endpoint = f"/summary/{game_id}"
        
        try:
            response = await self._make_request("GET", endpoint)
            data = response.json()
            
            return data if isinstance(data, dict) else None
            
        except Exception as e:
            logger.error(f"Failed to get game summary for {game_id}: {e}")
            return None
    
    async def get_ladder(self, grade_id: str) -> List[Dict[str, Any]]:
        """Get ladder for a grade"""
        endpoint = f"/ladder/{grade_id}"
        
        try:
            response = await self._make_request("GET", endpoint)
            data = response.json()
            
            if isinstance(data, dict) and "data" in data:
                return data["data"]
            elif isinstance(data, list):
                return data
            else:
                return []
                
        except Exception as e:
            logger.error(f"Failed to get ladder for grade {grade_id}: {e}")
            return []
    
    async def get_games(self, 
                       team_id: Optional[str] = None,
                       season_id: Optional[str] = None,
                       grade_id: Optional[str] = None,
                       status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get games with optional filters"""
        endpoint = "/games"
        params = {}
        
        if team_id:
            params["team"] = team_id
        if season_id:
            params["season"] = season_id
        if grade_id:
            params["grade"] = grade_id
        if status:
            params["status"] = status
        
        try:
            # Handle pagination
            all_games = []
            cursor = None
            
            while True:
                if cursor:
                    params["cursor"] = cursor
                
                response = await self._make_request("GET", endpoint, params=params)
                data = response.json()
                
                if isinstance(data, dict):
                    games = data.get("data", [])
                    all_games.extend(games)
                    
                    # Check for more pages
                    metadata = data.get("metadata", {})
                    if not metadata.get("hasMore", False):
                        break
                    cursor = metadata.get("cursor")
                else:
                    break
            
            return all_games
            
        except Exception as e:
            logger.error(f"Failed to get games: {e}")
            return []
    
    async def search_players(self, query: str, team_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search for players by name"""
        endpoint = "/players/search"
        params = {"q": query}
        
        if team_id:
            params["team"] = team_id
        
        try:
            response = await self._make_request("GET", endpoint, params=params)
            data = response.json()
            
            if isinstance(data, dict) and "data" in data:
                return data["data"]
            elif isinstance(data, list):
                return data
            else:
                return []
                
        except Exception as e:
            logger.error(f"Failed to search players: {e}")
            return []
    
    async def get_player_stats(self, player_id: str, season_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get player statistics"""
        endpoint = f"/players/{player_id}/stats"
        params = {}
        
        if season_id:
            params["season"] = season_id
        
        try:
            response = await self._make_request("GET", endpoint, params=params)
            data = response.json()
            
            return data if isinstance(data, dict) else None
            
        except Exception as e:
            logger.error(f"Failed to get player stats for {player_id}: {e}")
            return None

# Convenience functions for common operations
async def get_cscc_fixtures(team_id: str, season_id: str) -> List[Dict[str, Any]]:
    """Get Caroline Springs CC fixtures for a team"""
    async with PlayHQClient() as client:
        return await client.get_team_fixtures(team_id, season_id)

async def get_cscc_ladder(grade_id: str) -> List[Dict[str, Any]]:
    """Get Caroline Springs CC ladder for a grade"""
    async with PlayHQClient() as client:
        return await client.get_ladder(grade_id)

async def get_cscc_player_stats(player_name: str, team_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Get Caroline Springs CC player stats"""
    async with PlayHQClient() as client:
        # Search for player first
        players = await client.search_players(player_name, team_id)
        
        if not players:
            return None
        
        # Get stats for first match
        player = players[0]
        return await client.get_player_stats(player["id"])

async def get_cscc_recent_games(team_id: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Get recent games for Caroline Springs CC team"""
    async with PlayHQClient() as client:
        games = await client.get_games(team_id=team_id, status="completed")
        return games[:limit]

async def initialize_playhq_client() -> PlayHQClient:
    """Initialize and return a PlayHQ client instance"""
    return PlayHQClient()
