#!/usr/bin/env python3
"""
DailyNewsBot - Rate Limiter
============================
Prevents API rate limit violations with token bucket algorithm.
"""

from time import sleep, time
from collections import deque
from functools import wraps
from typing import Callable, Any
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    """Token bucket rate limiter with sliding window."""
    
    def __init__(self, max_calls: int, period: float):
        """
        Initialize rate limiter.
        
        Args:
            max_calls: Maximum calls allowed in the period
            period: Time window in seconds
        """
        self.max_calls = max_calls
        self.period = period
        self.calls: deque = deque()
    
    def acquire(self) -> float:
        """
        Acquire permission to make a call.
        
        Returns:
            Wait time in seconds (0 if no wait needed)
        """
        now = time()
        
        # Remove expired calls
        while self.calls and self.calls[0] < now - self.period:
            self.calls.popleft()
        
        # Check if we need to wait
        if len(self.calls) >= self.max_calls:
            wait_time = self.period - (now - self.calls[0])
            if wait_time > 0:
                return wait_time
        
        self.calls.append(now)
        return 0
    
    def __call__(self, func: Callable) -> Callable:
        """Decorator for rate-limited functions."""
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            wait_time = self.acquire()
            if wait_time > 0:
                logger.debug(f"[RATE] Waiting {wait_time:.2f}s before {func.__name__}")
                sleep(wait_time)
                self.calls.append(time())
            return func(*args, **kwargs)
        return wrapper


# Pre-configured rate limiters for common APIs
gemini_limiter = RateLimiter(max_calls=60, period=60)  # 60 calls/minute
newsapi_limiter = RateLimiter(max_calls=100, period=86400)  # 100 calls/day (free tier)
gnews_limiter = RateLimiter(max_calls=100, period=86400)  # 100 calls/day


def rate_limited(max_calls: int, period: float):
    """
    Decorator factory for rate limiting.
    
    Args:
        max_calls: Maximum calls allowed
        period: Time period in seconds
    
    Example:
        @rate_limited(10, 60)  # 10 calls per minute
        def my_api_call():
            pass
    """
    limiter = RateLimiter(max_calls, period)
    return limiter


if __name__ == "__main__":
    # Test rate limiter
    import time as t
    
    @rate_limited(3, 5)  # 3 calls per 5 seconds
    def test_call():
        print(f"Called at {t.time():.2f}")
    
    print("Testing rate limiter (3 calls/5 seconds):")
    for i in range(6):
        test_call()
    print("Done!")
