#!/bin/bash

# ANZx.ai Platform GCP Setup Script
# This script sets up the initial GCP projects and prerequisites

set -e

ORGANIZATION_ID=${1:-""}
BILLING_ACCOUNT_ID=${2:-""}

if [ -z "$ORGANIZATION_ID" ] || [ -z "$BILLING_ACCOUNT_ID" ]; then
    echo "Usage: ./setup-gcp.sh [ORGANIZATION_ID] [BILLING_ACCOUNT_ID]"
    echo ""
    echo "To find your organization ID:"
    echo "  gcloud organizations list"
    echo ""
    echo "To find your billing account ID:"
    echo "  gcloud billing accounts list"
    exit 1
fi

echo "🚀 Setting up ANZx.ai Platform on GCP"
echo "Organization ID: $ORGANIZATION_ID"
echo "Billing Account: $BILLING_ACCOUNT_ID"
echo "================================"

# Create projects
PROJECTS=("anzx-ai-dev" "anzx-ai-staging" "anzx-ai-prod")

for PROJECT_ID in "${PROJECTS[@]}"; do
    echo "📦 Creating project: $PROJECT_ID"
    
    # Create project
    gcloud projects create "$PROJECT_ID" \
        --organization="$ORGANIZATION_ID" \
        --name="ANZx.ai Platform - ${PROJECT_ID##*-}" \
        --set-as-default
    
    # Link billing account
    gcloud billing projects link "$PROJECT_ID" \
        --billing-account="$BILLING_ACCOUNT_ID"
    
    # Enable required APIs for Terraform
    echo "🔧 Enabling APIs for $PROJECT_ID..."
    gcloud services enable \
        cloudresourcemanager.googleapis.com \
        cloudbilling.googleapis.com \
        iam.googleapis.com \
        serviceusage.googleapis.com \
        --project="$PROJECT_ID"
    
    # Create Terraform state bucket
    echo "🗄️  Creating Terraform state bucket for $PROJECT_ID..."
    gsutil mb -p "$PROJECT_ID" -l australia-southeast1 "gs://anzx-terraform-state-${PROJECT_ID##*-}"
    
    # Enable versioning on state bucket
    gsutil versioning set on "gs://anzx-terraform-state-${PROJECT_ID##*-}"
    
    echo "✅ Project $PROJECT_ID setup complete!"
    echo ""
done

# Create service account for Terraform
echo "🔐 Creating Terraform service account..."
gcloud iam service-accounts create terraform-sa \
    --display-name="Terraform Service Account" \
    --description="Service account for Terraform deployments" \
    --project="anzx-ai-dev"

# Grant necessary permissions to Terraform service account
TERRAFORM_SA="terraform-sa@anzx-ai-dev.iam.gserviceaccount.com"

for PROJECT_ID in "${PROJECTS[@]}"; do
    echo "🔑 Granting permissions to Terraform SA for $PROJECT_ID..."
    
    # Project-level permissions
    gcloud projects add-iam-policy-binding "$PROJECT_ID" \
        --member="serviceAccount:$TERRAFORM_SA" \
        --role="roles/editor"
    
    gcloud projects add-iam-policy-binding "$PROJECT_ID" \
        --member="serviceAccount:$TERRAFORM_SA" \
        --role="roles/iam.serviceAccountAdmin"
    
    gcloud projects add-iam-policy-binding "$PROJECT_ID" \
        --member="serviceAccount:$TERRAFORM_SA" \
        --role="roles/storage.admin"
done

# Create and download service account key
echo "🔑 Creating service account key..."
gcloud iam service-accounts keys create terraform-key.json \
    --iam-account="$TERRAFORM_SA" \
    --project="anzx-ai-dev"

echo ""
echo "🎉 GCP setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Set the GOOGLE_APPLICATION_CREDENTIALS environment variable:"
echo "   export GOOGLE_APPLICATION_CREDENTIALS=$(pwd)/terraform-key.json"
echo ""
echo "2. Initialize and deploy the development environment:"
echo "   cd infrastructure"
echo "   ./scripts/deploy.sh dev init"
echo "   ./scripts/deploy.sh dev plan"
echo "   ./scripts/deploy.sh dev apply"
echo ""
echo "3. Update the GitHub repository settings with the project IDs in:"
echo "   - infrastructure/terraform/cloudbuild.tf"
echo "   - infrastructure/cloudbuild/*.yaml files"
echo ""
echo "⚠️  Important: Store the terraform-key.json file securely and never commit it to version control!"