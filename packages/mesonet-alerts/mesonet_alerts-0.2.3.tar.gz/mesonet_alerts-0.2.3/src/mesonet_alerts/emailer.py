"""
Email alerting functionality for mesonet services.

Provides EmailAlerter class for sending multipart HTML+text emails with SMTP support.
Includes future hooks for provider/severity-based routing.
"""

import os
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional, Dict, Any
import jinja2

from .config import EmailConfig, load_email_config
from .config_repo import ConfigRepository, EmailConfig as DBEmailConfig
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
        recipients: Optional[list[str]] = None,
        config_repo: Optional[ConfigRepository] = None
    ):
        """
        Initialize the email alerter.
        
        Args:
            config: Email configuration. If None, loads from environment or DB
            recipients: Override recipient list. If None, uses config recipients
            config_repo: ConfigRepository for loading from DynamoDB. If provided, takes precedence
        """
        # Try to load from DynamoDB first, then fallback to environment
        if config_repo:
            db_config = config_repo.get_email_config()
            if db_config:
                # Convert DB config to legacy config format
                # Get fallback values from environment for missing fields
                alerts_table_name = os.getenv("ALERTS_TABLE_NAME")
                expected_records = int(os.getenv("EXPECTED_RECORDS_PER_PROVIDER_PER_HOUR", "100"))
                
                self.config = EmailConfig(
                    smtp_host=db_config.smtp.host,
                    smtp_port=db_config.smtp.port,
                    smtp_user=db_config.smtp.user,
                    smtp_password=db_config.smtp.password,
                    from_address=db_config.smtp.from_address,
                    to_addresses=db_config.recipients,
                    alerts_table_name=alerts_table_name,
                    expected_records_per_provider_per_hour=expected_records
                )
                self.db_templates = db_config.templates
                self.using_db_config = True
                logger.info("Loaded email configuration from DynamoDB")
            else:
                logger.warning("Failed to load config from DynamoDB, falling back to environment")
                self.config = config or load_email_config()
                self.db_templates = {}
                self.using_db_config = False
        else:
            self.config = config or load_email_config()
            self.db_templates = {}
            self.using_db_config = False
            
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
            # Render templates - use DB templates if available, otherwise fallback to built-in
            if self.using_db_config and template in self.db_templates:
                # Use Jinja2 to render DB templates
                html_template = jinja2.Template(self.db_templates[template]['html'])
                text_template = jinja2.Template(self.db_templates[template]['text'])
                html_content = html_template.render(**context)
                text_content = text_template.render(**context)
                logger.debug(f"Rendered email using DB template: {template}")
            else:
                # Fallback to built-in templates
                html_content = render_html(template, context)
                text_content = render_text(template, context)
                logger.debug(f"Rendered email using built-in template: {template}")
            
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
            with smtplib.SMTP_SSL(self.config.smtp_host, self.config.smtp_port) as server:
                if self.config.smtp_user and self.config.smtp_password:
                    server.login(self.config.smtp_user, self.config.smtp_password)
                    logger.debug("SMTP SSL authentication successful")
                else:
                    logger.debug("Using SMTP SSL without authentication (local dev mode)")
                
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