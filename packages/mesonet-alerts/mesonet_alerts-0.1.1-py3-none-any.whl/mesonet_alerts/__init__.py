"""
Mesonet Alerts Package

A shared email alerting package for mesonet microservices providing:
- HTML + plaintext email templates with Jinja2
- SMTP configuration with ENV fallbacks
- DynamoDB alert persistence (optional)
- Retry helpers for provider operations
- Volume drop detection and alerting
"""

from .emailer import EmailAlerter
from .store import AlertStore
from .retry import run_with_retries, ProviderEmptyDataError

__version__ = "0.1.1"
__all__ = [
    "EmailAlerter",
    "AlertStore",
    "run_with_retries",
    "ProviderEmptyDataError",
] 