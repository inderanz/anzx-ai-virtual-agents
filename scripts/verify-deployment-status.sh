#!/bin/bash

# ANZX AI Platform - Deployment Status Verification Script
# Run this script to verify actual GCP deployment status

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID="extreme-gecko-466211-t1"
REGION="australia-southeast1"

echo -e "${BLUE}=== ANZX AI Platform Deployment Verification ===${NC}"
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo ""

# Function to check if a resource exists
check_resource() {
    local resource_type=$1
    local resource_name=$2
    local check_command=$3
    
    echo -n "Checking $resource_type '$resource_name'... "
    
    if eval "$check_command" >/dev/null 2>&1; then
        echo -e "${GREEN}✓ EXISTS${NC}"
        return 0
    else
        echo -e "${RED}✗ NOT FOUND${NC}"
        return 1
    fi
}

# Function to get resource status
get_resource_status() {
    local resource_type=$1
    local resource_name=$2
    local status_command=$3
    
    echo -n "Status of $resource_type '$resource_name'... "
    
    local status=$(eval "$status_command" 2>/dev/null || echo "NOT_FOUND")
    
    if [ "$status" = "NOT_FOUND" ]; then
        echo -e "${RED}NOT FOUND${NC}"
    elif [ "$status" = "READY" ] || [ "$status" = "RUNNING" ] || [ "$status" = "ACTIVE" ]; then
        echo -e "${GREEN}$status${NC}"
    else
        echo -e "${YELLOW}$status${NC}"
    fi
}

echo -e "${BLUE}1. Checking GCP Project and Authentication${NC}"
echo "Current project: $(gcloud config get-value project)"
echo "Current account: $(gcloud config get-value account)"
echo ""

echo -e "${BLUE}2. Checking Artifact Registry${NC}"
check_resource "Artifact Registry" "anzx-ai-registry" \
    "gcloud artifacts repositories describe anzx-ai-registry --location=$REGION --project=$PROJECT_ID"

echo ""
echo -e "${BLUE}3. Checking Docker Images in Artifact Registry${NC}"
echo "Listing images in registry..."
gcloud artifacts docker images list $REGION-docker.pkg.dev/$PROJECT_ID/anzx-ai-registry --format="table(IMAGE,TAGS,CREATE_TIME)" || echo "No images found or registry doesn't exist"

echo ""
echo -e "${BLUE}4. Checking Cloud SQL Instances${NC}"
check_resource "Cloud SQL Instance" "anzx-ai-postgres" \
    "gcloud sql instances describe anzx-ai-postgres --project=$PROJECT_ID"

get_resource_status "Cloud SQL Instance" "anzx-ai-postgres" \
    "gcloud sql instances describe anzx-ai-postgres --project=$PROJECT_ID --format='value(state)'"

echo ""
echo -e "${BLUE}5. Checking Memorystore Redis${NC}"
check_resource "Redis Instance" "anzx-ai-redis" \
    "gcloud redis instances describe anzx-ai-redis --region=$REGION --project=$PROJECT_ID"

get_resource_status "Redis Instance" "anzx-ai-redis" \
    "gcloud redis instances describe anzx-ai-redis --region=$REGION --project=$PROJECT_ID --format='value(state)'"

echo ""
echo -e "${BLUE}6. Checking GKE Clusters${NC}"
check_resource "GKE Cluster" "anzx-ai-cluster" \
    "gcloud container clusters describe anzx-ai-cluster --zone=$REGION-a --project=$PROJECT_ID"

get_resource_status "GKE Cluster" "anzx-ai-cluster" \
    "gcloud container clusters describe anzx-ai-cluster --zone=$REGION-a --project=$PROJECT_ID --format='value(status)'"

echo ""
echo -e "${BLUE}7. Checking Cloud Run Services${NC}"
services=("anzx-core-api" "anzx-knowledge-service" "anzx-chat-widget" "anzx-agent-orchestration")

for service in "${services[@]}"; do
    check_resource "Cloud Run Service" "$service" \
        "gcloud run services describe $service --region=$REGION --project=$PROJECT_ID"
    
    get_resource_status "Cloud Run Service" "$service" \
        "gcloud run services describe $service --region=$REGION --project=$PROJECT_ID --format='value(status.conditions[0].status)'"
done

echo ""
echo -e "${BLUE}8. Checking Load Balancer${NC}"
check_resource "Load Balancer" "anzx-ai-lb" \
    "gcloud compute url-maps describe anzx-ai-lb --global --project=$PROJECT_ID"

echo ""
echo -e "${BLUE}9. Checking SSL Certificates${NC}"
check_resource "SSL Certificate" "anzx-ai-ssl-cert" \
    "gcloud compute ssl-certificates describe anzx-ai-ssl-cert --global --project=$PROJECT_ID"

echo ""
echo -e "${BLUE}10. Checking VPC Network${NC}"
check_resource "VPC Network" "anzx-ai-vpc" \
    "gcloud compute networks describe anzx-ai-vpc --project=$PROJECT_ID"

echo ""
echo -e "${BLUE}11. Checking Cloud Storage Buckets${NC}"
buckets=("anzx-ai-terraform-state" "anzx-ai-uploads" "anzx-ai-backups")

for bucket in "${buckets[@]}"; do
    check_resource "Storage Bucket" "$bucket" \
        "gsutil ls -b gs://$bucket"
done

echo ""
echo -e "${BLUE}12. Checking Cloud Build Triggers${NC}"
echo "Cloud Build triggers:"
gcloud builds triggers list --project=$PROJECT_ID --format="table(name,status,github.name,github.push.branch)" || echo "No triggers found"

echo ""
echo -e "${BLUE}13. Checking IAM Service Accounts${NC}"
service_accounts=("anzx-ai-core-api" "anzx-ai-knowledge" "anzx-ai-terraform")

for sa in "${service_accounts[@]}"; do
    check_resource "Service Account" "$sa@$PROJECT_ID.iam.gserviceaccount.com" \
        "gcloud iam service-accounts describe $sa@$PROJECT_ID.iam.gserviceaccount.com --project=$PROJECT_ID"
done

echo ""
echo -e "${BLUE}14. Checking Secrets in Secret Manager${NC}"
secrets=("stripe-api-key" "firebase-service-account" "database-password")

for secret in "${secrets[@]}"; do
    check_resource "Secret" "$secret" \
        "gcloud secrets describe $secret --project=$PROJECT_ID"
done

echo ""
echo -e "${BLUE}15. Checking Monitoring and Logging${NC}"
echo "Checking if Cloud Monitoring is enabled..."
gcloud services list --enabled --filter="name:monitoring.googleapis.com" --project=$PROJECT_ID --format="value(name)" | grep -q monitoring && echo -e "${GREEN}✓ Cloud Monitoring enabled${NC}" || echo -e "${RED}✗ Cloud Monitoring not enabled${NC}"

echo "Checking if Cloud Logging is enabled..."
gcloud services list --enabled --filter="name:logging.googleapis.com" --project=$PROJECT_ID --format="value(name)" | grep -q logging && echo -e "${GREEN}✓ Cloud Logging enabled${NC}" || echo -e "${RED}✗ Cloud Logging not enabled${NC}"

echo ""
echo -e "${BLUE}16. Checking Terraform State${NC}"
echo "Checking Terraform state bucket..."
if gsutil ls gs://anzx-ai-terraform-state/terraform.tfstate >/dev/null 2>&1; then
    echo -e "${GREEN}✓ Terraform state file exists${NC}"
    echo "Last modified: $(gsutil stat gs://anzx-ai-terraform-state/terraform.tfstate | grep 'Creation time')"
else
    echo -e "${RED}✗ Terraform state file not found${NC}"
fi

echo ""
echo -e "${BLUE}17. Testing Service Endpoints${NC}"
echo "Testing public endpoints (if deployed)..."

# Try to get the load balancer IP
LB_IP=$(gcloud compute addresses describe anzx-ai-ip --global --project=$PROJECT_ID --format="value(address)" 2>/dev/null || echo "")

if [ -n "$LB_IP" ]; then
    echo "Load Balancer IP: $LB_IP"
    echo "Testing health endpoint..."
    curl -s -o /dev/null -w "%{http_code}" "http://$LB_IP/health" | grep -q "200" && echo -e "${GREEN}✓ Health endpoint responding${NC}" || echo -e "${RED}✗ Health endpoint not responding${NC}"
else
    echo -e "${YELLOW}Load Balancer IP not found or not assigned${NC}"
fi

echo ""
echo -e "${BLUE}=== Summary ===${NC}"
echo "Run this script to get a comprehensive view of your GCP deployment status."
echo "Green checkmarks (✓) indicate resources are deployed and working."
echo "Red X marks (✗) indicate missing or failed resources."
echo "Yellow warnings indicate resources in transitional states."
echo ""
echo "Next steps based on results:"
echo "1. If most resources are missing: Run terraform apply to deploy infrastructure"
echo "2. If infrastructure exists but services are down: Check Cloud Run deployments"
echo "3. If services are running but not accessible: Check load balancer and DNS configuration"