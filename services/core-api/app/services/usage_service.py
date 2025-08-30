"""
Usage metering and tracking service
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from ..models.user import Organization, Subscription, Conversation, Message
from ..config.billing import billing_config
from ..services.stripe_service import stripe_service

logger = logging.getLogger(__name__)


class UsageService:
    """Service for tracking and metering usage"""
    
    def __init__(self):
        self.billing_config = billing_config
    
    async def track_message_usage(
        self,
        db: Session,
        organization_id: str,
        tokens_input: int = 0,
        tokens_output: int = 0,
        cost: float = 0.0
    ) -> Dict[str, Any]:
        """
        Track message and token usage for an organization
        
        Args:
            db: Database session
            organization_id: Organization ID
            tokens_input: Input tokens used
            tokens_output: Output tokens used
            cost: Cost of the interaction
            
        Returns:
            Updated usage statistics
        """
        try:
            # Get organization
            org = db.query(Organization).filter(Organization.id == organization_id).first()
            if not org:
                raise ValueError(f"Organization {organization_id} not found")
            
            # Update usage counters
            total_tokens = tokens_input + tokens_output
            org.monthly_message_count += 1
            org.monthly_token_count += total_tokens
            
            # Get plan limits
            limits = self.billing_config.get_plan_limits(org.subscription_plan)
            
            # Check if usage exceeds limits
            usage = {
                "messages": org.monthly_message_count,
                "tokens": org.monthly_token_count
            }
            
            over_limit = self.billing_config.is_usage_over_limit(usage, limits)
            overage_cost = self.billing_config.calculate_overage_cost(usage, limits)
            
            # Update subscription usage counters
            subscription = db.query(Subscription).filter(
                Subscription.organization_id == organization_id
            ).first()
            
            if subscription:
                if not subscription.usage_counters:
                    subscription.usage_counters = {}
                
                subscription.usage_counters.update({
                    "messages": org.monthly_message_count,
                    "tokens": org.monthly_token_count,
                    "cost": subscription.usage_counters.get("cost", 0) + cost,
                    "overage_cost": overage_cost,
                    "last_updated": datetime.utcnow().isoformat()
                })
            
            db.commit()
            
            # Check for usage warnings
            await self._check_usage_warnings(db, org, limits)
            
            return {
                "organization_id": organization_id,
                "usage": usage,
                "limits": limits,
                "over_limit": over_limit,
                "overage_cost": overage_cost,
                "percentage_used": {
                    "messages": (usage["messages"] / limits.get("messages_per_month", 1)) * 100 if limits.get("messages_per_month", 0) > 0 else 0,
                    "tokens": (usage["tokens"] / limits.get("tokens_per_month", 1)) * 100 if limits.get("tokens_per_month", 0) > 0 else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to track usage for org {organization_id}: {e}")
            db.rollback()
            raise
    
    async def get_usage_stats(
        self,
        db: Session,
        organization_id: str,
        period: str = "current"
    ) -> Dict[str, Any]:
        """
        Get usage statistics for an organization
        
        Args:
            db: Database session
            organization_id: Organization ID
            period: Period to get stats for (current, previous, all)
            
        Returns:
            Usage statistics
        """
        try:
            org = db.query(Organization).filter(Organization.id == organization_id).first()
            if not org:
                raise ValueError(f"Organization {organization_id} not found")
            
            # Get plan limits
            limits = self.billing_config.get_plan_limits(org.subscription_plan)
            
            # Current period usage
            current_usage = {
                "messages": org.monthly_message_count,
                "tokens": org.monthly_token_count
            }
            
            # Calculate costs
            overage_cost = self.billing_config.calculate_overage_cost(current_usage, limits)
            
            # Get detailed conversation stats
            conversation_stats = db.query(
                func.count(Conversation.id).label("total_conversations"),
                func.sum(Conversation.message_count).label("total_messages"),
                func.sum(Conversation.total_tokens).label("total_tokens"),
                func.sum(Conversation.total_cost).label("total_cost"),
                func.avg(Conversation.satisfaction_rating).label("avg_satisfaction")
            ).filter(
                Conversation.organization_id == organization_id
            ).first()
            
            # Get usage by assistant type
            assistant_usage = db.query(
                func.count(Conversation.id).label("conversations"),
                func.sum(Conversation.message_count).label("messages"),
                func.sum(Conversation.total_tokens).label("tokens")
            ).join(
                Organization.assistants
            ).filter(
                Organization.id == organization_id
            ).group_by("assistants.type").all()
            
            return {
                "organization_id": organization_id,
                "plan": org.subscription_plan,
                "current_usage": current_usage,
                "limits": limits,
                "overage_cost": overage_cost,
                "percentage_used": {
                    "messages": (current_usage["messages"] / limits.get("messages_per_month", 1)) * 100 if limits.get("messages_per_month", 0) > 0 else 0,
                    "tokens": (current_usage["tokens"] / limits.get("tokens_per_month", 1)) * 100 if limits.get("tokens_per_month", 0) > 0 else 0
                },
                "conversation_stats": {
                    "total_conversations": conversation_stats.total_conversations or 0,
                    "total_messages": conversation_stats.total_messages or 0,
                    "total_tokens": conversation_stats.total_tokens or 0,
                    "total_cost": float(conversation_stats.total_cost or 0),
                    "average_satisfaction": float(conversation_stats.avg_satisfaction or 0)
                },
                "assistant_usage": [
                    {
                        "type": usage.type,
                        "conversations": usage.conversations,
                        "messages": usage.messages,
                        "tokens": usage.tokens
                    }
                    for usage in assistant_usage
                ]
            }
            
        except Exception as e:
            logger.error(f"Failed to get usage stats for org {organization_id}: {e}")
            raise
    
    async def reset_monthly_usage(
        self,
        db: Session,
        organization_id: str
    ) -> Dict[str, Any]:
        """Reset monthly usage counters (called at billing cycle)"""
        try:
            org = db.query(Organization).filter(Organization.id == organization_id).first()
            if not org:
                raise ValueError(f"Organization {organization_id} not found")
            
            # Store previous usage for reporting
            previous_usage = {
                "messages": org.monthly_message_count,
                "tokens": org.monthly_token_count
            }
            
            # Reset counters
            org.monthly_message_count = 0
            org.monthly_token_count = 0
            
            # Update subscription usage counters
            subscription = db.query(Subscription).filter(
                Subscription.organization_id == organization_id
            ).first()
            
            if subscription:
                if not subscription.usage_counters:
                    subscription.usage_counters = {}
                
                subscription.usage_counters.update({
                    "previous_period": previous_usage,
                    "messages": 0,
                    "tokens": 0,
                    "cost": 0,
                    "overage_cost": 0,
                    "reset_date": datetime.utcnow().isoformat()
                })
            
            db.commit()
            
            logger.info(f"Reset usage for organization {organization_id}: {previous_usage}")
            return {
                "organization_id": organization_id,
                "previous_usage": previous_usage,
                "reset_date": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to reset usage for org {organization_id}: {e}")
            db.rollback()
            raise
    
    async def check_usage_limits(
        self,
        db: Session,
        organization_id: str
    ) -> Dict[str, Any]:
        """Check if organization has exceeded usage limits"""
        try:
            org = db.query(Organization).filter(Organization.id == organization_id).first()
            if not org:
                raise ValueError(f"Organization {organization_id} not found")
            
            limits = self.billing_config.get_plan_limits(org.subscription_plan)
            usage = {
                "messages": org.monthly_message_count,
                "tokens": org.monthly_token_count
            }
            
            # Check each limit
            limit_status = {}
            for metric, limit in limits.items():
                if limit <= 0:  # -1 means unlimited
                    limit_status[metric] = {
                        "used": usage.get(metric.replace("_per_month", ""), 0),
                        "limit": limit,
                        "percentage": 0,
                        "over_limit": False,
                        "unlimited": True
                    }
                else:
                    used = usage.get(metric.replace("_per_month", ""), 0)
                    percentage = (used / limit) * 100
                    limit_status[metric] = {
                        "used": used,
                        "limit": limit,
                        "percentage": percentage,
                        "over_limit": used > limit,
                        "unlimited": False
                    }
            
            return {
                "organization_id": organization_id,
                "plan": org.subscription_plan,
                "limit_status": limit_status,
                "any_over_limit": any(status["over_limit"] for status in limit_status.values())
            }
            
        except Exception as e:
            logger.error(f"Failed to check limits for org {organization_id}: {e}")
            raise
    
    async def _check_usage_warnings(
        self,
        db: Session,
        organization: Organization,
        limits: Dict[str, int]
    ) -> None:
        """Check if usage warnings should be sent"""
        try:
            usage = {
                "messages": organization.monthly_message_count,
                "tokens": organization.monthly_token_count
            }
            
            for metric, used in usage.items():
                limit = limits.get(f"{metric}_per_month", 0)
                if limit <= 0:  # Unlimited
                    continue
                
                percentage = (used / limit) * 100
                
                # Check warning thresholds
                for threshold in self.billing_config.USAGE_WARNING_THRESHOLDS:
                    if percentage >= threshold * 100:
                        # TODO: Send usage warning notification
                        logger.warning(
                            f"Usage warning for org {organization.id}: "
                            f"{metric} at {percentage:.1f}% ({used}/{limit})"
                        )
                        break
                        
        except Exception as e:
            logger.error(f"Failed to check usage warnings: {e}")
    
    async def get_billing_summary(
        self,
        db: Session,
        organization_id: str
    ) -> Dict[str, Any]:
        """Get comprehensive billing summary"""
        try:
            # Get usage stats
            usage_stats = await self.get_usage_stats(db, organization_id)
            
            # Get subscription info
            subscription = db.query(Subscription).filter(
                Subscription.organization_id == organization_id
            ).first()
            
            # Get upcoming invoice from Stripe
            upcoming_invoice = None
            if subscription and subscription.stripe_customer_id:
                try:
                    upcoming_invoice = await stripe_service.get_upcoming_invoice(
                        subscription.stripe_customer_id
                    )
                except Exception as e:
                    logger.warning(f"Could not get upcoming invoice: {e}")
            
            return {
                "organization_id": organization_id,
                "usage_stats": usage_stats,
                "subscription": {
                    "plan": subscription.plan if subscription else "freemium",
                    "status": subscription.status if subscription else "active",
                    "current_period_start": subscription.current_period_start.isoformat() if subscription and subscription.current_period_start else None,
                    "current_period_end": subscription.current_period_end.isoformat() if subscription and subscription.current_period_end else None,
                    "usage_counters": subscription.usage_counters if subscription else {}
                },
                "upcoming_invoice": {
                    "amount_due": upcoming_invoice.amount_due if upcoming_invoice else 0,
                    "currency": upcoming_invoice.currency if upcoming_invoice else "aud",
                    "period_start": datetime.fromtimestamp(upcoming_invoice.period_start).isoformat() if upcoming_invoice else None,
                    "period_end": datetime.fromtimestamp(upcoming_invoice.period_end).isoformat() if upcoming_invoice else None
                } if upcoming_invoice else None
            }
            
        except Exception as e:
            logger.error(f"Failed to get billing summary for org {organization_id}: {e}")
            raise


# Global service instance
usage_service = UsageService()