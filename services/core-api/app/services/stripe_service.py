"""
Stripe integration service for subscription management
"""

import stripe
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from fastapi import HTTPException, status

from ..config.billing import billing_config

logger = logging.getLogger(__name__)

# Configure Stripe
stripe.api_key = billing_config.STRIPE_SECRET_KEY


class StripeService:
    """Stripe integration service"""
    
    def __init__(self):
        self.api_key = billing_config.STRIPE_SECRET_KEY
        if not self.api_key:
            logger.warning("Stripe API key not configured")
    
    async def create_customer(
        self,
        email: str,
        name: str,
        organization_id: str,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Create a new Stripe customer
        
        Args:
            email: Customer email
            name: Customer name
            organization_id: Organization ID
            metadata: Additional metadata
            
        Returns:
            Stripe customer object
        """
        try:
            customer_metadata = {
                "organization_id": organization_id,
                **(metadata or {})
            }
            
            customer = stripe.Customer.create(
                email=email,
                name=name,
                metadata=customer_metadata,
                tax_exempt="none"  # Subject to GST in Australia
            )
            
            logger.info(f"Created Stripe customer: {customer.id} for org: {organization_id}")
            return customer
            
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create Stripe customer: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to create customer: {str(e)}"
            )
    
    async def get_customer(self, customer_id: str) -> Dict[str, Any]:
        """Get Stripe customer by ID"""
        try:
            customer = stripe.Customer.retrieve(customer_id)
            return customer
        except stripe.error.StripeError as e:
            logger.error(f"Failed to retrieve customer {customer_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )
    
    async def update_customer(
        self,
        customer_id: str,
        email: Optional[str] = None,
        name: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Update Stripe customer"""
        try:
            update_data = {}
            if email:
                update_data["email"] = email
            if name:
                update_data["name"] = name
            if metadata:
                update_data["metadata"] = metadata
            
            customer = stripe.Customer.modify(customer_id, **update_data)
            logger.info(f"Updated Stripe customer: {customer_id}")
            return customer
            
        except stripe.error.StripeError as e:
            logger.error(f"Failed to update customer {customer_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to update customer: {str(e)}"
            )
    
    async def create_subscription(
        self,
        customer_id: str,
        price_id: str,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Create a new subscription
        
        Args:
            customer_id: Stripe customer ID
            price_id: Stripe price ID
            metadata: Additional metadata
            
        Returns:
            Stripe subscription object
        """
        try:
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{"price": price_id}],
                metadata=metadata or {},
                payment_behavior="default_incomplete",
                payment_settings={"save_default_payment_method": "on_subscription"},
                expand=["latest_invoice.payment_intent"]
            )
            
            logger.info(f"Created subscription: {subscription.id} for customer: {customer_id}")
            return subscription
            
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create subscription: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to create subscription: {str(e)}"
            )
    
    async def get_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """Get subscription by ID"""
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            return subscription
        except stripe.error.StripeError as e:
            logger.error(f"Failed to retrieve subscription {subscription_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subscription not found"
            )
    
    async def update_subscription(
        self,
        subscription_id: str,
        price_id: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Update subscription (change plan, etc.)"""
        try:
            update_data = {}
            
            if price_id:
                # Get current subscription to update items
                subscription = stripe.Subscription.retrieve(subscription_id)
                update_data["items"] = [{
                    "id": subscription["items"]["data"][0]["id"],
                    "price": price_id
                }]
                update_data["proration_behavior"] = "create_prorations"
            
            if metadata:
                update_data["metadata"] = metadata
            
            subscription = stripe.Subscription.modify(subscription_id, **update_data)
            logger.info(f"Updated subscription: {subscription_id}")
            return subscription
            
        except stripe.error.StripeError as e:
            logger.error(f"Failed to update subscription {subscription_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to update subscription: {str(e)}"
            )
    
    async def cancel_subscription(
        self,
        subscription_id: str,
        at_period_end: bool = True
    ) -> Dict[str, Any]:
        """Cancel subscription"""
        try:
            if at_period_end:
                subscription = stripe.Subscription.modify(
                    subscription_id,
                    cancel_at_period_end=True
                )
            else:
                subscription = stripe.Subscription.delete(subscription_id)
            
            logger.info(f"Cancelled subscription: {subscription_id}")
            return subscription
            
        except stripe.error.StripeError as e:
            logger.error(f"Failed to cancel subscription {subscription_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to cancel subscription: {str(e)}"
            )
    
    async def create_usage_record(
        self,
        subscription_item_id: str,
        quantity: int,
        timestamp: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Create usage record for metered billing"""
        try:
            usage_record = stripe.UsageRecord.create(
                subscription_item=subscription_item_id,
                quantity=quantity,
                timestamp=int((timestamp or datetime.now(timezone.utc)).timestamp()),
                action="set"  # Set absolute usage
            )
            
            logger.info(f"Created usage record: {quantity} for item: {subscription_item_id}")
            return usage_record
            
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create usage record: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to record usage: {str(e)}"
            )
    
    async def get_upcoming_invoice(self, customer_id: str) -> Dict[str, Any]:
        """Get upcoming invoice for customer"""
        try:
            invoice = stripe.Invoice.upcoming(customer=customer_id)
            return invoice
        except stripe.error.StripeError as e:
            logger.error(f"Failed to get upcoming invoice for {customer_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No upcoming invoice found"
            )
    
    async def list_invoices(
        self,
        customer_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """List invoices for customer"""
        try:
            invoices = stripe.Invoice.list(
                customer=customer_id,
                limit=limit
            )
            return invoices.data
        except stripe.error.StripeError as e:
            logger.error(f"Failed to list invoices for {customer_id}: {e}")
            return []
    
    async def create_payment_intent(
        self,
        amount: int,
        currency: str = "aud",
        customer_id: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Create payment intent for one-time payments"""
        try:
            payment_intent = stripe.PaymentIntent.create(
                amount=amount,  # Amount in cents
                currency=currency,
                customer=customer_id,
                metadata=metadata or {},
                automatic_payment_methods={"enabled": True}
            )
            
            logger.info(f"Created payment intent: {payment_intent.id}")
            return payment_intent
            
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create payment intent: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to create payment: {str(e)}"
            )
    
    async def create_setup_intent(
        self,
        customer_id: str,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Create setup intent for saving payment methods"""
        try:
            setup_intent = stripe.SetupIntent.create(
                customer=customer_id,
                metadata=metadata or {},
                automatic_payment_methods={"enabled": True}
            )
            
            logger.info(f"Created setup intent: {setup_intent.id}")
            return setup_intent
            
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create setup intent: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to create setup intent: {str(e)}"
            )
    
    async def list_payment_methods(self, customer_id: str) -> List[Dict[str, Any]]:
        """List payment methods for customer"""
        try:
            payment_methods = stripe.PaymentMethod.list(
                customer=customer_id,
                type="card"
            )
            return payment_methods.data
        except stripe.error.StripeError as e:
            logger.error(f"Failed to list payment methods for {customer_id}: {e}")
            return []
    
    def verify_webhook_signature(
        self,
        payload: bytes,
        signature: str,
        webhook_secret: Optional[str] = None
    ) -> Dict[str, Any]:
        """Verify webhook signature and return event"""
        try:
            secret = webhook_secret or billing_config.STRIPE_WEBHOOK_SECRET
            event = stripe.Webhook.construct_event(payload, signature, secret)
            return event
        except ValueError as e:
            logger.error(f"Invalid webhook payload: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid payload"
            )
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid webhook signature: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid signature"
            )


# Global service instance
stripe_service = StripeService()