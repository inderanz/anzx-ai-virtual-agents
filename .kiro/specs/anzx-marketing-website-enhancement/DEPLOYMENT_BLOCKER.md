# 🚨 Deployment Blocker - Route Conflict

## Status: ACTION REQUIRED

The ANZX Marketing deployment is blocked by a route conflict in Cloudflare.

## Issue

**Error from Cloud Build**:
```
✘ [ERROR] Can't deploy routes that are assigned to another worker.

"astro-blog-starter-template" is already assigned to routes:
  - anzx.ai/*

Unassign other workers from the routes you want to deploy to, and then try again.
```

## Root Cause

There's an old Cloudflare Worker named `astro-blog-starter-template` that's currently assigned to the `anzx.ai/*` route. This conflicts with our new worker (`anzx-cricket-proxy`) which needs to handle routing for both:
- Cricket chatbot: `anzx.ai/cricket*`
- ANZX Marketing: `anzx.ai/*`

## Solution Required

### Option 1: Remove Old Worker Routes (Recommended)

1. **Go to Cloudflare Dashboard**:
   - Visit: https://dash.cloudflare.com/e5e04460dc614be69eb5b8252bff5588/workers/overview

2. **Find the old worker**:
   - Look for worker named: `astro-blog-starter-template`

3. **Unassign routes**:
   - Click on the worker
   - Go to "Settings" or "Triggers" tab
   - Remove the route: `anzx.ai/*`
   - Save changes

4. **Optional - Delete the worker**:
   - If the worker is no longer needed, delete it entirely

### Option 2: Delete Old Worker Entirely

If `astro-blog-starter-template` is not being used:

1. Go to Cloudflare Workers dashboard
2. Find `astro-blog-starter-template`
3. Click "Delete"
4. Confirm deletion

## After Fixing

Once the old worker's routes are removed, re-run the deployment:

```bash
gcloud builds submit \
  --config=infrastructure/cloudbuild/pipelines/anzx-marketing-deploy.yaml \
  --project=virtual-stratum-473511-u5 \
  --substitutions=_PROJECT_ID=virtual-stratum-473511-u5,_REGION=australia-southeast1 .
```

## Current Build Status

**Build ID**: 4dd2c86a-1f59-4265-9874-57551ea451d1
**Status**: FAILED at Step #5 (deploy-worker)
**Reason**: Route conflict with `astro-blog-starter-template`

### What Succeeded ✅
- Step #0: Build Next.js application ✅
- Step #1: Get cricket agent URL ✅
- Step #2: Deploy to Cloudflare Pages ✅
  - Deployed to: https://9bdb5737.anzx-marketing.pages.dev
- Step #3: Update ANZX_MARKETING_URL secret ✅
  - Created version 3 of secret
- Step #4: Prepare worker config ✅
- Step #6: Write deployment state ✅

### What Failed ❌
- Step #5: Deploy Cloudflare Worker ❌
  - Reason: Route conflict

## Technical Details

### Our Worker Configuration
**Name**: `anzx-cricket-proxy`
**Routes**:
- `anzx.ai/cricket*` (for cricket chatbot)
- `anzx.ai/*` (for ANZX marketing - catch-all)
- `anzx.ai/_next/*` (for Next.js assets)
- `anzx.ai/images/*` (for images)

**Environment Variables**:
- `CRICKET_AGENT_URL`: Cloud Run service URL
- `CRICKET_CHATBOT_URL`: https://6ded74f7.anzx-cricket.pages.dev
- `ANZX_MARKETING_URL`: https://9bdb5737.anzx-marketing.pages.dev

### Conflicting Worker
**Name**: `astro-blog-starter-template`
**Routes**: `anzx.ai/*`

## Why This Happened

The `astro-blog-starter-template` worker was likely created during initial testing or development and was never cleaned up. It's now blocking our production deployment.

## Prevention

After fixing this issue, we should:
1. Document all active workers
2. Remove unused workers promptly
3. Use consistent naming conventions
4. Add worker cleanup to deployment scripts

## Next Steps

1. ⏳ **User Action Required**: Remove `astro-blog-starter-template` worker routes in Cloudflare dashboard
2. ⏳ Re-run deployment
3. ⏳ Verify deployment succeeds
4. ⏳ Test both cricket and marketing sites

## Verification After Fix

After removing the old worker and re-deploying, verify:

```bash
# Check worker deployment
curl -I https://anzx.ai

# Check cricket chatbot
curl -I https://anzx.ai/cricket

# Check marketing site
curl -I https://anzx.ai/en
```

All should return `200 OK` or appropriate redirects.

---

**Date**: 2025-10-04
**Status**: 🚨 BLOCKED - User action required
**Action**: Remove `astro-blog-starter-template` worker routes in Cloudflare
**Link**: https://dash.cloudflare.com/e5e04460dc614be69eb5b8252bff5588/workers/overview
