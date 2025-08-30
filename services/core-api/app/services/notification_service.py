"""
Notification service for billing and usage alerts
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from ..models.user import Organization, Subscription, User
from ..config.billing import billing_config

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for sending billing and usage notifications"""
    
    def __init__(self):
        self.billing_config = billing_config
    
    async def send_usage_warning(
        self,
        db: Session,
        organization_id: str,
        metric: str,
        percentage: float,
        current_usage: int,
        limit: int
    ) -> bool:
        """
        Send usage warning notification
        
        Args:
            db: Database session
            organization_id: Organization ID
            metric: Usage metric (messages, tokens)
            percentage: Percentage of limit used
            current_usage: Current usage amount
            limit: Usage limit
            
        Returns:
            True if notification sent successfully
        """
        try:
            # Get organization and admin users
            org = db.query(Organization).filter(Organization.id == organization_id).first()
            if not org:
                return False
            
            admin_users = db.query(User).filter(
                and_(
                    User.organization_id == organization_id,
                    User.role.in_(["admin", "super_admin"]),
                    User.is_active == True
                )
            ).all()
            
            if not admin_users:
                logger.warning(f"No admin users found for organization {organization_id}")
                return False
            
            # Prepare notification data
            notification_data = {
                "organization_name": org.name,
                "metric": metric,
                "percentage": percentage,
                "current_usage": current_usage,
                "limit": limit,
                "plan": org.subscription_plan,
                "remaining": limit - current_usage if limit > current_usage else 0
            }
            
            # Send notifications to all admin users
            for user in admin_users:
                await self._send_email_notification(
                    user.email,
                    "usage_warning",
                    notification_data
                )
            
            logger.info(
                f"Usage warning sent for org {organization_id}: "
                f"{metric} at {percentage:.1f}% ({current_usage}/{limit})"
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send usage warning: {e}")
            return False
    
    async def send_usage_limit_exceeded(
        self,
        db: Session,
        organization_id: str,
        overage_details: Dict[str, Any]
    ) -> bool:
        """Send notification when usage limits are exceeded"""
        try:
            org = db.query(Organization).filter(Organization.id == organization_id).first()
            if not org:
                return False
            
            admin_users = db.query(User).filter(
                and_(
                    User.organization_id == organization_id,
                    User.role.in_(["admin", "super_admin"]),
                    User.is_active == True
                )
            ).all()
            
            notification_data = {
                "organization_name": org.name,
                "plan": org.subscription_plan,
                "overage_details": overage_details,
                "overage_cost": overage_details.get("overage_cost", 0),
                "upgrade_url": f"/billing/upgrade?org={organization_id}"
            }
            
            for user in admin_users:
                await self._send_email_notification(
                    user.email,
                    "usage_limit_exceeded",
                    notification_data
                )
            
            logger.warning(f"Usage limit exceeded notification sent for org {organization_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send usage limit exceeded notification: {e}")
            return False
    
    async def send_payment_failed(
        self,
        db: Session,
        organization_id: str,
        invoice_details: Dict[str, Any]
    ) -> bool:
        """Send notification for failed payment"""
        try:
            org = db.query(Organization).filter(Organization.id == organization_id).first()
            if not org:
                return False
            
            admin_users = db.query(User).filter(
                and_(
                    User.organization_id == organization_id,
                    User.role.in_(["admin", "super_admin"]),
                    User.is_active == True
                )
            ).all()
            
            notification_data = {
                "organization_name": org.name,
                "invoice_amount": invoice_details.get("amount_due", 0),
                "currency": invoice_details.get("currency", "aud"),
                "due_date": invoice_details.get("due_date"),
                "payment_url": f"/billing/payment?org={organization_id}",
                "grace_period_days": self.billing_config.BILLING_GRACE_PERIOD_DAYS
            }
            
            for user in admin_users:
                await self._send_email_notification(
                    user.email,
                    "payment_failed",
                    notification_data
                )
            
            logger.warning(f"Payment failed notification sent for org {organization_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send payment failed notification: {e}")
            return False
    
    async def send_subscription_cancelled(
        self,
        db: Session,
        organization_id: str,
        cancellation_details: Dict[str, Any]
    ) -> bool:
        """Send notification for subscription cancellation"""
        try:
            org = db.query(Organization).filter(Organization.id == organization_id).first()
            if not org:
                return False
            
            admin_users = db.query(User).filter(
                and_(
                    User.organization_id == organization_id,
                    User.role.in_(["admin", "super_admin"]),
                    User.is_active == True
                )
            ).all()
            
            notification_data = {
                "organization_name": org.name,
                "cancelled_plan": cancellation_details.get("plan"),
                "effective_date": cancellation_details.get("effective_date"),
                "at_period_end": cancellation_details.get("at_period_end", True),
                "reactivate_url": f"/billing/reactivate?org={organization_id}"
            }
            
            for user in admin_users:
                await self._send_email_notification(
                    user.email,
                    "subscription_cancelled",
                    notification_data
                )
            
            logger.info(f"Subscription cancelled notification sent for org {organization_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send subscription cancelled notification: {e}")
            return False
    
    async def send_billing_summary(
        self,
        db: Session,
        organization_id: str,
        billing_period: Dict[str, Any]
    ) -> bool:
        """Send monthly billing summary"""
        try:
            org = db.query(Organization).filter(Organization.id == organization_id).first()
            if not org:
                return False
            
            admin_users = db.query(User).filter(
                and_(
                    User.organization_id == organization_id,
                    User.role.in_(["admin", "super_admin"]),
                    User.is_active == True
                )
            ).all()
            
            notification_data = {
                "organization_name": org.name,
                "billing_period": billing_period,
                "plan": org.subscription_plan,
                "usage_summary": billing_period.get("usage_summary", {}),
                "total_cost": billing_period.get("total_cost", 0),
                "next_billing_date": billing_period.get("next_billing_date"),
                "billing_url": f"/billing/dashboard?org={organization_id}"
            }
            
            for user in admin_users:
                await self._send_email_notification(
                    user.email,
                    "billing_summary",
                    notification_data
                )
            
            logger.info(f"Billing summary sent for org {organization_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send billing summary: {e}")
            return False
    
    async def _send_email_notification(
        self,
        email: str,
        template: str,
        data: Dict[str, Any]
    ) -> bool:
        """
        Send email notification (placeholder implementation)
        
        In production, this would integrate with:
        - SendGrid, Mailgun, or similar email service
        - Email templates
        - Unsubscribe handling
        - Delivery tracking
        """
        try:
            # TODO: Implement actual email sending
            logger.info(f"Email notification '{template}' would be sent to {email}")
            logger.debug(f"Email data: {data}")
            
            # For now, just log the notification
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {email}: {e}")
            return False
    
    async def send_welcome_email(
        self,
        email: str,
        organization_name: str,
        plan: str
    ) -> bool:
        """Send welcome email for new subscription"""
        try:
            notification_data = {
                "organization_name": organization_name,
                "plan": plan,
                "plan_features": self.billing_config.get_plan_config(plan)["features"],
                "getting_started_url": "/getting-started",
                "support_url": "/support"
            }
            
            await self._send_email_notification(
                email,
                "welcome",
                notification_data
            )
            
            logger.info(f"Welcome email sent to {email} for plan {plan}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send welcome email: {e}")
            return False
    
    async def check_and_send_usage_warnings(self, db: Session) -> int:
        """
        Check all organizations for usage warnings and send notifications
        
        Returns:
            Number of warnings sent
        """
        warnings_sent = 0
        
        try:
            # Get all active organizations
            organizations = db.query(Organization).filter(
                Organization.subscription_status == "active"
            ).all()
            
            for org in organizations:
                try:
                    limits = self.billing_config.get_plan_limits(org.subscription_plan)
                    usage = {
                        "messages": org.monthly_message_count,
                        "tokens": org.monthly_token_count
                    }
                    
                    # Check each metric
                    for metric, used in usage.items():
                        limit = limits.get(f"{metric}_per_month", 0)
                        if limit <= 0:  # Unlimited
                            continue
                        
                        percentage = (used / limit) * 100
                        
                        # Check warning thresholds
                        for threshold in self.billing_config.USAGE_WARNING_THRESHOLDS:
                            threshold_percentage = threshold * 100
                            
                            if percentage >= threshold_percentage:
                                # Check if we've already sent this warning recently
                                # (In production, you'd track this in the database)
                                
                                await self.send_usage_warning(
                                    db, str(org.id), metric, percentage, used, limit
                                )
                                warnings_sent += 1
                                break
                
                except Exception as e:
                    logger.error(f"Failed to check warnings for org {org.id}: {e}")
                    continue
            
            return warnings_sent
            
        except Exception as e:
            logger.error(f"Failed to check usage warnings: {e}")
            return 0


# Global notification service instance
notification_service = NotificationService()