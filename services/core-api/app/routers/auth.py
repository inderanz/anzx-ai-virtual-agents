"""
Authentication API endpoints
"""

from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from ..models.database import get_db
from ..models.user import User, Organization
from ..auth.firebase import firebase_auth
from ..auth.jwt_handler import jwt_handler
from ..auth.dependencies import get_current_user, get_current_user_optional
from ..compliance.audit import compliance_auditor, AuditEventType

router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])


# Request/Response models
class LoginRequest(BaseModel):
    firebase_token: str


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    user: dict
    organization: Optional[dict] = None


class RegisterRequest(BaseModel):
    firebase_token: str
    organization_name: Optional[str] = None


class RefreshRequest(BaseModel):
    refresh_token: str


class UserProfile(BaseModel):
    id: str
    email: str
    display_name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar_url: Optional[str] = None
    role: str
    organization_id: Optional[str] = None
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None


@router.post("/login", response_model=LoginResponse)
async def login(
    request: Request,
    login_request: LoginRequest,
    db: Session = Depends(get_db)
):
    """Login with Firebase token"""
    client_ip = _get_client_ip(request)
    
    # Verify Firebase token
    firebase_user = await firebase_auth.verify_token(login_request.firebase_token)
    
    # Find or create user
    user = db.query(User).filter(User.firebase_uid == firebase_user["uid"]).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found. Please register first."
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Get organization
    organization = None
    if user.organization_id:
        org = db.query(Organization).filter(Organization.id == user.organization_id).first()
        if org:
            organization = {
                "id": str(org.id),
                "name": org.name,
                "subscription_plan": org.subscription_plan,
                "subscription_status": org.subscription_status
            }
    
    # Create JWT tokens
    access_token = jwt_handler.create_access_token(
        user_id=str(user.id),
        email=user.email,
        organization_id=str(user.organization_id) if user.organization_id else None,
        roles=[user.role]
    )
    
    refresh_token = jwt_handler.create_refresh_token(str(user.id))
    
    # Log successful login
    compliance_auditor.log_event(
        event_type=AuditEventType.USER_LOGIN,
        action="user_login_success",
        outcome="success",
        user_id=str(user.id),
        ip_address=client_ip,
        details={
            "provider": firebase_user.get("provider"),
            "organization_id": str(user.organization_id) if user.organization_id else None
        }
    )
    
    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user={
            "id": str(user.id),
            "email": user.email,
            "display_name": user.display_name,
            "role": user.role,
            "organization_id": str(user.organization_id) if user.organization_id else None
        },
        organization=organization
    )


@router.post("/register", response_model=LoginResponse)
async def register(
    request: Request,
    register_request: RegisterRequest,
    db: Session = Depends(get_db)
):
    """Register new user with Firebase token"""
    client_ip = _get_client_ip(request)
    
    # Verify Firebase token
    firebase_user = await firebase_auth.verify_token(register_request.firebase_token)
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.firebase_uid == firebase_user["uid"]).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists"
        )
    
    # Create organization if provided
    organization = None
    if register_request.organization_name:
        organization = Organization(
            name=register_request.organization_name
        )
        db.add(organization)
        db.flush()  # Get the ID
    
    # Create user
    user = User(
        firebase_uid=firebase_user["uid"],
        email=firebase_user["email"],
        email_verified=firebase_user.get("email_verified", False),
        display_name=firebase_user.get("name"),
        avatar_url=firebase_user.get("picture"),
        organization_id=organization.id if organization else None,
        role="admin" if organization else "user"
    )
    
    db.add(user)
    db.commit()
    
    # Create JWT tokens
    access_token = jwt_handler.create_access_token(
        user_id=str(user.id),
        email=user.email,
        organization_id=str(user.organization_id) if user.organization_id else None,
        roles=[user.role]
    )
    
    refresh_token = jwt_handler.create_refresh_token(str(user.id))
    
    # Log successful registration
    compliance_auditor.log_event(
        event_type=AuditEventType.USER_LOGIN,
        action="user_registration_success",
        outcome="success",
        user_id=str(user.id),
        ip_address=client_ip,
        details={
            "provider": firebase_user.get("provider"),
            "organization_created": organization is not None,
            "organization_id": str(user.organization_id) if user.organization_id else None
        }
    )
    
    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user={
            "id": str(user.id),
            "email": user.email,
            "display_name": user.display_name,
            "role": user.role,
            "organization_id": str(user.organization_id) if user.organization_id else None
        },
        organization={
            "id": str(organization.id),
            "name": organization.name,
            "subscription_plan": organization.subscription_plan,
            "subscription_status": organization.subscription_status
        } if organization else None
    )


@router.post("/refresh", response_model=dict)
async def refresh_token(
    refresh_request: RefreshRequest,
    db: Session = Depends(get_db)
):
    """Refresh access token"""
    # Verify refresh token
    user_id = jwt_handler.verify_refresh_token(refresh_request.refresh_token)
    
    # Get user
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or inactive"
        )
    
    # Create new access token
    access_token = jwt_handler.create_access_token(
        user_id=str(user.id),
        email=user.email,
        organization_id=str(user.organization_id) if user.organization_id else None,
        roles=[user.role]
    )
    
    return {"access_token": access_token}


@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user profile"""
    user = db.query(User).filter(User.id == current_user["user_id"]).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserProfile(
        id=str(user.id),
        email=user.email,
        display_name=user.display_name,
        first_name=user.first_name,
        last_name=user.last_name,
        avatar_url=user.avatar_url,
        role=user.role,
        organization_id=str(user.organization_id) if user.organization_id else None,
        is_active=user.is_active,
        created_at=user.created_at,
        last_login=user.last_login
    )


@router.post("/logout")
async def logout(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """Logout user"""
    client_ip = _get_client_ip(request)
    
    # Log logout event
    compliance_auditor.log_event(
        event_type=AuditEventType.USER_LOGOUT,
        action="user_logout",
        outcome="success",
        user_id=current_user["user_id"],
        ip_address=client_ip
    )
    
    return {"message": "Logged out successfully"}


def _get_client_ip(request: Request) -> str:
    """Get client IP address from request"""
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    return request.client.host if request.client else "unknown"