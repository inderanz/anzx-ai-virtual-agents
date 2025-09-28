"""
Scorecard Model
Represents cricket match scorecard with batting and bowling details
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class BattingStats(BaseModel):
    """Individual batting statistics"""
    player_id: str = Field(..., description="Player ID")
    player_name: str = Field(..., description="Player name")
    runs: int = Field(0, description="Runs scored")
    balls: int = Field(0, description="Balls faced")
    fours: int = Field(0, description="Number of 4s")
    sixes: int = Field(0, description="Number of 6s")
    strike_rate: Optional[float] = Field(None, description="Strike rate")
    how_out: Optional[str] = Field(None, description="How player was dismissed")
    bowler: Optional[str] = Field(None, description="Bowler who dismissed player")
    
    @property
    def strike_rate_calculated(self) -> float:
        """Calculate strike rate if not provided"""
        if self.balls > 0:
            return round((self.runs / self.balls) * 100, 2)
        return 0.0

class BowlingStats(BaseModel):
    """Individual bowling statistics"""
    player_id: str = Field(..., description="Player ID")
    player_name: str = Field(..., description="Player name")
    overs: float = Field(0, description="Overs bowled")
    maidens: int = Field(0, description="Maidens bowled")
    runs_conceded: int = Field(0, description="Runs conceded")
    wickets: int = Field(0, description="Wickets taken")
    economy_rate: Optional[float] = Field(None, description="Economy rate")
    
    @property
    def economy_rate_calculated(self) -> float:
        """Calculate economy rate if not provided"""
        if self.overs > 0:
            return round(self.runs_conceded / self.overs, 2)
        return 0.0

class TeamScorecard(BaseModel):
    """Team scorecard for a match"""
    team_id: str = Field(..., description="Team ID")
    team_name: str = Field(..., description="Team name")
    total_runs: int = Field(0, description="Total runs scored")
    wickets: int = Field(0, description="Wickets lost")
    overs: float = Field(0, description="Overs faced")
    extras: int = Field(0, description="Extras (byes, leg byes, wides, no balls)")
    
    # Batting and bowling stats
    batting: List[BattingStats] = Field(default_factory=list, description="Batting statistics")
    bowling: List[BowlingStats] = Field(default_factory=list, description="Bowling statistics")
    
    def get_top_batsman(self) -> Optional[BattingStats]:
        """Get top scoring batsman"""
        if not self.batting:
            return None
        return max(self.batting, key=lambda x: x.runs)
    
    def get_top_bowler(self) -> Optional[BowlingStats]:
        """Get top wicket taker"""
        if not self.bowling:
            return None
        return max(self.bowling, key=lambda x: x.wickets)

class Scorecard(BaseModel):
    """Complete match scorecard"""
    id: str = Field(..., description="Scorecard ID")
    match_id: str = Field(..., description="Match ID")
    home_team: TeamScorecard = Field(..., description="Home team scorecard")
    away_team: TeamScorecard = Field(..., description="Away team scorecard")
    
    # Match details
    date: datetime = Field(..., description="Match date")
    venue: Optional[str] = Field(None, description="Match venue")
    grade: Optional[str] = Field(None, description="Grade/division")
    season: Optional[str] = Field(None, description="Season")
    
    # Match result
    result: Optional[str] = Field(None, description="Match result")
    man_of_the_match: Optional[str] = Field(None, description="Man of the match")
    
    # Additional info
    umpire: Optional[str] = Field(None, description="Match umpire")
    weather: Optional[str] = Field(None, description="Weather conditions")
    toss_winner: Optional[str] = Field(None, description="Toss winner")
    toss_decision: Optional[str] = Field(None, description="Toss decision")
    
    # Metadata for embeddings and filtering
    team_id: Optional[str] = Field(None, description="Team ID for metadata")
    season_id: Optional[str] = Field(None, description="Season ID for metadata")
    grade_id: Optional[str] = Field(None, description="Grade ID for metadata")
    type: Optional[str] = Field(None, description="Data type for metadata")
    
    # Timestamps
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    
    def get_winner(self) -> Optional[str]:
        """Get winning team name"""
        if self.home_team.total_runs > self.away_team.total_runs:
            return self.home_team.team_name
        elif self.away_team.total_runs > self.home_team.total_runs:
            return self.away_team.team_name
        return None
    
    def get_player_stats(self, player_name: str) -> Dict[str, Any]:
        """Get stats for a specific player"""
        stats = {
            "batting": None,
            "bowling": None
        }
        
        # Find batting stats
        for batting in self.home_team.batting + self.away_team.batting:
            if batting.player_name.lower() == player_name.lower():
                stats["batting"] = batting
                break
        
        # Find bowling stats
        for bowling in self.home_team.bowling + self.away_team.bowling:
            if bowling.player_name.lower() == player_name.lower():
                stats["bowling"] = bowling
                break
        
        return stats
    
    def to_text_summary(self) -> str:
        """Convert scorecard to text summary for embeddings"""
        lines = [
            f"Match: {self.home_team.team_name} vs {self.away_team.team_name}",
            f"Date: {self.date.strftime('%Y-%m-%d %H:%M')}",
            f"Venue: {self.venue or 'Unknown'}"
        ]
        
        if self.grade:
            lines.append(f"Grade: {self.grade}")
        
        if self.season:
            lines.append(f"Season: {self.season}")
        
        # Match result
        if self.result:
            lines.append(f"Result: {self.result}")
        
        # Scores
        lines.append(f"Score: {self.home_team.team_name} {self.home_team.total_runs}/{self.home_team.wickets} ({self.home_team.overs} overs)")
        lines.append(f"Score: {self.away_team.team_name} {self.away_team.total_runs}/{self.away_team.wickets} ({self.away_team.overs} overs)")
        
        # Top performers
        home_top_batsman = self.home_team.get_top_batsman()
        if home_top_batsman:
            lines.append(f"Top batsman ({self.home_team.team_name}): {home_top_batsman.player_name} {home_top_batsman.runs} runs")
        
        away_top_batsman = self.away_team.get_top_batsman()
        if away_top_batsman:
            lines.append(f"Top batsman ({self.away_team.team_name}): {away_top_batsman.player_name} {away_top_batsman.runs} runs")
        
        home_top_bowler = self.home_team.get_top_bowler()
        if home_top_bowler:
            lines.append(f"Top bowler ({self.home_team.team_name}): {home_top_bowler.player_name} {home_top_bowler.wickets}/{home_top_bowler.runs_conceded}")
        
        away_top_bowler = self.away_team.get_top_bowler()
        if away_top_bowler:
            lines.append(f"Top bowler ({self.away_team.team_name}): {away_top_bowler.player_name} {away_top_bowler.wickets}/{away_top_bowler.runs_conceded}")
        
        if self.man_of_the_match:
            lines.append(f"Man of the Match: {self.man_of_the_match}")
        
        return "\n".join(lines)
    
    def to_short_summary(self) -> str:
        """Short summary for quick display"""
        return f"{self.home_team.team_name} {self.home_team.total_runs}/{self.home_team.wickets} vs {self.away_team.team_name} {self.away_team.total_runs}/{self.away_team.wickets}"
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
