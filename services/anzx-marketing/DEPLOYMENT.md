# ANZX Marketing Website - Deployment Guide

## Overview

This document provides instructions for deploying the ANZX Marketing website to production at **https://anzx.ai**.

## Architecture

- **Platform**: Cloudflare Pages
- **Domain**: https://anzx.ai (root domain)
- **Cricket Chatbot**: https://anzx.ai/cricket (preserved)
- **Routing**: Cloudflare Worker handles routing between services
- **Google Cloud**: Same project as cricket deployment
- **Region**: australia-southeast1

## Prerequisites

1. **Google Cloud CLI** installed and authenticated
2. **Access** to Google Cloud project `anzx-ai-platform`
3. **Access** to Cloudflare account
4. **Secrets** configured in Google Cloud Secret Manager

## Quick Start

### 1. Verify Prerequisites

```bash
# Check gcloud is installed
gcloud --version

# Check authentication
gcloud auth list

# Verify project access
gcloud projects describe anzx-ai-platform
```

### 2. Verify Secrets

```bash
# List existing secrets (should include Cloudflare secrets from cricket)
gcloud secrets list --project=anzx-ai-platform --filter="name:CLOUDFLARE OR name:CRICKET"

# Create ANZX_MARKETING_URL secret (one-time, will be updated during deployment)
echo "https://anzx-marketing.pages.dev" | gcloud secrets create ANZX_MARKETING_URL \
  --data-file=- \
  --project=anzx-ai-platform
```

### 3. Build Locally (Optional)

```bash
# Navigate to service directory
cd services/anzx-marketing

# Install dependencies
npm install

# Build for production
npm run build

# Verify build output in 'out/' directory
ls -la out/
```

### 4. Deploy to Production

```bash
# Option 1: Use helper script (recommended)
./scripts/deploy-anzx-marketing.sh

# Option 2: Manual deployment
gcloud builds submit \
  --config=infrastructure/cloudbuild/pipelines/anzx-marketing-deploy.yaml \
  --project=anzx-ai-platform \
  --substitutions=_PROJECT_ID=anzx-ai-platform,_REGION=australia-southeast1
```

### 5. Verify Deployment

```bash
# Check deployment status
gcloud builds list --project=anzx-ai-platform --limit=5

# Visit the website
open https://anzx.ai

# Verify cricket chatbot still works
open https://anzx.ai/cricket
```

## Deployment Pipeline

The deployment pipeline (`infrastructure/cloudbuild/pipelines/anzx-marketing-deploy.yaml`) performs these steps:

1. **Build**: Compiles Next.js application
2. **Deploy to Cloudflare Pages**: Deploys to `anzx-marketing` project
3. **Update Secret**: Stores deployment URL in `ANZX_MARKETING_URL`
4. **Update Worker**: Updates Cloudflare Worker with new routing
5. **Deploy Worker**: Deploys updated worker to handle both services
6. **Write State**: Records deployment state to Cloud Storage

## Routing Logic

The Cloudflare Worker routes requests as follows:

```
/api/cricket/*  → Cricket Agent (Cloud Run)
/cricket/*      → Cricket Chatbot (Cloudflare Pages)
/*              → ANZX Marketing (Cloudflare Pages)
```

## Environment Variables

### Production Environment (`.env.production`)

```env
NEXT_PUBLIC_SITE_URL=https://anzx.ai
NEXT_PUBLIC_CORE_API_URL=https://api.anzx.ai
NEXT_PUBLIC_GA_MEASUREMENT_ID=G-XXXXXXXXXX
NEXT_PUBLIC_CLARITY_PROJECT_ID=xxxxxxxxxx
NODE_ENV=production
```

### Google Cloud Secrets

**Reused from Cricket Deployment:**
- `CLOUDFLARE_API_TOKEN` - Cloudflare API token
- `CLOUDFLARE_ACCOUNT_ID` - Cloudflare account ID
- `CLOUDFLARE_ZONE_ID` - Zone ID for anzx.ai
- `CLOUDFLARE_WORKER_NAME` - Worker name
- `CLOUDFLARE_ROUTE_PATTERN` - Route pattern
- `CRICKET_CHATBOT_URL` - Cricket chatbot deployment URL

**New for ANZX Marketing:**
- `ANZX_MARKETING_URL` - Marketing site deployment URL

## Monitoring

### Uptime Monitoring

```bash
# Configure uptime check
gcloud monitoring uptime-checks create https anzx-marketing-uptime \
  --resource-type=uptime-url \
  --host=anzx.ai \
  --path=/en \
  --project=anzx-ai-platform
```

### Error Monitoring

- **Sentry**: Configure in `.env.production`
- **Cloud Logging**: Automatic via Cloud Build
- **Cloudflare Analytics**: Available in Cloudflare dashboard

### Performance Monitoring

- **Google Analytics**: Real User Monitoring (RUM)
- **Microsoft Clarity**: Session recordings and heatmaps
- **Lighthouse CI**: Automated performance testing

## Troubleshooting

### Build Fails

```bash
# Check build logs
gcloud builds log <BUILD_ID> --project=anzx-ai-platform

# Test build locally
cd services/anzx-marketing
npm run build
```

### Deployment URL Not Captured

```bash
# Manually update secret
echo "https://your-deployment-url.anzx-marketing.pages.dev" | \
  gcloud secrets versions add ANZX_MARKETING_URL --data-file=- --project=anzx-ai-platform
```

### Worker Not Routing Correctly

```bash
# Check worker logs in Cloudflare dashboard
# Verify environment variables are set correctly
# Redeploy worker manually if needed
```

### Cricket Chatbot Stops Working

```bash
# Verify CRICKET_CHATBOT_URL secret is correct
gcloud secrets versions access latest --secret=CRICKET_CHATBOT_URL --project=anzx-ai-platform

# Rollback worker to previous version via Cloudflare dashboard
```

## Rollback

### Option 1: Rollback via Cloudflare Dashboard

1. Log into Cloudflare dashboard
2. Navigate to **Pages** > **anzx-marketing**
3. Select previous deployment
4. Click **"Rollback to this deployment"**

### Option 2: Rollback Worker

```bash
# Update worker to point to previous deployment
# Edit infrastructure/cloudflare/wrangler.toml
# Redeploy worker
cd infrastructure/cloudflare
npx wrangler deploy
```

### Option 3: Emergency Maintenance Page

```bash
# Update DNS to point to maintenance page
# Fix issues
# Redeploy when ready
```

## Performance Targets

- **LCP** (Largest Contentful Paint): < 2.5s
- **FID** (First Input Delay): < 100ms
- **CLS** (Cumulative Layout Shift): < 0.1
- **Lighthouse Score**: > 90
- **Bundle Size**: < 500KB (gzipped)

## Security

### Headers

Configured in `next.config.js`:
- Content-Security-Policy
- X-Frame-Options: SAMEORIGIN
- X-Content-Type-Options: nosniff
- Referrer-Policy: strict-origin-when-cross-origin

### Secrets Management

- Never commit secrets to git
- Use Google Cloud Secret Manager
- Rotate secrets regularly
- Use Workload Identity Federation (no service account keys)

## Support

- **Documentation**: See `.kiro/specs/anzx-marketing-website-enhancement/`
- **Deployment Checklist**: See `DEPLOYMENT_CHECKLIST.md`
- **Phase 17 Plan**: See `PHASE_17_DEPLOYMENT_PLAN.md`

## Additional Resources

- [Next.js Deployment Documentation](https://nextjs.org/docs/deployment)
- [Cloudflare Pages Documentation](https://developers.cloudflare.com/pages/)
- [Cloudflare Workers Documentation](https://developers.cloudflare.com/workers/)
- [Google Cloud Build Documentation](https://cloud.google.com/build/docs)

---

**Last Updated**: 2025-04-10
**Version**: 1.0.0
**Status**: Production Ready
