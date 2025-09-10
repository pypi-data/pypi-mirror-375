"""
Alert persistence for mesonet alerts.

Provides optional DynamoDB storage for alerts with deduplication and TTL support.
Includes future hooks for EventBridge/SNS fan-out.
"""

import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any
import json

from .config import load_email_config

logger = logging.getLogger(__name__)


class AlertStore:
    """
    Optional DynamoDB storage for alert persistence and deduplication.
    
    Provides alert storage with automatic TTL and deduplication capabilities.
    If ALERTS_TABLE_NAME is not configured, operations become no-ops with warnings.
    
    Proposed DynamoDB table schema:
    - PK: alert_pk = f"{provider}#{stage}"
    - SK: timestamp (ISO8601 format)
    - Attributes:
      - severity (String)
      - code (String)
      - message (String)
      - metadata (Map)
      - status (String, default "OPEN")
      - ttl (Number, Unix timestamp)
      - dedupe_key (String, optional for deduplication)
    """
    
    def __init__(self, table_name: Optional[str] = None):
        """
        Initialize the alert store.
        
        Args:
            table_name: DynamoDB table name. If None, loads from environment
        """
        config = load_email_config()
        self.table_name = table_name or config.alerts_table_name
        self._dynamodb_client = None
        self._table = None
        
        if self.table_name:
            self._initialize_dynamodb()
            logger.info(f"AlertStore initialized with table: {self.table_name}")
        else:
            logger.warning(
                "AlertStore initialized without table name - persistence disabled. "
                "Set ALERTS_TABLE_NAME environment variable to enable."
            )
    
    def _initialize_dynamodb(self) -> None:
        """Initialize DynamoDB client and table resource lazily."""
        try:
            import boto3
            from botocore.exceptions import ClientError, NoCredentialsError
            
            self._dynamodb_client = boto3.client('dynamodb')
            dynamodb_resource = boto3.resource('dynamodb')
            self._table = dynamodb_resource.Table(self.table_name)
            
        except ImportError:
            logger.error("boto3 not available - DynamoDB persistence disabled")
            self.table_name = None
        except NoCredentialsError:
            logger.warning("AWS credentials not found - DynamoDB persistence disabled")
            self.table_name = None
        except Exception as e:
            logger.error(f"Failed to initialize DynamoDB: {e}")
            self.table_name = None
    
    def put_alert(
        self,
        provider: str,
        stage: str,
        severity: str,
        code: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None,
        dedupe_key: Optional[str] = None,
        ttl_seconds: int = 86400
    ) -> None:
        """
        Store alert in DynamoDB with optional deduplication.
        
        Args:
            provider: Provider name (e.g., "colorado", "iowa")
            stage: Processing stage (e.g., "ingest", "harmonize")
            severity: Alert severity (e.g., "ERROR", "WARN", "INFO")
            code: Alert code (e.g., "PROVIDER_EMPTY", "INGEST_FAILURE")
            message: Human-readable alert message
            metadata: Additional alert metadata
            dedupe_key: Optional deduplication key to prevent duplicates
            ttl_seconds: TTL in seconds (default 24 hours)
        """
        if not self.table_name or not self._table:
            logger.warning("DynamoDB table not configured - skipping alert persistence")
            return
        
        try:
            # Calculate TTL timestamp
            ttl_timestamp = int((datetime.now(timezone.utc).timestamp() + ttl_seconds))
            timestamp_iso = datetime.now(timezone.utc).isoformat()
            
            # Build item
            item = {
                'alert_pk': f"{provider}#{stage}",
                'timestamp': timestamp_iso,
                'severity': severity,
                'code': code,
                'message': message,
                'metadata': metadata or {},
                'status': 'OPEN',
                'ttl': ttl_timestamp,
                'provider': provider,
                'stage': stage,
            }
            
            # Add dedupe key if provided
            if dedupe_key:
                item['dedupe_key'] = dedupe_key
            
            # Prepare put operation with optional deduplication
            put_kwargs = {
                'Item': item
            }
            
            # Add condition expression for deduplication if dedupe_key provided
            if dedupe_key:
                put_kwargs['ConditionExpression'] = 'attribute_not_exists(dedupe_key)'
            
            # Store alert
            self._table.put_item(**put_kwargs)
            
            logger.info(
                f"Alert stored successfully",
                extra={
                    "provider": provider,
                    "stage": stage,
                    "severity": severity,
                    "code": code,
                    "dedupe_key": dedupe_key,
                    "ttl_seconds": ttl_seconds,
                }
            )
            
            # TODO: Future EventBridge/SNS fan-out
            # This would publish the alert to EventBridge for downstream processing:
            # - Send to SNS topic for real-time notifications
            # - Trigger Lambda functions for alert processing
            # - Integration with incident management systems
            # - Webhook notifications to external systems
            #
            # Example:
            # self._publish_to_eventbridge({
            #     'source': 'mesonet.alerts',
            #     'detail-type': f'Alert {severity}',
            #     'detail': {
            #         'provider': provider,
            #         'stage': stage,
            #         'severity': severity,
            #         'code': code,
            #         'message': message,
            #         'metadata': metadata,
            #         'timestamp': timestamp_iso
            #     }
            # })
            
        except Exception as e:
            # Handle conditional write failures (duplicates) gracefully
            if 'ConditionalCheckFailedException' in str(e):
                logger.info(
                    f"Duplicate alert suppressed by dedupe_key: {dedupe_key}",
                    extra={
                        "provider": provider,
                        "stage": stage,
                        "severity": severity,
                        "code": code,
                    }
                )
                return
            
            logger.error(
                f"Failed to store alert: {e}",
                extra={
                    "provider": provider,
                    "stage": stage,
                    "severity": severity,
                    "code": code,
                    "error": str(e),
                }
            )
            # Don't raise - alert storage failure shouldn't break the main process
    
    def get_recent_alerts(
        self, 
        provider: str, 
        stage: str, 
        hours: int = 24
    ) -> list[Dict[str, Any]]:
        """
        Retrieve recent alerts for a provider/stage combination.
        
        Args:
            provider: Provider name
            stage: Processing stage
            hours: Number of hours to look back
            
        Returns:
            list[Dict[str, Any]]: List of recent alerts
        """
        if not self.table_name or not self._table:
            logger.warning("DynamoDB table not configured - returning empty results")
            return []
        
        try:
            from boto3.dynamodb.conditions import Key
            from datetime import timedelta
            
            # Calculate time window
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
            cutoff_iso = cutoff_time.isoformat()
            
            response = self._table.query(
                KeyConditionExpression=Key('alert_pk').eq(f"{provider}#{stage}") &
                                     Key('timestamp').gte(cutoff_iso),
                ScanIndexForward=False,  # Most recent first
                Limit=50  # Reasonable limit
            )
            
            return response.get('Items', [])
            
        except Exception as e:
            logger.error(f"Failed to retrieve alerts: {e}")
            return []


# TODO: Future EventBridge/SNS integration
# class AlertEventPublisher:
#     """Publisher for alert events to EventBridge/SNS."""
#     
#     def __init__(self, event_bus_name: str, sns_topic_arn: Optional[str] = None):
#         """
#         Initialize the event publisher.
#         
#         Args:
#             event_bus_name: EventBridge event bus name
#             sns_topic_arn: Optional SNS topic for immediate notifications
#         """
#         self.event_bus_name = event_bus_name
#         self.sns_topic_arn = sns_topic_arn
#         self._eventbridge_client = boto3.client('events')
#         self._sns_client = boto3.client('sns') if sns_topic_arn else None
#     
#     def publish_alert_event(self, alert_data: Dict[str, Any]) -> None:
#         """
#         Publish alert event to EventBridge and optionally SNS.
#         
#         This enables:
#         - Decoupled alert processing
#         - Integration with external systems
#         - Complex routing rules
#         - Audit trails
#         - Real-time dashboards
#         
#         Args:
#             alert_data: Alert information dictionary
#         """
#         pass 