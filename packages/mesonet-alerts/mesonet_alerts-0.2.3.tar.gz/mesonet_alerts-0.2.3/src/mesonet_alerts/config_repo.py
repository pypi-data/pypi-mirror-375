"""
DynamoDB-backed configuration repository for email settings and templates.
"""

import boto3
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import structlog

logger = structlog.get_logger(__name__)


@dataclass
class SMTPConfig:
    """SMTP configuration settings."""
    host: str
    port: int
    user: str
    password: str
    from_address: str


@dataclass
class EmailConfig:
    """Complete email configuration including SMTP and recipients."""
    smtp: SMTPConfig
    recipients: List[str]
    templates: Dict[str, Dict[str, str]]  # template_name -> {html, text}


class ConfigRepository:
    """Repository for loading email configuration from DynamoDB."""
    
    def __init__(self, dynamodb_client, table_name: str):
        """
        Initialize the configuration repository.
        
        Args:
            dynamodb_client: Boto3 DynamoDB client
            table_name: Name of the configuration table
        """
        self.dynamodb = dynamodb_client
        self.table_name = table_name
        
    def get_email_config(self, config_pk: str = "email_config", config_sk: str = "active") -> Optional[EmailConfig]:
        """
        Load email configuration from DynamoDB.
        
        Args:
            config_pk: Partition key for the configuration
            config_sk: Sort key for the configuration
            
        Returns:
            EmailConfig if found, None otherwise
        """
        try:
            response = self.dynamodb.get_item(
                TableName=self.table_name,
                Key={
                    'config_pk': {'S': config_pk},
                    'config_sk': {'S': config_sk}
                }
            )
            
            if 'Item' not in response:
                logger.warning(f"No email config found with pk={config_pk}, sk={config_sk}")
                return None
                
            item = response['Item']
            
            # Parse SMTP config
            smtp_data = item.get('smtp', {}).get('M', {})
            smtp_config = SMTPConfig(
                host=smtp_data.get('host', {}).get('S', 'localhost'),
                port=int(smtp_data.get('port', {}).get('N', '1025')),
                user=smtp_data.get('user', {}).get('S', ''),
                password=smtp_data.get('pass', {}).get('S', ''),
                from_address=smtp_data.get('from', {}).get('S', 'alerts@local.test')
            )
            
            # Parse recipients
            recipients_list = item.get('recipients', {}).get('M', {}).get('list', {}).get('L', [])
            recipients = [r.get('S', '') for r in recipients_list]
            
            # Parse templates
            templates_data = item.get('templates', {}).get('M', {})
            templates = {}
            for template_name, template_data in templates_data.items():
                template_map = template_data.get('M', {})
                templates[template_name] = {
                    'html': template_map.get('html', {}).get('S', ''),
                    'text': template_map.get('text', {}).get('S', '')
                }
            
            config = EmailConfig(
                smtp=smtp_config,
                recipients=recipients,
                templates=templates
            )
            
            logger.info(f"Loaded email config with {len(recipients)} recipients and {len(templates)} templates")
            return config
            
        except Exception as e:
            logger.error(f"Failed to load email config from DynamoDB: {e}")
            return None 