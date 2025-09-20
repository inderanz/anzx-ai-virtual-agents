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
