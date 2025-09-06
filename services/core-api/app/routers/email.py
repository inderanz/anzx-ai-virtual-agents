"""
Email Integration API Endpoints
"""

import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, EmailStr

from ..utils.database import get_db
from ..middleware.auth import get_current_user, get_organization_id
from ..services.email_service import email_service
from ..models.user import User
from ..config.email_config import EMAIL_PROVIDERS

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/email", tags=["email"])


# Pydantic models
class EmailConfigCreate(BaseModel):
    provider: str = Field(..., description="Email provider (gmail, outlook, yahoo, custom)")
    email_address: EmailStr = Field(..., description="Email address")
    username: str = Field(..., description="Username (usually same as email)")
    password: str = Field(..., description="Password or app password")
    display_name: Optional[str] = Field(default="ANZx.ai Support", description="Display name for outgoing emails")
    
    # Custom server settings (for custom provider)
    imap_server: Optional[str] = Field(None, description="Custom IMAP server")
    imap_port: Optional[int] = Field(993, description="IMAP port")
    smtp_server: Optional[str] = Field(None, description="Custom SMTP server")
    smtp_port: Optional[int] = Field(587, description="SMTP port")
    
    # Auto-reply settings
    auto_reply: Optional[bool] = Field(default=True, description="Enable auto-reply")
    signature: Optional[str] = Field(default="", description="Email signature")
    escalation_email: Optional[EmailStr] = Field(None, description="Escalation email address")
    
    # Business hours
    business_hours: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Business hours configuration")


class EmailConfigUpdate(BaseModel):
    display_name: Optional[str] = Field(None, description="Display name")
    auto_reply: Optional[bool] = Field(None, description="Enable auto-reply")
    signature: Optional[str] = Field(None, description="Email signature")
    escalation_email: Optional[EmailStr] = Field(None, description="Escalation email")
    business_hours: Optional[Dict[str, Any]] = Field(None, description="Business hours")


class EmailResponse(BaseModel):
    thread_id: str = Field(..., description="Email thread ID")
    response_content: str = Field(..., description="Response content")
    is_ai_generated: Optional[bool] = Field(default=True, description="Whether response is AI generated")


class EmailEscalation(BaseModel):
    thread_id: str = Field(..., description="Email thread ID")
    escalation_reason: str = Field(..., description="Reason for escalation")


# Email configuration endpoints
@router.post("/config", response_model=Dict[str, Any])
async def setup_email_integration(
    config: EmailConfigCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id)
):
    """Set up email integration for the organization"""
    try:
        # Build email configuration
        email_config = {
            "provider": config.provider,
            "email_address": config.email_address,
            "username": config.username,
            "password": config.password,
            "display_name": config.display_name,
            "auto_reply": config.auto_reply,
            "signature": config.signature,
            "escalation_email": config.escalation_email,
            "business_hours": config.business_hours or {}
        }
        
        # Add provider-specific settings
        if config.provider in EMAIL_PROVIDERS:
            provider_config = EMAIL_PROVIDERS[config.provider]
            email_config.update({
                "imap_server": provider_config["imap_server"],
                "imap_port": provider_config["imap_port"],
                "smtp_server": provider_config["smtp_server"],
                "smtp_port": provider_config["smtp_port"]
            })
        elif config.provider == "custom":
            email_config.update({
                "imap_server": config.imap_server,
                "imap_port": config.imap_port,
                "smtp_server": config.smtp_server,
                "smtp_port": config.smtp_port
            })
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid email provider"
            )
        
        # Set up email integration
        result = await email_service.setup_email_integration(
            db=db,
            organization_id=organization_id,
            email_config=email_config
        )
        
        # Start background email processing
        background_tasks.add_task(
            process_emails_background,
            organization_id=organization_id
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Email integration setup failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to set up email integration"
        )


@router.get("/config", response_model=Dict[str, Any])
async def get_email_config(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id)
):
    """Get current email configuration"""
    try:
        from ..models.user import Organization
        
        org = db.query(Organization).filter(Organization.id == organization_id).first()
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )
        
        email_settings = org.email_settings or {}
        
        # Remove sensitive information
        safe_config = {
            "enabled": email_settings.get("enabled", False),
            "email_address": email_settings.get("email_address"),
            "display_name": email_settings.get("display_name"),
            "auto_reply": email_settings.get("auto_reply", True),
            "signature": email_settings.get("signature", ""),
            "escalation_email": email_settings.get("escalation_email"),
            "business_hours": email_settings.get("business_hours", {}),
            "features_enabled": {
                "auto_reply": email_settings.get("auto_reply", True),
                "conversation_threading": True,
                "ai_responses": True,
                "escalation": bool(email_settings.get("escalation_email"))
            }
        }
        
        return safe_config
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get email config: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve email configuration"
        )


@router.put("/config", response_model=Dict[str, Any])
async def update_email_config(
    config_update: EmailConfigUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id)
):
    """Update email configuration"""
    try:
        from ..models.user import Organization
        
        org = db.query(Organization).filter(Organization.id == organization_id).first()
        if not org or not org.email_settings or not org.email_settings.get("enabled"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Email integration not set up"
            )
        
        # Update settings
        email_settings = org.email_settings.copy()
        
        if config_update.display_name is not None:
            email_settings["display_name"] = config_update.display_name
        
        if config_update.auto_reply is not None:
            email_settings["auto_reply"] = config_update.auto_reply
        
        if config_update.signature is not None:
            email_settings["signature"] = config_update.signature
        
        if config_update.escalation_email is not None:
            email_settings["escalation_email"] = config_update.escalation_email
        
        if config_update.business_hours is not None:
            email_settings["business_hours"] = config_update.business_hours
        
        org.email_settings = email_settings
        db.commit()
        
        return {"success": True, "message": "Email configuration updated"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update email config: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update email configuration"
        )


@router.delete("/config")
async def disable_email_integration(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id)
):
    """Disable email integration"""
    try:
        from ..models.user import Organization
        
        org = db.query(Organization).filter(Organization.id == organization_id).first()
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )
        
        # Disable email integration
        if org.email_settings:
            org.email_settings["enabled"] = False
        
        db.commit()
        
        return {"success": True, "message": "Email integration disabled"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to disable email integration: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to disable email integration"
        )


# Email processing endpoints
@router.post("/process", response_model=Dict[str, Any])
async def process_emails(
    background_tasks: BackgroundTasks,
    limit: Optional[int] = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id)
):
    """Manually trigger email processing"""
    try:
        result = await email_service.process_incoming_emails(
            db=db,
            organization_id=organization_id,
            limit=limit
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Email processing failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process emails"
        )


@router.get("/threads", response_model=List[Dict[str, Any]])
async def get_email_threads(
    status: Optional[str] = None,
    limit: Optional[int] = 50,
    offset: Optional[int] = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id)
):
    """Get email threads"""
    try:
        threads = await email_service.get_email_threads(
            db=db,
            organization_id=organization_id,
            status=status,
            limit=limit,
            offset=offset
        )
        
        return threads
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get email threads: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve email threads"
        )


@router.post("/respond", response_model=Dict[str, Any])
async def send_email_response(
    response: EmailResponse,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id)
):
    """Send email response"""
    try:
        result = await email_service.send_email_response(
            db=db,
            organization_id=organization_id,
            thread_id=response.thread_id,
            response_content=response.response_content,
            is_ai_generated=response.is_ai_generated
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to send email response: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send email response"
        )


@router.post("/escalate", response_model=Dict[str, Any])
async def escalate_email_thread(
    escalation: EmailEscalation,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id)
):
    """Escalate email thread to human agent"""
    try:
        result = await email_service.escalate_email_thread(
            db=db,
            organization_id=organization_id,
            thread_id=escalation.thread_id,
            escalation_reason=escalation.escalation_reason
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to escalate email thread: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to escalate email thread"
        )


@router.get("/providers", response_model=Dict[str, Any])
async def get_email_providers():
    """Get available email providers and their configurations"""
    return {
        "providers": EMAIL_PROVIDERS,
        "instructions": {
            "gmail": "Enable 2-factor authentication and generate an App Password in your Google Account settings.",
            "outlook": "Use your regular email password or set up OAuth authentication.",
            "yahoo": "Generate an App Password in your Yahoo Account Security settings.",
            "custom": "Enter your custom IMAP and SMTP server details."
        }
    }


# Background task functions
async def process_emails_background(organization_id: str):
    """Background task to process emails"""
    try:
        from ..utils.database import get_db
        
        db = next(get_db())
        await email_service.process_incoming_emails(
            db=db,
            organization_id=organization_id,
            limit=50
        )
        
    except Exception as e:
        logger.error(f"Background email processing failed: {e}")
    finally:
        db.close()