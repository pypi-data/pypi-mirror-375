"""
Unit tests for volume drop detection functionality.

Tests drop detection logic, alerting, and persistence.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone, timedelta

from mesonet_alerts.dropcheck import check_and_alert_volume_drop, get_volume_trend
from mesonet_alerts.emailer import EmailAlerter
from mesonet_alerts.store import AlertStore
from mesonet_alerts.config import EmailConfig


class TestVolumeDropCheck(unittest.TestCase):
    """Test cases for volume drop detection."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_emailer = Mock(spec=EmailAlerter)
        self.mock_store = Mock(spec=AlertStore)
        
        # Test time window
        self.window_end = datetime(2025, 1, 15, 14, 0, 0, tzinfo=timezone.utc)
        self.window_start = self.window_end - timedelta(hours=1)
        
        # Mock config
        self.mock_config = EmailConfig(
            smtp_host="localhost",
            smtp_port=1025,
            smtp_user="",
            smtp_password="",
            from_address="alerts@test.com",
            to_addresses=["admin@test.com"],
            alerts_table_name="alerts",
            expected_records_per_provider_per_hour=100
        )
    
    def test_no_drop_detected(self):
        """Test when actual count meets expectations."""
        with patch('mesonet_alerts.dropcheck.load_email_config', return_value=self.mock_config):
            check_and_alert_volume_drop(
                provider="colorado",
                actual_count=85,  # 85 >= 80 (100 * 0.8)
                threshold=0.20,
                window_start=self.window_start,
                window_end=self.window_end,
                emailer=self.mock_emailer,
                store=self.mock_store
            )
        
        # No alerts should be sent
        self.mock_emailer.send.assert_not_called()
        self.mock_store.put_alert.assert_not_called()
    
    def test_drop_detected_with_explicit_expected(self):
        """Test drop detection with explicitly provided expected count."""
        check_and_alert_volume_drop(
            provider="iowa",
            actual_count=75,  # 75 < 80 (100 * 0.8)
            expected_count=100,
            threshold=0.20,
            window_start=self.window_start,
            window_end=self.window_end,
            emailer=self.mock_emailer,
            store=self.mock_store
        )
        
        # Alert should be sent
        self.mock_emailer.send.assert_called_once()
        call_args = self.mock_emailer.send.call_args
        
        # Verify email parameters
        self.assertEqual(call_args[0][0], "volume_drop")  # template
        self.assertIn("25.0% drop detected", call_args[0][1])  # subject
        
        # Verify context
        context = call_args[0][2]
        self.assertEqual(context["provider"], "iowa")
        self.assertEqual(context["severity"], "WARN")
        self.assertEqual(context["actual"], 75)
        self.assertEqual(context["expected"], 100)
        self.assertEqual(context["drop_pct"], "25.0")
        
        # Alert should be stored
        self.mock_store.put_alert.assert_called_once()
        store_call_args = self.mock_store.put_alert.call_args
        self.assertEqual(store_call_args[1]["provider"], "iowa")
        self.assertEqual(store_call_args[1]["severity"], "WARN")
        self.assertEqual(store_call_args[1]["code"], "VOLUME_DROP")
        self.assertIn("drop#iowa#", store_call_args[1]["dedupe_key"])
    
    def test_drop_detected_with_config_default(self):
        """Test drop detection using config default expected count."""
        with patch('mesonet_alerts.dropcheck.load_email_config', return_value=self.mock_config):
            check_and_alert_volume_drop(
                provider="colorado",
                actual_count=70,  # 70 < 80 (100 * 0.8)
                # expected_count not provided, should use config default
                threshold=0.20,
                window_start=self.window_start,
                window_end=self.window_end,
                emailer=self.mock_emailer,
                store=self.mock_store
            )
        
        # Alert should be sent with config default
        self.mock_emailer.send.assert_called_once()
        context = self.mock_emailer.send.call_args[0][2]
        self.assertEqual(context["expected"], 100)  # From config
        self.assertEqual(context["drop_pct"], "30.0")  # (100-70)/100 * 100
    
    def test_custom_threshold(self):
        """Test custom drop threshold."""
        check_and_alert_volume_drop(
            provider="test",
            actual_count=85,  # 85 < 90 (100 * 0.9) but >= 80 (100 * 0.8)
            expected_count=100,
            threshold=0.10,  # 10% threshold instead of 20%
            window_start=self.window_start,
            window_end=self.window_end,
            emailer=self.mock_emailer,
            store=self.mock_store
        )
        
        # Alert should be sent with 10% threshold
        self.mock_emailer.send.assert_called_once()
        context = self.mock_emailer.send.call_args[0][2]
        self.assertEqual(context["drop_pct"], "15.0")
    
    def test_no_alert_without_store(self):
        """Test alerting without store persistence."""
        check_and_alert_volume_drop(
            provider="test",
            actual_count=70,
            expected_count=100,
            threshold=0.20,
            window_start=self.window_start,
            window_end=self.window_end,
            emailer=self.mock_emailer,
            store=None  # No store provided
        )
        
        # Email should still be sent
        self.mock_emailer.send.assert_called_once()
        
        # Store should not be called
        self.mock_store.put_alert.assert_not_called()
    
    def test_invalid_expected_count(self):
        """Test handling of invalid expected count."""
        with patch('mesonet_alerts.dropcheck.logger') as mock_logger:
            check_and_alert_volume_drop(
                provider="test",
                actual_count=50,
                expected_count=0,  # Invalid
                threshold=0.20,
                window_start=self.window_start,
                window_end=self.window_end,
                emailer=self.mock_emailer,
                store=self.mock_store
            )
        
        # Should log warning and skip check
        mock_logger.warning.assert_called_once()
        self.mock_emailer.send.assert_not_called()
        self.mock_store.put_alert.assert_not_called()
    
    def test_email_failure_handling(self):
        """Test handling of email sending failures."""
        self.mock_emailer.send.side_effect = Exception("SMTP failed")
        
        with patch('mesonet_alerts.dropcheck.logger') as mock_logger:
            check_and_alert_volume_drop(
                provider="test",
                actual_count=70,
                expected_count=100,
                threshold=0.20,
                window_start=self.window_start,
                window_end=self.window_end,
                emailer=self.mock_emailer,
                store=self.mock_store
            )
        
        # Should log error but continue with store operation
        mock_logger.error.assert_called()
        self.mock_store.put_alert.assert_called_once()
    
    def test_store_failure_handling(self):
        """Test handling of store failures."""
        self.mock_store.put_alert.side_effect = Exception("DynamoDB failed")
        
        with patch('mesonet_alerts.dropcheck.logger') as mock_logger:
            check_and_alert_volume_drop(
                provider="test",
                actual_count=70,
                expected_count=100,
                threshold=0.20,
                window_start=self.window_start,
                window_end=self.window_end,
                emailer=self.mock_emailer,
                store=self.mock_store
            )
        
        # Should log error but email should still be sent
        self.mock_emailer.send.assert_called_once()
        mock_logger.error.assert_called()
    
    def test_context_formatting(self):
        """Test alert context formatting."""
        with patch('mesonet_alerts.dropcheck.datetime') as mock_datetime:
            # Mock current time
            mock_now = datetime(2025, 1, 15, 14, 30, 0)
            mock_datetime.now.return_value = mock_now
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
            
            check_and_alert_volume_drop(
                provider="test_provider",
                stage="harmonize",
                actual_count=60,
                expected_count=100,
                threshold=0.25,
                window_start=self.window_start,
                window_end=self.window_end,
                emailer=self.mock_emailer,
                store=self.mock_store
            )
        
        # Verify context formatting
        context = self.mock_emailer.send.call_args[0][2]
        
        self.assertEqual(context["stage"], "harmonize")
        self.assertEqual(context["severity"], "WARN")
        self.assertEqual(context["provider"], "test_provider")
        self.assertEqual(context["actual"], 60)
        self.assertEqual(context["expected"], 100)
        self.assertEqual(context["drop_pct"], "40.0")
        self.assertEqual(context["window_start"], "2025-01-15 13:00 UTC")
        self.assertEqual(context["window_end"], "2025-01-15 14:00 UTC")
        self.assertEqual(context["timestamp_iso"], mock_now.isoformat())
    
    def test_edge_case_exact_threshold(self):
        """Test edge case where drop exactly equals threshold."""
        check_and_alert_volume_drop(
            provider="test",
            actual_count=80,  # Exactly at 20% threshold
            expected_count=100,
            threshold=0.20,
            window_start=self.window_start,
            window_end=self.window_end,
            emailer=self.mock_emailer,
            store=self.mock_store
        )
        
        # Should not trigger alert (80 >= 80)
        self.mock_emailer.send.assert_not_called()
        self.mock_store.put_alert.assert_not_called()
    
    def test_edge_case_just_below_threshold(self):
        """Test edge case where drop is just below threshold."""
        check_and_alert_volume_drop(
            provider="test",
            actual_count=79,  # Just below 20% threshold
            expected_count=100,
            threshold=0.20,
            window_start=self.window_start,
            window_end=self.window_end,
            emailer=self.mock_emailer,
            store=self.mock_store
        )
        
        # Should trigger alert
        self.mock_emailer.send.assert_called_once()
        context = self.mock_emailer.send.call_args[0][2]
        self.assertEqual(context["drop_pct"], "21.0")


class TestVolumeTrend(unittest.TestCase):
    """Test cases for volume trend analysis."""
    
    def test_get_volume_trend_not_implemented(self):
        """Test volume trend analysis placeholder."""
        mock_store = Mock(spec=AlertStore)
        
        with patch('mesonet_alerts.dropcheck.logger') as mock_logger:
            result = get_volume_trend("test_provider", "harmonize", 24, mock_store)
        
        # Should return placeholder response
        expected = {
            "provider": "test_provider",
            "stage": "harmonize",
            "hours_analyzed": 24,
            "trend": "unknown",
            "recommendation": "Implement volume trend analysis"
        }
        
        self.assertEqual(result, expected)
        mock_logger.debug.assert_called_once()


if __name__ == '__main__':
    unittest.main() 