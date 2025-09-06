"""
Conversation Management API Endpoints
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from ..utils.database import get_db
from ..middleware.auth import get_current_user, get_organization_id
from ..services.conversation_service import conversation_service
from ..models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/conversations", tags=["conversations"])


# Pydantic models
class ConversationCreate(BaseModel):
    assistant_id: str = Field(..., description="Assistant ID")
    title: Optional[str] = Field(None, description="Conversation title")
    channel: Optional[str] = Field(default="web", description="Communication channel")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")


class ConversationUpdate(BaseModel):
    title: Optional[str] = Field(None, description="Conversation title")
    status: Optional[str] = Field(None, description="Conversation status")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadata updates")


class ConversationEscalation(BaseModel):
    escalation_reason: str = Field(..., description="Reason for escalation")
    escalate_to: Optional[str] = Field(None, description="Specific user to escalate to")


class ConversationRouting(BaseModel):
    target_assistant_id: str = Field(..., description="Target assistant ID")
    routing_reason: str = Field(..., description="Reason for routing")


class ConversationArchive(BaseModel):
    archive_reason: Optional[str] = Field(None, description="Reason for archiving")


class MessageFeedback(BaseModel):
    message_id: str = Field(..., description="Message ID")
    rating: int = Field(..., ge=1, le=5, description="Rating from 1-5")
    comment: Optional[str] = Field(None, description="Feedback comment")


# Conversation CRUD endpoints
@router.post("", response_model=Dict[str, Any])
async def create_conversation(
    conversation_data: ConversationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id)
):
    """Create a new conversation"""
    try:
        result = await conversation_service.create_conversation(
            db=db,
            organization_id=organization_id,
            assistant_id=conversation_data.assistant_id,
            user_id=str(current_user.id),
            title=conversation_data.title,
            channel=conversation_data.channel,
            metadata=conversation_data.metadata
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Conversation creation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create conversation"
        )


@router.get("", response_model=List[Dict[str, Any]])
async def get_conversations(
    status: Optional[str] = Query(None, description="Filter by status"),
    channel: Optional[str] = Query(None, description="Filter by channel"),
    assistant_id: Optional[str] = Query(None, description="Filter by assistant ID"),
    limit: int = Query(50, ge=1, le=100, description="Maximum results"),
    offset: int = Query(0, ge=0, description="Results offset"),
    include_analytics: bool = Query(False, description="Include analytics data"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id)
):
    """Get conversations with filtering and pagination"""
    try:
        conversations = await conversation_service.get_conversations(
            db=db,
            organization_id=organization_id,
            user_id=str(current_user.id),
            status=status,
            channel=channel,
            assistant_id=assistant_id,
            limit=limit,
            offset=offset,
            include_analytics=include_analytics
        )
        
        return conversations
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get conversations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve conversations"
        )


@router.get("/{conversation_id}", response_model=Dict[str, Any])
async def get_conversation(
    conversation_id: str,
    include_messages: bool = Query(True, description="Include message history"),
    include_analytics: bool = Query(True, description="Include analytics data"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id)
):
    """Get specific conversation details"""
    try:
        conversation = await conversation_service.get_conversation(
            db=db,
            conversation_id=conversation_id,
            organization_id=organization_id,
            include_messages=include_messages,
            include_analytics=include_analytics
        )
        
        return conversation
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve conversation"
        )


@router.put("/{conversation_id}", response_model=Dict[str, Any])
async def update_conversation(
    conversation_id: str,
    update_data: ConversationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id)
):
    """Update conversation details"""
    try:
        # Convert to dict, excluding None values
        updates = {k: v for k, v in update_data.dict().items() if v is not None}
        
        result = await conversation_service.update_conversation(
            db=db,
            conversation_id=conversation_id,
            organization_id=organization_id,
            updates=updates
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update conversation"
        )


@router.post("/{conversation_id}/archive", response_model=Dict[str, Any])
async def archive_conversation(
    conversation_id: str,
    archive_data: ConversationArchive,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id)
):
    """Archive a conversation"""
    try:
        result = await conversation_service.archive_conversation(
            db=db,
            conversation_id=conversation_id,
            organization_id=organization_id,
            archive_reason=archive_data.archive_reason
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to archive conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to archive conversation"
        )


# Conversation management endpoints
@router.post("/{conversation_id}/escalate", response_model=Dict[str, Any])
async def escalate_conversation(
    conversation_id: str,
    escalation_data: ConversationEscalation,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id)
):
    """Escalate conversation to human agent"""
    try:
        result = await conversation_service.escalate_conversation(
            db=db,
            conversation_id=conversation_id,
            organization_id=organization_id,
            escalation_reason=escalation_data.escalation_reason,
            escalate_to=escalation_data.escalate_to
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to escalate conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to escalate conversation"
        )


@router.post("/{conversation_id}/route", response_model=Dict[str, Any])
async def route_conversation(
    conversation_id: str,
    routing_data: ConversationRouting,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id)
):
    """Route conversation to different assistant"""
    try:
        result = await conversation_service.route_conversation(
            db=db,
            conversation_id=conversation_id,
            organization_id=organization_id,
            target_assistant_id=routing_data.target_assistant_id,
            routing_reason=routing_data.routing_reason
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to route conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to route conversation"
        )


# Message feedback endpoints
@router.post("/messages/feedback", response_model=Dict[str, Any])
async def submit_message_feedback(
    feedback_data: MessageFeedback,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id)
):
    """Submit feedback for a message"""
    try:
        from ..models.user import Message, Conversation
        
        # Get message and verify ownership
        message = db.query(Message).join(Conversation).filter(
            Message.id == feedback_data.message_id,
            Conversation.organization_id == organization_id
        ).first()
        
        if not message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message not found"
            )
        
        # Update message feedback
        message.feedback_rating = feedback_data.rating
        message.feedback_comment = feedback_data.comment
        
        db.commit()
        
        return {
            "message_id": str(message.id),
            "feedback_rating": message.feedback_rating,
            "feedback_comment": message.feedback_comment,
            "submitted_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to submit message feedback: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit feedback"
        )


# Analytics endpoints
@router.get("/analytics/overview", response_model=Dict[str, Any])
async def get_conversation_analytics(
    start_date: Optional[datetime] = Query(None, description="Start date for analytics"),
    end_date: Optional[datetime] = Query(None, description="End date for analytics"),
    channel: Optional[str] = Query(None, description="Filter by channel"),
    assistant_id: Optional[str] = Query(None, description="Filter by assistant"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id)
):
    """Get conversation analytics overview"""
    try:
        analytics = await conversation_service.get_conversation_analytics(
            db=db,
            organization_id=organization_id,
            start_date=start_date,
            end_date=end_date,
            channel=channel,
            assistant_id=assistant_id
        )
        
        return analytics
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get conversation analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve analytics"
        )


@router.get("/analytics/satisfaction", response_model=Dict[str, Any])
async def get_satisfaction_analytics(
    start_date: Optional[datetime] = Query(None, description="Start date"),
    end_date: Optional[datetime] = Query(None, description="End date"),
    channel: Optional[str] = Query(None, description="Filter by channel"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id)
):
    """Get detailed satisfaction analytics"""
    try:
        from ..models.user import Message, Conversation
        from sqlalchemy import func
        
        # Default date range (last 30 days)
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()
        
        # Base query for messages with feedback
        query = db.query(Message).join(Conversation).filter(
            Conversation.organization_id == organization_id,
            Message.feedback_rating.isnot(None),
            Message.created_at >= start_date,
            Message.created_at <= end_date
        )
        
        # Apply channel filter
        if channel:
            query = query.filter(
                Conversation.metadata.op('->>')('channel') == channel
            )
        
        messages_with_feedback = query.all()
        
        if not messages_with_feedback:
            return {
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "total_ratings": 0,
                "average_rating": None,
                "rating_distribution": {str(i): 0 for i in range(1, 6)},
                "satisfaction_trend": [],
                "top_feedback_themes": []
            }
        
        # Calculate metrics
        ratings = [msg.feedback_rating for msg in messages_with_feedback]
        average_rating = sum(ratings) / len(ratings)
        
        # Rating distribution
        rating_distribution = {str(i): 0 for i in range(1, 6)}
        for rating in ratings:
            rating_distribution[str(rating)] += 1
        
        # Satisfaction trend (daily averages)
        daily_ratings = {}
        for msg in messages_with_feedback:
            date_key = msg.created_at.date().isoformat()
            if date_key not in daily_ratings:
                daily_ratings[date_key] = []
            daily_ratings[date_key].append(msg.feedback_rating)
        
        satisfaction_trend = []
        for date_key in sorted(daily_ratings.keys()):
            daily_avg = sum(daily_ratings[date_key]) / len(daily_ratings[date_key])
            satisfaction_trend.append({
                "date": date_key,
                "average_rating": round(daily_avg, 2),
                "rating_count": len(daily_ratings[date_key])
            })
        
        # Top feedback themes (simple keyword analysis)
        feedback_comments = [msg.feedback_comment for msg in messages_with_feedback if msg.feedback_comment]
        feedback_themes = analyze_feedback_themes(feedback_comments)
        
        return {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "total_ratings": len(ratings),
            "average_rating": round(average_rating, 2),
            "rating_distribution": rating_distribution,
            "satisfaction_trend": satisfaction_trend,
            "top_feedback_themes": feedback_themes
        }
        
    except Exception as e:
        logger.error(f"Failed to get satisfaction analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve satisfaction analytics"
        )


# Admin endpoints (for organization-wide conversation management)
@router.get("/admin/all", response_model=List[Dict[str, Any]])
async def get_all_conversations_admin(
    status: Optional[str] = Query(None, description="Filter by status"),
    channel: Optional[str] = Query(None, description="Filter by channel"),
    assistant_id: Optional[str] = Query(None, description="Filter by assistant ID"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    limit: int = Query(50, ge=1, le=100, description="Maximum results"),
    offset: int = Query(0, ge=0, description="Results offset"),
    include_analytics: bool = Query(False, description="Include analytics data"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id)
):
    """Get all conversations for organization (admin only)"""
    try:
        # Check if user has admin role
        if not current_user.role or current_user.role not in ["admin", "owner"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        
        conversations = await conversation_service.get_conversations(
            db=db,
            organization_id=organization_id,
            user_id=user_id,  # Can filter by specific user or see all
            status=status,
            channel=channel,
            assistant_id=assistant_id,
            limit=limit,
            offset=offset,
            include_analytics=include_analytics
        )
        
        return conversations
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get admin conversations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve conversations"
        )


def analyze_feedback_themes(comments: List[str]) -> List[Dict[str, Any]]:
    """Simple feedback theme analysis"""
    if not comments:
        return []
    
    # Simple keyword-based theme detection
    themes = {
        "helpful": ["helpful", "useful", "good", "great", "excellent", "perfect"],
        "fast": ["fast", "quick", "rapid", "immediate", "instant"],
        "accurate": ["accurate", "correct", "right", "precise", "exact"],
        "friendly": ["friendly", "polite", "nice", "kind", "pleasant"],
        "unclear": ["unclear", "confusing", "vague", "ambiguous"],
        "slow": ["slow", "delayed", "late", "waiting"],
        "unhelpful": ["unhelpful", "useless", "bad", "terrible", "awful"],
        "incorrect": ["wrong", "incorrect", "inaccurate", "false", "mistake"]
    }
    
    theme_counts = {theme: 0 for theme in themes}
    
    for comment in comments:
        comment_lower = comment.lower()
        for theme, keywords in themes.items():
            if any(keyword in comment_lower for keyword in keywords):
                theme_counts[theme] += 1
    
    # Return top themes
    sorted_themes = sorted(theme_counts.items(), key=lambda x: x[1], reverse=True)
    return [
        {"theme": theme, "count": count, "percentage": round(count / len(comments) * 100, 1)}
        for theme, count in sorted_themes[:5]
        if count > 0
    ]