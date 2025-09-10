"""
Email alerting functionality for mesonet services.

Provides EmailAlerter class for sending multipart HTML+text emails with SMTP support.
Includes future hooks for provider/severity-based routing.
"""

import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional, Dict, Any

from .config import EmailConfig, load_email_config
from .templates import render_html, render_text

logger = logging.getLogger(__name__)


class EmailAlerter:
    """
    Production-ready email alerting service with SMTP support.
    
    Handles multipart email composition and delivery with configurable SMTP settings.
    Provides hooks for future provider/severity-based recipient routing.
    """
    
    def __init__(
        self, 
        config: Optional[EmailConfig] = None, 
        recipients: Optional[list[str]] = None
    ):
        """
        Initialize the email alerter.
        
        Args:
            config: Email configuration. If None, loads from environment
            recipients: Override recipient list. If None, uses config recipients
        """
        self.config = config or load_email_config()
        self.recipients = recipients or self.config.to_addresses
        
        logger.info(
            f"EmailAlerter initialized with SMTP {self.config.smtp_host}:{self.config.smtp_port}, "
            f"{len(self.recipients)} recipients"
        )
    
    def send(
        self, 
        template: str, 
        subject: str, 
        context: Dict[str, Any], 
        recipients: Optional[list[str]] = None
    ) -> None:
        """
        Send alert email using specified template.
        
        Args:
            template: Template name (e.g., 'process_failure')
            subject: Email subject line
            context: Template variables dictionary
            recipients: Override recipients for this email
            
        Raises:
            Exception: If email sending fails
        """
        target_recipients = recipients or self.recipients
        
        if not target_recipients:
            logger.warning("No recipients configured, skipping email")
            return
        
        try:
            # Render templates
            html_content = render_html(template, context)
            text_content = render_text(template, context)
            
            # Create multipart message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.config.from_address
            msg['To'] = ', '.join(target_recipients)
            
            # Attach both text and HTML parts
            text_part = MIMEText(text_content, 'plain', 'utf-8')
            html_part = MIMEText(html_content, 'html', 'utf-8')
            
            msg.attach(text_part)
            msg.attach(html_part)
            
            # Send email
            self._send_message(msg, target_recipients)
            
            logger.info(
                f"Alert email sent successfully",
                extra={
                    "template": template,
                    "subject": subject,
                    "recipients": len(target_recipients),
                    "provider": context.get("provider"),
                    "severity": context.get("severity"),
                    # TODO: Add OpenTelemetry span context here
                    # "trace_id": context.get("trace_id"),
                    # "span_id": get_current_span().get_span_context().span_id
                }
            )
            
            # TODO: Add Prometheus metrics here
            # email_alerts_sent_total.labels(
            #     template=template,
            #     severity=context.get("severity", "unknown")
            # ).inc()
            
        except Exception as e:
            logger.error(
                f"Failed to send alert email: {e}",
                extra={
                    "template": template,
                    "subject": subject,
                    "error": str(e),
                    "provider": context.get("provider"),
                    "severity": context.get("severity"),
                }
            )
            raise
    
    def _send_message(self, msg: MIMEMultipart, recipients: list[str]) -> None:
        """
        Send the composed email message via SMTP.
        
        Args:
            msg: Composed multipart message
            recipients: List of recipient email addresses
        """
        try:
            with smtplib.SMTP(self.config.smtp_host, self.config.smtp_port) as server:
                # Use STARTTLS if credentials are provided
                if self.config.smtp_user and self.config.smtp_password:
                    server.starttls()
                    server.login(self.config.smtp_user, self.config.smtp_password)
                    logger.debug("SMTP authentication successful")
                else:
                    logger.debug("Using SMTP without authentication (local dev mode)")
                
                # Send message
                server.send_message(msg, to_addrs=recipients)
                
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error: {e}")
            raise
        except Exception as e:
            logger.error(f"Email sending error: {e}")
            raise
    
    def resolve_recipients(self, provider: str, severity: str) -> list[str]:
        """
        Resolve recipients based on provider and severity (future enhancement).
        
        This method provides a hook for sophisticated recipient routing based on:
        - Provider-specific contacts
        - Severity-based escalation rules
        - On-call schedules
        - Team assignments
        
        Args:
            provider: Provider name (e.g., "colorado", "iowa")
            severity: Alert severity (e.g., "ERROR", "WARN", "INFO")
            
        Returns:
            list[str]: Resolved recipient email addresses
        """
        # TODO: Implement provider/severity-based routing
        # This would typically involve:
        # 1. Query RecipientRoutingRepo.get_recipients(provider, severity)
        # 2. Apply business rules (e.g., escalate ERROR to on-call)
        # 3. Merge with default recipients based on configuration
        # 4. Handle special cases (e.g., provider-specific contacts)
        #
        # Example implementation:
        # routing_rules = RecipientRoutingRepo.get_recipients(provider, severity)
        # if severity == "ERROR":
        #     routing_rules.extend(OnCallService.get_current_oncall())
        # if provider in CRITICAL_PROVIDERS:
        #     routing_rules.extend(CRITICAL_PROVIDER_CONTACTS)
        # return list(set(routing_rules + self.recipients))  # dedupe
        
        logger.debug(f"Using consolidated recipients for {provider}/{severity}")
        return self.recipients 