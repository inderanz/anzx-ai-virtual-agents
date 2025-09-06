"""
Conversation Management Service
Handles conversation persistence, routing, escalation, and analytics
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from fastapi import HTTPException, status

from ..models.user import (
    Organization, User, Assistant, Conversation, Message, 
    ChatWidget, EmailThread
)
from ..services.agent_service import agent_service
from ..middleware.usage_tracking import usage_tracker

logger = logging.getLogger(__name__)


class ConversationService:
    """
    Service for managing conversations across multiple channels
    
    Features:
    - Conversation persistence with message history
    - Cross-channel conversation routing
    - Escalation workflows with human handoff
    - Conversation analytics and satisfaction tracking
    - Context management and continuity
    """
    
    def __init__(self):
        self.agent_service = agent_service
    
    async def create_conversation(
        self,
        db: Session,
        organization_id: str,
        assistant_id: str,
        user_id: Optional[str] = None,
        title: Optional[str] = None,
        channel: str = "web",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new conversation
        
        Args:
            db: Database session
            organization_id: Organization ID
            assistant_id: Assistant ID
            user_id: User ID (optional for anonymous conversations)
            title: Conversation title
            channel: Communication channel (web, email, widget)
            metadata: Additional metadata
            
        Returns:
            Created conversation details
        """
        try:
            # Validate organization and assistant
            org = db.query(Organization).filter(Organization.id == organization_id).first()
            if not org:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Organization not found"
                )
            
            assistant = db.query(Assistant).filter(
                Assistant.id == assistant_id,
                Assistant.organization_id == organization_id
            ).first()
            if not assistant:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Assistant not found"
                )
            
            # Create conversation
            conversation = Conversation(
                user_id=user_id,
                assistant_id=assistant_id,
                organization_id=organization_id,
                title=title or f"Conversation with {assistant.name}",
                status="active",
                metadata={
                    "channel": channel,
                    "created_via": channel,
                    **(metadata or {})
                }
            )
            
            db.add(conversation)
            db.commit()
            
            logger.info(f"Created conversation {conversation.id} for organization {organization_id}")
            
            return {
                "conversation_id": str(conversation.id),
                "title": conversation.title,
                "status": conversation.status,
                "channel": channel,
                "assistant": {
                    "id": str(assistant.id),
                    "name": assistant.name,
                    "type": assistant.type
                },
                "created_at": conversation.created_at.isoformat()
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to create conversation: {e}")
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create conversation"
            )
    
    async def get_conversations(
        self,
        db: Session,
        organization_id: str,
        user_id: Optional[str] = None,
        status: Optional[str] = None,
        channel: Optional[str] = None,
        assistant_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
        include_analytics: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get conversations with filtering and pagination
        
        Args:
            db: Database session
            organization_id: Organization ID
            user_id: Filter by user ID
            status: Filter by status
            channel: Filter by channel
            assistant_id: Filter by assistant ID
            limit: Maximum results
            offset: Results offset
            include_analytics: Include analytics data
            
        Returns:
            List of conversations
        """
        try:
            query = db.query(Conversation).filter(
                Conversation.organization_id == organization_id
            )
            
            # Apply filters
            if user_id:
                query = query.filter(Conversation.user_id == user_id)
            
            if status:
                query = query.filter(Conversation.status == status)
            
            if channel:
                query = query.filter(
                    Conversation.metadata.op('->>')('channel') == channel
                )
            
            if assistant_id:
                query = query.filter(Conversation.assistant_id == assistant_id)
            
            # Get conversations with pagination
            conversations = query.order_by(
                desc(Conversation.updated_at)
            ).offset(offset).limit(limit).all()
            
            result = []
            for conv in conversations:
                # Get basic conversation data
                conv_data = await self._format_conversation(db, conv, include_analytics)
                result.append(conv_data)
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to get conversations: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve conversations"
            )
    
    async def get_conversation(
        self,
        db: Session,
        conversation_id: str,
        organization_id: str,
        include_messages: bool = True,
        include_analytics: bool = True
    ) -> Dict[str, Any]:
        """
        Get specific conversation details
        
        Args:
            db: Database session
            conversation_id: Conversation ID
            organization_id: Organization ID
            include_messages: Include message history
            include_analytics: Include analytics data
            
        Returns:
            Conversation details
        """
        try:
            conversation = db.query(Conversation).filter(
                Conversation.id == conversation_id,
                Conversation.organization_id == organization_id
            ).first()
            
            if not conversation:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conversation not found"
                )
            
            # Format conversation data
            conv_data = await self._format_conversation(
                db, conversation, include_analytics
            )
            
            # Include messages if requested
            if include_messages:
                messages = db.query(Message).filter(
                    Message.conversation_id == conversation_id
                ).order_by(Message.created_at).all()
                
                conv_data["messages"] = [
                    await self._format_message(msg) for msg in messages
                ]
            
            return conv_data
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to get conversation: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve conversation"
            )
    
    async def update_conversation(
        self,
        db: Session,
        conversation_id: str,
        organization_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update conversation details
        
        Args:
            db: Database session
            conversation_id: Conversation ID
            organization_id: Organization ID
            updates: Fields to update
            
        Returns:
            Updated conversation details
        """
        try:
            conversation = db.query(Conversation).filter(
                Conversation.id == conversation_id,
                Conversation.organization_id == organization_id
            ).first()
            
            if not conversation:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conversation not found"
                )
            
            # Update allowed fields
            if "title" in updates:
                conversation.title = updates["title"]
            
            if "status" in updates:
                conversation.status = updates["status"]
            
            if "metadata" in updates:
                current_metadata = conversation.metadata or {}
                current_metadata.update(updates["metadata"])
                conversation.metadata = current_metadata
            
            conversation.updated_at = datetime.utcnow()
            db.commit()
            
            return {
                "conversation_id": str(conversation.id),
                "title": conversation.title,
                "status": conversation.status,
                "updated_at": conversation.updated_at.isoformat()
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to update conversation: {e}")
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update conversation"
            )
    
    async def archive_conversation(
        self,
        db: Session,
        conversation_id: str,
        organization_id: str,
        archive_reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Archive a conversation
        
        Args:
            db: Database session
            conversation_id: Conversation ID
            organization_id: Organization ID
            archive_reason: Reason for archiving
            
        Returns:
            Archive result
        """
        try:
            conversation = db.query(Conversation).filter(
                Conversation.id == conversation_id,
                Conversation.organization_id == organization_id
            ).first()
            
            if not conversation:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conversation not found"
                )
            
            # Update conversation status
            conversation.status = "archived"
            conversation.updated_at = datetime.utcnow()
            
            # Add archive metadata
            metadata = conversation.metadata or {}
            metadata.update({
                "archived_at": datetime.utcnow().isoformat(),
                "archive_reason": archive_reason or "Manual archive"
            })
            conversation.metadata = metadata
            
            db.commit()
            
            logger.info(f"Archived conversation {conversation_id}")
            
            return {
                "conversation_id": str(conversation.id),
                "status": "archived",
                "archived_at": datetime.utcnow().isoformat()
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to archive conversation: {e}")
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to archive conversation"
            )
    
    async def escalate_conversation(
        self,
        db: Session,
        conversation_id: str,
        organization_id: str,
        escalation_reason: str,
        escalate_to: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Escalate conversation to human agent
        
        Args:
            db: Database session
            conversation_id: Conversation ID
            organization_id: Organization ID
            escalation_reason: Reason for escalation
            escalate_to: Specific user to escalate to
            
        Returns:
            Escalation result
        """
        try:
            conversation = db.query(Conversation).filter(
                Conversation.id == conversation_id,
                Conversation.organization_id == organization_id
            ).first()
            
            if not conversation:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conversation not found"
                )
            
            # Update conversation status
            conversation.status = "escalated"
            conversation.updated_at = datetime.utcnow()
            
            # Add escalation metadata
            metadata = conversation.metadata or {}
            metadata.update({
                "escalated_at": datetime.utcnow().isoformat(),
                "escalation_reason": escalation_reason,
                "escalated_to": escalate_to,
                "escalated_from": "ai_assistant"
            })
            conversation.metadata = metadata
            
            # Create escalation message
            escalation_message = Message(
                conversation_id=conversation.id,
                content=f"Conversation escalated to human agent. Reason: {escalation_reason}",
                role="system",
                metadata={
                    "escalation": True,
                    "escalation_reason": escalation_reason,
                    "escalated_to": escalate_to
                }
            )
            db.add(escalation_message)
            
            db.commit()
            
            # Send escalation notification
            await self._send_escalation_notification(
                db=db,
                conversation=conversation,
                escalation_reason=escalation_reason,
                escalate_to=escalate_to
            )
            
            logger.info(f"Escalated conversation {conversation_id}")
            
            return {
                "conversation_id": str(conversation.id),
                "status": "escalated",
                "escalated_at": datetime.utcnow().isoformat(),
                "escalation_reason": escalation_reason
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to escalate conversation: {e}")
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to escalate conversation"
            )
    
    async def route_conversation(
        self,
        db: Session,
        conversation_id: str,
        organization_id: str,
        target_assistant_id: str,
        routing_reason: str
    ) -> Dict[str, Any]:
        """
        Route conversation to different assistant
        
        Args:
            db: Database session
            conversation_id: Conversation ID
            organization_id: Organization ID
            target_assistant_id: Target assistant ID
            routing_reason: Reason for routing
            
        Returns:
            Routing result
        """
        try:
            conversation = db.query(Conversation).filter(
                Conversation.id == conversation_id,
                Conversation.organization_id == organization_id
            ).first()
            
            if not conversation:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conversation not found"
                )
            
            # Validate target assistant
            target_assistant = db.query(Assistant).filter(
                Assistant.id == target_assistant_id,
                Assistant.organization_id == organization_id
            ).first()
            
            if not target_assistant:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Target assistant not found"
                )
            
            # Store previous assistant info
            previous_assistant_id = conversation.assistant_id
            
            # Update conversation
            conversation.assistant_id = target_assistant_id
            conversation.updated_at = datetime.utcnow()
            
            # Add routing metadata
            metadata = conversation.metadata or {}
            metadata.update({
                "routed_at": datetime.utcnow().isoformat(),
                "routing_reason": routing_reason,
                "previous_assistant_id": str(previous_assistant_id),
                "routed_to_assistant_id": str(target_assistant_id)
            })
            conversation.metadata = metadata
            
            # Create routing message
            routing_message = Message(
                conversation_id=conversation.id,
                content=f"Conversation routed to {target_assistant.name}. Reason: {routing_reason}",
                role="system",
                metadata={
                    "routing": True,
                    "routing_reason": routing_reason,
                    "previous_assistant_id": str(previous_assistant_id),
                    "new_assistant_id": str(target_assistant_id)
                }
            )
            db.add(routing_message)
            
            db.commit()
            
            logger.info(f"Routed conversation {conversation_id} to assistant {target_assistant_id}")
            
            return {
                "conversation_id": str(conversation.id),
                "routed_to": {
                    "assistant_id": str(target_assistant.id),
                    "assistant_name": target_assistant.name,
                    "assistant_type": target_assistant.type
                },
                "routed_at": datetime.utcnow().isoformat(),
                "routing_reason": routing_reason
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to route conversation: {e}")
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to route conversation"
            )
    
    async def get_conversation_analytics(
        self,
        db: Session,
        organization_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        channel: Optional[str] = None,
        assistant_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get conversation analytics
        
        Args:
            db: Database session
            organization_id: Organization ID
            start_date: Start date for analytics
            end_date: End date for analytics
            channel: Filter by channel
            assistant_id: Filter by assistant
            
        Returns:
            Analytics data
        """
        try:
            # Default date range (last 30 days)
            if not start_date:
                start_date = datetime.utcnow() - timedelta(days=30)
            if not end_date:
                end_date = datetime.utcnow()
            
            # Base query
            query = db.query(Conversation).filter(
                Conversation.organization_id == organization_id,
                Conversation.created_at >= start_date,
                Conversation.created_at <= end_date
            )
            
            # Apply filters
            if channel:
                query = query.filter(
                    Conversation.metadata.op('->>')('channel') == channel
                )
            
            if assistant_id:
                query = query.filter(Conversation.assistant_id == assistant_id)
            
            conversations = query.all()
            
            # Calculate analytics
            total_conversations = len(conversations)
            
            # Status breakdown
            status_counts = {}
            for conv in conversations:
                status = conv.status
                status_counts[status] = status_counts.get(status, 0) + 1
            
            # Channel breakdown
            channel_counts = {}
            for conv in conversations:
                conv_channel = conv.metadata.get("channel", "unknown") if conv.metadata else "unknown"
                channel_counts[conv_channel] = channel_counts.get(conv_channel, 0) + 1
            
            # Average metrics
            total_messages = sum(conv.message_count for conv in conversations)
            avg_messages_per_conversation = total_messages / total_conversations if total_conversations > 0 else 0
            
            total_cost = sum(float(conv.total_cost or 0) for conv in conversations)
            avg_cost_per_conversation = total_cost / total_conversations if total_conversations > 0 else 0
            
            # Resolution metrics
            resolved_conversations = [conv for conv in conversations if conv.status in ["resolved", "archived"]]
            resolution_rate = len(resolved_conversations) / total_conversations if total_conversations > 0 else 0
            
            escalated_conversations = [conv for conv in conversations if conv.status == "escalated"]
            escalation_rate = len(escalated_conversations) / total_conversations if total_conversations > 0 else 0
            
            # Satisfaction metrics (from message feedback)
            satisfaction_scores = []
            for conv in conversations:
                messages = db.query(Message).filter(
                    Message.conversation_id == conv.id,
                    Message.feedback_rating.isnot(None)
                ).all()
                
                for msg in messages:
                    if msg.feedback_rating:
                        satisfaction_scores.append(msg.feedback_rating)
            
            avg_satisfaction = sum(satisfaction_scores) / len(satisfaction_scores) if satisfaction_scores else None
            
            return {
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "totals": {
                    "conversations": total_conversations,
                    "messages": total_messages,
                    "cost_aud": round(total_cost, 4)
                },
                "averages": {
                    "messages_per_conversation": round(avg_messages_per_conversation, 2),
                    "cost_per_conversation_aud": round(avg_cost_per_conversation, 4),
                    "satisfaction_score": round(avg_satisfaction, 2) if avg_satisfaction else None
                },
                "rates": {
                    "resolution_rate": round(resolution_rate * 100, 2),
                    "escalation_rate": round(escalation_rate * 100, 2)
                },
                "breakdowns": {
                    "by_status": status_counts,
                    "by_channel": channel_counts
                },
                "satisfaction": {
                    "average_score": round(avg_satisfaction, 2) if avg_satisfaction else None,
                    "total_ratings": len(satisfaction_scores),
                    "score_distribution": self._calculate_score_distribution(satisfaction_scores)
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get conversation analytics: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve analytics"
            )
    
    async def _format_conversation(
        self,
        db: Session,
        conversation: Conversation,
        include_analytics: bool = False
    ) -> Dict[str, Any]:
        """Format conversation for API response"""
        try:
            # Get assistant info
            assistant = db.query(Assistant).filter(
                Assistant.id == conversation.assistant_id
            ).first()
            
            # Get user info if available
            user_info = None
            if conversation.user_id:
                user = db.query(User).filter(User.id == conversation.user_id).first()
                if user:
                    user_info = {
                        "id": str(user.id),
                        "email": user.email,
                        "display_name": user.display_name
                    }
            
            # Basic conversation data
            conv_data = {
                "conversation_id": str(conversation.id),
                "title": conversation.title,
                "status": conversation.status,
                "message_count": conversation.message_count,
                "total_tokens": conversation.total_tokens,
                "total_cost_aud": float(conversation.total_cost or 0),
                "channel": conversation.metadata.get("channel") if conversation.metadata else None,
                "assistant": {
                    "id": str(assistant.id) if assistant else None,
                    "name": assistant.name if assistant else "Unknown",
                    "type": assistant.type if assistant else "unknown"
                },
                "user": user_info,
                "metadata": conversation.metadata or {},
                "created_at": conversation.created_at.isoformat(),
                "updated_at": conversation.updated_at.isoformat() if conversation.updated_at else None
            }
            
            # Add analytics if requested
            if include_analytics:
                # Get last message time
                last_message = db.query(Message).filter(
                    Message.conversation_id == conversation.id
                ).order_by(desc(Message.created_at)).first()
                
                conv_data["analytics"] = {
                    "last_message_at": last_message.created_at.isoformat() if last_message else None,
                    "duration_minutes": self._calculate_conversation_duration(conversation, last_message),
                    "escalated": conversation.status == "escalated",
                    "escalation_info": self._get_escalation_info(conversation)
                }
            
            return conv_data
            
        except Exception as e:
            logger.error(f"Failed to format conversation: {e}")
            raise
    
    async def _format_message(self, message: Message) -> Dict[str, Any]:
        """Format message for API response"""
        return {
            "message_id": str(message.id),
            "content": message.content,
            "role": message.role,
            "model": message.model,
            "tokens_input": message.tokens_input,
            "tokens_output": message.tokens_output,
            "cost_aud": float(message.cost or 0),
            "latency_ms": message.latency_ms,
            "confidence_score": message.confidence_score,
            "feedback_rating": message.feedback_rating,
            "feedback_comment": message.feedback_comment,
            "citations": message.citations or [],
            "tool_calls": message.tool_calls or [],
            "metadata": message.metadata or {},
            "created_at": message.created_at.isoformat()
        }
    
    def _calculate_conversation_duration(
        self,
        conversation: Conversation,
        last_message: Optional[Message]
    ) -> Optional[int]:
        """Calculate conversation duration in minutes"""
        if not last_message:
            return None
        
        duration = last_message.created_at - conversation.created_at
        return int(duration.total_seconds() / 60)
    
    def _get_escalation_info(self, conversation: Conversation) -> Optional[Dict[str, Any]]:
        """Get escalation information from conversation metadata"""
        if not conversation.metadata or conversation.status != "escalated":
            return None
        
        return {
            "escalated_at": conversation.metadata.get("escalated_at"),
            "escalation_reason": conversation.metadata.get("escalation_reason"),
            "escalated_to": conversation.metadata.get("escalated_to")
        }
    
    def _calculate_score_distribution(self, scores: List[int]) -> Dict[str, int]:
        """Calculate satisfaction score distribution"""
        distribution = {str(i): 0 for i in range(1, 6)}
        
        for score in scores:
            if 1 <= score <= 5:
                distribution[str(score)] += 1
        
        return distribution
    
    async def _send_escalation_notification(
        self,
        db: Session,
        conversation: Conversation,
        escalation_reason: str,
        escalate_to: Optional[str] = None
    ):
        """Send escalation notification"""
        try:
            # This would integrate with notification service
            # For now, just log the escalation
            logger.info(f"Escalation notification: Conversation {conversation.id} escalated. Reason: {escalation_reason}")
            
            # In a real implementation, this would:
            # 1. Send email notification to escalate_to user
            # 2. Create in-app notification
            # 3. Update dashboard alerts
            # 4. Potentially integrate with external systems (Slack, Teams, etc.)
            
        except Exception as e:
            logger.error(f"Failed to send escalation notification: {e}")


# Global instance
conversation_service = ConversationService()