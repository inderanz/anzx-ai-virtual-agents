"""
Billing and subscription configuration
"""

import os
from typing import Dict, Any


class BillingConfig:
    """Billing configuration settings"""
    
    # Stripe configuration
    STRIPE_SECRET_KEY: str = os.getenv("STRIPE_SECRET_KEY", "")
    STRIPE_PUBLISHABLE_KEY: str = os.getenv("STRIPE_PUBLISHABLE_KEY", "")
    STRIPE_WEBHOOK_SECRET: str = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    
    # Environment
    STRIPE_ENVIRONMENT: str = os.getenv("STRIPE_ENVIRONMENT", "test")  # test or live
    
    # Plan configurations
    SUBSCRIPTION_PLANS: Dict[str, Dict[str, Any]] = {
        "freemium": {
            "name": "Freemium",
            "price": 0,
            "currency": "aud",
            "interval": "month",
            "stripe_price_id": None,
            "limits": {
                "messages_per_month": 1000,
                "tokens_per_month": 100000,
                "assistants": 1,
                "knowledge_sources": 5,
                "api_requests_per_minute": 10
            },
            "features": [
                "1 AI Assistant",
                "1,000 messages/month",
                "100K tokens/month",
                "5 knowledge sources",
                "Email support"
            ]
        },
        "pro": {
            "name": "Professional",
            "price": 79,  # AUD per month
            "currency": "aud",
            "interval": "month",
            "stripe_price_id": os.getenv("STRIPE_PRO_PRICE_ID"),
            "limits": {
                "messages_per_month": 10000,
                "tokens_per_month": 1000000,
                "assistants": 5,
                "knowledge_sources": 50,
                "api_requests_per_minute": 100
            },
            "features": [
                "5 AI Assistants",
                "10,000 messages/month",
                "1M tokens/month",
                "50 knowledge sources",
                "Priority support",
                "Advanced analytics",
                "Custom branding"
            ]
        },
        "enterprise": {
            "name": "Enterprise",
            "price": 299,  # AUD per month
            "currency": "aud",
            "interval": "month",
            "stripe_price_id": os.getenv("STRIPE_ENTERPRISE_PRICE_ID"),
            "limits": {
                "messages_per_month": 100000,
                "tokens_per_month": 10000000,
                "assistants": -1,  # Unlimited
                "knowledge_sources": -1,  # Unlimited
                "api_requests_per_minute": 1000
            },
            "features": [
                "Unlimited AI Assistants",
                "100,000 messages/month",
                "10M tokens/month",
                "Unlimited knowledge sources",
                "24/7 dedicated support",
                "Advanced analytics",
                "Custom branding",
                "SSO integration",
                "API access",
                "Custom integrations"
            ]
        }
    }
    
    # Usage-based pricing (overage charges)
    OVERAGE_PRICING: Dict[str, float] = {
        "messages": 0.01,  # AUD per message over limit
        "tokens": 0.000001,  # AUD per token over limit
    }
    
    # Billing settings
    BILLING_GRACE_PERIOD_DAYS: int = int(os.getenv("BILLING_GRACE_PERIOD_DAYS", "3"))
    USAGE_RESET_DAY: int = int(os.getenv("USAGE_RESET_DAY", "1"))  # Day of month to reset usage
    
    # Notification settings
    USAGE_WARNING_THRESHOLDS: list = [0.8, 0.9, 0.95]  # Warn at 80%, 90%, 95% of limit
    
    # Australian tax settings
    GST_RATE: float = 0.10  # 10% GST
    INCLUDE_GST: bool = os.getenv("INCLUDE_GST", "true").lower() == "true"
    
    @classmethod
    def get_plan_config(cls, plan_name: str) -> Dict[str, Any]:
        """Get configuration for a specific plan"""
        return cls.SUBSCRIPTION_PLANS.get(plan_name, cls.SUBSCRIPTION_PLANS["freemium"])
    
    @classmethod
    def get_plan_limits(cls, plan_name: str) -> Dict[str, int]:
        """Get usage limits for a specific plan"""
        plan = cls.get_plan_config(plan_name)
        return plan.get("limits", {})
    
    @classmethod
    def calculate_overage_cost(cls, usage: Dict[str, int], limits: Dict[str, int]) -> float:
        """Calculate overage costs"""
        total_cost = 0.0
        
        for metric, used in usage.items():
            limit = limits.get(metric, 0)
            if limit > 0 and used > limit:  # -1 means unlimited
                overage = used - limit
                rate = cls.OVERAGE_PRICING.get(metric, 0)
                total_cost += overage * rate
        
        return total_cost
    
    @classmethod
    def is_usage_over_limit(cls, usage: Dict[str, int], limits: Dict[str, int]) -> bool:
        """Check if usage exceeds limits"""
        for metric, used in usage.items():
            limit = limits.get(metric, 0)
            if limit > 0 and used > limit:  # -1 means unlimited
                return True
        return False


# Global config instance
billing_config = BillingConfig()