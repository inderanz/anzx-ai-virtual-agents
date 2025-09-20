#!/bin/bash

# ANZX AI Platform - Import Manual Resources to Terraform State
# This script imports manually created resources into Terraform state management

set -e

PROJECT_ID="extreme-gecko-466211-t1"
REGION="australia-southeast1"
DB_INSTANCE="anzx-ai-platform-db"

echo "🚀 Starting import of manual resources to Terraform state..."
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "=================================="

# Change to terraform directory
cd infrastructure/terraform

# Initialize terraform if needed
echo "📋 Initializing Terraform..."
terraform init

echo "🔍 Checking current Terraform state..."
terraform state list

echo ""
echo "🔧 Importing manually created resources..."

# Import database user if it exists but not in state
echo "📊 Checking database user..."
if gcloud sql users describe anzx_user --instance=$DB_INSTANCE --quiet 2>/dev/null; then
    echo "✅ Database user 'anzx_user' exists"
    
    # Check if already in state
    if terraform state show google_sql_user.user 2>/dev/null; then
        echo "ℹ️  Database user already in Terraform state"
    else
        echo "📥 Importing database user to Terraform state..."
        terraform import google_sql_user.user "anzx_user/$DB_INSTANCE" || echo "⚠️  Import failed or already exists"
    fi
else
    echo "❌ Database user 'anzx_user' not found - needs to be created"
fi

# Verify all resources are in state
echo ""
echo "🔍 Final state verification..."
terraform state list

echo ""
echo "📋 Checking for any drift..."
terraform plan -detailed-exitcode || {
    exit_code=$?
    if [ $exit_code -eq 2 ]; then
        echo "⚠️  Terraform detected configuration drift"
        echo "Run 'terraform apply' to fix any issues"
    elif [ $exit_code -eq 1 ]; then
        echo "❌ Terraform plan failed"
        exit 1
    else
        echo "✅ No configuration drift detected"
    fi
}

echo ""
echo "🎉 Resource import process completed!"
echo ""
echo "📝 Next steps:"
echo "1. Review any drift detected above"
echo "2. Run 'terraform apply' if needed to fix configuration"
echo "3. Test database connectivity: gcloud sql connect $DB_INSTANCE --user=anzx_user"
echo "4. Verify API endpoints are working with database"

# Generate a summary report
echo ""
echo "📊 RESOURCE SUMMARY REPORT"
echo "=========================="

echo "🏗️  Infrastructure Resources:"
terraform state list | grep -E "(google_cloud_run_service|google_sql|google_redis|google_storage)" | while read resource; do
    echo "  ✅ $resource"
done

echo ""
echo "🔐 Security Resources:"
terraform state list | grep -E "(google_service_account|google_project_iam)" | while read resource; do
    echo "  ✅ $resource"
done

echo ""
echo "🌐 Network Resources:"
terraform state list | grep -E "(google_compute_network|google_compute_subnetwork)" | while read resource; do
    echo "  ✅ $resource"
done

echo ""
echo "📦 Storage Resources:"
terraform state list | grep -E "(google_storage_bucket|google_artifact_registry)" | while read resource; do
    echo "  ✅ $resource"
done

echo ""
echo "🔧 Manual verification commands:"
echo "  gcloud sql instances describe $DB_INSTANCE"
echo "  gcloud sql users list --instance=$DB_INSTANCE"
echo "  gcloud run services list --region=$REGION"
echo "  curl -s https://anzx-ai-platform-core-api-ymh6bmf7oq-ts.a.run.app/health"

echo ""
echo "✨ Import process complete! Check the summary above for any issues."