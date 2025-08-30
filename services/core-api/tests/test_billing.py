"""
Tests for billing and subscription system
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from app.models.database import Base, get_db
from app.models.user import Organization, User, Subscription
from app.services.stripe_service import stripe_service
from app.services.usage_service import usage_service
from app.config.billing import billing_config


# Test database setup
TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture
def db_engine():
    """Create test database engine"""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    return engine


@pytest.fixture
def db_session(db_engine):
    """Create test database session"""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def override_get_db(db_session):
    """Override database dependency"""
    def _override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def client(override_get_db):
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def sample_organization(db_session):
    """Create sample organization"""
    org = Organization(
        name="Test Organization",
        subscription_plan="freemium",
        subscription_status="active",
        monthly_message_count=500,
        monthly_token_count=50000
    )
    db_session.add(org)
    db_session.commit()
    return org


@pytest.fixture
def sample_user(db_session, sample_organization):
    """Create sample user"""
    user = User(
        firebase_uid="test-user-123",
        email="test@example.com",
        organization_id=sample_organization.id,
        role="admin"
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def sample_subscription(db_session, sample_organization):
    """Create sample subscription"""
    subscription = Subscription(
        organization_id=sample_organization.id,
        stripe_customer_id="cus_test123",
        stripe_subscription_id="sub_test123",
        plan="pro",
        status="active",
        usage_counters={"messages": 500, "tokens": 50000}
    )
    db_session.add(subscription)
    db_session.commit()
    return subscription


class TestBillingConfig:
    """Test billing configuration"""
    
    def test_get_plan_config(self):
        """Test getting plan configuration"""
        freemium_config = billing_config.get_plan_config("freemium")
        assert freemium_config["name"] == "Freemium"
        assert freemium_config["price"] == 0
        assert freemium_config["limits"]["messages_per_month"] == 1000
        
        pro_config = billing_config.get_plan_config("pro")
        assert pro_config["name"] == "Professional"
        assert pro_config["price"] == 79
        assert pro_config["limits"]["messages_per_month"] == 10000
    
    def test_get_plan_limits(self):
        """Test getting plan limits"""
        freemium_limits = billing_config.get_plan_limits("freemium")
        assert freemium_limits["messages_per_month"] == 1000
        assert freemium_limits["tokens_per_month"] == 100000
        
        enterprise_limits = billing_config.get_plan_limits("enterprise")
        assert enterprise_limits["messages_per_month"] == 100000
        assert enterprise_limits["assistants"] == -1  # Unlimited
    
    def test_calculate_overage_cost(self):
        """Test overage cost calculation"""
        usage = {"messages": 1500, "tokens": 150000}
        limits = {"messages_per_month": 1000, "tokens_per_month": 100000}
        
        overage_cost = billing_config.calculate_overage_cost(usage, limits)
        
        # 500 messages * $0.01 + 50000 tokens * $0.000001
        expected_cost = (500 * 0.01) + (50000 * 0.000001)
        assert abs(overage_cost - expected_cost) < 0.001
    
    def test_is_usage_over_limit(self):
        """Test usage limit checking"""
        usage = {"messages": 1500, "tokens": 50000}
        limits = {"messages_per_month": 1000, "tokens_per_month": 100000}
        
        assert billing_config.is_usage_over_limit(usage, limits) is True
        
        usage_under = {"messages": 500, "tokens": 50000}
        assert billing_config.is_usage_over_limit(usage_under, limits) is False


class TestStripeService:
    """Test Stripe service integration"""
    
    @patch('stripe.Customer.create')
    async def test_create_customer(self, mock_create):
        """Test creating Stripe customer"""
        mock_create.return_value = Mock(id="cus_test123", email="test@example.com")
        
        customer = await stripe_service.create_customer(
            email="test@example.com",
            name="Test Organization",
            organization_id="org-123"
        )
        
        assert customer.id == "cus_test123"
        mock_create.assert_called_once()
    
    @patch('stripe.Subscription.create')
    async def test_create_subscription(self, mock_create):
        """Test creating Stripe subscription"""
        mock_subscription = Mock(
            id="sub_test123",
            customer="cus_test123",
            status="active"
        )
        mock_create.return_value = mock_subscription
        
        subscription = await stripe_service.create_subscription(
            customer_id="cus_test123",
            price_id="price_test123"
        )
        
        assert subscription.id == "sub_test123"
        mock_create.assert_called_once()
    
    @patch('stripe.Webhook.construct_event')
    def test_verify_webhook_signature(self, mock_construct):
        """Test webhook signature verification"""
        mock_event = {"type": "invoice.payment_succeeded", "data": {}}
        mock_construct.return_value = mock_event
        
        event = stripe_service.verify_webhook_signature(
            payload=b'{"test": "data"}',
            signature="test_signature"
        )
        
        assert event["type"] == "invoice.payment_succeeded"
        mock_construct.assert_called_once()


class TestUsageService:
    """Test usage tracking service"""
    
    async def test_track_message_usage(self, db_session, sample_organization):
        """Test tracking message usage"""
        usage_stats = await usage_service.track_message_usage(
            db=db_session,
            organization_id=str(sample_organization.id),
            tokens_input=100,
            tokens_output=200,
            cost=0.05
        )
        
        assert usage_stats["organization_id"] == str(sample_organization.id)
        assert usage_stats["usage"]["messages"] == 501  # 500 + 1
        assert usage_stats["usage"]["tokens"] == 50300  # 50000 + 300
        assert usage_stats["over_limit"] is False
    
    async def test_get_usage_stats(self, db_session, sample_organization):
        """Test getting usage statistics"""
        usage_stats = await usage_service.get_usage_stats(
            db=db_session,
            organization_id=str(sample_organization.id)
        )
        
        assert usage_stats["organization_id"] == str(sample_organization.id)
        assert usage_stats["plan"] == "freemium"
        assert usage_stats["current_usage"]["messages"] == 500
        assert usage_stats["current_usage"]["tokens"] == 50000
        assert "percentage_used" in usage_stats
    
    async def test_check_usage_limits(self, db_session, sample_organization):
        """Test checking usage limits"""
        # Set usage over limit
        sample_organization.monthly_message_count = 1500
        db_session.commit()
        
        limit_status = await usage_service.check_usage_limits(
            db=db_session,
            organization_id=str(sample_organization.id)
        )
        
        assert limit_status["any_over_limit"] is True
        assert limit_status["limit_status"]["messages_per_month"]["over_limit"] is True
    
    async def test_reset_monthly_usage(self, db_session, sample_organization):
        """Test resetting monthly usage"""
        reset_result = await usage_service.reset_monthly_usage(
            db=db_session,
            organization_id=str(sample_organization.id)
        )
        
        assert reset_result["previous_usage"]["messages"] == 500
        assert reset_result["previous_usage"]["tokens"] == 50000
        
        # Check that usage was reset
        db_session.refresh(sample_organization)
        assert sample_organization.monthly_message_count == 0
        assert sample_organization.monthly_token_count == 0


class TestBillingAPI:
    """Test billing API endpoints"""
    
    def test_get_available_plans(self, client):
        """Test getting available plans"""
        response = client.get("/api/v1/billing/plans")
        assert response.status_code == 200
        
        plans = response.json()
        assert "freemium" in plans
        assert "pro" in plans
        assert "enterprise" in plans
        
        freemium = plans["freemium"]
        assert freemium["name"] == "Freemium"
        assert freemium["price"] == 0
        assert len(freemium["features"]) > 0
    
    @patch('app.auth.dependencies.get_current_user')
    async def test_get_billing_info_unauthorized(self, mock_auth, client):
        """Test getting billing info without organization"""
        mock_auth.return_value = {"user_id": "user-123", "organization_id": None}
        
        response = client.get("/api/v1/billing/info")
        assert response.status_code == 400
        assert "must belong to an organization" in response.json()["detail"]
    
    @patch('app.auth.dependencies.get_current_user')
    @patch('app.services.usage_service.usage_service.get_billing_summary')
    async def test_get_billing_info_success(self, mock_summary, mock_auth, client, sample_organization):
        """Test getting billing info successfully"""
        mock_auth.return_value = {
            "user_id": "user-123",
            "organization_id": str(sample_organization.id)
        }
        
        mock_summary.return_value = {
            "subscription": {
                "plan": "freemium",
                "status": "active",
                "current_period_start": None,
                "current_period_end": None
            },
            "usage_stats": {
                "current_usage": {"messages": 500, "tokens": 50000},
                "limits": {"messages_per_month": 1000, "tokens_per_month": 100000}
            },
            "upcoming_invoice": None
        }
        
        response = client.get("/api/v1/billing/info")
        assert response.status_code == 200
        
        billing_info = response.json()
        assert billing_info["plan"] == "freemium"
        assert billing_info["status"] == "active"
    
    @patch('app.auth.dependencies.require_admin')
    @patch('app.services.stripe_service.stripe_service.create_customer')
    @patch('app.services.stripe_service.stripe_service.create_subscription')
    async def test_create_subscription_pro(
        self, mock_create_sub, mock_create_customer, mock_auth, client, sample_organization, sample_user
    ):
        """Test creating pro subscription"""
        mock_auth.return_value = {
            "user_id": str(sample_user.id),
            "organization_id": str(sample_organization.id)
        }
        
        mock_create_customer.return_value = Mock(id="cus_test123")
        mock_create_sub.return_value = Mock(
            id="sub_test123",
            latest_invoice=Mock(
                payment_intent=Mock(client_secret="pi_test_secret")
            )
        )
        
        response = client.post("/api/v1/billing/subscribe", json={"plan": "pro"})
        assert response.status_code == 200
        
        result = response.json()
        assert result["plan"] == "pro"
        assert "subscription_id" in result
        assert "client_secret" in result
    
    @patch('app.auth.dependencies.require_admin')
    async def test_create_freemium_subscription(self, mock_auth, client, sample_organization):
        """Test creating freemium subscription"""
        mock_auth.return_value = {
            "user_id": "user-123",
            "organization_id": str(sample_organization.id)
        }
        
        response = client.post("/api/v1/billing/subscribe", json={"plan": "freemium"})
        assert response.status_code == 200
        
        result = response.json()
        assert result["plan"] == "freemium"
        assert "Subscription updated" in result["message"]


class TestUsageTracking:
    """Test usage tracking middleware and utilities"""
    
    def test_calculate_token_cost(self):
        """Test token cost calculation"""
        from app.middleware.usage_tracking import UsageTracker
        
        cost = UsageTracker.calculate_token_cost(1000, 2000, "gemini-pro")
        
        # 1000 input tokens * $0.0005/1K + 2000 output tokens * $0.0015/1K
        expected_cost = (1000 / 1000) * 0.0005 + (2000 / 1000) * 0.0015
        assert abs(cost - expected_cost) < 0.0001
    
    async def test_track_ai_interaction(self, db_session, sample_organization):
        """Test tracking AI interaction"""
        from app.middleware.usage_tracking import UsageTracker
        
        usage_stats = await UsageTracker.track_ai_interaction(
            db=db_session,
            organization_id=str(sample_organization.id),
            tokens_input=500,
            tokens_output=1000,
            cost=0.02,
            model="gemini-pro"
        )
        
        assert usage_stats["organization_id"] == str(sample_organization.id)
        assert usage_stats["usage"]["tokens"] == 51500  # 50000 + 1500
    
    async def test_check_usage_limits_within_limit(self, db_session, sample_organization):
        """Test checking usage limits when within limits"""
        from app.middleware.usage_tracking import UsageTracker
        
        limit_check = await UsageTracker.check_usage_limits(
            db=db_session,
            organization_id=str(sample_organization.id),
            required_tokens=1000
        )
        
        assert limit_check["can_proceed"] is True
        assert limit_check["required_tokens"] == 1000
    
    async def test_check_usage_limits_over_limit(self, db_session, sample_organization):
        """Test checking usage limits when over limits"""
        from app.middleware.usage_tracking import UsageTracker
        
        # Set usage over limit
        sample_organization.monthly_token_count = 150000  # Over 100K limit
        db_session.commit()
        
        limit_check = await UsageTracker.check_usage_limits(
            db=db_session,
            organization_id=str(sample_organization.id),
            required_tokens=1000
        )
        
        assert limit_check["can_proceed"] is False


class TestWebhooks:
    """Test Stripe webhook handling"""
    
    @patch('app.services.stripe_service.stripe_service.verify_webhook_signature')
    async def test_payment_succeeded_webhook(self, mock_verify, client, sample_subscription):
        """Test payment succeeded webhook"""
        mock_event = {
            "type": "invoice.payment_succeeded",
            "data": {
                "object": {
                    "customer": "cus_test123",
                    "subscription": "sub_test123",
                    "amount_paid": 7900  # $79.00 AUD
                }
            }
        }
        mock_verify.return_value = mock_event
        
        response = client.post(
            "/api/v1/billing/webhooks/stripe",
            json=mock_event,
            headers={"stripe-signature": "test_signature"}
        )
        
        assert response.status_code == 200
        assert response.json()["status"] == "success"
    
    @patch('app.services.stripe_service.stripe_service.verify_webhook_signature')
    async def test_payment_failed_webhook(self, mock_verify, client, sample_subscription):
        """Test payment failed webhook"""
        mock_event = {
            "type": "invoice.payment_failed",
            "data": {
                "object": {
                    "customer": "cus_test123",
                    "amount_due": 7900,
                    "next_payment_attempt": 1234567890
                }
            }
        }
        mock_verify.return_value = mock_event
        
        response = client.post(
            "/api/v1/billing/webhooks/stripe",
            json=mock_event,
            headers={"stripe-signature": "test_signature"}
        )
        
        assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__])