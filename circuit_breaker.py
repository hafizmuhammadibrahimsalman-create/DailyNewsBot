import time
import logging
from functools import wraps
from typing import Callable, Any

logger = logging.getLogger(__name__)

class CircuitBreakerOpenException(Exception):
    pass

class CircuitBreaker:
    """
    Implements the Circuit Breaker pattern to prevent cascading failures.
    State machine: CLOSED (Normal) -> OPEN (Failing) -> HALF-OPEN (Testing)
    """
    
    def __init__(self, failure_threshold: int = 3, recovery_timeout: int = 60, name: str = "Service"):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.name = name
        
        self.failures = 0
        self.state = "CLOSED"
        self.last_failure_time = 0
        
    def __call__(self, func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            if self.state == "OPEN":
                if time.time() - self.last_failure_time > self.recovery_timeout:
                    self.state = "HALF-OPEN"
                    logger.info(f"[TEST] Circuit {self.name} is HALF-OPEN (Testing...)")
                else:
                    logger.warning(f"[BLOCKED] Circuit {self.name} is OPEN. Call blocked.")
                    raise CircuitBreakerOpenException(f"Circuit {self.name} is open")
            
            try:
                result = func(*args, **kwargs)
                if self.state == "HALF-OPEN":
                    self.state = "CLOSED"
                    self.failures = 0
                    logger.info(f"[OK] Circuit {self.name} recovered and CLOSED.")
                return result
                
            except Exception as e:
                self.failures += 1
                self.last_failure_time = time.time()
                logger.error(f"[ERR] call failed ({self.failures}/{self.failure_threshold}): {e}")
                
                if self.failures >= self.failure_threshold:
                    self.state = "OPEN"
                    logger.error(f"[TRIP] Circuit {self.name} tripped to OPEN!")
                
                raise e
                
        return wrapper

# Simple registry
breakers = {}

def circuit(name: str, threshold: int = 3, timeout: int = 60):
    if name not in breakers:
        breakers[name] = CircuitBreaker(threshold, timeout, name)
    return breakers[name]

if __name__ == "__main__":
    # Test
    @circuit("test_api", threshold=2, timeout=5)
    def flaky_api(succeed):
        if not succeed: raise ValueError("API Error")
        return "Success"

    print("1. Success call:", flaky_api(True))
    try: print("2. Fail call:", flaky_api(False)) 
    except: pass
    try: print("3. Fail call:", flaky_api(False)) 
    except: pass
    try: print("4. Blocked call:", flaky_api(True)) 
    except Exception as e: print(f"4. Blocked: {e}")
    
    time.sleep(6)
    print("5. Recovery call:", flaky_api(True))
