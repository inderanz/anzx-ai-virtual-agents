"""
Cricket Data Sync Job
Handles data synchronization from PlayHQ to vector store and GCS
"""

import asyncio
import hashlib
import json
import os
import tempfile
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging
from pathlib import Path

from app.config import get_settings, get_cscc_team_ids, get_cscc_org_id, get_cscc_season_id, get_cscc_grade_id
from agent.tools.playhq import PlayHQClient, initialize_playhq_client
from agent.tools.normalize import (
    CricketDataNormalizer, CricketSnippetGenerator,
    normalize_playhq_data, generate_snippet
)
from agent.tools.vector_client import get_vector_client
from models.fixture import Fixture, MatchStatus
from models.ladder import Ladder, LadderEntry
from models.team import Team, Player
from models.roster import Roster
from models.scorecard import Scorecard

# Try to import GCS client, fall back gracefully if not available
try:
    from google.cloud import storage
    GCS_AVAILABLE = True
except ImportError:
    GCS_AVAILABLE = False
    logger.warning("Google Cloud Storage not available, using local storage")

logger = logging.getLogger(__name__)

class GCSStorage:
    """GCS storage handler with local fallback"""
    
    def __init__(self, bucket_name: Optional[str] = None):
        self.bucket_name = bucket_name
        self.client = None
        self.bucket = None
        
        if bucket_name and GCS_AVAILABLE:
            try:
                self.client = storage.Client()
                self.bucket = self.client.bucket(bucket_name)
                logger.info(f"GCS storage initialized with bucket: {bucket_name}")
            except Exception as e:
                logger.warning(f"Failed to initialize GCS client: {e}")
                self.bucket_name = None
        else:
            logger.warning("GCS bucket not configured, using local storage")
    
    def write_json(self, path: str, data: Dict[str, Any]) -> str:
        """Write JSON data to storage (GCS or local)"""
        json_str = json.dumps(data, indent=2, default=str)
        
        if self.bucket:
            try:
                blob = self.bucket.blob(path)
                blob.upload_from_string(json_str, content_type='application/json')
                logger.info(f"Wrote JSON to GCS: {path}")
                return f"gs://{self.bucket_name}/{path}"
            except Exception as e:
                logger.error(f"Failed to write to GCS: {e}")
                # Fall back to local storage
                return self._write_local(path, json_str)
        else:
            return self._write_local(path, json_str)
    
    def _write_local(self, path: str, content: str) -> str:
        """Write to local storage as fallback"""
        local_path = Path("/tmp") / path
        local_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(local_path, 'w') as f:
            f.write(content)
        
        logger.info(f"Wrote JSON to local storage: {local_path}")
        return str(local_path)

class CricketDataSync:
    """Cricket data synchronization job"""
    
    def __init__(self):
        self.settings = get_settings()
        self.cscc_team_ids = get_cscc_team_ids()
        self.cscc_org_id = get_cscc_org_id()
        self.cscc_season_id = get_cscc_season_id()
        self.cscc_grade_id = get_cscc_grade_id()
        self.last_sync = None
        self.vector_client = get_vector_client()
        self.normalizer = CricketDataNormalizer()
        self.snippet_generator = CricketSnippetGenerator()
        self.storage = GCSStorage(self.settings.gcs_bucket)
        self.sync_stats = {
            "fixtures_updated": 0,
            "ladders_updated": 0,
            "teams_updated": 0,
            "scorecards_updated": 0,
            "rosters_updated": 0,
            "vector_upserts": 0,
            "gcs_writes": 0,
            "errors": 0
        }
    
    async def sync_all(self) -> Dict[str, Any]:
        """Sync all cricket data"""
        logger.info("Starting full cricket data sync")
        start_time = datetime.utcnow()
        
        try:
            # Reset stats
            self.sync_stats = {key: 0 for key in self.sync_stats}
            
            # Sync in order of dependency
            await self.sync_teams()
            await self.sync_fixtures()
            await self.sync_ladders()
            await self.sync_recent_scorecards()
            await self.sync_rosters()
            
            self.last_sync = datetime.utcnow()
            duration = (self.last_sync - start_time).total_seconds()
            
            # Check if there were any errors
            has_errors = self.sync_stats.get("errors", 0) > 0
            status = "error" if has_errors else "success"
            
            logger.info(f"Cricket data sync completed in {duration:.2f}s", extra={
                "duration_seconds": duration,
                "status": status,
                **self.sync_stats
            })
            
            return {
                "status": status,
                "duration_seconds": duration,
                "last_sync": self.last_sync.isoformat(),
                "stats": self.sync_stats
            }
            
        except Exception as e:
            logger.error(f"Cricket data sync failed: {e}")
            self.sync_stats["errors"] += 1
            
            return {
                "status": "error",
                "error": str(e),
                "stats": self.sync_stats
            }
    
    async def sync_teams(self) -> None:
        """Sync team data"""
        logger.info("Syncing team data")
        
        try:
            playhq_client = await initialize_playhq_client()
            
            # Get seasons
            seasons = await playhq_client.get_seasons(self.cscc_org_id)
            if not seasons:
                logger.warning("No seasons found")
                return
            
            # Get grades for current season
            grades = await playhq_client.get_grades(self.cscc_org_id, self.cscc_season_id)
            
            for grade in grades:
                teams = await playhq_client.get_teams(self.cscc_org_id, self.cscc_season_id, grade["id"])
                
                for team_data in teams:
                    if team_data["id"] in self.cscc_team_ids:
                        await self._process_team(team_data, grade, seasons[0])
            
            await playhq_client.close()
                                
        except Exception as e:
            logger.error(f"Failed to sync teams: {e}")
            self.sync_stats["errors"] += 1
    
    async def sync_fixtures(self) -> None:
        """Sync fixture data"""
        logger.info("Syncing fixture data")
        
        try:
            playhq_client = await initialize_playhq_client()
            
            for team_id in self.cscc_team_ids:
                # Get current season fixtures
                fixtures = await playhq_client.get_team_fixtures(team_id, self.cscc_season_id)
                
                for fixture_data in fixtures:
                    await self._process_fixture(fixture_data, team_id)
            
            await playhq_client.close()
                        
        except Exception as e:
            logger.error(f"Failed to sync fixtures: {e}")
            self.sync_stats["errors"] += 1
    
    async def sync_ladders(self) -> None:
        """Sync ladder data"""
        logger.info("Syncing ladder data")
        
        try:
            playhq_client = await initialize_playhq_client()
            
            # Get grades and their ladders
            grades = await playhq_client.get_grades(self.cscc_org_id, self.cscc_season_id)
            
            for grade in grades:
                ladder_data = await playhq_client.get_ladder(grade["id"])
                if ladder_data:
                    await self._process_ladder(ladder_data, grade)
            
            await playhq_client.close()
                        
        except Exception as e:
            logger.error(f"Failed to sync ladders: {e}")
            self.sync_stats["errors"] += 1
    
    async def sync_recent_scorecards(self) -> None:
        """Sync recent scorecard data"""
        logger.info("Syncing recent scorecard data")
        
        try:
            playhq_client = await initialize_playhq_client()
            
            # Get recent games
            recent_games = await playhq_client.get_games(
                status="completed",
                season_id=self.cscc_season_id
            )
            
            # Filter for CSCC teams and recent games
            cscc_games = [
                game for game in recent_games
                if any(team_id in [game.get("homeTeam", {}).get("id"), game.get("awayTeam", {}).get("id")]
                       for team_id in self.cscc_team_ids)
            ]
            
            # Get scorecards for recent games
            for game in cscc_games[:10]:  # Limit to 10 most recent
                scorecard = await playhq_client.get_game_summary(game["id"])
                if scorecard:
                    await self._process_scorecard(scorecard, game)
            
            await playhq_client.close()
                        
        except Exception as e:
            logger.error(f"Failed to sync scorecards: {e}")
            self.sync_stats["errors"] += 1
    
    async def sync_rosters(self) -> None:
        """Sync roster data"""
        logger.info("Syncing roster data")
        
        try:
            playhq_client = await initialize_playhq_client()
            
            for team_id in self.cscc_team_ids:
                # Get team roster
                roster_data = await playhq_client.get_team_roster(team_id)
                if roster_data:
                    await self._process_roster(roster_data, team_id)
            
            await playhq_client.close()
                        
        except Exception as e:
            logger.error(f"Failed to sync rosters: {e}")
            self.sync_stats["errors"] += 1
    
    async def _process_team(self, team_data: Dict[str, Any], grade: Dict[str, Any], season: Dict[str, Any]) -> None:
        """Process and store team data"""
        try:
            # Normalize team data
            normalized_team = self.normalizer.normalize_team(team_data, grade, season)
            
            # Generate snippet for embedding
            snippet = self.snippet_generator.generate_team_snippet(normalized_team)
            
            # Prepare document for vector store
            doc = {
                "id": f"team-{normalized_team.id}",
                "text": snippet,
                "metadata": {
                    "team_id": normalized_team.id,
                    "season_id": self.cscc_season_id,
                    "grade_id": grade.get("id"),
                    "type": "team",
                    "date": datetime.utcnow().isoformat()
                }
            }
            
            # Upsert to vector store
            self.vector_client.upsert([doc])
            self.sync_stats["vector_upserts"] += 1
            
            self.sync_stats["teams_updated"] += 1
            logger.debug(f"Processed team: {normalized_team.name}")
            
        except Exception as e:
            logger.error(f"Failed to process team {team_data.get('name', 'unknown')}: {e}")
            self.sync_stats["errors"] += 1
    
    async def _process_fixture(self, fixture_data: Dict[str, Any], team_id: str) -> None:
        """Process and store fixture data"""
        try:
            # Normalize fixture data
            normalized_fixture = self.normalizer.normalize_fixture(fixture_data, team_id)
            
            # Generate snippet for embedding
            snippet = self.snippet_generator.generate_fixture_snippet(normalized_fixture)
            
            # Prepare document for vector store
            doc = {
                "id": f"fixture-{normalized_fixture.id}",
                "text": snippet,
                "metadata": {
                    "team_id": team_id,
                    "season_id": self.cscc_season_id,
                    "grade_id": self.cscc_grade_id,
                    "type": "fixture",
                    "date": normalized_fixture.date.isoformat() if normalized_fixture.date else datetime.utcnow().isoformat()
                }
            }
            
            # Upsert to vector store
            self.vector_client.upsert([doc])
            self.sync_stats["vector_upserts"] += 1
            
            self.sync_stats["fixtures_updated"] += 1
            logger.debug(f"Processed fixture: {normalized_fixture.home_team} vs {normalized_fixture.away_team}")
            
        except Exception as e:
            logger.error(f"Failed to process fixture {fixture_data.get('id', 'unknown')}: {e}")
            self.sync_stats["errors"] += 1
    
    async def _process_ladder(self, ladder_data: List[Dict[str, Any]], grade: Dict[str, Any]) -> None:
        """Process and store ladder data"""
        try:
            # Normalize ladder data
            normalized_ladder = self.normalizer.normalize_ladder(ladder_data, grade, self.cscc_season_id)
            
            # Generate snippet for embedding
            snippet = self.snippet_generator.generate_ladder_snippet(normalized_ladder)
            
            # Prepare document for vector store
            doc = {
                "id": f"ladder-{grade['id']}",
                "text": snippet,
                "metadata": {
                    "team_id": None,  # Ladder applies to all teams in grade
                    "season_id": self.cscc_season_id,
                    "grade_id": grade["id"],
                    "type": "ladder",
                    "date": datetime.utcnow().isoformat()
                }
            }
            
            # Upsert to vector store
            self.vector_client.upsert([doc])
            self.sync_stats["vector_upserts"] += 1
            
            self.sync_stats["ladders_updated"] += 1
            logger.debug(f"Processed ladder: {normalized_ladder.grade_name}")
            
        except Exception as e:
            logger.error(f"Failed to process ladder for grade {grade.get('name', 'unknown')}: {e}")
            self.sync_stats["errors"] += 1
    
    async def _process_scorecard(self, scorecard_data: Dict[str, Any], game_data: Dict[str, Any]) -> None:
        """Process and store scorecard data"""
        try:
            # Normalize scorecard data
            normalized_scorecard = self.normalizer.normalize_scorecard(scorecard_data, game_data)
            
            # Generate snippet for embedding
            snippet = self.snippet_generator.generate_scorecard_snippet(normalized_scorecard)
            
            # Prepare document for vector store
            doc = {
                "id": f"scorecard-{normalized_scorecard.id}",
                "text": snippet,
                "metadata": {
                    "team_id": None,  # Scorecard applies to both teams
                    "season_id": self.cscc_season_id,
                    "grade_id": self.cscc_grade_id,
                    "type": "scorecard",
                    "date": normalized_scorecard.date.isoformat() if normalized_scorecard.date else datetime.utcnow().isoformat()
                }
            }
            
            # Upsert to vector store
            self.vector_client.upsert([doc])
            self.sync_stats["vector_upserts"] += 1
            
            self.sync_stats["scorecards_updated"] += 1
            logger.debug(f"Processed scorecard: {normalized_scorecard.id}")
            
        except Exception as e:
            logger.error(f"Failed to process scorecard {game_data.get('id', 'unknown')}: {e}")
            self.sync_stats["errors"] += 1
    
    async def _process_roster(self, roster_data: Dict[str, Any], team_id: str) -> None:
        """Process and store roster data"""
        try:
            # Normalize roster data
            normalized_roster = self.normalizer.normalize_roster(roster_data, team_id)
            
            # Generate snippet for embedding
            snippet = self.snippet_generator.generate_roster_snippet(normalized_roster)
            
            # Prepare document for vector store
            doc = {
                "id": f"roster-{team_id}",
                "text": snippet,
                "metadata": {
                    "team_id": team_id,
                    "season_id": self.cscc_season_id,
                    "grade_id": self.cscc_grade_id,
                    "type": "roster",
                    "date": datetime.utcnow().isoformat()
                }
            }
            
            # Upsert to vector store
            self.vector_client.upsert([doc])
            self.sync_stats["vector_upserts"] += 1
            
            self.sync_stats["rosters_updated"] += 1
            logger.debug(f"Processed roster: {team_id}")
            
        except Exception as e:
            logger.error(f"Failed to process roster {team_id}: {e}")
            self.sync_stats["errors"] += 1
    
    def get_sync_status(self) -> Dict[str, Any]:
        """Get current sync status"""
        return {
            "last_sync": self.last_sync.isoformat() if self.last_sync else None,
            "stats": self.sync_stats,
            "cscc_team_ids": self.cscc_team_ids,
            "vector_stats": self.vector_client.get_stats(),
            "settings": {
                "org_id": self.cscc_org_id,
                "season_id": self.cscc_season_id,
                "grade_id": self.cscc_grade_id,
                "playhq_mode": self.settings.playhq_mode,
                "vector_backend": self.settings.vector_backend
            }
        }

# Global sync instance
_sync_instance: Optional[CricketDataSync] = None

def get_sync_instance() -> CricketDataSync:
    """Get the global sync instance"""
    global _sync_instance
    if _sync_instance is None:
        _sync_instance = CricketDataSync()
    return _sync_instance

async def run_sync_job(scope: str = "all", target_id: Optional[str] = None) -> Dict[str, Any]:
    """Run sync job with specified scope"""
    sync = get_sync_instance()
    
    if scope == "all":
        return await sync.sync_all()
    elif scope == "team" and target_id:
        # TODO: Implement team-specific sync
        return {"status": "not_implemented", "message": "Team-specific sync not implemented"}
    elif scope == "match" and target_id:
        # TODO: Implement match-specific sync
        return {"status": "not_implemented", "message": "Match-specific sync not implemented"}
    elif scope == "ladder" and target_id:
        # TODO: Implement ladder-specific sync
        return {"status": "not_implemented", "message": "Ladder-specific sync not implemented"}
    else:
        return {"status": "error", "message": f"Invalid scope: {scope}"}

# New entrypoint functions for Task 6
async def run_full_refresh() -> Dict[str, Any]:
    """Run full refresh for all configured teams"""
    try:
        sync = CricketDataSync()
        return await sync.sync_all()
    except Exception as e:
        logger.error(f"Full refresh failed: {e}")
        return {
            "status": "error",
            "error": str(e)
        }

async def run_team_refresh(team_id: str) -> Dict[str, Any]:
    """Run refresh for a specific team"""
    sync = CricketDataSync()
    
    if team_id not in sync.cscc_team_ids:
        return {"status": "error", "message": f"Team {team_id} not in configured teams"}
    
    logger.info(f"Starting team refresh for {team_id}")
    start_time = datetime.utcnow()
    
    try:
        # Reset stats for this team
        sync.sync_stats = {key: 0 for key in sync.sync_stats}
        
        # Sync team-specific data
        await sync.sync_teams()
        await sync.sync_fixtures()
        await sync.sync_rosters()
        
        # Get recent scorecards for this team
        await sync.sync_recent_scorecards()
        
        duration = (datetime.utcnow() - start_time).total_seconds()
        
        logger.info(f"Team refresh completed for {team_id} in {duration:.2f}s", extra={
            "team_id": team_id,
            "duration_seconds": duration,
            **sync.sync_stats
        })
        
        return {
            "status": "success",
            "team_id": team_id,
            "duration_seconds": duration,
            "stats": sync.sync_stats
        }
        
    except Exception as e:
        logger.error(f"Team refresh failed for {team_id}: {e}")
        return {
            "status": "error",
            "team_id": team_id,
            "error": str(e)
        }

async def run_match_refresh(match_id: str) -> Dict[str, Any]:
    """Run refresh for a specific match"""
    sync = CricketDataSync()
    
    logger.info(f"Starting match refresh for {match_id}")
    start_time = datetime.utcnow()
    
    try:
        # Reset stats for this match
        sync.sync_stats = {key: 0 for key in sync.sync_stats}
        
        # Get match summary
        playhq_client = await initialize_playhq_client()
        match_summary = await playhq_client.get_game_summary(match_id)
        await playhq_client.close()
        
        if match_summary:
            # Process the match summary
            await sync._process_scorecard(match_summary, {"id": match_id})
            
            # Write to GCS
            team_slug = "unknown-team"  # Could be extracted from match data
            date_path = datetime.utcnow().strftime("%Y/%m/%d")
            gcs_path = f"cricket/{team_slug}/{date_path}/match_{match_id}.json"
            
            sync.storage.write_json(gcs_path, match_summary)
            sync.sync_stats["gcs_writes"] += 1
        
        duration = (datetime.utcnow() - start_time).total_seconds()
        
        logger.info(f"Match refresh completed for {match_id} in {duration:.2f}s", extra={
            "match_id": match_id,
            "duration_seconds": duration,
            **sync.sync_stats
        })
        
        return {
            "status": "success",
            "match_id": match_id,
            "duration_seconds": duration,
            "stats": sync.sync_stats
        }
        
    except Exception as e:
        logger.error(f"Match refresh failed for {match_id}: {e}")
        return {
            "status": "error",
            "match_id": match_id,
            "error": str(e)
        }

async def run_ladder_refresh(grade_id: str) -> Dict[str, Any]:
    """Run refresh for a specific grade ladder"""
    sync = CricketDataSync()
    
    logger.info(f"Starting ladder refresh for grade {grade_id}")
    start_time = datetime.utcnow()
    
    try:
        # Reset stats for this ladder
        sync.sync_stats = {key: 0 for key in sync.sync_stats}
        
        # Get ladder data
        playhq_client = await initialize_playhq_client()
        ladder_data = await playhq_client.get_ladder(grade_id)
        await playhq_client.close()
        
        if ladder_data:
            # Process the ladder
            grade_info = {"id": grade_id, "name": f"Grade {grade_id}"}
            await sync._process_ladder(ladder_data, grade_info)
            
            # Write to GCS
            date_path = datetime.utcnow().strftime("%Y/%m/%d")
            gcs_path = f"cricket/ladders/{date_path}/grade_{grade_id}.json"
            
            sync.storage.write_json(gcs_path, ladder_data)
            sync.sync_stats["gcs_writes"] += 1
        
        duration = (datetime.utcnow() - start_time).total_seconds()
        
        logger.info(f"Ladder refresh completed for grade {grade_id} in {duration:.2f}s", extra={
            "grade_id": grade_id,
            "duration_seconds": duration,
            **sync.sync_stats
        })
        
        return {
            "status": "success",
            "grade_id": grade_id,
            "duration_seconds": duration,
            "stats": sync.sync_stats
        }
        
    except Exception as e:
        logger.error(f"Ladder refresh failed for grade {grade_id}: {e}")
        return {
            "status": "error",
            "grade_id": grade_id,
            "error": str(e)
        }

# CLI handler for direct execution
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        scope = sys.argv[1]
        if scope == "team" and len(sys.argv) > 2:
            team_id = sys.argv[2]
            result = asyncio.run(run_team_refresh(team_id))
        elif scope == "match" and len(sys.argv) > 2:
            match_id = sys.argv[2]
            result = asyncio.run(run_match_refresh(match_id))
        elif scope == "ladder" and len(sys.argv) > 2:
            grade_id = sys.argv[2]
            result = asyncio.run(run_ladder_refresh(grade_id))
        else:
            result = {"status": "error", "message": "Invalid arguments"}
    else:
        result = asyncio.run(run_full_refresh())
    
    print(json.dumps(result, indent=2))
