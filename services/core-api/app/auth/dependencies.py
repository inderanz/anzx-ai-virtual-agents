"""
Authentication dependencies for FastAPI
"""

from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .firebase import firebase_auth
from .jwt_handler import jwt_handler
from ..compliance.audit import compliance_auditor, AuditEventType

security = HTTPBearer()


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """
    Get current authenticated user from JWT or Firebase token
    
    Args:
        request: FastAPI request object
        credentials: Authorization credentials
        
    Returns:
        User information dictionary
    """
    token = credentials.credentials
    client_ip = _get_client_ip(request)
    
    try:
        # Try JWT token first (internal API)
        try:
            payload = jwt_handler.verify_token(token)
            user_info = {
                "user_id": payload["sub"],
                "email": payload["email"],
                "organization_id": payload.get("org_id"),
                "roles": payload.get("roles", []),
                "token_type": "jwt"
            }
            
            # Log successful authentication
            compliance_auditor.log_event(
                event_type=AuditEventType.USER_LOGIN,
                action="jwt_authentication_success",
                outcome="success",
                user_id=user_info["user_id"],
                ip_address=client_ip,
                details={"token_type": "jwt"}
            )
            
            return user_info
            
        except HTTPException:
            # If JWT fails, try Firebase token
            firebase_user = await firebase_auth.verify_token(token)
            user_info = {
                "user_id": firebase_user["uid"],
                "email": firebase_user["email"],
                "email_verified": firebase_user["email_verified"],
                "name": firebase_user["name"],
                "picture": firebase_user["picture"],
                "provider": firebase_user["provider"],
                "custom_claims": firebase_user["custom_claims"],
                "token_type": "firebase"
            }
            
            # Log successful authentication
            compliance_auditor.log_event(
                event_type=AuditEventType.USER_LOGIN,
                action="firebase_authentication_success",
                outcome="success",
                user_id=user_info["user_id"],
                ip_address=client_ip,
                details={"token_type": "firebase", "provider": firebase_user["provider"]}
            )
            
            return user_info
            
    except HTTPException as e:
        # Log failed authentication
        compliance_auditor.log_event(
            event_type=AuditEventType.USER_LOGIN,
            action="authentication_failed",
            outcome="failure",
            ip_address=client_ip,
            details={"error": str(e.detail)},
            risk_level="medium"
        )
        raise e


async def get_current_user_optional(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[Dict[str, Any]]:
    """
    Get current user if authenticated, otherwise return None
    
    Args:
        request: FastAPI request object
        credentials: Optional authorization credentials
        
    Returns:
        User information dictionary or None
    """
    if not credentials:
        return None
    
    try:
        return await get_current_user(request, credentials)
    except HTTPException:
        return None


async def require_roles(required_roles: list):
    """
    Dependency factory for role-based access control
    
    Args:
        required_roles: List of required roles
        
    Returns:
        Dependency function
    """
    async def check_roles(current_user: Dict[str, Any] = Depends(get_current_user)):
        user_roles = current_user.get("roles", [])
        custom_claims = current_user.get("custom_claims", {})
        
        # Check JWT roles
        if any(role in user_roles for role in required_roles):
            return current_user
        
        # Check Firebase custom claims
        if any(custom_claims.get(role, False) for role in required_roles):
            return current_user
        
        # Log unauthorized access attempt
        compliance_auditor.log_event(
            event_type=AuditEventType.SECURITY_INCIDENT,
            action="unauthorized_access_attempt",
            outcome="blocked",
            user_id=current_user.get("user_id"),
            details={
                "required_roles": required_roles,
                "user_roles": user_roles,
                "custom_claims": custom_claims
            },
            risk_level="high"
        )
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Insufficient permissions. Required roles: {required_roles}"
        )
    
    return check_roles


async def require_organization_access(
    organization_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Require user to have access to specific organization
    
    Args:
        organization_id: Organization ID to check access for
        current_user: Current authenticated user
        
    Returns:
        User information if authorized
    """
    user_org_id = current_user.get("organization_id")
    custom_claims = current_user.get("custom_claims", {})
    
    # Check if user belongs to the organization
    if user_org_id == organization_id:
        return current_user
    
    # Check if user has admin access to multiple organizations
    if custom_claims.get("super_admin", False):
        return current_user
    
    # Check if user has specific organization access
    org_access = custom_claims.get("organization_access", [])
    if organization_id in org_access:
        return current_user
    
    # Log unauthorized organization access attempt
    compliance_auditor.log_event(
        event_type=AuditEventType.SECURITY_INCIDENT,
        action="unauthorized_organization_access",
        outcome="blocked",
        user_id=current_user.get("user_id"),
        details={
            "requested_organization": organization_id,
            "user_organization": user_org_id
        },
        risk_level="high"
    )
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Access denied to this organization"
    )


def _get_client_ip(request: Request) -> str:
    """Get client IP address from request"""
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    return request.client.host if request.client else "unknown"


# Role-based access dependencies
require_admin = require_roles(["admin", "super_admin"])
require_user = require_roles(["user", "admin", "super_admin"])
require_support = require_roles(["support", "admin", "super_admin"])