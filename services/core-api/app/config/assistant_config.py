"""
Assistant Configuration
Templates and capabilities for different assistant types
"""

from typing import Dict, Any, List

# Assistant templates with default configurations
ASSISTANT_TEMPLATES = {
    "support": {
        "name": "Support Assistant",
        "description": "Customer support and troubleshooting specialist",
        "capabilities": ["communication", "technical", "billing", "general"],
        "default_model": "gemini-1.5-pro",
        "temperature": 0.7,
        "max_tokens": 1000,
        "system_prompt_template": """
You are a helpful customer support assistant for {organization_name}. Your role is to:

1. Assist customers with their inquiries and problems
2. Provide clear, step-by-step troubleshooting guidance
3. Access customer account information when needed
4. Escalate complex issues to human agents when appropriate
5. Maintain a friendly, professional, and empathetic tone

Always prioritize customer satisfaction and aim to resolve issues efficiently.
If you cannot resolve an issue, explain what you've tried and why escalation is needed.
        """.strip(),
        "conversation_starters": [
            "Hi! I'm here to help with any questions or issues you might have. What can I assist you with today?",
            "Welcome! How can I help resolve your inquiry today?",
            "Hello! I'm your support assistant. What brings you here today?"
        ],
        "escalation_triggers": [
            "customer requests human agent",
            "billing dispute or refund request", 
            "technical issue beyond troubleshooting steps",
            "customer expresses high frustration",
            "security or privacy concern",
            "legal or compliance matter"
        ]
    },
    
    "sales": {
        "name": "Sales Assistant",
        "description": "Lead qualification and sales process specialist",
        "capabilities": ["communication", "analytics", "finance", "general"],
        "default_model": "gemini-1.5-pro",
        "temperature": 0.8,
        "max_tokens": 1000,
        "system_prompt_template": """
You are a knowledgeable sales assistant for {organization_name}. Your role is to:

1. Qualify leads and understand customer needs
2. Provide product information and recommendations
3. Handle pricing inquiries and create quotes
4. Guide customers through the sales process
5. Schedule demos and meetings with sales team
6. Maintain a consultative, helpful, and professional approach

Focus on understanding customer requirements and providing value.
Always aim to move qualified prospects toward a purchase decision.
        """.strip(),
        "conversation_starters": [
            "Hello! I'm here to help you find the perfect solution for your needs. What brings you here today?",
            "Hi! I'd love to learn more about your requirements and show you how we can help. What's your main challenge?",
            "Welcome! I'm your sales assistant. What would you like to know about our products and services?"
        ],
        "escalation_triggers": [
            "customer requests custom pricing",
            "enterprise or large-scale deployment",
            "complex integration requirements", 
            "customer wants to speak with sales manager",
            "contract negotiation needed"
        ]
    },
    
    "technical": {
        "name": "Technical Assistant",
        "description": "Developer support and technical guidance specialist",
        "capabilities": ["technical", "development", "analytics", "general"],
        "default_model": "gemini-1.5-pro",
        "temperature": 0.3,
        "max_tokens": 1500,
        "system_prompt_template": """
You are a technical assistant specializing in developer support for {organization_name}. Your role is to:

1. Provide technical documentation and API guidance
2. Help with integration and implementation questions
3. Troubleshoot technical issues and errors
4. Explain complex technical concepts clearly
5. Guide developers through best practices
6. Escalate to engineering team when needed

Focus on providing accurate, actionable technical guidance.
Always include code examples and step-by-step instructions when helpful.
        """.strip(),
        "conversation_starters": [
            "Hi! I'm here to help with technical questions and integration support. What can I assist you with?",
            "Hello! I'm your technical assistant. Are you working on an integration or have a technical question?",
            "Welcome! I specialize in technical support and developer guidance. How can I help you today?"
        ],
        "escalation_triggers": [
            "bug report or system issue",
            "feature request or enhancement",
            "complex integration requirements",
            "performance or scaling concerns",
            "security vulnerability report"
        ]
    },
    
    "admin": {
        "name": "Admin Assistant",
        "description": "Administrative tasks and calendar management specialist",
        "capabilities": ["communication", "general", "analytics"],
        "default_model": "gemini-1.5-pro",
        "temperature": 0.7,
        "max_tokens": 1000,
        "system_prompt_template": """
You are an administrative assistant specializing in calendar management and scheduling for {organization_name}. Your role is to:

1. Schedule meetings and appointments with conflict detection
2. Manage calendar events and send invitations
3. Handle task management and reminders
4. Compose and send professional emails
5. Coordinate between multiple participants and time zones
6. Provide scheduling recommendations and alternatives

Always confirm details before scheduling and provide clear confirmation messages.
Be proactive in suggesting optimal meeting times and handling conflicts.
        """.strip(),
        "conversation_starters": [
            "Hi! I'm your admin assistant. I can help you schedule meetings, manage your calendar, and handle administrative tasks. What would you like me to help you with?",
            "Hello! I'm here to help with scheduling, calendar management, and administrative support. How can I assist you today?",
            "Welcome! I specialize in calendar management and administrative tasks. What can I help you organize today?"
        ],
        "escalation_triggers": [
            "complex multi-party scheduling conflicts",
            "urgent meeting requests requiring immediate attention",
            "calendar integration issues or technical problems",
            "sensitive or confidential meeting arrangements",
            "budget or resource allocation requests"
        ]
    },
    
    "content": {
        "name": "Content Assistant",
        "description": "Content generation and brand consistency specialist",
        "capabilities": ["communication", "analytics", "general"],
        "default_model": "gemini-1.5-pro",
        "temperature": 0.8,
        "max_tokens": 1500,
        "system_prompt_template": """
You are a creative content assistant specializing in content generation and brand consistency for {organization_name}. Your role is to:

1. Generate high-quality content for various platforms and purposes
2. Maintain brand voice and tone consistency across all content
3. Adapt content for different platforms (social media, email, web, blog)
4. Analyze and improve existing content for engagement and clarity
5. Create content calendars and publishing schedules
6. Ensure content aligns with brand guidelines and messaging

Always focus on creating engaging, on-brand content that resonates with the target audience.
Consider platform-specific requirements and best practices for each content type.
        """.strip(),
        "conversation_starters": [
            "Hi! I'm your content assistant. I can help you create engaging content, maintain brand consistency, and adapt content for different platforms. What would you like to create today?",
            "Hello! I specialize in content creation and brand messaging. Whether you need social media posts, blog articles, or email campaigns, I'm here to help. What's your content goal?",
            "Welcome! I'm here to help you create compelling content that aligns with your brand voice. What type of content are you looking to develop?"
        ],
        "escalation_triggers": [
            "legal or compliance review needed for content",
            "sensitive or controversial content topics",
            "large-scale content campaign planning",
            "brand guideline conflicts or updates needed",
            "content performance issues requiring strategy review"
        ]
    },
    
    "insights": {
        "name": "Insights Assistant",
        "description": "Data analysis and business intelligence specialist",
        "capabilities": ["analytics", "technical", "general"],
        "default_model": "gemini-1.5-pro",
        "temperature": 0.3,
        "max_tokens": 1500,
        "system_prompt_template": """
You are an intelligent insights assistant specializing in data analysis and business intelligence for {organization_name}. Your role is to:

1. Analyze business data and identify meaningful patterns and trends
2. Generate actionable insights from complex datasets
3. Create visualizations and dashboards to communicate findings
4. Provide proactive recommendations based on data analysis
5. Answer natural language queries about business metrics and performance
6. Detect anomalies and alert stakeholders to important changes

Always focus on providing clear, actionable insights that drive business decisions.
Use data-driven reasoning and explain your analytical methodology when presenting findings.
        """.strip(),
        "conversation_starters": [
            "Hi! I'm your insights assistant. I can help you analyze data, identify trends, and generate actionable business insights. What would you like to explore?",
            "Hello! I specialize in data analysis and business intelligence. Whether you need performance metrics, trend analysis, or custom reports, I'm here to help. What data are you curious about?",
            "Welcome! I'm here to turn your data into actionable insights. What business questions can I help you answer today?"
        ],
        "escalation_triggers": [
            "complex statistical analysis requiring specialized expertise",
            "data privacy or compliance concerns with sensitive data",
            "large-scale data infrastructure or architecture questions",
            "strategic business decisions requiring executive input",
            "data quality issues affecting critical business processes"
        ]
    }
}

# Capability definitions and tool mappings
ASSISTANT_CAPABILITIES = {
    "communication": {
        "description": "Email, chat, and messaging capabilities",
        "allowed_tools": ["email", "slack", "teams", "sms"],
        "permissions": ["send_messages", "read_messages", "manage_conversations"]
    },
    
    "technical": {
        "description": "Technical support and troubleshooting",
        "allowed_tools": ["api_docs", "error_tracking", "system_monitoring", "logs"],
        "permissions": ["read_system_status", "access_documentation", "view_error_logs"]
    },
    
    "billing": {
        "description": "Billing and subscription management",
        "allowed_tools": ["stripe", "invoicing", "payment_processing"],
        "permissions": ["read_billing_info", "process_refunds", "update_subscriptions"]
    },
    
    "analytics": {
        "description": "Data analysis and reporting",
        "allowed_tools": ["bigquery", "analytics", "reporting", "dashboards"],
        "permissions": ["read_analytics", "generate_reports", "access_metrics"]
    },
    
    "finance": {
        "description": "Financial operations and accounting",
        "allowed_tools": ["xero", "quickbooks", "financial_reporting"],
        "permissions": ["read_financial_data", "generate_invoices", "process_payments"]
    },
    
    "development": {
        "description": "Software development and deployment",
        "allowed_tools": ["github", "ci_cd", "deployment", "code_review"],
        "permissions": ["read_repositories", "trigger_deployments", "access_build_logs"]
    },
    
    "general": {
        "description": "General purpose tools and utilities",
        "allowed_tools": ["web_search", "calendar", "file_storage", "notifications"],
        "permissions": ["basic_operations", "schedule_meetings", "send_notifications"]
    }
}

# Escalation rules and thresholds
ESCALATION_RULES = {
    "support": {
        "message_count_threshold": 10,
        "sentiment_threshold": -0.7,  # Negative sentiment
        "keywords": ["human", "agent", "manager", "supervisor", "escalate", "frustrated", "angry"],
        "auto_escalate_categories": ["billing_dispute", "security_issue", "legal_matter"],
        "escalation_delay_minutes": 30  # Wait time before auto-escalation
    },
    
    "sales": {
        "lead_score_threshold": 80,
        "enterprise_keywords": ["enterprise", "team", "organization", "company", "employees"],
        "pricing_keywords": ["price", "cost", "contract", "negotiate", "discount"],
        "auto_escalate_categories": ["custom_pricing", "enterprise_deal", "contract_negotiation"],
        "escalation_delay_minutes": 15
    },
    
    "technical": {
        "complexity_threshold": 0.8,
        "bug_keywords": ["bug", "error", "broken", "not working", "issue", "problem"],
        "feature_keywords": ["feature", "enhancement", "improvement", "add", "support"],
        "auto_escalate_categories": ["bug_report", "feature_request", "security_vulnerability"],
        "escalation_delay_minutes": 45
    },
    
    "admin": {
        "complexity_threshold": 0.8,
        "conflict_keywords": ["conflict", "busy", "unavailable", "reschedule", "urgent"],
        "sensitive_keywords": ["confidential", "private", "board", "executive", "legal"],
        "auto_escalate_categories": ["complex_scheduling", "sensitive_meetings", "technical_issues"],
        "escalation_delay_minutes": 20
    },
    
    "content": {
        "complexity_threshold": 0.8,
        "sensitive_keywords": ["legal", "compliance", "controversial", "political", "sensitive"],
        "campaign_keywords": ["campaign", "large scale", "multiple platforms", "strategy", "launch"],
        "auto_escalate_categories": ["sensitive_content", "brand_conflicts", "large_campaigns"],
        "escalation_delay_minutes": 25
    },
    
    "insights": {
        "complexity_threshold": 0.8,
        "complex_keywords": ["machine learning", "statistical significance", "regression analysis"],
        "privacy_keywords": ["sensitive", "confidential", "privacy", "gdpr", "compliance"],
        "auto_escalate_categories": ["complex_analysis", "data_privacy", "strategic_decisions"],
        "escalation_delay_minutes": 35
    }
}

# Performance and monitoring settings
ASSISTANT_PERFORMANCE = {
    "response_time_target_ms": 2000,
    "max_concurrent_conversations": 100,
    "conversation_timeout_minutes": 30,
    "max_message_length": 4000,
    "rate_limit_per_minute": 60,
    "health_check_interval_seconds": 30
}

# Integration settings for different assistant types
INTEGRATION_SETTINGS = {
    "support": {
        "required_integrations": ["email", "knowledge_base"],
        "optional_integrations": ["slack", "zendesk", "intercom"],
        "webhook_endpoints": ["/webhooks/support/email", "/webhooks/support/chat"]
    },
    
    "sales": {
        "required_integrations": ["crm", "calendar"],
        "optional_integrations": ["hubspot", "salesforce", "pipedrive"],
        "webhook_endpoints": ["/webhooks/sales/lead", "/webhooks/sales/meeting"]
    },
    
    "technical": {
        "required_integrations": ["documentation", "api_reference"],
        "optional_integrations": ["github", "jira", "confluence"],
        "webhook_endpoints": ["/webhooks/technical/issue", "/webhooks/technical/docs"]
    },
    
    "admin": {
        "required_integrations": ["calendar", "email"],
        "optional_integrations": ["google_calendar", "outlook", "zoom", "teams"],
        "webhook_endpoints": ["/webhooks/admin/calendar", "/webhooks/admin/meeting"]
    },
    
    "content": {
        "required_integrations": ["content_management"],
        "optional_integrations": ["social_media", "cms", "brand_guidelines", "asset_library"],
        "webhook_endpoints": ["/webhooks/content/publish", "/webhooks/content/review"]
    },
    
    "insights": {
        "required_integrations": ["analytics", "data_warehouse"],
        "optional_integrations": ["bigquery", "tableau", "powerbi", "looker"],
        "webhook_endpoints": ["/webhooks/insights/data", "/webhooks/insights/alert"]
    }
}

def get_assistant_template(assistant_type: str) -> Dict[str, Any]:
    """Get template configuration for assistant type"""
    return ASSISTANT_TEMPLATES.get(assistant_type, {})

def get_capability_config(capability: str) -> Dict[str, Any]:
    """Get configuration for a specific capability"""
    return ASSISTANT_CAPABILITIES.get(capability, {})

def get_escalation_rules(assistant_type: str) -> Dict[str, Any]:
    """Get escalation rules for assistant type"""
    return ESCALATION_RULES.get(assistant_type, {})

def validate_assistant_config(config: Dict[str, Any]) -> bool:
    """Validate assistant configuration"""
    required_fields = ["name", "type", "capabilities"]
    
    for field in required_fields:
        if field not in config:
            return False
    
    # Validate assistant type
    if config["type"] not in ASSISTANT_TEMPLATES:
        return False
    
    # Validate capabilities
    for capability in config["capabilities"]:
        if capability not in ASSISTANT_CAPABILITIES:
            return False
    
    return True