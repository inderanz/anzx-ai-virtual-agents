"""
PlayHQ Webhook Models
Pydantic models for PlayHQ webhook payloads
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class WebhookEventType(str, Enum):
    """PlayHQ webhook event types"""
    FIXTURE_UPDATE = "fixture_update"
    SCORECARD_UPDATE = "scorecard_update"
    LADDER_UPDATE = "ladder_update"
    ROSTER_UPDATE = "roster_update"

class WebhookPayload(BaseModel):
    """Base webhook payload"""
    event_type: WebhookEventType = Field(..., description="Event type")
    timestamp: datetime = Field(..., description="Event timestamp")
    data: Dict[str, Any] = Field(..., description="Event data")

class FixtureUpdateData(BaseModel):
    """Fixture update webhook data"""
    fixture_id: str = Field(..., description="Fixture ID")
    team_id: str = Field(..., description="Team ID")
    season_id: str = Field(..., description="Season ID")
    grade_id: str = Field(..., description="Grade ID")
    status: str = Field(..., description="Fixture status")
    venue: Optional[str] = Field(None, description="Venue")
    start_time: Optional[datetime] = Field(None, description="Start time")
    opponent: Optional[str] = Field(None, description="Opponent team")
    changes: Dict[str, Any] = Field(default_factory=dict, description="Changed fields")

class ScorecardUpdateData(BaseModel):
    """Scorecard update webhook data"""
    fixture_id: str = Field(..., description="Fixture ID")
    team_id: str = Field(..., description="Team ID")
    season_id: str = Field(..., description="Season ID")
    grade_id: str = Field(..., description="Grade ID")
    is_completed: bool = Field(..., description="Whether fixture is completed")
    batting_summary: Optional[Dict[str, Any]] = Field(None, description="Batting summary")
    bowling_summary: Optional[Dict[str, Any]] = Field(None, description="Bowling summary")
    score: Optional[str] = Field(None, description="Team score")
    overs: Optional[str] = Field(None, description="Overs bowled")
    changes: Dict[str, Any] = Field(default_factory=dict, description="Changed fields")

class LadderUpdateData(BaseModel):
    """Ladder update webhook data"""
    grade_id: str = Field(..., description="Grade ID")
    season_id: str = Field(..., description="Season ID")
    team_id: str = Field(..., description="Team ID")
    position: int = Field(..., description="Team position")
    points: int = Field(..., description="Team points")
    played: int = Field(..., description="Games played")
    won: int = Field(..., description="Games won")
    lost: int = Field(..., description="Games lost")
    changes: Dict[str, Any] = Field(default_factory=dict, description="Changed fields")

class RosterUpdateData(BaseModel):
    """Roster update webhook data"""
    team_id: str = Field(..., description="Team ID")
    season_id: str = Field(..., description="Season ID")
    grade_id: str = Field(..., description="Grade ID")
    players: List[Dict[str, Any]] = Field(..., description="Player list")
    changes: Dict[str, Any] = Field(default_factory=dict, description="Changed fields")

class WebhookRequest(BaseModel):
    """Webhook request model"""
    event_type: WebhookEventType
    timestamp: datetime
    data: Dict[str, Any]
    
    def get_typed_data(self) -> BaseModel:
        """Get typed data based on event type"""
        if self.event_type == WebhookEventType.FIXTURE_UPDATE:
            return FixtureUpdateData(**self.data)
        elif self.event_type == WebhookEventType.SCORECARD_UPDATE:
            return ScorecardUpdateData(**self.data)
        elif self.event_type == WebhookEventType.LADDER_UPDATE:
            return LadderUpdateData(**self.data)
        elif self.event_type == WebhookEventType.ROSTER_UPDATE:
            return RosterUpdateData(**self.data)
        else:
            raise ValueError(f"Unknown event type: {self.event_type}")

class WebhookResponse(BaseModel):
    """Webhook response model"""
    success: bool = Field(..., description="Processing success")
    message: str = Field(..., description="Response message")
    processed_count: int = Field(default=0, description="Number of records processed")
    errors: List[str] = Field(default_factory=list, description="Processing errors")
