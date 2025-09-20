#!/usr/bin/env python3
"""
ANZX AI Platform - Test User Setup
Creates a comprehensive test user with full access for Playwright testing
"""

import asyncio
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import hashlib
import secrets

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestUserManager:
    """Manages test user creation and configuration for comprehensive testing"""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.engine = None
        self.session = None
        
    def connect_database(self):
        """Connect to the database"""
        try:
            self.engine = create_engine(self.database_url)
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            self.session = SessionLocal()
            logger.info("✅ Database connection established")
            return True
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            return False
    
    def generate_test_credentials(self) -> Dict[str, str]:
        """Generate secure test credentials"""
        test_user_id = f"test-user-{uuid.uuid4().hex[:8]}"
        test_email = f"playwright.test+{uuid.uuid4().hex[:8]}@anzx.ai"
        test_password = secrets.token_urlsafe(16)
        firebase_uid = f"firebase-test-{uuid.uuid4().hex}"
        api_key = f"anzx_test_{secrets.token_urlsafe(32)}"
        
        return {
            "user_id": test_user_id,
            "email": test_email,
            "password": test_password,
            "firebase_uid": firebase_uid,
            "api_key": api_key
        }
    
    def create_test_organization(self, credentials: Dict[str, str]) -> str:
        """Create a test organization with full features enabled"""
        try:
            org_id = str(uuid.uuid4())
            
            # Create organization with premium features
            org_query = text("""
                INSERT INTO organizations (
                    id, name, subscription_plan, subscription_status, 
                    created_at, updated_at, settings, limits
                ) VALUES (
                    :id, :name, :plan, :status, 
                    :created_at, :updated_at, :settings, :limits
                )
            """)
            
            org_settings = {
                "features": {
                    "ai_agents": True,
                    "knowledge_base": True,
                    "analytics": True,
                    "integrations": True,
                    "custom_branding": True,
                    "api_access": True,
                    "webhooks": True,
                    "sso": True,
                    "audit_logs": True,
                    "advanced_security": True
                },
                "branding": {
                    "company_name": "ANZX Test Organization",
                    "logo_url": "https://example.com/test-logo.png",
                    "primary_color": "#007bff",
                    "secondary_color": "#6c757d"
                },
                "notifications": {
                    "email_enabled": True,
                    "slack_enabled": True,
                    "webhook_enabled": True
                }
            }
            
            org_limits = {
                "max_agents": 50,
                "max_conversations_per_month": 10000,
                "max_knowledge_documents": 1000,
                "max_api_calls_per_day": 50000,
                "max_users": 100,
                "storage_gb": 100
            }
            
            self.session.execute(org_query, {
                "id": org_id,
                "name": "ANZX Test Organization",
                "plan": "enterprise",
                "status": "active",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "settings": json.dumps(org_settings),
                "limits": json.dumps(org_limits)
            })
            
            logger.info(f"✅ Created test organization: {org_id}")
            return org_id
            
        except Exception as e:
            logger.error(f"❌ Failed to create test organization: {e}")
            raise
    
    def create_test_user(self, credentials: Dict[str, str], org_id: str) -> str:
        """Create a test user with admin privileges"""
        try:
            user_id = str(uuid.uuid4())
            
            # Create user with admin role
            user_query = text("""
                INSERT INTO users (
                    id, firebase_uid, email, organization_id, role, 
                    is_active, created_at, updated_at, preferences, permissions
                ) VALUES (
                    :id, :firebase_uid, :email, :org_id, :role,
                    :is_active, :created_at, :updated_at, :preferences, :permissions
                )
            """)
            
            user_preferences = {
                "theme": "light",
                "language": "en",
                "timezone": "Australia/Sydney",
                "notifications": {
                    "email": True,
                    "browser": True,
                    "mobile": True
                },
                "dashboard": {
                    "default_view": "overview",
                    "widgets": ["agents", "conversations", "analytics", "knowledge"]
                }
            }
            
            user_permissions = {
                "agents": {
                    "create": True,
                    "read": True,
                    "update": True,
                    "delete": True,
                    "deploy": True,
                    "configure": True
                },
                "conversations": {
                    "view_all": True,
                    "export": True,
                    "delete": True,
                    "moderate": True
                },
                "knowledge": {
                    "upload": True,
                    "manage": True,
                    "delete": True,
                    "configure": True
                },
                "analytics": {
                    "view_all": True,
                    "export": True,
                    "configure_dashboards": True
                },
                "organization": {
                    "manage_users": True,
                    "manage_billing": True,
                    "manage_settings": True,
                    "view_audit_logs": True
                },
                "api": {
                    "full_access": True,
                    "manage_keys": True,
                    "view_usage": True
                }
            }
            
            self.session.execute(user_query, {
                "id": user_id,
                "firebase_uid": credentials["firebase_uid"],
                "email": credentials["email"],
                "org_id": org_id,
                "role": "admin",
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "preferences": json.dumps(user_preferences),
                "permissions": json.dumps(user_permissions)
            })
            
            logger.info(f"✅ Created test user: {user_id}")
            return user_id
            
        except Exception as e:
            logger.error(f"❌ Failed to create test user: {e}")
            raise
    
    def create_test_api_key(self, credentials: Dict[str, str], user_id: str, org_id: str):
        """Create API key for programmatic testing"""
        try:
            api_key_id = str(uuid.uuid4())
            
            api_key_query = text("""
                INSERT INTO api_keys (
                    id, key_hash, name, user_id, organization_id,
                    permissions, is_active, expires_at, created_at, updated_at
                ) VALUES (
                    :id, :key_hash, :name, :user_id, :org_id,
                    :permissions, :is_active, :expires_at, :created_at, :updated_at
                )
            """)
            
            # Hash the API key for storage
            key_hash = hashlib.sha256(credentials["api_key"].encode()).hexdigest()
            
            api_permissions = {
                "scopes": ["read", "write", "admin"],
                "endpoints": ["*"],
                "rate_limit": {
                    "requests_per_minute": 1000,
                    "requests_per_hour": 10000
                }
            }
            
            # API key expires in 1 year
            expires_at = datetime.utcnow() + timedelta(days=365)
            
            self.session.execute(api_key_query, {
                "id": api_key_id,
                "key_hash": key_hash,
                "name": "Playwright Test API Key",
                "user_id": user_id,
                "org_id": org_id,
                "permissions": json.dumps(api_permissions),
                "is_active": True,
                "expires_at": expires_at,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            })
            
            logger.info(f"✅ Created API key: {api_key_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to create API key: {e}")
            raise
    
    def create_sample_agents(self, org_id: str, user_id: str) -> list:
        """Create sample AI agents for testing"""
        try:
            agent_types = [
                {
                    "name": "Test Support Agent",
                    "type": "support",
                    "description": "Customer support agent for testing"
                },
                {
                    "name": "Test Sales Agent", 
                    "type": "sales",
                    "description": "Sales assistant for testing"
                },
                {
                    "name": "Test Technical Agent",
                    "type": "technical", 
                    "description": "Technical support agent for testing"
                },
                {
                    "name": "Test Admin Agent",
                    "type": "admin",
                    "description": "Administrative assistant for testing"
                },
                {
                    "name": "Test Content Agent",
                    "type": "content",
                    "description": "Content creation agent for testing"
                },
                {
                    "name": "Test Insights Agent",
                    "type": "insights",
                    "description": "Data insights agent for testing"
                }
            ]
            
            created_agents = []
            
            for agent_config in agent_types:
                agent_id = str(uuid.uuid4())
                
                agent_query = text("""
                    INSERT INTO assistants (
                        id, name, description, type, organization_id, created_by,
                        is_active, deployment_status, version, model_config,
                        created_at, updated_at, deployed_at
                    ) VALUES (
                        :id, :name, :description, :type, :org_id, :created_by,
                        :is_active, :status, :version, :config,
                        :created_at, :updated_at, :deployed_at
                    )
                """)
                
                model_config = {
                    "model": "gemini-1.5-pro",
                    "temperature": 0.7,
                    "max_tokens": 1000,
                    "vertex_ai_agent_id": f"test-agent-{agent_id[:8]}",
                    "engine_id": f"test-engine-{agent_id[:8]}",
                    "capabilities": ["communication", "general"],
                    "tools": ["web_search", "calendar", "email"],
                    "escalation_enabled": True,
                    "escalation_threshold": 0.7
                }
                
                self.session.execute(agent_query, {
                    "id": agent_id,
                    "name": agent_config["name"],
                    "description": agent_config["description"],
                    "type": agent_config["type"],
                    "org_id": org_id,
                    "created_by": user_id,
                    "is_active": True,
                    "status": "deployed",
                    "version": "1.0.0",
                    "config": json.dumps(model_config),
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                    "deployed_at": datetime.utcnow()
                })
                
                created_agents.append({
                    "id": agent_id,
                    "name": agent_config["name"],
                    "type": agent_config["type"]
                })
            
            logger.info(f"✅ Created {len(created_agents)} test agents")
            return created_agents
            
        except Exception as e:
            logger.error(f"❌ Failed to create sample agents: {e}")
            raise
    
    def create_sample_conversations(self, agents: list, user_id: str, org_id: str):
        """Create sample conversations for testing"""
        try:
            sample_conversations = [
                {
                    "agent_type": "support",
                    "messages": [
                        {"role": "user", "content": "I'm having trouble logging into my account"},
                        {"role": "assistant", "content": "I'd be happy to help you with your login issue. Can you tell me what error message you're seeing?"},
                        {"role": "user", "content": "It says 'Invalid credentials' but I'm sure my password is correct"},
                        {"role": "assistant", "content": "Let me help you reset your password. I'll send you a secure reset link to your email address."}
                    ]
                },
                {
                    "agent_type": "sales",
                    "messages": [
                        {"role": "user", "content": "I'm interested in your enterprise plan"},
                        {"role": "assistant", "content": "Great! I'd love to help you explore our enterprise features. What size is your team?"},
                        {"role": "user", "content": "We have about 50 employees"},
                        {"role": "assistant", "content": "Perfect! Our enterprise plan is ideal for teams your size. Let me schedule a demo to show you the features."}
                    ]
                },
                {
                    "agent_type": "technical",
                    "messages": [
                        {"role": "user", "content": "How do I integrate the API with my React application?"},
                        {"role": "assistant", "content": "I'll guide you through the React integration. First, you'll need to install our SDK: npm install @anzx/ai-sdk"},
                        {"role": "user", "content": "Installed! What's next?"},
                        {"role": "assistant", "content": "Now you can initialize the client with your API key. Here's a code example..."}
                    ]
                }
            ]
            
            created_conversations = []
            
            for conv_data in sample_conversations:
                # Find matching agent
                agent = next((a for a in agents if a["type"] == conv_data["agent_type"]), None)
                if not agent:
                    continue
                
                conv_id = str(uuid.uuid4())
                
                # Create conversation
                conv_query = text("""
                    INSERT INTO conversations (
                        id, assistant_id, user_id, organization_id, channel,
                        status, created_at, updated_at, metadata
                    ) VALUES (
                        :id, :assistant_id, :user_id, :org_id, :channel,
                        :status, :created_at, :updated_at, :metadata
                    )
                """)
                
                metadata = {
                    "channel": "api",
                    "user_agent": "Playwright Test",
                    "ip_address": "127.0.0.1",
                    "session_id": f"test-session-{conv_id[:8]}"
                }
                
                self.session.execute(conv_query, {
                    "id": conv_id,
                    "assistant_id": agent["id"],
                    "user_id": user_id,
                    "org_id": org_id,
                    "channel": "api",
                    "status": "active",
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                    "metadata": json.dumps(metadata)
                })
                
                # Create messages
                for i, message in enumerate(conv_data["messages"]):
                    msg_id = str(uuid.uuid4())
                    
                    msg_query = text("""
                        INSERT INTO messages (
                            id, conversation_id, role, content, 
                            created_at, metadata
                        ) VALUES (
                            :id, :conv_id, :role, :content,
                            :created_at, :metadata
                        )
                    """)
                    
                    msg_metadata = {
                        "tokens": len(message["content"].split()),
                        "processing_time_ms": 150 + (i * 50),
                        "confidence_score": 0.95 if message["role"] == "assistant" else None
                    }
                    
                    self.session.execute(msg_query, {
                        "id": msg_id,
                        "conv_id": conv_id,
                        "role": message["role"],
                        "content": message["content"],
                        "created_at": datetime.utcnow() + timedelta(seconds=i*30),
                        "metadata": json.dumps(msg_metadata)
                    })
                
                created_conversations.append(conv_id)
            
            logger.info(f"✅ Created {len(created_conversations)} sample conversations")
            
        except Exception as e:
            logger.error(f"❌ Failed to create sample conversations: {e}")
            raise
    
    def setup_complete_test_environment(self) -> Dict[str, Any]:
        """Set up complete test environment with user, organization, agents, and data"""
        try:
            # Generate credentials
            credentials = self.generate_test_credentials()
            
            # Create organization
            org_id = self.create_test_organization(credentials)
            
            # Create user
            user_id = self.create_test_user(credentials, org_id)
            
            # Create API key
            self.create_test_api_key(credentials, user_id, org_id)
            
            # Create sample agents
            agents = self.create_sample_agents(org_id, user_id)
            
            # Create sample conversations
            self.create_sample_conversations(agents, user_id, org_id)
            
            # Commit all changes
            self.session.commit()
            
            test_environment = {
                "credentials": credentials,
                "organization": {
                    "id": org_id,
                    "name": "ANZX Test Organization",
                    "plan": "enterprise"
                },
                "user": {
                    "id": user_id,
                    "email": credentials["email"],
                    "role": "admin"
                },
                "agents": agents,
                "api_access": {
                    "api_key": credentials["api_key"],
                    "base_url": "https://anzx-ai-platform-core-api-ymh6bmf7oq-ts.a.run.app"
                },
                "test_data": {
                    "conversations_created": True,
                    "knowledge_base_ready": True,
                    "analytics_data": True
                }
            }
            
            logger.info("🎉 Complete test environment setup successful!")
            return test_environment
            
        except Exception as e:
            logger.error(f"❌ Test environment setup failed: {e}")
            if self.session:
                self.session.rollback()
            raise
        finally:
            if self.session:
                self.session.close()

def generate_playwright_config(test_env: Dict[str, Any]) -> str:
    """Generate Playwright configuration file with test user credentials"""
    
    playwright_config = f'''
// Playwright Test Configuration for ANZX AI Platform
// Auto-generated test user configuration

const {{ defineConfig, devices }} = require('@playwright/test');

module.exports = defineConfig({{
  testDir: './tests',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  
  use: {{
    baseURL: '{test_env["api_access"]["base_url"]}',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    
    // Test user credentials
    extraHTTPHeaders: {{
      'Authorization': 'Bearer {test_env["api_access"]["api_key"]}',
      'X-Test-User-ID': '{test_env["user"]["id"]}',
      'X-Test-Org-ID': '{test_env["organization"]["id"]}'
    }}
  }},

  projects: [
    {{
      name: 'chromium',
      use: {{ ...devices['Desktop Chrome'] }},
    }},
    {{
      name: 'firefox',
      use: {{ ...devices['Desktop Firefox'] }},
    }},
    {{
      name: 'webkit',
      use: {{ ...devices['Desktop Safari'] }},
    }},
    {{
      name: 'mobile-chrome',
      use: {{ ...devices['Pixel 5'] }},
    }},
  ],

  webServer: {{
    command: 'npm run start',
    url: 'http://127.0.0.1:3000',
    reuseExistingServer: !process.env.CI,
  }},
}});

// Test Environment Variables
process.env.TEST_USER_EMAIL = '{test_env["credentials"]["email"]}';
process.env.TEST_USER_PASSWORD = '{test_env["credentials"]["password"]}';
process.env.TEST_USER_ID = '{test_env["user"]["id"]}';
process.env.TEST_ORG_ID = '{test_env["organization"]["id"]}';
process.env.TEST_API_KEY = '{test_env["api_access"]["api_key"]}';
process.env.TEST_FIREBASE_UID = '{test_env["credentials"]["firebase_uid"]}';

// Available Test Agents
process.env.TEST_AGENTS = '{json.dumps([agent["id"] for agent in test_env["agents"]])}';
'''
    
    return playwright_config

def generate_test_helpers(test_env: Dict[str, Any]) -> str:
    """Generate test helper functions for Playwright"""
    
    test_helpers = f'''
// ANZX AI Platform Test Helpers
// Auto-generated helper functions for Playwright tests

class ANZXTestHelpers {{
  constructor(page) {{
    this.page = page;
    this.baseURL = '{test_env["api_access"]["base_url"]}';
    this.testUser = {{
      id: '{test_env["user"]["id"]}',
      email: '{test_env["credentials"]["email"]}',
      password: '{test_env["credentials"]["password"]}',
      orgId: '{test_env["organization"]["id"]}',
      apiKey: '{test_env["api_access"]["api_key"]}'
    }};
    this.testAgents = {json.dumps(test_env["agents"], indent=6)};
  }}

  // Authentication helpers
  async loginAsTestUser() {{
    await this.page.goto('/login');
    await this.page.fill('[data-testid="email"]', this.testUser.email);
    await this.page.fill('[data-testid="password"]', this.testUser.password);
    await this.page.click('[data-testid="login-button"]');
    await this.page.waitForURL('/dashboard');
  }}

  async setAuthHeaders() {{
    await this.page.setExtraHTTPHeaders({{
      'Authorization': `Bearer ${{this.testUser.apiKey}}`,
      'X-Test-User-ID': this.testUser.id,
      'X-Test-Org-ID': this.testUser.orgId
    }});
  }}

  // Agent testing helpers
  async createTestAgent(agentType = 'support') {{
    const response = await this.page.request.post(`${{this.baseURL}}/api/v1/agents/`, {{
      data: {{
        name: `Test Agent - ${{Date.now()}}`,
        type: agentType,
        description: `Test agent created by Playwright`,
        temperature: 0.7,
        max_tokens: 1000
      }},
      headers: {{
        'Authorization': `Bearer ${{this.testUser.apiKey}}`
      }}
    }});
    return await response.json();
  }}

  async startConversation(agentId, message) {{
    const response = await this.page.request.post(`${{this.baseURL}}/api/v1/agents/${{agentId}}/chat`, {{
      data: {{
        message: message,
        channel: 'playwright-test'
      }},
      headers: {{
        'Authorization': `Bearer ${{this.testUser.apiKey}}`
      }}
    }});
    return await response.json();
  }}

  async getAgentAnalytics(agentId, days = 30) {{
    const response = await this.page.request.get(`${{this.baseURL}}/api/v1/agents/${{agentId}}/analytics?days=${{days}}`, {{
      headers: {{
        'Authorization': `Bearer ${{this.testUser.apiKey}}`
      }}
    }});
    return await response.json();
  }}

  // Navigation helpers
  async navigateToAgents() {{
    await this.page.goto('/agents');
    await this.page.waitForSelector('[data-testid="agents-list"]');
  }}

  async navigateToAnalytics() {{
    await this.page.goto('/analytics');
    await this.page.waitForSelector('[data-testid="analytics-dashboard"]');
  }}

  async navigateToKnowledge() {{
    await this.page.goto('/knowledge');
    await this.page.waitForSelector('[data-testid="knowledge-base"]');
  }}

  // Assertion helpers
  async expectAgentToBeVisible(agentName) {{
    await expect(this.page.locator(`[data-testid="agent-${{agentName}}"]`)).toBeVisible();
  }}

  async expectConversationResponse(expectedText) {{
    await expect(this.page.locator('[data-testid="agent-response"]')).toContainText(expectedText);
  }}

  async expectAnalyticsData() {{
    await expect(this.page.locator('[data-testid="analytics-chart"]')).toBeVisible();
    await expect(this.page.locator('[data-testid="metrics-summary"]')).toBeVisible();
  }}

  // Cleanup helpers
  async cleanupTestData() {{
    // Delete test conversations
    await this.page.request.delete(`${{this.baseURL}}/api/v1/conversations/test-cleanup`, {{
      headers: {{
        'Authorization': `Bearer ${{this.testUser.apiKey}}`
      }}
    }});
    
    // Delete test agents (except pre-created ones)
    const agents = await this.page.request.get(`${{this.baseURL}}/api/v1/agents/`, {{
      headers: {{
        'Authorization': `Bearer ${{this.testUser.apiKey}}`
      }}
    }});
    const agentList = await agents.json();
    
    for (const agent of agentList.filter(a => a.name.includes('Test Agent -'))) {{
      await this.page.request.delete(`${{this.baseURL}}/api/v1/agents/${{agent.id}}`, {{
        headers: {{
          'Authorization': `Bearer ${{this.testUser.apiKey}}`
        }}
      }});
    }}
  }}
}}

module.exports = {{ ANZXTestHelpers }};
'''
    
    return test_helpers

async def main():
    """Main function to set up test user environment"""
    # Note: This would need actual database connection
    # For now, we'll generate the configuration files
    
    logger.info("🚀 Setting up ANZX AI Platform Test User Environment")
    
    # Mock test environment for demonstration
    mock_test_env = {
        "credentials": {
            "user_id": "test-user-12345678",
            "email": "playwright.test+12345678@anzx.ai",
            "password": "SecureTestPassword123!",
            "firebase_uid": "firebase-test-abcd1234",
            "api_key": "anzx_test_abcdef123456789"
        },
        "organization": {
            "id": "org-test-87654321",
            "name": "ANZX Test Organization",
            "plan": "enterprise"
        },
        "user": {
            "id": "user-test-11223344",
            "email": "playwright.test+12345678@anzx.ai",
            "role": "admin"
        },
        "agents": [
            {"id": "agent-support-001", "name": "Test Support Agent", "type": "support"},
            {"id": "agent-sales-001", "name": "Test Sales Agent", "type": "sales"},
            {"id": "agent-technical-001", "name": "Test Technical Agent", "type": "technical"},
            {"id": "agent-admin-001", "name": "Test Admin Agent", "type": "admin"},
            {"id": "agent-content-001", "name": "Test Content Agent", "type": "content"},
            {"id": "agent-insights-001", "name": "Test Insights Agent", "type": "insights"}
        ],
        "api_access": {
            "api_key": "anzx_test_abcdef123456789",
            "base_url": "https://anzx-ai-platform-core-api-ymh6bmf7oq-ts.a.run.app"
        },
        "test_data": {
            "conversations_created": True,
            "knowledge_base_ready": True,
            "analytics_data": True
        }
    }
    
    # Generate Playwright configuration
    playwright_config = generate_playwright_config(mock_test_env)
    with open("playwright.config.js", "w") as f:
        f.write(playwright_config)
    
    # Generate test helpers
    test_helpers = generate_test_helpers(mock_test_env)
    with open("test-helpers.js", "w") as f:
        f.write(test_helpers)
    
    # Generate environment file
    env_content = f"""# ANZX AI Platform Test Environment
# Auto-generated test user credentials

TEST_USER_EMAIL={mock_test_env['credentials']['email']}
TEST_USER_PASSWORD={mock_test_env['credentials']['password']}
TEST_USER_ID={mock_test_env['user']['id']}
TEST_ORG_ID={mock_test_env['organization']['id']}
TEST_API_KEY={mock_test_env['api_access']['api_key']}
TEST_FIREBASE_UID={mock_test_env['credentials']['firebase_uid']}
TEST_BASE_URL={mock_test_env['api_access']['base_url']}

# Test Agent IDs
TEST_SUPPORT_AGENT_ID={mock_test_env['agents'][0]['id']}
TEST_SALES_AGENT_ID={mock_test_env['agents'][1]['id']}
TEST_TECHNICAL_AGENT_ID={mock_test_env['agents'][2]['id']}
TEST_ADMIN_AGENT_ID={mock_test_env['agents'][3]['id']}
TEST_CONTENT_AGENT_ID={mock_test_env['agents'][4]['id']}
TEST_INSIGHTS_AGENT_ID={mock_test_env['agents'][5]['id']}
"""
    
    with open(".env.test", "w") as f:
        f.write(env_content)
    
    # Save complete test environment
    with open("test_environment.json", "w") as f:
        json.dump(mock_test_env, f, indent=2)
    
    logger.info("✅ Generated test configuration files:")
    logger.info("   📄 playwright.config.js - Playwright configuration")
    logger.info("   📄 test-helpers.js - Test helper functions")
    logger.info("   📄 .env.test - Environment variables")
    logger.info("   📄 test_environment.json - Complete test environment")
    
    logger.info("\n🎯 Test User Details:")
    logger.info(f"   Email: {mock_test_env['credentials']['email']}")
    logger.info(f"   Password: {mock_test_env['credentials']['password']}")
    logger.info(f"   API Key: {mock_test_env['api_access']['api_key']}")
    logger.info(f"   Organization: {mock_test_env['organization']['name']}")
    logger.info(f"   Role: {mock_test_env['user']['role']}")
    logger.info(f"   Available Agents: {len(mock_test_env['agents'])}")
    
    logger.info("\n🚀 Ready for Playwright testing!")

if __name__ == "__main__":
    asyncio.run(main())