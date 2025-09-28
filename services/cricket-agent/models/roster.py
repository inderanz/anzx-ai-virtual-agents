"""
Roster Model
Represents team roster with player details
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from .team import Player

class Roster(BaseModel):
    """Team roster"""
    team_id: str = Field(..., description="Team ID")
    team_name: str = Field(..., description="Team name")
    grade: Optional[str] = Field(None, description="Team grade/division")
    season: Optional[str] = Field(None, description="Season")
    
    # Players
    players: List[Player] = Field(default_factory=list, description="Team players")
    
    # Team management
    coach: Optional[str] = Field(None, description="Team coach")
    manager: Optional[str] = Field(None, description="Team manager")
    assistant_coach: Optional[str] = Field(None, description="Assistant coach")
    
    # Metadata for embeddings and filtering
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
    
    def get_wicket_keepers(self) -> List[Player]:
        """Get wicket keepers"""
        return [player for player in self.players if player.is_wicket_keeper]
    
    def get_players_by_position(self, position: str) -> List[Player]:
        """Get players by position"""
        return [player for player in self.players if player.position and player.position.lower() == position.lower()]
    
    def get_players_by_batting_style(self, style: str) -> List[Player]:
        """Get players by batting style"""
        return [player for player in self.players if player.batting_style and player.batting_style.lower() == style.lower()]
    
    def get_players_by_bowling_style(self, style: str) -> List[Player]:
        """Get players by bowling style"""
        return [player for player in self.players if player.bowling_style and player.bowling_style.lower() == style.lower()]
    
    def to_text_summary(self) -> str:
        """Convert roster to text summary for embeddings"""
        lines = [
            f"Team: {self.team_name}",
            f"Grade: {self.grade or 'Unknown'}",
            f"Season: {self.season or 'Unknown'}"
        ]
        
        # Management
        if self.coach:
            lines.append(f"Coach: {self.coach}")
        if self.manager:
            lines.append(f"Manager: {self.manager}")
        if self.assistant_coach:
            lines.append(f"Assistant Coach: {self.assistant_coach}")
        
        lines.append("")
        lines.append("Players:")
        
        # Sort players by role importance
        sorted_players = sorted(self.players, key=lambda p: (
            not p.is_captain,  # Captain first
            not p.is_vice_captain,  # Vice captain second
            not p.is_wicket_keeper,  # Wicket keeper third
            p.name  # Then alphabetically
        ))
        
        for player in sorted_players:
            role = player.get_role_display()
            jersey = f"#{player.jersey_number}" if player.jersey_number else ""
            
            player_info = f"  - {player.name}"
            if jersey:
                player_info += f" {jersey}"
            if role:
                player_info += f" ({role})"
            
            # Add batting/bowling style if available
            styles = []
            if player.batting_style:
                styles.append(f"Bat: {player.batting_style}")
            if player.bowling_style:
                styles.append(f"Bowl: {player.bowling_style}")
            
            if styles:
                player_info += f" [{', '.join(styles)}]"
            
            lines.append(player_info)
        
        return "\n".join(lines)
    
    def to_short_summary(self) -> str:
        """Short summary for quick display"""
        captain = self.get_captain()
        vice_captain = self.get_vice_captain()
        
        summary = f"{self.team_name} ({len(self.players)} players)"
        
        if captain:
            summary += f" - Captain: {captain.name}"
        if vice_captain:
            summary += f", VC: {vice_captain.name}"
        
        return summary
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
