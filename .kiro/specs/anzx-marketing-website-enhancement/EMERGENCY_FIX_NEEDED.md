# 🚨 EMERGENCY: Both Sites Broken

## Current Status: BOTH SITES DOWN

- ❌ **Main site (anzx.ai)** - 404 errors
- ❌ **Cricket (anzx.ai/cricket)** - Incomplete loading (HTTP 103)
- ✅ **Direct Pages URLs** - Both working fine

## What Happened

When we deployed the Cloudflare Worker with routes for `anzx.ai/cricket*`, it took over ALL routing for the `anzx.ai` domain, breaking the custom domain configuration that was set up for the main site.

## Root Cause

**Cloudflare routing precedence:**
1. Workers with routes take precedence over Pages custom domains
2. When we deployed the worker with `anzx.ai/cricket*` route
3. It took over the entire `anzx.ai` domain
4. The Pages custom domain configuration was overridden
5. Now the worker is handling ALL requests, but it only knows how to proxy `/cricket`

## Evidence

```bash
# Main site - 404
$ curl -sI https://anzx.ai/en
HTTP/2 404

# Cricket - Incomplete
$ curl -sI https://anzx.ai/cricket  
HTTP/2 103

# Direct URLs work
$ curl -sI https://e7218b3a.anzx-marketing.pages.dev/en/
HTTP/2 200

$ curl -sI https://d1e8b1c8.anzx-cricket.pages.dev
HTTP/2 200
```

## The Fix

### Option A: Remove Worker, Use Subdomain for Cricket (RECOMMENDED)

**Simplest and most reliable solution:**

1. **Remove the worker completely**
2. **Configure custom domains on Pages projects:**
   - `anzx.ai` → anzx-marketing Pages project
   - `cricket.anzx.ai` → anzx-cricket Pages project
3. **Update links** to use `cricket.anzx.ai` instead of `anzx.ai/cricket`

**Pros:**
- No worker complexity
- Direct Pages serving (faster)
- No routing conflicts
- Easy to maintain

**Cons:**
- URL changes from `/cricket` to subdomain
- Need to update any existing links

### Option B: Fix Worker to Proxy Everything (COMPLEX)

Update the worker to:
1. Proxy `/cricket*` to cricket Pages
2. Proxy ALL other routes to marketing Pages
3. Handle static assets correctly

**Pros:**
- Keeps `/cricket` path
- Single domain

**Cons:**
- Complex worker logic
- Extra proxy hop (slower)
- More points of failure
- Harder to debug

### Option C: Quick Emergency Rollback

**Immediate fix to restore main site:**

1. Delete the worker deployment
2. Main site will work again via Pages custom domain
3. Cricket will be broken but accessible via direct URL
4. Then implement proper solution

## Recommended Action Plan

### Immediate (5 minutes):
1. **Delete the worker** to restore main site
2. Main site will work immediately
3. Cricket accessible via direct URL temporarily

### Short-term (15 minutes):
1. **Set up subdomain**: Configure `cricket.anzx.ai` as custom domain on anzx-cricket Pages
2. **Update DNS**: Add CNAME record for cricket subdomain
3. **Test both sites**: Both should work perfectly

### Long-term:
1. Update any documentation/links to use `cricket.anzx.ai`
2. Set up redirect from `/cricket` to `cricket.anzx.ai` if needed
3. Remove worker completely

## Commands to Execute

### Emergency Rollback (Delete Worker):
```bash
# Delete the worker
export CLOUDFLARE_API_TOKEN=$(gcloud secrets versions access latest --secret=CLOUDFLARE_API_TOKEN)
npx wrangler@latest delete anzx-cricket-proxy

# Or via API
curl -X DELETE "https://api.cloudflare.com/client/v4/accounts/e5e04460dc614be69eb5b8252bff5588/workers/scripts/anzx-cricket-proxy" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN"
```

### Set Up Cricket Subdomain:
```bash
# In Cloudflare dashboard:
# 1. Go to Pages → anzx-cricket
# 2. Custom domains → Add domain
# 3. Enter: cricket.anzx.ai
# 4. Activate
```

## Why This Happened

We tried to use a worker to proxy `/cricket` to a different Pages project while keeping the main site on another Pages project with a custom domain. This created a routing conflict because:

1. Cloudflare Workers with routes take precedence
2. The worker route `anzx.ai/cricket*` matched
3. But the worker's `return fetch(request)` for non-cricket routes didn't work as expected
4. The Pages custom domain was overridden

## The Correct Architecture

**For multiple apps on one domain, you have two options:**

### Option 1: Subdomain (Recommended)
```
anzx.ai → anzx-marketing (Pages custom domain)
cricket.anzx.ai → anzx-cricket (Pages custom domain)
```

### Option 2: Worker Proxy (Complex)
```
anzx.ai → Worker
  ├─ /cricket* → anzx-cricket Pages
  └─ /* → anzx-marketing Pages
```

Option 1 is simpler, faster, and more reliable.

## Immediate Action Required

**Delete the worker NOW to restore the main site:**

```bash
export CLOUDFLARE_API_TOKEN=$(gcloud secrets versions access latest --secret=CLOUDFLARE_API_TOKEN)
npx wrangler@latest delete anzx-cricket-proxy
```

Then set up cricket subdomain properly.

---

**Status**: CRITICAL - Both sites down  
**Priority**: P0 - Immediate fix required  
**ETA**: 5 minutes to restore main site  
**Next**: Set up proper subdomain architecture
