# Phase 2 Implementation Safety Checklist

## 🚨 CRITICAL: Do Not Break Existing Functionality

This checklist MUST be completed for every task to ensure we don't break the existing marketing website or deployed services.

---

## Before Starting Any Task

### 1. Code Review
- [ ] Read ALL existing code in the file/component you're modifying
- [ ] Understand current functionality and dependencies
- [ ] Check git history to understand why code was written this way
- [ ] Look for comments or documentation about the component
- [ ] Check for existing tests that cover this component

### 2. Environment Setup
- [ ] Local development environment matches production
- [ ] Can access deployed core-api at Cloud Run URL
- [ ] Can access PostgreSQL database (read-only for testing)
- [ ] Have GCP credentials for `extreme-gecko-466211-t1`
- [ ] Can run existing test suite locally

### 3. Integration Points
- [ ] Identify all services this component calls
- [ ] Verify those services are deployed and accessible
- [ ] Test API endpoints with curl/Postman before coding
- [ ] Check existing environment variables
- [ ] Review existing error handling patterns

---

## During Implementation

### 1. Additive Changes Only
- [ ] New code is ADDED, not replacing existing code
- [ ] Existing functions/components still work
- [ ] New features are behind feature flags if possible
- [ ] Backward compatibility maintained
- [ ] No breaking changes to APIs or interfaces

### 2. Testing as You Go
- [ ] Test existing functionality after each change
- [ ] Run existing test suite frequently
- [ ] Test in local environment first
- [ ] Test against deployed services (not mocks)
- [ ] Check browser console for errors

### 3. Code Quality
- [ ] Follow existing code style and patterns
- [ ] Add comments for complex logic
- [ ] Handle errors gracefully
- [ ] Log important events
- [ ] No console.log in production code

---

## Before Committing Code

### 1. Local Testing
- [ ] All existing tests pass
- [ ] New tests added for new functionality
- [ ] Manual testing of affected components
- [ ] Test error scenarios
- [ ] Check for console errors/warnings

### 2. Integration Testing
- [ ] Test against deployed backend services
- [ ] Verify API calls work correctly
- [ ] Check authentication flows
- [ ] Test with real data (not mocks)
- [ ] Verify database operations

### 3. Code Review Prep
- [ ] Code is clean and well-documented
- [ ] No commented-out code
- [ ] No debug statements
- [ ] Environment variables documented
- [ ] README updated if needed

---

## Before Deploying to Staging

### 1. Pre-Deployment Checks
- [ ] All tests pass in CI/CD
- [ ] Code reviewed by at least one other developer
- [ ] Database migrations tested
- [ ] Environment variables configured
- [ ] Rollback plan documented

### 2. Staging Deployment
- [ ] Deploy to staging environment FIRST
- [ ] Test ALL existing pages/features
- [ ] Test new functionality
- [ ] Check logs for errors
- [ ] Performance testing

### 3. Staging Validation
- [ ] Homepage loads correctly
- [ ] All navigation links work
- [ ] Agent cards display properly
- [ ] Existing forms still work
- [ ] No console errors
- [ ] Mobile responsive
- [ ] Cross-browser testing

---

## Before Deploying to Production

### 1. Final Checks
- [ ] Staging has been stable for at least 24 hours
- [ ] All stakeholders have approved
- [ ] Rollback plan is ready and tested
- [ ] Monitoring and alerting configured
- [ ] On-call engineer available

### 2. Production Deployment
- [ ] Deploy during low-traffic period
- [ ] Monitor logs in real-time
- [ ] Check error rates
- [ ] Verify all existing functionality
- [ ] Test new functionality
- [ ] Monitor for 1 hour minimum

### 3. Post-Deployment
- [ ] All health checks passing
- [ ] No increase in error rates
- [ ] Performance metrics normal
- [ ] User feedback monitored
- [ ] Document any issues

---

## Rollback Criteria

Immediately rollback if ANY of these occur:

- [ ] Error rate increases by > 5%
- [ ] Any existing page returns 500 errors
- [ ] Homepage doesn't load
- [ ] Authentication stops working
- [ ] Database connection errors
- [ ] Performance degrades significantly
- [ ] User reports of broken functionality

---

## Component-Specific Checklists

### Backend (core-api)

**Before modifying:**
- [ ] Review existing routers and their endpoints
- [ ] Check existing service implementations
- [ ] Verify database models and migrations
- [ ] Test existing API endpoints

**After modifying:**
- [ ] All existing endpoints still return 200 OK
- [ ] Database migrations are backward compatible
- [ ] No breaking changes to API contracts
- [ ] Existing tests pass
- [ ] New endpoints documented

### Frontend (anzx-marketing)

**Before modifying:**
- [ ] Review existing component structure
- [ ] Check existing styling and layout
- [ ] Verify routing configuration
- [ ] Test existing pages

**After modifying:**
- [ ] All existing pages load correctly
- [ ] Navigation still works
- [ ] Styling is consistent
- [ ] No layout shifts
- [ ] Mobile responsive
- [ ] Accessibility maintained

### Infrastructure

**Before modifying:**
- [ ] Review existing Terraform/infrastructure code
- [ ] Check current resource configurations
- [ ] Verify IAM roles and permissions
- [ ] Document current state

**After modifying:**
- [ ] No changes to existing resources
- [ ] New resources properly tagged
- [ ] IAM follows least-privilege
- [ ] Costs estimated
- [ ] Terraform plan reviewed

---

## Emergency Contacts

**If something breaks:**

1. **Immediate Actions:**
   - Stop deployment
   - Rollback to previous version
   - Check logs for errors
   - Notify team

2. **Escalation:**
   - Technical Lead: [Contact]
   - DevOps Engineer: [Contact]
   - On-Call Engineer: [Contact]

3. **Communication:**
   - Post in team Slack channel
   - Update status page if customer-facing
   - Document incident

---

## Testing Checklist by Component

### Homepage (/)
- [ ] Page loads without errors
- [ ] Hero section displays correctly
- [ ] Agent cards render properly
- [ ] "Hire Me" buttons work (new)
- [ ] "Learn More" buttons work (existing)
- [ ] Navigation menu works
- [ ] Footer links work
- [ ] Mobile responsive

### Get Started Page (/get-started)
- [ ] Page loads without errors
- [ ] Google sign-up form displays (new)
- [ ] URL parameters work (?agent=emma) (new)
- [ ] Existing content preserved
- [ ] Form submission works (new)
- [ ] Error handling works (new)

### Agent Detail Pages
- [ ] All agent pages load
- [ ] Content displays correctly
- [ ] Images load
- [ ] Links work
- [ ] No console errors

### API Endpoints (core-api)
- [ ] GET /health returns 200
- [ ] POST /api/v1/auth/login works
- [ ] GET /api/v1/agents works
- [ ] POST /api/v1/agents works
- [ ] POST /api/v1/public/signup works (new)
- [ ] POST /api/v1/public/agents/provision works (new)
- [ ] GET /api/v1/public/agents/:id/status works (new)

---

## Success Criteria

### Existing Functionality
- ✅ All existing pages load correctly
- ✅ All existing API endpoints work
- ✅ No increase in error rates
- ✅ Performance metrics unchanged
- ✅ All existing tests pass

### New Functionality
- ✅ New features work as designed
- ✅ New tests pass
- ✅ Documentation complete
- ✅ Monitoring configured
- ✅ No security vulnerabilities

---

## Sign-Off

Before marking any task as complete:

- [ ] Developer: Tested locally and in staging
- [ ] Code Reviewer: Reviewed and approved
- [ ] QA: Tested in staging environment
- [ ] Tech Lead: Approved for production
- [ ] DevOps: Deployment successful

**Remember:** It's better to take extra time to test thoroughly than to break production!

