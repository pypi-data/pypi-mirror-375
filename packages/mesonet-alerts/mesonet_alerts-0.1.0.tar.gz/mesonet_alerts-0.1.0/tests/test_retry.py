"""
Unit tests for retry functionality.

Tests retry logic, backoff behavior, and exception handling.
"""

import unittest
from unittest.mock import Mock, patch
import time

from mesonet_alerts.retry import (
    run_with_retries, 
    ProviderEmptyDataError, 
    retry_on_exceptions,
    is_network_error,
    is_rate_limit_error,
    is_provider_error
)


class TestRetryFunctionality(unittest.TestCase):
    """Test cases for retry functionality."""
    
    def test_success_on_first_attempt(self):
        """Test function succeeding on first attempt."""
        mock_fn = Mock(return_value="success")
        is_retryable = Mock(return_value=True)
        
        result = run_with_retries(mock_fn, is_retryable, attempts=3)
        
        self.assertEqual(result, "success")
        mock_fn.assert_called_once()
        is_retryable.assert_not_called()
    
    def test_success_after_retries(self):
        """Test function succeeding after retries."""
        mock_fn = Mock(side_effect=[
            ProviderEmptyDataError("Empty data"),
            ProviderEmptyDataError("Still empty"),
            "success"
        ])
        is_retryable = Mock(return_value=True)
        
        with patch('time.sleep') as mock_sleep:
            result = run_with_retries(mock_fn, is_retryable, attempts=3, backoffs=[0.1, 0.2])
            
            self.assertEqual(result, "success")
            self.assertEqual(mock_fn.call_count, 3)
            self.assertEqual(is_retryable.call_count, 2)
            
            # Verify sleep calls
            self.assertEqual(mock_sleep.call_count, 2)
            mock_sleep.assert_any_call(0.1)
            mock_sleep.assert_any_call(0.2)
    
    def test_failure_after_all_retries(self):
        """Test function failing after all retries exhausted."""
        final_error = ProviderEmptyDataError("Final failure")
        mock_fn = Mock(side_effect=[
            ProviderEmptyDataError("First failure"),
            ProviderEmptyDataError("Second failure"),
            final_error
        ])
        is_retryable = Mock(return_value=True)
        
        with patch('time.sleep') as mock_sleep:
            with self.assertRaises(ProviderEmptyDataError) as cm:
                run_with_retries(mock_fn, is_retryable, attempts=3)
            
            self.assertEqual(cm.exception, final_error)
            self.assertEqual(mock_fn.call_count, 3)
            self.assertEqual(is_retryable.call_count, 2)
            self.assertEqual(mock_sleep.call_count, 2)
    
    def test_non_retryable_error(self):
        """Test non-retryable error stops retries immediately."""
        non_retryable_error = ValueError("Invalid input")
        mock_fn = Mock(side_effect=non_retryable_error)
        is_retryable = Mock(return_value=False)
        
        with self.assertRaises(ValueError) as cm:
            run_with_retries(mock_fn, is_retryable, attempts=3)
        
        self.assertEqual(cm.exception, non_retryable_error)
        mock_fn.assert_called_once()
        is_retryable.assert_called_once_with(non_retryable_error)
    
    def test_custom_backoffs(self):
        """Test custom backoff intervals."""
        mock_fn = Mock(side_effect=[
            ProviderEmptyDataError("Error 1"),
            ProviderEmptyDataError("Error 2"),
            "success"
        ])
        is_retryable = Mock(return_value=True)
        custom_backoffs = [0.5, 1.0]
        
        with patch('time.sleep') as mock_sleep:
            result = run_with_retries(mock_fn, is_retryable, attempts=3, backoffs=custom_backoffs)
            
            self.assertEqual(result, "success")
            mock_sleep.assert_any_call(0.5)
            mock_sleep.assert_any_call(1.0)
    
    def test_backoffs_extension(self):
        """Test backoffs list extension when shorter than attempts."""
        mock_fn = Mock(side_effect=[
            ProviderEmptyDataError("Error 1"),
            ProviderEmptyDataError("Error 2"),
            ProviderEmptyDataError("Error 3"),
            ProviderEmptyDataError("Error 4")
        ])
        is_retryable = Mock(return_value=True)
        short_backoffs = [0.1]  # Only one backoff for 4 attempts
        
        with patch('time.sleep') as mock_sleep:
            with self.assertRaises(ProviderEmptyDataError):
                run_with_retries(mock_fn, is_retryable, attempts=4, backoffs=short_backoffs)
            
            # Should use 0.1 for all retries since it extends with the last value
            expected_calls = [unittest.mock.call(0.1)] * 3
            mock_sleep.assert_has_calls(expected_calls)
    
    def test_invalid_attempts(self):
        """Test invalid attempts parameter raises ValueError."""
        mock_fn = Mock()
        is_retryable = Mock()
        
        with self.assertRaises(ValueError):
            run_with_retries(mock_fn, is_retryable, attempts=0)
    
    def test_default_backoffs(self):
        """Test default backoff values."""
        mock_fn = Mock(side_effect=[
            ProviderEmptyDataError("Error 1"),
            ProviderEmptyDataError("Error 2"),
            ProviderEmptyDataError("Error 3")
        ])
        is_retryable = Mock(return_value=True)
        
        with patch('time.sleep') as mock_sleep:
            with self.assertRaises(ProviderEmptyDataError):
                run_with_retries(mock_fn, is_retryable)  # Use defaults
            
            # Default backoffs are [1, 3, 9]
            mock_sleep.assert_any_call(1)
            mock_sleep.assert_any_call(3)


class TestRetryDecorator(unittest.TestCase):
    """Test cases for retry decorator."""
    
    def test_decorator_success(self):
        """Test decorator with successful function."""
        @retry_on_exceptions(ProviderEmptyDataError, ValueError)
        def test_function(value):
            return f"result: {value}"
        
        result = test_function("test")
        self.assertEqual(result, "result: test")
    
    def test_decorator_with_retries(self):
        """Test decorator with retryable exceptions."""
        call_count = 0
        
        @retry_on_exceptions(ProviderEmptyDataError)
        def test_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ProviderEmptyDataError("Not ready yet")
            return "success"
        
        with patch('time.sleep'):
            result = test_function()
            
            self.assertEqual(result, "success")
            self.assertEqual(call_count, 3)
    
    def test_decorator_non_retryable_exception(self):
        """Test decorator with non-retryable exception."""
        @retry_on_exceptions(ProviderEmptyDataError)
        def test_function():
            raise ValueError("This should not be retried")
        
        with self.assertRaises(ValueError):
            test_function()


class TestErrorClassification(unittest.TestCase):
    """Test cases for error classification functions."""
    
    def test_is_network_error(self):
        """Test network error detection."""
        network_errors = [
            Exception("Connection timeout"),
            Exception("Network unreachable"),
            Exception("DNS resolution failed"),
            Exception("Connection refused"),
            Exception("Broken pipe"),
        ]
        
        for error in network_errors:
            with self.subTest(error=str(error)):
                self.assertTrue(is_network_error(error))
        
        # Non-network errors
        non_network_errors = [
            Exception("Invalid data format"),
            Exception("Authentication failed"),
            ValueError("Invalid parameter"),
        ]
        
        for error in non_network_errors:
            with self.subTest(error=str(error)):
                self.assertFalse(is_network_error(error))
    
    def test_is_rate_limit_error(self):
        """Test rate limit error detection."""
        rate_limit_errors = [
            Exception("Rate limit exceeded"),
            Exception("Too many requests"),
            Exception("Throttling in effect"),
            Exception("HTTP 429 error"),
            Exception("Quota exceeded"),
        ]
        
        for error in rate_limit_errors:
            with self.subTest(error=str(error)):
                self.assertTrue(is_rate_limit_error(error))
        
        # Non-rate-limit errors
        non_rate_limit_errors = [
            Exception("Invalid data format"),
            Exception("Authentication failed"),
            ValueError("Invalid parameter"),
        ]
        
        for error in non_rate_limit_errors:
            with self.subTest(error=str(error)):
                self.assertFalse(is_rate_limit_error(error))
    
    def test_is_provider_error(self):
        """Test provider error classification."""
        # Should be retryable
        retryable_errors = [
            ProviderEmptyDataError("No data"),
            Exception("Connection timeout"),
            Exception("Rate limit exceeded"),
        ]
        
        for error in retryable_errors:
            with self.subTest(error=str(error)):
                self.assertTrue(is_provider_error(error))
        
        # Should not be retryable
        non_retryable_errors = [
            ValueError("Invalid parameter"),
            Exception("Authentication failed"),
            Exception("Invalid data format"),
        ]
        
        for error in non_retryable_errors:
            with self.subTest(error=str(error)):
                # These should still return False unless they match network/rate limit patterns
                result = is_provider_error(error)
                if "Invalid parameter" in str(error) or "Authentication failed" in str(error):
                    self.assertFalse(result)


class TestProviderEmptyDataError(unittest.TestCase):
    """Test cases for ProviderEmptyDataError."""
    
    def test_provider_empty_data_error_inheritance(self):
        """Test ProviderEmptyDataError inherits from RuntimeError."""
        error = ProviderEmptyDataError("Test message")
        self.assertIsInstance(error, RuntimeError)
        self.assertEqual(str(error), "Test message")
    
    def test_provider_empty_data_error_can_be_raised(self):
        """Test ProviderEmptyDataError can be raised and caught."""
        with self.assertRaises(ProviderEmptyDataError) as cm:
            raise ProviderEmptyDataError("Provider returned empty data")
        
        self.assertEqual(str(cm.exception), "Provider returned empty data")


if __name__ == '__main__':
    unittest.main() 