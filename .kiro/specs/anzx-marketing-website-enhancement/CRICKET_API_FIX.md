# Cricket API Connection Fix

## Problem Identified

The cricket frontend was **hardcoded** to call a specific API URL:
```typescript
fetch('https://cricket-agent-aa5gcxefza-ts.a.run.app/v1/ask', ...)
```

This meant:
- The API URL couldn't be changed without modifying code
- The deployment pipeline's `CRICKET_AGENT_URL` environment variable was being set but not used
- If the Cloud Run URL changed, the frontend would break

## Solution Applied

### 1. Updated Chat Components

Modified both chat components to use environment variables:

**Before:**
```typescript
const response = await fetch('https://cricket-agent-aa5gcxefza-ts.a.run.app/v1/ask', {
```

**After:**
```typescript
const apiUrl = process.env.NEXT_PUBLIC_CRICKET_AGENT_URL || 'https://cricket-agent-aa5gcxefza-ts.a.run.app'
const response = await fetch(`${apiUrl}/v1/ask`, {
```

Files updated:
- `services/cricket-marketing/components/chat-dock.tsx`
- `services/cricket-marketing/components/chat-fullpage.tsx`

### 2. Updated Deployment Pipeline

Added `NEXT_PUBLIC_CRICKET_AGENT_URL` to the build environment:

```yaml
cat > .env.production << EOF
CRICKET_AGENT_URL=$AGENT_URL
NEXT_PUBLIC_CRICKET_AGENT_URL=$AGENT_URL  # NEW: For Next.js client-side
NEXT_PUBLIC_APP_URL=https://cricket.anzx.ai
NODE_ENV=production
EOF
```

## How It Works Now

```
┌─────────────────────────────────────────────────────────────┐
│                  Deployment Pipeline                        │
│  1. Gets cricket-agent URL from Cloud Run                   │
│  2. Sets NEXT_PUBLIC_CRICKET_AGENT_URL=$AGENT_URL          │
│  3. Builds Next.js app (env var baked into build)          │
│  4. Deploys to Cloudflare Pages                            │
└─────────────────────────────────────────────────────────────┘
                            │
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              cricket.anzx.ai (Frontend)                     │
│  - Reads NEXT_PUBLIC_CRICKET_AGENT_URL from build          │
│  - Falls back to hardcoded URL if not set                  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ↓ API calls to
┌─────────────────────────────────────────────────────────────┐
│         cricket-agent.run.app (Backend API)                 │
│         Google Cloud Run (Python/FastAPI)                   │
└─────────────────────────────────────────────────────────────┘
```

## Why NEXT_PUBLIC_ Prefix?

Next.js requires the `NEXT_PUBLIC_` prefix for environment variables that need to be accessible in the browser (client-side code). Variables without this prefix are only available server-side.

## Testing

After redeploying, you can verify the API connection:

```bash
# Redeploy the cricket chatbot
gcloud builds submit --config=infrastructure/cloudbuild/pipelines/cricket-chatbot-deploy-fixed.yaml

# Test the site
open https://cricket.anzx.ai

# Check browser console - should see API calls to the correct URL
# Open DevTools → Network tab → Filter by "ask"
```

## Fallback Behavior

If the environment variable isn't set during build, it falls back to the hardcoded URL:
```typescript
const apiUrl = process.env.NEXT_PUBLIC_CRICKET_AGENT_URL || 'https://cricket-agent-aa5gcxefza-ts.a.run.app'
```

This ensures the app still works even if the environment variable is missing.

## Benefits

1. **Dynamic Configuration**: API URL is set during deployment
2. **Flexibility**: Can easily change the backend URL without code changes
3. **Environment-Specific**: Can use different URLs for dev/staging/prod
4. **Maintainable**: Single source of truth in deployment pipeline

## Next Deployment

The next time you run the cricket deployment pipeline, it will:
1. Get the current cricket-agent URL from Cloud Run
2. Set it as `NEXT_PUBLIC_CRICKET_AGENT_URL`
3. Build the Next.js app with this URL baked in
4. Deploy to cricket.anzx.ai

The frontend will then call the correct API URL automatically.

---

**Status**: ✅ Fixed  
**Files Modified**: 
- `services/cricket-marketing/components/chat-dock.tsx`
- `services/cricket-marketing/components/chat-fullpage.tsx`
- `infrastructure/cloudbuild/pipelines/cricket-chatbot-deploy-fixed.yaml`

**Next Step**: Redeploy cricket chatbot to apply changes
