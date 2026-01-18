import hashlib
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Any
import sys
import os

# Force UTF-8 encoding for Windows console
try:
    from console_utils import setup_console
    setup_console()
except ImportError:
    if sys.platform == 'win32':
        os.system('chcp 65001 > nul 2>&1')
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')

class SmartCache:
    """Intelligent caching to reduce API calls"""
    
    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
    
    def get(self, key: str, max_age_minutes: int = 60) -> Optional[Any]:
        """Get cached data if fresh enough"""
        cache_file = self._get_path(key)
        
        if not cache_file.exists():
            return None
        
        try:
            data = json.loads(cache_file.read_text(encoding='utf-8'))
            cached_time = datetime.fromisoformat(data['timestamp'])
            
            if datetime.now() - cached_time < timedelta(minutes=max_age_minutes):
                print(f"[CACHE] Cache Hit: {key[:20]}...")
                return data['content']
            
        except Exception as e:
            print(f"[WARN] Cache read error: {e}")
            
        return None
    
    def set(self, key: str, content: Any):
        """Cache data with timestamp"""
        cache_file = self._get_path(key)
        try:
            cache_file.write_text(json.dumps({
                'timestamp': datetime.now().isoformat(),
                'content': content
            }, ensure_ascii=False, indent=2), encoding='utf-8')
        except Exception as e:
            print(f"[WARN] Cache write error: {e}")
    
    def _hash(self, key: str) -> str:
        return hashlib.md5(key.encode()).hexdigest()

    def _get_path(self, key: str) -> Path:
        return self.cache_dir / f"{self._hash(key)}.json"

if __name__ == "__main__":
    # Test
    c = SmartCache()
    c.set("test_key", {"data": "This is a cache test"})
    print(c.get("test_key"))
