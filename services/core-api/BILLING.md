# ANZx.ai Billing System Documentation

## Overview

The ANZx.ai platform implements a comprehensive subscription-based billing system with usage metering, Stripe integration, and automated notifications. The system supports multiple subscription tiers with usage-based overage charges and Australian tax compliance.

## Subscription Plans

### Freemium Plan
- **Price**: Free
- **Limits**: 
  - 1,000 messages/month
  - 100K tokens/month
  - 1 AI Assistant
  - 5 knowledge sources
- **Features**: Basic AI assistance, email support

### Professional Plan
- **Price**: $79 AUD/month
- **Limits**:
  - 10,000 messages/month
  - 1M tokens/month
  - 5 AI Assistants
  - 50 knowledge sources
- **Features**: Priority support, advanced analytics, custom branding

### Enterprise Plan
- **Price**: $299 AUD/month
- **Limits**:
  - 100,000 messages/month
  - 10M tokens/month
  - Unlimited AI Assistants
  - Unlimited knowledge sources
- **Features**: 24/7 support, SSO, API access, custom integrations

## Architecture

### Core Components

#### 1. Billing Configuration (`app/config/billing.py`)
- Plan definitions and pricing
- Usage limits and overage rates
- Australian tax settings (GST)
- Notification thresholds

#### 2. Stripe Service (`app/services/stripe_service.py`)
- Customer management
- Subscription lifecycle
- Payment processing
- Webhook handling
- Invoice management

#### 3. Usage Service (`app/services/usage_service.py`)
- Usage tracking and metering
- Limit enforcement
- Overage calculation
- Billing summaries

#### 4. Notification Service (`app/services/notification_service.py`)
- Usage warnings
- Payment notifications
- Billing summaries
- Welcome emails

#### 5. Usage Tracking Middleware (`app/middleware/usage_tracking.py`)
- Automatic usage metering
- Cost calculation
- Limit checking

## Usage Tracking

### Automatic Tracking

The system automatically tracks usage through middleware and service integrations:

```python
# Track AI interaction
usage_stats = await UsageTracker.track_ai_interaction(
    db=db,
    organization_id=org_id,
    tokens_input=1000,
    tokens_output=2000,
    cost=0.05,
    model="gemini-pro"
)

# Check limits before processing
limit_check = await UsageTracker.check_usage_limits(
    db=db,
    organization_id=org_id,
    required_tokens=5000
)

if not limit_check["can_proceed"]:
    raise HTTPException(status_code=429, detail="Usage limit exceeded")
```

### Usage Metrics

The system tracks the following metrics:
- **Messages**: Number of AI interactions
- **Tokens**: Input and output tokens consumed
- **Cost**: Actual cost of AI model usage
- **Conversations**: Number of chat sessions
- **API Requests**: Number of API calls

### Overage Charges

When usage exceeds plan limits, overage charges apply:
- **Messages**: $0.01 AUD per message over limit
- **Tokens**: $0.000001 AUD per token over limit

## API Endpoints

### Billing Information

```http
GET /api/v1/billing/info
Authorization: Bearer <token>
```

Returns comprehensive billing information including current usage, limits, and upcoming invoices.

### Available Plans

```http
GET /api/v1/billing/plans
```

Returns all available subscription plans with pricing and features.

### Create Subscription

```http
POST /api/v1/billing/subscribe
Authorization: Bearer <token>
Content-Type: application/json

{
  "plan": "pro"
}
```

Creates or upgrades a subscription to the specified plan.

### Change Plan

```http
PUT /api/v1/billing/subscription/plan
Authorization: Bearer <token>
Content-Type: application/json

{
  "plan": "enterprise"
}
```

Changes the current subscription plan with prorated billing.

### Cancel Subscription

```http
DELETE /api/v1/billing/subscription?at_period_end=true
Authorization: Bearer <token>
```

Cancels the subscription, optionally at the end of the current period.

### Usage Statistics

```http
GET /api/v1/billing/usage
Authorization: Bearer <token>
```

Returns detailed usage statistics and limit information.

### Invoices

```http
GET /api/v1/billing/invoices?limit=10
Authorization: Bearer <token>
```

Returns billing invoices for the organization.

## Stripe Integration

### Customer Management

Organizations are automatically mapped to Stripe customers:

```python
# Create Stripe customer
customer = await stripe_service.create_customer(
    email=user.email,
    name=organization.name,
    organization_id=str(organization.id)
)

# Update organization with Stripe customer ID
organization.stripe_customer_id = customer.id
```

### Subscription Lifecycle

1. **Creation**: Subscription created with payment intent
2. **Payment**: Customer completes payment setup
3. **Activation**: Webhook confirms successful payment
4. **Billing**: Monthly recurring billing
5. **Updates**: Plan changes with prorated billing
6. **Cancellation**: Immediate or at period end

### Webhook Handling

The system handles key Stripe webhooks:

```python
@router.post("/webhooks/stripe")
async def stripe_webhook(request: Request, stripe_signature: str):
    event = stripe_service.verify_webhook_signature(payload, signature)
    
    if event["type"] == "invoice.payment_succeeded":
        await handle_payment_succeeded(event["data"]["object"])
    elif event["type"] == "invoice.payment_failed":
        await handle_payment_failed(event["data"]["object"])
    # ... handle other events
```

Supported webhook events:
- `invoice.payment_succeeded`
- `invoice.payment_failed`
- `customer.subscription.updated`
- `customer.subscription.deleted`

## Usage Notifications

### Warning Thresholds

Automatic notifications are sent at:
- **80%** of usage limit
- **90%** of usage limit
- **95%** of usage limit
- **100%** (limit exceeded)

### Notification Types

1. **Usage Warnings**: Sent when approaching limits
2. **Limit Exceeded**: Sent when usage exceeds plan limits
3. **Payment Failed**: Sent when payment processing fails
4. **Subscription Cancelled**: Sent when subscription is cancelled
5. **Billing Summary**: Monthly usage and cost summary

### Email Templates

Notifications use structured templates:

```python
await notification_service.send_usage_warning(
    db=db,
    organization_id=org_id,
    metric="messages",
    percentage=85.0,
    current_usage=8500,
    limit=10000
)
```

## Australian Compliance

### GST (Goods and Services Tax)

- **Rate**: 10% GST applied to all Australian customers
- **Inclusion**: GST included in displayed prices
- **Reporting**: Automatic GST calculation and reporting

### Privacy and Data Protection

- **Australian Privacy Principles**: Full compliance with APP requirements
- **Data Breach Notification**: Automated NDB scheme compliance
- **Data Portability**: Export capabilities for customer data

## Development Setup

### Environment Variables

```bash
# Stripe Configuration
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_ENVIRONMENT=test

# Plan Price IDs
STRIPE_PRO_PRICE_ID=price_...
STRIPE_ENTERPRISE_PRICE_ID=price_...

# Billing Settings
BILLING_GRACE_PERIOD_DAYS=3
USAGE_RESET_DAY=1
INCLUDE_GST=true
```

### Local Testing

1. **Install Stripe CLI**:
   ```bash
   brew install stripe/stripe-cli/stripe
   stripe login
   ```

2. **Forward Webhooks**:
   ```bash
   stripe listen --forward-to localhost:8000/api/v1/billing/webhooks/stripe
   ```

3. **Test Payments**:
   ```bash
   # Use test card numbers
   # 4242424242424242 - Successful payment
   # 4000000000000002 - Declined payment
   ```

### Testing

Run billing system tests:

```bash
# Run all billing tests
python -m pytest tests/test_billing.py -v

# Run specific test class
python -m pytest tests/test_billing.py::TestBillingAPI -v

# Run with coverage
python -m pytest tests/test_billing.py --cov=app.services --cov=app.routers
```

## Production Deployment

### Stripe Configuration

1. **Create Products and Prices**:
   ```bash
   # Create Professional plan
   stripe products create --name="Professional Plan"
   stripe prices create --product=prod_... --unit-amount=7900 --currency=aud --recurring[interval]=month
   
   # Create Enterprise plan
   stripe products create --name="Enterprise Plan"
   stripe prices create --product=prod_... --unit-amount=29900 --currency=aud --recurring[interval]=month
   ```

2. **Configure Webhooks**:
   - Add webhook endpoint: `https://api.anzx.ai/api/v1/billing/webhooks/stripe`
   - Select events: `invoice.*`, `customer.subscription.*`
   - Copy webhook secret to environment variables

### Monitoring

Key metrics to monitor:
- **Subscription Growth**: New subscriptions per month
- **Churn Rate**: Subscription cancellations
- **Usage Patterns**: Average usage per plan
- **Revenue**: Monthly recurring revenue (MRR)
- **Payment Failures**: Failed payment rate

### Database Maintenance

Regular maintenance tasks:
- **Usage Reset**: Monthly usage counter reset
- **Invoice Archival**: Archive old invoices
- **Audit Log Cleanup**: Remove old audit entries
- **Usage Analytics**: Generate usage reports

## Security Considerations

### Payment Security

- **PCI Compliance**: Stripe handles all payment data
- **Webhook Verification**: All webhooks verified with signatures
- **API Keys**: Secure storage of Stripe API keys
- **Audit Logging**: All billing actions logged

### Access Control

- **Admin Only**: Billing operations require admin role
- **Organization Isolation**: Users can only access their organization's billing
- **Rate Limiting**: API endpoints protected against abuse

### Data Protection

- **Encryption**: Sensitive billing data encrypted at rest
- **Audit Trail**: Complete audit trail for compliance
- **Data Retention**: Configurable data retention policies

## Troubleshooting

### Common Issues

1. **Webhook Failures**:
   ```bash
   # Check webhook logs in Stripe dashboard
   # Verify webhook secret configuration
   # Test webhook endpoint manually
   ```

2. **Payment Failures**:
   ```bash
   # Check customer payment methods
   # Verify subscription status
   # Review failed payment notifications
   ```

3. **Usage Tracking Issues**:
   ```bash
   # Check middleware configuration
   # Verify database connections
   # Review usage service logs
   ```

### Debug Mode

Enable detailed logging:

```bash
export DEBUG=true
export LOG_LEVEL=DEBUG
```

### Health Checks

Monitor billing system health:

```http
GET /health
```

Response includes billing system status:
```json
{
  "checks": {
    "stripe": {"status": "healthy"},
    "billing_database": {"status": "healthy"},
    "usage_tracking": {"status": "healthy"}
  }
}
```

## Migration Guide

### From Free to Paid Plans

1. **Customer Creation**: Automatic Stripe customer creation
2. **Payment Setup**: Customer adds payment method
3. **Subscription Creation**: Subscription activated after payment
4. **Usage Migration**: Existing usage data preserved

### Plan Upgrades/Downgrades

1. **Immediate Effect**: Plan changes take effect immediately
2. **Prorated Billing**: Automatic proration for plan changes
3. **Usage Limits**: New limits applied immediately
4. **Feature Access**: Features enabled/disabled based on new plan

### Data Export

Organizations can export their billing data:

```http
GET /api/v1/billing/export
Authorization: Bearer <token>
```

Returns comprehensive billing history in JSON format for compliance and portability.

## Support

For billing system support:
- **Documentation**: This guide and API documentation
- **Logs**: Check application logs for detailed error information
- **Stripe Dashboard**: Monitor payments and subscriptions
- **Health Checks**: Use health endpoints to verify system status

The billing system is designed to be robust, compliant, and user-friendly while providing comprehensive usage tracking and flexible subscription management.