#!/bin/bash
set -euo pipefail

echo "🚀 Deploying Cloudflare Worker"
echo "==============================="
echo ""

# Get Cloudflare API token
echo "Getting Cloudflare API token..."
export CLOUDFLARE_API_TOKEN=$(gcloud secrets versions access latest --secret=CLOUDFLARE_API_TOKEN)

# Deploy the worker
echo "Deploying worker from infrastructure/cloudflare..."
npx wrangler@latest deploy --config infrastructure/cloudflare/wrangler.toml

echo ""
echo "✅ Worker deployed successfully!"
echo ""
echo "The worker will now route:"
echo "  - https://anzx.ai/cricket → https://d1e8b1c8.anzx-cricket.pages.dev"
echo "  - https://anzx.ai/api/cricket → Cricket Agent API"
