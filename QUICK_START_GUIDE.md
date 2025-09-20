# ANZX AI Platform - Quick Start Guide

**For any LLM continuing this project**

## 🚀 **IMMEDIATE ACTIONS NEEDED**

### **1. Fix Database Connection (CRITICAL)**
```bash
# Run the database fix script
./fix_database_connection.sh
```
**What it does:**
- Diagnoses database connection issues
- Resets database user password
- Updates Cloud Run environment variables
- Tests API connectivity
- Updates Terraform configuration

### **2. Import Manual Resources to Terraform**
```bash
# Import manually created resources
./import_manual_resources.sh
```
**What it does:**
- Imports database user to Terraform state
- Verifies all resources are managed
- Checks for configuration drift
- Provides resource summary

### **3. Verify Everything is Working**
```bash
# Quick health check
curl -s https://anzx-ai-platform-core-api-ymh6bmf7oq-ts.a.run.app/health | jq .

# Test database connectivity
curl -s https://anzx-ai-platform-core-api-ymh6bmf7oq-ts.a.run.app/assistants | jq .
```

## 📁 **KEY FILES TO UNDERSTAND**

1. **`PROJECT_STATE_COMPLETE.md`** - Complete project documentation
2. **`infrastructure/terraform/main.tf`** - Infrastructure definition
3. **`services/core-api/app/main.py`** - API entry point
4. **`services/core-api/app/services/vertex_ai_service.py`** - AI integration
5. **`fix_database_connection.sh`** - Database fix script
6. **`import_manual_resources.sh`** - State management script

## 🎯 **CURRENT STATUS**

### ✅ **Working**
- Core API deployed and healthy
- Authentication system functional
- Infrastructure properly configured
- Docker images built and deployed
- Comprehensive testing framework ready

### 🔴 **Broken**
- Database connection (authentication failure)
- Assistant endpoints (due to database)
- Full customer testing (needs database)

### 🟡 **Needs Work**
- Test user creation
- Sample data population
- End-to-end testing execution

## 🔧 **AFTER FIXING DATABASE**

### **Create Test Data**
```bash
# Set up test environment
cd services/core-api
python -m pip install -r requirements.txt
python ../../../test_user_setup.py
```

### **Run Comprehensive Tests**
```bash
# Unit tests
python -m pytest tests/ --cov=app

# Integration tests
python -m pytest tests/integration/ -v

# Customer journey tests
python ../../../customer_testing_scenarios.py
```

### **Deploy Additional Features**
```bash
# Deploy chat widget
cd services/chat-widget
npm install
npm run build
npm run deploy

# Deploy website
cd ../../website
# Deploy to hosting platform
```

## 🌐 **LIVE ENDPOINTS**

- **API Base:** https://anzx-ai-platform-core-api-ymh6bmf7oq-ts.a.run.app
- **Health Check:** `/health` ✅
- **API Docs:** `/docs` ✅
- **OpenAPI Schema:** `/openapi.json` ✅
- **Assistants:** `/assistants` ⚠️ (Database issue)

## 🔑 **ENVIRONMENT SETUP**

```bash
# Set up Google Cloud
export PROJECT_ID="extreme-gecko-466211-t1"
export REGION="australia-southeast1"
gcloud config set project $PROJECT_ID
gcloud auth application-default login

# Verify access
gcloud run services list --region=$REGION
```

## 📊 **SUCCESS CRITERIA**

After running the fix scripts, you should see:

1. **Health endpoint returns 200 OK**
2. **Assistants endpoint returns `{"assistants": []}` instead of database error**
3. **Terraform state shows all resources**
4. **No authentication errors in logs**

## 🆘 **IF SOMETHING GOES WRONG**

### **Database Still Not Working**
1. Check Cloud SQL instance status: `gcloud sql instances describe anzx-ai-platform-db`
2. Verify network connectivity between Cloud Run and Cloud SQL
3. Check Cloud Run logs: `gcloud run services logs read anzx-ai-platform-core-api --region=australia-southeast1`

### **Terraform Issues**
1. Check state lock: `terraform force-unlock <LOCK_ID>`
2. Refresh state: `terraform refresh`
3. Re-import resources: Run `import_manual_resources.sh` again

### **API Not Responding**
1. Check service status: `gcloud run services describe anzx-ai-platform-core-api --region=australia-southeast1`
2. Check recent deployments: `gcloud run revisions list --service=anzx-ai-platform-core-api --region=australia-southeast1`
3. Redeploy if needed: `cd infrastructure/terraform && terraform apply`

## 🎉 **ONCE EVERYTHING IS WORKING**

You'll have a fully functional AI platform with:
- ✅ 6 different AI agent types
- ✅ Complete API for agent management
- ✅ Knowledge base integration
- ✅ Analytics and monitoring
- ✅ Comprehensive testing framework
- ✅ Production-ready infrastructure

**Start with the database fix script and work through the checklist above!**