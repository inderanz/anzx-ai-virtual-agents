#!/bin/bash
# ANZX AI Platform - Complete Test User Access Setup
# Grants full access to database, services, and APIs for comprehensive testing

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
DB_INSTANCE="anzx-ai-platform-db"
DB_NAME="anzx_ai_platform"
DB_USER="anzx_user"
SERVICE_ACCOUNT="anzx-ai-platform-run-sa@${PROJECT_ID}.iam.gserviceaccount.com"

echo -e "${BLUE}🚀 Setting up ANZX AI Platform Test User Access${NC}"
echo "=================================================="

# Function to print status
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if gcloud is authenticated
echo -e "${BLUE}🔐 Checking authentication...${NC}"
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    print_error "No active gcloud authentication found"
    echo "Please run: gcloud auth login"
    exit 1
fi

CURRENT_USER=$(gcloud auth list --filter=status:ACTIVE --format="value(account)")
print_status "Authenticated as: $CURRENT_USER"

# Set project
echo -e "${BLUE}📋 Setting project context...${NC}"
gcloud config set project $PROJECT_ID
print_status "Project set to: $PROJECT_ID"

# Grant current user necessary IAM roles for testing
echo -e "${BLUE}👤 Granting test user permissions...${NC}"

# Database access roles
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="user:$CURRENT_USER" \
    --role="roles/cloudsql.admin" \
    --quiet

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="user:$CURRENT_USER" \
    --role="roles/cloudsql.client" \
    --quiet

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="user:$CURRENT_USER" \
    --role="roles/cloudsql.instanceUser" \
    --quiet

print_status "Database access roles granted"

# Cloud Run access roles
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="user:$CURRENT_USER" \
    --role="roles/run.admin" \
    --quiet

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="user:$CURRENT_USER" \
    --role="roles/run.invoker" \
    --quiet

print_status "Cloud Run access roles granted"

# Vertex AI access roles
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="user:$CURRENT_USER" \
    --role="roles/aiplatform.admin" \
    --quiet

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="user:$CURRENT_USER" \
    --role="roles/discoveryengine.admin" \
    --quiet

print_status "AI/ML service access roles granted"

# Storage and other service roles
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="user:$CURRENT_USER" \
    --role="roles/storage.admin" \
    --quiet

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="user:$CURRENT_USER" \
    --role="roles/secretmanager.admin" \
    --quiet

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="user:$CURRENT_USER" \
    --role="roles/monitoring.admin" \
    --quiet

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="user:$CURRENT_USER" \
    --role="roles/logging.admin" \
    --quiet

print_status "Storage and monitoring access roles granted"

# Service account impersonation for testing
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="user:$CURRENT_USER" \
    --role="roles/iam.serviceAccountTokenCreator" \
    --quiet

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="user:$CURRENT_USER" \
    --role="roles/iam.serviceAccountUser" \
    --quiet

print_status "Service account impersonation roles granted"

# Get database connection info
echo -e "${BLUE}🗄️  Getting database connection information...${NC}"

DB_CONNECTION_NAME=$(gcloud sql instances describe $DB_INSTANCE --format="value(connectionName)")
DB_PUBLIC_IP=$(gcloud sql instances describe $DB_INSTANCE --format="value(ipAddresses[0].ipAddress)")

print_status "Database connection name: $DB_CONNECTION_NAME"
print_status "Database public IP: $DB_PUBLIC_IP"

# Get current database password (if available from terraform state)
echo -e "${BLUE}🔑 Retrieving database credentials...${NC}"

# Try to get password from terraform state
if [ -f "infrastructure/terraform/terraform.tfvars" ]; then
    DB_PASSWORD=$(grep "db_password" infrastructure/terraform/terraform.tfvars | cut -d'"' -f2 2>/dev/null || echo "")
    if [ -n "$DB_PASSWORD" ]; then
        print_status "Database password retrieved from terraform.tfvars"
    fi
fi

# If password not found, generate a new one and update
if [ -z "$DB_PASSWORD" ]; then
    print_warning "Database password not found, generating new password..."
    DB_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
    
    # Update database user password
    gcloud sql users set-password $DB_USER \
        --instance=$DB_INSTANCE \
        --password="$DB_PASSWORD" \
        --quiet
    
    print_status "New database password set"
fi

# Enable Cloud SQL Auth Proxy for local connections
echo -e "${BLUE}🔌 Setting up Cloud SQL Auth Proxy...${NC}"

# Download Cloud SQL Auth Proxy if not exists
if [ ! -f "./cloud_sql_proxy" ]; then
    echo "Downloading Cloud SQL Auth Proxy..."
    curl -o cloud_sql_proxy https://dl.google.com/cloudsql/cloud_sql_proxy.darwin.amd64
    chmod +x cloud_sql_proxy
    print_status "Cloud SQL Auth Proxy downloaded"
fi

# Create database connection script
cat > connect_to_db.sh << EOF
#!/bin/bash
# Database connection script for testing
echo "🔌 Starting Cloud SQL Auth Proxy..."
./cloud_sql_proxy -instances=$DB_CONNECTION_NAME=tcp:5432 &
PROXY_PID=\$!
echo "Cloud SQL Auth Proxy started with PID: \$PROXY_PID"
echo "Database available at: localhost:5432"
echo "To stop proxy: kill \$PROXY_PID"
echo "Connection string: postgresql://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME"
EOF

chmod +x connect_to_db.sh
print_status "Database connection script created: connect_to_db.sh"

# Create environment file with all credentials
echo -e "${BLUE}📝 Creating test environment configuration...${NC}"

cat > .env.test << EOF
# ANZX AI Platform Test Environment
# Generated on $(date)

# Project Configuration
PROJECT_ID=$PROJECT_ID
REGION=$REGION
ENVIRONMENT=testing

# Database Configuration
DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME
DB_HOST=localhost
DB_PORT=5432
DB_NAME=$DB_NAME
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASSWORD
DB_CONNECTION_NAME=$DB_CONNECTION_NAME
DB_PUBLIC_IP=$DB_PUBLIC_IP

# API Configuration
API_BASE_URL=https://anzx-ai-platform-core-api-ymh6bmf7oq-ts.a.run.app
KNOWLEDGE_SERVICE_URL=https://anzx-ai-platform-knowledge-service-ymh6bmf7oq-ts.a.run.app

# Service Account
SERVICE_ACCOUNT=$SERVICE_ACCOUNT

# Test User Configuration (will be created by test setup)
TEST_USER_EMAIL=playwright.test@anzx.ai
TEST_USER_PASSWORD=TestPassword123!
TEST_ORG_NAME=ANZX Test Organization
TEST_ORG_PLAN=enterprise

# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT=$PROJECT_ID
VERTEX_AI_PROJECT=$PROJECT_ID
VERTEX_AI_LOCATION=$REGION

# Testing Configuration
TESTING=true
LOG_LEVEL=DEBUG
ENABLE_TEST_ROUTES=true
SKIP_AUTH_FOR_TESTING=false

# Playwright Configuration
PLAYWRIGHT_BASE_URL=https://anzx-ai-platform-core-api-ymh6bmf7oq-ts.a.run.app
PLAYWRIGHT_TIMEOUT=30000
PLAYWRIGHT_RETRIES=2
EOF

print_status "Test environment file created: .env.test"

# Create Python requirements for testing
cat > requirements-test.txt << EOF
# Testing Requirements for ANZX AI Platform
pytest>=7.4.0
pytest-asyncio>=0.21.0
pytest-cov>=4.1.0
pytest-mock>=3.11.0
requests>=2.31.0
aiohttp>=3.8.0
sqlalchemy>=2.0.0
psycopg2-binary>=2.9.0
alembic>=1.11.0
python-dotenv>=1.0.0
faker>=19.0.0
factory-boy>=3.3.0
httpx>=0.24.0
asyncpg>=0.28.0
pydantic>=2.0.0
fastapi>=0.100.0
uvicorn>=0.23.0
EOF

print_status "Test requirements file created: requirements-test.txt"

# Create database setup script
cat > setup_test_database.py << 'EOF'
#!/usr/bin/env python3
"""
Database setup script for ANZX AI Platform testing
Creates test user with full access to all features
"""

import asyncio
import os
import json
import uuid
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, Any
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.test')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    import sqlalchemy
    from sqlalchemy import create_engine, text, MetaData, Table
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.exc import SQLAlchemyError
except ImportError:
    logger.error("SQLAlchemy not installed. Run: pip install -r requirements-test.txt")
    exit(1)

class TestDatabaseSetup:
    """Sets up test database with comprehensive test data"""
    
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL')
        if not self.database_url:
            raise ValueError("DATABASE_URL not found in environment")
        
        self.engine = None
        self.session = None
        
    def connect(self):
        """Connect to database"""
        try:
            self.engine = create_engine(self.database_url)
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            self.session = SessionLocal()
            
            # Test connection
            self.session.execute(text("SELECT 1"))
            logger.info("✅ Database connection successful")
            return True
            
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            return False
    
    def create_test_organization(self) -> str:
        """Create test organization"""
        try:
            org_id = str(uuid.uuid4())
            
            # Check if organizations table exists
            result = self.session.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'organizations'
                );
            """))
            
            if not result.scalar():
                logger.warning("Organizations table doesn't exist, creating basic structure...")
                self.session.execute(text("""
                    CREATE TABLE IF NOT EXISTS organizations (
                        id UUID PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        subscription_plan VARCHAR(50) DEFAULT 'enterprise',
                        subscription_status VARCHAR(50) DEFAULT 'active',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        settings JSONB DEFAULT '{}',
                        limits JSONB DEFAULT '{}'
                    );
                """))
            
            # Insert test organization
            self.session.execute(text("""
                INSERT INTO organizations (
                    id, name, subscription_plan, subscription_status,
                    created_at, updated_at, settings, limits
                ) VALUES (
                    :id, :name, :plan, :status,
                    :created_at, :updated_at, :settings, :limits
                ) ON CONFLICT (id) DO NOTHING;
            """), {
                "id": org_id,
                "name": "ANZX Test Organization",
                "plan": "enterprise",
                "status": "active",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "settings": json.dumps({
                    "features": {
                        "ai_agents": True,
                        "knowledge_base": True,
                        "analytics": True,
                        "integrations": True,
                        "api_access": True
                    }
                }),
                "limits": json.dumps({
                    "max_agents": 100,
                    "max_conversations": 10000,
                    "max_api_calls": 50000
                })
            })
            
            logger.info(f"✅ Test organization created: {org_id}")
            return org_id
            
        except Exception as e:
            logger.error(f"❌ Failed to create organization: {e}")
            raise
    
    def create_test_user(self, org_id: str) -> Dict[str, str]:
        """Create test user with admin privileges"""
        try:
            user_id = str(uuid.uuid4())
            firebase_uid = f"test-firebase-{uuid.uuid4().hex[:8]}"
            email = os.getenv('TEST_USER_EMAIL', 'playwright.test@anzx.ai')
            
            # Check if users table exists
            result = self.session.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'users'
                );
            """))
            
            if not result.scalar():
                logger.warning("Users table doesn't exist, creating basic structure...")
                self.session.execute(text("""
                    CREATE TABLE IF NOT EXISTS users (
                        id UUID PRIMARY KEY,
                        firebase_uid VARCHAR(255) UNIQUE,
                        email VARCHAR(255) UNIQUE NOT NULL,
                        organization_id UUID,
                        role VARCHAR(50) DEFAULT 'admin',
                        is_active BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        preferences JSONB DEFAULT '{}',
                        permissions JSONB DEFAULT '{}'
                    );
                """))
            
            # Insert test user
            self.session.execute(text("""
                INSERT INTO users (
                    id, firebase_uid, email, organization_id, role,
                    is_active, created_at, updated_at, preferences, permissions
                ) VALUES (
                    :id, :firebase_uid, :email, :org_id, :role,
                    :is_active, :created_at, :updated_at, :preferences, :permissions
                ) ON CONFLICT (email) DO UPDATE SET
                    firebase_uid = EXCLUDED.firebase_uid,
                    organization_id = EXCLUDED.organization_id,
                    updated_at = EXCLUDED.updated_at;
            """), {
                "id": user_id,
                "firebase_uid": firebase_uid,
                "email": email,
                "org_id": org_id,
                "role": "admin",
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "preferences": json.dumps({
                    "theme": "light",
                    "language": "en",
                    "timezone": "Australia/Sydney"
                }),
                "permissions": json.dumps({
                    "agents": {"create": True, "read": True, "update": True, "delete": True},
                    "conversations": {"view_all": True, "export": True, "delete": True},
                    "knowledge": {"upload": True, "manage": True, "delete": True},
                    "analytics": {"view_all": True, "export": True},
                    "organization": {"manage_users": True, "manage_settings": True},
                    "api": {"full_access": True}
                })
            })
            
            logger.info(f"✅ Test user created: {user_id}")
            
            return {
                "user_id": user_id,
                "firebase_uid": firebase_uid,
                "email": email,
                "organization_id": org_id
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to create user: {e}")
            raise
    
    def create_api_key(self, user_id: str, org_id: str) -> str:
        """Create API key for testing"""
        try:
            api_key = f"anzx_test_{secrets.token_urlsafe(32)}"
            key_hash = hashlib.sha256(api_key.encode()).hexdigest()
            
            # Check if api_keys table exists
            result = self.session.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'api_keys'
                );
            """))
            
            if not result.scalar():
                logger.warning("API keys table doesn't exist, creating basic structure...")
                self.session.execute(text("""
                    CREATE TABLE IF NOT EXISTS api_keys (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        key_hash VARCHAR(255) UNIQUE NOT NULL,
                        name VARCHAR(255),
                        user_id UUID,
                        organization_id UUID,
                        permissions JSONB DEFAULT '{}',
                        is_active BOOLEAN DEFAULT TRUE,
                        expires_at TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """))
            
            # Insert API key
            self.session.execute(text("""
                INSERT INTO api_keys (
                    key_hash, name, user_id, organization_id,
                    permissions, is_active, expires_at, created_at, updated_at
                ) VALUES (
                    :key_hash, :name, :user_id, :org_id,
                    :permissions, :is_active, :expires_at, :created_at, :updated_at
                );
            """), {
                "key_hash": key_hash,
                "name": "Playwright Test API Key",
                "user_id": user_id,
                "org_id": org_id,
                "permissions": json.dumps({
                    "scopes": ["read", "write", "admin"],
                    "endpoints": ["*"]
                }),
                "is_active": True,
                "expires_at": datetime.utcnow() + timedelta(days=365),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            })
            
            logger.info("✅ API key created")
            return api_key
            
        except Exception as e:
            logger.error(f"❌ Failed to create API key: {e}")
            raise
    
    def setup_complete_environment(self) -> Dict[str, Any]:
        """Set up complete test environment"""
        try:
            if not self.connect():
                raise Exception("Failed to connect to database")
            
            # Create organization
            org_id = self.create_test_organization()
            
            # Create user
            user_data = self.create_test_user(org_id)
            
            # Create API key
            api_key = self.create_api_key(user_data["user_id"], org_id)
            
            # Commit changes
            self.session.commit()
            
            test_env = {
                "organization": {
                    "id": org_id,
                    "name": "ANZX Test Organization"
                },
                "user": user_data,
                "api_key": api_key,
                "database_url": self.database_url,
                "api_base_url": os.getenv('API_BASE_URL'),
                "setup_timestamp": datetime.utcnow().isoformat()
            }
            
            # Save to file
            with open('test_environment.json', 'w') as f:
                json.dump(test_env, f, indent=2)
            
            logger.info("🎉 Complete test environment setup successful!")
            logger.info(f"   📧 Email: {user_data['email']}")
            logger.info(f"   🔑 API Key: {api_key[:20]}...")
            logger.info(f"   🏢 Organization: {org_id}")
            logger.info(f"   📄 Config saved to: test_environment.json")
            
            return test_env
            
        except Exception as e:
            logger.error(f"❌ Setup failed: {e}")
            if self.session:
                self.session.rollback()
            raise
        finally:
            if self.session:
                self.session.close()

def main():
    """Main setup function"""
    try:
        setup = TestDatabaseSetup()
        test_env = setup.setup_complete_environment()
        
        print("\n" + "="*60)
        print("🎯 TEST ENVIRONMENT READY FOR PLAYWRIGHT!")
        print("="*60)
        print(f"API Base URL: {test_env['api_base_url']}")
        print(f"User Email: {test_env['user']['email']}")
        print(f"API Key: {test_env['api_key'][:20]}...")
        print(f"Organization ID: {test_env['organization']['id']}")
        print("\nNext steps:")
        print("1. Start Cloud SQL Proxy: ./connect_to_db.sh")
        print("2. Run Playwright tests with the generated credentials")
        print("3. Use test_environment.json for test configuration")
        
    except Exception as e:
        logger.error(f"Setup failed: {e}")
        exit(1)

if __name__ == "__main__":
    main()
EOF

chmod +x setup_test_database.py
print_status "Database setup script created: setup_test_database.py"

# Create Playwright test configuration
cat > playwright.config.js << 'EOF'
// Playwright Test Configuration for ANZX AI Platform
const { defineConfig, devices } = require('@playwright/test');
require('dotenv').config({ path: '.env.test' });

module.exports = defineConfig({
  testDir: './tests',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  
  use: {
    baseURL: process.env.PLAYWRIGHT_BASE_URL,
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    timeout: parseInt(process.env.PLAYWRIGHT_TIMEOUT) || 30000,
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
  ],
});
EOF

print_status "Playwright configuration created: playwright.config.js"

# Create sample Playwright test
mkdir -p tests
cat > tests/test_anzx_platform.spec.js << 'EOF'
// ANZX AI Platform - Comprehensive Playwright Tests
const { test, expect } = require('@playwright/test');
const fs = require('fs');

// Load test environment
let testEnv = {};
if (fs.existsSync('test_environment.json')) {
  testEnv = JSON.parse(fs.readFileSync('test_environment.json', 'utf8'));
}

test.describe('ANZX AI Platform Tests', () => {
  
  test('Health Check', async ({ request }) => {
    const response = await request.get('/health');
    expect(response.status()).toBe(200);
    
    const data = await response.json();
    expect(data.status).toBe('healthy');
    expect(data.service).toBe('anzx-core-api');
  });
  
  test('API Documentation Access', async ({ page }) => {
    await page.goto('/docs');
    await expect(page.locator('title')).toContainText('ANZX AI Platform API');
  });
  
  test('Assistant Discovery', async ({ request }) => {
    const response = await request.get('/assistants');
    expect(response.status()).toBe(200);
    
    const data = await response.json();
    expect(data).toHaveProperty('assistants');
  });
  
  test('API with Authentication', async ({ request }) => {
    if (!testEnv.api_key) {
      test.skip('No API key available for testing');
    }
    
    const response = await request.get('/api/v1/agents/', {
      headers: {
        'Authorization': `Bearer ${testEnv.api_key}`
      }
    });
    
    // Should return 200 or 401/403 (not 500)
    expect([200, 401, 403]).toContain(response.status());
  });
  
});
EOF

print_status "Sample Playwright test created: tests/test_anzx_platform.spec.js"

# Create installation script
cat > install_test_dependencies.sh << 'EOF'
#!/bin/bash
# Install all dependencies for testing

echo "📦 Installing Python dependencies..."
pip3 install -r requirements-test.txt

echo "📦 Installing Node.js dependencies..."
npm init -y
npm install @playwright/test
npx playwright install

echo "✅ All dependencies installed!"
echo "Next steps:"
echo "1. Run: ./connect_to_db.sh (in another terminal)"
echo "2. Run: python3 setup_test_database.py"
echo "3. Run: npx playwright test"
EOF

chmod +x install_test_dependencies.sh
print_status "Installation script created: install_test_dependencies.sh"

# Final summary
echo ""
echo -e "${GREEN}🎉 ANZX AI Platform Test Access Setup Complete!${NC}"
echo "=================================================="
echo ""
echo -e "${BLUE}📋 What was configured:${NC}"
echo "   ✅ IAM roles and permissions for testing"
echo "   ✅ Database access and connection setup"
echo "   ✅ Cloud SQL Auth Proxy configuration"
echo "   ✅ Test environment variables"
echo "   ✅ Python test dependencies"
echo "   ✅ Playwright configuration"
echo "   ✅ Sample test files"
echo ""
echo -e "${BLUE}🚀 Next Steps:${NC}"
echo "   1. Install dependencies: ./install_test_dependencies.sh"
echo "   2. Start database proxy: ./connect_to_db.sh"
echo "   3. Setup test data: python3 setup_test_database.py"
echo "   4. Run Playwright tests: npx playwright test"
echo ""
echo -e "${BLUE}📄 Generated Files:${NC}"
echo "   📄 .env.test - Test environment configuration"
echo "   📄 requirements-test.txt - Python testing dependencies"
echo "   📄 setup_test_database.py - Database setup script"
echo "   📄 connect_to_db.sh - Database connection script"
echo "   📄 playwright.config.js - Playwright configuration"
echo "   📄 tests/test_anzx_platform.spec.js - Sample tests"
echo "   📄 install_test_dependencies.sh - Dependency installer"
echo ""
echo -e "${YELLOW}⚠️  Important Notes:${NC}"
echo "   • Keep the Cloud SQL Auth Proxy running during tests"
echo "   • Test credentials are saved in test_environment.json"
echo "   • Use .env.test for environment configuration"
echo "   • All test data will be created in the actual database"
echo ""
echo -e "${GREEN}✨ Ready for comprehensive Playwright testing!${NC}"
EOF