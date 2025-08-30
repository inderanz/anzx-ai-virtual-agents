"""
Australian Privacy Principles (APP) Compliance Framework
Implements privacy controls and consent management for Australian Privacy Act 1988
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)


class ConsentType(str, Enum):
    """Types of consent under Australian Privacy Principles"""
    COLLECTION = "collection"           # APP 3 - Collection of solicited personal information
    USE_DISCLOSURE = "use_disclosure"   # APP 6 - Use or disclosure of personal information
    DIRECT_MARKETING = "direct_marketing"  # APP 7 - Direct marketing
    CROSS_BORDER = "cross_border"       # APP 8 - Cross-border disclosure
    GOVERNMENT_ID = "government_id"     # APP 9 - Adoption, use or disclosure of government related identifiers


class ConsentStatus(str, Enum):
    """Consent status values"""
    GIVEN = "given"
    WITHDRAWN = "withdrawn"
    EXPIRED = "expired"
    PENDING = "pending"


class PersonalInformationType(str, Enum):
    """Types of personal information under APP"""
    BASIC = "basic"                     # Name, contact details
    SENSITIVE = "sensitive"             # Health, biometric, genetic, etc.
    GOVERNMENT_ID = "government_id"     # Driver's license, passport, etc.
    FINANCIAL = "financial"             # Credit card, bank details
    BIOMETRIC = "biometric"             # Fingerprints, facial recognition
    HEALTH = "health"                   # Medical records, health status


class ConsentRecord(BaseModel):
    """Individual consent record"""
    user_id: str
    consent_type: ConsentType
    status: ConsentStatus
    purpose: str
    information_types: List[PersonalInformationType]
    granted_at: Optional[datetime] = None
    withdrawn_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    evidence: Dict[str, Any] = Field(default_factory=dict)


class PrivacyNotice(BaseModel):
    """Privacy notice content for APP 5 compliance"""
    organization_name: str = "ANZx.ai Pty Ltd"
    contact_email: str = "privacy@anzx.ai"
    contact_phone: str = "+61 2 8000 0000"
    contact_address: str = "Level 1, 123 Collins Street, Melbourne VIC 3000"
    
    collection_purposes: List[str] = Field(default_factory=lambda: [
        "Provide AI assistant services",
        "Process customer support requests",
        "Improve service quality and features",
        "Comply with legal obligations",
        "Prevent fraud and security threats"
    ])
    
    information_types: List[PersonalInformationType] = Field(default_factory=lambda: [
        PersonalInformationType.BASIC,
        PersonalInformationType.FINANCIAL
    ])
    
    disclosure_recipients: List[str] = Field(default_factory=lambda: [
        "Cloud service providers (Google Cloud Platform)",
        "Payment processors (Stripe)",
        "Analytics providers",
        "Legal and regulatory authorities when required"
    ])
    
    overseas_disclosures: List[str] = Field(default_factory=lambda: [
        "United States (Google Cloud Platform, Stripe)",
        "European Union (Analytics providers)"
    ])
    
    retention_period: str = "7 years or as required by law"
    access_correction_process: str = "Contact privacy@anzx.ai to request access or correction"


class APPCompliance:
    """Australian Privacy Principles compliance manager"""
    
    def __init__(self):
        self.privacy_notice = PrivacyNotice()
        self.consent_records: Dict[str, List[ConsentRecord]] = {}
    
    def collect_consent(
        self,
        user_id: str,
        consent_type: ConsentType,
        purpose: str,
        information_types: List[PersonalInformationType],
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        evidence: Optional[Dict[str, Any]] = None
    ) -> ConsentRecord:
        """
        Collect consent from user (APP 3, 6, 7, 8)
        
        Args:
            user_id: Unique user identifier
            consent_type: Type of consent being collected
            purpose: Specific purpose for collection/use
            information_types: Types of personal information
            ip_address: User's IP address for evidence
            user_agent: User's browser/device info
            evidence: Additional evidence of consent
        
        Returns:
            ConsentRecord: The created consent record
        """
        consent = ConsentRecord(
            user_id=user_id,
            consent_type=consent_type,
            status=ConsentStatus.GIVEN,
            purpose=purpose,
            information_types=information_types,
            granted_at=datetime.utcnow(),
            ip_address=ip_address,
            user_agent=user_agent,
            evidence=evidence or {}
        )
        
        # Set expiry for certain consent types
        if consent_type == ConsentType.DIRECT_MARKETING:
            consent.expires_at = datetime.utcnow() + timedelta(days=365)
        
        # Store consent record
        if user_id not in self.consent_records:
            self.consent_records[user_id] = []
        self.consent_records[user_id].append(consent)
        
        logger.info(f"Consent collected for user {user_id}: {consent_type} - {purpose}")
        return consent
    
    def withdraw_consent(
        self,
        user_id: str,
        consent_type: ConsentType,
        purpose: Optional[str] = None
    ) -> bool:
        """
        Withdraw consent (APP 2.1 - Right to withdraw)
        
        Args:
            user_id: User identifier
            consent_type: Type of consent to withdraw
            purpose: Specific purpose (optional)
        
        Returns:
            bool: True if consent was withdrawn
        """
        if user_id not in self.consent_records:
            return False
        
        withdrawn = False
        for consent in self.consent_records[user_id]:
            if (consent.consent_type == consent_type and 
                consent.status == ConsentStatus.GIVEN and
                (purpose is None or consent.purpose == purpose)):
                
                consent.status = ConsentStatus.WITHDRAWN
                consent.withdrawn_at = datetime.utcnow()
                withdrawn = True
                
                logger.info(f"Consent withdrawn for user {user_id}: {consent_type}")
        
        return withdrawn
    
    def check_consent(
        self,
        user_id: str,
        consent_type: ConsentType,
        purpose: Optional[str] = None
    ) -> bool:
        """
        Check if valid consent exists
        
        Args:
            user_id: User identifier
            consent_type: Type of consent to check
            purpose: Specific purpose (optional)
        
        Returns:
            bool: True if valid consent exists
        """
        if user_id not in self.consent_records:
            return False
        
        now = datetime.utcnow()
        
        for consent in self.consent_records[user_id]:
            if (consent.consent_type == consent_type and
                consent.status == ConsentStatus.GIVEN and
                (purpose is None or consent.purpose == purpose) and
                (consent.expires_at is None or consent.expires_at > now)):
                return True
        
        return False
    
    def get_user_consents(self, user_id: str) -> List[ConsentRecord]:
        """Get all consent records for a user"""
        return self.consent_records.get(user_id, [])
    
    def generate_privacy_notice(self) -> Dict[str, Any]:
        """Generate privacy notice for APP 5 compliance"""
        return {
            "organization": {
                "name": self.privacy_notice.organization_name,
                "contact": {
                    "email": self.privacy_notice.contact_email,
                    "phone": self.privacy_notice.contact_phone,
                    "address": self.privacy_notice.contact_address
                }
            },
            "collection": {
                "purposes": self.privacy_notice.collection_purposes,
                "information_types": [t.value for t in self.privacy_notice.information_types],
                "legal_basis": "Consent and legitimate business interests"
            },
            "use_disclosure": {
                "recipients": self.privacy_notice.disclosure_recipients,
                "overseas_disclosures": self.privacy_notice.overseas_disclosures,
                "safeguards": "Contractual protections and adequacy decisions"
            },
            "rights": {
                "access": "You can request access to your personal information",
                "correction": "You can request correction of inaccurate information",
                "complaint": "You can lodge a complaint with the Office of the Australian Information Commissioner",
                "withdrawal": "You can withdraw consent at any time"
            },
            "retention": self.privacy_notice.retention_period,
            "contact_process": self.privacy_notice.access_correction_process,
            "last_updated": datetime.utcnow().isoformat()
        }
    
    def validate_cross_border_disclosure(
        self,
        user_id: str,
        destination_country: str,
        recipient: str,
        purpose: str
    ) -> bool:
        """
        Validate cross-border disclosure under APP 8
        
        Args:
            user_id: User identifier
            destination_country: Country where data will be sent
            recipient: Organization receiving the data
            purpose: Purpose of the disclosure
        
        Returns:
            bool: True if disclosure is permitted
        """
        # Check if user has given consent for cross-border disclosure
        if not self.check_consent(user_id, ConsentType.CROSS_BORDER):
            logger.warning(f"Cross-border disclosure blocked - no consent: {user_id} -> {destination_country}")
            return False
        
        # Check if destination country has adequate protection
        adequate_countries = [
            "New Zealand", "European Union", "United Kingdom", 
            "Canada", "Switzerland", "Argentina", "Uruguay"
        ]
        
        if destination_country not in adequate_countries:
            # Additional safeguards required
            logger.info(f"Cross-border disclosure to non-adequate country: {destination_country}")
            # In practice, would check for binding corporate rules, standard contractual clauses, etc.
        
        logger.info(f"Cross-border disclosure approved: {user_id} -> {destination_country} ({recipient})")
        return True
    
    def log_access_request(
        self,
        user_id: str,
        request_type: str,
        details: Dict[str, Any]
    ) -> None:
        """Log access/correction requests for APP 12 compliance"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "request_type": request_type,
            "details": details,
            "status": "received"
        }
        
        logger.info(f"Privacy request logged: {request_type} for user {user_id}")
        # In practice, would store in database for tracking and response


# Global compliance instance
app_compliance = APPCompliance()