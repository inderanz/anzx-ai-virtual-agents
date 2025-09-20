#!/bin/bash

# ANZX AI Platform - Local Development Setup
# This script sets up the complete local development environment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    if ! command_exists docker; then
        print_error "Docker is not installed. Please install Docker Desktop for Mac."
        exit 1
    fi
    
    if ! command_exists docker-compose; then
        print_error "Docker Compose is not installed. Please install Docker Compose."
        exit 1
    fi
    
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker Desktop."
        exit 1
    fi
    
    print_success "All prerequisites are met!"
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    mkdir -p logs
    mkdir -p uploads
    mkdir -p credentials
    mkdir -p nginx/ssl
    mkdir -p data/postgres
    mkdir -p data/redis
    
    print_success "Directories created!"
}

# Setup environment variables
setup_environment() {
    print_status "Setting up environment variables..."
    
    if [ ! -f .env ]; then
        cat > .env << EOF
# ANZX AI Platform - Local Development Environment Variables

# Database
DATABASE_URL=postgresql://anzx_user:local_dev_password@localhost:5432/anzx_ai_platform
POSTGRES_DB=anzx_ai_platform
POSTGRES_USER=anzx_user
POSTGRES_PASSWORD=local_dev_password

# Redis
REDIS_URL=redis://localhost:6379

# JWT
JWT_SECRET_KEY=local_dev_jwt_secret_key_12345_very_secure

# Stripe (Test Keys)
STRIPE_SECRET_KEY=sk_test_local_development_key
STRIPE_PUBLISHABLE_KEY=pk_test_local_development_key
STRIPE_WEBHOOK_SECRET=whsec_local_development_webhook_secret

# Google Cloud (Development)
PROJECT_ID=extreme-gecko-466211-t1
REGION=australia-southeast1
GOOGLE_APPLICATION_CREDENTIALS=./credentials/service-account.json

# OpenAI (Optional - add your key)
OPENAI_API_KEY=

# Vertex AI
VERTEX_AI_PROJECT_ID=extreme-gecko-466211-t1
VERTEX_AI_LOCATION=australia-southeast1

# Email (Development - using Mailhog)
SMTP_HOST=localhost
SMTP_PORT=1025
SMTP_USER=
SMTP_PASSWORD=
SMTP_FROM=noreply@anzx.local

# Application
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:3000,http://localhost:8000,http://localhost

# Chat Widget
WIDGET_API_URL=http://localhost/api
WIDGET_WS_URL=ws://localhost/ws

# Monitoring
SENTRY_DSN=
PROMETHEUS_ENABLED=false

# Feature Flags
ENABLE_AGENT_SPACE=true
ENABLE_MCP_TOOLS=true
ENABLE_ANALYTICS=true
EOF
        print_success "Environment file created!"
    else
        print_warning "Environment file already exists. Skipping..."
    fi
}

# Setup Google Cloud credentials (mock for development)
setup_credentials() {
    print_status "Setting up development credentials..."
    
    if [ ! -f credentials/service-account.json ]; then
        cat > credentials/service-account.json << EOF
{
  "type": "service_account",
  "project_id": "extreme-gecko-466211-t1",
  "private_key_id": "dev-key-id",
  "private_key": "-----BEGIN PRIVATE KEY-----\nDEVELOPMENT_MOCK_KEY\n-----END PRIVATE KEY-----\n",
  "client_email": "dev-service-account@extreme-gecko-466211-t1.iam.gserviceaccount.com",
  "client_id": "123456789",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/dev-service-account%40extreme-gecko-466211-t1.iam.gserviceaccount.com"
}
EOF
        print_warning "Mock service account created for development. Replace with real credentials for production."
    else
        print_success "Service account credentials already exist!"
    fi
}

# Build and start services
start_services() {
    print_status "Building and starting services..."
    
    # Pull latest images
    docker-compose pull postgres redis nginx mailhog adminer
    
    # Build custom images
    docker-compose build --no-cache
    
    # Start services
    docker-compose up -d
    
    print_success "Services started!"
}

# Wait for services to be healthy
wait_for_services() {
    print_status "Waiting for services to be healthy..."
    
    # Wait for database
    print_status "Waiting for PostgreSQL..."
    timeout 60 bash -c 'until docker-compose exec -T postgres pg_isready -U anzx_user -d anzx_ai_platform; do sleep 2; done'
    
    # Wait for Redis
    print_status "Waiting for Redis..."
    timeout 30 bash -c 'until docker-compose exec -T redis redis-cli ping | grep -q PONG; do sleep 2; done'
    
    # Wait for Core API
    print_status "Waiting for Core API..."
    timeout 120 bash -c 'until curl -f http://localhost:8000/health >/dev/null 2>&1; do sleep 5; done'
    
    # Wait for Knowledge Service
    print_status "Waiting for Knowledge Service..."
    timeout 120 bash -c 'until curl -f http://localhost:8001/health >/dev/null 2>&1; do sleep 5; done'
    
    print_success "All services are healthy!"
}

# Run database migrations
run_migrations() {
    print_status "Running database migrations..."
    
    # Wait a bit more for the API to be fully ready
    sleep 10
    
    # Run Alembic migrations
    docker-compose exec -T core-api alembic upgrade head
    
    if [ $? -eq 0 ]; then
        print_success "Database migrations completed!"
    else
        print_warning "Migration failed, but continuing..."
    fi
}

# Create test data
create_test_data() {
    print_status "Creating test data..."
    
    # Test the API endpoints
    print_status "Testing API endpoints..."
    
    # Test health endpoint
    if curl -f http://localhost:8000/health >/dev/null 2>&1; then
        print_success "Health endpoint working!"
    else
        print_warning "Health endpoint not responding"
    fi
    
    # Test assistants endpoint
    if curl -f http://localhost:8000/assistants >/dev/null 2>&1; then
        print_success "Assistants endpoint working!"
    else
        print_warning "Assistants endpoint not responding"
    fi
    
    print_success "Test data setup completed!"
}

# Display service URLs
display_urls() {
    print_success "🚀 ANZX AI Platform is running!"
    echo ""
    echo "📋 Service URLs:"
    echo "   🌐 Main Application:     http://localhost"
    echo "   🔧 Core API:            http://localhost:8000"
    echo "   📚 API Documentation:   http://localhost:8000/docs"
    echo "   🧠 Knowledge Service:   http://localhost:8001"
    echo "   💬 Chat Widget:         http://localhost:3000"
    echo "   📧 Mailhog (Email):     http://localhost:8025"
    echo "   🗄️  Adminer (Database): http://localhost:8080"
    echo ""
    echo "🔑 Database Connection:"
    echo "   Host: localhost:5432"
    echo "   Database: anzx_ai_platform"
    echo "   Username: anzx_user"
    echo "   Password: local_dev_password"
    echo ""
    echo "📊 Monitoring:"
    echo "   📈 Logs: docker-compose logs -f [service-name]"
    echo "   🔍 Status: docker-compose ps"
    echo ""
    echo "🛠️  Development Commands:"
    echo "   🔄 Restart: docker-compose restart [service-name]"
    echo "   🛑 Stop: docker-compose down"
    echo "   🧹 Clean: docker-compose down -v --remove-orphans"
    echo ""
}

# Main execution
main() {
    echo "🚀 Setting up ANZX AI Platform for local development..."
    echo ""
    
    check_prerequisites
    create_directories
    setup_environment
    setup_credentials
    start_services
    wait_for_services
    run_migrations
    create_test_data
    display_urls
    
    print_success "Setup completed successfully! 🎉"
}

# Handle script interruption
trap 'print_error "Setup interrupted!"; exit 1' INT TERM

# Run main function
main "$@"