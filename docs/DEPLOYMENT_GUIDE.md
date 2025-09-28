# Cricket Agent Platform Deployment Guide

## Overview

This guide covers deploying the complete Cricket Agent platform to Google Cloud Platform, including the cricket-agent service, cricket-bridge service, and supporting infrastructure.

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Cricket Agent │    │  Cricket Bridge │    │   Website UI    │
│   (Cloud Run)   │    │   (Cloud Run)   │    │   (Cloud Run)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Google Cloud Platform                        │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│  │Cloud SQL    │ │Secret Mgr   │ │Cloud Storage│ │Cloud Sched  │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Prerequisites

### 1. Google Cloud Setup

```bash
# Set project ID
export PROJECT_ID="your-project-id"
export REGION="australia-southeast1"
export ENVIRONMENT="dev"

# Enable required APIs
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable sql.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable cloudscheduler.googleapis.com
gcloud services enable aiplatform.googleapis.com
gcloud services enable logging.googleapis.com
gcloud services enable monitoring.googleapis.com
```

### 2. Artifact Registry Setup

```bash
# Create Artifact Registry repository
gcloud artifacts repositories create anzx-repo \
  --repository-format=docker \
  --location=$REGION \
  --description="ANZX AI Platform Docker Images"

# Configure Docker authentication
gcloud auth configure-docker $REGION-docker.pkg.dev
```

### 3. Service Accounts

```bash
# Create service accounts
gcloud iam service-accounts create cricket-agent-sa \
  --display-name="Cricket Agent Service Account"

gcloud iam service-accounts create cricket-bridge-sa \
  --display-name="Cricket Bridge Service Account"

# Grant permissions to cricket-agent-sa
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:cricket-agent-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/cloudsql.client"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:cricket-agent-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:cricket-agent-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/storage.objectAdmin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:cricket-agent-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:cricket-agent-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/logging.logWriter"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:cricket-agent-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/monitoring.metricWriter"

# Grant permissions to cricket-bridge-sa
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:cricket-bridge-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:cricket-bridge-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/storage.objectAdmin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:cricket-bridge-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/logging.logWriter"
```

## Secrets Configuration

### 1. Create Secrets

```bash
# PlayHQ API Key
echo -n "your-playhq-api-key" | gcloud secrets create PLAYHQ_API_KEY \
  --data-file=- \
  --replication-policy="automatic"

# CSCC IDs Bundle
cat > cscc-ids.json << EOF
{
  "tenant": "ca",
  "org_id": "your-org-id",
  "season_id": "your-season-id",
  "grade_id": "your-grade-id",
  "teams": [
    {
      "name": "Caroline Springs Blue U10",
      "team_id": "your-team-id-1"
    },
    {
      "name": "Caroline Springs White U10", 
      "team_id": "your-team-id-2"
    }
  ]
}
EOF

gcloud secrets create CSCC_IDS \
  --data-file=cscc-ids.json \
  --replication-policy="automatic"

# Internal Token
echo -n "your-internal-token" | gcloud secrets create CRICKET_INTERNAL_TOKEN \
  --data-file=- \
  --replication-policy="automatic"

# Relay Token
echo -n "your-relay-token" | gcloud secrets create CRICKET_RELAY_TOKEN \
  --data-file=- \
  --replication-policy="automatic"

# PlayHQ Private Token (for private mode)
echo -n "your-playhq-private-token" | gcloud secrets create PLAYHQ_PRIVATE_TOKEN \
  --data-file=- \
  --replication-policy="automatic"

# PlayHQ Webhook Secret (for private mode)
echo -n "your-webhook-secret" | gcloud secrets create PLAYHQ_WEBHOOK_SECRET \
  --data-file=- \
  --replication-policy="automatic"
```

### 2. Grant Secret Access

```bash
# Grant cricket-agent access to secrets
gcloud secrets add-iam-policy-binding PLAYHQ_API_KEY \
  --member="serviceAccount:cricket-agent-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding CSCC_IDS \
  --member="serviceAccount:cricket-agent-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding CRICKET_INTERNAL_TOKEN \
  --member="serviceAccount:cricket-agent-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding PLAYHQ_PRIVATE_TOKEN \
  --member="serviceAccount:cricket-agent-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding PLAYHQ_WEBHOOK_SECRET \
  --member="serviceAccount:cricket-agent-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

# Grant cricket-bridge access to secrets
gcloud secrets add-iam-policy-binding CRICKET_RELAY_TOKEN \
  --member="serviceAccount:cricket-bridge-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

## Database Setup

### 1. Create Cloud SQL Instance

```bash
# Create Cloud SQL instance
gcloud sql instances create cricket-agent-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=$REGION \
  --storage-type=SSD \
  --storage-size=10GB \
  --storage-auto-increase \
  --backup \
  --enable-ip-alias \
  --network=default

# Create database
gcloud sql databases create cricket_agent \
  --instance=cricket-agent-db

# Create user
gcloud sql users create cricket_agent_user \
  --instance=cricket-agent-db \
  --password=your-db-password
```

### 2. Configure Cloud SQL Connection

```bash
# Get connection name
CONNECTION_NAME=$(gcloud sql instances describe cricket-agent-db \
  --format="value(connectionName)")

echo "Connection name: $CONNECTION_NAME"
```

## Storage Setup

### 1. Create GCS Buckets

```bash
# Create bucket for cricket data
gsutil mb gs://$PROJECT_ID-$ENVIRONMENT-cricket-data

# Create bucket for WhatsApp sessions
gsutil mb gs://$PROJECT_ID-$ENVIRONMENT-cricket-bridge-sessions

# Set bucket permissions
gsutil iam ch serviceAccount:cricket-agent-sa@$PROJECT_ID.iam.gserviceaccount.com:objectAdmin \
  gs://$PROJECT_ID-$ENVIRONMENT-cricket-data

gsutil iam ch serviceAccount:cricket-bridge-sa@$PROJECT_ID.iam.gserviceaccount.com:objectAdmin \
  gs://$PROJECT_ID-$ENVIRONMENT-cricket-bridge-sessions
```

## Cloud Build Triggers

### 1. Create Triggers

```bash
# Cricket Agent Trigger
gcloud builds triggers create github \
  --repo-name=anzx-ai-virtual-agents \
  --repo-owner=your-github-username \
  --branch-pattern="^main$" \
  --build-config=infrastructure/cloudbuild/cricket-agent.yaml \
  --substitutions=_ENVIRONMENT=$ENVIRONMENT,_REGION=$REGION,_PROJECT_ID=$PROJECT_ID,_SERVICE_ACCOUNT=cricket-agent-sa@$PROJECT_ID.iam.gserviceaccount.com,_CLOUDSQL_INSTANCE=$CONNECTION_NAME \
  --name=cricket-agent-trigger

# Cricket Bridge Trigger
gcloud builds triggers create github \
  --repo-name=anzx-ai-virtual-agents \
  --repo-owner=your-github-username \
  --branch-pattern="^main$" \
  --build-config=infrastructure/cloudbuild/cricket-bridge.yaml \
  --substitutions=_ENVIRONMENT=$ENVIRONMENT,_REGION=$REGION,_PROJECT_ID=$PROJECT_ID,_SERVICE_ACCOUNT=cricket-bridge-sa@$PROJECT_ID.iam.gserviceaccount.com,_CRICKET_AGENT_URL=https://dev-anzx-cricket-agent-xxxxx-uc.a.run.app,_RELAY_TOKEN=your-relay-token,_GCS_BUCKET=$PROJECT_ID-$ENVIRONMENT-cricket-bridge-sessions \
  --name=cricket-bridge-trigger

# PR Testing Trigger
gcloud builds triggers create github \
  --repo-name=anzx-ai-virtual-agents \
  --repo-owner=your-github-username \
  --pull-request-pattern=".*" \
  --build-config=infrastructure/cloudbuild/pr-tests.yaml \
  --substitutions=_ENVIRONMENT=$ENVIRONMENT,_REGION=$REGION,_PROJECT_ID=$PROJECT_ID \
  --name=pr-tests-trigger
```

### 2. Create PR Tests Configuration

```yaml
# infrastructure/cloudbuild/pr-tests.yaml
steps:
  # Test Cricket Agent
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'build'
      - '-t'
      - 'cricket-agent-test'
      - './services/cricket-agent'
    id: 'build-cricket-agent'

  - name: 'cricket-agent-test'
    entrypoint: 'python'
    args: ['-m', 'pytest', 'tests/', '-v']
    env:
      - 'ENVIRONMENT=test'
      - 'PLAYHQ_MODE=public'
    id: 'test-cricket-agent'
    waitFor: ['build-cricket-agent']

  # Test Cricket Bridge
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'build'
      - '-t'
      - 'cricket-bridge-test'
      - './services/cricket-bridge'
    id: 'build-cricket-bridge'

  - name: 'cricket-bridge-test'
    entrypoint: 'npm'
    args: ['test']
    env:
      - 'NODE_ENV=test'
    id: 'test-cricket-bridge'
    waitFor: ['build-cricket-bridge']

options:
  logging: CLOUD_LOGGING_ONLY
  machineType: 'E2_HIGHCPU_4'

timeout: '600s'
```

## Deployment

### 1. Manual Deployment

```bash
# Deploy Cricket Agent
gcloud builds submit \
  --config=infrastructure/cloudbuild/cricket-agent.yaml \
  --substitutions=_ENVIRONMENT=$ENVIRONMENT,_REGION=$REGION,_PROJECT_ID=$PROJECT_ID,_SERVICE_ACCOUNT=cricket-agent-sa@$PROJECT_ID.iam.gserviceaccount.com,_CLOUDSQL_INSTANCE=$CONNECTION_NAME \
  .

# Deploy Cricket Bridge
gcloud builds submit \
  --config=infrastructure/cloudbuild/cricket-bridge.yaml \
  --substitutions=_ENVIRONMENT=$ENVIRONMENT,_REGION=$REGION,_PROJECT_ID=$PROJECT_ID,_SERVICE_ACCOUNT=cricket-bridge-sa@$PROJECT_ID.iam.gserviceaccount.com,_CRICKET_AGENT_URL=https://dev-anzx-cricket-agent-xxxxx-uc.a.run.app,_RELAY_TOKEN=your-relay-token,_GCS_BUCKET=$PROJECT_ID-$ENVIRONMENT-cricket-bridge-sessions \
  .
```

### 2. Automatic Deployment

Push to main branch to trigger automatic deployment:

```bash
git add .
git commit -m "Deploy cricket agent platform"
git push origin main
```

## Cloud Scheduler Setup

### 1. Create Sync Job

```bash
# Get cricket agent URL
CRICKET_AGENT_URL=$(gcloud run services describe dev-anzx-cricket-agent \
  --region=$REGION \
  --format="value(status.url)")

# Create scheduler job
gcloud scheduler jobs create http cricket-sync-job \
  --schedule="0 2 * * *" \
  --uri="$CRICKET_AGENT_URL/internal/refresh" \
  --http-method=POST \
  --headers="Authorization=Bearer $(gcloud auth print-access-token)" \
  --body='{"scope": "all"}' \
  --time-zone="Australia/Melbourne" \
  --location=$REGION
```

### 2. Test Scheduler Job

```bash
# Run job immediately for testing
gcloud scheduler jobs run cricket-sync-job --location=$REGION
```

## Monitoring Setup

### 1. Create Alert Policies

```bash
# High latency alert
gcloud alpha monitoring policies create \
  --policy-from-file=docs/alerts/high-latency.yaml

# Error rate alert
gcloud alpha monitoring policies create \
  --policy-from-file=docs/alerts/error-rate.yaml

# Health check alert
gcloud alpha monitoring policies create \
  --policy-from-file=docs/alerts/health-checks.yaml
```

### 2. Create Dashboards

```bash
# Import dashboards
gcloud alpha monitoring dashboards create \
  --config-from-file=docs/dashboards/cricket-agent.yaml

gcloud alpha monitoring dashboards create \
  --config-from-file=docs/dashboards/cricket-bridge.yaml
```

## Verification

### 1. Health Checks

```bash
# Check cricket agent health
curl -f "$CRICKET_AGENT_URL/healthz"

# Check cricket bridge health
CRICKET_BRIDGE_URL=$(gcloud run services describe dev-anzx-cricket-bridge \
  --region=$REGION \
  --format="value(status.url)")
curl -f "$CRICKET_BRIDGE_URL/healthz"
```

### 2. Test Endpoints

```bash
# Test cricket agent query
curl -X POST "$CRICKET_AGENT_URL/v1/ask" \
  -H "Content-Type: application/json" \
  -d '{"text": "Show me the fixtures for Caroline Springs", "source": "web"}'

# Test metrics endpoint
curl "$CRICKET_AGENT_URL/metrics"

# Test cricket bridge relay
curl -X POST "$CRICKET_BRIDGE_URL/relay" \
  -H "Content-Type: application/json" \
  -H "X-Relay-Token: your-relay-token" \
  -d '{"text": "Show me the fixtures", "team_hint": "Caroline Springs"}'
```

### 3. Check Logs

```bash
# View cricket agent logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=dev-anzx-cricket-agent" --limit=50

# View cricket bridge logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=dev-anzx-cricket-bridge" --limit=50
```

## Troubleshooting

### 1. Common Issues

**Service won't start:**
- Check service account permissions
- Verify secrets are accessible
- Check Cloud SQL connection

**High latency:**
- Check Cloud SQL performance
- Review Vertex AI quotas
- Monitor resource usage

**Webhook failures:**
- Verify webhook secret
- Check private mode configuration
- Review PlayHQ webhook setup

### 2. Debug Commands

```bash
# Check service status
gcloud run services list --region=$REGION

# View service logs
gcloud logging read "resource.type=cloud_run_revision" --limit=100

# Check secrets
gcloud secrets list

# Test database connection
gcloud sql connect cricket-agent-db --user=cricket_agent_user --database=cricket_agent
```

## Cost Optimization

### 1. Resource Limits

- **Cricket Agent:** 4Gi memory, 2 CPU, max 20 instances
- **Cricket Bridge:** 2Gi memory, 1 CPU, min 1 instance, max 5 instances
- **Cloud SQL:** db-f1-micro (can be upgraded as needed)

### 2. Monitoring Costs

```bash
# Check current costs
gcloud billing budgets list

# Set up budget alerts
gcloud billing budgets create \
  --billing-account=YOUR_BILLING_ACCOUNT \
  --display-name="Cricket Agent Budget" \
  --budget-amount=100USD \
  --threshold-rule=percent=80 \
  --threshold-rule=percent=100
```

## Security Considerations

### 1. Network Security

- Services use `--no-allow-unauthenticated`
- Internal communication via service accounts
- Secrets stored in Secret Manager

### 2. Data Protection

- No PII in logs
- Encrypted data in transit and at rest
- Regular security scans

### 3. Access Control

- Service accounts with minimal permissions
- Workload Identity for secret access
- Regular permission audits

## Cloudflare Worker (Optional)

The platform supports deploying a Cloudflare Worker to proxy `/api/cricket/*` requests to the cricket-agent Cloud Run service, providing a public API endpoint.

### Prerequisites

**Required Secrets in Secret Manager:**
- `CLOUDFLARE_API_TOKEN` - Cloudflare API token
- `CLOUDFLARE_ACCOUNT_ID` - Cloudflare account ID for anzx.ai
- `CLOUDFLARE_ZONE_ID` - Zone ID for anzx.ai domain
- `CLOUDFLARE_WORKER_NAME` - Worker name (e.g., `anzx-cricket-proxy`)
- `CLOUDFLARE_ROUTE_PATTERN` - Route pattern (e.g., `anzx.ai/api/cricket*`)

### Enabling Cloudflare Worker Deployment

**Option 1: Cloud Build Trigger Configuration**
```bash
# Create trigger with Cloudflare deployment enabled
gcloud builds triggers create github \
  --repo-name=anzx-ai-virtual-agents \
  --repo-owner=your-github-username \
  --branch-pattern="^main$" \
  --build-config=infrastructure/cloudbuild/pipelines/cricket-deploy.yaml \
  --substitutions=_CLOUDFLARE_DEPLOY=true,_ENVIRONMENT=$ENVIRONMENT,_REGION=$REGION,_PROJECT_ID=$PROJECT_ID \
  --name=cricket-deploy-with-cloudflare
```

**Option 2: Manual Deployment**
```bash
# Deploy with Cloudflare Worker
gcloud builds submit \
  --config=infrastructure/cloudbuild/pipelines/cricket-deploy.yaml \
  --substitutions=_CLOUDFLARE_DEPLOY=true,_ENVIRONMENT=$ENVIRONMENT,_REGION=$REGION,_PROJECT_ID=$PROJECT_ID \
  .
```

### What the Cloudflare Worker Does

- **Proxy Requests:** Forwards `/api/cricket/*` requests to cricket-agent Cloud Run
- **CORS Support:** Handles CORS preflight requests for `https://anzx.ai`
- **Path Mapping:** Maps `/api/cricket/healthz` → `/healthz`, `/api/cricket/v1/ask` → `/v1/ask`
- **Error Handling:** Returns appropriate error responses for proxy failures

### Validation

**Test the Cloudflare Worker:**
```bash
# Health check
curl -I https://anzx.ai/api/cricket/healthz

# Cricket query
curl -X POST https://anzx.ai/api/cricket/v1/ask \
  -H 'Content-Type: application/json' \
  -d '{"text":"Show me the fixtures for Caroline Springs", "source":"web"}'

# CORS preflight
curl -X OPTIONS https://anzx.ai/api/cricket/v1/ask \
  -H 'Origin: https://anzx.ai' \
  -H 'Access-Control-Request-Method: POST' \
  -H 'Access-Control-Request-Headers: Content-Type'
```

**Expected Responses:**
- Health check: `200 OK` with CORS headers
- Cricket query: JSON response with cricket data
- CORS preflight: `204 No Content` with CORS headers

### Worker Configuration

The Worker is configured via `infrastructure/cloudflare/wrangler.toml.tmpl`:

```toml
name = "anzx-cricket-proxy"
main = "infrastructure/cloudflare/worker.js"
compatibility_date = "2025-09-28"
account_id = "your-account-id"
routes = [
  { pattern = "anzx.ai/api/cricket*", zone_id = "your-zone-id" }
]
[vars]
CRICKET_AGENT_URL = "https://cricket-agent-xxxxx-uc.a.run.app"
```

### Deployment State

When Cloudflare Worker deployment is enabled, the deployment state includes:

```json
{
  "cloudflare": {
    "worker_name": "anzx-cricket-proxy",
    "route_pattern": "anzx.ai/api/cricket*",
    "zone_id": "your-zone-id",
    "account_id": "your-account-id", 
    "wrangler_version": "3.x.x",
    "status": "deployed"
  }
}
```

### Troubleshooting

**Worker Not Deploying:**
- Check all required secrets exist in Secret Manager
- Verify `_CLOUDFLARE_DEPLOY=true` is set
- Check Cloudflare API token permissions

**Proxy Errors:**
- Verify cricket-agent Cloud Run service is healthy
- Check Worker logs in Cloudflare dashboard
- Test direct cricket-agent URL

**CORS Issues:**
- Verify Origin header is `https://anzx.ai`
- Check CORS headers in response
- Test with browser developer tools

## Next Steps

1. **Production Deployment:** Update environment variables for production
2. **Custom Domain:** Configure custom domain for services
3. **SSL Certificates:** Set up SSL certificates for HTTPS
4. **Backup Strategy:** Implement automated backups
5. **Disaster Recovery:** Create disaster recovery procedures
6. **Performance Tuning:** Optimize based on usage patterns
7. **Scaling:** Implement auto-scaling policies
8. **Monitoring:** Set up comprehensive monitoring and alerting
