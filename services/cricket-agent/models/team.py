"""
Team Model
Represents a cricket team with players and metadata
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class Player(BaseModel):
    """Individual player model"""
    id: str = Field(..., description="Player ID")
    name: str = Field(..., description="Player name")
    position: Optional[str] = Field(None, description="Player position/role")
    jersey_number: Optional[int] = Field(None, description="Jersey number")
    is_captain: bool = Field(False, description="Is team captain")
    is_vice_captain: bool = Field(False, description="Is vice captain")
    is_wicket_keeper: bool = Field(False, description="Is wicket keeper")
    
    # Player details
    age: Optional[int] = Field(None, description="Player age")
    batting_style: Optional[str] = Field(None, description="Batting style (LHB, RHB)")
    bowling_style: Optional[str] = Field(None, description="Bowling style")
    
    # Contact info (if available)
    phone: Optional[str] = Field(None, description="Phone number")
    email: Optional[str] = Field(None, description="Email address")
    
    def get_role_display(self) -> str:
        """Get display role for player"""
        roles = []
        if self.is_captain:
            roles.append("Captain")
        elif self.is_vice_captain:
            roles.append("Vice Captain")
        if self.is_wicket_keeper:
            roles.append("WK")
        if self.position:
            roles.append(self.position)
        return ", ".join(roles) if roles else "Player"
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class Team(BaseModel):
    """Cricket team model"""
    id: str = Field(..., description="Team ID")
    name: str = Field(..., description="Team name")
    grade: Optional[str] = Field(None, description="Team grade/division")
    season: Optional[str] = Field(None, description="Season")
    players: List[Player] = Field(default_factory=list, description="Team players")
    coach: Optional[str] = Field(None, description="Team coach")
    manager: Optional[str] = Field(None, description="Team manager")
    
    # Metadata for embeddings and filtering
    team_id: Optional[str] = Field(None, description="Team ID for metadata")
    season_id: Optional[str] = Field(None, description="Season ID for metadata")
    grade_id: Optional[str] = Field(None, description="Grade ID for metadata")
    type: Optional[str] = Field(None, description="Data type for metadata")
    
    # Timestamps
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    
    def get_player_by_name(self, name: str) -> Optional[Player]:
        """Find player by name (case-insensitive)"""
        name_lower = name.lower()
        for player in self.players:
            if player.name.lower() == name_lower:
                return player
        return None
    
    def get_captain(self) -> Optional[Player]:
        """Get team captain"""
        for player in self.players:
            if player.is_captain:
                return player
        return None
    
    def get_vice_captain(self) -> Optional[Player]:
        """Get vice captain"""
        for player in self.players:
            if player.is_vice_captain:
                return player
        return None
    
    def to_text_summary(self) -> str:
        """Convert team to text summary for embeddings"""
        lines = [
            f"Team: {self.name}",
            f"Grade: {self.grade or 'Unknown'}",
            f"Season: {self.season or 'Unknown'}"
        ]
        
        if self.coach:
            lines.append(f"Coach: {self.coach}")
        
        if self.manager:
            lines.append(f"Manager: {self.manager}")
        
        # Add players
        if self.players:
            lines.append("Players:")
            for player in self.players:
                role = ""
                if player.is_captain:
                    role = " (Captain)"
                elif player.is_vice_captain:
                    role = " (Vice Captain)"
                
                lines.append(f"  - {player.name}{role}")
        
        return "\n".join(lines)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
