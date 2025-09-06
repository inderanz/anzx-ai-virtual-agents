"""
Conversation Dashboard Service
Provides dashboard data and insights for conversation management
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc

from ..models.user import Conversation, Message, Assistant, User, Organization

logger = logging.getLogger(__name__)


class ConversationDashboardService:
    """
    Service for generating conversation dashboard data and insights
    """
    
    async def get_dashboard_overview(
        self,
        db: Session,
        organization_id: str,
        time_period: str = "7d"
    ) -> Dict[str, Any]:
        """
        Get conversation dashboard overview
        
        Args:
            db: Database session
            organization_id: Organization ID
            time_period: Time period (1d, 7d, 30d, 90d)
            
        Returns:
            Dashboard overview data
        """
        try:
            # Calculate date range
            end_date = datetime.utcnow()
            days_map = {"1d": 1, "7d": 7, "30d": 30, "90d": 90}
            days = days_map.get(time_period, 7)
            start_date = end_date - timedelta(days=days)
            
            # Get conversations in period
            conversations = db.query(Conversation).filter(
                Conversation.organization_id == organization_id,
                Conversation.created_at >= start_date,
                Conversation.created_at <= end_date
            ).all()
            
            # Calculate metrics
            total_conversations = len(conversations)
            active_conversations = len([c for c in conversations if c.status == "active"])
            resolved_conversations = len([c for c in conversations if c.status in ["resolved", "archived"]])
            escalated_conversations = len([c for c in conversations if c.status == "escalated"])
            
            # Calculate rates
            resolution_rate = (resolved_conversations / total_conversations * 100) if total_conversations > 0 else 0
            escalation_rate = (escalated_conversations / total_conversations * 100) if total_conversations > 0 else 0
            
            # Channel breakdown
            channel_stats = {}
            for conv in conversations:
                channel = conv.metadata.get("channel", "unknown") if conv.metadata else "unknown"
                if channel not in channel_stats:
                    channel_stats[channel] = {"count": 0, "resolved": 0}
                channel_stats[channel]["count"] += 1
                if conv.status in ["resolved", "archived"]:
                    channel_stats[channel]["resolved"] += 1
            
            # Calculate channel resolution rates
            for channel in channel_stats:
                total = channel_stats[channel]["count"]
                resolved = channel_stats[channel]["resolved"]
                channel_stats[channel]["resolution_rate"] = (resolved / total * 100) if total > 0 else 0
            
            # Average metrics
            total_messages = sum(conv.message_count for conv in conversations)
            avg_messages_per_conversation = total_messages / total_conversations if total_conversations > 0 else 0
            
            total_cost = sum(float(conv.total_cost or 0) for conv in conversations)
            avg_cost_per_conversation = total_cost / total_conversations if total_conversations > 0 else 0
            
            # Response time analysis
            response_times = await self._calculate_response_times(db, conversations)
            
            # Satisfaction metrics
            satisfaction_data = await self._get_satisfaction_metrics(db, conversations)
            
            return {
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "days": days
                },
                "overview": {
                    "total_conversations": total_conversations,
                    "active_conversations": active_conversations,
                    "resolved_conversations": resolved_conversations,
                    "escalated_conversations": escalated_conversations,
                    "resolution_rate": round(resolution_rate, 1),
                    "escalation_rate": round(escalation_rate, 1)
                },
                "averages": {
                    "messages_per_conversation": round(avg_messages_per_conversation, 1),
                    "cost_per_conversation_aud": round(avg_cost_per_conversation, 4),
                    "response_time_minutes": response_times.get("average", 0)
                },
                "channels": channel_stats,
                "response_times": response_times,
                "satisfaction": satisfaction_data,
                "trends": await self._get_conversation_trends(db, organization_id, start_date, end_date)
            }
            
        except Exception as e:
            logger.error(f"Failed to get dashboard overview: {e}")
            raise
    
    async def get_active_conversations(
        self,
        db: Session,
        organization_id: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get currently active conversations requiring attention
        
        Args:
            db: Database session
            organization_id: Organization ID
            limit: Maximum results
            
        Returns:
            List of active conversations
        """
        try:
            # Get active conversations ordered by priority
            conversations = db.query(Conversation).filter(
                Conversation.organization_id == organization_id,
                Conversation.status.in_(["active", "escalated"])
            ).order_by(
                # Escalated conversations first
                desc(Conversation.status == "escalated"),
                # Then by last activity (oldest first)
                Conversation.updated_at
            ).limit(limit).all()
            
            result = []
            for conv in conversations:
                # Get last message
                last_message = db.query(Message).filter(
                    Message.conversation_id == conv.id
                ).order_by(desc(Message.created_at)).first()
                
                # Get assistant info
                assistant = db.query(Assistant).filter(
                    Assistant.id == conv.assistant_id
                ).first()
                
                # Get user info
                user_info = None
                if conv.user_id:
                    user = db.query(User).filter(User.id == conv.user_id).first()
                    if user:
                        user_info = {
                            "id": str(user.id),
                            "email": user.email,
                            "display_name": user.display_name
                        }
                
                # Calculate time since last activity
                time_since_activity = None
                if last_message:
                    delta = datetime.utcnow() - last_message.created_at
                    time_since_activity = int(delta.total_seconds() / 60)  # minutes
                
                # Determine priority
                priority = "normal"
                if conv.status == "escalated":
                    priority = "high"
                elif time_since_activity and time_since_activity > 60:  # No activity for 1 hour
                    priority = "medium"
                
                result.append({
                    "conversation_id": str(conv.id),
                    "title": conv.title,
                    "status": conv.status,
                    "priority": priority,
                    "channel": conv.metadata.get("channel") if conv.metadata else "unknown",
                    "message_count": conv.message_count,
                    "time_since_activity_minutes": time_since_activity,
                    "assistant": {
                        "id": str(assistant.id) if assistant else None,
                        "name": assistant.name if assistant else "Unknown",
                        "type": assistant.type if assistant else "unknown"
                    },
                    "user": user_info,
                    "last_message": {
                        "content": last_message.content[:100] + "..." if last_message and len(last_message.content) > 100 else last_message.content if last_message else None,
                        "role": last_message.role if last_message else None,
                        "created_at": last_message.created_at.isoformat() if last_message else None
                    },
                    "created_at": conv.created_at.isoformat(),
                    "updated_at": conv.updated_at.isoformat() if conv.updated_at else None
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to get active conversations: {e}")
            raise
    
    async def get_escalation_queue(
        self,
        db: Session,
        organization_id: str
    ) -> List[Dict[str, Any]]:
        """
        Get conversations in escalation queue
        
        Args:
            db: Database session
            organization_id: Organization ID
            
        Returns:
            List of escalated conversations
        """
        try:
            escalated_conversations = db.query(Conversation).filter(
                Conversation.organization_id == organization_id,
                Conversation.status == "escalated"
            ).order_by(Conversation.updated_at).all()
            
            result = []
            for conv in escalated_conversations:
                # Get escalation info from metadata
                escalation_info = {}
                if conv.metadata:
                    escalation_info = {
                        "escalated_at": conv.metadata.get("escalated_at"),
                        "escalation_reason": conv.metadata.get("escalation_reason"),
                        "escalated_to": conv.metadata.get("escalated_to")
                    }
                
                # Calculate escalation age
                escalation_age_minutes = None
                if escalation_info.get("escalated_at"):
                    try:
                        escalated_at = datetime.fromisoformat(escalation_info["escalated_at"])
                        delta = datetime.utcnow() - escalated_at
                        escalation_age_minutes = int(delta.total_seconds() / 60)
                    except:
                        pass
                
                # Get user info
                user_info = None
                if conv.user_id:
                    user = db.query(User).filter(User.id == conv.user_id).first()
                    if user:
                        user_info = {
                            "email": user.email,
                            "display_name": user.display_name
                        }
                
                result.append({
                    "conversation_id": str(conv.id),
                    "title": conv.title,
                    "channel": conv.metadata.get("channel") if conv.metadata else "unknown",
                    "escalation_reason": escalation_info.get("escalation_reason"),
                    "escalated_to": escalation_info.get("escalated_to"),
                    "escalation_age_minutes": escalation_age_minutes,
                    "message_count": conv.message_count,
                    "user": user_info,
                    "created_at": conv.created_at.isoformat(),
                    "escalated_at": escalation_info.get("escalated_at")
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to get escalation queue: {e}")
            raise
    
    async def get_performance_metrics(
        self,
        db: Session,
        organization_id: str,
        assistant_id: Optional[str] = None,
        time_period: str = "7d"
    ) -> Dict[str, Any]:
        """
        Get performance metrics for assistants
        
        Args:
            db: Database session
            organization_id: Organization ID
            assistant_id: Specific assistant ID (optional)
            time_period: Time period for metrics
            
        Returns:
            Performance metrics
        """
        try:
            # Calculate date range
            end_date = datetime.utcnow()
            days_map = {"1d": 1, "7d": 7, "30d": 30, "90d": 90}
            days = days_map.get(time_period, 7)
            start_date = end_date - timedelta(days=days)
            
            # Base query
            query = db.query(Conversation).filter(
                Conversation.organization_id == organization_id,
                Conversation.created_at >= start_date,
                Conversation.created_at <= end_date
            )
            
            if assistant_id:
                query = query.filter(Conversation.assistant_id == assistant_id)
            
            conversations = query.all()
            
            # Group by assistant
            assistant_metrics = {}
            
            for conv in conversations:
                asst_id = str(conv.assistant_id)
                if asst_id not in assistant_metrics:
                    # Get assistant info
                    assistant = db.query(Assistant).filter(
                        Assistant.id == conv.assistant_id
                    ).first()
                    
                    assistant_metrics[asst_id] = {
                        "assistant_id": asst_id,
                        "assistant_name": assistant.name if assistant else "Unknown",
                        "assistant_type": assistant.type if assistant else "unknown",
                        "conversations": 0,
                        "resolved": 0,
                        "escalated": 0,
                        "total_messages": 0,
                        "total_cost": 0.0,
                        "total_tokens": 0,
                        "satisfaction_scores": []
                    }
                
                metrics = assistant_metrics[asst_id]
                metrics["conversations"] += 1
                metrics["total_messages"] += conv.message_count
                metrics["total_cost"] += float(conv.total_cost or 0)
                metrics["total_tokens"] += conv.total_tokens
                
                if conv.status in ["resolved", "archived"]:
                    metrics["resolved"] += 1
                elif conv.status == "escalated":
                    metrics["escalated"] += 1
                
                # Get satisfaction scores
                messages_with_feedback = db.query(Message).filter(
                    Message.conversation_id == conv.id,
                    Message.feedback_rating.isnot(None)
                ).all()
                
                for msg in messages_with_feedback:
                    if msg.feedback_rating:
                        metrics["satisfaction_scores"].append(msg.feedback_rating)
            
            # Calculate derived metrics
            for asst_id, metrics in assistant_metrics.items():
                total_convs = metrics["conversations"]
                
                metrics["resolution_rate"] = (metrics["resolved"] / total_convs * 100) if total_convs > 0 else 0
                metrics["escalation_rate"] = (metrics["escalated"] / total_convs * 100) if total_convs > 0 else 0
                metrics["avg_messages_per_conversation"] = metrics["total_messages"] / total_convs if total_convs > 0 else 0
                metrics["avg_cost_per_conversation"] = metrics["total_cost"] / total_convs if total_convs > 0 else 0
                metrics["avg_tokens_per_conversation"] = metrics["total_tokens"] / total_convs if total_convs > 0 else 0
                
                # Satisfaction metrics
                scores = metrics["satisfaction_scores"]
                if scores:
                    metrics["avg_satisfaction"] = sum(scores) / len(scores)
                    metrics["satisfaction_count"] = len(scores)
                else:
                    metrics["avg_satisfaction"] = None
                    metrics["satisfaction_count"] = 0
                
                # Remove raw scores from output
                del metrics["satisfaction_scores"]
            
            return {
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "days": days
                },
                "assistants": list(assistant_metrics.values())
            }
            
        except Exception as e:
            logger.error(f"Failed to get performance metrics: {e}")
            raise
    
    async def _calculate_response_times(
        self,
        db: Session,
        conversations: List[Conversation]
    ) -> Dict[str, Any]:
        """Calculate response time metrics"""
        try:
            response_times = []
            
            for conv in conversations:
                # Get messages ordered by time
                messages = db.query(Message).filter(
                    Message.conversation_id == conv.id
                ).order_by(Message.created_at).all()
                
                # Calculate response times between user and assistant messages
                for i in range(len(messages) - 1):
                    current_msg = messages[i]
                    next_msg = messages[i + 1]
                    
                    # User message followed by assistant message
                    if current_msg.role == "user" and next_msg.role == "assistant":
                        delta = next_msg.created_at - current_msg.created_at
                        response_time_minutes = delta.total_seconds() / 60
                        response_times.append(response_time_minutes)
            
            if not response_times:
                return {"average": 0, "median": 0, "min": 0, "max": 0, "count": 0}
            
            response_times.sort()
            count = len(response_times)
            
            return {
                "average": round(sum(response_times) / count, 2),
                "median": round(response_times[count // 2], 2),
                "min": round(min(response_times), 2),
                "max": round(max(response_times), 2),
                "count": count
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate response times: {e}")
            return {"average": 0, "median": 0, "min": 0, "max": 0, "count": 0}
    
    async def _get_satisfaction_metrics(
        self,
        db: Session,
        conversations: List[Conversation]
    ) -> Dict[str, Any]:
        """Get satisfaction metrics"""
        try:
            all_ratings = []
            
            for conv in conversations:
                messages_with_feedback = db.query(Message).filter(
                    Message.conversation_id == conv.id,
                    Message.feedback_rating.isnot(None)
                ).all()
                
                for msg in messages_with_feedback:
                    if msg.feedback_rating:
                        all_ratings.append(msg.feedback_rating)
            
            if not all_ratings:
                return {
                    "average_rating": None,
                    "total_ratings": 0,
                    "rating_distribution": {str(i): 0 for i in range(1, 6)}
                }
            
            # Calculate distribution
            distribution = {str(i): 0 for i in range(1, 6)}
            for rating in all_ratings:
                distribution[str(rating)] += 1
            
            return {
                "average_rating": round(sum(all_ratings) / len(all_ratings), 2),
                "total_ratings": len(all_ratings),
                "rating_distribution": distribution
            }
            
        except Exception as e:
            logger.error(f"Failed to get satisfaction metrics: {e}")
            return {
                "average_rating": None,
                "total_ratings": 0,
                "rating_distribution": {str(i): 0 for i in range(1, 6)}
            }
    
    async def _get_conversation_trends(
        self,
        db: Session,
        organization_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """Get conversation trends over time"""
        try:
            # Group conversations by day
            daily_stats = {}
            
            conversations = db.query(Conversation).filter(
                Conversation.organization_id == organization_id,
                Conversation.created_at >= start_date,
                Conversation.created_at <= end_date
            ).all()
            
            # Initialize all days with zero counts
            current_date = start_date.date()
            end_date_only = end_date.date()
            
            while current_date <= end_date_only:
                daily_stats[current_date.isoformat()] = {
                    "date": current_date.isoformat(),
                    "conversations": 0,
                    "resolved": 0,
                    "escalated": 0
                }
                current_date += timedelta(days=1)
            
            # Count conversations by day
            for conv in conversations:
                date_key = conv.created_at.date().isoformat()
                if date_key in daily_stats:
                    daily_stats[date_key]["conversations"] += 1
                    
                    if conv.status in ["resolved", "archived"]:
                        daily_stats[date_key]["resolved"] += 1
                    elif conv.status == "escalated":
                        daily_stats[date_key]["escalated"] += 1
            
            # Convert to list and sort by date
            trends = list(daily_stats.values())
            trends.sort(key=lambda x: x["date"])
            
            return trends
            
        except Exception as e:
            logger.error(f"Failed to get conversation trends: {e}")
            return []


# Global instance
conversation_dashboard_service = ConversationDashboardService()