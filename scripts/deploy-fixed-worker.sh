#!/bin/bash
set -e

echo "🚀 Deploying Fixed Cloudflare Worker (Complete Proxy)"
echo "=================================================="

# Get Cloudflare API token from Secret Manager
echo "📦 Retrieving Cloudflare API token..."
export CLOUDFLARE_API_TOKEN=$(gcloud secrets versions access latest --secret=CLOUDFLARE_API_TOKEN)

if [ -z "$CLOUDFLARE_API_TOKEN" ]; then
  echo "❌ Error: Could not retrieve CLOUDFLARE_API_TOKEN"
  exit 1
fi

echo "✅ Token retrieved"

# Deploy the new worker
echo ""
echo "🔧 Deploying anzx-complete-proxy worker..."
cd infrastructure/cloudflare

npx wrangler@latest deploy \
  --config wrangler-fixed.toml \
  --compatibility-date 2025-09-28

echo ""
echo "✅ Worker deployed successfully!"
echo ""
echo "📋 Testing the deployment..."
echo ""

# Test main site
echo "Testing main site (anzx.ai)..."
curl -sI https://anzx.ai/ | head -n 1

# Test cricket
echo "Testing cricket (anzx.ai/cricket)..."
curl -sI https://anzx.ai/cricket | head -n 1

echo ""
echo "🎉 Deployment complete!"
echo ""
echo "The new worker routes:"
echo "  • anzx.ai/* → anzx-marketing Pages"
echo "  • anzx.ai/cricket* → anzx-cricket Pages"
echo "  • anzx.ai/api/cricket* → Cricket Agent Cloud Run"
