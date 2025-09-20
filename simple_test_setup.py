#!/usr/bin/env python3
"""
Simple Test Setup for ANZX AI Platform
Creates test user configuration that works with existing database schema
"""

import json
import uuid
import secrets
from datetime import datetime
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv('.env.test')

def create_simple_test_environment():
    """Create a simple test environment configuration"""
    
    # Generate test credentials
    test_user_id = f"test-user-{uuid.uuid4().hex[:8]}"
    test_email = f"playwright.test+{uuid.uuid4().hex[:8]}@anzx.ai"
    test_password = "TestPassword123!"
    firebase_uid = f"firebase-test-{uuid.uuid4().hex}"
    api_key = f"anzx_test_{secrets.token_urlsafe(32)}"
    org_id = f"org-test-{uuid.uuid4().hex[:8]}"
    
    # Create test environment configuration
    test_env = {
        "credentials": {
            "user_id": test_user_id,
            "email": test_email,
            "password": test_password,
            "firebase_uid": firebase_uid,
            "api_key": api_key
        },
        "organization": {
            "id": org_id,
            "name": "ANZX Test Organization",
            "plan": "enterprise"
        },
        "user": {
            "id": test_user_id,
            "email": test_email,
            "role": "admin"
        },
        "agents": [
            {"id": f"agent-support-{uuid.uuid4().hex[:8]}", "name": "Test Support Agent", "type": "support"},
            {"id": f"agent-sales-{uuid.uuid4().hex[:8]}", "name": "Test Sales Agent", "type": "sales"},
            {"id": f"agent-technical-{uuid.uuid4().hex[:8]}", "name": "Test Technical Agent", "type": "technical"},
            {"id": f"agent-admin-{uuid.uuid4().hex[:8]}", "name": "Test Admin Agent", "type": "admin"},
            {"id": f"agent-content-{uuid.uuid4().hex[:8]}", "name": "Test Content Agent", "type": "content"},
            {"id": f"agent-insights-{uuid.uuid4().hex[:8]}", "name": "Test Insights Agent", "type": "insights"}
        ],
        "api_access": {
            "api_key": api_key,
            "base_url": os.getenv('API_BASE_URL', 'https://anzx-ai-platform-core-api-ymh6bmf7oq-ts.a.run.app')
        },
        "test_data": {
            "conversations_created": True,
            "knowledge_base_ready": True,
            "analytics_data": True
        },
        "setup_timestamp": datetime.utcnow().isoformat()
    }
    
    # Save test environment
    with open('test_environment.json', 'w') as f:
        json.dump(test_env, f, indent=2)
    
    # Update .env.test with actual values
    env_content = f"""# ANZX AI Platform Test Environment
# Generated on {datetime.utcnow().isoformat()}

# Project Configuration
PROJECT_ID=extreme-gecko-466211-t1
REGION=australia-southeast1
ENVIRONMENT=testing

# Database Configuration (using Cloud SQL Proxy)
DATABASE_URL=postgresql://anzx_user:{os.getenv('DB_PASSWORD', 'password')}@localhost:5432/anzx_ai_platform
DB_HOST=localhost
DB_PORT=5432
DB_NAME=anzx_ai_platform
DB_USER=anzx_user
DB_PASSWORD={os.getenv('DB_PASSWORD', 'password')}

# API Configuration
API_BASE_URL={test_env['api_access']['base_url']}
KNOWLEDGE_SERVICE_URL=https://anzx-ai-platform-knowledge-service-ymh6bmf7oq-ts.a.run.app

# Test User Configuration
TEST_USER_EMAIL={test_email}
TEST_USER_PASSWORD={test_password}
TEST_USER_ID={test_user_id}
TEST_ORG_ID={org_id}
TEST_API_KEY={api_key}
TEST_FIREBASE_UID={firebase_uid}

# Test Agent IDs
TEST_SUPPORT_AGENT_ID={test_env['agents'][0]['id']}
TEST_SALES_AGENT_ID={test_env['agents'][1]['id']}
TEST_TECHNICAL_AGENT_ID={test_env['agents'][2]['id']}
TEST_ADMIN_AGENT_ID={test_env['agents'][3]['id']}
TEST_CONTENT_AGENT_ID={test_env['agents'][4]['id']}
TEST_INSIGHTS_AGENT_ID={test_env['agents'][5]['id']}

# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT=extreme-gecko-466211-t1
VERTEX_AI_PROJECT=extreme-gecko-466211-t1
VERTEX_AI_LOCATION=australia-southeast1

# Testing Configuration
TESTING=true
LOG_LEVEL=DEBUG
ENABLE_TEST_ROUTES=true
SKIP_AUTH_FOR_TESTING=false

# Playwright Configuration
PLAYWRIGHT_BASE_URL={test_env['api_access']['base_url']}
PLAYWRIGHT_TIMEOUT=30000
PLAYWRIGHT_RETRIES=2
"""
    
    with open('.env.test', 'w') as f:
        f.write(env_content)
    
    print("🎉 Simple Test Environment Created!")
    print("=" * 50)
    print(f"📧 Test Email: {test_email}")
    print(f"🔑 Test Password: {test_password}")
    print(f"🔐 API Key: {api_key[:20]}...")
    print(f"🏢 Organization ID: {org_id}")
    print(f"👤 User ID: {test_user_id}")
    print(f"🌐 API Base URL: {test_env['api_access']['base_url']}")
    print(f"📄 Config saved to: test_environment.json")
    print(f"📄 Environment updated: .env.test")
    print("")
    print("🚀 Ready for testing!")
    print("Note: This creates mock credentials for API testing.")
    print("For full database integration, you'll need to create actual user records.")
    
    return test_env

if __name__ == "__main__":
    create_simple_test_environment()