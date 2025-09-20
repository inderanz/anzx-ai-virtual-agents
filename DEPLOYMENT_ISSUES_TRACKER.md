# ANZx AI Platform - Deployment Issues Tracker

This document tracks all deployment issues encountered and their solutions to prevent recurring problems.

## 🚨 Current Active Issues

### Issue #006: Resources Already Exist
**Status:** 🔴 ACTIVE  
**Date:** 2024-12-19  
**Component:** Terraform Infrastructure  
**Error:** Multiple "already exists" errors for Artifact Registry, Redis, Secrets  
**Root Cause:** Resources were created in previous runs but not tracked in Terraform state  
**Impact:** Cannot create infrastructure via Terraform  
**Workaround:** Import existing resources or delete and recreate  
**Permanent Fix Needed:**
- [ ] Import existing resources into Terraform state
- [ ] Or delete existing resources and recreate

### Issue #007: Invalid Database Flag for pgvector
**Status:** 🟡 IN PROGRESS  
**Date:** 2024-12-19  
**Component:** Cloud SQL PostgreSQL  
**Error:** `invalidFlagName` for shared_preload_libraries=vector  
**Root Cause:** Incorrect flag syntax for pgvector extension in Cloud SQL  
**Impact:** Cannot create PostgreSQL database with vector support (CRITICAL for AI features)  
**Research:** pgvector is available in Cloud SQL PostgreSQL but needs different configuration  
**Permanent Fix Needed:**
- [ ] Use correct database flag syntax for pgvector
- [ ] Verify pgvector is supported in PostgreSQL 15 on Cloud SQL
- [ ] Test vector operations after deployment

### Issue #008: Docker Build Failing - Missing Package
**Status:** 🔴 ACTIVE  
**Date:** 2024-12-19  
**Component:** Core API Docker Build  
**Error:** `Could not find a version that satisfies the requirement google-cloud-sql-connector==1.4.3`  
**Root Cause:** Package version not available or incorrect package name  
**Impact:** Cannot build Docker images for deployment  
**Workaround:** Update requirements.txt with correct package versions  
**Permanent Fix Needed:**
- [ ] Update google-cloud-sql-connector to available version
- [ ] Verify all package versions in requirements-prod.txt
- [ ] Test Docker build locally

### Issue #001: SQL API Permission Denied
**Status:** 🔴 ACTIVE  
**Date:** 2024-12-19  
**Component:** Terraform Infrastructure  
**Error:**
```
Error 403: Not found or permission denied for service(s): sql.googleapis.com
Help Token: AVSZLmuO4HOw3FTjn6N_k4IOIG2htYvYfaq-gBJcF-Q45yQWw3BnpLDk-swbZUB7UzTh1yvb2bt9aHp1Mkv95w5Rmqrmwr0sTOuE5yaaSUnzMWfc
```

**Root Cause:** GCP project doesn't have proper permissions or billing enabled for Cloud SQL API  
**Impact:** Cannot create Cloud SQL PostgreSQL database via Terraform  
**Workaround:** Removed sql.googleapis.com from Terraform and will create manually  
**Permanent Fix Needed:** 
- [ ] Enable billing on GCP project
- [ ] Verify Cloud SQL API permissions
- [ ] Re-add to Terraform once permissions resolved

---

### Issue #002: Kiro IDE Auto-formatting Breaking Code
**Status:** 🔴 ACTIVE  
**Date:** 2024-12-19  
**Component:** Website Files (HTML/CSS/JS)  
**Error:** Auto-formatting removes advanced animations and breaks JavaScript syntax  

**Root Cause:** Kiro IDE auto-formatting is too aggressive and removes custom code  
**Impact:** Website loses enterprise-grade animations and interactive features  
**Workaround:** Restore files manually after auto-formatting  
**Permanent Fix Needed:**
- [ ] Configure Kiro IDE formatting rules
- [ ] Use .editorconfig to preserve formatting
- [ ] Consider disabling auto-format for specific files

---

## ✅ Resolved Issues

### Issue #003: Terraform State Lock (Recurring)
**Status:** 🔴 ACTIVE  
**Date:** 2024-12-19  
**Component:** Terraform Infrastructure  
**Error:** `Error acquiring the state lock` - Lock ID: 1758216868911907  
**Root Cause:** Terraform operations interrupted leaving stale locks  
**Solution:** Use `terraform force-unlock [LOCK_ID]`  
**Prevention:** Always run `terraform plan` before `terraform apply`, ensure clean exits

---

### Issue #004: OpenAI References in Terraform
**Status:** ✅ RESOLVED  
**Date:** 2024-12-19  
**Component:** Terraform Variables  
**Error:** OpenAI API key variable when using Vertex AI  
**Solution:** Removed `openai_api_key` variable from `variables.tf`  
**Prevention:** Code review to ensure only Google services are referenced

---

### Issue #005: Duplicate Terraform Resources
**Status:** ✅ RESOLVED  
**Date:** 2024-12-19  
**Component:** Terraform Configuration  
**Error:** Multiple main.tf files causing duplicate resource definitions  
**Solution:** Consolidated into single clean main.tf file  
**Prevention:** Use single main.tf or proper module structure

---

## 🔧 Infrastructure Issues

### Database Configuration
- **Issue:** Cloud SQL requires manual setup due to API permissions
- **Current State:** Using local PostgreSQL for development
- **Action Required:** Enable Cloud SQL API and create production database

### Container Registry
- **Issue:** Docker images not yet built and pushed
- **Current State:** Terraform references non-existent images
- **Action Required:** Build and push Docker images before Cloud Run deployment

### Vertex AI Configuration
- **Issue:** Need to verify Vertex AI Agent Builder permissions
- **Current State:** API enabled but not tested
- **Action Required:** Test Vertex AI connectivity and permissions

---

## 🚀 Deployment Checklist

### Pre-deployment Requirements
- [ ] GCP billing enabled
- [ ] All required APIs enabled with proper permissions
- [ ] Docker images built and pushed to Artifact Registry
- [ ] Database schema migrated
- [ ] Environment variables configured
- [ ] SSL certificates configured
- [ ] Domain DNS configured

### Post-deployment Verification
- [ ] All Cloud Run services healthy
- [ ] Database connectivity working
- [ ] Redis connectivity working
- [ ] Vertex AI integration working
- [ ] Website loading correctly
- [ ] API endpoints responding
- [ ] Monitoring and logging active

---

## 📋 Known Limitations

### Current Architecture Constraints
1. **Database:** Using public IP instead of private VPC (security concern)
2. **SSL:** Not enforced on database connections (security concern)
3. **Monitoring:** Basic monitoring only, need comprehensive observability
4. **Backup:** Automated backups configured but not tested
5. **Scaling:** Auto-scaling configured but not load tested

### Technical Debt
1. **Error Handling:** Need comprehensive error handling in all services
2. **Testing:** Missing integration tests for Cloud Run deployment
3. **Security:** Need to implement proper IAM roles and service accounts
4. **Documentation:** API documentation needs updating for production URLs

---

## 🔄 Continuous Improvement

### Automation Needed
- [ ] Automated Docker image building and pushing
- [ ] Automated database migrations
- [ ] Automated testing pipeline
- [ ] Automated rollback procedures
- [ ] Automated monitoring setup

### Monitoring and Alerting
- [ ] Set up comprehensive logging
- [ ] Configure performance monitoring
- [ ] Set up error alerting
- [ ] Create operational dashboards
- [ ] Implement health checks

---

## 📞 Emergency Contacts & Resources

### GCP Support
- Project ID: `extreme-gecko-466211-t1`
- Region: `australia-southeast1`
- Support Level: Basic

### Key Resources
- Terraform State: `gs://anzx-ai-terraform-state/production`
- Artifact Registry: `australia-southeast1-docker.pkg.dev/extreme-gecko-466211-t1/anzx-ai-platform-docker`
- Monitoring: Google Cloud Console

---

## 📝 Issue Reporting Template

When adding new issues, use this template:

```markdown
### Issue #XXX: [Brief Description]
**Status:** 🔴 ACTIVE / 🟡 IN PROGRESS / ✅ RESOLVED  
**Date:** YYYY-MM-DD  
**Component:** [Component Name]  
**Error:** [Error message or description]  
**Root Cause:** [Analysis of why this happened]  
**Impact:** [What this affects]  
**Workaround:** [Temporary solution if any]  
**Permanent Fix Needed:** [What needs to be done]
- [ ] Action item 1
- [ ] Action item 2
```

---

**Last Updated:** 2024-12-19  
**Next Review:** 2024-12-20  
**Maintained By:** Development Team