# ANZX Marketing - Deployment Guide

## 🚀 Deployment to Cloudflare Pages via Google Cloud Build

This guide explains how to deploy the ANZX Marketing website to Cloudflare Pages using Google Cloud Build.

## Prerequisites

1. **Google Cloud Project** with Cloud Build API enabled
2. **Cloudflare Account** with Pages enabled
3. **Cloudflare API Token** with Pages permissions
4. **GitHub Repository** connected to Cloud Build

## Setup Steps

### 1. Enable Google Cloud Build API

```bash
gcloud services enable cloudbuild.googleapis.com
```

### 2. Get Cloudflare Credentials

1. Log in to Cloudflare Dashboard
2. Go to **My Profile** → **API Tokens**
3. Create a new token with **Cloudflare Pages** permissions
4. Note your **Account ID** from the dashboard

### 3. Store Secrets in Google Secret Manager

```bash
# Store Cloudflare API Token
echo -n "your-cloudflare-api-token" | gcloud secrets create cloudflare-api-token --data-file=-

# Store Cloudflare Account ID
echo -n "your-cloudflare-account-id" | gcloud secrets create cloudflare-account-id --data-file=-

# Grant Cloud Build access to secrets
gcloud secrets add-iam-policy-binding cloudflare-api-token \
  --member="serviceAccount:PROJECT_NUMBER@cloudbuild.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding cloudflare-account-id \
  --member="serviceAccount:PROJECT_NUMBER@cloudbuild.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

### 4. Create Cloud Build Trigger

```bash
gcloud builds triggers create github \
  --name="anzx-marketing-deploy" \
  --repo-name="anzx-ai-virtual-agents" \
  --repo-owner="your-github-username" \
  --branch-pattern="^main$" \
  --build-config="services/anzx-marketing/cloudbuild.yaml" \
  --substitutions='_CLOUDFLARE_API_TOKEN=$(gcloud secrets versions access latest --secret=cloudflare-api-token),_CLOUDFLARE_ACCOUNT_ID=$(gcloud secrets versions access latest --secret=cloudflare-account-id)'
```

### 5. Manual Deployment

To deploy manually:

```bash
gcloud builds submit \
  --config=services/anzx-marketing/cloudbuild.yaml \
  --substitutions=_CLOUDFLARE_API_TOKEN="your-token",_CLOUDFLARE_ACCOUNT_ID="your-account-id" \
  .
```

## Deployment Process

1. **Push to GitHub** - Push code to `main` branch
2. **Cloud Build Triggered** - Automatically starts build
3. **Install Dependencies** - `npm install`
4. **Type Check** - `npm run type-check`
5. **Lint** - `npm run lint`
6. **Build** - `npm run build`
7. **Deploy to Cloudflare** - Using Wrangler CLI

## Environment Variables

The following environment variables are set during build:

- `NEXT_PUBLIC_CORE_API_URL` - Core API endpoint
- `NEXT_PUBLIC_CHAT_WIDGET_URL` - Chat widget endpoint
- `NEXT_PUBLIC_GOOGLE_CLOUD_PROJECT` - GCP project ID

Additional variables can be set in Cloudflare Pages dashboard:

1. Go to **Pages** → **anzx-marketing** → **Settings** → **Environment Variables**
2. Add production variables:
   - `NEXT_PUBLIC_GA_MEASUREMENT_ID`
   - `NEXT_PUBLIC_CLARITY_PROJECT_ID`
   - `NEXT_PUBLIC_FIREBASE_API_KEY`
   - etc.

## Custom Domain Setup

### 1. Add Custom Domain in Cloudflare

1. Go to **Pages** → **anzx-marketing** → **Custom domains**
2. Click **Set up a custom domain**
3. Enter `anzx.ai`
4. Follow DNS configuration instructions

### 2. Configure DNS

Add the following DNS records in Cloudflare:

```
Type: CNAME
Name: anzx.ai
Target: anzx-marketing.pages.dev
Proxy: Enabled (Orange cloud)
```

### 3. SSL/TLS Configuration

1. Go to **SSL/TLS** → **Overview**
2. Set encryption mode to **Full (strict)**
3. Enable **Always Use HTTPS**
4. Enable **Automatic HTTPS Rewrites**

## Monitoring

### Build Logs

View build logs in Google Cloud Console:
```bash
gcloud builds list --limit=10
gcloud builds log BUILD_ID
```

### Deployment Status

Check deployment status in Cloudflare:
1. Go to **Pages** → **anzx-marketing** → **Deployments**
2. View deployment history and logs

### Performance Monitoring

- **Cloudflare Analytics** - Traffic and performance metrics
- **Google Analytics** - User behavior and conversions
- **Microsoft Clarity** - Session recordings and heatmaps

## Rollback

To rollback to a previous deployment:

1. Go to **Pages** → **anzx-marketing** → **Deployments**
2. Find the previous successful deployment
3. Click **...** → **Rollback to this deployment**

## Troubleshooting

### Build Fails

1. Check Cloud Build logs for errors
2. Verify all environment variables are set
3. Test build locally: `npm run build`

### Deployment Fails

1. Verify Cloudflare API token is valid
2. Check Cloudflare account ID is correct
3. Ensure Wrangler CLI is installed correctly

### Site Not Loading

1. Check DNS configuration
2. Verify custom domain is properly configured
3. Check SSL/TLS settings
4. Clear Cloudflare cache

### Performance Issues

1. Enable Cloudflare caching
2. Optimize images (use WebP/AVIF)
3. Enable Brotli compression
4. Use Cloudflare CDN

## Cost Optimization

- **Cloudflare Pages** - Free tier includes:
  - Unlimited bandwidth
  - Unlimited requests
  - 500 builds per month
  - 1 concurrent build

- **Google Cloud Build** - Free tier includes:
  - 120 build-minutes per day
  - First 10 builds per day are free

## Security

- **HTTPS Only** - All traffic encrypted
- **DDoS Protection** - Cloudflare's built-in protection
- **WAF** - Web Application Firewall (optional)
- **Rate Limiting** - Protect against abuse
- **Bot Management** - Block malicious bots

## Next Steps

1. ✅ Test deployment to staging environment
2. ✅ Configure custom domain
3. ✅ Set up monitoring and alerts
4. ✅ Enable analytics
5. ✅ Configure CDN caching rules
6. ✅ Set up automated backups
7. ✅ Document runbook for incidents

## Support

For deployment issues:
- Google Cloud Build: https://cloud.google.com/build/docs
- Cloudflare Pages: https://developers.cloudflare.com/pages
- Wrangler CLI: https://developers.cloudflare.com/workers/wrangler
