"""
Data Breach Notification System
Implements Notifiable Data Breaches (NDB) scheme compliance for Australian Privacy Act 1988
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
import logging
import asyncio
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class BreachSeverity(str, Enum):
    """Breach severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class BreachType(str, Enum):
    """Types of data breaches"""
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    UNAUTHORIZED_DISCLOSURE = "unauthorized_disclosure"
    LOSS_OF_DATA = "loss_of_data"
    THEFT = "theft"
    SYSTEM_COMPROMISE = "system_compromise"
    HUMAN_ERROR = "human_error"
    MALICIOUS_ATTACK = "malicious_attack"


class NotificationStatus(str, Enum):
    """Notification status"""
    PENDING = "pending"
    SENT = "sent"
    ACKNOWLEDGED = "acknowledged"
    FAILED = "failed"


class AffectedDataType(str, Enum):
    """Types of affected personal information"""
    CONTACT_INFO = "contact_info"
    FINANCIAL_INFO = "financial_info"
    IDENTITY_INFO = "identity_info"
    HEALTH_INFO = "health_info"
    BIOMETRIC_INFO = "biometric_info"
    SENSITIVE_INFO = "sensitive_info"
    GOVERNMENT_ID = "government_id"


@dataclass
class BreachAssessment:
    """Assessment of whether breach is notifiable under NDB scheme"""
    is_notifiable: bool
    reasoning: str
    likely_to_cause_serious_harm: bool
    risk_factors: List[str]
    mitigation_factors: List[str]


class DataBreach(BaseModel):
    """Data breach record"""
    breach_id: str
    title: str
    description: str
    breach_type: BreachType
    severity: BreachSeverity
    discovered_at: datetime
    occurred_at: Optional[datetime] = None
    contained_at: Optional[datetime] = None
    
    # Affected data
    affected_individuals_count: int = 0
    affected_data_types: List[AffectedDataType] = Field(default_factory=list)
    data_volume_estimate: Optional[str] = None
    
    # Assessment
    assessment: Optional[BreachAssessment] = None
    
    # Response actions
    containment_actions: List[str] = Field(default_factory=list)
    remediation_actions: List[str] = Field(default_factory=list)
    
    # Notifications
    oaic_notification_required: bool = False
    oaic_notification_sent: bool = False
    oaic_notification_sent_at: Optional[datetime] = None
    
    individual_notification_required: bool = False
    individual_notifications_sent: int = 0
    individual_notification_method: Optional[str] = None
    
    # Investigation
    investigation_status: str = "ongoing"
    investigation_findings: List[str] = Field(default_factory=list)
    
    # Metadata
    reported_by: str
    assigned_to: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class BreachNotificationSystem:
    """Notifiable Data Breaches (NDB) scheme compliance system"""
    
    def __init__(self):
        self.breaches: Dict[str, DataBreach] = {}
        self.notification_templates = self._load_notification_templates()
    
    def report_breach(
        self,
        title: str,
        description: str,
        breach_type: BreachType,
        severity: BreachSeverity,
        reported_by: str,
        occurred_at: Optional[datetime] = None,
        affected_individuals_count: int = 0,
        affected_data_types: Optional[List[AffectedDataType]] = None
    ) -> str:
        """
        Report a potential data breach
        
        Args:
            title: Brief title of the breach
            description: Detailed description
            breach_type: Type of breach
            severity: Severity level
            reported_by: Person reporting the breach
            occurred_at: When the breach occurred (if known)
            affected_individuals_count: Number of affected individuals
            affected_data_types: Types of personal information affected
        
        Returns:
            str: Breach ID
        """
        breach_id = f"BREACH-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
        
        breach = DataBreach(
            breach_id=breach_id,
            title=title,
            description=description,
            breach_type=breach_type,
            severity=severity,
            discovered_at=datetime.utcnow(),
            occurred_at=occurred_at,
            affected_individuals_count=affected_individuals_count,
            affected_data_types=affected_data_types or [],
            reported_by=reported_by
        )
        
        self.breaches[breach_id] = breach
        
        # Immediate assessment
        assessment = self._assess_breach_notifiability(breach)
        breach.assessment = assessment
        
        # Auto-assign based on severity
        if severity in [BreachSeverity.HIGH, BreachSeverity.CRITICAL]:
            breach.assigned_to = "privacy-officer@anzx.ai"
        
        logger.critical(f"Data breach reported: {breach_id} - {title} (Severity: {severity})")
        
        # Trigger immediate response for critical breaches
        if severity == BreachSeverity.CRITICAL:
            asyncio.create_task(self._immediate_response(breach_id))
        
        return breach_id
    
    def _assess_breach_notifiability(self, breach: DataBreach) -> BreachAssessment:
        """
        Assess whether breach is notifiable under NDB scheme
        
        A breach is notifiable if it is likely to result in serious harm to affected individuals
        """
        risk_factors = []
        mitigation_factors = []
        
        # Risk factors that increase likelihood of serious harm
        if AffectedDataType.FINANCIAL_INFO in breach.affected_data_types:
            risk_factors.append("Financial information exposed (risk of financial fraud)")
        
        if AffectedDataType.IDENTITY_INFO in breach.affected_data_types:
            risk_factors.append("Identity information exposed (risk of identity theft)")
        
        if AffectedDataType.HEALTH_INFO in breach.affected_data_types:
            risk_factors.append("Health information exposed (risk of discrimination)")
        
        if AffectedDataType.SENSITIVE_INFO in breach.affected_data_types:
            risk_factors.append("Sensitive information exposed (risk of discrimination/harassment)")
        
        if breach.affected_individuals_count > 100:
            risk_factors.append("Large number of individuals affected")
        
        if breach.breach_type in [BreachType.MALICIOUS_ATTACK, BreachType.THEFT]:
            risk_factors.append("Malicious intent involved")
        
        # Mitigation factors that reduce likelihood of serious harm
        if breach.contained_at and (breach.contained_at - breach.discovered_at).total_seconds() < 3600:
            mitigation_factors.append("Breach contained within 1 hour of discovery")
        
        if breach.breach_type == BreachType.HUMAN_ERROR:
            mitigation_factors.append("Internal error with no malicious intent")
        
        if not any(dt in [AffectedDataType.FINANCIAL_INFO, AffectedDataType.IDENTITY_INFO, 
                         AffectedDataType.HEALTH_INFO, AffectedDataType.SENSITIVE_INFO] 
                  for dt in breach.affected_data_types):
            mitigation_factors.append("Only basic contact information affected")
        
        # Determine if likely to cause serious harm
        risk_score = len(risk_factors) * 2 - len(mitigation_factors)
        likely_serious_harm = risk_score > 2 or breach.severity in [BreachSeverity.HIGH, BreachSeverity.CRITICAL]
        
        reasoning = f"Risk factors: {', '.join(risk_factors) if risk_factors else 'None'}. " \
                   f"Mitigation factors: {', '.join(mitigation_factors) if mitigation_factors else 'None'}. " \
                   f"Risk score: {risk_score}"
        
        return BreachAssessment(
            is_notifiable=likely_serious_harm,
            reasoning=reasoning,
            likely_to_cause_serious_harm=likely_serious_harm,
            risk_factors=risk_factors,
            mitigation_factors=mitigation_factors
        )
    
    async def _immediate_response(self, breach_id: str) -> None:
        """Immediate response actions for critical breaches"""
        breach = self.breaches[breach_id]
        
        # 1. Contain the breach
        await self._contain_breach(breach_id)
        
        # 2. Notify privacy officer immediately
        await self._notify_privacy_officer(breach_id)
        
        # 3. Start 72-hour notification clock if notifiable
        if breach.assessment and breach.assessment.is_notifiable:
            await self._start_notification_timer(breach_id)
    
    async def _contain_breach(self, breach_id: str) -> None:
        """Implement breach containment measures"""
        breach = self.breaches[breach_id]
        
        containment_actions = [
            "Isolated affected systems",
            "Disabled compromised accounts",
            "Implemented additional access controls",
            "Preserved forensic evidence"
        ]
        
        breach.containment_actions.extend(containment_actions)
        breach.contained_at = datetime.utcnow()
        
        logger.info(f"Breach {breach_id} contained with actions: {containment_actions}")
    
    async def _notify_privacy_officer(self, breach_id: str) -> None:
        """Notify privacy officer of critical breach"""
        breach = self.breaches[breach_id]
        
        # In practice, would send email/SMS/Slack notification
        logger.critical(f"URGENT: Privacy officer notification for breach {breach_id}")
        
        # Log notification
        breach.investigation_findings.append(f"Privacy officer notified at {datetime.utcnow()}")
    
    async def _start_notification_timer(self, breach_id: str) -> None:
        """Start 72-hour notification timer for OAIC"""
        breach = self.breaches[breach_id]
        
        # Schedule OAIC notification reminder
        notification_deadline = datetime.utcnow() + timedelta(hours=72)
        
        logger.warning(f"OAIC notification required for breach {breach_id} by {notification_deadline}")
        
        # In practice, would schedule automated reminders
        breach.oaic_notification_required = True
    
    def notify_oaic(
        self,
        breach_id: str,
        contact_person: str,
        contact_email: str,
        contact_phone: str
    ) -> bool:
        """
        Submit notification to Office of the Australian Information Commissioner
        
        Args:
            breach_id: Breach identifier
            contact_person: Contact person for follow-up
            contact_email: Contact email
            contact_phone: Contact phone
        
        Returns:
            bool: True if notification was sent successfully
        """
        if breach_id not in self.breaches:
            return False
        
        breach = self.breaches[breach_id]
        
        if not breach.assessment or not breach.assessment.is_notifiable:
            logger.warning(f"Attempted OAIC notification for non-notifiable breach: {breach_id}")
            return False
        
        # Check 72-hour deadline
        hours_since_discovery = (datetime.utcnow() - breach.discovered_at).total_seconds() / 3600
        if hours_since_discovery > 72:
            logger.error(f"OAIC notification for breach {breach_id} is overdue by {hours_since_discovery - 72:.1f} hours")
        
        # Prepare notification data
        notification_data = {
            "breach_id": breach_id,
            "organization": "ANZx.ai Pty Ltd",
            "contact_person": contact_person,
            "contact_email": contact_email,
            "contact_phone": contact_phone,
            "breach_description": breach.description,
            "breach_type": breach.breach_type.value,
            "occurred_at": breach.occurred_at.isoformat() if breach.occurred_at else "Unknown",
            "discovered_at": breach.discovered_at.isoformat(),
            "affected_individuals": breach.affected_individuals_count,
            "affected_data_types": [dt.value for dt in breach.affected_data_types],
            "containment_actions": breach.containment_actions,
            "remediation_actions": breach.remediation_actions,
            "assessment": breach.assessment.reasoning if breach.assessment else ""
        }
        
        # In practice, would submit via OAIC online form or API
        logger.info(f"OAIC notification submitted for breach {breach_id}")
        
        breach.oaic_notification_sent = True
        breach.oaic_notification_sent_at = datetime.utcnow()
        
        return True
    
    def notify_individuals(
        self,
        breach_id: str,
        notification_method: str = "email",
        custom_message: Optional[str] = None
    ) -> int:
        """
        Notify affected individuals about the breach
        
        Args:
            breach_id: Breach identifier
            notification_method: Method of notification (email, letter, phone)
            custom_message: Custom message to include
        
        Returns:
            int: Number of individuals notified
        """
        if breach_id not in self.breaches:
            return 0
        
        breach = self.breaches[breach_id]
        
        if not breach.individual_notification_required:
            logger.info(f"Individual notification not required for breach {breach_id}")
            return 0
        
        # Use template based on breach type and severity
        template = self.notification_templates.get(
            f"{breach.breach_type.value}_{breach.severity.value}",
            self.notification_templates["default"]
        )
        
        # In practice, would send actual notifications to affected individuals
        notifications_sent = breach.affected_individuals_count
        
        breach.individual_notifications_sent = notifications_sent
        breach.individual_notification_method = notification_method
        
        logger.info(f"Individual notifications sent for breach {breach_id}: {notifications_sent} via {notification_method}")
        
        return notifications_sent
    
    def update_breach(
        self,
        breach_id: str,
        **updates
    ) -> bool:
        """Update breach record with new information"""
        if breach_id not in self.breaches:
            return False
        
        breach = self.breaches[breach_id]
        
        for key, value in updates.items():
            if hasattr(breach, key):
                setattr(breach, key, value)
        
        breach.updated_at = datetime.utcnow()
        
        # Re-assess if key details changed
        if any(key in ['affected_individuals_count', 'affected_data_types', 'breach_type'] 
               for key in updates.keys()):
            breach.assessment = self._assess_breach_notifiability(breach)
        
        return True
    
    def get_breach(self, breach_id: str) -> Optional[DataBreach]:
        """Get breach record by ID"""
        return self.breaches.get(breach_id)
    
    def list_breaches(
        self,
        status_filter: Optional[str] = None,
        severity_filter: Optional[BreachSeverity] = None
    ) -> List[DataBreach]:
        """List breaches with optional filters"""
        breaches = list(self.breaches.values())
        
        if status_filter:
            breaches = [b for b in breaches if b.investigation_status == status_filter]
        
        if severity_filter:
            breaches = [b for b in breaches if b.severity == severity_filter]
        
        return sorted(breaches, key=lambda b: b.discovered_at, reverse=True)
    
    def _load_notification_templates(self) -> Dict[str, str]:
        """Load notification templates for different breach types"""
        return {
            "default": """
Dear [NAME],

We are writing to inform you of a data security incident that may have affected your personal information.

What happened: [BREACH_DESCRIPTION]

What information was involved: [AFFECTED_DATA_TYPES]

What we are doing: [CONTAINMENT_ACTIONS]

What you can do: [RECOMMENDED_ACTIONS]

For more information, please contact our Privacy Officer at privacy@anzx.ai or +61 2 8000 0000.

We sincerely apologize for this incident and any inconvenience it may cause.

ANZx.ai Privacy Team
            """,
            
            "unauthorized_access_high": """
URGENT: Security Incident Notification

Dear [NAME],

We are writing to inform you of a serious security incident that has affected your personal information stored in our systems.

[DETAILED_BREACH_DESCRIPTION]

Immediate actions you should take:
1. Monitor your financial accounts for unusual activity
2. Consider placing a fraud alert on your credit file
3. Change passwords for any accounts that may use similar information

We have taken immediate steps to secure our systems and are working with cybersecurity experts and law enforcement.

For support and more information, please contact our dedicated incident response line at +61 2 8000 0001.

ANZx.ai Security Team
            """
        }


# Global breach notification system
breach_notification_system = BreachNotificationSystem()