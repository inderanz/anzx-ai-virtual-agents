"""
Email Configuration Settings
"""

import os
from typing import Dict, Any
from pydantic import BaseSettings


class EmailSettings(BaseSettings):
    """Email service configuration"""
    
    # Default IMAP/SMTP settings for common providers
    GMAIL_IMAP_SERVER: str = "imap.gmail.com"
    GMAIL_IMAP_PORT: int = 993
    GMAIL_SMTP_SERVER: str = "smtp.gmail.com"
    GMAIL_SMTP_PORT: int = 587
    
    OUTLOOK_IMAP_SERVER: str = "outlook.office365.com"
    OUTLOOK_IMAP_PORT: int = 993
    OUTLOOK_SMTP_SERVER: str = "smtp.office365.com"
    OUTLOOK_SMTP_PORT: int = 587
    
    # Email processing settings
    MAX_EMAILS_PER_BATCH: int = 50
    EMAIL_CHECK_INTERVAL_MINUTES: int = 5
    EMAIL_RETENTION_DAYS: int = 365
    
    # Security settings
    ENCRYPTION_KEY: str = os.getenv("EMAIL_ENCRYPTION_KEY", "")
    
    # Rate limiting
    MAX_EMAILS_PER_HOUR: int = 100
    MAX_RESPONSES_PER_HOUR: int = 50
    
    # Email templates
    ESCALATION_TEMPLATE: str = """
Email thread has been escalated and requires human attention.

Thread Details:
- Subject: {subject}
- Customer: {customer_name} ({customer_email})
- Created: {created_at}
- Messages: {message_count}
- Escalation Reason: {escalation_reason}

Please review and respond to this email thread in the ANZx.ai dashboard.

Thread ID: {thread_id}
Dashboard Link: {dashboard_link}
    """
    
    AUTO_REPLY_TEMPLATE: str = """
Thank you for contacting us. We have received your message and will respond shortly.

If this is urgent, please contact us directly at {escalation_email}.

Best regards,
{organization_name} Support Team

---
This is an automated response from ANZx.ai Assistant.
    """
    
    class Config:
        env_prefix = "EMAIL_"


# Email provider configurations
EMAIL_PROVIDERS = {
    "gmail": {
        "name": "Gmail",
        "imap_server": "imap.gmail.com",
        "imap_port": 993,
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "requires_app_password": True,
        "oauth_supported": True,
        "instructions": "Use an App Password instead of your regular password. Enable 2-factor authentication and generate an App Password in your Google Account settings."
    },
    "outlook": {
        "name": "Outlook/Office 365",
        "imap_server": "outlook.office365.com",
        "imap_port": 993,
        "smtp_server": "smtp.office365.com",
        "smtp_port": 587,
        "requires_app_password": False,
        "oauth_supported": True,
        "instructions": "Use your regular email password or set up OAuth authentication."
    },
    "yahoo": {
        "name": "Yahoo Mail",
        "imap_server": "imap.mail.yahoo.com",
        "imap_port": 993,
        "smtp_server": "smtp.mail.yahoo.com",
        "smtp_port": 587,
        "requires_app_password": True,
        "oauth_supported": False,
        "instructions": "Generate an App Password in your Yahoo Account Security settings."
    },
    "custom": {
        "name": "Custom IMAP/SMTP",
        "imap_server": "",
        "imap_port": 993,
        "smtp_server": "",
        "smtp_port": 587,
        "requires_app_password": False,
        "oauth_supported": False,
        "instructions": "Enter your custom IMAP and SMTP server details."
    }
}

# Email validation patterns
EMAIL_PATTERNS = {
    "gmail": r".*@gmail\.com$",
    "outlook": r".*@(outlook|hotmail|live)\.com$",
    "yahoo": r".*@yahoo\.com$"
}

# Business hours configuration
DEFAULT_BUSINESS_HOURS = {
    "enabled": False,
    "timezone": "Australia/Sydney",
    "monday": {"enabled": True, "start": "09:00", "end": "17:00"},
    "tuesday": {"enabled": True, "start": "09:00", "end": "17:00"},
    "wednesday": {"enabled": True, "start": "09:00", "end": "17:00"},
    "thursday": {"enabled": True, "start": "09:00", "end": "17:00"},
    "friday": {"enabled": True, "start": "09:00", "end": "17:00"},
    "saturday": {"enabled": False, "start": "09:00", "end": "17:00"},
    "sunday": {"enabled": False, "start": "09:00", "end": "17:00"}
}

# Auto-reply settings
DEFAULT_AUTO_REPLY_SETTINGS = {
    "enabled": True,
    "business_hours_only": False,
    "delay_minutes": 0,
    "include_ai_response": True,
    "escalation_threshold": 3  # Escalate after 3 back-and-forth messages
}

# Email signature templates
SIGNATURE_TEMPLATES = {
    "professional": """
Best regards,
{agent_name}
{organization_name}

Email: {support_email}
Website: {website}
    """,
    "friendly": """
Thanks for reaching out!

{agent_name}
{organization_name} Support Team
    """,
    "minimal": """
{agent_name}
{organization_name}
    """
}

email_settings = EmailSettings()