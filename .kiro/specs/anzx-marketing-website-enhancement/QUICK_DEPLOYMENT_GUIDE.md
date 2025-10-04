# ANZX Marketing - Quick Deployment Guide

## 🚀 Deploy in 5 Steps

### Step 1: Create Secret (One-time)
```bash
echo "https://anzx-marketing.pages.dev" | \
  gcloud secrets create ANZX_MARKETING_URL \
  --data-file=- \
  --project=anzx-ai-platform
```

### Step 2: Verify Prerequisites
```bash
# Check authentication
gcloud auth list

# Verify secrets exist
gcloud secrets list --project=anzx-ai-platform --filter="name:CLOUDFLARE OR name:CRICKET"
```

### Step 3: Deploy
```bash
# Run deployment script
./scripts/deploy-anzx-marketing.sh
```

### Step 4: Verify
```bash
# Visit website
open https://anzx.ai

# Verify cricket chatbot
open https://anzx.ai/cricket
```

### Step 5: Monitor
- Check Cloud Build logs
- Monitor analytics
- Watch for errors

---

## 📋 Quick Checklist

**Before Deployment:**
- [ ] Tests passing
- [ ] Build succeeds locally
- [ ] Secrets configured
- [ ] `.env.production` created

**After Deployment:**
- [ ] Homepage loads
- [ ] Cricket chatbot works
- [ ] Forms submit
- [ ] Analytics tracking
- [ ] No console errors

---

## 🔄 Quick Rollback

**Via Cloudflare Dashboard:**
1. Login to Cloudflare
2. Pages → anzx-marketing
3. Select previous deployment
4. Click "Rollback"

---

## 📞 Quick Reference

**Project**: anzx-ai-platform
**Region**: australia-southeast1
**Domain**: https://anzx.ai
**Cricket**: https://anzx.ai/cricket

**Pipeline**: `infrastructure/cloudbuild/pipelines/anzx-marketing-deploy.yaml`
**Script**: `scripts/deploy-anzx-marketing.sh`

---

## 🆘 Troubleshooting

**Build fails?**
```bash
cd services/anzx-marketing
npm run build
```

**Worker not routing?**
- Check Cloudflare dashboard
- Verify environment variables
- Check worker logs

**Cricket broken?**
- Rollback worker immediately
- Check CRICKET_CHATBOT_URL secret

---

**Full Documentation**: See `DEPLOYMENT_CHECKLIST.md` and `DEPLOYMENT.md`
