"""
Compliance API endpoints
Handles privacy requests, consent management, and breach notifications
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel, EmailStr

from ..compliance.privacy import (
    app_compliance, ConsentType, PersonalInformationType, 
    ConsentRecord, PrivacyNotice
)
from ..compliance.breach_notification import (
    breach_notification_system, BreachType, BreachSeverity,
    AffectedDataType, DataBreach
)
from ..compliance.audit import compliance_auditor, AuditEventType

router = APIRouter(prefix="/api/v1/compliance", tags=["compliance"])


# Request/Response models
class ConsentRequest(BaseModel):
    consent_type: ConsentType
    purpose: str
    information_types: List[PersonalInformationType]
    agreed: bool


class ConsentResponse(BaseModel):
    consent_id: str
    status: str
    granted_at: datetime
    expires_at: Optional[datetime] = None


class PrivacyRequest(BaseModel):
    request_type: str  # access, correction, deletion, portability
    description: str
    contact_email: EmailStr


class BreachReportRequest(BaseModel):
    title: str
    description: str
    breach_type: BreachType
    severity: BreachSeverity
    affected_individuals_count: int = 0
    affected_data_types: List[AffectedDataType] = []
    occurred_at: Optional[datetime] = None


# Dependency to get current user
async def get_current_user(request: Request) -> str:
    """Extract user ID from JWT token"""
    # In practice, would validate JWT and extract user ID
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Mock user ID extraction
    return "user_123"


def get_client_ip(request: Request) -> str:
    """Get client IP address"""
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


@router.get("/privacy-notice")
async def get_privacy_notice():
    """Get privacy notice for APP 5 compliance"""
    return app_compliance.generate_privacy_notice()


@router.post("/consent", response_model=ConsentResponse)
async def give_consent(
    consent_request: ConsentRequest,
    request: Request,
    user_id: str = Depends(get_current_user)
):
    """Collect user consent for data processing"""
    if not consent_request.agreed:
        raise HTTPException(status_code=400, detail="Consent must be explicitly given")
    
    client_ip = get_client_ip(request)
    user_agent = request.headers.get("User-Agent", "")
    
    # Collect consent
    consent = app_compliance.collect_consent(
        user_id=user_id,
        consent_type=consent_request.consent_type,
        purpose=consent_request.purpose,
        information_types=consent_request.information_types,
        ip_address=client_ip,
        user_agent=user_agent,
        evidence={
            "timestamp": datetime.utcnow().isoformat(),
            "method": "web_form",
            "version": "1.0"
        }
    )
    
    # Log consent event
    compliance_auditor.log_event(
        event_type=AuditEventType.CONSENT_GIVEN,
        action=f"consent_given_{consent_request.consent_type}",
        user_id=user_id,
        ip_address=client_ip,
        details={
            "consent_type": consent_request.consent_type,
            "purpose": consent_request.purpose,
            "information_types": [t.value for t in consent_request.information_types]
        }
    )
    
    return ConsentResponse(
        consent_id=f"consent_{user_id}_{consent.consent_type}",
        status=consent.status,
        granted_at=consent.granted_at,
        expires_at=consent.expires_at
    )


@router.delete("/consent/{consent_type}")
async def withdraw_consent(
    consent_type: ConsentType,
    request: Request,
    user_id: str = Depends(get_current_user)
):
    """Withdraw user consent"""
    client_ip = get_client_ip(request)
    
    success = app_compliance.withdraw_consent(
        user_id=user_id,
        consent_type=consent_type
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Consent not found")
    
    # Log consent withdrawal
    compliance_auditor.log_event(
        event_type=AuditEventType.CONSENT_WITHDRAWN,
        action=f"consent_withdrawn_{consent_type}",
        user_id=user_id,
        ip_address=client_ip,
        details={"consent_type": consent_type}
    )
    
    return {"message": "Consent withdrawn successfully"}


@router.get("/consent")
async def get_user_consents(user_id: str = Depends(get_current_user)):
    """Get all user consent records"""
    consents = app_compliance.get_user_consents(user_id)
    
    return {
        "consents": [
            {
                "consent_type": c.consent_type,
                "status": c.status,
                "purpose": c.purpose,
                "granted_at": c.granted_at,
                "withdrawn_at": c.withdrawn_at,
                "expires_at": c.expires_at
            }
            for c in consents
        ]
    }


@router.post("/privacy-request")
async def submit_privacy_request(
    privacy_request: PrivacyRequest,
    request: Request,
    user_id: str = Depends(get_current_user)
):
    """Submit privacy request (access, correction, deletion, portability)"""
    client_ip = get_client_ip(request)
    
    # Log privacy request
    request_id = compliance_auditor.log_privacy_event(
        action=f"privacy_request_{privacy_request.request_type}",
        user_id=user_id,
        ip_address=client_ip,
        details={
            "request_type": privacy_request.request_type,
            "description": privacy_request.description,
            "contact_email": privacy_request.contact_email
        }
    )
    
    # Log in APP compliance system
    app_compliance.log_access_request(
        user_id=user_id,
        request_type=privacy_request.request_type,
        details={
            "description": privacy_request.description,
            "contact_email": privacy_request.contact_email,
            "submitted_at": datetime.utcnow().isoformat(),
            "ip_address": client_ip
        }
    )
    
    return {
        "request_id": request_id,
        "message": "Privacy request submitted successfully",
        "expected_response_time": "30 days",
        "contact_email": "privacy@anzx.ai"
    }


# Admin endpoints for breach management
@router.post("/breach/report")
async def report_breach(
    breach_request: BreachReportRequest,
    request: Request,
    user_id: str = Depends(get_current_user)  # Admin user
):
    """Report a data breach (admin only)"""
    # In practice, would check admin permissions
    
    breach_id = breach_notification_system.report_breach(
        title=breach_request.title,
        description=breach_request.description,
        breach_type=breach_request.breach_type,
        severity=breach_request.severity,
        reported_by=user_id,
        occurred_at=breach_request.occurred_at,
        affected_individuals_count=breach_request.affected_individuals_count,
        affected_data_types=breach_request.affected_data_types
    )
    
    return {
        "breach_id": breach_id,
        "message": "Breach reported successfully",
        "assessment_required": True
    }


@router.get("/breach/{breach_id}")
async def get_breach(
    breach_id: str,
    user_id: str = Depends(get_current_user)  # Admin user
):
    """Get breach details (admin only)"""
    breach = breach_notification_system.get_breach(breach_id)
    
    if not breach:
        raise HTTPException(status_code=404, detail="Breach not found")
    
    return breach


@router.get("/breaches")
async def list_breaches(
    status: Optional[str] = None,
    severity: Optional[BreachSeverity] = None,
    user_id: str = Depends(get_current_user)  # Admin user
):
    """List all breaches (admin only)"""
    breaches = breach_notification_system.list_breaches(
        status_filter=status,
        severity_filter=severity
    )
    
    return {"breaches": breaches}


@router.post("/breach/{breach_id}/notify-oaic")
async def notify_oaic(
    breach_id: str,
    contact_person: str,
    contact_email: EmailStr,
    contact_phone: str,
    user_id: str = Depends(get_current_user)  # Admin user
):
    """Submit OAIC notification for breach"""
    success = breach_notification_system.notify_oaic(
        breach_id=breach_id,
        contact_person=contact_person,
        contact_email=contact_email,
        contact_phone=contact_phone
    )
    
    if not success:
        raise HTTPException(status_code=400, detail="OAIC notification failed")
    
    return {"message": "OAIC notification submitted successfully"}


@router.post("/breach/{breach_id}/notify-individuals")
async def notify_individuals(
    breach_id: str,
    notification_method: str = "email",
    custom_message: Optional[str] = None,
    user_id: str = Depends(get_current_user)  # Admin user
):
    """Notify affected individuals about breach"""
    notifications_sent = breach_notification_system.notify_individuals(
        breach_id=breach_id,
        notification_method=notification_method,
        custom_message=custom_message
    )
    
    return {
        "message": f"Notifications sent to {notifications_sent} individuals",
        "method": notification_method
    }