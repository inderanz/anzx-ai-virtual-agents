#!/bin/bash

# ANZX AI Platform - Cloud Run Deployment Script
# Project: extreme-gecko-466211-t1

set -e

# Configuration
PROJECT_ID="extreme-gecko-466211-t1"
REGION="australia-southeast1"
REPOSITORY_NAME="anzx-ai-platform-docker"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if gcloud is authenticated
check_auth() {
    log "Checking Google Cloud authentication..."
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        error "Not authenticated with Google Cloud. Please run 'gcloud auth login'"
        exit 1
    fi
    success "Authenticated with Google Cloud"
}

# Set project
set_project() {
    log "Setting project to $PROJECT_ID..."
    gcloud config set project $PROJECT_ID
    success "Project set to $PROJECT_ID"
}

# Enable required APIs
enable_apis() {
    log "Enabling required Google Cloud APIs..."
    
    apis=(
        "run.googleapis.com"
        "cloudbuild.googleapis.com"
        "artifactregistry.googleapis.com"
        "sql.googleapis.com"
        "redis.googleapis.com"
        "secretmanager.googleapis.com"
        "monitoring.googleapis.com"
        "logging.googleapis.com"
        "vpcaccess.googleapis.com"
    )
    
    for api in "${apis[@]}"; do
        log "Enabling $api..."
        gcloud services enable $api --quiet
    done
    
    success "All required APIs enabled"
}

# Create Artifact Registry repository
create_artifact_registry() {
    log "Creating Artifact Registry repository..."
    
    if gcloud artifacts repositories describe $REPOSITORY_NAME --location=$REGION >/dev/null 2>&1; then
        warning "Artifact Registry repository already exists"
    else
        gcloud artifacts repositories create $REPOSITORY_NAME \
            --repository-format=docker \
            --location=$REGION \
            --description="Docker repository for ANZX AI Platform"
        success "Artifact Registry repository created"
    fi
}

# Configure Docker authentication
configure_docker() {
    log "Configuring Docker authentication..."
    gcloud auth configure-docker $REGION-docker.pkg.dev --quiet
    success "Docker authentication configured"
}

# Create secrets in Secret Manager
create_secrets() {
    log "Creating secrets in Secret Manager..."
    
    # Database URL secret
    if ! gcloud secrets describe anzx-ai-platform-db-url >/dev/null 2>&1; then
        echo -n "postgresql://anzx_user:your-password@10.0.0.1:5432/anzx_ai_platform" | \
        gcloud secrets create anzx-ai-platform-db-url --data-file=-
        success "Database URL secret created"
    else
        warning "Database URL secret already exists"
    fi
    
    # Redis URL secret
    if ! gcloud secrets describe anzx-ai-platform-redis-url >/dev/null 2>&1; then
        echo -n "redis://10.0.0.2:6379" | \
        gcloud secrets create anzx-ai-platform-redis-url --data-file=-
        success "Redis URL secret created"
    else
        warning "Redis URL secret already exists"
    fi
    
    # JWT Secret
    if ! gcloud secrets describe anzx-ai-platform-jwt-secret >/dev/null 2>&1; then
        echo -n "$(openssl rand -base64 32)" | \
        gcloud secrets create anzx-ai-platform-jwt-secret --data-file=-
        success "JWT secret created"
    else
        warning "JWT secret already exists"
    fi
    
    # Stripe Secret Key
    if ! gcloud secrets describe anzx-ai-platform-stripe-key >/dev/null 2>&1; then
        echo -n "sk_test_your_stripe_key_here" | \
        gcloud secrets create anzx-ai-platform-stripe-key --data-file=-
        success "Stripe secret created"
    else
        warning "Stripe secret already exists"
    fi
}

# Build and push Docker images
build_and_push_images() {
    log "Building and pushing Docker images..."
    
    # Build Core API
    log "Building Core API image..."
    docker build -t $REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY_NAME/core-api:latest \
        -f services/core-api/Dockerfile services/core-api/
    
    docker push $REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY_NAME/core-api:latest
    success "Core API image built and pushed"
    
    # Build Knowledge Service
    log "Building Knowledge Service image..."
    docker build -t $REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY_NAME/knowledge-service:latest \
        -f services/knowledge-service/Dockerfile services/knowledge-service/
    
    docker push $REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY_NAME/knowledge-service:latest
    success "Knowledge Service image built and pushed"
}

# Create VPC Connector (if needed)
create_vpc_connector() {
    log "Creating VPC Connector..."
    
    if gcloud compute networks vpc-access connectors describe anzx-ai-platform-connector \
        --region=$REGION >/dev/null 2>&1; then
        warning "VPC Connector already exists"
    else
        gcloud compute networks vpc-access connectors create anzx-ai-platform-connector \
            --region=$REGION \
            --subnet-project=$PROJECT_ID \
            --subnet=default \
            --subnet-range=10.8.0.0/28 \
            --min-instances=2 \
            --max-instances=10
        success "VPC Connector created"
    fi
}

# Deploy Core API to Cloud Run
deploy_core_api() {
    log "Deploying Core API to Cloud Run..."
    
    gcloud run deploy anzx-ai-core-api \
        --image=$REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY_NAME/core-api:latest \
        --region=$REGION \
        --platform=managed \
        --allow-unauthenticated \
        --port=8000 \
        --memory=4Gi \
        --cpu=2 \
        --min-instances=1 \
        --max-instances=100 \
        --concurrency=100 \
        --timeout=300 \
        --set-env-vars="ENVIRONMENT=production,PROJECT_ID=$PROJECT_ID,REGION=$REGION" \
        --set-secrets="DATABASE_URL=anzx-ai-platform-db-url:latest,REDIS_URL=anzx-ai-platform-redis-url:latest,JWT_SECRET_KEY=anzx-ai-platform-jwt-secret:latest,STRIPE_SECRET_KEY=anzx-ai-platform-stripe-key:latest" \
        --vpc-connector=anzx-ai-platform-connector \
        --vpc-egress=private-ranges-only
    
    success "Core API deployed to Cloud Run"
}

# Deploy Knowledge Service to Cloud Run
deploy_knowledge_service() {
    log "Deploying Knowledge Service to Cloud Run..."
    
    gcloud run deploy anzx-ai-knowledge-service \
        --image=$REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY_NAME/knowledge-service:latest \
        --region=$REGION \
        --platform=managed \
        --allow-unauthenticated \
        --port=8001 \
        --memory=2Gi \
        --cpu=1 \
        --min-instances=1 \
        --max-instances=50 \
        --concurrency=50 \
        --timeout=300 \
        --set-env-vars="ENVIRONMENT=production,PROJECT_ID=$PROJECT_ID,REGION=$REGION" \
        --set-secrets="DATABASE_URL=anzx-ai-platform-db-url:latest" \
        --vpc-connector=anzx-ai-platform-connector \
        --vpc-egress=private-ranges-only
    
    success "Knowledge Service deployed to Cloud Run"
}

# Create database migration job
create_migration_job() {
    log "Creating database migration job..."
    
    gcloud run jobs create anzx-ai-db-migration \
        --image=$REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY_NAME/core-api:latest \
        --region=$REGION \
        --memory=1Gi \
        --cpu=1 \
        --max-retries=3 \
        --parallelism=1 \
        --task-count=1 \
        --task-timeout=600 \
        --set-env-vars="ENVIRONMENT=production,PROJECT_ID=$PROJECT_ID" \
        --set-secrets="DATABASE_URL=anzx-ai-platform-db-url:latest" \
        --vpc-connector=anzx-ai-platform-connector \
        --vpc-egress=private-ranges-only \
        --command="python" \
        --args="-m,alembic,upgrade,head" \
        --quiet || warning "Migration job might already exist"
    
    success "Database migration job created"
}

# Run health checks
run_health_checks() {
    log "Running health checks..."
    
    # Get service URLs
    API_URL=$(gcloud run services describe anzx-ai-core-api --region=$REGION --format="value(status.url)")
    KNOWLEDGE_URL=$(gcloud run services describe anzx-ai-knowledge-service --region=$REGION --format="value(status.url)")
    
    log "API URL: $API_URL"
    log "Knowledge Service URL: $KNOWLEDGE_URL"
    
    # Health check for API
    log "Checking API health..."
    if curl -f -s "$API_URL/health" > /dev/null; then
        success "API health check passed"
    else
        error "API health check failed"
        exit 1
    fi
    
    # Health check for Knowledge Service
    log "Checking Knowledge Service health..."
    if curl -f -s "$KNOWLEDGE_URL/health" > /dev/null; then
        success "Knowledge Service health check passed"
    else
        error "Knowledge Service health check failed"
        exit 1
    fi
}

# Set up monitoring
setup_monitoring() {
    log "Setting up monitoring and alerting..."
    
    # Create notification channel
    if ! gcloud alpha monitoring channels list --filter="displayName:Email" --format="value(name)" | grep -q .; then
        gcloud alpha monitoring channels create \
            --display-name="Email" \
            --type="email" \
            --channel-labels="email_address=alerts@anzx-ai.com"
        success "Email notification channel created"
    else
        warning "Email notification channel already exists"
    fi
    
    success "Monitoring setup completed"
}

# Create Cloud Build trigger
create_build_trigger() {
    log "Creating Cloud Build trigger..."
    
    if gcloud builds triggers describe anzx-ai-platform-deploy >/dev/null 2>&1; then
        warning "Build trigger already exists"
    else
        gcloud builds triggers create github \
            --repo-name=anzx-ai-platform \
            --repo-owner=your-github-username \
            --branch-pattern="^main$" \
            --build-config=cloudbuild.yaml \
            --name=anzx-ai-platform-deploy \
            --description="Deploy ANZX AI Platform on main branch push"
        success "Build trigger created"
    fi
}

# Main deployment function
main() {
    log "Starting ANZX AI Platform deployment to Cloud Run..."
    log "Project: $PROJECT_ID"
    log "Region: $REGION"
    
    check_auth
    set_project
    enable_apis
    create_artifact_registry
    configure_docker
    create_secrets
    create_vpc_connector
    build_and_push_images
    create_migration_job
    deploy_core_api
    deploy_knowledge_service
    run_health_checks
    setup_monitoring
    create_build_trigger
    
    success "🎉 ANZX AI Platform successfully deployed to Cloud Run!"
    
    # Display service URLs
    API_URL=$(gcloud run services describe anzx-ai-core-api --region=$REGION --format="value(status.url)")
    KNOWLEDGE_URL=$(gcloud run services describe anzx-ai-knowledge-service --region=$REGION --format="value(status.url)")
    
    echo ""
    echo "🌐 Service URLs:"
    echo "   Core API: $API_URL"
    echo "   Knowledge Service: $KNOWLEDGE_URL"
    echo ""
    echo "📊 Next steps:"
    echo "   1. Set up your domain and SSL certificate"
    echo "   2. Configure your database connection"
    echo "   3. Update your secrets with real values"
    echo "   4. Set up monitoring dashboards"
    echo "   5. Configure your CI/CD pipeline"
    echo ""
}

# Run main function
main "$@"