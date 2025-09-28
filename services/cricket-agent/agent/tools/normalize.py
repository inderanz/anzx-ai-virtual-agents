"""
Cricket Data Normalization
Converts raw PlayHQ JSON to normalized Pydantic models
Implements snippet generators and metadata attachment
"""

import hashlib
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import logging

from models.team import Team, Player
from models.fixture import Fixture, MatchStatus
from models.scorecard import Scorecard, TeamScorecard, BattingStats, BowlingStats
from models.ladder import Ladder, LadderEntry
from models.roster import Roster

logger = logging.getLogger(__name__)

class CricketDataNormalizer:
    """Normalizes raw PlayHQ data to structured models"""
    
    def __init__(self):
        self.normalization_stats = {
            "teams_processed": 0,
            "fixtures_processed": 0,
            "scorecards_processed": 0,
            "ladders_processed": 0,
            "rosters_processed": 0,
            "errors": 0
        }
    
    def normalize_team(self, raw_data: Dict[str, Any], grade: Dict[str, Any], season: Dict[str, Any]) -> Optional[Team]:
        """Normalize team data from PlayHQ"""
        try:
            # Extract team information
            team_id = raw_data.get("id", "")
            team_name = raw_data.get("name", "Unknown Team")
            
            # Create team model
            team = Team(
                id=team_id,
                name=team_name,
                grade=grade.get("name"),
                season=season.get("name")
            )
            
            # Add metadata
            team.created_at = datetime.utcnow()
            team.updated_at = datetime.utcnow()
            
            self.normalization_stats["teams_processed"] += 1
            logger.debug(f"Normalized team: {team.name}")
            
            return team
            
        except Exception as e:
            logger.error(f"Failed to normalize team: {e}")
            self.normalization_stats["errors"] += 1
            return None
    
    def normalize_fixture(self, raw_data: Dict[str, Any], team_id: str) -> Optional[Fixture]:
        """Normalize fixture data from PlayHQ"""
        try:
            # Extract fixture information
            fixture_id = raw_data.get("id", "")
            home_team_data = raw_data.get("homeTeam", {})
            away_team_data = raw_data.get("awayTeam", {})
            
            # Parse date
            date_str = raw_data.get("date", "")
            try:
                fixture_date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            except (ValueError, TypeError):
                fixture_date = datetime.utcnow()
            
            # Determine match status
            status_str = raw_data.get("status", "scheduled")
            try:
                status = MatchStatus(status_str)
            except ValueError:
                status = MatchStatus.SCHEDULED
            
            # Create fixture model
            fixture = Fixture(
                id=fixture_id,
                home_team=home_team_data.get("name", "Unknown"),
                away_team=away_team_data.get("name", "Unknown"),
                home_team_id=home_team_data.get("id", ""),
                away_team_id=away_team_data.get("id", ""),
                date=fixture_date,
                venue=raw_data.get("venue"),
                grade=raw_data.get("grade"),
                status=status
            )
            
            # Add metadata
            fixture.created_at = datetime.utcnow()
            fixture.updated_at = datetime.utcnow()
            
            self.normalization_stats["fixtures_processed"] += 1
            logger.debug(f"Normalized fixture: {fixture.home_team} vs {fixture.away_team}")
            
            return fixture
            
        except Exception as e:
            logger.error(f"Failed to normalize fixture: {e}")
            self.normalization_stats["errors"] += 1
            return None
    
    def normalize_scorecard(self, raw_data: Dict[str, Any], game_data: Dict[str, Any]) -> Optional[Scorecard]:
        """Normalize scorecard data from PlayHQ"""
        try:
            # Extract game information
            game_id = raw_data.get("id", "")
            home_team_data = raw_data.get("homeTeam", {})
            away_team_data = raw_data.get("awayTeam", {})
            
            # Parse date
            date_str = raw_data.get("date", "")
            try:
                game_date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            except (ValueError, TypeError):
                game_date = datetime.utcnow()
            
            # Create team scorecards
            home_scorecard = TeamScorecard(
                team_id=home_team_data.get("id", ""),
                team_name=home_team_data.get("name", "Unknown"),
                total_runs=home_team_data.get("score", 0),
                wickets=home_team_data.get("wickets", 0),
                overs=home_team_data.get("overs", 0.0),
                extras=home_team_data.get("extras", 0)
            )
            
            away_scorecard = TeamScorecard(
                team_id=away_team_data.get("id", ""),
                team_name=away_team_data.get("name", "Unknown"),
                total_runs=away_team_data.get("score", 0),
                wickets=away_team_data.get("wickets", 0),
                overs=away_team_data.get("overs", 0.0),
                extras=away_team_data.get("extras", 0)
            )
            
            # Create scorecard model
            scorecard = Scorecard(
                id=game_id,
                match_id=game_id,
                home_team=home_scorecard,
                away_team=away_scorecard,
                date=game_date,
                venue=raw_data.get("venue"),
                result=raw_data.get("result")
            )
            
            # Add metadata
            scorecard.created_at = datetime.utcnow()
            scorecard.updated_at = datetime.utcnow()
            
            self.normalization_stats["scorecards_processed"] += 1
            logger.debug(f"Normalized scorecard: {scorecard.home_team.team_name} vs {scorecard.away_team.team_name}")
            
            return scorecard
            
        except Exception as e:
            logger.error(f"Failed to normalize scorecard: {e}")
            self.normalization_stats["errors"] += 1
            return None
    
    def normalize_ladder(self, raw_data: List[Dict[str, Any]], grade: Dict[str, Any]) -> Optional[Ladder]:
        """Normalize ladder data from PlayHQ"""
        try:
            # Create ladder entries
            entries = []
            for entry_data in raw_data:
                team_data = entry_data.get("team", {})
                
                entry = LadderEntry(
                    position=entry_data.get("position", 0),
                    team_id=team_data.get("id", ""),
                    team_name=team_data.get("name", "Unknown"),
                    matches_played=entry_data.get("matchesPlayed", 0),
                    matches_won=entry_data.get("matchesWon", 0),
                    matches_lost=entry_data.get("matchesLost", 0),
                    matches_drawn=entry_data.get("matchesDrawn", 0),
                    matches_tied=entry_data.get("matchesTied", 0),
                    points=entry_data.get("points", 0),
                    percentage=entry_data.get("percentage")
                )
                entries.append(entry)
            
            # Create ladder model
            ladder = Ladder(
                id=f"ladder-{grade.get('id', 'unknown')}",
                grade_id=grade.get("id", ""),
                grade_name=grade.get("name", "Unknown Grade"),
                entries=entries
            )
            
            # Add metadata
            ladder.last_updated = datetime.utcnow()
            ladder.created_at = datetime.utcnow()
            
            self.normalization_stats["ladders_processed"] += 1
            logger.debug(f"Normalized ladder: {ladder.grade_name} with {len(entries)} entries")
            
            return ladder
            
        except Exception as e:
            logger.error(f"Failed to normalize ladder: {e}")
            self.normalization_stats["errors"] += 1
            return None
    
    def normalize_roster(self, raw_data: Dict[str, Any], team_id: str) -> Optional[Roster]:
        """Normalize roster data from PlayHQ"""
        try:
            # Extract team information
            team_name = raw_data.get("name", "Unknown Team")
            players_data = raw_data.get("players", [])
            
            # Create player models
            players = []
            for player_data in players_data:
                player = Player(
                    id=player_data.get("id", ""),
                    name=player_data.get("name", "Unknown Player"),
                    position=player_data.get("position"),
                    jersey_number=player_data.get("jerseyNumber"),
                    is_captain=player_data.get("isCaptain", False),
                    is_vice_captain=player_data.get("isViceCaptain", False),
                    is_wicket_keeper=player_data.get("isWicketKeeper", False),
                    age=player_data.get("age"),
                    batting_style=player_data.get("battingStyle"),
                    bowling_style=player_data.get("bowlingStyle")
                )
                players.append(player)
            
            # Create roster model
            roster = Roster(
                team_id=team_id,
                team_name=team_name,
                players=players
            )
            
            # Add metadata
            roster.created_at = datetime.utcnow()
            roster.updated_at = datetime.utcnow()
            
            self.normalization_stats["rosters_processed"] += 1
            logger.debug(f"Normalized roster: {roster.team_name} with {len(players)} players")
            
            return roster
            
        except Exception as e:
            logger.error(f"Failed to normalize roster: {e}")
            self.normalization_stats["errors"] += 1
            return None

class CricketSnippetGenerator:
    """Generates text snippets for embeddings and display"""
    
    @staticmethod
    def generate_fixture_snippet(fixture: Fixture) -> str:
        """Generate fixture snippet for embeddings"""
        lines = [
            f"Fixture: {fixture.home_team} vs {fixture.away_team}",
            f"Date: {fixture.date.strftime('%Y-%m-%d %H:%M')}",
            f"Status: {fixture.status.value}"
        ]
        
        if fixture.venue:
            lines.append(f"Venue: {fixture.venue}")
        
        if fixture.grade:
            lines.append(f"Grade: {fixture.grade}")
        
        if fixture.status.value == "completed" and fixture.result:
            lines.append(f"Result: {fixture.result}")
        
        return "\n".join(lines)
    
    @staticmethod
    def generate_batting_summary(scorecard: Scorecard) -> str:
        """Generate batting summary snippet"""
        lines = ["Batting Summary:"]
        
        # Home team batting
        if scorecard.home_team.batting:
            lines.append(f"{scorecard.home_team.team_name}:")
            for batting in scorecard.home_team.batting[:5]:  # Top 5 batsmen
                lines.append(f"  {batting.player_name}: {batting.runs} runs ({batting.balls} balls)")
        
        # Away team batting
        if scorecard.away_team.batting:
            lines.append(f"{scorecard.away_team.team_name}:")
            for batting in scorecard.away_team.batting[:5]:  # Top 5 batsmen
                lines.append(f"  {batting.player_name}: {batting.runs} runs ({batting.balls} balls)")
        
        return "\n".join(lines)
    
    @staticmethod
    def generate_ladder_entry(ladder: Ladder, team_id: str) -> str:
        """Generate ladder entry snippet for specific team"""
        entry = ladder.get_team_position(team_id)
        if not entry:
            return f"Team not found in {ladder.grade_name} ladder"
        
        lines = [
            f"Ladder Position: {entry.position}",
            f"Team: {entry.team_name}",
            f"Points: {entry.points}",
            f"Matches: {entry.matches_played} played, {entry.matches_won} won, {entry.matches_lost} lost"
        ]
        
        if entry.percentage:
            lines.append(f"Percentage: {entry.percentage:.1f}%")
        
        return "\n".join(lines)
    
    @staticmethod
    def generate_roster_snippet(roster: Roster) -> str:
        """Generate roster snippet"""
        lines = [
            f"Team: {roster.team_name}",
            f"Players: {len(roster.players)}"
        ]
        
        # Add captain and vice captain
        captain = roster.get_captain()
        if captain:
            lines.append(f"Captain: {captain.name}")
        
        vice_captain = roster.get_vice_captain()
        if vice_captain:
            lines.append(f"Vice Captain: {vice_captain.name}")
        
        # Add wicket keepers
        wicket_keepers = roster.get_wicket_keepers()
        if wicket_keepers:
            wk_names = [wk.name for wk in wicket_keepers]
            lines.append(f"Wicket Keepers: {', '.join(wk_names)}")
        
        return "\n".join(lines)
    
    @staticmethod
    def generate_team_snippet(team: Team) -> str:
        """Generate team snippet for embeddings"""
        lines = [
            f"Team: {team.name}",
            f"Grade: {team.grade}",
            f"Season: {team.season}"
        ]
        
        if team.players:
            lines.append(f"Players: {len(team.players)}")
            # Add captain if available
            captain = next((p for p in team.players if p.is_captain), None)
            if captain:
                lines.append(f"Captain: {captain.name}")
        
        return "\n".join(lines)
    
    @staticmethod
    def generate_ladder_snippet(ladder: Ladder) -> str:
        """Generate ladder snippet for embeddings"""
        lines = [
            f"Ladder: {ladder.grade_name}",
            f"Season: {ladder.season}",
            f"Teams: {len(ladder.entries)}"
        ]
        
        # Add top 3 teams
        top_teams = ladder.entries[:3]
        for i, entry in enumerate(top_teams, 1):
            lines.append(f"{i}. {entry.team_name} - {entry.points} points")
        
        return "\n".join(lines)
    
    @staticmethod
    def generate_scorecard_snippet(scorecard: Scorecard) -> str:
        """Generate scorecard snippet for embeddings"""
        lines = [
            f"Match: {scorecard.home_team.team_name} vs {scorecard.away_team.team_name}",
            f"Date: {scorecard.date.strftime('%Y-%m-%d')}",
            f"Status: {scorecard.status.value}"
        ]
        
        if scorecard.result:
            lines.append(f"Result: {scorecard.result}")
        
        # Add scores if available
        if scorecard.home_team.total_runs is not None:
            lines.append(f"{scorecard.home_team.team_name}: {scorecard.home_team.total_runs}/{scorecard.home_team.total_wickets}")
        
        if scorecard.away_team.total_runs is not None:
            lines.append(f"{scorecard.away_team.team_name}: {scorecard.away_team.total_runs}/{scorecard.away_team.total_wickets}")
        
        return "\n".join(lines)

class CricketMetadataAttacher:
    """Attaches metadata to normalized models"""
    
    @staticmethod
    def attach_team_metadata(team: Team, team_id: str, season_id: str, grade_id: str) -> Team:
        """Attach metadata to team model"""
        # Add metadata attributes
        team.team_id = team_id
        team.season_id = season_id
        team.grade_id = grade_id
        team.type = "team"
        
        return team
    
    @staticmethod
    def attach_fixture_metadata(fixture: Fixture, team_id: str, season_id: str, grade_id: str) -> Fixture:
        """Attach metadata to fixture model"""
        # Add metadata attributes
        fixture.team_id = team_id
        fixture.season_id = season_id
        fixture.grade_id = grade_id
        fixture.type = "fixture"
        
        return fixture
    
    @staticmethod
    def attach_scorecard_metadata(scorecard: Scorecard, team_id: str, season_id: str, grade_id: str) -> Scorecard:
        """Attach metadata to scorecard model"""
        # Add metadata attributes
        scorecard.team_id = team_id
        scorecard.season_id = season_id
        scorecard.grade_id = grade_id
        scorecard.type = "scorecard"
        
        return scorecard
    
    @staticmethod
    def attach_ladder_metadata(ladder: Ladder, team_id: str, season_id: str, grade_id: str) -> Ladder:
        """Attach metadata to ladder model"""
        # Add metadata attributes
        ladder.team_id = team_id
        ladder.season_id = season_id
        ladder.grade_id = grade_id
        ladder.type = "ladder"
        
        return ladder
    
    @staticmethod
    def attach_roster_metadata(roster: Roster, team_id: str, season_id: str, grade_id: str) -> Roster:
        """Attach metadata to roster model"""
        # Add metadata attributes
        roster.team_id = team_id
        roster.season_id = season_id
        roster.grade_id = grade_id
        roster.type = "roster"
        
        return roster

class CricketTextChunker:
    """Chunks text for embeddings (max 1000 tokens)"""
    
    @staticmethod
    def chunk_text(text: str, max_tokens: int = 1000) -> List[str]:
        """Split text into chunks for embeddings"""
        # Simple token estimation (4 chars per token)
        max_chars = max_tokens * 4
        
        if len(text) <= max_chars:
            return [text]
        
        chunks = []
        current_chunk = ""
        
        for line in text.split('\n'):
            if len(current_chunk) + len(line) + 1 <= max_chars:
                current_chunk += line + '\n'
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = line + '\n'
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    @staticmethod
    def generate_embedding_text(model: Any, metadata: Dict[str, Any]) -> str:
        """Generate text for embedding with metadata"""
        lines = []
        
        # Add type-specific content
        if hasattr(model, 'to_text_summary'):
            lines.append(model.to_text_summary())
        
        # Add metadata
        if metadata.get("team_id"):
            lines.append(f"Team ID: {metadata['team_id']}")
        if metadata.get("season_id"):
            lines.append(f"Season: {metadata['season_id']}")
        if metadata.get("grade_id"):
            lines.append(f"Grade: {metadata['grade_id']}")
        if metadata.get("type"):
            lines.append(f"Type: {metadata['type']}")
        
        return "\n".join(lines)

# Convenience functions
def normalize_playhq_data(data_type: str, raw_data: Dict[str, Any], **kwargs) -> Optional[Any]:
    """Normalize PlayHQ data by type"""
    normalizer = CricketDataNormalizer()
    
    if data_type == "team":
        return normalizer.normalize_team(raw_data, kwargs.get("grade", {}), kwargs.get("season", {}))
    elif data_type == "fixture":
        return normalizer.normalize_fixture(raw_data, kwargs.get("team_id", ""))
    elif data_type == "scorecard":
        return normalizer.normalize_scorecard(raw_data, kwargs.get("game_data", {}))
    elif data_type == "ladder":
        return normalizer.normalize_ladder(raw_data, kwargs.get("grade", {}))
    elif data_type == "roster":
        return normalizer.normalize_roster(raw_data, kwargs.get("team_id", ""))
    else:
        logger.error(f"Unknown data type: {data_type}")
        return None

def generate_snippet(model: Any, snippet_type: str) -> str:
    """Generate snippet by type"""
    generator = CricketSnippetGenerator()
    
    if snippet_type == "fixture":
        return generator.generate_fixture_snippet(model)
    elif snippet_type == "batting":
        return generator.generate_batting_summary(model)
    elif snippet_type == "ladder":
        return generator.generate_ladder_entry(model, model.team_id)
    elif snippet_type == "roster":
        return generator.generate_roster_snippet(model)
    else:
        return model.to_text_summary() if hasattr(model, 'to_text_summary') else str(model)
