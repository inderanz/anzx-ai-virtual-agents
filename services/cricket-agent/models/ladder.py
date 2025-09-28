"""
Ladder Model
Represents cricket competition ladder/standings
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class LadderEntry(BaseModel):
    """Individual ladder entry for a team"""
    position: int = Field(..., description="Ladder position")
    team_id: str = Field(..., description="Team ID")
    team_name: str = Field(..., description="Team name")
    
    # Match statistics
    matches_played: int = Field(0, description="Matches played")
    matches_won: int = Field(0, description="Matches won")
    matches_lost: int = Field(0, description="Matches lost")
    matches_drawn: int = Field(0, description="Matches drawn")
    matches_tied: int = Field(0, description="Matches tied")
    
    # Points and percentages
    points: int = Field(0, description="Competition points")
    percentage: Optional[float] = Field(None, description="Percentage")
    
    # Runs and wickets
    runs_for: int = Field(0, description="Runs scored for")
    runs_against: int = Field(0, description="Runs scored against")
    wickets_for: int = Field(0, description="Wickets taken for")
    wickets_against: int = Field(0, description="Wickets taken against")
    
    # Additional stats
    bonus_points: int = Field(0, description="Bonus points")
    penalty_points: int = Field(0, description="Penalty points")
    
    @property
    def win_percentage(self) -> float:
        """Calculate win percentage"""
        if self.matches_played > 0:
            return round((self.matches_won / self.matches_played) * 100, 2)
        return 0.0
    
    @property
    def net_run_rate(self) -> float:
        """Calculate net run rate"""
        if self.matches_played > 0:
            return round((self.runs_for - self.runs_against) / self.matches_played, 2)
        return 0.0

class Ladder(BaseModel):
    """Cricket competition ladder"""
    id: str = Field(..., description="Ladder ID")
    grade_id: str = Field(..., description="Grade ID")
    grade_name: str = Field(..., description="Grade name")
    season: Optional[str] = Field(None, description="Season")
    
    # Ladder entries
    entries: List[LadderEntry] = Field(default_factory=list, description="Ladder entries")
    
    # Metadata for embeddings and filtering
    team_id: Optional[str] = Field(None, description="Team ID for metadata")
    season_id: Optional[str] = Field(None, description="Season ID for metadata")
    grade_id: Optional[str] = Field(None, description="Grade ID for metadata")
    type: Optional[str] = Field(None, description="Data type for metadata")
    
    # Timestamps
    last_updated: Optional[datetime] = Field(None, description="Last update timestamp")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    
    def get_team_position(self, team_id: str) -> Optional[LadderEntry]:
        """Get ladder position for a specific team"""
        for entry in self.entries:
            if entry.team_id == team_id:
                return entry
        return None
    
    def get_team_position_by_name(self, team_name: str) -> Optional[LadderEntry]:
        """Get ladder position for a team by name"""
        for entry in self.entries:
            if entry.team_name.lower() == team_name.lower():
                return entry
        return None
    
    def get_top_teams(self, count: int = 4) -> List[LadderEntry]:
        """Get top N teams"""
        return sorted(self.entries, key=lambda x: (x.points, x.percentage or 0), reverse=True)[:count]
    
    def get_bottom_teams(self, count: int = 4) -> List[LadderEntry]:
        """Get bottom N teams"""
        return sorted(self.entries, key=lambda x: (x.points, x.percentage or 0))[:count]
    
    def get_cscc_teams(self, cscc_team_ids: List[str]) -> List[LadderEntry]:
        """Get CSCC teams from the ladder"""
        cscc_entries = []
        for entry in self.entries:
            if entry.team_id in cscc_team_ids:
                cscc_entries.append(entry)
        return sorted(cscc_entries, key=lambda x: x.position)
    
    def to_text_summary(self) -> str:
        """Convert ladder to text summary for embeddings"""
        lines = [
            f"Ladder: {self.grade_name}",
            f"Season: {self.season or 'Unknown'}"
        ]
        
        if self.last_updated:
            lines.append(f"Last Updated: {self.last_updated.strftime('%Y-%m-%d %H:%M')}")
        
        lines.append("")
        lines.append("Pos | Team | P | W | L | D | T | Pts | %")
        lines.append("-" * 50)
        
        for entry in self.entries:
            percentage_str = f"{entry.percentage:.1f}" if entry.percentage else "0.0"
            lines.append(
                f"{entry.position:3d} | {entry.team_name[:20]:20s} | "
                f"{entry.matches_played:2d} | {entry.matches_won:2d} | "
                f"{entry.matches_lost:2d} | {entry.matches_drawn:2d} | "
                f"{entry.matches_tied:2d} | {entry.points:3d} | {percentage_str}"
            )
        
        return "\n".join(lines)
    
    def to_short_summary(self) -> str:
        """Short summary for quick display"""
        if not self.entries:
            return f"{self.grade_name} Ladder (No entries)"
        
        top_team = self.entries[0]
        return f"{self.grade_name}: {top_team.team_name} leads with {top_team.points} points"
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
