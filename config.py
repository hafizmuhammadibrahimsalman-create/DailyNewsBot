#!/usr/bin/env python3
"""
DailyNewsBot - Enhanced Configuration Management
=================================================
Secure, validated configuration with dataclasses and environment support.
"""

import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project paths
BASE_DIR = Path(__file__).parent
CACHE_DIR = BASE_DIR / "cache"
LOG_DIR = BASE_DIR / "logs"


@dataclass
class APIConfig:
    """API configuration with validation."""
    gemini_api_key: str = field(default_factory=lambda: os.getenv("GEMINI_API_KEY", ""))
    news_api_key: Optional[str] = field(default_factory=lambda: os.getenv("NEWS_API_KEY"))
    gnews_api_key: Optional[str] = field(default_factory=lambda: os.getenv("GNEWS_API_KEY"))
    
    # Rate limits
    gemini_rate_limit: int = 60
    api_timeout: int = 30
    
    def validate(self) -> bool:
        """Validate required API keys."""
        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY is required")
        if len(self.gemini_api_key) < 20:
            raise ValueError("GEMINI_API_KEY appears invalid (too short)")
        return True


@dataclass
class WhatsAppConfig:
    """WhatsApp configuration."""
    phone_number: str = field(default_factory=lambda: os.getenv("WHATSAPP_NUMBER", ""))
    wait_time: int = 30
    close_tab: bool = False
    
    def validate(self) -> bool:
        """Validate phone number."""
        if not self.phone_number:
            raise ValueError("WHATSAPP_NUMBER is required")
        clean = self.phone_number.replace("+", "").replace("-", "").replace(" ", "")
        if not clean.isdigit():
            raise ValueError("WHATSAPP_NUMBER must contain only digits")
        if len(clean) < 10:
            raise ValueError("WHATSAPP_NUMBER appears too short")
        return True


@dataclass
class TopicConfig:
    """Individual topic configuration."""
    name: str
    keywords: List[str]
    priority: str = "MEDIUM"  # HIGH, MEDIUM, LOW
    filter_type: str = "all"  # all, beneficial, important, attention_worthy
    include_all: bool = False


# Default topics
TOPICS: Dict[str, TopicConfig] = {
    "ai": TopicConfig(
        name="AI & Machine Learning",
        keywords=["artificial intelligence", "machine learning", "ChatGPT", "Gemini", "OpenAI", "LLM"],
        priority="HIGH",
        include_all=True
    ),
    "technology": TopicConfig(
        name="Technology",
        keywords=["technology", "tech news", "software", "startup", "innovation"],
        priority="HIGH",
        filter_type="beneficial"
    ),
    "pakistan": TopicConfig(
        name="Pakistan News",
        keywords=["Islamabad", "Taxila", "Karachi", "Pakistan", "Rawalpindi"],
        priority="HIGH",
        filter_type="important"
    ),
    "politics": TopicConfig(
        name="Politics",
        keywords=["Pakistan politics", "government", "election", "Parliament"],
        priority="MEDIUM"
    ),
    "business": TopicConfig(
        name="Business",
        keywords=["business", "economy", "stock market", "PSX", "rupee"],
        priority="MEDIUM",
        filter_type="attention_worthy"
    ),
    "sports": TopicConfig(
        name="Sports",
        keywords=["Pakistan cricket", "PSL", "sports"],
        priority="LOW",
        filter_type="very_valuable"
    ),
    "science": TopicConfig(
        name="Science",
        keywords=["science breakthrough", "research", "space", "medicine"],
        priority="MEDIUM",
        filter_type="beneficial"
    ),
    "ijt": TopicConfig(
        name="Islami Jamiat Talaba",
        keywords=["Islami Jamiat Talaba", "IJT", "student union"],
        priority="HIGH",
        filter_type="attention_required"
    )
}


@dataclass
class NewsConfig:
    """News fetching configuration."""
    topics: Dict[str, TopicConfig] = field(default_factory=lambda: TOPICS)
    max_articles_per_topic: int = 5
    max_total_articles: int = 25
    cache_ttl: int = 3600  # 1 hour
    language: str = "en"
    country: str = "pk"


@dataclass
class AIConfig:
    """AI summarization configuration."""
    model_name: str = "gemini-2.0-flash"
    flash_model: str = "gemini-2.0-flash"
    temperature: float = 0.3
    max_tokens: int = 2048
    summary_max_length: int = 150
    similarity_threshold: float = 0.65


@dataclass
class SystemConfig:
    """System-wide configuration."""
    cache_dir: Path = field(default_factory=lambda: CACHE_DIR)
    log_dir: Path = field(default_factory=lambda: LOG_DIR)
    
    log_level: str = "INFO"
    log_rotation_size: int = 10 * 1024 * 1024  # 10MB
    log_backup_count: int = 5
    
    max_workers: int = 5
    request_timeout: int = 30
    retry_attempts: int = 3
    
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout: int = 60
    
    enable_video_generation: bool = False
    enable_analytics: bool = True
    enable_dashboard: bool = True
    
    def ensure_directories(self):
        """Create necessary directories."""
        self.cache_dir.mkdir(exist_ok=True)
        self.log_dir.mkdir(exist_ok=True)
        (self.log_dir / "health_reports").mkdir(exist_ok=True)


@dataclass
class ScheduleConfig:
    """Scheduling configuration."""
    run_time: str = "21:00"  # 9:00 PM
    timezone: str = "Asia/Karachi"
    run_days: List[int] = field(default_factory=lambda: list(range(7)))


class Config:
    """Main configuration - aggregates all sections."""
    
    def __init__(self, config_file: Optional[str] = None):
        self.api = APIConfig()
        self.whatsapp = WhatsAppConfig()
        self.news = NewsConfig()
        self.ai = AIConfig()
        self.system = SystemConfig()
        self.schedule = ScheduleConfig()
        
        if config_file and Path(config_file).exists():
            self.load_from_file(config_file)
        
        self.system.ensure_directories()
    
    def validate_all(self) -> bool:
        """Validate all configuration sections."""
        try:
            self.api.validate()
            self.whatsapp.validate()
            return True
        except ValueError as e:
            print(f"[ERR] Configuration validation failed: {e}")
            return False
    
    def load_from_file(self, filepath: str):
        """Load configuration from JSON file."""
        with open(filepath, encoding='utf-8') as f:
            data = json.load(f)
        
        if "system" in data:
            for key, value in data["system"].items():
                if hasattr(self.system, key):
                    if key.endswith("_dir"):
                        value = Path(value)
                    setattr(self.system, key, value)
        
        if "schedule" in data:
            for key, value in data["schedule"].items():
                if hasattr(self.schedule, key):
                    setattr(self.schedule, key, value)
    
    def save_to_file(self, filepath: str):
        """Save current configuration to JSON file."""
        data = {
            "system": {
                "log_level": self.system.log_level,
                "max_workers": self.system.max_workers,
                "retry_attempts": self.system.retry_attempts
            },
            "schedule": {
                "run_time": self.schedule.run_time,
                "timezone": self.schedule.timezone,
                "run_days": self.schedule.run_days
            }
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get configuration summary for logging."""
        return {
            "topics": list(self.news.topics.keys()),
            "max_articles": self.news.max_total_articles,
            "ai_model": self.ai.model_name,
            "log_level": self.system.log_level
        }


# Global config instance
_config: Optional[Config] = None

def get_config(config_file: Optional[str] = None) -> Config:
    """Get global configuration instance."""
    global _config
    if _config is None:
        _config = Config(config_file)
    return _config


# === LEGACY COMPATIBILITY ===
# These exports maintain backward compatibility with existing code

WHATSAPP_NUMBER = os.getenv("WHATSAPP_NUMBER", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
GNEWS_API_KEY = os.getenv("GNEWS_API_KEY", "")

MAX_ARTICLES_PER_TOPIC = 5
MAX_TOTAL_ARTICLES = 25
REPORT_TIME = "21:00"

GEMINI_MODEL = "gemini-2.0-flash"
GEMINI_FLASH = "gemini-2.0-flash"

SUMMARIZER_PROMPT = """You are an expert news analyst. Your job is to:
1. Analyze news articles and extract what's truly important
2. Filter out time-wasting or irrelevant news
3. Present information in a clear, concise manner
4. Highlight actionable insights
5. Focus on what benefits the user directly

Be extremely selective. Quality over quantity."""

INFOGRAPHIC_PROMPT = """Create a text-based infographic for WhatsApp that visualizes key developments. Use:
- Clear hierarchy with headers
- Bullet points for key facts
- Numbers and statistics highlighted
- Keep it readable on mobile
Maximum 500 characters per section."""

LOG_FILE = BASE_DIR / "news_bot.log"
CACHE_DIR.mkdir(exist_ok=True)


if __name__ == "__main__":
    config = get_config()
    print("Configuration loaded:")
    print(json.dumps(config.get_summary(), indent=2))
    
    if config.validate_all():
        print("\n[OK] Configuration is valid")
    else:
        print("\n[ERR] Configuration validation failed")
