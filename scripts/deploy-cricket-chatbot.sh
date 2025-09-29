#!/bin/bash

# ANZx Cricket Chatbot Deployment Script
# Deploys the cricket chatbot to Cloudflare Pages via Cloud Build

set -e

echo "🏏 Deploying ANZx Cricket Chatbot to Cloudflare Pages..."

# Configuration
PROJECT_ID="virtual-stratum-473511-u5"
REGION="australia-southeast1"
BUILD_CONFIG="infrastructure/cloudbuild/pipelines/cricket-chatbot-deploy-fixed.yaml"

# Check if we're in the right directory
if [ ! -f "services/cricket-marketing/package.json" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Check if gcloud is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "❌ Error: Please authenticate with gcloud first"
    echo "Run: gcloud auth login"
    exit 1
fi

# Set the project
echo "🔧 Setting project to $PROJECT_ID..."
gcloud config set project $PROJECT_ID

# Check if required secrets exist
echo "🔍 Checking required secrets..."
REQUIRED_SECRETS=("CLOUDFLARE_API_TOKEN" "CLOUDFLARE_ACCOUNT_ID")
for secret in "${REQUIRED_SECRETS[@]}"; do
    if ! gcloud secrets describe "$secret" >/dev/null 2>&1; then
        echo "❌ Error: Secret '$secret' not found in Secret Manager"
        echo "Please create the secret first:"
        echo "gcloud secrets create $secret --data-file=-"
        exit 1
    fi
done

echo "✅ All required secrets found"

# Submit the build
echo "🚀 Submitting Cloud Build job..."
gcloud builds submit \
    --config="$BUILD_CONFIG" \
    --substitutions="_PROJECT_ID=$PROJECT_ID,_REGION=$REGION" \
    --async

echo "✅ Build submitted successfully!"
echo "📊 Monitor the build at: https://console.cloud.google.com/cloud-build/builds?project=$PROJECT_ID"
echo "🌐 Once deployed, your cricket chatbot will be available at: https://anzx.ai/cricket"
