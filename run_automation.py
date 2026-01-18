#!/usr/bin/env python3
"""
DailyNewsBot - Enhanced Automation Controller
==============================================
Production-ready system with comprehensive logging, 
component health checks, and robust error handling.

Author: Muhammad Ibrahim Salman
Version: 2.0
"""

import sys
import os
import time
import argparse
import logging
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List
from logging.handlers import RotatingFileHandler

# Project root setup
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# Console encoding fix for Windows
try:
    from console_utils import setup_console
    setup_console()
except ImportError:
    if sys.platform == 'win32':
        os.system('chcp 65001 > nul 2>&1')
        try:
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
        except: pass


def setup_logging(log_dir: str = "logs") -> logging.Logger:
    """Setup comprehensive logging with file rotation."""
    Path(log_dir).mkdir(exist_ok=True)
    
    logger = logging.getLogger("AutomationMaster")
    logger.setLevel(logging.DEBUG)
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # File handler with rotation (10MB max, 5 backups)
    file_handler = RotatingFileHandler(
        f"{log_dir}/automation.log",
        maxBytes=10*1024*1024,
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


class NewsAutomationController:
    """Main controller for the DailyNewsBot automation system."""
    
    def __init__(self, dry_run: bool = False, json_output: bool = False):
        self.dry_run = dry_run
        self.json_output = json_output
        self.logger = setup_logging()
        self.stats = {
            "start_time": datetime.now().isoformat(),
            "mode": "dry_run" if dry_run else "live",
            "articles_fetched": 0,
            "articles_processed": 0,
            "messages_sent": 0,
            "steps": {},
            "errors": []
        }
        
    # =========================================================================
    # HEALTH CHECKS
    # =========================================================================
    
    def health_check(self) -> Dict[str, Any]:
        """Run comprehensive system health check with component status."""
        self.logger.info("=" * 60)
        self.logger.info("[>>] SYSTEM HEALTH CHECK")
        self.logger.info("=" * 60)
        
        health_status = {
            "timestamp": datetime.now().isoformat(),
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}",
            "environment": {},
            "components": {},
            "overall": True
        }
        
        # 1. Python version check
        if sys.version_info < (3, 8):
            self.logger.error("[ERR] Python 3.8+ required")
            health_status["overall"] = False
        else:
            self.logger.info(f"[OK] Python {sys.version_info.major}.{sys.version_info.minor}")
        
        # 2. Network check
        health_status["components"]["network"] = self._check_network()
        
        # 3. Environment variables
        health_status["environment"] = self._check_environment()
        
        # 4. Component checks
        components = [
            ("news_fetcher", self._check_news_fetcher),
            ("ai_summarizer", self._check_ai_summarizer),
            ("whatsapp_sender", self._check_whatsapp_sender),
            ("smart_cache", self._check_cache),
            ("circuit_breaker", self._check_circuit_breaker),
            ("dashboard_generator", self._check_dashboard),
        ]
        
        for name, check_func in components:
            try:
                status, message = check_func()
                health_status["components"][name] = {"status": status, "message": message}
                log_func = self.logger.info if status else self.logger.warning
                log_func(f"[{'OK' if status else 'WARN'}] {name}: {message}")
            except Exception as e:
                health_status["components"][name] = {"status": False, "message": str(e)}
                self.logger.error(f"[ERR] {name}: {e}")
        
        # Calculate overall health
        env_ok = health_status["environment"].get("WHATSAPP_NUMBER", False) and \
                 health_status["environment"].get("GEMINI_API_KEY", False)
        components_ok = all(c.get("status", False) for c in health_status["components"].values() 
                          if isinstance(c, dict))
        health_status["overall"] = env_ok and health_status["components"]["network"]
        
        # Log summary
        self.logger.info("=" * 60)
        if health_status["overall"]:
            self.logger.info("[OK] SYSTEM HEALTHY - Ready to run")
        else:
            self.logger.warning("[WARN] SYSTEM HAS ISSUES - Review above errors")
        self.logger.info("=" * 60)
        
        # Save health report
        self._save_health_report(health_status)
        
        return health_status
    
    def _check_network(self) -> bool:
        """Check internet connectivity."""
        import socket
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            self.logger.info("[OK] Network connected")
            return True
        except OSError:
            self.logger.error("[ERR] No internet connection")
            return False
    
    def _check_environment(self) -> Dict[str, bool]:
        """Verify environment configuration."""
        from dotenv import load_dotenv
        load_dotenv()
        
        required = ['WHATSAPP_NUMBER', 'GEMINI_API_KEY']
        optional = ['NEWS_API_KEY', 'GNEWS_API_KEY']
        
        status = {}
        for var in required:
            value = os.getenv(var, '')
            is_valid = bool(value) and 'YOUR_' not in value
            status[var] = is_valid
            if is_valid:
                self.logger.info(f"[OK] {var} configured")
            else:
                self.logger.error(f"[ERR] {var} missing or placeholder")
        
        for var in optional:
            value = os.getenv(var, '')
            is_valid = bool(value) and 'YOUR_' not in value
            status[var] = is_valid
            if is_valid:
                self.logger.info(f"[OK] {var} configured")
            else:
                self.logger.info(f"[INFO] {var} not configured (optional)")
        
        return status
    
    def _check_news_fetcher(self):
        from news_fetcher import NewsFetcher
        NewsFetcher()
        return True, "Module loaded"
    
    def _check_ai_summarizer(self):
        from ai_summarizer import GeminiSummarizer
        summarizer = GeminiSummarizer()
        return summarizer.enabled, "Gemini API ready" if summarizer.enabled else "API key issue"
    
    def _check_whatsapp_sender(self):
        from whatsapp_sender import WhatsAppSender
        sender = WhatsAppSender()
        return bool(sender.phone_number), f"Target: {sender.phone_number}"
    
    def _check_cache(self):
        from smart_cache import SmartCache
        SmartCache()
        return True, "Cache initialized"
    
    def _check_circuit_breaker(self):
        from circuit_breaker import CircuitBreaker
        return True, "Circuit breaker ready"
    
    def _check_dashboard(self):
        from dashboard_generator import DashboardGenerator
        return True, "Dashboard generator ready"
    
    def _save_health_report(self, health_status: Dict[str, Any]):
        """Save health report to JSON file."""
        try:
            report_path = PROJECT_ROOT / "logs" / "health_reports"
            report_path.mkdir(parents=True, exist_ok=True)
            
            filename = f"health_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_path / filename, 'w', encoding='utf-8') as f:
                json.dump(health_status, f, indent=2)
            
            self.logger.debug(f"Health report saved: {filename}")
        except Exception as e:
            self.logger.error(f"Failed to save health report: {e}")
    
    # =========================================================================
    # MAIN AUTOMATION
    # =========================================================================
    
    def run_full_cycle(self) -> Dict[str, Any]:
        """Execute the complete automation workflow."""
        start_time = time.time()
        
        self.logger.info("=" * 60)
        self.logger.info(f"[>>] STARTING FULL AUTOMATION CYCLE")
        self.logger.info(f"     Mode: {'DRY RUN' if self.dry_run else 'LIVE'}")
        self.logger.info("=" * 60)
        
        try:
            # Step 1: Health Check
            health = self.health_check()
            self.stats["steps"]["health"] = health["overall"]
            
            if not health["overall"]:
                self.stats["success"] = False
                self.stats["error"] = "Health check failed"
                return self.stats
            
            # Step 2: Fetch News
            self.logger.info("[>>] Fetching news...")
            all_news = self._fetch_news()
            total_articles = sum(len(v) for v in all_news.values())
            self.stats["articles_fetched"] = total_articles
            self.stats["steps"]["fetch"] = {"articles": total_articles}
            
            if total_articles == 0:
                self.logger.warning("[WARN] No articles fetched")
            
            # Step 3: Deduplicate
            all_news = self._deduplicate_news(all_news)
            
            # Step 4: Summarize
            self.logger.info("[>>] Generating AI summary...")
            report = self._summarize_news(all_news)
            self.stats["steps"]["summarize"] = bool(report)
            
            if not report:
                self.stats["success"] = False
                self.stats["error"] = "Summarization failed"
                return self.stats
            
            self.logger.info(f"[OK] Report generated ({len(report)} chars)")
            
            # Step 5: Send
            send_success = self._send_message(report)
            self.stats["steps"]["send"] = send_success
            self.stats["messages_sent"] = 1 if send_success and not self.dry_run else 0
            
            # Step 6: Dashboard
            self._generate_dashboard()
            
            # Final stats
            elapsed = time.time() - start_time
            self.stats["elapsed_seconds"] = round(elapsed, 2)
            self.stats["success"] = True
            
            self.logger.info("=" * 60)
            self.logger.info(f"[OK] CYCLE COMPLETE in {elapsed:.1f}s")
            self.logger.info("=" * 60)
            
            # Save run stats
            self._save_run_stats()
            
            if self.json_output:
                print(json.dumps(self.stats, indent=2))
            
            return self.stats
            
        except KeyboardInterrupt:
            self.logger.info("[STOP] Interrupted by user")
            self.stats["success"] = False
            self.stats["error"] = "User interrupted"
            return self.stats
        except Exception as e:
            self.logger.exception(f"[FATAL] Fatal error: {e}")
            self.stats["success"] = False
            self.stats["error"] = str(e)
            self.stats["errors"].append(str(e))
            return self.stats
    
    def _fetch_news(self) -> Dict[str, List[Dict]]:
        """Fetch news from all sources."""
        from news_fetcher import NewsFetcher
        fetcher = NewsFetcher()
        return fetcher.fetch_all_news()
    
    def _deduplicate_news(self, all_news: Dict) -> Dict:
        """Remove duplicate articles."""
        try:
            from news_clustering import NewsClusterer
            clusterer = NewsClusterer(similarity_threshold=0.65)
            return clusterer.cluster_news(all_news)
        except Exception as e:
            self.logger.warning(f"[WARN] Deduplication failed: {e}")
            return all_news
    
    def _summarize_news(self, all_news: Dict) -> Optional[str]:
        """Summarize news using AI."""
        try:
            from ai_summarizer import GeminiSummarizer
            summarizer = GeminiSummarizer()
            
            # Filter by topic
            filtered = {}
            for topic, articles in all_news.items():
                if articles:
                    filtered[topic] = summarizer.filter_relevant_news(articles, topic)
            
            return summarizer.create_intelligence_report(filtered)
        except Exception as e:
            self.logger.error(f"[ERR] Summarization failed: {e}")
            return None
    
    def _send_message(self, message: str) -> bool:
        """Send message via WhatsApp."""
        if self.dry_run:
            self.logger.info("[DRY] DRY RUN - Message not sent")
            self.logger.info(f"Preview ({len(message)} chars):\n{message[:500]}...")
            return True
        
        self.logger.info("[>>] Sending via WhatsApp...")
        try:
            from whatsapp_sender import WhatsAppSender
            sender = WhatsAppSender()
            success = sender.send_message(message)
            if success:
                self.logger.info("[OK] Message sent successfully")
            else:
                self.logger.warning("[WARN] Send command issued but verify delivery")
            return success
        except Exception as e:
            self.logger.error(f"[ERR] Send failed: {e}")
            return False
    
    def _generate_dashboard(self):
        """Generate analytics dashboard."""
        try:
            from dashboard_generator import DashboardGenerator
            dash = DashboardGenerator()
            dash_path = dash.generate()
            self.logger.info(f"[OK] Dashboard updated: {dash_path}")
            self.stats["dashboard"] = str(dash_path)
        except Exception as e:
            self.logger.error(f"[WARN] Dashboard generation failed: {e}")
    
    def _save_run_stats(self):
        """Save run statistics to JSON file."""
        try:
            stats_file = PROJECT_ROOT / "logs" / "run_stats.json"
            stats_file.parent.mkdir(exist_ok=True)
            
            # Load existing stats
            if stats_file.exists():
                with open(stats_file, encoding='utf-8') as f:
                    all_stats = json.load(f)
            else:
                all_stats = []
            
            # Keep last 100 runs
            all_stats.append(self.stats)
            all_stats = all_stats[-100:]
            
            # Save
            with open(stats_file, 'w', encoding='utf-8') as f:
                json.dump(all_stats, f, indent=2)
            
            self.logger.debug("Run stats saved")
        except Exception as e:
            self.logger.error(f"Failed to save stats: {e}")


# =============================================================================
# CLI INTERFACE
# =============================================================================

def main():
    """Main entry point with argument parsing."""
    parser = argparse.ArgumentParser(
        description='DailyNewsBot - Enhanced Automation Controller',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_automation.py --health      # Run comprehensive health check
  python run_automation.py --dry-run     # Test without sending messages
  python run_automation.py --run         # Execute live automation
  python run_automation.py --dashboard   # Generate dashboard only
  python run_automation.py --run --json  # Live run with JSON output
        """
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--health', action='store_true', help='Run system health check')
    group.add_argument('--dry-run', action='store_true', help='Test run without sending')
    group.add_argument('--run', action='store_true', help='Execute live automation')
    group.add_argument('--dashboard', action='store_true', help='Generate dashboard only')
    
    parser.add_argument('--json', action='store_true', help='Output results as JSON')
    
    args = parser.parse_args()
    
    try:
        if args.dashboard:
            from dashboard_generator import DashboardGenerator
            path = DashboardGenerator().generate()
            print(f"[OK] Dashboard generated: {path}")
            return 0
        
        controller = NewsAutomationController(
            dry_run=args.dry_run,
            json_output=args.json
        )
        
        if args.health:
            result = controller.health_check()
            return 0 if result['overall'] else 1
        
        if args.dry_run or args.run:
            result = controller.run_full_cycle()
            return 0 if result.get('success') else 1
        
    except KeyboardInterrupt:
        print("\n[STOP] Interrupted by user")
        return 130
    except Exception as e:
        print(f"[FATAL] Fatal error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
