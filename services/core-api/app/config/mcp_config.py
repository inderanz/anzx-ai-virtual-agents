"""
MCP Configuration Settings
"""

import os
from typing import List, Dict, Any
from pydantic import BaseSettings


class MCPSettings(BaseSettings):
    """MCP service configuration"""
    
    # Server management
    MAX_SERVERS: int = 10
    DEFAULT_TIMEOUT: int = 30
    HEALTH_CHECK_INTERVAL: int = 60
    MAX_RETRIES: int = 3
    
    # Security settings
    ENABLE_SANDBOX: bool = True
    ALLOWED_COMMANDS: List[str] = [
        "uvx",  # Python package runner
        "node",  # Node.js
        "python",  # Python
        "python3",  # Python 3
    ]
    
    # Tool execution
    TOOL_EXECUTION_TIMEOUT: int = 30
    MAX_CONCURRENT_TOOLS: int = 5
    ENABLE_TOOL_CACHING: bool = True
    TOOL_CACHE_TTL: int = 300  # 5 minutes
    
    # Resource limits
    MAX_MEMORY_MB: int = 512
    MAX_CPU_PERCENT: int = 50
    MAX_EXECUTION_TIME: int = 60
    
    # Logging and monitoring
    LOG_LEVEL: str = "INFO"
    ENABLE_METRICS: bool = True
    METRICS_INTERVAL: int = 60
    
    # Built-in servers
    ENABLE_GOOGLEAPIS_TOOLBOX: bool = True
    ENABLE_STRIPE_MCP: bool = False
    ENABLE_XERO_MCP: bool = False
    ENABLE_SLACK_MCP: bool = False
    
    # Google APIs configuration
    GOOGLE_APPLICATION_CREDENTIALS: str = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")
    GOOGLE_PROJECT_ID: str = os.getenv("GOOGLE_PROJECT_ID", "")
    
    # Third-party API keys
    STRIPE_API_KEY: str = os.getenv("STRIPE_API_KEY", "")
    XERO_CLIENT_ID: str = os.getenv("XERO_CLIENT_ID", "")
    XERO_CLIENT_SECRET: str = os.getenv("XERO_CLIENT_SECRET", "")
    SLACK_BOT_TOKEN: str = os.getenv("SLACK_BOT_TOKEN", "")
    
    class Config:
        env_prefix = "MCP_"


# Built-in MCP server configurations
BUILTIN_MCP_SERVERS = {
    "googleapis-genai-toolbox": {
        "name": "googleapis-genai-toolbox",
        "description": "Google APIs GenAI Toolbox - Access Google services like Gmail, Calendar, Drive",
        "command": "uvx",
        "args": ["googleapis-genai-toolbox"],
        "env": {
            "GOOGLE_APPLICATION_CREDENTIALS": "${GOOGLE_APPLICATION_CREDENTIALS}",
            "GOOGLE_PROJECT_ID": "${GOOGLE_PROJECT_ID}"
        },
        "capabilities": ["tools"],
        "tools": [
            {
                "name": "gmail_send",
                "description": "Send email via Gmail",
                "parameters": {
                    "to": {"type": "string", "description": "Recipient email"},
                    "subject": {"type": "string", "description": "Email subject"},
                    "body": {"type": "string", "description": "Email body"}
                }
            },
            {
                "name": "calendar_create_event",
                "description": "Create calendar event",
                "parameters": {
                    "title": {"type": "string", "description": "Event title"},
                    "start_time": {"type": "string", "description": "Start time (ISO format)"},
                    "end_time": {"type": "string", "description": "End time (ISO format)"},
                    "description": {"type": "string", "description": "Event description"}
                }
            },
            {
                "name": "drive_upload",
                "description": "Upload file to Google Drive",
                "parameters": {
                    "filename": {"type": "string", "description": "File name"},
                    "content": {"type": "string", "description": "File content"},
                    "folder_id": {"type": "string", "description": "Folder ID (optional)"}
                }
            }
        ],
        "auto_install": True,
        "health_check_interval": 60,
        "max_retries": 3
    },
    
    "stripe-mcp": {
        "name": "stripe-mcp",
        "description": "Stripe MCP server for payment processing and billing operations",
        "command": "uvx",
        "args": ["stripe-mcp"],
        "env": {
            "STRIPE_API_KEY": "${STRIPE_API_KEY}"
        },
        "capabilities": ["tools"],
        "tools": [
            {
                "name": "create_customer",
                "description": "Create a new Stripe customer",
                "parameters": {
                    "email": {"type": "string", "description": "Customer email"},
                    "name": {"type": "string", "description": "Customer name"},
                    "description": {"type": "string", "description": "Customer description"}
                }
            },
            {
                "name": "create_subscription",
                "description": "Create a subscription for a customer",
                "parameters": {
                    "customer_id": {"type": "string", "description": "Stripe customer ID"},
                    "price_id": {"type": "string", "description": "Stripe price ID"},
                    "trial_days": {"type": "integer", "description": "Trial period in days"}
                }
            },
            {
                "name": "get_invoices",
                "description": "Get customer invoices",
                "parameters": {
                    "customer_id": {"type": "string", "description": "Stripe customer ID"},
                    "limit": {"type": "integer", "description": "Number of invoices to retrieve"}
                }
            }
        ],
        "auto_install": False,
        "health_check_interval": 60,
        "max_retries": 3
    },
    
    "xero-mcp": {
        "name": "xero-mcp",
        "description": "Xero MCP server for Australian accounting integration",
        "command": "uvx",
        "args": ["xero-mcp"],
        "env": {
            "XERO_CLIENT_ID": "${XERO_CLIENT_ID}",
            "XERO_CLIENT_SECRET": "${XERO_CLIENT_SECRET}"
        },
        "capabilities": ["tools"],
        "tools": [
            {
                "name": "get_contacts",
                "description": "Get Xero contacts",
                "parameters": {
                    "limit": {"type": "integer", "description": "Number of contacts to retrieve"}
                }
            },
            {
                "name": "create_invoice",
                "description": "Create a new invoice",
                "parameters": {
                    "contact_id": {"type": "string", "description": "Contact ID"},
                    "line_items": {"type": "array", "description": "Invoice line items"},
                    "due_date": {"type": "string", "description": "Due date (ISO format)"}
                }
            },
            {
                "name": "get_bank_transactions",
                "description": "Get bank transactions",
                "parameters": {
                    "bank_account_id": {"type": "string", "description": "Bank account ID"},
                    "from_date": {"type": "string", "description": "From date (ISO format)"},
                    "to_date": {"type": "string", "description": "To date (ISO format)"}
                }
            }
        ],
        "auto_install": False,
        "health_check_interval": 60,
        "max_retries": 3
    },
    
    "slack-mcp": {
        "name": "slack-mcp",
        "description": "Slack MCP server for team notifications and communication",
        "command": "uvx",
        "args": ["slack-mcp"],
        "env": {
            "SLACK_BOT_TOKEN": "${SLACK_BOT_TOKEN}"
        },
        "capabilities": ["tools"],
        "tools": [
            {
                "name": "send_message",
                "description": "Send message to Slack channel",
                "parameters": {
                    "channel": {"type": "string", "description": "Channel name or ID"},
                    "text": {"type": "string", "description": "Message text"},
                    "username": {"type": "string", "description": "Bot username (optional)"}
                }
            },
            {
                "name": "create_channel",
                "description": "Create a new Slack channel",
                "parameters": {
                    "name": {"type": "string", "description": "Channel name"},
                    "is_private": {"type": "boolean", "description": "Whether channel is private"},
                    "purpose": {"type": "string", "description": "Channel purpose"}
                }
            },
            {
                "name": "get_user_info",
                "description": "Get user information",
                "parameters": {
                    "user_id": {"type": "string", "description": "User ID"}
                }
            }
        ],
        "auto_install": False,
        "health_check_interval": 60,
        "max_retries": 3
    }
}

# Security policies for MCP servers
MCP_SECURITY_POLICIES = {
    "default": {
        "max_execution_time": 60,
        "max_memory_mb": 512,
        "max_cpu_percent": 50,
        "allowed_network_access": True,
        "allowed_file_access": False,
        "allowed_system_commands": False,
        "rate_limit_requests_per_minute": 60
    },
    
    "googleapis-genai-toolbox": {
        "max_execution_time": 30,
        "max_memory_mb": 256,
        "max_cpu_percent": 30,
        "allowed_network_access": True,
        "allowed_file_access": False,
        "allowed_system_commands": False,
        "rate_limit_requests_per_minute": 100,
        "required_scopes": [
            "https://www.googleapis.com/auth/gmail.send",
            "https://www.googleapis.com/auth/calendar",
            "https://www.googleapis.com/auth/drive.file"
        ]
    },
    
    "stripe-mcp": {
        "max_execution_time": 30,
        "max_memory_mb": 128,
        "max_cpu_percent": 20,
        "allowed_network_access": True,
        "allowed_file_access": False,
        "allowed_system_commands": False,
        "rate_limit_requests_per_minute": 50,
        "required_env_vars": ["STRIPE_API_KEY"]
    },
    
    "xero-mcp": {
        "max_execution_time": 45,
        "max_memory_mb": 256,
        "max_cpu_percent": 30,
        "allowed_network_access": True,
        "allowed_file_access": False,
        "allowed_system_commands": False,
        "rate_limit_requests_per_minute": 30,
        "required_env_vars": ["XERO_CLIENT_ID", "XERO_CLIENT_SECRET"]
    },
    
    "slack-mcp": {
        "max_execution_time": 20,
        "max_memory_mb": 128,
        "max_cpu_percent": 20,
        "allowed_network_access": True,
        "allowed_file_access": False,
        "allowed_system_commands": False,
        "rate_limit_requests_per_minute": 100,
        "required_env_vars": ["SLACK_BOT_TOKEN"]
    }
}

# Tool categories and descriptions
MCP_TOOL_CATEGORIES = {
    "communication": {
        "name": "Communication",
        "description": "Tools for email, messaging, and notifications",
        "icon": "mail",
        "tools": ["gmail_send", "slack_send_message"]
    },
    
    "calendar": {
        "name": "Calendar & Scheduling",
        "description": "Tools for calendar management and scheduling",
        "icon": "calendar",
        "tools": ["calendar_create_event", "calendar_get_events"]
    },
    
    "finance": {
        "name": "Finance & Accounting",
        "description": "Tools for financial operations and accounting",
        "icon": "dollar-sign",
        "tools": ["stripe_create_customer", "xero_create_invoice", "xero_get_bank_transactions"]
    },
    
    "storage": {
        "name": "File Storage",
        "description": "Tools for file management and storage",
        "icon": "folder",
        "tools": ["drive_upload", "drive_download"]
    },
    
    "analytics": {
        "name": "Analytics & Reporting",
        "description": "Tools for data analysis and reporting",
        "icon": "bar-chart",
        "tools": ["analytics_get_report", "analytics_create_dashboard"]
    }
}

mcp_settings = MCPSettings()