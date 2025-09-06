"""
Email Processing Background Tasks
Handles periodic email checking and processing
"""

import logging
import asyncio
from datetime import datetime, timedelta
from typing import List
from sqlalchemy.orm import Session

from ..utils.database import get_db
from ..services.email_service import email_service
from ..models.user import Organization

logger = logging.getLogger(__name__)


class EmailProcessor:
    """
    Background email processor that periodically checks for new emails
    and processes them for organizations with email integration enabled
    """
    
    def __init__(self):
        self.is_running = False
        self.check_interval = 300  # 5 minutes
        self.max_emails_per_batch = 50
    
    async def start(self):
        """Start the email processing loop"""
        if self.is_running:
            logger.warning("Email processor is already running")
            return
        
        self.is_running = True
        logger.info("Starting email processor")
        
        while self.is_running:
            try:
                await self._process_all_organizations()
                await asyncio.sleep(self.check_interval)
                
            except Exception as e:
                logger.error(f"Email processor error: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying
    
    async def stop(self):
        """Stop the email processing loop"""
        logger.info("Stopping email processor")
        self.is_running = False
    
    async def _process_all_organizations(self):
        """Process emails for all organizations with email integration enabled"""
        try:
            db = next(get_db())
            
            # Get organizations with email integration enabled
            organizations = db.query(Organization).filter(
                Organization.email_settings.op('->>')('enabled') == 'true'
            ).all()
            
            logger.info(f"Processing emails for {len(organizations)} organizations")
            
            for org in organizations:
                try:
                    await self._process_organization_emails(db, str(org.id))
                    
                except Exception as e:
                    logger.error(f"Failed to process emails for organization {org.id}: {e}")
            
        except Exception as e:
            logger.error(f"Failed to process organizations: {e}")
        finally:
            db.close()
    
    async def _process_organization_emails(self, db: Session, organization_id: str):
        """Process emails for a specific organization"""
        try:
            result = await email_service.process_incoming_emails(
                db=db,
                organization_id=organization_id,
                limit=self.max_emails_per_batch
            )
            
            if result["processed"] > 0:
                logger.info(f"Processed {result['processed']} emails for organization {organization_id}")
            
            if result["errors"] > 0:
                logger.warning(f"Failed to process {result['errors']} emails for organization {organization_id}")
                
        except Exception as e:
            logger.error(f"Email processing failed for organization {organization_id}: {e}")


class EmailScheduler:
    """
    Scheduler for email-related background tasks
    """
    
    def __init__(self):
        self.processor = EmailProcessor()
        self.cleanup_task = None
        self.processor_task = None
    
    async def start_all_tasks(self):
        """Start all email background tasks"""
        logger.info("Starting email scheduler tasks")
        
        # Start email processor
        self.processor_task = asyncio.create_task(self.processor.start())
        
        # Start cleanup task
        self.cleanup_task = asyncio.create_task(self._cleanup_old_threads())
    
    async def stop_all_tasks(self):
        """Stop all email background tasks"""
        logger.info("Stopping email scheduler tasks")
        
        # Stop processor
        if self.processor_task:
            await self.processor.stop()
            self.processor_task.cancel()
        
        # Stop cleanup task
        if self.cleanup_task:
            self.cleanup_task.cancel()
    
    async def _cleanup_old_threads(self):
        """Cleanup old email threads periodically"""
        while True:
            try:
                await self._perform_cleanup()
                await asyncio.sleep(86400)  # Run daily
                
            except Exception as e:
                logger.error(f"Email cleanup error: {e}")
                await asyncio.sleep(3600)  # Wait 1 hour before retrying
    
    async def _perform_cleanup(self):
        """Perform cleanup of old email threads"""
        try:
            db = next(get_db())
            
            # Delete threads older than 1 year that are closed
            cutoff_date = datetime.utcnow() - timedelta(days=365)
            
            from ..models.user import EmailThread
            
            deleted_count = db.query(EmailThread).filter(
                EmailThread.status == "closed",
                EmailThread.created_at < cutoff_date
            ).delete()
            
            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} old email threads")
                db.commit()
            
        except Exception as e:
            logger.error(f"Email cleanup failed: {e}")
            db.rollback()
        finally:
            db.close()


# Global scheduler instance
email_scheduler = EmailScheduler()


# Utility functions for manual processing
async def process_organization_emails_now(organization_id: str, limit: int = 50) -> dict:
    """Process emails for an organization immediately"""
    try:
        db = next(get_db())
        
        result = await email_service.process_incoming_emails(
            db=db,
            organization_id=organization_id,
            limit=limit
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Manual email processing failed: {e}")
        raise
    finally:
        db.close()


async def send_test_email(organization_id: str, test_email: str) -> dict:
    """Send a test email to verify email integration"""
    try:
        db = next(get_db())
        
        # Get organization
        org = db.query(Organization).filter(Organization.id == organization_id).first()
        if not org or not org.email_settings or not org.email_settings.get("enabled"):
            raise Exception("Email integration not enabled")
        
        # Create a test email response
        result = await email_service.send_email_response(
            db=db,
            organization_id=organization_id,
            thread_id="test_thread",
            response_content=f"""
This is a test email from ANZx.ai email integration.

If you received this email, your email integration is working correctly.

Test details:
- Organization ID: {organization_id}
- Test time: {datetime.utcnow().isoformat()}
- Email address: {org.email_settings.get('email_address')}

Best regards,
ANZx.ai System
            """,
            is_ai_generated=False
        )
        
        return {"success": True, "message": "Test email sent successfully"}
        
    except Exception as e:
        logger.error(f"Test email failed: {e}")
        raise
    finally:
        db.close()