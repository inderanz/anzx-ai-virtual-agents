#!/bin/bash

# ANZX Marketing Deployment Script
# Deploys the ANZX Marketing website to Cloudflare Pages at https://anzx.ai

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID="${PROJECT_ID:-anzx-ai-platform}"
REGION="${REGION:-australia-southeast1}"
PIPELINE_FILE="infrastructure/cloudbuild/pipelines/anzx-marketing-deploy.yaml"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}ANZX Marketing Deployment${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}Error: gcloud CLI is not installed${NC}"
    echo "Please install it from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if user is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" &> /dev/null; then
    echo -e "${RED}Error: Not authenticated with gcloud${NC}"
    echo "Please run: gcloud auth login"
    exit 1
fi

# Check if pipeline file exists
if [ ! -f "$PIPELINE_FILE" ]; then
    echo -e "${RED}Error: Pipeline file not found: $PIPELINE_FILE${NC}"
    exit 1
fi

echo -e "${YELLOW}Configuration:${NC}"
echo "  Project ID: $PROJECT_ID"
echo "  Region: $REGION"
echo "  Pipeline: $PIPELINE_FILE"
echo ""

# Confirm deployment
read -p "$(echo -e ${YELLOW}Do you want to proceed with deployment? [y/N]: ${NC})" -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${RED}Deployment cancelled${NC}"
    exit 0
fi

echo ""
echo -e "${BLUE}Starting deployment...${NC}"
echo ""

# Trigger Cloud Build
gcloud builds submit \
    --config="$PIPELINE_FILE" \
    --project="$PROJECT_ID" \
    --substitutions="_PROJECT_ID=$PROJECT_ID,_REGION=$REGION" \
    --no-source

BUILD_STATUS=$?

echo ""
if [ $BUILD_STATUS -eq 0 ]; then
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}Deployment Successful!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo -e "${GREEN}ANZX Marketing website is now live at:${NC}"
    echo -e "${GREEN}  https://anzx.ai${NC}"
    echo ""
    echo -e "${YELLOW}Cricket chatbot remains available at:${NC}"
    echo -e "${YELLOW}  https://anzx.ai/cricket${NC}"
    echo ""
    echo -e "${BLUE}Next steps:${NC}"
    echo "  1. Visit https://anzx.ai to verify the deployment"
    echo "  2. Test all pages and functionality"
    echo "  3. Verify cricket chatbot still works at /cricket"
    echo "  4. Monitor analytics and error logs"
    echo ""
else
    echo -e "${RED}========================================${NC}"
    echo -e "${RED}Deployment Failed${NC}"
    echo -e "${RED}========================================${NC}"
    echo ""
    echo -e "${RED}Please check the Cloud Build logs for details${NC}"
    echo ""
    exit 1
fi
