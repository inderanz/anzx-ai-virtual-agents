#!/bin/bash

# ANZX AI Platform - Fixed Infrastructure Deployment
# Addresses Terraform variable issues from previous deployment

set -e

PROJECT_ID="extreme-gecko-466211-t1"

echo "🔧 === ANZX AI Platform - Fixed Infrastructure Deployment ==="
echo "Project: $PROJECT_ID"
echo ""

echo "🚨 Previous deployment failed due to missing Terraform variables."
echo "This deployment includes all required variables with sensible defaults."
echo ""

# Check current status
echo "📋 Current Status:"
echo "----------------"

# Check images
echo "🐳 Docker Images:"
gcloud artifacts docker images list australia-southeast1-docker.pkg.dev/$PROJECT_ID/anzx-ai-platform-docker --format="table(IMAGE,TAGS,CREATE_TIME)" --limit=3

# Check services
echo ""
echo "☁️  Cloud Run Services:"
SERVICES=$(gcloud run services list --region=australia-southeast1 --project=$PROJECT_ID --format="value(metadata.name)" | wc -l)
echo "Current services: $SERVICES"

echo ""
echo "🔧 This deployment will:"
echo "  ✅ Use existing Docker images (no rebuild)"
echo "  🔧 Deploy infrastructure with ALL required Terraform variables"
echo "  🗄️  Create Cloud SQL database (free tier)"
echo "  🔄 Create Redis instance (free tier)"
echo "  ☁️  Deploy Cloud Run services"
echo "  🧪 Run comprehensive health checks"
echo ""

read -p "🚀 Continue with fixed infrastructure deployment? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Deployment cancelled."
    exit 0
fi

echo "🚀 Starting fixed infrastructure deployment..."
DEPLOY_BUILD_ID=$(gcloud builds submit \
    --config=cloudbuild-infrastructure-fixed.yaml \
    --project=$PROJECT_ID \
    --format="value(id)")

if [ $? -ne 0 ]; then
    echo "❌ Failed to submit fixed infrastructure deployment job"
    exit 1
fi

echo "⏳ Deployment submitted successfully!"
echo "📊 Build ID: $DEPLOY_BUILD_ID"
echo "🌐 Monitor: https://console.cloud.google.com/cloud-build/builds/$DEPLOY_BUILD_ID?project=$PROJECT_ID"
echo ""
echo "🔍 Following deployment logs..."

# Follow logs
gcloud builds log $DEPLOY_BUILD_ID --stream --project=$PROJECT_ID

# Check final status
echo ""
echo "🧪 Checking final deployment status..."

# Wait a moment for final status to propagate
sleep 10

# Get final build status
FINAL_STATUS=$(gcloud builds describe $DEPLOY_BUILD_ID --project=$PROJECT_ID --format="value(status)" 2>/dev/null || echo "UNKNOWN")

case $FINAL_STATUS in
    "SUCCESS")
        echo ""
        echo "🎉 ================================="
        echo "🎉 DEPLOYMENT SUCCESSFUL! 🎉"
        echo "🎉 ================================="
        
        # Try to get service URLs
        API_URL=$(gcloud run services describe anzx-ai-platform-core-api \
            --region=australia-southeast1 \
            --project=$PROJECT_ID \
            --format="value(status.url)" 2>/dev/null || echo "")
        
        if [ -n "$API_URL" ]; then
            echo ""
            echo "🌐 Your ANZX AI Platform is ready:"
            echo "   🚀 API: $API_URL"
            echo "   📚 Docs: $API_URL/docs"
            echo "   ❤️  Health: $API_URL/health"
            echo "   🤖 Assistants: $API_URL/assistants"
            echo ""
            echo "🧪 Quick test:"
            echo "   curl $API_URL/health"
            
            # Test the API
            echo ""
            echo "🔍 Testing API accessibility..."
            if curl -f -s --max-time 10 "$API_URL/health" >/dev/null 2>&1; then
                echo "✅ API is accessible and healthy!"
            else
                echo "⏳ API may still be starting up. Try again in a few minutes."
            fi
        else
            echo "⚠️  Services deployed but URLs not yet available. Check Cloud Console."
        fi
        ;;
    "FAILURE")
        echo ""
        echo "❌ ================================="
        echo "❌ DEPLOYMENT FAILED"
        echo "❌ ================================="
        echo ""
        echo "🔍 Check the build logs for details:"
        echo "   gcloud builds log $DEPLOY_BUILD_ID --project=$PROJECT_ID"
        echo ""
        echo "🌐 Or view in console:"
        echo "   https://console.cloud.google.com/cloud-build/builds/$DEPLOY_BUILD_ID?project=$PROJECT_ID"
        exit 1
        ;;
    *)
        echo ""
        echo "⏳ Deployment status: $FINAL_STATUS"
        echo "🔍 Check build status:"
        echo "   gcloud builds describe $DEPLOY_BUILD_ID --project=$PROJECT_ID"
        ;;
esac