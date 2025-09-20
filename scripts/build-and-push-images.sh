#!/bin/bash

# ANZX AI Platform - Build and Push Docker Images for Cloud Run
# This script builds multi-platform images compatible with Cloud Run (AMD64)

set -e

# Configuration
PROJECT_ID="extreme-gecko-466211-t1"
REGION="australia-southeast1"
REGISTRY_URL="$REGION-docker.pkg.dev/$PROJECT_ID/anzx-ai-platform-docker"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== ANZX AI Platform - Docker Image Build & Push ===${NC}"
echo "Registry: $REGISTRY_URL"
echo "Target Platform: linux/amd64 (Cloud Run compatible)"
echo ""

# Configure Docker for GCP
echo -e "${BLUE}1. Configuring Docker for GCP Artifact Registry${NC}"
gcloud auth configure-docker $REGION-docker.pkg.dev --quiet

# Create buildx builder for multi-platform builds
echo -e "${BLUE}2. Setting up Docker Buildx for multi-platform builds${NC}"
docker buildx create --name anzx-builder --use --bootstrap 2>/dev/null || docker buildx use anzx-builder

# Function to build and push image
build_and_push() {
    local service_name=$1
    local service_path=$2
    local dockerfile_path=${3:-"Dockerfile"}
    
    echo -e "${YELLOW}Building $service_name...${NC}"
    
    # Build for AMD64 (Cloud Run compatible)
    docker buildx build \
        --platform linux/amd64 \
        --tag "$REGISTRY_URL/$service_name:latest" \
        --tag "$REGISTRY_URL/$service_name:$(date +%Y%m%d-%H%M%S)" \
        --push \
        --file "$service_path/$dockerfile_path" \
        "$service_path"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Successfully built and pushed $service_name${NC}"
    else
        echo -e "${RED}✗ Failed to build $service_name${NC}"
        exit 1
    fi
}

# Build all services
echo -e "${BLUE}3. Building and pushing service images${NC}"

# Core API Service
build_and_push "core-api" "services/core-api"

# Knowledge Service  
build_and_push "knowledge-service" "services/knowledge-service"

# Chat Widget Service
build_and_push "chat-widget" "services/chat-widget"

# Agent Orchestration Service (if exists)
if [ -d "services/agent-orchestration" ]; then
    build_and_push "agent-orchestration" "services/agent-orchestration"
fi

echo ""
echo -e "${BLUE}4. Verifying pushed images${NC}"
echo "Images in registry:"
gcloud artifacts docker images list $REGISTRY_URL --format="table(IMAGE:label=SERVICE,TAGS:label=TAG,CREATE_TIME:label=CREATED)" --sort-by=CREATE_TIME --limit=20

echo ""
echo -e "${GREEN}=== Build and Push Complete ===${NC}"
echo "All images are now compatible with Cloud Run (linux/amd64)"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Deploy services to Cloud Run: terraform apply"
echo "2. Verify services are running: ./scripts/check-core-services.sh"
echo "3. Test endpoints for functionality"