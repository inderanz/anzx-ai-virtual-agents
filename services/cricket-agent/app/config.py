"""
Cricket Agent Configuration
Robust configuration with Secret Manager + Workload Identity
Safe fallbacks for local dev, public/private mode guards
"""

import os
import json
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, validator
from pydantic_settings import BaseSettings
from google.cloud import secretmanager
import logging

logger = logging.getLogger(__name__)

class TeamInfo(BaseModel):
    """Team information from IDs bundle"""
    name: str = Field(..., description="Team name")
    team_id: str = Field(..., description="Team ID")

class IDsBundle(BaseModel):
    """CSCC IDs bundle schema"""
    tenant: str = Field(..., description="PlayHQ tenant")
    org_id: str = Field(..., description="Organization ID")
    season_id: str = Field(..., description="Season ID")
    grade_id: str = Field(..., description="Grade ID")
    teams: List[TeamInfo] = Field(..., description="Team information")

class Settings(BaseSettings):
    """Application settings with robust secret management"""
    
    # Environment
    app_env: str = Field(default="dev", description="Application environment")
    port: int = Field(default=8080, description="Service port")
    
    # Google Cloud configuration
    gcp_project: Optional[str] = Field(default=None, description="GCP project ID")
    region: str = Field(default="australia-southeast1", description="GCP region")
    vertex_location: str = Field(default="australia-southeast1", description="Vertex AI location")
    
    # AI Models
    vertex_model: str = Field(default="gemini-1.5-flash", description="Vertex AI model")
    embed_model: str = Field(default="text-embedding-005", description="Embedding model")
    
    # PlayHQ configuration
    playhq_mode: str = Field(default="public", description="PlayHQ mode: public, private")
    playhq_base_url: str = Field(default="https://api.playhq.com/v1", description="PlayHQ API base URL")
    
    # Vector store configuration
    vector_backend: str = Field(default="vertex_rag", description="Vector store backend")
    
    # GCS configuration
    gcs_bucket: Optional[str] = Field(default=None, description="GCS bucket for data storage")
    
    # Sync configuration
    match_days: str = Field(default="Fri,Sat", description="Match days hint (comma-separated)")
    recent_completed_limit: int = Field(default=5, description="Number of recent completed games to fetch")
    
    # Secret references (can be Secret Manager refs or raw values)
    secret_playhq_api_key: Optional[str] = Field(default=None, description="PlayHQ API key secret ref")
    secret_ids_bundle: Optional[str] = Field(default=None, description="CSCC IDs bundle secret ref")
    secret_internal_token: Optional[str] = Field(default=None, description="Internal token secret ref")
    secret_playhq_private_token: Optional[str] = Field(default=None, description="Private token secret ref")
    secret_playhq_webhook_secret: Optional[str] = Field(default=None, description="PlayHQ webhook secret ref")
    
    # Resolved secrets (populated at runtime)
    playhq_api_key: Optional[str] = Field(default=None, description="Resolved PlayHQ API key")
    ids_bundle: Optional[IDsBundle] = Field(default=None, description="Resolved IDs bundle")
    internal_token: Optional[str] = Field(default=None, description="Resolved internal token")
    playhq_private_token: Optional[str] = Field(default=None, description="Resolved private token")
    playhq_webhook_secret: Optional[str] = Field(default=None, description="Resolved webhook secret")
    
    # Service metadata
    service_name: str = Field(default="cricket-agent", description="Service name")
    version: str = Field(default="1.0.0", description="Service version")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    @validator('playhq_mode')
    def validate_playhq_mode(cls, v):
        if v not in ['public', 'private']:
            raise ValueError('playhq_mode must be "public" or "private"')
        return v
    
    @validator('vector_backend')
    def validate_vector_backend(cls, v):
        allowed = ['vertex_rag', 'knowledge_service', 'redis', 'pgvector']
        if v not in allowed:
            raise ValueError(f'vector_backend must be one of: {allowed}')
        return v

# Global settings instance
_settings: Optional[Settings] = None

def read_secret(ref_or_value: str | None) -> str | None:
    """
    Read secret from Secret Manager or return raw value for local dev
    
    Args:
        ref_or_value: Secret Manager reference (projects/...) or raw value
        
    Returns:
        Secret value or None if not found
        
    Raises:
        ValueError: If secret reference is invalid
    """
    if not ref_or_value:
        return None
    
    # If it's a Secret Manager reference
    if ref_or_value.startswith("projects/"):
        try:
            client = secretmanager.SecretManagerServiceClient()
            response = client.access_secret_version(request={"name": ref_or_value})
            secret_value = response.payload.data.decode("UTF-8")
            logger.info(f"Loaded secret from Secret Manager: {ref_or_value}")
            return secret_value
        except Exception as e:
            logger.error(f"Failed to load secret {ref_or_value}: {e}")
            raise ValueError(f"Failed to load secret {ref_or_value}: {e}")
    else:
        # Raw value for local dev
        logger.debug(f"Using raw secret value for local dev")
        return ref_or_value

def get_settings() -> Settings:
    """Get application settings with secret resolution and validation"""
    global _settings
    
    if _settings is None:
        _settings = Settings()
        
        # Resolve secrets
        _settings = _resolve_secrets(_settings)
        
        # Validate configuration
        _validate_configuration(_settings)
    
    return _settings

def _resolve_secrets(settings: Settings) -> Settings:
    """Resolve secrets from Secret Manager or environment"""
    try:
        # Resolve PlayHQ API key
        if settings.secret_playhq_api_key:
            settings.playhq_api_key = read_secret(settings.secret_playhq_api_key)
        
        # Resolve IDs bundle
        if settings.secret_ids_bundle:
            bundle_json = read_secret(settings.secret_ids_bundle)
            if bundle_json:
                try:
                    bundle_data = json.loads(bundle_json)
                    settings.ids_bundle = IDsBundle(**bundle_data)
                except Exception as e:
                    raise ValueError(f"Invalid IDs bundle JSON: {e}")
        
        # Resolve internal token
        if settings.secret_internal_token:
            settings.internal_token = read_secret(settings.secret_internal_token)
        
        # Resolve private token (only if private mode)
        if settings.playhq_mode == "private" and settings.secret_playhq_private_token:
            settings.playhq_private_token = read_secret(settings.secret_playhq_private_token)
        
        # Resolve webhook secret (only if private mode)
        if settings.playhq_mode == "private" and settings.secret_playhq_webhook_secret:
            settings.playhq_webhook_secret = read_secret(settings.secret_playhq_webhook_secret)
        
        logger.info("Secrets resolved successfully")
        
    except Exception as e:
        logger.error(f"Failed to resolve secrets: {e}")
        raise
    
    return settings

def _validate_configuration(settings: Settings) -> None:
    """Validate configuration based on mode and required secrets"""
    errors = []
    
    # Validate required secrets for public mode
    if settings.playhq_mode == "public":
        if not settings.playhq_api_key:
            errors.append("SECRET_PLAYHQ_API_KEY is required for public mode")
        if not settings.ids_bundle:
            errors.append("SECRET_IDS_BUNDLE is required for public mode")
        if not settings.internal_token:
            errors.append("SECRET_INTERNAL_TOKEN is required")
    
    # Validate required secrets for private mode
    elif settings.playhq_mode == "private":
        if not settings.playhq_api_key:
            errors.append("SECRET_PLAYHQ_API_KEY is required for private mode")
        if not settings.ids_bundle:
            errors.append("SECRET_IDS_BUNDLE is required for private mode")
        if not settings.internal_token:
            errors.append("SECRET_INTERNAL_TOKEN is required")
        if not settings.playhq_private_token:
            errors.append("SECRET_PLAYHQ_PRIVATE_TOKEN is required for private mode")
    
    # Validate IDs bundle schema
    if settings.ids_bundle:
        bundle = settings.ids_bundle
        if not bundle.tenant:
            errors.append("IDs bundle missing tenant")
        if not bundle.org_id:
            errors.append("IDs bundle missing org_id")
        if not bundle.season_id:
            errors.append("IDs bundle missing season_id")
        if not bundle.grade_id:
            errors.append("IDs bundle missing grade_id")
        if not bundle.teams:
            errors.append("IDs bundle missing teams")
        elif len(bundle.teams) == 0:
            errors.append("IDs bundle has no teams")
    
    if errors:
        error_msg = "Configuration validation failed:\n" + "\n".join(f"  - {error}" for error in errors)
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    logger.info(f"Configuration validated successfully for {settings.playhq_mode} mode")

def is_private_mode() -> bool:
    """Check if running in private mode"""
    settings = get_settings()
    return settings.playhq_mode == "private"

def get_playhq_headers() -> Dict[str, str]:
    """Get PlayHQ API headers"""
    settings = get_settings()
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    if settings.playhq_api_key:
        headers["x-api-key"] = settings.playhq_api_key
    
    if settings.ids_bundle and settings.ids_bundle.tenant:
        headers["x-phq-tenant"] = settings.ids_bundle.tenant
    
    return headers

def get_cscc_team_ids() -> List[str]:
    """Get Caroline Springs CC team IDs as a list"""
    settings = get_settings()
    
    if not settings.ids_bundle or not settings.ids_bundle.teams:
        return []
    
    return [team.team_id for team in settings.ids_bundle.teams]

def get_cscc_org_id() -> Optional[str]:
    """Get Caroline Springs CC organization ID"""
    settings = get_settings()
    return settings.ids_bundle.org_id if settings.ids_bundle else None

def get_cscc_season_id() -> Optional[str]:
    """Get Caroline Springs CC season ID"""
    settings = get_settings()
    return settings.ids_bundle.season_id if settings.ids_bundle else None

def get_cscc_grade_id() -> Optional[str]:
    """Get Caroline Springs CC grade ID"""
    settings = get_settings()
    return settings.ids_bundle.grade_id if settings.ids_bundle else None
