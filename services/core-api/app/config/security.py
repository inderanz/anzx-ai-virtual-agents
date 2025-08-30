"""
Security configuration and settings
"""

import os
from typing import List, Dict, Any
from pydantic import BaseSettings


class SecuritySettings(BaseSettings):
    """Security configuration settings"""
    
    # JWT Configuration
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET", "your-secret-key")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    
    # Encryption Configuration
    KMS_PROJECT_ID: str = os.getenv("GOOGLE_CLOUD_PROJECT", "")
    KMS_LOCATION: str = os.getenv("KMS_LOCATION", "australia-southeast1")
    KMS_KEY_RING: str = os.getenv("KMS_KEY_RING", "anzx-keyring")
    KMS_KEY_NAME: str = os.getenv("KMS_KEY_NAME", "anzx-app-key")
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 60
    RATE_LIMIT_BURST: int = 10
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = [
        "https://anzx.ai",
        "https://www.anzx.ai",
        "https://app.anzx.ai",
        "https://widget.anzx.ai"
    ]
    
    # Security Headers
    SECURITY_HEADERS: Dict[str, str] = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
    }
    
    # Content Security Policy
    CSP_POLICY: str = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "font-src 'self' https://fonts.gstatic.com; "
        "connect-src 'self' wss: https:; "
        "frame-ancestors 'none'"
    )
    
    # Audit Configuration
    AUDIT_LOG_RETENTION_DAYS: int = 2555  # 7 years
    AUDIT_LOG_LEVEL: str = "INFO"
    
    # Privacy Configuration
    PRIVACY_OFFICER_EMAIL: str = "privacy@anzx.ai"
    PRIVACY_OFFICER_PHONE: str = "+61 2 8000 0000"
    DATA_RETENTION_YEARS: int = 7
    
    # Breach Notification Configuration
    OAIC_NOTIFICATION_DEADLINE_HOURS: int = 72
    BREACH_RESPONSE_TEAM_EMAIL: str = "security@anzx.ai"
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    class Config:
        env_file = ".env"


# Global security settings
security_settings = SecuritySettings()