# ANZX Marketing Deployment Checklist

## Pre-Deployment Checklist

### 1. Code Quality & Testing
- [ ] All unit tests passing (`npm test`)
- [ ] All integration tests passing
- [ ] E2E tests passing
- [ ] No TypeScript errors (`npm run type-check`)
- [ ] No ESLint errors (`npm run lint`)
- [ ] Build succeeds locally (`npm run build`)
- [ ] Accessibility tests passing (WCAG 2.1 AA)
- [ ] Cross-browser testing complete (Chrome, Firefox, Safari, Edge)
- [ ] Mobile responsiveness verified

### 2. Environment Configuration
- [ ] `.env.production` created with all required variables
- [ ] `NEXT_PUBLIC_CORE_API_URL` set to production API
- [ ] `NEXT_PUBLIC_SITE_URL` set to https://anzx.ai
- [ ] Google Analytics ID configured
- [ ] Microsoft Clarity ID configured
- [ ] All API endpoints verified

### 3. Google Cloud Secrets
- [ ] `CLOUDFLARE_API_TOKEN` exists (reused from cricket)
- [ ] `CLOUDFLARE_ACCOUNT_ID` exists (reused from cricket)
- [ ] `CLOUDFLARE_ZONE_ID` exists (reused from cricket)
- [ ] `CLOUDFLARE_WORKER_NAME` exists (reused from cricket)
- [ ] `CLOUDFLARE_ROUTE_PATTERN` exists (reused from cricket)
- [ ] `CRICKET_CHATBOT_URL` exists (reused from cricket)
- [ ] `ANZX_MARKETING_URL` secret created (NEW)

### 4. Cloudflare Configuration
- [ ] Cloudflare account access verified
- [ ] DNS records for anzx.ai verified
- [ ] Cloudflare Pages project `anzx-marketing` created
- [ ] Worker routing tested in staging (if available)

### 5. Content Review
- [ ] All pages have proper meta tags
- [ ] All images optimized (WebP/AVIF)
- [ ] All links working (no 404s)
- [ ] All forms tested
- [ ] Blog posts reviewed for quality
- [ ] Legal pages (privacy, terms) reviewed
- [ ] Contact information verified
- [ ] Pricing information accurate

### 6. Performance Optimization
- [ ] Core Web Vitals targets met:
  - [ ] LCP < 2.5s
  - [ ] FID < 100ms
  - [ ] CLS < 0.1
- [ ] Bundle size optimized
- [ ] Images lazy-loaded
- [ ] Code splitting implemented
- [ ] Lighthouse score > 90

### 7. Security Audit
- [ ] Content Security Policy configured
- [ ] Security headers configured
- [ ] Input validation on all forms
- [ ] XSS protection verified
- [ ] No hardcoded secrets in code
- [ ] HTTPS enforced

### 8. Analytics & Monitoring
- [ ] Google Analytics 4 configured
- [ ] Microsoft Clarity configured
- [ ] Error tracking (Sentry) configured
- [ ] Uptime monitoring configured
- [ ] Performance monitoring configured
- [ ] Alert notifications configured

---

## Deployment Steps

### Step 1: Create Google Cloud Secret (One-time)
```bash
# Create ANZX_MARKETING_URL secret (will be populated during deployment)
echo "https://anzx-marketing.pages.dev" | gcloud secrets create ANZX_MARKETING_URL --data-file=- --project=anzx-ai-platform
```

### Step 2: Verify Existing Secrets
```bash
# Verify all required secrets exist
gcloud secrets list --project=anzx-ai-platform --filter="name:CLOUDFLARE OR name:CRICKET"
```

### Step 3: Run Deployment
```bash
# Option 1: Use helper script
./scripts/deploy-anzx-marketing.sh

# Option 2: Manual deployment
gcloud builds submit \
  --config=infrastructure/cloudbuild/pipelines/anzx-marketing-deploy.yaml \
  --project=anzx-ai-platform \
  --substitutions=_PROJECT_ID=anzx-ai-platform,_REGION=australia-southeast1
```

### Step 4: Monitor Deployment
- [ ] Watch Cloud Build logs for errors
- [ ] Verify build completes successfully
- [ ] Check deployment URL is captured
- [ ] Verify secret is updated
- [ ] Confirm worker deployment succeeds

---

## Post-Deployment Verification

### 1. Homepage Verification
- [ ] Homepage loads: https://anzx.ai
- [ ] English homepage: https://anzx.ai/en
- [ ] Hindi homepage: https://anzx.ai/hi
- [ ] Hero section displays correctly
- [ ] Agent cards render properly
- [ ] CTAs are clickable
- [ ] Navigation works
- [ ] Footer displays correctly

### 2. Product Pages
- [ ] AI Interviewer page: https://anzx.ai/ai-interviewer
- [ ] Customer Service AI page: https://anzx.ai/customer-service-ai
- [ ] AI Sales Agent page: https://anzx.ai/ai-sales-agent
- [ ] Demo request forms work

### 3. Content Pages
- [ ] Blog listing: https://anzx.ai/blog
- [ ] Individual blog posts load
- [ ] Educational pages load:
  - [ ] https://anzx.ai/what-is-an-ai-agent
  - [ ] https://anzx.ai/agentic-ai
  - [ ] https://anzx.ai/workflow-automation
- [ ] Comparison pages load:
  - [ ] https://anzx.ai/ai-agents-vs-rpa
  - [ ] https://anzx.ai/ai-agents-vs-automation

### 4. Regional Pages
- [ ] Australia: https://anzx.ai/ai-agents-australia
- [ ] New Zealand: https://anzx.ai/ai-agents-new-zealand
- [ ] India: https://anzx.ai/ai-agents-india
- [ ] Singapore: https://anzx.ai/ai-agents-singapore
- [ ] Currency displays correctly for each region
- [ ] Local contact information displays

### 5. Integrations
- [ ] Integrations page: https://anzx.ai/integrations
- [ ] Individual integration pages load
- [ ] Search functionality works
- [ ] Category filters work

### 6. Cricket Chatbot (Must Still Work!)
- [ ] Cricket chatbot loads: https://anzx.ai/cricket
- [ ] Chat functionality works
- [ ] No 404 errors
- [ ] Static assets load correctly

### 7. Forms & Interactions
- [ ] Demo request form submits
- [ ] Newsletter signup works
- [ ] Contact forms work
- [ ] Lead capture works
- [ ] Form validation works
- [ ] Success/error messages display

### 8. Analytics & Tracking
- [ ] Google Analytics tracking fires
- [ ] Microsoft Clarity recording works
- [ ] Page views tracked
- [ ] Conversion events tracked
- [ ] No console errors

### 9. Performance
- [ ] Page load time < 3s
- [ ] Images load properly
- [ ] No layout shifts
- [ ] Smooth animations
- [ ] Mobile performance good

### 10. Mobile Testing
- [ ] Responsive design works
- [ ] Touch interactions work
- [ ] Mobile navigation works
- [ ] Forms work on mobile
- [ ] Images display correctly

### 11. Cross-Browser Testing
- [ ] Chrome (desktop & mobile)
- [ ] Firefox
- [ ] Safari (desktop & mobile)
- [ ] Edge

### 12. SEO Verification
- [ ] Meta tags present on all pages
- [ ] Open Graph tags working
- [ ] Twitter Cards working
- [ ] Structured data valid
- [ ] Sitemap accessible
- [ ] robots.txt accessible

---

## Monitoring (First 24 Hours)

### Metrics to Watch
- [ ] Uptime (should be 100%)
- [ ] Error rate (should be < 1%)
- [ ] Page load times (should be < 3s)
- [ ] Core Web Vitals
- [ ] Traffic patterns
- [ ] Conversion rates

### Alerts to Configure
- [ ] Downtime alerts
- [ ] Error rate spikes
- [ ] Performance degradation
- [ ] Failed form submissions

---

## Rollback Plan

If issues are detected:

### Option 1: Rollback via Cloudflare Dashboard
1. Log into Cloudflare dashboard
2. Navigate to Pages > anzx-marketing
3. Select previous deployment
4. Click "Rollback to this deployment"

### Option 2: Rollback Worker
1. Update worker to point to previous deployment URL
2. Redeploy worker with old configuration

### Option 3: Emergency DNS Change
1. Update DNS to point to backup/maintenance page
2. Fix issues
3. Redeploy when ready

---

## Success Criteria

Deployment is considered successful when:

- ✅ All pages load without errors
- ✅ Cricket chatbot still works at /cricket
- ✅ Forms submit successfully
- ✅ Analytics tracking works
- ✅ Core Web Vitals meet targets
- ✅ No console errors
- ✅ Mobile responsive
- ✅ Cross-browser compatible
- ✅ SEO tags present
- ✅ Performance targets met
- ✅ No increase in error rate
- ✅ Uptime maintained

---

## Post-Launch Tasks

### Week 1
- [ ] Monitor analytics daily
- [ ] Review error logs
- [ ] Check conversion rates
- [ ] Gather user feedback
- [ ] Fix any critical issues

### Week 2-4
- [ ] Analyze traffic patterns
- [ ] Optimize underperforming pages
- [ ] A/B test CTAs
- [ ] Improve SEO based on data
- [ ] Plan content updates

---

## Contact Information

**Deployment Lead**: [Your Name]
**Google Cloud Project**: anzx-ai-platform
**Cloudflare Account**: [Account Email]
**Emergency Contact**: [Phone/Email]

---

## Notes

- This deployment reuses 100% of cricket deployment infrastructure
- Same Google Cloud project, region, and secrets
- Only new secret is ANZX_MARKETING_URL
- Worker routing updated to handle both services
- Cricket chatbot must continue working at /cricket

---

**Last Updated**: 2025-04-10
**Status**: Ready for Deployment
