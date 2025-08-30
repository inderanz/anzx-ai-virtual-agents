"""
Google Agent Space built-in connector configuration
Based on: https://cloud.google.com/agentspace/docs
"""

import os
from typing import Dict, Any, List, Optional
from enum import Enum


class AgentSpaceConnectorType(Enum):
    """Agent Space built-in connector types"""
    GMAIL = "gmail"
    GOOGLE_CALENDAR = "google_calendar"
    GOOGLE_DRIVE = "google_drive"
    GOOGLE_DOCS = "google_docs"
    GOOGLE_SHEETS = "google_sheets"
    GOOGLE_WORKSPACE = "google_workspace"


class AgentSpaceConnectorConfig:
    """Configuration for Agent Space built-in connectors"""
    
    # OAuth 2.0 Configuration
    CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    REDIRECT_URI: str = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/google/callback")
    
    # Service Account Configuration
    SERVICE_ACCOUNT_KEY_PATH: Optional[str] = os.getenv("GOOGLE_SERVICE_ACCOUNT_KEY")
    SERVICE_ACCOUNT_EMAIL: Optional[str] = os.getenv("GOOGLE_SERVICE_ACCOUNT_EMAIL")
    DOMAIN_WIDE_DELEGATION: bool = os.getenv("GOOGLE_DOMAIN_WIDE_DELEGATION", "false").lower() == "true"
    
    # Agent Space built-in connectors (configured via Agent Builder UI/API)
    AGENT_SPACE_CONNECTORS: Dict[str, Dict[str, Any]] = {
        "gmail": {
            "connector_id": "gmail",
            "display_name": "Gmail",
            "description": "Built-in Gmail connector for email operations",
            "enabled": True,
            "oauth_required": True,
            "configuration": {
                "scopes": [
                    "https://www.googleapis.com/auth/gmail.readonly",
                    "https://www.googleapis.com/auth/gmail.send",
                    "https://www.googleapis.com/auth/gmail.compose"
                ],
                "capabilities": [
                    "read_emails",
                    "send_emails",
                    "search_emails",
                    "manage_drafts"
                ]
            }
        },
        "google_calendar": {
            "connector_id": "google_calendar", 
            "display_name": "Google Calendar",
            "description": "Built-in Calendar connector for scheduling",
            "enabled": True,
            "oauth_required": True,
            "configuration": {
                "scopes": [
                    "https://www.googleapis.com/auth/calendar",
                    "https://www.googleapis.com/auth/calendar.events"
                ],
                "capabilities": [
                    "create_events",
                    "read_events",
                    "update_events",
                    "delete_events",
                    "find_free_time"
                ]
            }
        },
        "google_drive": {
            "connector_id": "google_drive",
            "display_name": "Google Drive", 
            "description": "Built-in Drive connector for file management",
            "enabled": True,
            "oauth_required": True,
            "configuration": {
                "scopes": [
                    "https://www.googleapis.com/auth/drive",
                    "https://www.googleapis.com/auth/drive.file"
                ],
                "capabilities": [
                    "list_files",
                    "upload_files", 
                    "download_files",
                    "share_files",
                    "create_folders"
                ]
            }
        },
        "google_workspace": {
            "connector_id": "google_workspace",
            "display_name": "Google Workspace",
            "description": "Built-in Workspace connector for Docs, Sheets, etc.",
            "enabled": True,
            "oauth_required": True,
            "configuration": {
                "scopes": [
                    "https://www.googleapis.com/auth/documents",
                    "https://www.googleapis.com/auth/spreadsheets",
                    "https://www.googleapis.com/auth/presentations"
                ],
                "capabilities": [
                    "create_documents",
                    "read_documents",
                    "update_documents", 
                    "create_spreadsheets",
                    "read_spreadsheets",
                    "update_spreadsheets"
                ]
            }
        }
    }
    
    # Service-specific configurations
    GMAIL_CONFIG: Dict[str, Any] = {
        "max_results": 100,
        "batch_size": 50,
        "rate_limit_per_minute": 250,  # Gmail API quota
        "supported_formats": ["text/plain", "text/html"],
        "attachment_max_size_mb": 25,
        "auto_reply_enabled": True,
        "signature_template": "Sent via ANZX AI Platform"
    }
    
    CALENDAR_CONFIG: Dict[str, Any] = {
        "max_results": 250,
        "rate_limit_per_minute": 1000,  # Calendar API quota
        "default_timezone": "Australia/Sydney",
        "meeting_duration_default": 30,  # minutes
        "buffer_time_minutes": 15,
        "working_hours": {
            "start": "09:00",
            "end": "17:00",
            "timezone": "Australia/Sydney"
        },
        "auto_accept_meetings": False,
        "send_notifications": True
    }
    
    WORKSPACE_CONFIG: Dict[str, Any] = {
        "drive": {
            "max_file_size_mb": 100,
            "supported_mime_types": [
                "application/pdf",
                "application/vnd.google-apps.document",
                "application/vnd.google-apps.spreadsheet",
                "application/vnd.google-apps.presentation",
                "text/plain",
                "application/msword",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            ],
            "rate_limit_per_minute": 1000
        },
        "docs": {
            "export_format": "text/plain",
            "include_comments": True,
            "include_suggestions": False
        },
        "sheets": {
            "max_rows": 10000,
            "max_columns": 100,
            "export_format": "text/csv"
        }
    }
    
    # Connector health check configuration
    HEALTH_CHECK_CONFIG: Dict[str, Any] = {
        "check_interval_minutes": 5,
        "timeout_seconds": 30,
        "max_retries": 3,
        "backoff_factor": 2,
        "alert_on_failure": True,
        "fallback_enabled": True
    }
    
    # Security and compliance
    SECURITY_CONFIG: Dict[str, Any] = {
        "token_encryption_enabled": True,
        "audit_logging_enabled": True,
        "data_residency_australia": True,
        "pii_detection_enabled": True,
        "content_filtering_enabled": True,
        "access_logging_enabled": True
    }
    
    # Rate limiting and quotas
    RATE_LIMITS: Dict[str, Dict[str, int]] = {
        "gmail": {
            "requests_per_minute": 250,
            "requests_per_day": 1000000,
            "concurrent_requests": 10
        },
        "calendar": {
            "requests_per_minute": 1000,
            "requests_per_day": 1000000,
            "concurrent_requests": 20
        },
        "workspace": {
            "requests_per_minute": 1000,
            "requests_per_day": 20000,
            "concurrent_requests": 15
        }
    }
    
    # Error handling and retry configuration
    RETRY_CONFIG: Dict[str, Any] = {
        "max_retries": 3,
        "backoff_factor": 2,
        "retry_on_status_codes": [429, 500, 502, 503, 504],
        "timeout_seconds": 30,
        "circuit_breaker_enabled": True,
        "circuit_breaker_threshold": 5
    }
    
    # Monitoring and alerting
    MONITORING_CONFIG: Dict[str, Any] = {
        "metrics_enabled": True,
        "performance_tracking": True,
        "error_tracking": True,
        "usage_analytics": True,
        "cost_tracking": True,
        "alert_thresholds": {
            "error_rate_percent": 5,
            "latency_ms": 5000,
            "quota_usage_percent": 80
        }
    }
    
    @classmethod
    def get_service_scopes(cls, services: List[str]) -> List[str]:
        """Get OAuth scopes for specified services"""
        scopes = []
        for service in services:
            if service in cls.OAUTH_SCOPES:
                scopes.extend(cls.OAUTH_SCOPES[service])
        return list(set(scopes))  # Remove duplicates
    
    @classmethod
    def get_service_config(cls, service: str) -> Dict[str, Any]:
        """Get configuration for specific service"""
        config_map = {
            "gmail": cls.GMAIL_CONFIG,
            "calendar": cls.CALENDAR_CONFIG,
            "workspace": cls.WORKSPACE_CONFIG
        }
        return config_map.get(service, {})
    
    @classmethod
    def get_rate_limit(cls, service: str) -> Dict[str, int]:
        """Get rate limit configuration for service"""
        return cls.RATE_LIMITS.get(service, {
            "requests_per_minute": 100,
            "requests_per_day": 10000,
            "concurrent_requests": 5
        })
    
    @classmethod
    def is_service_enabled(cls, service: str) -> bool:
        """Check if service is enabled"""
        return bool(cls.CLIENT_ID and cls.CLIENT_SECRET)
    
    @classmethod
    def validate_configuration(cls) -> Dict[str, Any]:
        """Validate connector configuration"""
        issues = []
        warnings = []
        
        # Check required OAuth configuration
        if not cls.CLIENT_ID:
            issues.append("GOOGLE_CLIENT_ID not configured")
        if not cls.CLIENT_SECRET:
            issues.append("GOOGLE_CLIENT_SECRET not configured")
        
        # Check service account configuration
        if cls.DOMAIN_WIDE_DELEGATION and not cls.SERVICE_ACCOUNT_KEY_PATH:
            issues.append("Domain-wide delegation enabled but no service account key provided")
        
        # Check security configuration
        if not cls.SECURITY_CONFIG["token_encryption_enabled"]:
            warnings.append("Token encryption is disabled")
        if not cls.SECURITY_CONFIG["audit_logging_enabled"]:
            warnings.append("Audit logging is disabled")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings
        }


# Global config instance
agent_space_connector_config = AgentSpaceConnectorConfig()