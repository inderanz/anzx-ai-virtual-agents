"""
Unit tests for Cricket Data Normalization
Tests normalization, snippet generation, and metadata attachment
"""

import pytest
from datetime import datetime
from typing import Dict, Any

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from agent.tools.normalize import (
    CricketDataNormalizer,
    CricketSnippetGenerator,
    CricketMetadataAttacher,
    CricketTextChunker,
    normalize_playhq_data,
    generate_snippet
)
from models.team import Team, Player
from models.fixture import Fixture, MatchStatus
from models.scorecard import Scorecard, TeamScorecard, BattingStats, BowlingStats
from models.ladder import Ladder, LadderEntry
from models.roster import Roster

# Mock data for testing
MOCK_TEAM_DATA = {
    "id": "team-123",
    "name": "Caroline Springs Blue U10",
    "grade": "Under 10s",
    "season": "2025/26"
}

MOCK_GRADE_DATA = {
    "id": "grade-456",
    "name": "Under 10s",
    "type": "junior"
}

MOCK_SEASON_DATA = {
    "id": "season-789",
    "name": "2025/26 Season",
    "status": "active"
}

MOCK_FIXTURE_DATA = {
    "id": "fixture-101",
    "homeTeam": {
        "id": "team-123",
        "name": "Caroline Springs Blue U10"
    },
    "awayTeam": {
        "id": "team-456",
        "name": "Opponent Team"
    },
    "date": "2025-10-15T10:00:00Z",
    "venue": "Caroline Springs Oval",
    "status": "scheduled",
    "grade": "Under 10s"
}

MOCK_SCORECARD_DATA = {
    "id": "game-201",
    "homeTeam": {
        "id": "team-123",
        "name": "Caroline Springs Blue U10",
        "score": 120,
        "wickets": 8
    },
    "awayTeam": {
        "id": "team-456",
        "name": "Opponent Team",
        "score": 95,
        "wickets": 10
    },
    "date": "2025-10-15T10:00:00Z",
    "venue": "Caroline Springs Oval",
    "result": "Caroline Springs Blue U10 won by 25 runs"
}

MOCK_LADDER_DATA = [
    {
        "position": 1,
        "team": {
            "id": "team-123",
            "name": "Caroline Springs Blue U10"
        },
        "matchesPlayed": 5,
        "matchesWon": 4,
        "matchesLost": 1,
        "points": 16,
        "percentage": 80.0
    },
    {
        "position": 2,
        "team": {
            "id": "team-456",
            "name": "Opponent Team"
        },
        "matchesPlayed": 5,
        "matchesWon": 3,
        "matchesLost": 2,
        "points": 12,
        "percentage": 60.0
    }
]

MOCK_ROSTER_DATA = {
    "id": "team-123",
    "name": "Caroline Springs Blue U10",
    "players": [
        {
            "id": "player-001",
            "name": "Harshvardhan",
            "position": "Batsman",
            "jerseyNumber": 7,
            "isCaptain": True,
            "battingStyle": "RHB",
            "bowlingStyle": "Right-arm medium"
        },
        {
            "id": "player-002",
            "name": "Alex Smith",
            "position": "Bowler",
            "jerseyNumber": 12,
            "isViceCaptain": True,
            "battingStyle": "LHB",
            "bowlingStyle": "Left-arm spin"
        }
    ]
}

class TestCricketDataNormalizer:
    """Test cricket data normalization"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.normalizer = CricketDataNormalizer()
    
    def test_normalize_team_success(self):
        """Test successful team normalization"""
        team = self.normalizer.normalize_team(
            MOCK_TEAM_DATA, 
            MOCK_GRADE_DATA, 
            MOCK_SEASON_DATA
        )
        
        assert team is not None
        assert team.id == "team-123"
        assert team.name == "Caroline Springs Blue U10"
        assert team.grade == "Under 10s"
        assert team.season == "2025/26 Season"
        assert self.normalizer.normalization_stats["teams_processed"] == 1
    
    def test_normalize_team_missing_data(self):
        """Test team normalization with missing data"""
        incomplete_data = {"id": "team-123"}
        team = self.normalizer.normalize_team(
            incomplete_data, 
            MOCK_GRADE_DATA, 
            MOCK_SEASON_DATA
        )
        
        assert team is not None
        assert team.name == "Unknown Team"
        assert team.grade == "Under 10s"
    
    def test_normalize_fixture_success(self):
        """Test successful fixture normalization"""
        fixture = self.normalizer.normalize_fixture(MOCK_FIXTURE_DATA, "team-123")
        
        assert fixture is not None
        assert fixture.id == "fixture-101"
        assert fixture.home_team == "Caroline Springs Blue U10"
        assert fixture.away_team == "Opponent Team"
        assert fixture.status == MatchStatus.SCHEDULED
        assert fixture.venue == "Caroline Springs Oval"
        assert self.normalizer.normalization_stats["fixtures_processed"] == 1
    
    def test_normalize_fixture_invalid_date(self):
        """Test fixture normalization with invalid date"""
        invalid_data = MOCK_FIXTURE_DATA.copy()
        invalid_data["date"] = "invalid-date"
        
        fixture = self.normalizer.normalize_fixture(invalid_data, "team-123")
        
        assert fixture is not None
        assert fixture.date is not None  # Should fallback to current time
    
    def test_normalize_scorecard_success(self):
        """Test successful scorecard normalization"""
        scorecard = self.normalizer.normalize_scorecard(MOCK_SCORECARD_DATA, MOCK_SCORECARD_DATA)
        
        assert scorecard is not None
        assert scorecard.id == "game-201"
        assert scorecard.home_team.team_name == "Caroline Springs Blue U10"
        assert scorecard.away_team.team_name == "Opponent Team"
        assert scorecard.home_team.total_runs == 120
        assert scorecard.away_team.total_runs == 95
        assert self.normalizer.normalization_stats["scorecards_processed"] == 1
    
    def test_normalize_ladder_success(self):
        """Test successful ladder normalization"""
        ladder = self.normalizer.normalize_ladder(MOCK_LADDER_DATA, MOCK_GRADE_DATA)
        
        assert ladder is not None
        assert ladder.grade_id == "grade-456"
        assert ladder.grade_name == "Under 10s"
        assert len(ladder.entries) == 2
        
        # Check first entry
        first_entry = ladder.entries[0]
        assert first_entry.position == 1
        assert first_entry.team_name == "Caroline Springs Blue U10"
        assert first_entry.points == 16
        assert first_entry.percentage == 80.0
        
        assert self.normalizer.normalization_stats["ladders_processed"] == 1
    
    def test_normalize_roster_success(self):
        """Test successful roster normalization"""
        roster = self.normalizer.normalize_roster(MOCK_ROSTER_DATA, "team-123")
        
        assert roster is not None
        assert roster.team_id == "team-123"
        assert roster.team_name == "Caroline Springs Blue U10"
        assert len(roster.players) == 2
        
        # Check first player
        first_player = roster.players[0]
        assert first_player.name == "Harshvardhan"
        assert first_player.is_captain == True
        assert first_player.jersey_number == 7
        
        # Check second player
        second_player = roster.players[1]
        assert second_player.name == "Alex Smith"
        assert second_player.is_vice_captain == True
        
        assert self.normalizer.normalization_stats["rosters_processed"] == 1
    
    def test_normalize_error_handling(self):
        """Test error handling in normalization"""
        # Test with completely invalid data
        invalid_data = None
        result = self.normalizer.normalize_team(invalid_data, {}, {})
        
        assert result is None
        assert self.normalizer.normalization_stats["errors"] == 1

class TestCricketSnippetGenerator:
    """Test snippet generation"""
    
    def test_generate_fixture_snippet(self):
        """Test fixture snippet generation"""
        fixture = Fixture(
            id="fixture-101",
            home_team="Caroline Springs Blue U10",
            away_team="Opponent Team",
            home_team_id="team-123",
            away_team_id="team-456",
            date=datetime(2025, 10, 15, 10, 0),
            venue="Caroline Springs Oval",
            status=MatchStatus.SCHEDULED
        )
        
        snippet = CricketSnippetGenerator.generate_fixture_snippet(fixture)
        
        assert "Fixture: Caroline Springs Blue U10 vs Opponent Team" in snippet
        assert "Date: 2025-10-15 10:00" in snippet
        assert "Status: scheduled" in snippet
        assert "Venue: Caroline Springs Oval" in snippet
    
    def test_generate_batting_summary(self):
        """Test batting summary generation"""
        # Create scorecard with batting stats
        home_team = TeamScorecard(
            team_id="team-123",
            team_name="Caroline Springs Blue U10",
            total_runs=120,
            wickets=8,
            overs=20.0,
            batting=[
                BattingStats(
                    player_id="player-001",
                    player_name="Harshvardhan",
                    runs=45,
                    balls=30,
                    fours=6,
                    sixes=1
                )
            ]
        )
        
        away_team = TeamScorecard(
            team_id="team-456",
            team_name="Opponent Team",
            total_runs=95,
            wickets=10,
            overs=18.0
        )
        
        scorecard = Scorecard(
            id="game-201",
            match_id="game-201",
            home_team=home_team,
            away_team=away_team,
            date=datetime(2025, 10, 15, 10, 0)
        )
        
        snippet = CricketSnippetGenerator.generate_batting_summary(scorecard)
        
        assert "Batting Summary:" in snippet
        assert "Caroline Springs Blue U10:" in snippet
        assert "Harshvardhan: 45 runs (30 balls)" in snippet
    
    def test_generate_ladder_entry(self):
        """Test ladder entry generation"""
        entries = [
            LadderEntry(
                position=1,
                team_id="team-123",
                team_name="Caroline Springs Blue U10",
                matches_played=5,
                matches_won=4,
                matches_lost=1,
                points=16,
                percentage=80.0
            )
        ]
        
        ladder = Ladder(
            id="ladder-456",
            grade_id="grade-456",
            grade_name="Under 10s",
            entries=entries
        )
        ladder.team_id = "team-123"  # Set metadata
        
        snippet = CricketSnippetGenerator.generate_ladder_entry(ladder, "team-123")
        
        assert "Ladder Position: 1" in snippet
        assert "Team: Caroline Springs Blue U10" in snippet
        assert "Points: 16" in snippet
        assert "Matches: 5 played, 4 won, 1 lost" in snippet
        assert "Percentage: 80.0%" in snippet
    
    def test_generate_roster_snippet(self):
        """Test roster snippet generation"""
        players = [
            Player(
                id="player-001",
                name="Harshvardhan",
                is_captain=True
            ),
            Player(
                id="player-002",
                name="Alex Smith",
                is_vice_captain=True
            ),
            Player(
                id="player-003",
                name="John Doe",
                is_wicket_keeper=True
            )
        ]
        
        roster = Roster(
            team_id="team-123",
            team_name="Caroline Springs Blue U10",
            players=players
        )
        
        snippet = CricketSnippetGenerator.generate_roster_snippet(roster)
        
        assert "Team: Caroline Springs Blue U10" in snippet
        assert "Players: 3" in snippet
        assert "Captain: Harshvardhan" in snippet
        assert "Vice Captain: Alex Smith" in snippet
        assert "Wicket Keepers: John Doe" in snippet

class TestCricketMetadataAttacher:
    """Test metadata attachment"""
    
    def test_attach_team_metadata(self):
        """Test team metadata attachment"""
        team = Team(
            id="team-123",
            name="Caroline Springs Blue U10"
        )
        
        team_with_metadata = CricketMetadataAttacher.attach_team_metadata(
            team, "team-123", "season-789", "grade-456"
        )
        
        assert team_with_metadata.team_id == "team-123"
        assert team_with_metadata.season_id == "season-789"
        assert team_with_metadata.grade_id == "grade-456"
        assert team_with_metadata.type == "team"
    
    def test_attach_fixture_metadata(self):
        """Test fixture metadata attachment"""
        fixture = Fixture(
            id="fixture-101",
            home_team="Team A",
            away_team="Team B",
            home_team_id="team-123",
            away_team_id="team-456",
            date=datetime.utcnow()
        )
        
        fixture_with_metadata = CricketMetadataAttacher.attach_fixture_metadata(
            fixture, "team-123", "season-789", "grade-456"
        )
        
        assert fixture_with_metadata.team_id == "team-123"
        assert fixture_with_metadata.season_id == "season-789"
        assert fixture_with_metadata.grade_id == "grade-456"
        assert fixture_with_metadata.type == "fixture"

class TestCricketTextChunker:
    """Test text chunking for embeddings"""
    
    def test_chunk_short_text(self):
        """Test chunking short text"""
        text = "Short text that doesn't need chunking."
        chunks = CricketTextChunker.chunk_text(text, max_tokens=1000)
        
        assert len(chunks) == 1
        assert chunks[0] == text
    
    def test_chunk_long_text(self):
        """Test chunking long text"""
        # Create long text (simulate > 1000 tokens)
        long_text = "Line of text.\n" * 1000  # ~5000 characters
        chunks = CricketTextChunker.chunk_text(long_text, max_tokens=100)
        
        assert len(chunks) > 1
        assert all(len(chunk) <= 400 for chunk in chunks)  # 100 tokens * 4 chars
    
    def test_generate_embedding_text(self):
        """Test embedding text generation"""
        team = Team(
            id="team-123",
            name="Caroline Springs Blue U10",
            grade="Under 10s"
        )
        
        metadata = {
            "team_id": "team-123",
            "season_id": "season-789",
            "grade_id": "grade-456",
            "type": "team"
        }
        
        embedding_text = CricketTextChunker.generate_embedding_text(team, metadata)
        
        assert "Team: Caroline Springs Blue U10" in embedding_text
        assert "Grade: Under 10s" in embedding_text
        assert "Team ID: team-123" in embedding_text
        assert "Season: season-789" in embedding_text
        assert "Grade: grade-456" in embedding_text
        assert "Type: team" in embedding_text

class TestConvenienceFunctions:
    """Test convenience functions"""
    
    def test_normalize_playhq_data_team(self):
        """Test team normalization via convenience function"""
        team = normalize_playhq_data(
            "team", 
            MOCK_TEAM_DATA,
            grade=MOCK_GRADE_DATA,
            season=MOCK_SEASON_DATA
        )
        
        assert team is not None
        assert team.name == "Caroline Springs Blue U10"
    
    def test_normalize_playhq_data_fixture(self):
        """Test fixture normalization via convenience function"""
        fixture = normalize_playhq_data(
            "fixture",
            MOCK_FIXTURE_DATA,
            team_id="team-123"
        )
        
        assert fixture is not None
        assert fixture.home_team == "Caroline Springs Blue U10"
    
    def test_normalize_playhq_data_invalid_type(self):
        """Test invalid data type handling"""
        result = normalize_playhq_data("invalid_type", {})
        assert result is None
    
    def test_generate_snippet_fixture(self):
        """Test fixture snippet generation via convenience function"""
        fixture = Fixture(
            id="fixture-101",
            home_team="Team A",
            away_team="Team B",
            home_team_id="team-123",
            away_team_id="team-456",
            date=datetime.utcnow()
        )
        
        snippet = generate_snippet(fixture, "fixture")
        assert "Fixture: Team A vs Team B" in snippet
    
    def test_generate_snippet_default(self):
        """Test default snippet generation"""
        team = Team(id="team-123", name="Test Team")
        snippet = generate_snippet(team, "unknown_type")
        
        # Should fallback to to_text_summary method
        assert "Team: Test Team" in snippet

if __name__ == "__main__":
    pytest.main([__file__])
