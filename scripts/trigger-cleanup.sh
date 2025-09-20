#!/bin/bash

# ANZX AI Platform - Trigger Complete Cleanup via Cloud Build
# This script triggers the cleanup Cloud Build job

set -e

PROJECT_ID="extreme-gecko-466211-t1"

echo "=== ANZX AI Platform - Trigger Cleanup ==="
echo "Project: $PROJECT_ID"
echo ""

echo "⚠️  WARNING: This will DELETE ALL existing resources!"
echo "   - Cloud Run services"
echo "   - Cloud SQL databases"
echo "   - Redis instances"
echo "   - VPC networks"
echo "   - Storage buckets"
echo "   - Terraform state"
echo ""

read -p "Are you sure you want to proceed? (type 'yes' to confirm): " -r
if [[ ! $REPLY == "yes" ]]; then
    echo "Cleanup cancelled."
    exit 0
fi

echo "Triggering cleanup Cloud Build job..."
BUILD_ID=$(gcloud builds submit \
    --config=cloudbuild-cleanup.yaml \
    --project=$PROJECT_ID \
    --format="value(id)")

if [ $? -eq 0 ]; then
    echo "✓ Cleanup job submitted successfully"
    echo "Build ID: $BUILD_ID"
    echo ""
    echo "Monitor the cleanup:"
    echo "  Web Console: https://console.cloud.google.com/cloud-build/builds/$BUILD_ID?project=$PROJECT_ID"
    echo "  CLI: gcloud builds log $BUILD_ID --stream --project=$PROJECT_ID"
    echo ""
    
    read -p "Follow cleanup logs? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        gcloud builds log $BUILD_ID --stream --project=$PROJECT_ID
    fi
else
    echo "✗ Failed to submit cleanup job"
    exit 1
fi