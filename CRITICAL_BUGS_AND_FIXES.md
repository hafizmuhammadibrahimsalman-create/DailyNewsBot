# Critical Bugs and Fixes

This document details the 8 critical bugs found and fixed in DailyNewsBot.

---

## Bug #1: TOPICS Dataclass Access
**File:** `news_fetcher.py` | **Severity:** 🔴 CRITICAL

### Problem
Code accessed TOPICS dict values using `cfg['name']` but config uses dataclasses.

### Before
```python
for tid, cfg in TOPICS.items():
    logger.info(f"Fetching: {cfg['name']}")  # CRASH!
```

### After
```python
for tid, cfg in TOPICS.items():
    topic_name = cfg.name if hasattr(cfg, 'name') else cfg.get('name', tid)
    logger.info(f"Fetching: {topic_name}")
```

---

## Bug #2: logger.warn() Deprecated
**File:** Multiple files | **Severity:** 🔴 CRITICAL

### Problem
`logger.warn()` is deprecated and may not exist in all Python versions.

### Before
```python
logger.warn(f"NewsAPI: {e}")
```

### After
```python
logger.warning(f"NewsAPI: {e}")
```

---

## Bug #3: Silent Exception Handlers
**File:** `news_fetcher.py` | **Severity:** 🟠 MAJOR

### Problem
Empty `except: pass` blocks hide all errors, making debugging impossible.

### Before
```python
try:
    arts.extend(self._fetch_newsapi(cfg['keywords']))
except Exception: pass  # What error?
```

### After
```python
try:
    arts.extend(self._fetch_newsapi(keywords))
except Exception as e:
    logger.warning(f"NewsAPI error for {tid}: {e}")
```

---

## Bug #4: Unsafe API Key Validation
**File:** `ai_summarizer.py` | **Severity:** 🔴 CRITICAL

### Problem
API key checked for existence but not validity, causing runtime failures.

### Before
```python
self.api_key = os.getenv("GEMINI_API_KEY")
# Could be empty string, "YOUR_KEY_HERE", etc.
```

### After
```python
def _get_api_key(self, key_name: str) -> Optional[str]:
    key = SecureConfig.get_credential(key_name)
    if key and len(key) > 10 and "YOUR_" not in key:
        return key
    return None
```

---

## Bug #5: Missing Timeouts
**File:** `content_scraper.py` | **Severity:** 🟠 MAJOR

### Problem
`future.result()` called without timeout, can hang indefinitely.

### Before
```python
for future in future_to_url:
    results[url] = future.result()  # Hangs forever!
```

### After
```python
for future in future_to_url:
    try:
        results[url] = future.result(timeout=10)  # 10 second max
    except FuturesTimeoutError:
        logger.warning(f"Timeout waiting for {url}")
        results[url] = ""
```

---

## Bug #6: Race Conditions in Circuit Breaker
**File:** `circuit_breaker.py` | **Severity:** 🔴 CRITICAL

### Problem
State mutations not thread-safe, causing corruption under concurrent load.

### Before
```python
class CircuitBreaker:
    def __init__(self):
        self.failures = 0
        self.state = "CLOSED"
    
    def record_failure(self):
        self.failures += 1  # NOT THREAD SAFE!
```

### After
```python
import threading

class CircuitBreaker:
    def __init__(self):
        self._lock = threading.Lock()
        self.failures = 0
        self.state = "CLOSED"
    
    def record_failure(self):
        with self._lock:  # THREAD SAFE!
            self.failures += 1
```

---

## Bug #7: Missing Dependencies
**File:** `requirements.txt` | **Severity:** 🔴 CRITICAL

### Problem
Code imports packages not listed in requirements.txt.

### Added
```txt
schedule>=1.1.0      # Job scheduling
tenacity>=8.0.0      # Retry logic
colorlog>=6.0.0      # Colored logs
pytest>=7.4.0        # Testing
```

---

## Bug #8: No Environment Validation
**File:** `env_validator.py` (NEW) | **Severity:** 🟠 MAJOR

### Problem
No pre-flight checks for API keys, causing cryptic runtime errors.

### Solution
Created `env_validator.py` that checks:
- GEMINI_API_KEY format and length
- WHATSAPP_NUMBER validity
- Required directories exist
- Python version >= 3.8
- All dependencies installed

### Usage
```bash
python env_validator.py
```

---

## Summary

| # | Bug | File | Status |
|---|-----|------|--------|
| 1 | Dataclass access | news_fetcher.py | ✅ Fixed |
| 2 | logger.warn() | multiple | ✅ Fixed |
| 3 | Silent exceptions | news_fetcher.py | ✅ Fixed |
| 4 | API validation | ai_summarizer.py | ✅ Fixed |
| 5 | Missing timeouts | content_scraper.py | ✅ Fixed |
| 6 | Race conditions | circuit_breaker.py | ✅ Fixed |
| 7 | Missing deps | requirements.txt | ✅ Fixed |
| 8 | No env validation | env_validator.py | ✅ NEW |

---

## Verification

Run these commands to verify fixes:

```bash
# 1. Validate environment
python env_validator.py

# 2. Run health check
python run_automation.py --health

# 3. Test run (no sending)
python run_automation.py --dry-run

# 4. Run test suite
python test_suite.py
```
