#!/bin/bash

# ANZX Marketing - Deployment Script
# Deploys to Cloudflare Pages via Google Cloud Build

set -e

echo "🚀 ANZX Marketing Deployment"
echo "=============================="
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI is not installed"
    echo "Install from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if logged in
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" &> /dev/null; then
    echo "❌ Not logged in to gcloud"
    echo "Run: gcloud auth login"
    exit 1
fi

# Get project ID
PROJECT_ID=$(gcloud config get-value project)
echo "📦 Project: $PROJECT_ID"
echo ""

# Confirm deployment
read -p "Deploy to production? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Deployment cancelled"
    exit 1
fi

echo ""
echo "🔨 Starting deployment..."
echo ""

# Submit build
gcloud builds submit \
  --config=services/anzx-marketing/cloudbuild.yaml \
  --substitutions=_CORE_API_URL="https://api.anzx.ai",_CHAT_WIDGET_URL="https://chat.anzx.ai" \
  .

echo ""
echo "✅ Deployment complete!"
echo ""
echo "🌐 Site will be available at: https://anzx.ai"
echo "📊 View deployment: https://console.cloud.google.com/cloud-build"
echo ""
