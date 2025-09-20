#!/bin/bash

# ANZX AI Platform - Production Deployment Script
set -e

PROJECT_ID="extreme-gecko-466211-t1"
REGION="australia-southeast1"

echo "🚀 Starting ANZX AI Platform deployment..."

# Deploy Core API
echo "📦 Deploying Core API..."
gcloud run deploy anzx-core-api \
  --image australia-southeast1-docker.pkg.dev/$PROJECT_ID/anzx-ai-platform-docker/core-api:latest \
  --region $REGION \
  --allow-unauthenticated \
  --port 8000 \
  --memory 2Gi \
  --cpu 2 \
  --min-instances 1 \
  --max-instances 10 \
  --timeout 300 \
  --set-env-vars "ENVIRONMENT=production,DATABASE_URL=postgresql://anzx_user:AnzxAI2024SecureDB@34.40.163.17:5432/anzx_ai_platform" \
  --quiet

# Deploy Knowledge Service
echo "📚 Deploying Knowledge Service..."
gcloud run deploy anzx-knowledge-service \
  --image australia-southeast1-docker.pkg.dev/$PROJECT_ID/anzx-ai-platform-docker/knowledge-service:latest \
  --region $REGION \
  --allow-unauthenticated \
  --port 8000 \
  --memory 1Gi \
  --cpu 1 \
  --min-instances 1 \
  --max-instances 5 \
  --timeout 300 \
  --set-env-vars "ENVIRONMENT=production" \
  --quiet

# Deploy Chat Widget
echo "💬 Deploying Chat Widget..."
gcloud run deploy anzx-chat-widget \
  --image australia-southeast1-docker.pkg.dev/$PROJECT_ID/anzx-ai-platform-docker/chat-widget:latest \
  --region $REGION \
  --allow-unauthenticated \
  --port 80 \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 1 \
  --max-instances 5 \
  --timeout 300 \
  --quiet

echo "✅ All services deployed successfully!"

# Get service URLs
echo "🌐 Service URLs:"
echo "Core API: $(gcloud run services describe anzx-core-api --region=$REGION --format='value(status.url)')"
echo "Knowledge Service: $(gcloud run services describe anzx-knowledge-service --region=$REGION --format='value(status.url)')"
echo "Chat Widget: $(gcloud run services describe anzx-chat-widget --region=$REGION --format='value(status.url)')"

echo "🎉 ANZX AI Platform deployed successfully!"