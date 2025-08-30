"""
Security audit logging and compliance monitoring
"""

import json
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)


class AuditEventType(str, Enum):
    """Types of audit events"""
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    DATA_DELETION = "data_deletion"
    CONSENT_GIVEN = "consent_given"
    CONSENT_WITHDRAWN = "consent_withdrawn"
    PRIVACY_REQUEST = "privacy_request"
    SECURITY_INCIDENT = "security_incident"
    ADMIN_ACTION = "admin_action"
    API_ACCESS = "api_access"
    CROSS_BORDER_TRANSFER = "cross_border_transfer"


class AuditEvent(BaseModel):
    """Audit event record"""
    event_id: str
    event_type: AuditEventType
    timestamp: datetime
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    resource: Optional[str] = None
    action: str
    outcome: str  # success, failure, partial
    details: Dict[str, Any] = {}
    risk_level: str = "low"  # low, medium, high, critical


class ComplianceAuditor:
    """Security and compliance audit system"""
    
    def __init__(self):
        self.events: list[AuditEvent] = []
    
    def log_event(
        self,
        event_type: AuditEventType,
        action: str,
        outcome: str = "success",
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        resource: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        risk_level: str = "low"
    ) -> str:
        """Log an audit event"""
        event_id = f"AUDIT-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{len(self.events)}"
        
        event = AuditEvent(
            event_id=event_id,
            event_type=event_type,
            timestamp=datetime.utcnow(),
            user_id=user_id,
            session_id=session_id,
            ip_address=ip_address,
            user_agent=user_agent,
            resource=resource,
            action=action,
            outcome=outcome,
            details=details or {},
            risk_level=risk_level
        )
        
        self.events.append(event)
        
        # Log to structured logging
        log_data = {
            "audit_event": event.dict(),
            "compliance": True
        }
        
        if risk_level in ["high", "critical"]:
            logger.warning(f"High-risk audit event: {event_id} - {action}")
        else:
            logger.info(f"Audit event: {event_id} - {action}")
        
        return event_id
    
    def log_privacy_event(
        self,
        action: str,
        user_id: str,
        details: Dict[str, Any],
        ip_address: Optional[str] = None
    ) -> str:
        """Log privacy-related events for APP compliance"""
        return self.log_event(
            event_type=AuditEventType.PRIVACY_REQUEST,
            action=action,
            user_id=user_id,
            ip_address=ip_address,
            details=details,
            risk_level="medium"
        )
    
    def log_data_access(
        self,
        user_id: str,
        resource: str,
        action: str,
        outcome: str = "success",
        sensitive_data: bool = False,
        ip_address: Optional[str] = None
    ) -> str:
        """Log data access events"""
        risk_level = "high" if sensitive_data else "low"
        
        return self.log_event(
            event_type=AuditEventType.DATA_ACCESS,
            action=action,
            outcome=outcome,
            user_id=user_id,
            resource=resource,
            ip_address=ip_address,
            details={"sensitive_data": sensitive_data},
            risk_level=risk_level
        )


# Global auditor instance
compliance_auditor = ComplianceAuditor()