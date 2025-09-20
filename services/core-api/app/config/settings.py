"""
Application Settings
Configuration management using Pydantic Settings
"""

import os
from typing import List, Optional
from functools import lru_cache

from pydantic import BaseSettings, validator


class Settings(BaseSettings):
    """Application settings"""
    
    # Environment
    environment: str = "development"
    debug: bool = True
    log_level: str = "INFO"
    
    # Database
    database_url: str = "postgresql://anzx_user:local_dev_password@localhost:5432/anzx_ai_platform"
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # Security
    jwt_secret_key: str = "local_dev_jwt_secret_key_12345"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    
    # CORS
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost",
        "https://anzx.ai",
        "https://*.anzx.ai"
    ]
    
    # Google Cloud
    project_id: str = "extreme-gecko-466211-t1"
    region: str = "australia-southeast1"
    google_application_credentials: Optional[str] = None
    
    # Stripe
    stripe_secret_key: Optional[str] = None
    stripe_publishable_key: Optional[str] = None
    stripe_webhook_secret: Optional[str] = None
    
    # Vertex AI (Google Cloud)
    vertex_ai_project: str = "extreme-gecko-466211-t1"
    vertex_ai_location: str = "australia-southeast1"
    
    # Email
    smtp_host: str = "localhost"
    smtp_port: int = 1025
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_from: str = "noreply@anzx.local"
    
    # File uploads
    max_upload_size: int = 50 * 1024 * 1024  # 50MB
    allowed_file_types: List[str] = [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/plain",
        "text/csv"
    ]
    
    # Rate limiting
    rate_limit_per_minute: int = 60
    
    # Feature flags
    enable_agent_space: bool = True
    enable_mcp_tools: bool = True
    enable_analytics: bool = True
    
    @validator("cors_origins", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Production environment overrides
        if self.environment == "production":
            self.debug = False
            self.log_level = "WARNING"
            # Database URL should come from environment variable in production
            if "DATABASE_URL" in os.environ:
                self.database_url = os.environ["DATABASE_URL"]
            # Redis URL should come from environment variable in production
            if "REDIS_URL" in os.environ:
                self.redis_url = os.environ["REDIS_URL"]
            # JWT secret should come from environment variable in production
            if "JWT_SECRET_KEY" in os.environ:
                self.jwt_secret_key = os.environ["JWT_SECRET_KEY"]
            # SMTP configuration for production
            if "SMTP_HOST" in os.environ:
                self.smtp_host = os.environ["SMTP_HOST"]
                self.smtp_port = int(os.environ.get("SMTP_PORT", "587"))
                self.smtp_user = os.environ.get("SMTP_USER")
                self.smtp_password = os.environ.get("SMTP_PASSWORD")
                self.smtp_from = os.environ.get("SMTP_FROM", "noreply@anzx.ai")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()