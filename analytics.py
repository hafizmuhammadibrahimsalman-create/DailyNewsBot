import json
import time
from pathlib import Path
from datetime import datetime, timedelta

STATS_FILE = "stats.json"

class Analytics:
    """Tracks system usage and performance metrics."""
    
    @staticmethod
    def load_stats():
        if Path(STATS_FILE).exists():
            try:
                return json.loads(Path(STATS_FILE).read_text())
            except:
                pass
        return {
            "total_runs": 0,
            "total_errors": 0,
            "api_calls": 0,
            "last_run": None,
            "history": [] 
        }

    @staticmethod
    def log_run(duration_sec: float, success: bool, articles_count: int):
        stats = Analytics.load_stats()
        stats["total_runs"] += 1
        if not success:
            stats["total_errors"] += 1
        
        stats["last_run"] = datetime.now().isoformat()
        
        # Add to history (keep last 50)
        entry = {
            "timestamp": datetime.now().isoformat(),
            "duration": round(duration_sec, 2),
            "success": success,
            "articles": articles_count
        }
        stats["history"].insert(0, entry)
        stats["history"] = stats["history"][:50]
        
        try:
            Path(STATS_FILE).write_text(json.dumps(stats, indent=2))
        except Exception as e:
            print(f"[WARN] Failed to save analytics: {e}")

    @staticmethod
    def log_api_call(service: str):
        stats = Analytics.load_stats()
        stats["api_calls"] += 1
        # Could track per-service here too
        Path(STATS_FILE).write_text(json.dumps(stats, indent=2))

if __name__ == "__main__":
    # Test
    Analytics.log_run(5.5, True, 120)
    print("Logged test run.")
