# Phase 17: Deployment & Launch - Updated Implementation Plan

## Overview

This document outlines the updated deployment strategy for the ANZX Marketing website. The site will be deployed to **https://anzx.ai** (root domain) while preserving the existing cricket chatbot at **http://anzx.ai/cricket**.

## Deployment Architecture

### Current State
- **Cricket Chatbot**: Deployed at `https://anzx.ai/cricket` via Cloudflare Pages + Worker
- **Platform**: Cloudflare Pages with custom routing via Cloudflare Worker
- **Google Cloud Project**: Same project as cricket (from cricket-chatbot-deploy-fixed.yaml)
- **Cloudflare Account**: Same account as cricket
- **Secrets**: Reuse existing Cloudflare secrets

### Target State
- **ANZX Marketing**: Deploy to `https://anzx.ai` (root domain)
- **Cricket Chatbot**: Remains at `https://anzx.ai/cricket` (unchanged)
- **Routing Strategy**: Cloudflare Worker will route:
  - `/cricket/*` → Cricket Chatbot (existing)
  - `/*` → ANZX Marketing (new)
- **Configuration**: Use same Google Cloud project, Cloudflare account, and secrets

## Updated Task Breakdown

### Task 76: Set up CI/CD Pipeline ✅

**Implementation Steps:**

1. **Create Cloudflare Pages Deployment Pipeline**
   - Copy `infrastructure/cloudbuild/pipelines/cricket-chatbot-deploy-fixed.yaml`
   - Create new file: `infrastructure/cloudbuild/pipelines/anzx-marketing-deploy.yaml`
   - Modify for anzx-marketing service deployment

2. **Key Changes from Cricket Pipeline:**
   - Source directory: `services/anzx-marketing` (instead of `services/cricket-marketing`)
   - Cloudflare project name: `anzx-marketing` (instead of `anzx-cricket`)
   - Custom domain: `https://anzx.ai` (root domain)
   - Build command: `npm run build` (Next.js 14 static export)
   - Output directory: `out/` (Next.js export output)
   - **Use same secrets**: CLOUDFLARE_API_TOKEN, CLOUDFLARE_ACCOUNT_ID, CLOUDFLARE_ZONE_ID
   - **Use same project**: ${_PROJECT_ID} from cricket pipeline
   - **Use same region**: ${_REGION} from cricket pipeline (australia-southeast1)

3. **Pipeline Steps:**
   - Step 1: Build Next.js application
   - Step 2: Deploy to Cloudflare Pages
   - Step 3: Update deployment URL secret
   - Step 4: Update Cloudflare Worker routing
   - Step 5: Write deployment state

4. **Environment Variables:**
   ```env
   NEXT_PUBLIC_CORE_API_URL=https://api.anzx.ai
   NEXT_PUBLIC_SITE_URL=https://anzx.ai
   NEXT_PUBLIC_GA_MEASUREMENT_ID=${GA_MEASUREMENT_ID}
   NEXT_PUBLIC_CLARITY_PROJECT_ID=${CLARITY_PROJECT_ID}
   NODE_ENV=production
   ```

### Task 77: Configure Production Environment ✅

**Implementation Steps:**

1. **Use Existing Google Cloud Secrets (Same as Cricket):**
   ```bash
   # These secrets already exist from cricket deployment:
   # - CLOUDFLARE_API_TOKEN
   # - CLOUDFLARE_ACCOUNT_ID
   # - CLOUDFLARE_ZONE_ID
   # - CLOUDFLARE_WORKER_NAME
   # - CLOUDFLARE_ROUTE_PATTERN
   
   # Only create new secret for ANZX Marketing deployment URL:
   gcloud secrets create ANZX_MARKETING_URL --data-file=-
   
   # Analytics IDs (if not already exist):
   gcloud secrets create ANZX_GA_MEASUREMENT_ID --data-file=- || echo "Already exists"
   gcloud secrets create ANZX_CLARITY_PROJECT_ID --data-file=- || echo "Already exists"
   ```

2. **Update Cloudflare Worker Configuration:**
   - Modify `infrastructure/cloudflare/worker.js` to handle root domain routing
   - Add routing logic:
     ```javascript
     // Route /cricket/* to cricket chatbot
     if (url.pathname.startsWith('/cricket')) {
       return fetch(CRICKET_CHATBOT_URL + url.pathname + url.search);
     }
     
     // Route everything else to ANZX Marketing
     return fetch(ANZX_MARKETING_URL + url.pathname + url.search);
     ```

3. **Update wrangler.toml Template:**
   - Add `ANZX_MARKETING_URL` environment variable
   - Keep existing `CRICKET_CHATBOT_URL` variable
   - Update routing patterns

4. **Production Environment File:**
   - Create `.env.production` in `services/anzx-marketing/`
   - Configure all production URLs and API keys

### Task 78: Perform Security Audit ✅

**Implementation Steps:**

1. **Content Security Policy:**
   - Review and update CSP headers in `next.config.js`
   - Ensure proper directives for:
     - Google Analytics
     - Microsoft Clarity
     - Cloudflare CDN
     - Image sources

2. **Input Validation:**
   - Verify all form inputs use Zod validation
   - Check API route input sanitization
   - Test for SQL injection (if applicable)

3. **XSS Protection:**
   - Verify React's built-in XSS protection
   - Check for `dangerouslySetInnerHTML` usage
   - Validate MDX content rendering

4. **Security Headers:**
   - X-Frame-Options: SAMEORIGIN
   - X-Content-Type-Options: nosniff
   - Referrer-Policy: strict-origin-when-cross-origin
   - Permissions-Policy

### Task 79: Set up Monitoring and Alerting ✅

**Implementation Steps:**

1. **Uptime Monitoring:**
   - Configure Google Cloud Monitoring uptime checks
   - Monitor `https://anzx.ai/en`
   - Alert on 5xx errors or downtime

2. **Error Rate Alerts:**
   - Set up Sentry error tracking
   - Configure alert thresholds
   - Set up Slack/email notifications

3. **Performance Monitoring:**
   - Monitor Core Web Vitals via Google Analytics
   - Set up performance degradation alerts
   - Track page load times

4. **Log Aggregation:**
   - Configure Cloud Logging
   - Set up log-based metrics
   - Create dashboard for key metrics

### Task 80: Deploy to Production ✅

**Implementation Steps:**

1. **Pre-Deployment Checklist:**
   - [ ] All tests passing
   - [ ] Environment variables configured
   - [ ] Secrets created in Google Cloud
   - [ ] Cloudflare project created
   - [ ] DNS records verified
   - [ ] Backup of current site (if any)

2. **Deployment Process:**
   ```bash
   # Trigger Cloud Build deployment (same project/region as cricket)
   gcloud builds submit \
     --config=infrastructure/cloudbuild/pipelines/anzx-marketing-deploy.yaml \
     --substitutions=_PROJECT_ID=${PROJECT_ID},_REGION=australia-southeast1
   
   # Or use the helper script:
   ./scripts/deploy-anzx-marketing.sh
   ```
   
   **Note**: Uses exact same Google Cloud project and region as cricket deployment

3. **Post-Deployment Verification:**
   - [ ] Homepage loads: `https://anzx.ai/en`
   - [ ] Hindi homepage loads: `https://anzx.ai/hi`
   - [ ] Product pages load correctly
   - [ ] Blog pages load correctly
   - [ ] Cricket chatbot still works: `https://anzx.ai/cricket`
   - [ ] Analytics tracking works
   - [ ] Forms submit correctly
   - [ ] No console errors
   - [ ] Mobile responsive
   - [ ] All images load

4. **Rollback Plan:**
   - Keep previous Cloudflare Pages deployment
   - Can rollback via Cloudflare dashboard
   - Update worker to point to previous deployment

## Routing Strategy

### Cloudflare Worker Routing Logic

```javascript
// Updated worker.js routing
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    
    // Route 1: Cricket Chatbot (preserve existing)
    if (url.pathname.startsWith('/cricket')) {
      const cricketUrl = env.CRICKET_CHATBOT_URL + url.pathname + url.search;
      return fetch(cricketUrl, request);
    }
    
    // Route 2: ANZX Marketing (new - root domain)
    const marketingUrl = env.ANZX_MARKETING_URL + url.pathname + url.search;
    return fetch(marketingUrl, request);
  }
};
```

## Configuration Details (From Cricket Pipeline)

### Reused from Cricket Deployment:

1. **Google Cloud Project:**
   - Project ID: `${_PROJECT_ID}` (same as cricket)
   - Region: `${_REGION}` (australia-southeast1)
   - Cloud Storage bucket: `${_PROJECT_ID}_cloudbuild`
   - Deployment state bucket: `anzx-deploy-state`

2. **Cloudflare Secrets (Already Exist):**
   - `CLOUDFLARE_API_TOKEN` - API token for Cloudflare
   - `CLOUDFLARE_ACCOUNT_ID` - Cloudflare account ID
   - `CLOUDFLARE_ZONE_ID` - Zone ID for anzx.ai domain
   - `CLOUDFLARE_WORKER_NAME` - Worker name
   - `CLOUDFLARE_ROUTE_PATTERN` - Route pattern for worker

3. **New Secrets to Create:**
   - `ANZX_MARKETING_URL` - Deployment URL for ANZX Marketing
   - `ANZX_GA_MEASUREMENT_ID` - Google Analytics ID (if not exists)
   - `ANZX_CLARITY_PROJECT_ID` - Microsoft Clarity ID (if not exists)

4. **Build Configuration:**
   - Node.js version: 20 (same as cricket)
   - Wrangler: latest version
   - Cloud SDK: slim image

## File Structure

### New Files to Create:

1. **`infrastructure/cloudbuild/pipelines/anzx-marketing-deploy.yaml`**
   - Exact copy of cricket-chatbot-deploy-fixed.yaml
   - Only modify: service name, directory, project name
   - Keep all secrets, project IDs, regions identical

2. **`infrastructure/cloudflare/worker-updated.js`**
   - Updated routing logic for both services

3. **`infrastructure/cloudflare/wrangler-updated.toml.tmpl`**
   - Template with both service URLs
   - Keep existing Cloudflare account/zone IDs

4. **`services/anzx-marketing/.env.production`**
   - Production environment variables

5. **`scripts/deploy-anzx-marketing.sh`**
   - Helper script to trigger deployment
   - Use same project and region as cricket

### Files to Modify:

1. **`infrastructure/cloudflare/worker.js`**
   - Add ANZX Marketing routing

2. **`infrastructure/cloudflare/wrangler.toml.tmpl`**
   - Add ANZX_MARKETING_URL variable

## Deployment Sequence

### Phase 1: Preparation (Pre-Deployment)
1. Create Google Cloud secrets
2. Create Cloudflare Pages project
3. Configure environment variables
4. Run security audit
5. Run final tests

### Phase 2: Initial Deployment
1. Deploy ANZX Marketing to Cloudflare Pages
2. Capture deployment URL
3. Update secrets with deployment URL

### Phase 3: Worker Update
1. Update Cloudflare Worker with new routing
2. Deploy updated worker
3. Verify routing works correctly

### Phase 4: Verification
1. Test root domain (https://anzx.ai)
2. Test cricket chatbot (https://anzx.ai/cricket)
3. Monitor for errors
4. Verify analytics

### Phase 5: Monitoring
1. Set up uptime monitoring
2. Configure alerts
3. Monitor for 24 hours
4. Optimize as needed

## Risk Mitigation

### Risks and Mitigation Strategies:

1. **Risk: Cricket chatbot stops working**
   - Mitigation: Test routing thoroughly before production
   - Rollback: Revert worker to previous version

2. **Risk: DNS propagation issues**
   - Mitigation: No DNS changes needed (using existing domain)
   - Worker handles routing at edge

3. **Risk: Performance degradation**
   - Mitigation: Monitor Core Web Vitals
   - Cloudflare CDN provides global edge caching

4. **Risk: Build failures**
   - Mitigation: Test build locally first
   - Use same Node.js version (20) as cricket

5. **Risk: Environment variable issues**
   - Mitigation: Validate all secrets before deployment
   - Use .env.production template

## Success Criteria

### Deployment is successful when:

- [ ] ANZX Marketing loads at `https://anzx.ai`
- [ ] All pages accessible and functional
- [ ] Cricket chatbot still works at `https://anzx.ai/cricket`
- [ ] No 404 or 500 errors
- [ ] Analytics tracking works
- [ ] Core Web Vitals meet targets (LCP < 2.5s, FID < 100ms, CLS < 0.1)
- [ ] Mobile responsive
- [ ] All tests passing
- [ ] No console errors
- [ ] Monitoring and alerts configured

## Timeline

- **Task 76 (CI/CD Pipeline)**: 2 hours
- **Task 77 (Production Config)**: 1 hour
- **Task 78 (Security Audit)**: 2 hours
- **Task 79 (Monitoring)**: 1 hour
- **Task 80 (Deployment)**: 2 hours
- **Total**: ~8 hours (1 day)

## Next Steps

1. **Review this plan** - Confirm approach is correct
2. **Create deployment pipeline** - Based on cricket template
3. **Configure secrets** - Set up Google Cloud secrets
4. **Test locally** - Verify build works
5. **Deploy to staging** - Test in staging environment (optional)
6. **Deploy to production** - Execute deployment
7. **Monitor and verify** - Ensure everything works

---

## Questions for Review

Before proceeding with implementation, please confirm:

1. ✅ Deploy ANZX Marketing to root domain (`https://anzx.ai`)
2. ✅ Keep cricket chatbot at `/cricket` path unchanged
3. ✅ Use Cloudflare Pages + Worker (same as cricket)
4. ✅ Copy and modify cricket deployment pipeline
5. ✅ Update worker routing to handle both services

**Please review and approve this plan before I proceed with implementation.**

---

## Summary of Configuration Reuse

### ✅ Reused from Cricket Deployment (No Changes Needed):

1. **Google Cloud:**
   - Same project ID
   - Same region (australia-southeast1)
   - Same Cloud Storage buckets
   - Same deployment state storage

2. **Cloudflare:**
   - Same API token (CLOUDFLARE_API_TOKEN)
   - Same account ID (CLOUDFLARE_ACCOUNT_ID)
   - Same zone ID (CLOUDFLARE_ZONE_ID)
   - Same worker name (CLOUDFLARE_WORKER_NAME)
   - Same route pattern (CLOUDFLARE_ROUTE_PATTERN)

3. **Build Tools:**
   - Same Node.js version (20)
   - Same Wrangler CLI
   - Same Cloud SDK image

### 🆕 New Configuration (Only These Need to be Created):

1. **New Secret:**
   - `ANZX_MARKETING_URL` - Stores the Cloudflare Pages deployment URL

2. **New Cloudflare Project:**
   - Project name: `anzx-marketing`
   - Deployed to same Cloudflare account

3. **Updated Worker:**
   - Add routing for root domain
   - Keep cricket routing unchanged

### 📝 Implementation Approach:

1. Copy `cricket-chatbot-deploy-fixed.yaml` exactly
2. Change only these values:
   - Service directory: `services/anzx-marketing`
   - Project name: `anzx-marketing`
   - Secret name: `ANZX_MARKETING_URL`
3. Keep everything else identical (project, region, secrets, configuration)

---

**Status**: ⏳ AWAITING REVIEW
**Last Updated**: 2025-03-10
**Prepared By**: Kiro AI Assistant

**Key Point**: This deployment reuses 100% of the cricket deployment infrastructure - same Google Cloud project, same Cloudflare account, same secrets. Only the service name and deployment URL are different.
