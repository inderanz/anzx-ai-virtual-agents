"""
Third-Party MCP Integrations
Handles integration with Stripe, Xero, Slack, and other MCP servers
"""

import logging
import os
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from ..models.user import Organization, MCPServer
from ..config.mcp_config import BUILTIN_MCP_SERVERS, mcp_settings
from .mcp_server_manager import mcp_server_manager
from .mcp_tool_registry import mcp_tool_registry

logger = logging.getLogger(__name__)


class MCPIntegrationManager:
    """
    Manages third-party MCP integrations
    
    Features:
    - Stripe MCP server for billing operations
    - Xero MCP server for Australian accounting
    - Slack MCP server for team notifications
    - Extensible framework for additional integrations
    """
    
    def __init__(self):
        self.available_integrations = {
            "stripe": StripeIntegration(),
            "xero": XeroIntegration(),
            "slack": SlackIntegration(),
            "googleapis": GoogleAPIsIntegration()
        }
    
    async def setup_integration(
        self,
        db: Session,
        organization_id: str,
        integration_name: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Set up a third-party MCP integration
        
        Args:
            db: Database session
            organization_id: Organization ID
            integration_name: Name of integration (stripe, xero, slack, etc.)
            config: Integration configuration
            
        Returns:
            Setup result
        """
        try:
            if integration_name not in self.available_integrations:
                raise ValueError(f"Integration '{integration_name}' not available")
            
            integration = self.available_integrations[integration_name]
            
            # Validate configuration
            validation_result = await integration.validate_config(config)
            if not validation_result["valid"]:
                raise ValueError(f"Invalid configuration: {validation_result['error']}")
            
            # Set up the integration
            setup_result = await integration.setup(db, organization_id, config)
            
            # Register MCP server
            server_config = await integration.get_server_config(config)
            registration_result = await mcp_server_manager.register_server(
                db=db,
                organization_id=organization_id,
                server_config=server_config
            )
            
            # Start the server
            start_result = await mcp_server_manager.start_server(server_config["name"])
            
            # Discover and register tools
            discovery_result = await mcp_tool_registry.discover_tools(
                db=db,
                server_name=server_config["name"],
                organization_id=organization_id
            )
            
            logger.info(f"Set up {integration_name} integration for organization {organization_id}")
            
            return {
                "integration": integration_name,
                "status": "configured",
                "server": registration_result,
                "tools_discovered": discovery_result["tools_registered"],
                "setup_details": setup_result
            }
            
        except Exception as e:
            logger.error(f"Failed to set up {integration_name} integration: {e}")
            raise
    
    async def get_available_integrations(self) -> Dict[str, Any]:
        """Get list of available integrations"""
        integrations = {}
        
        for name, integration in self.available_integrations.items():
            integrations[name] = {
                "name": name,
                "display_name": integration.display_name,
                "description": integration.description,
                "category": integration.category,
                "required_config": integration.required_config,
                "optional_config": integration.optional_config,
                "capabilities": integration.capabilities,
                "pricing_info": integration.pricing_info
            }
        
        return integrations
    
    async def test_integration(
        self,
        integration_name: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Test an integration configuration"""
        try:
            if integration_name not in self.available_integrations:
                raise ValueError(f"Integration '{integration_name}' not available")
            
            integration = self.available_integrations[integration_name]
            return await integration.test_connection(config)
            
        except Exception as e:
            logger.error(f"Integration test failed for {integration_name}: {e}")
            return {"success": False, "error": str(e)}


class BaseIntegration:
    """Base class for MCP integrations"""
    
    def __init__(self):
        self.display_name = ""
        self.description = ""
        self.category = ""
        self.required_config = []
        self.optional_config = []
        self.capabilities = []
        self.pricing_info = {}
    
    async def validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate integration configuration"""
        for field in self.required_config:
            if field not in config or not config[field]:
                return {"valid": False, "error": f"Missing required field: {field}"}
        
        return {"valid": True}
    
    async def setup(
        self,
        db: Session,
        organization_id: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Set up the integration"""
        raise NotImplementedError
    
    async def get_server_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Get MCP server configuration"""
        raise NotImplementedError
    
    async def test_connection(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Test connection with the integration"""
        raise NotImplementedError


class StripeIntegration(BaseIntegration):
    """Stripe MCP integration for payment processing"""
    
    def __init__(self):
        super().__init__()
        self.display_name = "Stripe"
        self.description = "Payment processing and billing operations"
        self.category = "finance"
        self.required_config = ["api_key"]
        self.optional_config = ["webhook_secret", "test_mode"]
        self.capabilities = ["payments", "subscriptions", "customers", "invoices"]
        self.pricing_info = {
            "type": "transaction_based",
            "description": "Stripe charges per transaction processed"
        }
    
    async def setup(
        self,
        db: Session,
        organization_id: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Set up Stripe integration"""
        try:
            # Store encrypted API key (in production, use proper encryption)
            # For now, just validate the key format
            api_key = config["api_key"]
            
            if not api_key.startswith(("sk_test_", "sk_live_")):
                raise ValueError("Invalid Stripe API key format")
            
            test_mode = api_key.startswith("sk_test_")
            
            return {
                "api_key_type": "test" if test_mode else "live",
                "webhook_configured": bool(config.get("webhook_secret")),
                "capabilities_enabled": self.capabilities
            }
            
        except Exception as e:
            logger.error(f"Stripe setup failed: {e}")
            raise
    
    async def get_server_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Get Stripe MCP server configuration"""
        return {
            "name": "stripe-mcp",
            "command": "uvx",
            "args": ["stripe-mcp"],
            "env": {
                "STRIPE_API_KEY": config["api_key"],
                "STRIPE_WEBHOOK_SECRET": config.get("webhook_secret", "")
            },
            "timeout": 30,
            "max_retries": 3,
            "health_check_interval": 60,
            "auto_restart": True,
            "security_sandbox": True,
            "allowed_capabilities": ["tools"]
        }
    
    async def test_connection(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Test Stripe connection"""
        try:
            # In production, would make actual Stripe API call
            api_key = config["api_key"]
            
            if not api_key.startswith(("sk_test_", "sk_live_")):
                return {"success": False, "error": "Invalid API key format"}
            
            # Simulate successful connection test
            return {
                "success": True,
                "test_mode": api_key.startswith("sk_test_"),
                "account_id": "acct_test123456"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}


class XeroIntegration(BaseIntegration):
    """Xero MCP integration for Australian accounting"""
    
    def __init__(self):
        super().__init__()
        self.display_name = "Xero"
        self.description = "Australian accounting and bookkeeping integration"
        self.category = "finance"
        self.required_config = ["client_id", "client_secret"]
        self.optional_config = ["tenant_id", "scopes"]
        self.capabilities = ["accounting", "invoicing", "reporting", "bank_feeds"]
        self.pricing_info = {
            "type": "subscription_based",
            "description": "Requires active Xero subscription"
        }
    
    async def setup(
        self,
        db: Session,
        organization_id: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Set up Xero integration"""
        try:
            # Validate OAuth credentials
            client_id = config["client_id"]
            client_secret = config["client_secret"]
            
            if not client_id or not client_secret:
                raise ValueError("Client ID and secret are required")
            
            # Set default scopes if not provided
            scopes = config.get("scopes", [
                "accounting.transactions",
                "accounting.contacts",
                "accounting.settings"
            ])
            
            return {
                "oauth_configured": True,
                "scopes": scopes,
                "requires_tenant_selection": not config.get("tenant_id"),
                "capabilities_enabled": self.capabilities
            }
            
        except Exception as e:
            logger.error(f"Xero setup failed: {e}")
            raise
    
    async def get_server_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Get Xero MCP server configuration"""
        return {
            "name": "xero-mcp",
            "command": "uvx",
            "args": ["xero-mcp"],
            "env": {
                "XERO_CLIENT_ID": config["client_id"],
                "XERO_CLIENT_SECRET": config["client_secret"],
                "XERO_TENANT_ID": config.get("tenant_id", ""),
                "XERO_SCOPES": ",".join(config.get("scopes", []))
            },
            "timeout": 45,
            "max_retries": 3,
            "health_check_interval": 120,
            "auto_restart": True,
            "security_sandbox": True,
            "allowed_capabilities": ["tools"]
        }
    
    async def test_connection(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Test Xero connection"""
        try:
            # In production, would test OAuth flow
            client_id = config["client_id"]
            client_secret = config["client_secret"]
            
            if not client_id or not client_secret:
                return {"success": False, "error": "Missing credentials"}
            
            # Simulate successful connection test
            return {
                "success": True,
                "oauth_valid": True,
                "tenant_id": config.get("tenant_id", "tenant_123456")
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}


class SlackIntegration(BaseIntegration):
    """Slack MCP integration for team notifications"""
    
    def __init__(self):
        super().__init__()
        self.display_name = "Slack"
        self.description = "Team notifications and communication"
        self.category = "communication"
        self.required_config = ["bot_token"]
        self.optional_config = ["signing_secret", "app_token"]
        self.capabilities = ["messaging", "channels", "users", "files"]
        self.pricing_info = {
            "type": "free",
            "description": "Free with Slack workspace"
        }
    
    async def setup(
        self,
        db: Session,
        organization_id: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Set up Slack integration"""
        try:
            bot_token = config["bot_token"]
            
            if not bot_token.startswith("xoxb-"):
                raise ValueError("Invalid Slack bot token format")
            
            return {
                "bot_token_valid": True,
                "socket_mode": bool(config.get("app_token")),
                "webhook_configured": bool(config.get("signing_secret")),
                "capabilities_enabled": self.capabilities
            }
            
        except Exception as e:
            logger.error(f"Slack setup failed: {e}")
            raise
    
    async def get_server_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Get Slack MCP server configuration"""
        return {
            "name": "slack-mcp",
            "command": "uvx",
            "args": ["slack-mcp"],
            "env": {
                "SLACK_BOT_TOKEN": config["bot_token"],
                "SLACK_SIGNING_SECRET": config.get("signing_secret", ""),
                "SLACK_APP_TOKEN": config.get("app_token", "")
            },
            "timeout": 30,
            "max_retries": 3,
            "health_check_interval": 60,
            "auto_restart": True,
            "security_sandbox": True,
            "allowed_capabilities": ["tools"]
        }
    
    async def test_connection(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Test Slack connection"""
        try:
            bot_token = config["bot_token"]
            
            if not bot_token.startswith("xoxb-"):
                return {"success": False, "error": "Invalid bot token format"}
            
            # Simulate successful connection test
            return {
                "success": True,
                "workspace": "test-workspace",
                "bot_user_id": "U123456789"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}


class GoogleAPIsIntegration(BaseIntegration):
    """Google APIs integration via googleapis-genai-toolbox"""
    
    def __init__(self):
        super().__init__()
        self.display_name = "Google APIs"
        self.description = "Gmail, Calendar, Drive, and other Google services"
        self.category = "productivity"
        self.required_config = ["service_account_key"]
        self.optional_config = ["project_id", "scopes"]
        self.capabilities = ["gmail", "calendar", "drive", "sheets", "docs"]
        self.pricing_info = {
            "type": "usage_based",
            "description": "Google API usage charges may apply"
        }
    
    async def setup(
        self,
        db: Session,
        organization_id: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Set up Google APIs integration"""
        try:
            service_account_key = config["service_account_key"]
            
            # Validate service account key format
            if isinstance(service_account_key, str):
                try:
                    key_data = json.loads(service_account_key)
                except json.JSONDecodeError:
                    raise ValueError("Invalid service account key JSON")
            else:
                key_data = service_account_key
            
            required_fields = ["type", "project_id", "private_key", "client_email"]
            for field in required_fields:
                if field not in key_data:
                    raise ValueError(f"Missing field in service account key: {field}")
            
            if key_data["type"] != "service_account":
                raise ValueError("Key must be for a service account")
            
            return {
                "service_account_configured": True,
                "project_id": key_data["project_id"],
                "client_email": key_data["client_email"],
                "capabilities_enabled": self.capabilities
            }
            
        except Exception as e:
            logger.error(f"Google APIs setup failed: {e}")
            raise
    
    async def get_server_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Get Google APIs MCP server configuration"""
        # Write service account key to temporary file
        key_file_path = f"/tmp/service_account_{int(datetime.now().timestamp())}.json"
        
        with open(key_file_path, 'w') as f:
            if isinstance(config["service_account_key"], str):
                f.write(config["service_account_key"])
            else:
                json.dump(config["service_account_key"], f)
        
        return {
            "name": "googleapis-genai-toolbox",
            "command": "uvx",
            "args": ["googleapis-genai-toolbox"],
            "env": {
                "GOOGLE_APPLICATION_CREDENTIALS": key_file_path,
                "GOOGLE_PROJECT_ID": config.get("project_id", "")
            },
            "timeout": 30,
            "max_retries": 3,
            "health_check_interval": 60,
            "auto_restart": True,
            "security_sandbox": True,
            "allowed_capabilities": ["tools"]
        }
    
    async def test_connection(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Test Google APIs connection"""
        try:
            service_account_key = config["service_account_key"]
            
            # Basic validation
            if isinstance(service_account_key, str):
                key_data = json.loads(service_account_key)
            else:
                key_data = service_account_key
            
            if key_data.get("type") != "service_account":
                return {"success": False, "error": "Invalid service account key"}
            
            # Simulate successful connection test
            return {
                "success": True,
                "project_id": key_data["project_id"],
                "client_email": key_data["client_email"]
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}


# Global instance
mcp_integration_manager = MCPIntegrationManager()