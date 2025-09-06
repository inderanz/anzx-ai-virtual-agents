"""
Email Integration Service
Handles IMAP/Gmail integration for support email processing
"""

import logging
import email
import imaplib
import smtplib
import re
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.header import decode_header
from email.utils import parseaddr, formataddr
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from ..models.user import Organization, Assistant, Conversation, Message, EmailThread
from ..services.agent_service import agent_service
from ..middleware.usage_tracking import usage_tracker
from ..config.email_config import email_settings

logger = logging.getLogger(__name__)


class EmailService:
    """
    Service for handling email integration with IMAP/Gmail
    
    Features:
    - IMAP/Gmail mailbox monitoring
    - Email parsing and conversation threading
    - AI response generation
    - Email sending with proper formatting
    - Escalation and human handoff workflows
    """
    
    def __init__(self):
        self.agent_service = agent_service
        self.imap_connections = {}
        self.smtp_connections = {}
    
    async def setup_email_integration(
        self,
        db: Session,
        organization_id: str,
        email_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Set up email integration for an organization
        
        Args:
            db: Database session
            organization_id: Organization ID
            email_config: Email configuration
            
        Returns:
            Setup result
        """
        try:
            # Validate organization
            org = db.query(Organization).filter(Organization.id == organization_id).first()
            if not org:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Organization not found"
                )
            
            # Test email connection
            connection_test = await self._test_email_connection(email_config)
            if not connection_test["success"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Email connection failed: {connection_test['error']}"
                )
            
            # Store email configuration (encrypted)
            encrypted_config = self._encrypt_email_config(email_config)
            
            # Update organization with email settings
            org.email_settings = {
                "enabled": True,
                "email_address": email_config.get("email_address"),
                "display_name": email_config.get("display_name", "ANZx.ai Support"),
                "auto_reply": email_config.get("auto_reply", True),
                "signature": email_config.get("signature", ""),
                "escalation_email": email_config.get("escalation_email"),
                "business_hours": email_config.get("business_hours", {
                    "enabled": False,
                    "timezone": "Australia/Sydney",
                    "monday": {"start": "09:00", "end": "17:00"},
                    "tuesday": {"start": "09:00", "end": "17:00"},
                    "wednesday": {"start": "09:00", "end": "17:00"},
                    "thursday": {"start": "09:00", "end": "17:00"},
                    "friday": {"start": "09:00", "end": "17:00"},
                    "saturday": {"enabled": False},
                    "sunday": {"enabled": False}
                }),
                "config": encrypted_config
            }
            
            db.commit()
            
            logger.info(f"Email integration set up for organization {organization_id}")
            
            return {
                "success": True,
                "email_address": email_config.get("email_address"),
                "features_enabled": {
                    "auto_reply": email_config.get("auto_reply", True),
                    "conversation_threading": True,
                    "ai_responses": True,
                    "escalation": bool(email_config.get("escalation_email"))
                }
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to set up email integration: {e}")
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to set up email integration"
            )
    
    async def process_incoming_emails(
        self,
        db: Session,
        organization_id: str,
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        Process incoming emails from IMAP/Gmail
        
        Args:
            db: Database session
            organization_id: Organization ID
            limit: Maximum emails to process
            
        Returns:
            Processing results
        """
        try:
            # Get organization email settings
            org = db.query(Organization).filter(Organization.id == organization_id).first()
            if not org or not org.email_settings or not org.email_settings.get("enabled"):
                return {"processed": 0, "errors": 0, "message": "Email integration not enabled"}
            
            email_config = self._decrypt_email_config(org.email_settings["config"])
            
            # Connect to IMAP
            imap_conn = await self._get_imap_connection(organization_id, email_config)
            
            # Select inbox
            imap_conn.select('INBOX')
            
            # Search for unread emails
            status, messages = imap_conn.search(None, 'UNSEEN')
            if status != 'OK':
                raise Exception("Failed to search for emails")
            
            email_ids = messages[0].split()
            processed_count = 0
            error_count = 0
            
            # Process emails (limit to avoid overwhelming)
            for email_id in email_ids[:limit]:
                try:
                    await self._process_single_email(
                        db=db,
                        imap_conn=imap_conn,
                        email_id=email_id,
                        organization_id=organization_id,
                        email_config=email_config
                    )
                    processed_count += 1
                    
                except Exception as e:
                    logger.error(f"Failed to process email {email_id}: {e}")
                    error_count += 1
            
            return {
                "processed": processed_count,
                "errors": error_count,
                "total_found": len(email_ids)
            }
            
        except Exception as e:
            logger.error(f"Failed to process incoming emails: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to process incoming emails"
            )
    
    async def send_email_response(
        self,
        db: Session,
        organization_id: str,
        thread_id: str,
        response_content: str,
        is_ai_generated: bool = True
    ) -> Dict[str, Any]:
        """
        Send email response
        
        Args:
            db: Database session
            organization_id: Organization ID
            thread_id: Email thread ID
            response_content: Response content
            is_ai_generated: Whether response is AI generated
            
        Returns:
            Send result
        """
        try:
            # Get email thread
            thread = db.query(EmailThread).filter(
                EmailThread.id == thread_id,
                EmailThread.organization_id == organization_id
            ).first()
            
            if not thread:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Email thread not found"
                )
            
            # Get organization email settings
            org = db.query(Organization).filter(Organization.id == organization_id).first()
            email_config = self._decrypt_email_config(org.email_settings["config"])
            
            # Create email message
            msg = MIMEMultipart()
            msg['From'] = formataddr((
                org.email_settings.get("display_name", "ANZx.ai Support"),
                email_config["email_address"]
            ))
            msg['To'] = thread.customer_email
            msg['Subject'] = f"Re: {thread.subject}"
            msg['In-Reply-To'] = thread.last_message_id
            msg['References'] = thread.message_references
            
            # Add response content
            body = response_content
            
            # Add signature if configured
            signature = org.email_settings.get("signature")
            if signature:
                body += f"\n\n{signature}"
            
            # Add AI disclaimer if AI generated
            if is_ai_generated:
                body += "\n\n---\nThis response was generated by ANZx.ai Assistant. If you need further assistance, please reply to this email."
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            smtp_conn = await self._get_smtp_connection(organization_id, email_config)
            smtp_conn.send_message(msg)
            
            # Update thread
            thread.last_response_at = datetime.utcnow()
            thread.response_count += 1
            thread.status = "responded"
            
            # Create message record
            message = Message(
                conversation_id=thread.conversation_id,
                content=response_content,
                role="assistant",
                metadata={
                    "email_thread_id": thread_id,
                    "is_ai_generated": is_ai_generated,
                    "email_sent": True
                }
            )
            db.add(message)
            
            db.commit()
            
            # Track usage
            await usage_tracker.track_email_response(
                db=db,
                organization_id=organization_id,
                thread_id=thread_id,
                is_ai_generated=is_ai_generated
            )
            
            logger.info(f"Email response sent for thread {thread_id}")
            
            return {
                "success": True,
                "thread_id": thread_id,
                "message_id": str(message.id),
                "sent_at": datetime.utcnow().isoformat()
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to send email response: {e}")
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send email response"
            )
    
    async def escalate_email_thread(
        self,
        db: Session,
        organization_id: str,
        thread_id: str,
        escalation_reason: str
    ) -> Dict[str, Any]:
        """
        Escalate email thread to human agent
        
        Args:
            db: Database session
            organization_id: Organization ID
            thread_id: Email thread ID
            escalation_reason: Reason for escalation
            
        Returns:
            Escalation result
        """
        try:
            # Get email thread
            thread = db.query(EmailThread).filter(
                EmailThread.id == thread_id,
                EmailThread.organization_id == organization_id
            ).first()
            
            if not thread:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Email thread not found"
                )
            
            # Get organization settings
            org = db.query(Organization).filter(Organization.id == organization_id).first()
            escalation_email = org.email_settings.get("escalation_email")
            
            if not escalation_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No escalation email configured"
                )
            
            # Update thread status
            thread.status = "escalated"
            thread.escalated_at = datetime.utcnow()
            thread.escalation_reason = escalation_reason
            
            # Send escalation notification
            await self._send_escalation_notification(
                db=db,
                thread=thread,
                escalation_email=escalation_email,
                escalation_reason=escalation_reason,
                organization_id=organization_id
            )
            
            db.commit()
            
            logger.info(f"Email thread {thread_id} escalated to {escalation_email}")
            
            return {
                "success": True,
                "thread_id": thread_id,
                "escalated_to": escalation_email,
                "escalated_at": thread.escalated_at.isoformat()
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to escalate email thread: {e}")
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to escalate email thread"
            )
    
    async def get_email_threads(
        self,
        db: Session,
        organization_id: str,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get email threads for an organization"""
        try:
            query = db.query(EmailThread).filter(
                EmailThread.organization_id == organization_id
            )
            
            if status:
                query = query.filter(EmailThread.status == status)
            
            threads = query.order_by(EmailThread.created_at.desc()).offset(offset).limit(limit).all()
            
            result = []
            for thread in threads:
                # Get message count
                message_count = db.query(Message).filter(
                    Message.conversation_id == thread.conversation_id
                ).count()
                
                result.append({
                    "thread_id": str(thread.id),
                    "subject": thread.subject,
                    "customer_email": thread.customer_email,
                    "customer_name": thread.customer_name,
                    "status": thread.status,
                    "priority": thread.priority,
                    "message_count": message_count,
                    "response_count": thread.response_count,
                    "created_at": thread.created_at.isoformat(),
                    "last_message_at": thread.last_message_at.isoformat() if thread.last_message_at else None,
                    "last_response_at": thread.last_response_at.isoformat() if thread.last_response_at else None,
                    "escalated_at": thread.escalated_at.isoformat() if thread.escalated_at else None,
                    "escalation_reason": thread.escalation_reason
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to get email threads: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve email threads"
            )
    
    async def _process_single_email(
        self,
        db: Session,
        imap_conn: imaplib.IMAP4_SSL,
        email_id: bytes,
        organization_id: str,
        email_config: Dict[str, Any]
    ):
        """Process a single email"""
        try:
            # Fetch email
            status, msg_data = imap_conn.fetch(email_id, '(RFC822)')
            if status != 'OK':
                raise Exception("Failed to fetch email")
            
            # Parse email
            email_message = email.message_from_bytes(msg_data[0][1])
            
            # Extract email details
            email_details = self._extract_email_details(email_message)
            
            # Check if this is part of an existing thread
            thread = await self._find_or_create_thread(
                db=db,
                email_details=email_details,
                organization_id=organization_id
            )
            
            # Create conversation if needed
            if not thread.conversation_id:
                conversation = await self._create_email_conversation(
                    db=db,
                    thread=thread,
                    organization_id=organization_id
                )
                thread.conversation_id = conversation.id
            
            # Save incoming message
            message = Message(
                conversation_id=thread.conversation_id,
                content=email_details["body"],
                role="user",
                metadata={
                    "email_thread_id": str(thread.id),
                    "email_from": email_details["from_email"],
                    "email_subject": email_details["subject"],
                    "email_message_id": email_details["message_id"]
                }
            )
            db.add(message)
            
            # Update thread
            thread.last_message_at = datetime.utcnow()
            thread.last_message_id = email_details["message_id"]
            
            # Generate AI response if auto-reply is enabled
            org = db.query(Organization).filter(Organization.id == organization_id).first()
            if org.email_settings.get("auto_reply", True):
                await self._generate_ai_response(
                    db=db,
                    thread=thread,
                    incoming_message=email_details["body"],
                    organization_id=organization_id
                )
            
            # Mark email as read
            imap_conn.store(email_id, '+FLAGS', '\\Seen')
            
            db.commit()
            
        except Exception as e:
            logger.error(f"Failed to process email {email_id}: {e}")
            db.rollback()
            raise
    
    def _extract_email_details(self, email_message) -> Dict[str, Any]:
        """Extract details from email message"""
        try:
            # Get subject
            subject = ""
            if email_message["Subject"]:
                subject_parts = decode_header(email_message["Subject"])
                subject = "".join([
                    part.decode(encoding or 'utf-8') if isinstance(part, bytes) else part
                    for part, encoding in subject_parts
                ])
            
            # Get from address
            from_header = email_message.get("From", "")
            from_name, from_email = parseaddr(from_header)
            
            # Get message ID
            message_id = email_message.get("Message-ID", "")
            
            # Get references for threading
            references = email_message.get("References", "")
            in_reply_to = email_message.get("In-Reply-To", "")
            
            # Extract body
            body = self._extract_email_body(email_message)
            
            return {
                "subject": subject,
                "from_name": from_name,
                "from_email": from_email,
                "message_id": message_id,
                "references": references,
                "in_reply_to": in_reply_to,
                "body": body,
                "date": email_message.get("Date", "")
            }
            
        except Exception as e:
            logger.error(f"Failed to extract email details: {e}")
            return {
                "subject": "Unknown Subject",
                "from_name": "",
                "from_email": "unknown@example.com",
                "message_id": "",
                "references": "",
                "in_reply_to": "",
                "body": "Failed to parse email content",
                "date": ""
            }
    
    def _extract_email_body(self, email_message) -> str:
        """Extract plain text body from email"""
        try:
            if email_message.is_multipart():
                for part in email_message.walk():
                    if part.get_content_type() == "text/plain":
                        payload = part.get_payload(decode=True)
                        if payload:
                            return payload.decode('utf-8', errors='ignore')
            else:
                payload = email_message.get_payload(decode=True)
                if payload:
                    return payload.decode('utf-8', errors='ignore')
            
            return "No text content found"
            
        except Exception as e:
            logger.error(f"Failed to extract email body: {e}")
            return "Failed to extract email content"
    
    async def _find_or_create_thread(
        self,
        db: Session,
        email_details: Dict[str, Any],
        organization_id: str
    ) -> EmailThread:
        """Find existing thread or create new one"""
        try:
            # Try to find existing thread by references or subject
            thread = None
            
            # Check by message references
            if email_details["in_reply_to"]:
                thread = db.query(EmailThread).filter(
                    EmailThread.organization_id == organization_id,
                    EmailThread.message_references.contains(email_details["in_reply_to"])
                ).first()
            
            # Check by subject (remove Re: prefix)
            if not thread:
                clean_subject = re.sub(r'^(Re:|RE:|Fwd:|FWD:)\s*', '', email_details["subject"], flags=re.IGNORECASE)
                thread = db.query(EmailThread).filter(
                    EmailThread.organization_id == organization_id,
                    EmailThread.customer_email == email_details["from_email"],
                    EmailThread.subject.ilike(f"%{clean_subject}%")
                ).first()
            
            # Create new thread if not found
            if not thread:
                thread_id = self._generate_thread_id(email_details)
                
                thread = EmailThread(
                    id=thread_id,
                    organization_id=organization_id,
                    subject=email_details["subject"],
                    customer_email=email_details["from_email"],
                    customer_name=email_details["from_name"] or email_details["from_email"],
                    status="new",
                    priority="normal",
                    message_references=email_details["references"] + " " + email_details["message_id"],
                    last_message_id=email_details["message_id"]
                )
                db.add(thread)
            else:
                # Update existing thread
                thread.message_references += " " + email_details["message_id"]
                thread.status = "active"
            
            return thread
            
        except Exception as e:
            logger.error(f"Failed to find/create email thread: {e}")
            raise
    
    def _generate_thread_id(self, email_details: Dict[str, Any]) -> str:
        """Generate unique thread ID"""
        content = f"{email_details['from_email']}{email_details['subject']}{datetime.utcnow().isoformat()}"
        return "thread_" + hashlib.md5(content.encode()).hexdigest()[:12]
    
    async def _create_email_conversation(
        self,
        db: Session,
        thread: EmailThread,
        organization_id: str
    ) -> Conversation:
        """Create conversation for email thread"""
        try:
            # Get support assistant for the organization
            assistant = db.query(Assistant).filter(
                Assistant.organization_id == organization_id,
                Assistant.type == "support"
            ).first()
            
            if not assistant:
                raise Exception("No support assistant found for organization")
            
            conversation = Conversation(
                assistant_id=assistant.id,
                organization_id=organization_id,
                title=f"Email: {thread.subject}",
                status="active",
                metadata={
                    "email_thread_id": str(thread.id),
                    "customer_email": thread.customer_email,
                    "customer_name": thread.customer_name,
                    "channel": "email"
                }
            )
            
            db.add(conversation)
            db.flush()  # Get the ID
            
            return conversation
            
        except Exception as e:
            logger.error(f"Failed to create email conversation: {e}")
            raise
    
    async def _generate_ai_response(
        self,
        db: Session,
        thread: EmailThread,
        incoming_message: str,
        organization_id: str
    ):
        """Generate AI response for email"""
        try:
            # Get conversation
            conversation = db.query(Conversation).filter(
                Conversation.id == thread.conversation_id
            ).first()
            
            if not conversation:
                return
            
            # Generate AI response
            response_data = await self.agent_service.chat_with_agent(
                db=db,
                assistant_id=str(conversation.assistant_id),
                user_message=incoming_message,
                conversation_id=str(conversation.id),
                user_id=None  # Email customer
            )
            
            # Send email response
            await self.send_email_response(
                db=db,
                organization_id=organization_id,
                thread_id=str(thread.id),
                response_content=response_data["response"],
                is_ai_generated=True
            )
            
        except Exception as e:
            logger.error(f"Failed to generate AI response for email: {e}")
    
    async def _send_escalation_notification(
        self,
        db: Session,
        thread: EmailThread,
        escalation_email: str,
        escalation_reason: str,
        organization_id: str
    ):
        """Send escalation notification to human agent"""
        try:
            # Get organization email settings
            org = db.query(Organization).filter(Organization.id == organization_id).first()
            email_config = self._decrypt_email_config(org.email_settings["config"])
            
            # Create escalation email
            msg = MIMEMultipart()
            msg['From'] = formataddr((
                "ANZx.ai System",
                email_config["email_address"]
            ))
            msg['To'] = escalation_email
            msg['Subject'] = f"ESCALATION: {thread.subject}"
            
            body = f"""
Email thread has been escalated and requires human attention.

Thread Details:
- Subject: {thread.subject}
- Customer: {thread.customer_name} ({thread.customer_email})
- Created: {thread.created_at.strftime('%Y-%m-%d %H:%M:%S')}
- Messages: {thread.response_count + 1}
- Escalation Reason: {escalation_reason}

Please review and respond to this email thread in the ANZx.ai dashboard.

Thread ID: {thread.id}
Dashboard Link: https://app.anzx.ai/email-threads/{thread.id}
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send notification
            smtp_conn = await self._get_smtp_connection(organization_id, email_config)
            smtp_conn.send_message(msg)
            
        except Exception as e:
            logger.error(f"Failed to send escalation notification: {e}")
    
    async def _test_email_connection(self, email_config: Dict[str, Any]) -> Dict[str, Any]:
        """Test email connection"""
        try:
            # Test IMAP connection
            imap_conn = imaplib.IMAP4_SSL(
                email_config["imap_server"],
                email_config.get("imap_port", 993)
            )
            imap_conn.login(email_config["username"], email_config["password"])
            imap_conn.logout()
            
            # Test SMTP connection
            smtp_conn = smtplib.SMTP_SSL(
                email_config["smtp_server"],
                email_config.get("smtp_port", 465)
            )
            smtp_conn.login(email_config["username"], email_config["password"])
            smtp_conn.quit()
            
            return {"success": True}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _get_imap_connection(self, organization_id: str, email_config: Dict[str, Any]) -> imaplib.IMAP4_SSL:
        """Get or create IMAP connection"""
        if organization_id not in self.imap_connections:
            conn = imaplib.IMAP4_SSL(
                email_config["imap_server"],
                email_config.get("imap_port", 993)
            )
            conn.login(email_config["username"], email_config["password"])
            self.imap_connections[organization_id] = conn
        
        return self.imap_connections[organization_id]
    
    async def _get_smtp_connection(self, organization_id: str, email_config: Dict[str, Any]) -> smtplib.SMTP_SSL:
        """Get or create SMTP connection"""
        if organization_id not in self.smtp_connections:
            conn = smtplib.SMTP_SSL(
                email_config["smtp_server"],
                email_config.get("smtp_port", 465)
            )
            conn.login(email_config["username"], email_config["password"])
            self.smtp_connections[organization_id] = conn
        
        return self.smtp_connections[organization_id]
    
    def _encrypt_email_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Encrypt sensitive email configuration"""
        # In production, use proper encryption (e.g., Fernet)
        # For now, just return as-is (should be encrypted in real implementation)
        return config
    
    def _decrypt_email_config(self, encrypted_config: Dict[str, Any]) -> Dict[str, Any]:
        """Decrypt email configuration"""
        # In production, decrypt the configuration
        # For now, just return as-is
        return encrypted_config


# Global instance
email_service = EmailService()