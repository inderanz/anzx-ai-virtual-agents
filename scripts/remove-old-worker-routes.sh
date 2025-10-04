#!/bin/bash

# Script to remove routes from old astro-blog-starter-template worker
# This unblocks the ANZX Marketing deployment

set -euo pipefail

PROJECT_ID="virtual-stratum-473511-u5"

echo "🔧 Removing routes from old worker..."
echo ""

# Get Cloudflare credentials from Secret Manager
echo "📥 Fetching Cloudflare credentials..."
CF_API_TOKEN=$(gcloud secrets versions access latest --secret=CLOUDFLARE_API_TOKEN --project=$PROJECT_ID)
CF_ACCOUNT_ID=$(gcloud secrets versions access latest --secret=CLOUDFLARE_ACCOUNT_ID --project=$PROJECT_ID)
CF_ZONE_ID=$(gcloud secrets versions access latest --secret=CLOUDFLARE_ZONE_ID --project=$PROJECT_ID)

echo "✅ Credentials fetched"
echo ""

# List all workers to find the old one
echo "🔍 Finding astro-blog-starter-template worker..."
WORKERS_RESPONSE=$(curl -s -X GET "https://api.cloudflare.com/client/v4/accounts/$CF_ACCOUNT_ID/workers/scripts" \
  -H "Authorization: Bearer $CF_API_TOKEN" \
  -H "Content-Type: application/json")

echo "Workers found:"
echo "$WORKERS_RESPONSE" | jq -r '.result[].id' 2>/dev/null || echo "Could not parse workers list"
echo ""

# Check if astro-blog-starter-template exists
WORKER_EXISTS=$(echo "$WORKERS_RESPONSE" | jq -r '.result[] | select(.id=="astro-blog-starter-template") | .id' 2>/dev/null || echo "")

if [ -z "$WORKER_EXISTS" ]; then
  echo "⚠️  Worker 'astro-blog-starter-template' not found in workers list"
  echo "It might have been deleted already or have a different name"
  echo ""
  echo "Available workers:"
  echo "$WORKERS_RESPONSE" | jq -r '.result[].id' 2>/dev/null || echo "Could not list workers"
  exit 0
fi

echo "✅ Found worker: astro-blog-starter-template"
echo ""

# Get routes for the zone
echo "🔍 Fetching all routes for zone..."
ROUTES_RESPONSE=$(curl -s -X GET "https://api.cloudflare.com/client/v4/zones/$CF_ZONE_ID/workers/routes" \
  -H "Authorization: Bearer $CF_API_TOKEN" \
  -H "Content-Type: application/json")

echo "Routes response:"
echo "$ROUTES_RESPONSE" | jq '.' 2>/dev/null || echo "$ROUTES_RESPONSE"
echo ""

# Find routes assigned to astro-blog-starter-template
echo "🔍 Finding routes assigned to astro-blog-starter-template..."
ROUTE_IDS=$(echo "$ROUTES_RESPONSE" | jq -r '.result[] | select(.script=="astro-blog-starter-template") | .id' 2>/dev/null || echo "")

if [ -z "$ROUTE_IDS" ]; then
  echo "✅ No routes found assigned to astro-blog-starter-template"
  echo "The worker might not have any routes, or they were already removed"
  exit 0
fi

echo "Found routes to remove:"
echo "$ROUTE_IDS"
echo ""

# Delete each route
echo "🗑️  Removing routes..."
for ROUTE_ID in $ROUTE_IDS; do
  echo "Removing route: $ROUTE_ID"
  
  DELETE_RESPONSE=$(curl -s -X DELETE "https://api.cloudflare.com/client/v4/zones/$CF_ZONE_ID/workers/routes/$ROUTE_ID" \
    -H "Authorization: Bearer $CF_API_TOKEN" \
    -H "Content-Type: application/json")
  
  SUCCESS=$(echo "$DELETE_RESPONSE" | jq -r '.success' 2>/dev/null || echo "false")
  
  if [ "$SUCCESS" = "true" ]; then
    echo "  ✅ Route $ROUTE_ID removed successfully"
  else
    echo "  ❌ Failed to remove route $ROUTE_ID"
    echo "  Response: $DELETE_RESPONSE"
  fi
done

echo ""
echo "✅ Route removal complete!"
echo ""
echo "🎯 Next steps:"
echo "1. Re-run the deployment:"
echo "   gcloud builds submit --config=infrastructure/cloudbuild/pipelines/anzx-marketing-deploy.yaml --project=$PROJECT_ID --substitutions=_PROJECT_ID=$PROJECT_ID,_REGION=australia-southeast1 ."
echo ""
echo "2. Or use the helper script:"
echo "   ./scripts/deploy-anzx-marketing.sh"
