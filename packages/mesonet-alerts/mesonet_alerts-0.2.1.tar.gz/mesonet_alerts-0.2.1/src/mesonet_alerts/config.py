"""
Configuration management for mesonet alerts.

Handles environment variables and provides future hooks for database-backed configuration.
"""

import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv
load_dotenv()


@dataclass
class EmailConfig:
    """Email configuration with SMTP settings and recipients."""
    
    smtp_host: str
    smtp_port: int
    smtp_user: str
    smtp_password: str
    from_address: str
    to_addresses: list[str]
    alerts_table_name: Optional[str]
    expected_records_per_provider_per_hour: int


def load_email_config() -> EmailConfig:
    """
    Load email configuration from environment variables.
    
    Environment variables:
        ALERTS_SMTP_HOST: SMTP server hostname (default: localhost)
        ALERTS_SMTP_PORT: SMTP server port (default: 1025)
        ALERTS_SMTP_USER: SMTP username (default: empty)
        ALERTS_SMTP_PASS: SMTP password (default: empty)
        ALERTS_FROM: From email address (default: alerts@local.test)
        ALERTS_TO: Comma-separated recipient addresses (default: admin@local.test,kevin@local.test)
        ALERTS_TABLE_NAME: DynamoDB table for alert persistence (optional)
        EXPECTED_RECORDS_PER_PROVIDER_PER_HOUR: Expected records threshold (default: 100)
    
    Returns:
        EmailConfig: Configuration object with all settings
    """
    # Parse comma-separated recipients
    to_addresses_str = os.getenv("ALERTS_TO", "admin@local.test,kevin@local.test")
    to_addresses = [addr.strip() for addr in to_addresses_str.split(",") if addr.strip()]
    
    return EmailConfig(
        smtp_host=os.getenv("ALERTS_SMTP_HOST", "localhost"),
        smtp_port=int(os.getenv("ALERTS_SMTP_PORT", "1025")),
        smtp_user=os.getenv("ALERTS_SMTP_USER", ""),
        smtp_password=os.getenv("ALERTS_SMTP_PASS", ""),
        from_address=os.getenv("ALERTS_FROM", "alerts@local.test"),
        to_addresses=to_addresses,
        alerts_table_name=os.getenv("ALERTS_TABLE_NAME"),
        expected_records_per_provider_per_hour=int(
            os.getenv("EXPECTED_RECORDS_PER_PROVIDER_PER_HOUR", "100")
        ),
    )


# TODO: Future database-backed configuration
# class EmailConfigRepo:
#     """Repository for fetching email configuration from database."""
#     
#     @staticmethod
#     def get_active_config() -> EmailConfig:
#         """
#         Fetch active email configuration from database.
#         
#         This would retrieve SMTP credentials, template overrides,
#         and recipient lists from a centralized configuration table.
#         
#         Returns:
#             EmailConfig: Active configuration from database
#         """
#         pass
#
#
# class RecipientRoutingRepo:
#     """Repository for provider/severity-based recipient routing."""
#     
#     @staticmethod
#     def get_recipients(provider: str, severity: str) -> list[str]:
#         """
#         Get recipients based on provider and severity level.
#         
#         This would implement sophisticated routing rules like:
#         - Critical errors go to on-call team
#         - Provider-specific alerts go to data team + provider contacts
#         - Volume drops go to operations team
#         
#         Args:
#             provider: Provider name (e.g., "colorado", "iowa")
#             severity: Alert severity (e.g., "ERROR", "WARN", "INFO")
#             
#         Returns:
#             list[str]: Email addresses for this provider/severity combination
#         """
#         pass 