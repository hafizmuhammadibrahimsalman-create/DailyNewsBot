#!/usr/bin/env python3
"""
DailyNewsBot - Health Check System
===================================
Comprehensive system health verification.
"""

import logging
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
import json

logger = logging.getLogger(__name__)


class HealthCheck:
    """System health verification."""
    
    def __init__(self, cache_dir: str = "cache", log_dir: str = "logs"):
        self.cache_dir = Path(cache_dir)
        self.log_dir = Path(log_dir)
        self.checks: Dict[str, Any] = {}
    
    def check_api_keys(self) -> Dict[str, bool]:
        """Verify API keys are configured."""
        import os
        from dotenv import load_dotenv
        load_dotenv()
        
        gemini_key = os.getenv("GEMINI_API_KEY", "")
        whatsapp = os.getenv("WHATSAPP_NUMBER", "")
        
        result = {
            'gemini_key': bool(gemini_key and len(gemini_key) > 20 and "YOUR_" not in gemini_key),
            'whatsapp_number': bool(whatsapp and len(whatsapp) > 8),
            'is_ok': True
        }
        result['is_ok'] = result['gemini_key'] and result['whatsapp_number']
        
        self.checks['api_keys'] = result
        return result
    
    def check_directories(self) -> Dict[str, Any]:
        """Verify required directories exist."""
        self.cache_dir.mkdir(exist_ok=True)
        self.log_dir.mkdir(exist_ok=True)
        (self.log_dir / "health_reports").mkdir(exist_ok=True)
        
        result = {
            'cache_dir': self.cache_dir.exists(),
            'log_dir': self.log_dir.exists(),
            'is_ok': True
        }
        result['is_ok'] = result['cache_dir'] and result['log_dir']
        
        self.checks['directories'] = result
        return result
    
    def check_disk_space(self) -> Dict[str, Any]:
        """Check available disk space."""
        stat = shutil.disk_usage(self.cache_dir)
        free_gb = stat.free / (1024 ** 3)
        
        result = {
            'free_space_gb': round(free_gb, 2),
            'total_space_gb': round(stat.total / (1024 ** 3), 2),
            'is_ok': free_gb > 0.5  # At least 500MB free
        }
        
        self.checks['disk_space'] = result
        return result
    
    def check_network(self) -> Dict[str, Any]:
        """Check network connectivity."""
        import socket
        import time
        
        result = {'is_ok': False, 'latency_ms': None}
        
        try:
            start = time.time()
            socket.create_connection(("8.8.8.8", 53), timeout=5)
            latency = (time.time() - start) * 1000
            
            result['is_ok'] = True
            result['latency_ms'] = round(latency, 2)
        except (socket.timeout, OSError) as e:
            result['error'] = str(e)
        
        self.checks['network'] = result
        return result
    
    def check_dependencies(self) -> Dict[str, Any]:
        """Check if required packages are installed."""
        required = ['google.generativeai', 'pywhatkit', 'feedparser', 'requests', 'dotenv']
        
        results = {}
        for pkg in required:
            try:
                __import__(pkg.replace('.', '_') if '.' in pkg else pkg)
                results[pkg] = True
            except ImportError:
                results[pkg] = False
        
        result = {
            'packages': results,
            'is_ok': all(results.values())
        }
        
        self.checks['dependencies'] = result
        return result
    
    def run_all(self) -> Dict[str, Any]:
        """Run all health checks."""
        logger.info("[>>] Running health checks...")
        
        self.check_api_keys()
        self.check_directories()
        self.check_disk_space()
        self.check_network()
        self.check_dependencies()
        
        # Summary
        all_ok = all(
            v.get('is_ok', True) 
            for v in self.checks.values()
            if isinstance(v, dict)
        )
        
        self.checks['summary'] = {
            'timestamp': datetime.now().isoformat(),
            'all_ok': all_ok,
        }
        
        # Save report
        self._save_report()
        
        if all_ok:
            logger.info("[OK] All health checks passed")
        else:
            logger.warning("[WARN] Some health checks failed")
        
        return self.checks
    
    def _save_report(self):
        """Save health report to file."""
        try:
            report_path = self.log_dir / "health_reports"
            report_path.mkdir(parents=True, exist_ok=True)
            
            filename = f"health_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_path / filename, 'w', encoding='utf-8') as f:
                json.dump(self.checks, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save health report: {e}")
    
    def print_summary(self):
        """Print health check summary to console."""
        print("\n" + "=" * 50)
        print("HEALTH CHECK SUMMARY")
        print("=" * 50)
        
        for check_name, check_result in self.checks.items():
            if check_name == 'summary':
                continue
            
            if isinstance(check_result, dict):
                status = "[OK]" if check_result.get('is_ok') else "[FAIL]"
                print(f"{status} {check_name}")
        
        print("=" * 50)
        if self.checks.get('summary', {}).get('all_ok'):
            print("RESULT: ALL CHECKS PASSED")
        else:
            print("RESULT: SOME CHECKS FAILED")
        print("=" * 50 + "\n")


if __name__ == "__main__":
    health = HealthCheck()
    health.run_all()
    health.print_summary()
