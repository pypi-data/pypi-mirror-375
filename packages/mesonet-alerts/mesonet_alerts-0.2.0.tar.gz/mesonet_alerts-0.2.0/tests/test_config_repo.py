"""
Unit tests for ConfigRepository class.
"""

import unittest
from unittest.mock import Mock, patch
from mesonet_alerts.config_repo import ConfigRepository, SMTPConfig, EmailConfig


class TestConfigRepository(unittest.TestCase):
    """Test cases for ConfigRepository."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_dynamodb = Mock()
        self.table_name = "test_config_table"
        self.repo = ConfigRepository(self.mock_dynamodb, self.table_name)
    
    def test_get_email_config_success(self):
        """Test successful configuration retrieval."""
        # Mock DynamoDB response
        mock_response = {
            'Item': {
                'config_pk': {'S': 'email_config'},
                'config_sk': {'S': 'active'},
                'smtp': {
                    'M': {
                        'host': {'S': 'smtp.example.com'},
                        'port': {'N': '587'},
                        'user': {'S': 'user@example.com'},
                        'pass': {'S': 'password123'},
                        'from': {'S': 'alerts@example.com'}
                    }
                },
                'recipients': {
                    'M': {
                        'list': {
                            'L': [
                                {'S': 'admin@example.com'},
                                {'S': 'team@example.com'}
                            ]
                        }
                    }
                },
                'templates': {
                    'M': {
                        'process_failure': {
                            'M': {
                                'html': {'S': '<html><body>Error: {{error}}</body></html>'},
                                'text': {'S': 'Error: {{error}}'}
                            }
                        }
                    }
                }
            }
        }
        
        self.mock_dynamodb.get_item.return_value = mock_response
        
        # Test
        config = self.repo.get_email_config()
        
        # Assertions
        self.assertIsNotNone(config)
        self.assertEqual(config.smtp.host, 'smtp.example.com')
        self.assertEqual(config.smtp.port, 587)
        self.assertEqual(config.smtp.user, 'user@example.com')
        self.assertEqual(config.smtp.password, 'password123')
        self.assertEqual(config.smtp.from_address, 'alerts@example.com')
        self.assertEqual(len(config.recipients), 2)
        self.assertIn('admin@example.com', config.recipients)
        self.assertIn('team@example.com', config.recipients)
        self.assertIn('process_failure', config.templates)
        
        # Verify DynamoDB call
        self.mock_dynamodb.get_item.assert_called_once_with(
            TableName=self.table_name,
            Key={
                'config_pk': {'S': 'email_config'},
                'config_sk': {'S': 'active'}
            }
        )
    
    def test_get_email_config_not_found(self):
        """Test configuration not found."""
        # Mock DynamoDB response with no item
        mock_response = {}
        self.mock_dynamodb.get_item.return_value = mock_response
        
        # Test
        config = self.repo.get_email_config()
        
        # Assertions
        self.assertIsNone(config)
    
    def test_get_email_config_exception(self):
        """Test exception handling."""
        # Mock DynamoDB exception
        self.mock_dynamodb.get_item.side_effect = Exception("DynamoDB error")
        
        # Test
        config = self.repo.get_email_config()
        
        # Assertions
        self.assertIsNone(config)
    
    def test_get_email_config_custom_keys(self):
        """Test configuration retrieval with custom keys."""
        # Mock DynamoDB response
        mock_response = {
            'Item': {
                'smtp': {'M': {'host': {'S': 'test.smtp.com'}, 'port': {'N': '25'}, 'user': {'S': ''}, 'pass': {'S': ''}, 'from': {'S': 'test@local'}}},
                'recipients': {'M': {'list': {'L': [{'S': 'test@local'}]}}},
                'templates': {'M': {}}
            }
        }
        
        self.mock_dynamodb.get_item.return_value = mock_response
        
        # Test with custom keys
        config = self.repo.get_email_config('custom_pk', 'custom_sk')
        
        # Assertions
        self.assertIsNotNone(config)
        self.assertEqual(config.smtp.host, 'test.smtp.com')
        
        # Verify DynamoDB call with custom keys
        self.mock_dynamodb.get_item.assert_called_once_with(
            TableName=self.table_name,
            Key={
                'config_pk': {'S': 'custom_pk'},
                'config_sk': {'S': 'custom_sk'}
            }
        )


if __name__ == '__main__':
    unittest.main() 