# Cricket Subdomain Setup Guide

## Current Status
- ✅ **Main site (anzx.ai)** - Working perfectly
- ✅ **Cricket Pages (d1e8b1c8.anzx-cricket.pages.dev)** - Working perfectly
- ❌ **Cricket on main domain (anzx.ai/cricket)** - Not working (worker deleted)

## Solution: Set Up cricket.anzx.ai Subdomain

Since you own `anzx.ai`, you automatically own ALL subdomains. We'll set up `cricket.anzx.ai` to point directly to your cricket Pages project.

## Steps to Configure in Cloudflare Dashboard

### Step 1: Add Custom Domain to Cricket Pages Project

1. Go to [Cloudflare Dashboard](https://dash.cloudflare.com/)
2. Navigate to **Workers & Pages** → **Pages**
3. Click on **anzx-cricket** project
4. Go to **Custom domains** tab
5. Click **Set up a custom domain**
6. Enter: `cricket.anzx.ai`
7. Click **Continue**
8. Cloudflare will automatically:
   - Create the DNS CNAME record
   - Provision SSL certificate
   - Activate the domain

### Step 2: Verify DNS Configuration

The DNS should be automatically configured, but you can verify:

1. Go to **Websites** → **anzx.ai** → **DNS** → **Records**
2. You should see a new CNAME record:
   - **Type**: CNAME
   - **Name**: cricket
   - **Target**: anzx-cricket.pages.dev
   - **Proxy status**: Proxied (orange cloud)

### Step 3: Test the Subdomain

After setup (may take 1-2 minutes for DNS propagation):

```bash
# Test the subdomain
curl -I https://cricket.anzx.ai

# Should return HTTP 200
```

## Architecture After Setup

```
anzx.ai → Cloudflare Pages (anzx-marketing project)
  ├─ /en/ → Marketing site
  ├─ /es/ → Marketing site (Spanish)
  └─ /fr/ → Marketing site (French)

cricket.anzx.ai → Cloudflare Pages (anzx-cricket project)
  └─ / → Cricket chatbot
```

## Benefits of This Approach

1. **No Worker Complexity** - Direct Pages serving (faster)
2. **No Routing Conflicts** - Each subdomain is independent
3. **Easy to Maintain** - Simple DNS configuration
4. **Better Performance** - No proxy hop
5. **Free** - Subdomains are included with your domain

## Update Links (Optional)

If you have any links to `anzx.ai/cricket`, update them to `cricket.anzx.ai`:

- In marketing site navigation
- In documentation
- In external references

## Rollback Plan

If you need to rollback:
1. Remove custom domain from cricket Pages project
2. DNS record will be automatically removed
3. Cricket will only be accessible via direct Pages URL

## Expected Timeline

- **DNS Setup**: Instant (via Cloudflare dashboard)
- **SSL Certificate**: 1-2 minutes
- **Full Propagation**: 1-5 minutes

## Verification Commands

```bash
# Check DNS resolution
dig cricket.anzx.ai

# Check HTTPS
curl -I https://cricket.anzx.ai

# Check content
curl https://cricket.anzx.ai | head -20
```

## Next Steps

1. Follow the steps above to set up `cricket.anzx.ai`
2. Test the subdomain
3. Update any links in your marketing site (if needed)
4. Remove worker deployment files (optional cleanup)

---

**Status**: Ready to implement  
**Estimated Time**: 5 minutes  
**Risk**: Low (main site unaffected)
