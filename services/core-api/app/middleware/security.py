"""
Security middleware for FastAPI
Implements security headers, rate limiting, and compliance logging
"""

import time
from typing import Dict, Optional
from fastapi import Request, Response, HTTPException
from fastapi.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import logging

from ..compliance.audit import compliance_auditor, AuditEventType
from ..compliance.privacy import app_compliance

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # HSTS header for HTTPS
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # CSP header
        csp_policy = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' https://fonts.gstatic.com; "
            "connect-src 'self' wss: https:; "
            "frame-ancestors 'none'"
        )
        response.headers["Content-Security-Policy"] = csp_policy
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware"""
    
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, list] = {}
    
    async def dispatch(self, request: Request, call_next):
        client_ip = self._get_client_ip(request)
        current_time = time.time()
        
        # Clean old requests
        if client_ip in self.requests:
            self.requests[client_ip] = [
                req_time for req_time in self.requests[client_ip]
                if current_time - req_time < 60
            ]
        else:
            self.requests[client_ip] = []
        
        # Check rate limit
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            # Log rate limit violation
            compliance_auditor.log_event(
                event_type=AuditEventType.SECURITY_INCIDENT,
                action="rate_limit_exceeded",
                outcome="blocked",
                ip_address=client_ip,
                details={"requests_count": len(self.requests[client_ip])},
                risk_level="medium"
            )
            
            return JSONResponse(
                status_code=429,
                content={"error": "Rate limit exceeded", "retry_after": 60}
            )
        
        # Add current request
        self.requests[client_ip].append(current_time)
        
        return await call_next(request)
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address from request"""
        # Check for forwarded headers (from load balancer)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"


class ComplianceLoggingMiddleware(BaseHTTPMiddleware):
    """Log API requests for compliance and audit purposes"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get("User-Agent", "")
        
        # Get user ID from JWT token if available
        user_id = None
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            # In practice, would decode JWT to get user ID
            user_id = "extracted_from_jwt"
        
        try:
            response = await call_next(request)
            outcome = "success" if response.status_code < 400 else "failure"
            
            # Log API access
            compliance_auditor.log_event(
                event_type=AuditEventType.API_ACCESS,
                action=f"{request.method} {request.url.path}",
                outcome=outcome,
                user_id=user_id,
                ip_address=client_ip,
                user_agent=user_agent,
                details={
                    "status_code": response.status_code,
                    "response_time_ms": round((time.time() - start_time) * 1000, 2),
                    "query_params": dict(request.query_params),
                    "path_params": request.path_params
                },
                risk_level="low"
            )
            
            return response
            
        except Exception as e:
            # Log failed requests
            compliance_auditor.log_event(
                event_type=AuditEventType.API_ACCESS,
                action=f"{request.method} {request.url.path}",
                outcome="error",
                user_id=user_id,
                ip_address=client_ip,
                user_agent=user_agent,
                details={
                    "error": str(e),
                    "response_time_ms": round((time.time() - start_time) * 1000, 2)
                },
                risk_level="high"
            )
            raise
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address from request"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"


class PrivacyComplianceMiddleware(BaseHTTPMiddleware):
    """Ensure privacy compliance for data processing requests"""
    
    async def dispatch(self, request: Request, call_next):
        # Check for data processing endpoints
        if self._is_data_processing_endpoint(request):
            user_id = self._extract_user_id(request)
            
            if user_id:
                # Check consent for data processing
                if not app_compliance.check_consent(user_id, "collection"):
                    return JSONResponse(
                        status_code=403,
                        content={
                            "error": "Consent required",
                            "message": "Valid consent is required for data processing",
                            "consent_url": "/api/v1/consent"
                        }
                    )
        
        return await call_next(request)
    
    def _is_data_processing_endpoint(self, request: Request) -> bool:
        """Check if endpoint processes personal data"""
        data_processing_paths = [
            "/api/v1/users",
            "/api/v1/conversations",
            "/api/v1/documents",
            "/api/v1/analytics"
        ]
        
        return any(request.url.path.startswith(path) for path in data_processing_paths)
    
    def _extract_user_id(self, request: Request) -> Optional[str]:
        """Extract user ID from request"""
        # In practice, would decode JWT token
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            return "user_id_from_jwt"
        return None