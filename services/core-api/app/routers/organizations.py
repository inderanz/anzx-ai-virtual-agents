"""
Organization management API endpoints
"""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..models.database import get_db
from ..models.user import Organization, User
from ..auth.dependencies import get_current_user, require_admin, require_organization_access
from ..compliance.audit import compliance_auditor, AuditEventType

router = APIRouter(prefix="/api/v1/organizations", tags=["organizations"])


# Request/Response models
class OrganizationCreate(BaseModel):
    name: str
    description: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[str] = None


class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[str] = None


class OrganizationResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[str] = None
    subscription_plan: str
    subscription_status: str
    created_at: datetime
    updated_at: datetime
    member_count: int


class OrganizationMember(BaseModel):
    id: str
    email: str
    display_name: Optional[str] = None
    role: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None


class InviteUserRequest(BaseModel):
    email: str
    role: str = "user"


@router.post("/", response_model=OrganizationResponse)
async def create_organization(
    request: Request,
    org_data: OrganizationCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new organization"""
    client_ip = _get_client_ip(request)
    
    # Check if user already has an organization
    user = db.query(User).filter(User.id == current_user["user_id"]).first()
    if user and user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already belongs to an organization"
        )
    
    # Create organization
    organization = Organization(
        name=org_data.name,
        description=org_data.description,
        website=org_data.website,
        industry=org_data.industry
    )
    
    db.add(organization)
    db.flush()  # Get the ID
    
    # Update user to be admin of the organization
    if user:
        user.organization_id = organization.id
        user.role = "admin"
    
    db.commit()
    
    # Get member count
    member_count = db.query(User).filter(User.organization_id == organization.id).count()
    
    # Log organization creation
    compliance_auditor.log_event(
        event_type=AuditEventType.DATA_ACCESS,
        action="organization_created",
        outcome="success",
        user_id=current_user["user_id"],
        ip_address=client_ip,
        details={
            "organization_id": str(organization.id),
            "organization_name": organization.name
        }
    )
    
    return OrganizationResponse(
        id=str(organization.id),
        name=organization.name,
        description=organization.description,
        website=organization.website,
        industry=organization.industry,
        subscription_plan=organization.subscription_plan,
        subscription_status=organization.subscription_status,
        created_at=organization.created_at,
        updated_at=organization.updated_at,
        member_count=member_count
    )


@router.get("/{organization_id}", response_model=OrganizationResponse)
async def get_organization(
    organization_id: str,
    current_user: dict = Depends(require_organization_access),
    db: Session = Depends(get_db)
):
    """Get organization details"""
    organization = db.query(Organization).filter(Organization.id == organization_id).first()
    
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    # Get member count
    member_count = db.query(User).filter(User.organization_id == organization.id).count()
    
    return OrganizationResponse(
        id=str(organization.id),
        name=organization.name,
        description=organization.description,
        website=organization.website,
        industry=organization.industry,
        subscription_plan=organization.subscription_plan,
        subscription_status=organization.subscription_status,
        created_at=organization.created_at,
        updated_at=organization.updated_at,
        member_count=member_count
    )


@router.put("/{organization_id}", response_model=OrganizationResponse)
async def update_organization(
    organization_id: str,
    org_data: OrganizationUpdate,
    request: Request,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update organization details"""
    client_ip = _get_client_ip(request)
    
    # Verify organization access
    await require_organization_access(organization_id, current_user)
    
    organization = db.query(Organization).filter(Organization.id == organization_id).first()
    
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    # Update fields
    update_data = org_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(organization, field, value)
    
    organization.updated_at = datetime.utcnow()
    db.commit()
    
    # Get member count
    member_count = db.query(User).filter(User.organization_id == organization.id).count()
    
    # Log organization update
    compliance_auditor.log_event(
        event_type=AuditEventType.DATA_ACCESS,
        action="organization_updated",
        outcome="success",
        user_id=current_user["user_id"],
        ip_address=client_ip,
        details={
            "organization_id": str(organization.id),
            "updated_fields": list(update_data.keys())
        }
    )
    
    return OrganizationResponse(
        id=str(organization.id),
        name=organization.name,
        description=organization.description,
        website=organization.website,
        industry=organization.industry,
        subscription_plan=organization.subscription_plan,
        subscription_status=organization.subscription_status,
        created_at=organization.created_at,
        updated_at=organization.updated_at,
        member_count=member_count
    )


@router.get("/{organization_id}/members", response_model=List[OrganizationMember])
async def get_organization_members(
    organization_id: str,
    current_user: dict = Depends(require_organization_access),
    db: Session = Depends(get_db)
):
    """Get organization members"""
    # Verify organization access
    await require_organization_access(organization_id, current_user)
    
    members = db.query(User).filter(User.organization_id == organization_id).all()
    
    return [
        OrganizationMember(
            id=str(member.id),
            email=member.email,
            display_name=member.display_name,
            role=member.role,
            is_active=member.is_active,
            created_at=member.created_at,
            last_login=member.last_login
        )
        for member in members
    ]


@router.post("/{organization_id}/invite")
async def invite_user(
    organization_id: str,
    invite_data: InviteUserRequest,
    request: Request,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Invite user to organization"""
    client_ip = _get_client_ip(request)
    
    # Verify organization access
    await require_organization_access(organization_id, current_user)
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == invite_data.email).first()
    if existing_user and existing_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already belongs to an organization"
        )
    
    # TODO: Implement email invitation system
    # For now, just log the invitation attempt
    compliance_auditor.log_event(
        event_type=AuditEventType.DATA_ACCESS,
        action="user_invitation_sent",
        outcome="success",
        user_id=current_user["user_id"],
        ip_address=client_ip,
        details={
            "organization_id": organization_id,
            "invited_email": invite_data.email,
            "invited_role": invite_data.role
        }
    )
    
    return {"message": f"Invitation sent to {invite_data.email}"}


@router.delete("/{organization_id}/members/{user_id}")
async def remove_member(
    organization_id: str,
    user_id: str,
    request: Request,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Remove member from organization"""
    client_ip = _get_client_ip(request)
    
    # Verify organization access
    await require_organization_access(organization_id, current_user)
    
    # Cannot remove yourself
    if user_id == current_user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot remove yourself from organization"
        )
    
    user = db.query(User).filter(
        User.id == user_id,
        User.organization_id == organization_id
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found in organization"
        )
    
    # Remove user from organization
    user.organization_id = None
    user.role = "user"
    db.commit()
    
    # Log member removal
    compliance_auditor.log_event(
        event_type=AuditEventType.DATA_ACCESS,
        action="member_removed",
        outcome="success",
        user_id=current_user["user_id"],
        ip_address=client_ip,
        details={
            "organization_id": organization_id,
            "removed_user_id": user_id,
            "removed_user_email": user.email
        }
    )
    
    return {"message": "Member removed successfully"}


def _get_client_ip(request: Request) -> str:
    """Get client IP address from request"""
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    return request.client.host if request.client else "unknown"