"""
Volume drop detection and alerting for mesonet services.

Provides functionality to detect significant drops in data volume and trigger alerts.
Includes hooks for database-backed expected volume configuration.
"""

import logging
from datetime import datetime
from typing import Optional

from .config import load_email_config
from .emailer import EmailAlerter
from .store import AlertStore

logger = logging.getLogger(__name__)


def check_and_alert_volume_drop(
    *,
    provider: str,
    stage: str = "harmonize",
    actual_count: int,
    expected_count: Optional[int] = None,
    threshold: float = 0.20,
    window_start: datetime,
    window_end: datetime,
    emailer: EmailAlerter,
    store: Optional[AlertStore] = None
) -> None:
    """
    Check for volume drops and send alerts if threshold is exceeded.
    
    This function compares actual data volume against expected volume and triggers
    alerts when the drop exceeds the specified threshold percentage.
    
    Args:
        provider: Provider name (e.g., "colorado", "iowa")
        stage: Processing stage (default: "harmonize")
        actual_count: Actual number of records processed
        expected_count: Expected number of records. If None, uses ENV default
        threshold: Drop threshold as decimal (0.20 = 20% drop)
        window_start: Start of the time window being checked
        window_end: End of the time window being checked
        emailer: EmailAlerter instance for sending notifications
        store: Optional AlertStore for persistence
        
    Example:
        from datetime import datetime, timezone, timedelta
        
        now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
        window_end = now
        window_start = now - timedelta(hours=1)
        
        emailer = EmailAlerter()
        store = AlertStore()
        
        check_and_alert_volume_drop(
            provider="colorado",
            stage="harmonize",
            actual_count=75,  # Only 75 records
            expected_count=100,  # Expected 100
            threshold=0.20,  # Alert on >20% drop
            window_start=window_start,
            window_end=window_end,
            emailer=emailer,
            store=store
        )
        # This would trigger an alert since 75 < 100 * (1 - 0.20) = 80
    """
    # Get expected count from config if not provided
    if expected_count is None:
        config = load_email_config()
        expected_count = config.expected_records_per_provider_per_hour
        logger.debug(f"Using default expected count from config: {expected_count}")
    
    # Calculate drop percentage
    if expected_count <= 0:
        logger.warning(f"Invalid expected count: {expected_count}. Skipping volume drop check.")
        return
    
    drop_threshold_count = expected_count * (1 - threshold)
    
    if actual_count >= drop_threshold_count:
        logger.debug(
            f"Volume check passed for {provider}: {actual_count} >= {drop_threshold_count:.0f} "
            f"(threshold: {threshold:.1%})"
        )
        return
    
    # Calculate actual drop percentage
    drop_percentage = ((expected_count - actual_count) / expected_count) * 100
    
    logger.warning(
        f"Volume drop detected for {provider}: {actual_count}/{expected_count} "
        f"({drop_percentage:.1f}% drop, threshold: {threshold:.1%})",
        extra={
            "provider": provider,
            "stage": stage,
            "actual_count": actual_count,
            "expected_count": expected_count,
            "drop_percentage": drop_percentage,
            "threshold_percentage": threshold * 100,
            "window_start": window_start.isoformat(),
            "window_end": window_end.isoformat(),
        }
    )
    
    # Determine severity based on drop percentage
    if drop_percentage >= 40:
        severity = "CRITICAL"
        severity_level = "ERROR"  # For DynamoDB storage
    else:
        severity = "WARNING" 
        severity_level = "WARN"   # For DynamoDB storage
    
    # Build alert context
    context = {
        "stage": stage,
        "severity": severity,
        "provider": provider,
        "expected": expected_count,
        "actual": actual_count,
        "drop_pct": f"{drop_percentage:.1f}",
        "window_start": window_start.strftime("%Y-%m-%d %H:%M UTC"),
        "window_end": window_end.strftime("%Y-%m-%d %H:%M UTC"),
        "timestamp_iso": datetime.now().isoformat(),
        # Add trace context if available
        "run_id": None,  # Could be passed in future versions
        "trace_id": None,  # Could be extracted from logging context
    }
    
    # Send email alert
    try:
        # Create severity-specific subject line
        if severity == "CRITICAL":
            subject = f"🚨 [CRITICAL] Volume Drop: {provider} - {drop_percentage:.1f}% drop detected"
        else:
            subject = f"⚠️ [WARNING] Volume Drop: {provider} - {drop_percentage:.1f}% drop detected"
        
        emailer.send("volume_drop", subject, context)
        
        logger.info(
            f"Volume drop alert sent for {provider}",
            extra={
                "provider": provider,
                "drop_percentage": drop_percentage,
                "email_sent": True,
            }
        )
        
    except Exception as e:
        logger.error(
            f"Failed to send volume drop alert for {provider}: {e}",
            extra={
                "provider": provider,
                "error": str(e),
                "email_sent": False,
            }
        )
    
    # Store alert if persistence is enabled
    if store:
        try:
            dedupe_key = f"drop#{provider}#{window_start.isoformat()}"
            
            store.put_alert(
                provider=provider,
                stage=stage,
                severity=severity_level,
                code="VOLUME_DROP",
                message=f"Volume drop detected: {actual_count}/{expected_count} records ({drop_percentage:.1f}% drop)",
                metadata={
                    "actual_count": actual_count,
                    "expected_count": expected_count,
                    "drop_percentage": drop_percentage,
                    "threshold_percentage": threshold * 100,
                    "window_start": window_start.isoformat(),
                    "window_end": window_end.isoformat(),
                },
                dedupe_key=dedupe_key,
                ttl_seconds=7 * 24 * 3600  # Keep volume alerts for 7 days
            )
            
            logger.info(
                f"Volume drop alert stored for {provider}",
                extra={
                    "provider": provider,
                    "dedupe_key": dedupe_key,
                    "alert_stored": True,
                }
            )
            
        except Exception as e:
            logger.error(
                f"Failed to store volume drop alert for {provider}: {e}",
                extra={
                    "provider": provider,
                    "error": str(e),
                    "alert_stored": False,
                }
            )


# TODO: Future database-backed expected volume configuration
# class VolumeExpectationRepo:
#     """Repository for provider-specific volume expectations."""
#     
#     @staticmethod
#     def get_expected_volume(
#         provider: str, 
#         stage: str, 
#         time_window_hours: int = 1
#     ) -> Optional[int]:
#         """
#         Get expected volume for a provider/stage/time window combination.
#         
#         This would enable sophisticated volume expectations based on:
#         - Historical averages by provider
#         - Seasonal patterns (e.g., fewer records in winter)
#         - Day-of-week patterns (e.g., different volumes on weekends)
#         - Provider-specific SLAs and capabilities
#         - Maintenance windows and known outages
#         
#         Args:
#             provider: Provider name
#             stage: Processing stage
#             time_window_hours: Time window in hours
#             
#         Returns:
#             Optional[int]: Expected record count or None if not configured
#         """
#         pass
#     
#     @staticmethod
#     def update_expected_volume(
#         provider: str,
#         stage: str,
#         expected_count: int,
#         time_window_hours: int = 1,
#         effective_date: Optional[datetime] = None
#     ) -> None:
#         """
#         Update expected volume configuration for a provider.
#         
#         Args:
#             provider: Provider name
#             stage: Processing stage
#             expected_count: New expected record count
#             time_window_hours: Time window in hours
#             effective_date: When this expectation becomes effective
#         """
#         pass


def get_volume_trend(
    provider: str,
    stage: str,
    hours_back: int = 24,
    store: Optional[AlertStore] = None
) -> dict:
    """
    Analyze volume trend for a provider over recent time periods.
    
    This function would provide insights into volume patterns to help
    with capacity planning and anomaly detection.
    
    Args:
        provider: Provider name
        stage: Processing stage  
        hours_back: Number of hours to analyze
        store: AlertStore for retrieving historical data
        
    Returns:
        dict: Volume trend analysis
    """
    # TODO: Implement volume trend analysis
    # This would:
    # 1. Query recent volume drop alerts from AlertStore
    # 2. Calculate volume statistics (mean, median, std dev)
    # 3. Identify patterns (time-of-day, day-of-week effects)
    # 4. Return trend analysis for dashboards and capacity planning
    
    logger.debug(f"Volume trend analysis not implemented yet for {provider}/{stage}")
    return {
        "provider": provider,
        "stage": stage,
        "hours_analyzed": hours_back,
        "trend": "unknown",
        "recommendation": "Implement volume trend analysis"
    } 