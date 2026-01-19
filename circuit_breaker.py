#!/usr/bin/env python3
"""
DailyNewsBot - Circuit Breaker
===============================
Implements the Circuit Breaker pattern for API resilience.
Thread-safe implementation for concurrent usage.
"""

import time
import logging
import threading
from functools import wraps
from typing import Callable, Any

logger = logging.getLogger(__name__)


class CircuitBreakerOpenException(Exception):
    """Raised when circuit is open and call is blocked."""
    pass


class CircuitBreaker:
    """
    Thread-safe Circuit Breaker pattern implementation.
    
    State machine:
        CLOSED (Normal) -> OPEN (Failing) -> HALF-OPEN (Testing) -> CLOSED
    """
    
    def __init__(self, failure_threshold: int = 3, recovery_timeout: int = 60, name: str = "Service"):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.name = name
        
        # State (protected by lock)
        self._lock = threading.Lock()
        self.failures = 0
        self.state = "CLOSED"
        self.last_failure_time = 0
    
    def _should_attempt_recovery(self) -> bool:
        """Check if enough time has passed to attempt recovery."""
        return time.time() - self.last_failure_time > self.recovery_timeout
    
    def record_success(self):
        """Record a successful call (thread-safe)."""
        with self._lock:
            if self.state == "HALF-OPEN":
                self.state = "CLOSED"
                self.failures = 0
                logger.info(f"[OK] Circuit {self.name} recovered - now CLOSED")
    
    def record_failure(self):
        """Record a failed call (thread-safe)."""
        with self._lock:
            self.failures += 1
            self.last_failure_time = time.time()
            
            if self.failures >= self.failure_threshold:
                self.state = "OPEN"
                logger.error(f"[TRIP] Circuit {self.name} tripped to OPEN!")
    
    def is_open(self) -> bool:
        """Check if circuit is open (thread-safe)."""
        with self._lock:
            return self.state == "OPEN"
    
    def __call__(self, func: Callable) -> Callable:
        """Decorator to apply circuit breaker to a function."""
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Check circuit state
            with self._lock:
                if self.state == "OPEN":
                    if self._should_attempt_recovery():
                        self.state = "HALF-OPEN"
                        logger.info(f"[TEST] Circuit {self.name} is HALF-OPEN (Testing...)")
                    else:
                        logger.warning(f"[BLOCKED] Circuit {self.name} is OPEN. Call blocked.")
                        raise CircuitBreakerOpenException(f"Circuit {self.name} is open")
            
            # Execute function
            try:
                result = func(*args, **kwargs)
                self.record_success()
                return result
                
            except Exception as e:
                with self._lock:
                    self.failures += 1
                    self.last_failure_time = time.time()
                    logger.error(f"[ERR] {self.name} call failed ({self.failures}/{self.failure_threshold}): {e}")
                    
                    if self.failures >= self.failure_threshold:
                        self.state = "OPEN"
                        logger.error(f"[TRIP] Circuit {self.name} tripped to OPEN!")
                
                raise
        
        return wrapper


# Global registry for circuit breakers
_breakers: dict = {}
_registry_lock = threading.Lock()


def circuit(name: str, threshold: int = 3, timeout: int = 60) -> CircuitBreaker:
    """
    Get or create a circuit breaker (thread-safe registry).
    
    Args:
        name: Unique name for this circuit
        threshold: Number of failures before opening
        timeout: Seconds before attempting recovery
    
    Returns:
        CircuitBreaker instance (can be used as decorator)
    """
    with _registry_lock:
        if name not in _breakers:
            _breakers[name] = CircuitBreaker(threshold, timeout, name)
        return _breakers[name]


def get_circuit_status() -> dict:
    """Get status of all circuits."""
    with _registry_lock:
        return {
            name: {
                'state': cb.state,
                'failures': cb.failures,
                'threshold': cb.failure_threshold
            }
            for name, cb in _breakers.items()
        }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test circuit breaker
    @circuit("test_api", threshold=2, timeout=5)
    def flaky_api(succeed: bool):
        if not succeed:
            raise ValueError("API Error")
        return "Success"

    print("1. Success call:", flaky_api(True))
    
    try:
        print("2. Fail call:", flaky_api(False))
    except ValueError:
        pass
    
    try:
        print("3. Fail call:", flaky_api(False))
    except ValueError:
        pass
    
    try:
        print("4. Blocked call:", flaky_api(True))
    except CircuitBreakerOpenException as e:
        print(f"4. Blocked: {e}")
    
    print("\nWaiting for recovery...")
    time.sleep(6)
    
    print("5. Recovery call:", flaky_api(True))
    print("\nCircuit status:", get_circuit_status())
