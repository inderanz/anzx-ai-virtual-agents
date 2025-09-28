"""
Fixture Model
Represents a cricket match fixture
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class MatchStatus(str, Enum):
    """Match status enumeration"""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    POSTPONED = "postponed"

class Fixture(BaseModel):
    """Cricket fixture/match model"""
    id: str = Field(..., description="Fixture ID")
    home_team: str = Field(..., description="Home team name")
    away_team: str = Field(..., description="Away team name")
    home_team_id: str = Field(..., description="Home team ID")
    away_team_id: str = Field(..., description="Away team ID")
    
    # Match details
    date: datetime = Field(..., description="Match date and time")
    venue: Optional[str] = Field(None, description="Match venue")
    grade: Optional[str] = Field(None, description="Grade/division")
    season: Optional[str] = Field(None, description="Season")
    
    # Status and results
    status: MatchStatus = Field(MatchStatus.SCHEDULED, description="Match status")
    home_score: Optional[int] = Field(None, description="Home team score")
    away_score: Optional[int] = Field(None, description="Away team score")
    result: Optional[str] = Field(None, description="Match result")
    
    # Additional info
    umpire: Optional[str] = Field(None, description="Match umpire")
    weather: Optional[str] = Field(None, description="Weather conditions")
    notes: Optional[str] = Field(None, description="Additional notes")
    
    # Metadata for embeddings and filtering
    team_id: Optional[str] = Field(None, description="Team ID for metadata")
    season_id: Optional[str] = Field(None, description="Season ID for metadata")
    grade_id: Optional[str] = Field(None, description="Grade ID for metadata")
    type: Optional[str] = Field(None, description="Data type for metadata")
    
    # Timestamps
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    
    def is_cscc_team(self, cscc_team_ids: List[str]) -> bool:
        """Check if this fixture involves a CSCC team"""
        return (self.home_team_id in cscc_team_ids or 
                self.away_team_id in cscc_team_ids)
    
    def get_cscc_team(self, cscc_team_ids: List[str]) -> Optional[str]:
        """Get the CSCC team name if this fixture involves CSCC"""
        if self.home_team_id in cscc_team_ids:
            return self.home_team
        elif self.away_team_id in cscc_team_ids:
            return self.away_team
        return None
    
    def get_opponent(self, cscc_team_ids: List[str]) -> Optional[str]:
        """Get the opponent team name if this fixture involves CSCC"""
        if self.home_team_id in cscc_team_ids:
            return self.away_team
        elif self.away_team_id in cscc_team_ids:
            return self.home_team
        return None
    
    def is_home_game(self, cscc_team_ids: List[str]) -> bool:
        """Check if this is a home game for CSCC"""
        return self.home_team_id in cscc_team_ids
    
    def to_text_summary(self) -> str:
        """Convert fixture to text summary for embeddings"""
        lines = [
            f"Match: {self.home_team} vs {self.away_team}",
            f"Date: {self.date.strftime('%Y-%m-%d %H:%M')}",
            f"Status: {self.status.value}"
        ]
        
        if self.venue:
            lines.append(f"Venue: {self.venue}")
        
        if self.grade:
            lines.append(f"Grade: {self.grade}")
        
        if self.season:
            lines.append(f"Season: {self.season}")
        
        if self.status == MatchStatus.COMPLETED and self.result:
            lines.append(f"Result: {self.result}")
            if self.home_score is not None and self.away_score is not None:
                lines.append(f"Score: {self.home_team} {self.home_score} - {self.away_team} {self.away_score}")
        
        if self.umpire:
            lines.append(f"Umpire: {self.umpire}")
        
        if self.weather:
            lines.append(f"Weather: {self.weather}")
        
        if self.notes:
            lines.append(f"Notes: {self.notes}")
        
        return "\n".join(lines)
    
    def to_short_summary(self) -> str:
        """Short summary for quick display"""
        if self.status == MatchStatus.COMPLETED:
            if self.result:
                return f"{self.home_team} vs {self.away_team} - {self.result}"
            else:
                return f"{self.home_team} vs {self.away_team} - Completed"
        else:
            return f"{self.home_team} vs {self.away_team} - {self.date.strftime('%Y-%m-%d %H:%M')}"
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
