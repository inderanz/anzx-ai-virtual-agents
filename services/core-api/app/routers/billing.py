"""
Billing and subscription API endpoints
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Request, Header
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..models.database import get_db
from ..models.user import Organization, Subscription, User
from ..auth.dependencies import get_current_user, require_admin, require_organization_access
from ..services.stripe_service import stripe_service
from ..services.usage_service import usage_service
from ..config.billing import billing_config
from ..compliance.audit import compliance_auditor, AuditEventType

router = APIRouter(prefix="/api/v1/billing", tags=["billing"])


# Request/Response models
class SubscriptionPlanRequest(BaseModel):
    plan: str  # freemium, pro, enterprise


class PaymentMethodRequest(BaseModel):
    payment_method_id: str


class BillingInfoResponse(BaseModel):
    organization_id: str
    plan: str
    status: str
    current_period_start: Optional[datetime] = None
    current_period_end: Optional[datetime] = None
    usage_stats: Dict[str, Any]
    upcoming_invoice: Optional[Dict[str, Any]] = None


class UsageStatsResponse(BaseModel):
    organization_id: str
    plan: str
    current_usage: Dict[str, int]
    limits: Dict[str, int]
    percentage_used: Dict[str, float]
    overage_cost: float
    conversation_stats: Dict[str, Any]


class PlanResponse(BaseModel):
    name: str
    price: float
    currency: str
    interval: str
    limits: Dict[str, int]
    features: List[str]


class InvoiceResponse(BaseModel):
    id: str
    amount_paid: int
    amount_due: int
    currency: str
    status: str
    created: datetime
    period_start: datetime
    period_end: datetime
    hosted_invoice_url: Optional[str] = None


@router.get("/plans", response_model=Dict[str, PlanResponse])
async def get_available_plans():
    """Get all available subscription plans"""
    plans = {}
    for plan_name, plan_config in billing_config.SUBSCRIPTION_PLANS.items():
        plans[plan_name] = PlanResponse(
            name=plan_config["name"],
            price=plan_config["price"],
            currency=plan_config["currency"],
            interval=plan_config["interval"],
            limits=plan_config["limits"],
            features=plan_config["features"]
        )
    
    return plans


@router.get("/info", response_model=BillingInfoResponse)
async def get_billing_info(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get billing information for current user's organization"""
    if not current_user.get("organization_id"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must belong to an organization"
        )
    
    organization_id = current_user["organization_id"]
    
    try:
        # Get billing summary
        billing_summary = await usage_service.get_billing_summary(db, organization_id)
        
        return BillingInfoResponse(
            organization_id=organization_id,
            plan=billing_summary["subscription"]["plan"],
            status=billing_summary["subscription"]["status"],
            current_period_start=billing_summary["subscription"]["current_period_start"],
            current_period_end=billing_summary["subscription"]["current_period_end"],
            usage_stats=billing_summary["usage_stats"],
            upcoming_invoice=billing_summary["upcoming_invoice"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get billing info: {str(e)}"
        )


@router.get("/usage", response_model=UsageStatsResponse)
async def get_usage_stats(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get usage statistics for current user's organization"""
    if not current_user.get("organization_id"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must belong to an organization"
        )
    
    organization_id = current_user["organization_id"]
    
    try:
        usage_stats = await usage_service.get_usage_stats(db, organization_id)
        
        return UsageStatsResponse(
            organization_id=organization_id,
            plan=usage_stats["plan"],
            current_usage=usage_stats["current_usage"],
            limits=usage_stats["limits"],
            percentage_used=usage_stats["percentage_used"],
            overage_cost=usage_stats["overage_cost"],
            conversation_stats=usage_stats["conversation_stats"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get usage stats: {str(e)}"
        )


@router.post("/subscribe")
async def create_subscription(
    plan_request: SubscriptionPlanRequest,
    request: Request,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Create or upgrade subscription"""
    if not current_user.get("organization_id"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must belong to an organization"
        )
    
    organization_id = current_user["organization_id"]
    client_ip = _get_client_ip(request)
    
    # Validate plan
    if plan_request.plan not in billing_config.SUBSCRIPTION_PLANS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid subscription plan"
        )
    
    plan_config = billing_config.get_plan_config(plan_request.plan)
    
    # Freemium plan doesn't require Stripe
    if plan_request.plan == "freemium":
        try:
            # Update organization
            org = db.query(Organization).filter(Organization.id == organization_id).first()
            org.subscription_plan = "freemium"
            org.subscription_status = "active"
            
            # Update or create subscription record
            subscription = db.query(Subscription).filter(
                Subscription.organization_id == organization_id
            ).first()
            
            if not subscription:
                subscription = Subscription(
                    organization_id=organization_id,
                    stripe_customer_id="",
                    plan="freemium",
                    status="active"
                )
                db.add(subscription)
            else:
                subscription.plan = "freemium"
                subscription.status = "active"
            
            db.commit()
            
            # Log subscription change
            compliance_auditor.log_event(
                event_type=AuditEventType.DATA_ACCESS,
                action="subscription_changed",
                outcome="success",
                user_id=current_user["user_id"],
                ip_address=client_ip,
                details={
                    "organization_id": organization_id,
                    "new_plan": "freemium",
                    "previous_plan": subscription.plan if subscription else None
                }
            )
            
            return {"message": "Subscription updated to freemium", "plan": "freemium"}
            
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update subscription: {str(e)}"
            )
    
    # Paid plans require Stripe integration
    try:
        # Get organization
        org = db.query(Organization).filter(Organization.id == organization_id).first()
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )
        
        # Get or create Stripe customer
        stripe_customer_id = org.stripe_customer_id
        if not stripe_customer_id:
            # Create Stripe customer
            user = db.query(User).filter(User.id == current_user["user_id"]).first()
            customer = await stripe_service.create_customer(
                email=user.email,
                name=org.name,
                organization_id=organization_id,
                metadata={"plan": plan_request.plan}
            )
            stripe_customer_id = customer.id
            org.stripe_customer_id = stripe_customer_id
        
        # Create Stripe subscription
        stripe_subscription = await stripe_service.create_subscription(
            customer_id=stripe_customer_id,
            price_id=plan_config["stripe_price_id"],
            metadata={
                "organization_id": organization_id,
                "plan": plan_request.plan
            }
        )
        
        # Update organization
        org.subscription_plan = plan_request.plan
        org.subscription_status = "pending"  # Will be updated by webhook
        
        # Update or create subscription record
        subscription = db.query(Subscription).filter(
            Subscription.organization_id == organization_id
        ).first()
        
        if not subscription:
            subscription = Subscription(
                organization_id=organization_id,
                stripe_customer_id=stripe_customer_id,
                stripe_subscription_id=stripe_subscription.id,
                stripe_price_id=plan_config["stripe_price_id"],
                plan=plan_request.plan,
                status="pending"
            )
            db.add(subscription)
        else:
            subscription.stripe_subscription_id = stripe_subscription.id
            subscription.stripe_price_id = plan_config["stripe_price_id"]
            subscription.plan = plan_request.plan
            subscription.status = "pending"
        
        db.commit()
        
        # Log subscription creation
        compliance_auditor.log_event(
            event_type=AuditEventType.DATA_ACCESS,
            action="subscription_created",
            outcome="success",
            user_id=current_user["user_id"],
            ip_address=client_ip,
            details={
                "organization_id": organization_id,
                "plan": plan_request.plan,
                "stripe_subscription_id": stripe_subscription.id
            }
        )
        
        return {
            "message": "Subscription created",
            "subscription_id": stripe_subscription.id,
            "client_secret": stripe_subscription.latest_invoice.payment_intent.client_secret,
            "plan": plan_request.plan
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create subscription: {str(e)}"
        )


@router.put("/subscription/plan")
async def change_subscription_plan(
    plan_request: SubscriptionPlanRequest,
    request: Request,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Change subscription plan"""
    if not current_user.get("organization_id"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must belong to an organization"
        )
    
    organization_id = current_user["organization_id"]
    client_ip = _get_client_ip(request)
    
    # Validate plan
    if plan_request.plan not in billing_config.SUBSCRIPTION_PLANS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid subscription plan"
        )
    
    try:
        subscription = db.query(Subscription).filter(
            Subscription.organization_id == organization_id
        ).first()
        
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No subscription found"
            )
        
        plan_config = billing_config.get_plan_config(plan_request.plan)
        previous_plan = subscription.plan
        
        # Handle downgrade to freemium
        if plan_request.plan == "freemium":
            if subscription.stripe_subscription_id:
                # Cancel Stripe subscription
                await stripe_service.cancel_subscription(
                    subscription.stripe_subscription_id,
                    at_period_end=True
                )
            
            subscription.plan = "freemium"
            subscription.status = "active"
        else:
            # Update Stripe subscription
            if subscription.stripe_subscription_id:
                await stripe_service.update_subscription(
                    subscription.stripe_subscription_id,
                    price_id=plan_config["stripe_price_id"],
                    metadata={
                        "organization_id": organization_id,
                        "plan": plan_request.plan
                    }
                )
            
            subscription.plan = plan_request.plan
            subscription.stripe_price_id = plan_config["stripe_price_id"]
        
        # Update organization
        org = db.query(Organization).filter(Organization.id == organization_id).first()
        org.subscription_plan = plan_request.plan
        
        db.commit()
        
        # Log plan change
        compliance_auditor.log_event(
            event_type=AuditEventType.DATA_ACCESS,
            action="subscription_plan_changed",
            outcome="success",
            user_id=current_user["user_id"],
            ip_address=client_ip,
            details={
                "organization_id": organization_id,
                "previous_plan": previous_plan,
                "new_plan": plan_request.plan
            }
        )
        
        return {
            "message": "Subscription plan updated",
            "plan": plan_request.plan,
            "previous_plan": previous_plan
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to change subscription plan: {str(e)}"
        )


@router.delete("/subscription")
async def cancel_subscription(
    request: Request,
    at_period_end: bool = True,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Cancel subscription"""
    if not current_user.get("organization_id"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must belong to an organization"
        )
    
    organization_id = current_user["organization_id"]
    client_ip = _get_client_ip(request)
    
    try:
        subscription = db.query(Subscription).filter(
            Subscription.organization_id == organization_id
        ).first()
        
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No subscription found"
            )
        
        # Cancel Stripe subscription if exists
        if subscription.stripe_subscription_id:
            await stripe_service.cancel_subscription(
                subscription.stripe_subscription_id,
                at_period_end=at_period_end
            )
        
        # Update subscription status
        subscription.status = "cancelled" if not at_period_end else "cancel_at_period_end"
        
        # Update organization to freemium if immediate cancellation
        if not at_period_end:
            org = db.query(Organization).filter(Organization.id == organization_id).first()
            org.subscription_plan = "freemium"
            org.subscription_status = "active"
        
        db.commit()
        
        # Log cancellation
        compliance_auditor.log_event(
            event_type=AuditEventType.DATA_ACCESS,
            action="subscription_cancelled",
            outcome="success",
            user_id=current_user["user_id"],
            ip_address=client_ip,
            details={
                "organization_id": organization_id,
                "at_period_end": at_period_end,
                "plan": subscription.plan
            }
        )
        
        return {
            "message": "Subscription cancelled",
            "at_period_end": at_period_end,
            "status": subscription.status
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel subscription: {str(e)}"
        )


@router.get("/invoices", response_model=List[InvoiceResponse])
async def get_invoices(
    limit: int = 10,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get billing invoices"""
    if not current_user.get("organization_id"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must belong to an organization"
        )
    
    organization_id = current_user["organization_id"]
    
    try:
        subscription = db.query(Subscription).filter(
            Subscription.organization_id == organization_id
        ).first()
        
        if not subscription or not subscription.stripe_customer_id:
            return []
        
        # Get invoices from Stripe
        invoices = await stripe_service.list_invoices(
            subscription.stripe_customer_id,
            limit=limit
        )
        
        return [
            InvoiceResponse(
                id=invoice.id,
                amount_paid=invoice.amount_paid,
                amount_due=invoice.amount_due,
                currency=invoice.currency,
                status=invoice.status,
                created=datetime.fromtimestamp(invoice.created),
                period_start=datetime.fromtimestamp(invoice.period_start),
                period_end=datetime.fromtimestamp(invoice.period_end),
                hosted_invoice_url=invoice.hosted_invoice_url
            )
            for invoice in invoices
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get invoices: {str(e)}"
        )


@router.post("/webhooks/stripe")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None, alias="stripe-signature"),
    db: Session = Depends(get_db)
):
    """Handle Stripe webhooks"""
    try:
        payload = await request.body()
        
        # Verify webhook signature
        event = stripe_service.verify_webhook_signature(payload, stripe_signature)
        
        # Handle different event types
        if event["type"] == "invoice.payment_succeeded":
            await _handle_payment_succeeded(db, event["data"]["object"])
        elif event["type"] == "invoice.payment_failed":
            await _handle_payment_failed(db, event["data"]["object"])
        elif event["type"] == "customer.subscription.updated":
            await _handle_subscription_updated(db, event["data"]["object"])
        elif event["type"] == "customer.subscription.deleted":
            await _handle_subscription_deleted(db, event["data"]["object"])
        
        return {"status": "success"}
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Webhook processing failed"
        )


async def _handle_payment_succeeded(db: Session, invoice: Dict[str, Any]):
    """Handle successful payment"""
    try:
        customer_id = invoice["customer"]
        subscription_id = invoice["subscription"]
        
        # Find subscription
        subscription = db.query(Subscription).filter(
            Subscription.stripe_customer_id == customer_id
        ).first()
        
        if subscription:
            subscription.status = "active"
            
            # Update organization
            org = db.query(Organization).filter(
                Organization.id == subscription.organization_id
            ).first()
            if org:
                org.subscription_status = "active"
            
            db.commit()
            logger.info(f"Payment succeeded for subscription {subscription_id}")
        
    except Exception as e:
        logger.error(f"Failed to handle payment succeeded: {e}")
        db.rollback()


async def _handle_payment_failed(db: Session, invoice: Dict[str, Any]):
    """Handle failed payment"""
    try:
        customer_id = invoice["customer"]
        
        # Find subscription
        subscription = db.query(Subscription).filter(
            Subscription.stripe_customer_id == customer_id
        ).first()
        
        if subscription:
            subscription.status = "past_due"
            
            # Update organization
            org = db.query(Organization).filter(
                Organization.id == subscription.organization_id
            ).first()
            if org:
                org.subscription_status = "past_due"
            
            db.commit()
            logger.warning(f"Payment failed for customer {customer_id}")
        
    except Exception as e:
        logger.error(f"Failed to handle payment failed: {e}")
        db.rollback()


async def _handle_subscription_updated(db: Session, subscription_data: Dict[str, Any]):
    """Handle subscription update"""
    try:
        stripe_subscription_id = subscription_data["id"]
        status = subscription_data["status"]
        
        # Find subscription
        subscription = db.query(Subscription).filter(
            Subscription.stripe_subscription_id == stripe_subscription_id
        ).first()
        
        if subscription:
            subscription.status = status
            subscription.current_period_start = datetime.fromtimestamp(
                subscription_data["current_period_start"]
            )
            subscription.current_period_end = datetime.fromtimestamp(
                subscription_data["current_period_end"]
            )
            
            # Update organization
            org = db.query(Organization).filter(
                Organization.id == subscription.organization_id
            ).first()
            if org:
                org.subscription_status = status
            
            db.commit()
            logger.info(f"Subscription updated: {stripe_subscription_id} -> {status}")
        
    except Exception as e:
        logger.error(f"Failed to handle subscription updated: {e}")
        db.rollback()


async def _handle_subscription_deleted(db: Session, subscription_data: Dict[str, Any]):
    """Handle subscription deletion"""
    try:
        stripe_subscription_id = subscription_data["id"]
        
        # Find subscription
        subscription = db.query(Subscription).filter(
            Subscription.stripe_subscription_id == stripe_subscription_id
        ).first()
        
        if subscription:
            subscription.status = "cancelled"
            
            # Downgrade organization to freemium
            org = db.query(Organization).filter(
                Organization.id == subscription.organization_id
            ).first()
            if org:
                org.subscription_plan = "freemium"
                org.subscription_status = "active"
            
            db.commit()
            logger.info(f"Subscription deleted: {stripe_subscription_id}")
        
    except Exception as e:
        logger.error(f"Failed to handle subscription deleted: {e}")
        db.rollback()


def _get_client_ip(request: Request) -> str:
    """Get client IP address from request"""
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    return request.client.host if request.client else "unknown"