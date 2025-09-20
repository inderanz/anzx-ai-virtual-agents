"""
Google Connectors Configuration
Configuration for Google Workspace integrations
"""

from typing import Dict, Any, List

# Google Calendar Configuration
GOOGLE_CALENDAR_CONFIG = {
    "api_version": "v3",
    "scopes": [
        "https://www.googleapis.com/auth/calendar",
        "https://www.googleapis.com/auth/calendar.events"
    ],
    "default_calendar": "primary",
    "timezone": "Australia/Sydney",
    "working_hours": {
        "start": "09:00",
        "end": "17:00",
        "days": ["monday", "tuesday", "wednesday", "thursday", "friday"]
    },
    "meeting_defaults": {
        "duration_minutes": 60,
        "buffer_minutes": 15,
        "location": "Google Meet",
        "send_notifications": True
    }
}

# Gmail Configuration
GMAIL_CONFIG = {
    "api_version": "v1",
    "scopes": [
        "https://www.googleapis.com/auth/gmail.send",
        "https://www.googleapis.com/auth/gmail.compose",
        "https://www.googleapis.com/auth/gmail.readonly"
    ],
    "default_signature": """
Best regards,
ANZX AI Assistant
""",
    "email_templates": {
        "meeting_invitation": {
            "subject": "Meeting Invitation: {title}",
            "body": """
Hello {recipient_name},

I hope this email finds you well. I would like to invite you to a meeting:

Title: {title}
Date: {date}
Time: {time}
Duration: {duration}
Location: {location}

Agenda:
{agenda}

Please let me know if this time works for you.

Best regards,
{sender_name}
"""
        },
        "follow_up": {
            "subject": "Follow-up: {subject}",
            "body": """
Hello {recipient_name},

I wanted to follow up on our previous conversation regarding {topic}.

{message}

Please let me know if you have any questions or if there's anything else I can help you with.

Best regards,
{sender_name}
"""
        }
    }
}

# Google Workspace Configuration
GOOGLE_WORKSPACE_CONFIG = {
    "domain": "anzx.ai",
    "admin_email": "admin@anzx.ai",
    "default_permissions": {
        "calendar": ["read", "write"],
        "gmail": ["send", "compose"],
        "drive": ["read"]
    },
    "oauth_config": {
        "client_id": "your-client-id",
        "client_secret": "your-client-secret",
        "redirect_uri": "https://anzx.ai/auth/google/callback",
        "scopes": [
            "https://www.googleapis.com/auth/calendar",
            "https://www.googleapis.com/auth/gmail.send",
            "https://www.googleapis.com/auth/drive.readonly"
        ]
    }
}

# Connector Status and Health Check
CONNECTOR_HEALTH_CONFIG = {
    "check_interval_seconds": 300,  # 5 minutes
    "timeout_seconds": 30,
    "retry_attempts": 3,
    "failure_threshold": 3,
    "recovery_threshold": 2
}

# Rate Limiting Configuration
RATE_LIMIT_CONFIG = {
    "calendar": {
        "requests_per_minute": 100,
        "requests_per_hour": 1000,
        "burst_limit": 10
    },
    "gmail": {
        "requests_per_minute": 250,
        "requests_per_hour": 1000000,
        "burst_limit": 25
    },
    "drive": {
        "requests_per_minute": 1000,
        "requests_per_hour": 10000,
        "burst_limit": 100
    }
}

# Error Handling Configuration
ERROR_HANDLING_CONFIG = {
    "retry_delays": [1, 2, 4, 8, 16],  # Exponential backoff in seconds
    "max_retries": 5,
    "circuit_breaker": {
        "failure_threshold": 5,
        "recovery_timeout": 60,
        "expected_recovery_time": 30
    },
    "fallback_responses": {
        "calendar_unavailable": "I'm unable to access your calendar right now. Please try again later or check your calendar manually.",
        "gmail_unavailable": "I'm unable to send emails right now. Please try again later or send the email manually.",
        "general_error": "I'm experiencing technical difficulties with Google services. Please try again in a few minutes."
    }
}

def get_connector_config(connector_name: str) -> Dict[str, Any]:
    """Get configuration for a specific connector"""
    configs = {
        "google_calendar": GOOGLE_CALENDAR_CONFIG,
        "gmail": GMAIL_CONFIG,
        "google_workspace": GOOGLE_WORKSPACE_CONFIG
    }
    return configs.get(connector_name, {})

def get_all_connector_configs() -> Dict[str, Dict[str, Any]]:
    """Get all connector configurations"""
    return {
        "google_calendar": GOOGLE_CALENDAR_CONFIG,
        "gmail": GMAIL_CONFIG,
        "google_workspace": GOOGLE_WORKSPACE_CONFIG,
        "health": CONNECTOR_HEALTH_CONFIG,
        "rate_limits": RATE_LIMIT_CONFIG,
        "error_handling": ERROR_HANDLING_CONFIG
    }

def validate_connector_config(connector_name: str, config: Dict[str, Any]) -> bool:
    """Validate connector configuration"""
    required_fields = {
        "google_calendar": ["api_version", "scopes", "default_calendar"],
        "gmail": ["api_version", "scopes"],
        "google_workspace": ["domain", "oauth_config"]
    }
    
    if connector_name not in required_fields:
        return False
    
    for field in required_fields[connector_name]:
        if field not in config:
            return False
    
    return True