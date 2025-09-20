#!/usr/bin/env python3
"""
ANZX AI Platform - Database Tables Setup
Creates all necessary database tables and initial data
"""

import os
import sys
import logging
from datetime import datetime
import uuid
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_tables_sql():
    """Generate SQL to create all necessary tables"""
    return """
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Organizations table
CREATE TABLE IF NOT EXISTS organizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    subscription_plan VARCHAR(50) DEFAULT 'free',
    subscription_status VARCHAR(50) DEFAULT 'active',
    settings JSONB DEFAULT '{}',
    limits JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    firebase_uid VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    role VARCHAR(50) DEFAULT 'user',
    is_active BOOLEAN DEFAULT true,
    preferences JSONB DEFAULT '{}',
    permissions JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Assistants table
CREATE TABLE IF NOT EXISTS assistants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    type VARCHAR(50) NOT NULL,
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    system_prompt TEXT,
    model_config JSONB DEFAULT '{}',
    tools_config JSONB DEFAULT '{}',
    knowledge_sources JSONB DEFAULT '[]',
    is_active BOOLEAN DEFAULT true,
    deployment_status VARCHAR(50) DEFAULT 'draft',
    version VARCHAR(20) DEFAULT '1.0.0',
    total_conversations INTEGER DEFAULT 0,
    total_messages INTEGER DEFAULT 0,
    average_response_time FLOAT DEFAULT 0.0,
    satisfaction_score FLOAT DEFAULT 0.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deployed_at TIMESTAMP WITH TIME ZONE
);

-- Conversations table
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    assistant_id UUID REFERENCES assistants(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    channel VARCHAR(50) DEFAULT 'api',
    status VARCHAR(50) DEFAULT 'active',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Messages table
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL, -- 'user' or 'assistant'
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- API Keys table
CREATE TABLE IF NOT EXISTS api_keys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    key_hash VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    permissions JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    expires_at TIMESTAMP WITH TIME ZONE,
    last_used_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Knowledge Base Documents table
CREATE TABLE IF NOT EXISTS knowledge_documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    content TEXT,
    document_type VARCHAR(50),
    source_url VARCHAR(500),
    metadata JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Usage Tracking table
CREATE TABLE IF NOT EXISTS usage_tracking (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    assistant_id UUID REFERENCES assistants(id) ON DELETE SET NULL,
    conversation_id UUID REFERENCES conversations(id) ON DELETE SET NULL,
    event_type VARCHAR(50) NOT NULL,
    tokens_input INTEGER DEFAULT 0,
    tokens_output INTEGER DEFAULT 0,
    cost_usd DECIMAL(10, 6) DEFAULT 0.0,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_firebase_uid ON users(firebase_uid);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_organization_id ON users(organization_id);
CREATE INDEX IF NOT EXISTS idx_assistants_organization_id ON assistants(organization_id);
CREATE INDEX IF NOT EXISTS idx_assistants_type ON assistants(type);
CREATE INDEX IF NOT EXISTS idx_assistants_is_active ON assistants(is_active);
CREATE INDEX IF NOT EXISTS idx_conversations_assistant_id ON conversations(assistant_id);
CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_conversations_organization_id ON conversations(organization_id);
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at);
CREATE INDEX IF NOT EXISTS idx_api_keys_key_hash ON api_keys(key_hash);
CREATE INDEX IF NOT EXISTS idx_api_keys_user_id ON api_keys(user_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_documents_organization_id ON knowledge_documents(organization_id);
CREATE INDEX IF NOT EXISTS idx_usage_tracking_organization_id ON usage_tracking(organization_id);
CREATE INDEX IF NOT EXISTS idx_usage_tracking_created_at ON usage_tracking(created_at);

-- Update triggers for updated_at columns
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_organizations_updated_at BEFORE UPDATE ON organizations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_assistants_updated_at BEFORE UPDATE ON assistants FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_conversations_updated_at BEFORE UPDATE ON conversations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_api_keys_updated_at BEFORE UPDATE ON api_keys FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_knowledge_documents_updated_at BEFORE UPDATE ON knowledge_documents FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
"""

def create_sample_data_sql():
    """Generate SQL to create sample test data"""
    org_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    
    return f"""
-- Insert test organization
INSERT INTO organizations (id, name, subscription_plan, subscription_status, settings, limits)
VALUES (
    '{org_id}',
    'ANZX Test Organization',
    'enterprise',
    'active',
    '{{"features": {{"ai_agents": true, "knowledge_base": true, "analytics": true, "integrations": true, "custom_branding": true, "api_access": true, "webhooks": true, "sso": true, "audit_logs": true, "advanced_security": true}}, "branding": {{"company_name": "ANZX Test Organization", "logo_url": "https://example.com/test-logo.png", "primary_color": "#007bff", "secondary_color": "#6c757d"}}, "notifications": {{"email_enabled": true, "slack_enabled": true, "webhook_enabled": true}}}}',
    '{{"max_agents": 50, "max_conversations_per_month": 10000, "max_knowledge_documents": 1000, "max_api_calls_per_day": 50000, "max_users": 100, "storage_gb": 100}}'
) ON CONFLICT (id) DO NOTHING;

-- Insert test user
INSERT INTO users (id, firebase_uid, email, organization_id, role, is_active, preferences, permissions)
VALUES (
    '{user_id}',
    'firebase-test-{uuid.uuid4().hex[:8]}',
    'playwright.test+{uuid.uuid4().hex[:8]}@anzx.ai',
    '{org_id}',
    'admin',
    true,
    '{{"theme": "light", "language": "en", "timezone": "Australia/Sydney", "notifications": {{"email": true, "browser": true, "mobile": true}}, "dashboard": {{"default_view": "overview", "widgets": ["agents", "conversations", "analytics", "knowledge"]}}}}',
    '{{"agents": {{"create": true, "read": true, "update": true, "delete": true, "deploy": true, "configure": true}}, "conversations": {{"view_all": true, "export": true, "delete": true, "moderate": true}}, "knowledge": {{"upload": true, "manage": true, "delete": true, "configure": true}}, "analytics": {{"view_all": true, "export": true, "configure_dashboards": true}}, "organization": {{"manage_users": true, "manage_billing": true, "manage_settings": true, "view_audit_logs": true}}, "api": {{"full_access": true, "manage_keys": true, "view_usage": true}}}}'
) ON CONFLICT (firebase_uid) DO NOTHING;

-- Insert sample assistants
INSERT INTO assistants (name, description, type, organization_id, created_by, model_config, is_active, deployment_status, deployed_at)
VALUES 
    ('Test Support Agent', 'Customer support agent for testing', 'support', '{org_id}', '{user_id}', '{{"model": "gemini-1.5-pro", "temperature": 0.7, "max_tokens": 1000, "vertex_ai_agent_id": "test-agent-support", "engine_id": "test-engine-support", "capabilities": ["communication", "general"], "tools": ["web_search", "calendar", "email"], "escalation_enabled": true, "escalation_threshold": 0.7}}', true, 'deployed', NOW()),
    ('Test Sales Agent', 'Sales assistant for testing', 'sales', '{org_id}', '{user_id}', '{{"model": "gemini-1.5-pro", "temperature": 0.8, "max_tokens": 1000, "vertex_ai_agent_id": "test-agent-sales", "engine_id": "test-engine-sales", "capabilities": ["communication", "analytics", "finance"], "tools": ["crm", "calendar", "email"], "escalation_enabled": true, "escalation_threshold": 0.7}}', true, 'deployed', NOW()),
    ('Test Technical Agent', 'Technical support agent for testing', 'technical', '{org_id}', '{user_id}', '{{"model": "gemini-1.5-pro", "temperature": 0.3, "max_tokens": 1500, "vertex_ai_agent_id": "test-agent-technical", "engine_id": "test-engine-technical", "capabilities": ["technical", "development"], "tools": ["api_docs", "github", "documentation"], "escalation_enabled": true, "escalation_threshold": 0.7}}', true, 'deployed', NOW()),
    ('Test Admin Agent', 'Administrative assistant for testing', 'admin', '{org_id}', '{user_id}', '{{"model": "gemini-1.5-pro", "temperature": 0.7, "max_tokens": 1000, "vertex_ai_agent_id": "test-agent-admin", "engine_id": "test-engine-admin", "capabilities": ["communication", "general"], "tools": ["calendar", "email", "scheduling"], "escalation_enabled": true, "escalation_threshold": 0.7}}', true, 'deployed', NOW()),
    ('Test Content Agent', 'Content creation agent for testing', 'content', '{org_id}', '{user_id}', '{{"model": "gemini-1.5-pro", "temperature": 0.8, "max_tokens": 1500, "vertex_ai_agent_id": "test-agent-content", "engine_id": "test-engine-content", "capabilities": ["communication", "analytics"], "tools": ["content_management", "social_media"], "escalation_enabled": true, "escalation_threshold": 0.7}}', true, 'deployed', NOW()),
    ('Test Insights Agent', 'Data insights agent for testing', 'insights', '{org_id}', '{user_id}', '{{"model": "gemini-1.5-pro", "temperature": 0.3, "max_tokens": 1500, "vertex_ai_agent_id": "test-agent-insights", "engine_id": "test-engine-insights", "capabilities": ["analytics", "technical"], "tools": ["bigquery", "analytics", "reporting"], "escalation_enabled": true, "escalation_threshold": 0.7}}', true, 'deployed', NOW())
ON CONFLICT DO NOTHING;

-- Insert sample knowledge documents
INSERT INTO knowledge_documents (organization_id, title, content, document_type, metadata)
VALUES 
    ('{org_id}', 'Getting Started Guide', 'This is a comprehensive getting started guide for the ANZX AI Platform. It covers basic setup, configuration, and usage patterns.', 'guide', '{{"category": "documentation", "tags": ["getting-started", "setup", "guide"]}}'),
    ('{org_id}', 'API Documentation', 'Complete API documentation for the ANZX AI Platform including authentication, endpoints, and examples.', 'api-docs', '{{"category": "technical", "tags": ["api", "documentation", "reference"]}}'),
    ('{org_id}', 'Troubleshooting FAQ', 'Frequently asked questions and troubleshooting steps for common issues.', 'faq', '{{"category": "support", "tags": ["faq", "troubleshooting", "help"]}}')
ON CONFLICT DO NOTHING;
"""

def execute_sql_via_gcloud(sql_commands):
    """Execute SQL commands via gcloud sql connect"""
    import tempfile
    import subprocess
    
    # Write SQL to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False) as f:
        f.write(sql_commands)
        sql_file = f.name
    
    try:
        # Execute SQL via gcloud
        cmd = [
            'gcloud', 'sql', 'connect', 'anzx-ai-platform-db',
            '--user=anzx_user',
            '--database=anzx_ai_platform',
            '--quiet'
        ]
        
        logger.info("Executing SQL commands via gcloud...")
        
        # Read the SQL file and pipe it to gcloud
        with open(sql_file, 'r') as f:
            sql_content = f.read()
        
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = process.communicate(input=sql_content)
        
        if process.returncode == 0:
            logger.info("✅ SQL commands executed successfully")
            if stdout:
                logger.info(f"Output: {stdout}")
            return True
        else:
            logger.error(f"❌ SQL execution failed: {stderr}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error executing SQL: {e}")
        return False
    finally:
        # Clean up temporary file
        try:
            os.unlink(sql_file)
        except:
            pass

def main():
    """Main function to set up database tables and sample data"""
    logger.info("🚀 ANZX AI Platform - Database Setup")
    logger.info("=" * 50)
    
    # Step 1: Create tables
    logger.info("📋 Step 1: Creating database tables...")
    tables_sql = create_tables_sql()
    
    if execute_sql_via_gcloud(tables_sql):
        logger.info("✅ Database tables created successfully")
    else:
        logger.error("❌ Failed to create database tables")
        return False
    
    # Step 2: Create sample data
    logger.info("📊 Step 2: Creating sample test data...")
    sample_data_sql = create_sample_data_sql()
    
    if execute_sql_via_gcloud(sample_data_sql):
        logger.info("✅ Sample data created successfully")
    else:
        logger.error("❌ Failed to create sample data")
        return False
    
    logger.info("🎉 Database setup completed successfully!")
    logger.info("=" * 50)
    
    # Test the API endpoints
    logger.info("🧪 Testing API endpoints...")
    
    import subprocess
    import json
    
    try:
        # Test health endpoint
        result = subprocess.run([
            'curl', '-s', 
            'https://anzx-ai-platform-core-api-1088103632448.australia-southeast1.run.app/health'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            health_data = json.loads(result.stdout)
            logger.info(f"✅ Health check: {health_data['status']}")
        
        # Test assistants endpoint
        result = subprocess.run([
            'curl', '-s',
            'https://anzx-ai-platform-core-api-1088103632448.australia-southeast1.run.app/assistants'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            assistants_data = json.loads(result.stdout)
            if 'assistants' in assistants_data:
                logger.info(f"✅ Assistants endpoint: Found {len(assistants_data['assistants'])} assistants")
            elif 'error' in assistants_data:
                logger.warning(f"⚠️  Assistants endpoint error: {assistants_data['error'][:100]}...")
        
    except Exception as e:
        logger.warning(f"⚠️  API testing failed: {e}")
    
    logger.info("")
    logger.info("📝 Next steps:")
    logger.info("1. Test API endpoints to verify database connectivity")
    logger.info("2. Run comprehensive tests")
    logger.info("3. Create additional test data as needed")
    logger.info("4. Deploy frontend components")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)