"""
Email Integration Tests
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from sqlalchemy.orm import Session

from app.services.email_service import EmailService
from app.models.user import Organization, EmailThread, Conversation, Message, Assistant
from app.config.email_config import EMAIL_PROVIDERS


class TestEmailService:
    """Test email service functionality"""
    
    @pytest.fixture
    def email_service(self):
        return EmailService()
    
    @pytest.fixture
    def mock_db(self):
        return Mock(spec=Session)
    
    @pytest.fixture
    def sample_organization(self):
        org = Mock(spec=Organization)
        org.id = "test-org-id"
        org.email_settings = {
            "enabled": True,
            "email_address": "support@test.com",
            "display_name": "Test Support",
            "auto_reply": True,
            "signature": "Best regards,\nTest Team",
            "escalation_email": "escalation@test.com",
            "config": {
                "provider": "gmail",
                "username": "support@test.com",
                "password": "test-password",
                "imap_server": "imap.gmail.com",
                "imap_port": 993,
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587
            }
        }
        return org
    
    @pytest.fixture
    def sample_email_config(self):
        return {
            "provider": "gmail",
            "email_address": "support@test.com",
            "username": "support@test.com",
            "password": "test-password",
            "display_name": "Test Support",
            "auto_reply": True,
            "signature": "Best regards,\nTest Team",
            "escalation_email": "escalation@test.com"
        }
    
    @pytest.mark.asyncio
    async def test_setup_email_integration_success(self, email_service, mock_db, sample_email_config):
        """Test successful email integration setup"""
        # Mock organization
        org = Mock(spec=Organization)
        org.id = "test-org-id"
        mock_db.query.return_value.filter.return_value.first.return_value = org
        
        # Mock email connection test
        with patch.object(email_service, '_test_email_connection') as mock_test:
            mock_test.return_value = {"success": True}
            
            with patch.object(email_service, '_encrypt_email_config') as mock_encrypt:
                mock_encrypt.return_value = sample_email_config
                
                result = await email_service.setup_email_integration(
                    db=mock_db,
                    organization_id="test-org-id",
                    email_config=sample_email_config
                )
                
                assert result["success"] is True
                assert result["email_address"] == "support@test.com"
                assert "features_enabled" in result
                mock_db.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_setup_email_integration_connection_failure(self, email_service, mock_db, sample_email_config):
        """Test email integration setup with connection failure"""
        # Mock organization
        org = Mock(spec=Organization)
        mock_db.query.return_value.filter.return_value.first.return_value = org
        
        # Mock failed connection test
        with patch.object(email_service, '_test_email_connection') as mock_test:
            mock_test.return_value = {"success": False, "error": "Authentication failed"}
            
            with pytest.raises(Exception) as exc_info:
                await email_service.setup_email_integration(
                    db=mock_db,
                    organization_id="test-org-id",
                    email_config=sample_email_config
                )
            
            assert "Email connection failed" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_process_incoming_emails(self, email_service, mock_db, sample_organization):
        """Test processing incoming emails"""
        mock_db.query.return_value.filter.return_value.first.return_value = sample_organization
        
        # Mock IMAP connection and email data
        mock_imap = Mock()
        mock_imap.select.return_value = None
        mock_imap.search.return_value = ('OK', [b'1 2 3'])
        
        with patch.object(email_service, '_get_imap_connection') as mock_get_imap:
            mock_get_imap.return_value = mock_imap
            
            with patch.object(email_service, '_process_single_email') as mock_process:
                mock_process.return_value = None
                
                result = await email_service.process_incoming_emails(
                    db=mock_db,
                    organization_id="test-org-id",
                    limit=50
                )
                
                assert result["processed"] == 3
                assert result["errors"] == 0
                assert result["total_found"] == 3
                assert mock_process.call_count == 3
    
    @pytest.mark.asyncio
    async def test_send_email_response(self, email_service, mock_db, sample_organization):
        """Test sending email response"""
        # Mock email thread
        thread = Mock(spec=EmailThread)
        thread.id = "test-thread-id"
        thread.customer_email = "customer@test.com"
        thread.subject = "Test Subject"
        thread.last_message_id = "msg-123"
        thread.message_references = "ref-123"
        thread.conversation_id = "conv-123"
        
        mock_db.query.return_value.filter.return_value.first.side_effect = [thread, sample_organization]
        
        # Mock SMTP connection
        mock_smtp = Mock()
        
        with patch.object(email_service, '_get_smtp_connection') as mock_get_smtp:
            mock_get_smtp.return_value = mock_smtp
            
            with patch('app.middleware.usage_tracking.usage_tracker.track_email_response') as mock_track:
                mock_track.return_value = None
                
                result = await email_service.send_email_response(
                    db=mock_db,
                    organization_id="test-org-id",
                    thread_id="test-thread-id",
                    response_content="Thank you for your message.",
                    is_ai_generated=True
                )
                
                assert result["success"] is True
                assert result["thread_id"] == "test-thread-id"
                mock_smtp.send_message.assert_called_once()
                mock_db.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_escalate_email_thread(self, email_service, mock_db, sample_organization):
        """Test email thread escalation"""
        # Mock email thread
        thread = Mock(spec=EmailThread)
        thread.id = "test-thread-id"
        thread.customer_email = "customer@test.com"
        thread.subject = "Test Subject"
        
        mock_db.query.return_value.filter.return_value.first.side_effect = [thread, sample_organization]
        
        with patch.object(email_service, '_send_escalation_notification') as mock_notify:
            mock_notify.return_value = None
            
            result = await email_service.escalate_email_thread(
                db=mock_db,
                organization_id="test-org-id",
                thread_id="test-thread-id",
                escalation_reason="Customer requires human assistance"
            )
            
            assert result["success"] is True
            assert result["thread_id"] == "test-thread-id"
            assert result["escalated_to"] == "escalation@test.com"
            assert thread.status == "escalated"
            mock_notify.assert_called_once()
            mock_db.commit.assert_called_once()
    
    def test_extract_email_details(self, email_service):
        """Test email detail extraction"""
        # Mock email message
        email_msg = Mock()
        email_msg.__getitem__ = Mock(side_effect=lambda key: {
            "Subject": "Test Subject",
            "From": "Test User <test@example.com>",
            "Message-ID": "<msg123@example.com>",
            "References": "<ref1@example.com> <ref2@example.com>",
            "In-Reply-To": "<reply@example.com>",
            "Date": "Mon, 1 Jan 2024 12:00:00 +0000"
        }.get(key, ""))
        email_msg.get = Mock(side_effect=lambda key, default="": {
            "Subject": "Test Subject",
            "From": "Test User <test@example.com>",
            "Message-ID": "<msg123@example.com>",
            "References": "<ref1@example.com> <ref2@example.com>",
            "In-Reply-To": "<reply@example.com>",
            "Date": "Mon, 1 Jan 2024 12:00:00 +0000"
        }.get(key, default))
        
        with patch.object(email_service, '_extract_email_body') as mock_body:
            mock_body.return_value = "Test email body"
            
            details = email_service._extract_email_details(email_msg)
            
            assert details["subject"] == "Test Subject"
            assert details["from_name"] == "Test User"
            assert details["from_email"] == "test@example.com"
            assert details["message_id"] == "<msg123@example.com>"
            assert details["body"] == "Test email body"
    
    def test_extract_email_body_plain_text(self, email_service):
        """Test extracting plain text email body"""
        # Mock email message
        email_msg = Mock()
        email_msg.is_multipart.return_value = False
        email_msg.get_payload.return_value = b"Test email content"
        
        body = email_service._extract_email_body(email_msg)
        
        assert body == "Test email content"
    
    def test_extract_email_body_multipart(self, email_service):
        """Test extracting body from multipart email"""
        # Mock email parts
        text_part = Mock()
        text_part.get_content_type.return_value = "text/plain"
        text_part.get_payload.return_value = b"Test email content"
        
        html_part = Mock()
        html_part.get_content_type.return_value = "text/html"
        
        email_msg = Mock()
        email_msg.is_multipart.return_value = True
        email_msg.walk.return_value = [email_msg, text_part, html_part]
        
        body = email_service._extract_email_body(email_msg)
        
        assert body == "Test email content"
    
    @pytest.mark.asyncio
    async def test_find_or_create_thread_existing(self, email_service, mock_db):
        """Test finding existing email thread"""
        # Mock existing thread
        existing_thread = Mock(spec=EmailThread)
        existing_thread.id = "existing-thread"
        
        mock_db.query.return_value.filter.return_value.first.return_value = existing_thread
        
        email_details = {
            "subject": "Re: Test Subject",
            "from_email": "customer@test.com",
            "from_name": "Test Customer",
            "message_id": "<new-msg@example.com>",
            "references": "<ref1@example.com>",
            "in_reply_to": "<reply@example.com>"
        }
        
        thread = await email_service._find_or_create_thread(
            db=mock_db,
            email_details=email_details,
            organization_id="test-org-id"
        )
        
        assert thread == existing_thread
        assert "<new-msg@example.com>" in thread.message_references
    
    @pytest.mark.asyncio
    async def test_find_or_create_thread_new(self, email_service, mock_db):
        """Test creating new email thread"""
        # No existing thread found
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        email_details = {
            "subject": "New Test Subject",
            "from_email": "customer@test.com",
            "from_name": "Test Customer",
            "message_id": "<new-msg@example.com>",
            "references": "",
            "in_reply_to": ""
        }
        
        with patch.object(email_service, '_generate_thread_id') as mock_gen_id:
            mock_gen_id.return_value = "new-thread-id"
            
            thread = await email_service._find_or_create_thread(
                db=mock_db,
                email_details=email_details,
                organization_id="test-org-id"
            )
            
            mock_db.add.assert_called_once()
            # Verify thread properties would be set correctly
            assert mock_gen_id.called
    
    def test_generate_thread_id(self, email_service):
        """Test thread ID generation"""
        email_details = {
            "from_email": "test@example.com",
            "subject": "Test Subject"
        }
        
        thread_id = email_service._generate_thread_id(email_details)
        
        assert thread_id.startswith("thread_")
        assert len(thread_id) == 19  # "thread_" + 12 char hash
    
    @pytest.mark.asyncio
    async def test_create_email_conversation(self, email_service, mock_db):
        """Test creating conversation for email thread"""
        # Mock thread
        thread = Mock(spec=EmailThread)
        thread.id = "test-thread"
        thread.subject = "Test Subject"
        thread.customer_email = "customer@test.com"
        thread.customer_name = "Test Customer"
        
        # Mock assistant
        assistant = Mock(spec=Assistant)
        assistant.id = "assistant-id"
        
        mock_db.query.return_value.filter.return_value.first.return_value = assistant
        
        # Mock conversation creation
        mock_conversation = Mock(spec=Conversation)
        mock_conversation.id = "conv-id"
        
        with patch('app.models.user.Conversation') as mock_conv_class:
            mock_conv_class.return_value = mock_conversation
            
            conversation = await email_service._create_email_conversation(
                db=mock_db,
                thread=thread,
                organization_id="test-org-id"
            )
            
            assert conversation == mock_conversation
            mock_db.add.assert_called_once_with(mock_conversation)
            mock_db.flush.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_test_email_connection_success(self, email_service):
        """Test successful email connection test"""
        email_config = {
            "imap_server": "imap.gmail.com",
            "imap_port": 993,
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "username": "test@gmail.com",
            "password": "test-password"
        }
        
        with patch('imaplib.IMAP4_SSL') as mock_imap:
            mock_imap_instance = Mock()
            mock_imap.return_value = mock_imap_instance
            
            with patch('smtplib.SMTP_SSL') as mock_smtp:
                mock_smtp_instance = Mock()
                mock_smtp.return_value = mock_smtp_instance
                
                result = await email_service._test_email_connection(email_config)
                
                assert result["success"] is True
                mock_imap_instance.login.assert_called_once()
                mock_imap_instance.logout.assert_called_once()
                mock_smtp_instance.login.assert_called_once()
                mock_smtp_instance.quit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_test_email_connection_failure(self, email_service):
        """Test failed email connection test"""
        email_config = {
            "imap_server": "imap.gmail.com",
            "imap_port": 993,
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "username": "test@gmail.com",
            "password": "wrong-password"
        }
        
        with patch('imaplib.IMAP4_SSL') as mock_imap:
            mock_imap.side_effect = Exception("Authentication failed")
            
            result = await email_service._test_email_connection(email_config)
            
            assert result["success"] is False
            assert "Authentication failed" in result["error"]


class TestEmailProviders:
    """Test email provider configurations"""
    
    def test_gmail_provider_config(self):
        """Test Gmail provider configuration"""
        gmail_config = EMAIL_PROVIDERS["gmail"]
        
        assert gmail_config["name"] == "Gmail"
        assert gmail_config["imap_server"] == "imap.gmail.com"
        assert gmail_config["imap_port"] == 993
        assert gmail_config["smtp_server"] == "smtp.gmail.com"
        assert gmail_config["smtp_port"] == 587
        assert gmail_config["requires_app_password"] is True
        assert gmail_config["oauth_supported"] is True
    
    def test_outlook_provider_config(self):
        """Test Outlook provider configuration"""
        outlook_config = EMAIL_PROVIDERS["outlook"]
        
        assert outlook_config["name"] == "Outlook/Office 365"
        assert outlook_config["imap_server"] == "outlook.office365.com"
        assert outlook_config["imap_port"] == 993
        assert outlook_config["smtp_server"] == "smtp.office365.com"
        assert outlook_config["smtp_port"] == 587
        assert outlook_config["requires_app_password"] is False
        assert outlook_config["oauth_supported"] is True
    
    def test_all_providers_have_required_fields(self):
        """Test that all providers have required configuration fields"""
        required_fields = ["name", "imap_server", "imap_port", "smtp_server", "smtp_port"]
        
        for provider_name, config in EMAIL_PROVIDERS.items():
            for field in required_fields:
                assert field in config, f"Provider {provider_name} missing field {field}"


if __name__ == "__main__":
    pytest.main([__file__])