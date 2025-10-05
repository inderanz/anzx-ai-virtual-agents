#!/bin/bash

# Fix Worker Routes Script
# This script removes old worker routes and deploys the new configuration

echo "🔧 Fixing Cloudflare Worker Routes..."
echo ""
echo "MANUAL STEPS REQUIRED:"
echo "1. Go to: https://dash.cloudflare.com/e5e04460dc614be69eb5b8252bff5588/workers/overview"
echo "2. Find worker 'anzx-cricket-proxy' (if it exists)"
echo "3. Click on it → Go to 'Triggers' tab"
echo "4. Remove these routes:"
echo "   - anzx.ai/cricket*"
echo "   - anzx.ai/api/cricket*"
echo "5. Save changes"
echo ""
echo "After completing the above steps, press ENTER to deploy the new worker..."
read

echo "📦 Deploying updated worker configuration..."
npx wrangler@latest deploy

echo ""
echo "✅ Worker deployment complete!"
echo ""
echo "🧪 Testing anzx.ai..."
curl -sI https://anzx.ai/ | head -5
echo ""
echo "✅ Done! Your site should now be live at https://anzx.ai"
