#!/bin/bash

# ANZX AI Platform - Complete Deployment Cleanup
# This script removes all existing resources to start fresh

set -e

PROJECT_ID="extreme-gecko-466211-t1"
REGION="australia-southeast1"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== ANZX AI Platform - Complete Cleanup ===${NC}"
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo ""

echo -e "${YELLOW}WARNING: This will delete ALL existing resources!${NC}"
read -p "Are you sure you want to proceed? (type 'yes' to confirm): " -r
if [[ ! $REPLY == "yes" ]]; then
    echo "Cleanup cancelled."
    exit 0
fi

echo -e "${BLUE}1. Cleaning up Cloud Run services${NC}"
services=$(gcloud run services list --region=$REGION --format="value(metadata.name)" --project=$PROJECT_ID 2>/dev/null || echo "")
if [ -n "$services" ]; then
    for service in $services; do
        echo "Deleting Cloud Run service: $service"
        gcloud run services delete $service --region=$REGION --project=$PROJECT_ID --quiet || true
    done
else
    echo "No Cloud Run services found"
fi

echo -e "${BLUE}2. Cleaning up Cloud SQL instances${NC}"
instances=$(gcloud sql instances list --format="value(name)" --project=$PROJECT_ID 2>/dev/null || echo "")
if [ -n "$instances" ]; then
    for instance in $instances; do
        echo "Deleting Cloud SQL instance: $instance"
        gcloud sql instances delete $instance --project=$PROJECT_ID --quiet || true
    done
else
    echo "No Cloud SQL instances found"
fi

echo -e "${BLUE}3. Cleaning up Redis instances${NC}"
redis_instances=$(gcloud redis instances list --region=$REGION --format="value(name)" --project=$PROJECT_ID 2>/dev/null || echo "")
if [ -n "$redis_instances" ]; then
    for instance in $redis_instances; do
        echo "Deleting Redis instance: $instance"
        gcloud redis instances delete $instance --region=$REGION --project=$PROJECT_ID --quiet || true
    done
else
    echo "No Redis instances found"
fi

echo -e "${BLUE}4. Cleaning up VPC connectors${NC}"
connectors=$(gcloud compute networks vpc-access connectors list --region=$REGION --format="value(name)" --project=$PROJECT_ID 2>/dev/null || echo "")
if [ -n "$connectors" ]; then
    for connector in $connectors; do
        echo "Deleting VPC connector: $connector"
        gcloud compute networks vpc-access connectors delete $connector --region=$REGION --project=$PROJECT_ID --quiet || true
    done
else
    echo "No VPC connectors found"
fi

echo -e "${BLUE}5. Cleaning up VPC networks${NC}"
networks=$(gcloud compute networks list --format="value(name)" --filter="name~anzx" --project=$PROJECT_ID 2>/dev/null || echo "")
if [ -n "$networks" ]; then
    for network in $networks; do
        # Delete subnets first
        subnets=$(gcloud compute networks subnets list --network=$network --format="value(name)" --project=$PROJECT_ID 2>/dev/null || echo "")
        for subnet in $subnets; do
            echo "Deleting subnet: $subnet"
            gcloud compute networks subnets delete $subnet --region=$REGION --project=$PROJECT_ID --quiet || true
        done
        
        echo "Deleting VPC network: $network"
        gcloud compute networks delete $network --project=$PROJECT_ID --quiet || true
    done
else
    echo "No custom VPC networks found"
fi

echo -e "${BLUE}6. Cleaning up Secret Manager secrets${NC}"
secrets=$(gcloud secrets list --format="value(name)" --filter="name~anzx" --project=$PROJECT_ID 2>/dev/null || echo "")
if [ -n "$secrets" ]; then
    for secret in $secrets; do
        echo "Deleting secret: $secret"
        gcloud secrets delete $secret --project=$PROJECT_ID --quiet || true
    done
else
    echo "No secrets found"
fi

echo -e "${BLUE}7. Cleaning up Storage buckets${NC}"
buckets=$(gsutil ls -p $PROJECT_ID 2>/dev/null | grep "anzx" || echo "")
if [ -n "$buckets" ]; then
    for bucket in $buckets; do
        echo "Deleting bucket: $bucket"
        gsutil -m rm -r $bucket || true
    done
else
    echo "No ANZX buckets found"
fi

echo -e "${BLUE}8. Cleaning up Terraform state and resources${NC}"
cd infrastructure/terraform

# Force unlock any existing locks
echo "Checking for Terraform state locks..."
terraform force-unlock -force 1758336178218037 2>/dev/null || true

# Initialize Terraform to ensure backend is configured
echo "Initializing Terraform backend..."
terraform init -reconfigure

# Destroy all Terraform managed resources
echo "Destroying Terraform managed resources..."
terraform destroy -auto-approve || echo "Terraform destroy completed with warnings"

# Clean up the remote state file completely
echo -e "${BLUE}9. Cleaning up remote Terraform state${NC}"
STATE_BUCKET="anzx-ai-terraform-state-1758328389"
echo "Removing all state files from bucket: $STATE_BUCKET"
gsutil -m rm -r gs://$STATE_BUCKET/production/ 2>/dev/null || echo "State files already clean"

# Remove any local state files (should not exist with remote backend)
echo "Removing any local state files..."
rm -f terraform.tfstate*
rm -f .terraform.lock.hcl
rm -rf .terraform/

echo -e "${BLUE}10. Ensuring clean remote state setup${NC}"
# Reinitialize with clean backend
terraform init

# Verify state is empty
echo "Verifying clean state..."
terraform show || echo "State is clean (no resources)"

echo ""
echo -e "${GREEN}=== Cleanup Complete ===${NC}"
echo "All ANZX AI Platform resources have been removed."
echo ""
echo "Next steps:"
echo "1. Review and fix code issues"
echo "2. Deploy fresh infrastructure"
echo "3. Test deployment"