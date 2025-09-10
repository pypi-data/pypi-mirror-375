"""
Unit tests for EmailAlerter class.

Tests email composition, SMTP operations, and error handling with mocked dependencies.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from email.mime.multipart import MIMEMultipart

from mesonet_alerts.emailer import EmailAlerter
from mesonet_alerts.config import EmailConfig


class TestEmailAlerter(unittest.TestCase):
    """Test cases for EmailAlerter class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = EmailConfig(
            smtp_host="localhost",
            smtp_port=1025,
            smtp_user="",
            smtp_password="",
            from_address="alerts@test.com",
            to_addresses=["admin@test.com", "ops@test.com"],
            alerts_table_name=None,
            expected_records_per_provider_per_hour=100
        )
        
        self.context = {
            "stage": "ingest",
            "severity": "ERROR",
            "provider": "test_provider",
            "run_id": "test_run_123",
            "trace_id": "trace_456",
            "error": "Test error message",
            "attempts": 3,
            "timestamp_iso": "2025-01-15T10:30:00Z"
        }
    
    @patch('mesonet_alerts.emailer.smtplib.SMTP')
    def test_send_email_success(self, mock_smtp_class):
        """Test successful email sending."""
        # Setup mock
        mock_server = Mock()
        mock_smtp_class.return_value.__enter__.return_value = mock_server
        
        # Create emailer and send
        emailer = EmailAlerter(config=self.config)
        emailer.send("process_failure", "Test Alert", self.context)
        
        # Verify SMTP operations
        mock_smtp_class.assert_called_once_with("localhost", 1025)
        mock_server.send_message.assert_called_once()
        
        # Verify message structure
        call_args = mock_server.send_message.call_args
        msg = call_args[0][0]  # First positional argument
        
        self.assertIsInstance(msg, MIMEMultipart)
        self.assertEqual(msg['From'], "alerts@test.com")
        self.assertEqual(msg['To'], "admin@test.com, ops@test.com")
        self.assertEqual(msg['Subject'], "Test Alert")
        
        # Verify multipart structure (text + html)
        parts = msg.get_payload()
        self.assertEqual(len(parts), 2)
        self.assertEqual(parts[0].get_content_type(), 'text/plain')
        self.assertEqual(parts[1].get_content_type(), 'text/html')
    
    @patch('mesonet_alerts.emailer.smtplib.SMTP')
    def test_send_email_with_auth(self, mock_smtp_class):
        """Test email sending with SMTP authentication."""
        # Setup config with auth
        auth_config = EmailConfig(
            smtp_host="smtp.gmail.com",
            smtp_port=587,
            smtp_user="test@gmail.com",
            smtp_password="password123",
            from_address="alerts@test.com",
            to_addresses=["admin@test.com"],
            alerts_table_name=None,
            expected_records_per_provider_per_hour=100
        )
        
        # Setup mock
        mock_server = Mock()
        mock_smtp_class.return_value.__enter__.return_value = mock_server
        
        # Create emailer and send
        emailer = EmailAlerter(config=auth_config)
        emailer.send("process_failure", "Test Alert", self.context)
        
        # Verify SMTP authentication
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with("test@gmail.com", "password123")
        mock_server.send_message.assert_called_once()
    
    @patch('mesonet_alerts.emailer.smtplib.SMTP')
    def test_send_email_no_recipients(self, mock_smtp_class):
        """Test email sending with no recipients configured."""
        # Setup config with no recipients
        no_recipients_config = EmailConfig(
            smtp_host="localhost",
            smtp_port=1025,
            smtp_user="",
            smtp_password="",
            from_address="alerts@test.com",
            to_addresses=[],
            alerts_table_name=None,
            expected_records_per_provider_per_hour=100
        )
        
        emailer = EmailAlerter(config=no_recipients_config)
        
        # Should not attempt to send email
        with patch('mesonet_alerts.emailer.logger') as mock_logger:
            emailer.send("process_failure", "Test Alert", self.context)
            mock_logger.warning.assert_called_once_with("No recipients configured, skipping email")
        
        # SMTP should not be called
        mock_smtp_class.assert_not_called()
    
    @patch('mesonet_alerts.emailer.smtplib.SMTP')
    def test_send_email_smtp_error(self, mock_smtp_class):
        """Test email sending with SMTP error."""
        # Setup mock to raise exception
        mock_smtp_class.return_value.__enter__.side_effect = Exception("SMTP connection failed")
        
        emailer = EmailAlerter(config=self.config)
        
        # Should raise exception
        with self.assertRaises(Exception) as cm:
            emailer.send("process_failure", "Test Alert", self.context)
        
        self.assertEqual(str(cm.exception), "SMTP connection failed")
    
    def test_recipient_override(self):
        """Test overriding recipients for a specific email."""
        with patch('mesonet_alerts.emailer.smtplib.SMTP') as mock_smtp_class:
            mock_server = Mock()
            mock_smtp_class.return_value.__enter__.return_value = mock_server
            
            emailer = EmailAlerter(config=self.config)
            override_recipients = ["emergency@test.com"]
            
            emailer.send("process_failure", "Test Alert", self.context, recipients=override_recipients)
            
            # Verify overridden recipients
            call_args = mock_server.send_message.call_args
            msg = call_args[0][0]
            to_addrs = call_args[1]['to_addrs']
            
            self.assertEqual(msg['To'], "emergency@test.com")
            self.assertEqual(to_addrs, ["emergency@test.com"])
    
    @patch('mesonet_alerts.emailer.render_html')
    @patch('mesonet_alerts.emailer.render_text')
    def test_template_rendering(self, mock_render_text, mock_render_html):
        """Test that templates are rendered with correct context."""
        mock_render_html.return_value = "<html>Test HTML</html>"
        mock_render_text.return_value = "Test Text"
        
        with patch('mesonet_alerts.emailer.smtplib.SMTP') as mock_smtp_class:
            mock_server = Mock()
            mock_smtp_class.return_value.__enter__.return_value = mock_server
            
            emailer = EmailAlerter(config=self.config)
            emailer.send("process_failure", "Test Alert", self.context)
            
            # Verify template rendering calls
            mock_render_html.assert_called_once_with("process_failure", self.context)
            mock_render_text.assert_called_once_with("process_failure", self.context)
    
    def test_resolve_recipients_default(self):
        """Test default recipient resolution."""
        emailer = EmailAlerter(config=self.config)
        recipients = emailer.resolve_recipients("test_provider", "ERROR")
        
        self.assertEqual(recipients, self.config.to_addresses)
    
    def test_initialization_with_recipient_override(self):
        """Test EmailAlerter initialization with recipient override."""
        override_recipients = ["override@test.com"]
        emailer = EmailAlerter(config=self.config, recipients=override_recipients)
        
        self.assertEqual(emailer.recipients, override_recipients)
    
    @patch('mesonet_alerts.emailer.load_email_config')
    def test_initialization_without_config(self, mock_load_config):
        """Test EmailAlerter initialization without explicit config."""
        mock_load_config.return_value = self.config
        
        emailer = EmailAlerter()
        
        mock_load_config.assert_called_once()
        self.assertEqual(emailer.config, self.config)


if __name__ == '__main__':
    unittest.main() 