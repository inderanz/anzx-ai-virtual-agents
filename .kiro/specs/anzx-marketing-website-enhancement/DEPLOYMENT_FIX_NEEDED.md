# Deployment Fix Required

## Current Status

✅ **Build Successful** - New teal/cyan colors deployed to Cloudflare Pages
✅ **Pages URL Working** - https://fadf9881.anzx-marketing.pages.dev/en/
❌ **Custom Domain Broken** - https://anzx.ai not working

## Problem

The Cloudflare Worker `anzx-cricket-proxy` has routes assigned that conflict with the new worker deployment:
- `anzx.ai/cricket*`
- `anzx.ai/api/cricket*`

These routes are blocking the new `anzx-complete-proxy` worker from deploying.

## Solution

### Option 1: Manual Fix (Recommended - 2 minutes)

1. Go to Cloudflare Dashboard:
   https://dash.cloudflare.com/e5e04460dc614be69eb5b8252bff5588/workers/overview

2. Find worker `anzx-cricket-proxy`

3. Click on it → Go to "Triggers" or "Routes" tab

4. Remove these routes:
   - `anzx.ai/cricket*`
   - `anzx.ai/api/cricket*`

5. Save changes

6. Run deployment:
   ```bash
   cd infrastructure/cloudflare
   npx wrangler@latest deploy
   ```

### Option 2: Automated Script

```bash
cd infrastructure/cloudflare
./fix-worker-routes.sh
```

## What Changed

### Professional Color Scheme Applied ✅
- **Old Colors**: Purple/Pink (#667eea, #764ba2, #f093fb, #4facfe, #00f2fe)
- **New Colors**: Teal/Navy (#0f172a, #1e293b, #0f766e, #0d9488, #14b8a6)

### UI/UX Improvements ✅
1. **Increased Glassmorphism**: 10% → 20% opacity
2. **Stronger Shadows**: Enhanced depth with teal glow
3. **Teal Gradient CTAs**: Maximum conversion optimization
4. **White Bold Content**: High contrast for readability

### Files Modified
- `services/anzx-marketing/components/home/HomeHero.tsx`
- `services/anzx-marketing/components/ui/Button.tsx`
- `infrastructure/cloudflare/worker-fixed.js`
- `infrastructure/cloudflare/wrangler.toml`

## After Fix

Once the worker routes are cleared and deployed:

1. **anzx.ai** will be served directly by Cloudflare Pages (custom domain)
2. **anzx.ai/cricket** will be proxied by the worker to cricket chatbot
3. **anzx.ai/api/cricket** will be proxied to Cricket Agent Cloud Run

## Verification

After deployment, test:
```bash
# Should show new teal colors
curl -s https://anzx.ai/en | grep -o "0f172a\|14b8a6\|teal-500"

# Should return 200
curl -sI https://anzx.ai/ | head -1
```

## Pipeline Fix Needed

Update `infrastructure/cloudbuild/pipelines/anzx-marketing-deploy.yaml` to:
1. Remove secret management steps (causing permission errors)
2. Simplify worker deployment
3. Make it idempotent (can run multiple times safely)
