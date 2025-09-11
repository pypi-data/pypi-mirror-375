"""
Retry helpers for mesonet services.

Provides configurable retry logic with exponential backoff for provider operations.
Includes custom exceptions for different failure scenarios.
"""

import logging
import time
from typing import Callable, TypeVar, List
from functools import wraps

logger = logging.getLogger(__name__)

T = TypeVar('T')


class ProviderEmptyDataError(RuntimeError):
    """
    Exception raised when a provider returns empty data.
    
    This is a retryable error that indicates the provider endpoint
    is responding but not returning any data records.
    """
    pass


def run_with_retries(
    fn: Callable[[], T],
    is_retryable: Callable[[Exception], bool],
    attempts: int = 3,
    backoffs: List[int] | None = None
) -> T:
    """
    Execute a function with retry logic and exponential backoff.
    
    This helper provides a simple but effective retry mechanism for operations
    that may fail due to transient issues like network timeouts, rate limiting,
    or temporary service unavailability.
    
    Args:
        fn: Function to execute (should take no arguments)
        is_retryable: Function to determine if an exception should trigger a retry
        attempts: Maximum number of attempts (default: 3)
        backoffs: List of sleep seconds between attempts (default: [1, 3, 9])
        
    Returns:
        T: Result of successful function execution
        
    Raises:
        Exception: The last exception encountered after all retries are exhausted
        
    Example:
        def fetch_data():
            # Your data fetching logic here
            response = requests.get("https://api.example.com/data")
            if not response.json().get("records"):
                raise ProviderEmptyDataError("No records returned")
            return response.json()
        
        def is_retryable_error(e):
            return isinstance(e, (ProviderEmptyDataError, requests.Timeout))
        
        try:
            data = run_with_retries(fetch_data, is_retryable_error, attempts=3)
        except ProviderEmptyDataError:
            # Handle final failure after retries
            pass
    """
    if backoffs is None:
        backoffs = [1, 3, 9]
    
    if attempts < 1:
        raise ValueError("Attempts must be at least 1")
    
    if len(backoffs) < attempts - 1:
        # Extend backoffs if needed by repeating the last value
        last_backoff = backoffs[-1] if backoffs else 9
        backoffs.extend([last_backoff] * (attempts - 1 - len(backoffs)))
    
    last_exception = None
    
    for attempt in range(attempts):
        try:
            logger.debug(f"Executing function, attempt {attempt + 1}/{attempts}")
            result = fn()
            
            if attempt > 0:
                logger.info(f"Function succeeded on attempt {attempt + 1}/{attempts}")
            
            return result
            
        except Exception as e:
            last_exception = e
            
            # Check if this is the last attempt
            if attempt == attempts - 1:
                logger.error(
                    f"Function failed after {attempts} attempts: {e}",
                    extra={"attempts": attempts, "final_error": str(e)}
                )
                break
            
            # Check if the error is retryable
            if not is_retryable(e):
                logger.error(
                    f"Non-retryable error encountered on attempt {attempt + 1}: {e}",
                    extra={"attempt": attempt + 1, "error": str(e)}
                )
                break
            
            # Calculate backoff time
            backoff_time = backoffs[attempt]
            
            logger.warning(
                f"Retryable error on attempt {attempt + 1}/{attempts}: {e}. "
                f"Retrying in {backoff_time} seconds...",
                extra={
                    "attempt": attempt + 1,
                    "total_attempts": attempts,
                    "backoff_seconds": backoff_time,
                    "error": str(e),
                    "error_type": type(e).__name__
                }
            )
            
            # Sleep before retry
            time.sleep(backoff_time)
    
    # All retries exhausted, raise the last exception
    if last_exception:
        raise last_exception
    else:
        # This shouldn't happen, but just in case
        raise RuntimeError("Unexpected error: no exception to re-raise")


def retry_on_exceptions(*exception_types):
    """
    Decorator for automatic retry on specific exception types.
    
    This decorator provides a convenient way to add retry logic to functions
    without modifying their implementation.
    
    Args:
        *exception_types: Exception types that should trigger retries
        
    Example:
        @retry_on_exceptions(ProviderEmptyDataError, requests.Timeout)
        def fetch_provider_data(provider_url):
            response = requests.get(provider_url, timeout=30)
            if not response.json().get("data"):
                raise ProviderEmptyDataError("No data returned")
            return response.json()
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            def execute():
                return func(*args, **kwargs)
            
            def is_retryable(e):
                return isinstance(e, exception_types)
            
            return run_with_retries(execute, is_retryable)
        
        return wrapper
    return decorator


# Common retry predicates for convenience
def is_network_error(e: Exception) -> bool:
    """
    Check if an exception represents a network-related error.
    
    Args:
        e: Exception to check
        
    Returns:
        bool: True if the exception indicates a network issue
    """
    error_str = str(e).lower()
    return any(keyword in error_str for keyword in [
        'timeout', 'connection', 'network', 'dns', 'resolve',
        'unreachable', 'refused', 'reset', 'broken pipe'
    ])


def is_rate_limit_error(e: Exception) -> bool:
    """
    Check if an exception represents a rate limiting error.
    
    Args:
        e: Exception to check
        
    Returns:
        bool: True if the exception indicates rate limiting
    """
    error_str = str(e).lower()
    return any(keyword in error_str for keyword in [
        'rate limit', 'throttl', 'too many requests', '429',
        'quota exceeded', 'limit exceeded'
    ])


def is_provider_error(e: Exception) -> bool:
    """
    Check if an exception represents a provider-specific error that should be retried.
    
    Args:
        e: Exception to check
        
    Returns:
        bool: True if the exception should trigger a retry
    """
    return (
        isinstance(e, ProviderEmptyDataError) or
        is_network_error(e) or
        is_rate_limit_error(e)
    ) 