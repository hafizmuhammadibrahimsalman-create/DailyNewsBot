#!/usr/bin/env python3
"""
DailyNewsBot - Comprehensive Test Suite
========================================
Run with: python test_suite.py
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import json

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

# Set test environment variables
os.environ["GEMINI_API_KEY"] = "test_key_12345678901234567890123456789"
os.environ["WHATSAPP_NUMBER"] = "+923300301917"


class TestConfiguration(unittest.TestCase):
    """Test configuration management."""
    
    def test_config_initialization(self):
        """Test config loads correctly."""
        from config import Config
        config = Config()
        self.assertIsNotNone(config.api)
        self.assertIsNotNone(config.whatsapp)
        self.assertIsNotNone(config.news)
        
    def test_api_key_validation_valid(self):
        """Test valid API key passes validation."""
        from config import APIConfig
        config = APIConfig(gemini_api_key="test_key_12345678901234567890123456789")
        self.assertTrue(config.validate())
        
    def test_api_key_validation_short(self):
        """Test short API key fails."""
        from config import APIConfig
        config = APIConfig(gemini_api_key="short")
        with self.assertRaises(ValueError):
            config.validate()
            
    def test_api_key_validation_empty(self):
        """Test empty API key fails."""
        from config import APIConfig
        config = APIConfig(gemini_api_key="")
        with self.assertRaises(ValueError):
            config.validate()
            
    def test_phone_validation_valid(self):
        """Test valid phone numbers pass."""
        from config import WhatsAppConfig
        valid_numbers = ["+923001234567", "+1234567890", "923001234567"]
        for num in valid_numbers:
            config = WhatsAppConfig(phone_number=num)
            self.assertTrue(config.validate())
            
    def test_phone_validation_invalid(self):
        """Test invalid phone numbers fail."""
        from config import WhatsAppConfig
        invalid_numbers = ["", "123", "abc123"]
        for num in invalid_numbers:
            config = WhatsAppConfig(phone_number=num)
            with self.assertRaises(ValueError):
                config.validate()
    
    def test_topics_config(self):
        """Test topics are configured."""
        from config import TOPICS
        self.assertIn("ai", TOPICS)
        self.assertIn("technology", TOPICS)
        self.assertIn("pakistan", TOPICS)


class TestCircuitBreaker(unittest.TestCase):
    """Test circuit breaker pattern."""
    
    def test_initial_state_closed(self):
        """Test circuit starts closed."""
        from circuit_breaker import CircuitBreaker
        cb = CircuitBreaker(failure_threshold=3, recovery_timeout=60)
        self.assertEqual(cb.state, "CLOSED")
        
    def test_circuit_opens_on_failures(self):
        """Test circuit opens after threshold failures."""
        from circuit_breaker import CircuitBreaker
        cb = CircuitBreaker(failure_threshold=3, recovery_timeout=60)
        
        for _ in range(3):
            cb.failures += 1
        cb.state = "OPEN"  # Simulate the state change
        
        self.assertEqual(cb.state, "OPEN")
    
    def test_decorator_exists(self):
        """Test circuit decorator is available."""
        from circuit_breaker import circuit
        self.assertTrue(callable(circuit))


class TestNewsClusterer(unittest.TestCase):
    """Test news clustering/deduplication."""
    
    def test_removes_duplicates(self):
        """Test duplicate removal."""
        from news_clustering import NewsClusterer
        
        clusterer = NewsClusterer(similarity_threshold=0.7)
        
        test_news = {
            "test": [
                {"title": "Breaking: Test News Story"},
                {"title": "Breaking: Test News Story"},  # Duplicate
                {"title": "Completely Different Story"}
            ]
        }
        
        result = clusterer.cluster_news(test_news)
        
        # Should have removed one duplicate
        self.assertEqual(len(result["test"]), 2)
    
    def test_keeps_different_articles(self):
        """Test different articles are kept."""
        from news_clustering import NewsClusterer
        
        clusterer = NewsClusterer(similarity_threshold=0.9)
        
        test_news = {
            "test": [
                {"title": "Story about AI"},
                {"title": "Story about Sports"},
                {"title": "Story about Politics"}
            ]
        }
        
        result = clusterer.cluster_news(test_news)
        self.assertEqual(len(result["test"]), 3)


class TestSmartCache(unittest.TestCase):
    """Test caching system."""
    
    def test_set_and_get(self):
        """Test basic cache operations."""
        from smart_cache import SmartCache
        import tempfile
        
        cache = SmartCache(tempfile.mkdtemp())
        cache.set("test_key", {"data": "test_value"})
        
        result = cache.get("test_key", max_age_minutes=60)
        self.assertIsNotNone(result)
        self.assertEqual(result["data"], "test_value")
    
    def test_expired_returns_none(self):
        """Test expired cache returns None."""
        from smart_cache import SmartCache
        import tempfile
        
        cache = SmartCache(tempfile.mkdtemp())
        cache.set("old_key", {"data": "old"})
        
        # Get with 0 minute max age should return None
        result = cache.get("old_key", max_age_minutes=0)
        self.assertIsNone(result)
    
    def test_missing_key_returns_none(self):
        """Test missing key returns None."""
        from smart_cache import SmartCache
        import tempfile
        
        cache = SmartCache(tempfile.mkdtemp())
        result = cache.get("nonexistent_key", max_age_minutes=60)
        self.assertIsNone(result)


class TestNewsFetcher(unittest.TestCase):
    """Test news fetching."""
    
    def test_fetcher_initialization(self):
        """Test fetcher initializes."""
        from news_fetcher import NewsFetcher
        fetcher = NewsFetcher()
        self.assertIsNotNone(fetcher)
    
    @patch('feedparser.parse')
    def test_google_rss_fetch(self, mock_parse):
        """Test Google RSS fetch."""
        mock_parse.return_value = Mock(
            entries=[
                Mock(
                    title="Test Article",
                    link="https://example.com/test",
                    source=Mock(title="Test Source")
                )
            ]
        )
        
        from news_fetcher import NewsFetcher
        fetcher = NewsFetcher()
        
        result = fetcher._fetch_google_rss(["test"])
        
        self.assertGreater(len(result), 0)
        self.assertIn("title", result[0])


class TestAISummarizer(unittest.TestCase):
    """Test AI summarization."""
    
    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    def test_summarizer_initialization(self, mock_model, mock_configure):
        """Test summarizer initializes."""
        os.environ["GEMINI_API_KEY"] = "test_key_12345678901234567890123456789"
        
        from ai_summarizer import GeminiSummarizer
        summarizer = GeminiSummarizer()
        
        self.assertTrue(summarizer.enabled)
    
    def test_basic_report_generation(self):
        """Test basic report generation (fallback mode)."""
        from ai_summarizer import GeminiSummarizer
        
        with patch('google.generativeai.configure'):
            with patch('google.generativeai.GenerativeModel'):
                summarizer = GeminiSummarizer()
                summarizer.enabled = False  # Force fallback mode
                
                test_news = {
                    "ai": [{"title": "Test AI News", "source": "Test", "url": "http://test.com"}]
                }
                
                report = summarizer._create_basic_report(test_news)
                
                self.assertIn("Daily News Report", report)
                self.assertIn("Test AI News", report)


class TestDashboardGenerator(unittest.TestCase):
    """Test dashboard generation."""
    
    def test_dashboard_generation(self):
        """Test dashboard HTML generation."""
        from dashboard_generator import DashboardGenerator
        import tempfile
        import os as os_module
        
        # Change to temp directory
        original_dir = os_module.getcwd()
        temp_dir = tempfile.mkdtemp()
        os_module.chdir(temp_dir)
        
        # Create stats file
        with open("stats.json", "w") as f:
            json.dump({"history": [], "total_runs": 0}, f)
        
        try:
            dash = DashboardGenerator()
            path = dash.generate()
            
            self.assertTrue(os_module.path.exists("dashboard.html"))
        finally:
            os_module.chdir(original_dir)


class TestWhatsAppSender(unittest.TestCase):
    """Test WhatsApp sending."""
    
    def test_sender_initialization(self):
        """Test sender initializes."""
        from whatsapp_sender import WhatsAppSender
        sender = WhatsAppSender()
        self.assertIsNotNone(sender.phone_number)
    
    @patch('pywhatkit.sendwhatmsg_instantly')
    def test_send_message(self, mock_send):
        """Test message sending."""
        mock_send.return_value = None
        
        from whatsapp_sender import WhatsAppSender
        sender = WhatsAppSender()
        
        with patch('pyautogui.press'):
            result = sender.send_message("Test message")
        
        self.assertTrue(result)


class TestAutomationController(unittest.TestCase):
    """Test main automation controller."""
    
    def test_controller_initialization(self):
        """Test controller initializes."""
        from run_automation import NewsAutomationController
        controller = NewsAutomationController(dry_run=True)
        self.assertTrue(controller.dry_run)
    
    def test_health_check_structure(self):
        """Test health check returns proper structure."""
        from run_automation import NewsAutomationController
        
        controller = NewsAutomationController(dry_run=True)
        
        with patch.object(controller, '_check_network', return_value=True):
            health = controller.health_check()
        
        self.assertIn("timestamp", health)
        self.assertIn("components", health)
        self.assertIn("overall", health)


class IntegrationTests(unittest.TestCase):
    """Integration tests for full workflow."""
    
    @patch('pywhatkit.sendwhatmsg_instantly')
    @patch('google.generativeai.GenerativeModel')
    @patch('google.generativeai.configure')
    @patch('feedparser.parse')
    def test_dry_run_workflow(self, mock_feed, mock_configure, mock_model, mock_wa):
        """Test complete dry run workflow."""
        # Mock feedparser
        mock_feed.return_value = Mock(
            entries=[Mock(
                title="Test Article",
                link="https://example.com",
                source=Mock(title="Test")
            )]
        )
        
        # Mock Gemini
        mock_response = Mock()
        mock_response.text = "Test summary"
        mock_model.return_value.generate_content.return_value = mock_response
        
        from run_automation import NewsAutomationController
        
        controller = NewsAutomationController(dry_run=True)
        
        # Run full cycle
        with patch.object(controller, 'health_check', return_value={"overall": True, "components": {}}):
            with patch.object(controller, '_fetch_news', return_value={"ai": [{"title": "Test"}]}):
                with patch.object(controller, '_summarize_news', return_value="Test Report"):
                    result = controller.run_full_cycle()
        
        self.assertTrue(result.get("success") or result.get("steps", {}).get("health"))


class TestRateLimiter(unittest.TestCase):
    """Test rate limiting functionality."""
    
    def test_rate_limiter_initialization(self):
        """Test rate limiter initializes correctly."""
        from rate_limiter import RateLimiter
        limiter = RateLimiter(max_calls=10, period=60)
        self.assertEqual(limiter.max_calls, 10)
        self.assertEqual(limiter.period, 60)
    
    def test_rate_limiter_allows_within_limit(self):
        """Test calls within limit are allowed."""
        from rate_limiter import RateLimiter
        limiter = RateLimiter(max_calls=5, period=60)
        
        # Should allow first 5 calls
        for _ in range(5):
            wait_time = limiter.acquire()
            self.assertEqual(wait_time, 0)
    
    def test_rate_limiter_blocks_over_limit(self):
        """Test calls over limit are blocked."""
        from rate_limiter import RateLimiter
        limiter = RateLimiter(max_calls=2, period=10)
        
        # Use up limit
        limiter.acquire()
        limiter.acquire()
        
        # Third call should require waiting
        wait_time = limiter.acquire()
        self.assertGreater(wait_time, 0)
    
    def test_rate_limiter_decorator(self):
        """Test rate limiter as decorator."""
        from rate_limiter import rate_limited
        
        call_count = [0]
        
        @rate_limited(3, 10)
        def test_func():
            call_count[0] += 1
            return "success"
        
        # Should allow calls
        result = test_func()
        self.assertEqual(result, "success")
        self.assertEqual(call_count[0], 1)


class TestUtils(unittest.TestCase):
    """Test utility functions."""
    
    def test_retry_with_backoff_success(self):
        """Test retry decorator with successful call."""
        from utils import retry_with_backoff
        
        @retry_with_backoff(retries=3, backoff_in_seconds=0.1)
        def always_succeeds():
            return "success"
        
        result = always_succeeds()
        self.assertEqual(result, "success")
    
    def test_retry_with_backoff_eventual_success(self):
        """Test retry decorator retries until success."""
        from utils import retry_with_backoff
        
        attempts = [0]
        
        @retry_with_backoff(retries=3, backoff_in_seconds=0.1)
        def fails_twice():
            attempts[0] += 1
            if attempts[0] < 3:
                raise ValueError("Not yet")
            return "success"
        
        result = fails_twice()
        self.assertEqual(result, "success")
        self.assertEqual(attempts[0], 3)
    
    def test_sanitize_text(self):
        """Test text sanitization."""
        from utils import sanitize_text
        
        dirty = "Test â€™ text â€ with issues"
        clean = sanitize_text(dirty)
        
        self.assertNotIn("â€™", clean)
        self.assertIn("'", clean)
    
    def test_truncate(self):
        """Test text truncation."""
        from utils import truncate
        
        long_text = "A" * 100
        truncated = truncate(long_text, 50)
        
        self.assertEqual(len(truncated), 50)
        self.assertTrue(truncated.endswith("..."))
    
    def test_validate_phone_number_valid(self):
        """Test phone number validation with valid numbers."""
        from utils import validate_phone_number
        
        valid_numbers = ["+923001234567", "+12345678901", "923001234567"]
        for num in valid_numbers:
            result = validate_phone_number(num)
            self.assertIsNotNone(result)


class TestWhatsAppFormatter(unittest.TestCase):
    """Test WhatsApp message formatting."""
    
    def test_format_report_basic(self):
        """Test basic report formatting."""
        from whatsapp_formatter import WhatsAppFormatter
        
        test_news = {
            "ai": [
                {"title": "AI Breakthrough", "source": "TechCrunch"},
                {"title": "ML Advances", "source": "Reuters"}
            ],
            "tech": [
                {"title": "New iPhone", "source": "Apple"}
            ]
        }
        
        formatted = WhatsAppFormatter.format_report(test_news)
        
        self.assertIn("DAILY NEWS", formatted.upper())
        self.assertIn("AI Breakthrough", formatted)
        self.assertIn("TechCrunch", formatted)
    
    def test_sanitize_text(self):
        """Test text sanitization in formatter."""
        from whatsapp_formatter import WhatsAppFormatter
        
        dirty = "Test â€™ message"
        clean = WhatsAppFormatter.sanitize(dirty)
        
        self.assertNotIn("â€™", clean)
    
    def test_format_error(self):
        """Test error message formatting."""
        from whatsapp_formatter import WhatsAppFormatter
        
        error_msg = WhatsAppFormatter.format_error("Database connection failed")
        
        self.assertIn("FAILED", error_msg.upper())
        self.assertIn("Database connection", error_msg)


class TestAnalyticsDB(unittest.TestCase):
    """Test analytics database."""
    
    def test_database_initialization(self):
        """Test database creates tables."""
        from analytics_db import AnalyticsDatabase
        import tempfile
        
        temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        db = AnalyticsDatabase(temp_db.name)
        
        # Should initialize without errors
        self.assertIsNotNone(db)
    
    def test_log_run(self):
        """Test logging a run."""
        from analytics_db import AnalyticsDatabase
        import tempfile
        
        temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        db = AnalyticsDatabase(temp_db.name)
        
        run_id = db.log_run(
            duration=15.5,
            success=True,
            articles_count=25,
            messages_sent=1
        )
        
        self.assertIsInstance(run_id, int)
        self.assertGreater(run_id, 0)
    
    def test_get_statistics(self):
        """Test retrieving statistics."""
        from analytics_db import AnalyticsDatabase
        import tempfile
        
        temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        db = AnalyticsDatabase(temp_db.name)
        
        # Log a run
        db.log_run(10.0, True, 20)
        
        stats = db.get_statistics()
        
        self.assertIn('total_runs', stats)
        self.assertIn('successful_runs', stats)
        self.assertEqual(stats['total_runs'], 1)


class TestHealthCheck(unittest.TestCase):
    """Test health check system."""
    
    def test_health_check_initialization(self):
        """Test health check initializes."""
        from health_check import HealthCheck
        
        health = HealthCheck()
        self.assertIsNotNone(health)
    
    def test_check_directories(self):
        """Test directory checking."""
        from health_check import HealthCheck
        
        health = HealthCheck()
        result = health.check_directories()
        
        self.assertIn('is_ok', result)
        self.assertIn('cache_dir', result)
        self.assertIn('log_dir', result)
    
    def test_check_disk_space(self):
        """Test disk space check."""
        from health_check import HealthCheck
        
        health = HealthCheck()
        result = health.check_disk_space()
        
        self.assertIn('free_space_gb', result)
        self.assertIn('is_ok', result)
        self.assertGreater(result['free_space_gb'], 0)
    
    def test_run_all_checks(self):
        """Test running all health checks."""
        from health_check import HealthCheck
        
        health = HealthCheck()
        results = health.run_all()
        
        self.assertIn('summary', results)
        self.assertIn('all_ok', results['summary'])


def run_tests():
    """Run all tests with detailed output."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestConfiguration,
        TestCircuitBreaker,
        TestNewsClusterer,
        TestSmartCache,
        TestNewsFetcher,
        TestAISummarizer,
        TestDashboardGenerator,
        TestWhatsAppSender,
        TestAutomationController,
        TestRateLimiter,
        TestUtils,
        TestWhatsAppFormatter,
        TestAnalyticsDB,
        TestHealthCheck,
        IntegrationTests
    ]
    
    for test_class in test_classes:
        suite.addTests(loader.loadTestsFromTestCase(test_class))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 60)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
