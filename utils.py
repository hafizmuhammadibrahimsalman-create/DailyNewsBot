#!/usr/bin/env python3
"""
DailyNewsBot - Utility Functions
=================================
Common utilities including retry logic, error handling, and helpers.
"""

import time
import logging
from functools import wraps
from typing import Callable, Any, Optional, Type, Tuple

logger = logging.getLogger(__name__)


# =============================================================================
# RETRY LOGIC
# =============================================================================

def retry_with_backoff(
    retries: int = 3,
    backoff_in_seconds: float = 1,
    max_backoff: float = 60,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
) -> Callable:
    """
    Decorator for retrying failed operations with exponential backoff.
    
    Args:
        retries: Maximum number of retry attempts
        backoff_in_seconds: Initial backoff time
        max_backoff: Maximum backoff time
        exceptions: Tuple of exceptions to catch and retry
    
    Example:
        @retry_with_backoff(retries=3, backoff_in_seconds=2)
        def flaky_api_call():
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            attempt = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    attempt += 1
                    if attempt > retries:
                        logger.error(f"[FAIL] {func.__name__} failed after {retries} retries: {e}")
                        raise
                    
                    wait = min(backoff_in_seconds * (2 ** (attempt - 1)), max_backoff)
                    logger.warning(f"[RETRY] {func.__name__} attempt {attempt}/{retries} failed: {e}. Waiting {wait:.1f}s")
                    time.sleep(wait)
        return wrapper
    return decorator


# =============================================================================
# ERROR HANDLING
# =============================================================================

def handle_errors(
    default: Any = None,
    log_error: bool = True,
    reraise: bool = False
) -> Callable:
    """
    Decorator for consistent error handling.
    
    Args:
        default: Default value to return on error
        log_error: Whether to log the error
        reraise: Whether to re-raise the exception
    
    Example:
        @handle_errors(default={}, log_error=True)
        def risky_function():
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if log_error:
                    logger.error(f"[ERR] Error in {func.__name__}: {e}", exc_info=True)
                if reraise:
                    raise
                return default
        return wrapper
    return decorator


def safe_execute(func: Callable, *args, default: Any = None, **kwargs) -> Any:
    """
    Safely execute a function and return default on error.
    
    Args:
        func: Function to execute
        *args: Positional arguments
        default: Default value on error
        **kwargs: Keyword arguments
    
    Returns:
        Function result or default value
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logger.debug(f"safe_execute caught: {e}")
        return default


# =============================================================================
# TEXT UTILITIES
# =============================================================================

def sanitize_text(text: str) -> str:
    """
    Sanitize text by removing/replacing problematic characters.
    
    Args:
        text: Input text
    
    Returns:
        Sanitized text safe for console and file output
    """
    if not text:
        return text
    
    # Fix common mojibake patterns
    fixes = {
        'â€™': "'", 'â€˜': "'", 'â€œ': '"', 'â€': '"',
        'â€"': '-', 'â€"': '-', 'â€¦': '...', 'Â': '',
        '\u2018': "'", '\u2019': "'", '\u201c': '"', '\u201d': '"',
        '\u2013': '-', '\u2014': '-', '\u2026': '...',
    }
    for bad, good in fixes.items():
        text = text.replace(bad, good)
    
    # Remove remaining non-ASCII
    return text.encode('ascii', errors='ignore').decode('ascii')


def truncate(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate text to max length with suffix."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def validate_phone_number(number: str) -> str:
    """
    Validate and normalize phone number.
    
    Args:
        number: Phone number string
    
    Returns:
        Normalized phone number
    
    Raises:
        ValueError: If number is invalid
    """
    import re
    
    if not number:
        raise ValueError("Phone number is required")
    
    # Remove common formatting
    clean = re.sub(r'[\s\-\(\)]', '', number)
    
    # Check format
    if not re.match(r'^\+?[1-9]\d{9,14}$', clean):
        raise ValueError(f"Invalid phone number format: {number}")
    
    # Ensure + prefix
    if not clean.startswith('+'):
        clean = '+' + clean
    
    return clean


# =============================================================================
# TIMING UTILITIES
# =============================================================================

class Timer:
    """Context manager for timing operations."""
    
    def __init__(self, name: str = "Operation"):
        self.name = name
        self.start_time: Optional[float] = None
        self.elapsed: float = 0
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, *args):
        self.elapsed = time.time() - self.start_time
        logger.info(f"[TIME] {self.name} took {self.elapsed:.2f}s")


if __name__ == "__main__":
    # Test utilities
    print("Testing utilities...")
    
    # Test retry
    @retry_with_backoff(retries=2, backoff_in_seconds=0.1)
    def flaky():
        import random
        if random.random() < 0.7:
            raise ValueError("Random failure")
        return "Success!"
    
    try:
        result = flaky()
        print(f"Retry test: {result}")
    except ValueError:
        print("Retry test: Failed after retries (expected)")
    
    # Test timer
    with Timer("Sleep test"):
        time.sleep(0.1)
    
    # Test sanitize
    dirty = "Test â€™ text â€" with issues"
    clean = sanitize_text(dirty)
    print(f"Sanitize: '{dirty}' -> '{clean}'")
    
    print("Done!")
