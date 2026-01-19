# DailyNewsBot v2.0

**Production-ready automated news aggregation and delivery system** with AI summarization and WhatsApp integration.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Code Quality](https://img.shields.io/badge/code%20quality-production-green.svg)]()

---

## 🚀 Quick Start

### 1. Clone & Install
```bash
git clone https://github.com/hafizmuhammadibrahimsalman-create/DailyNewsBot.git
cd DailyNewsBot
pip install -r requirements.txt
```

### 2. Configure
Create `.env` file (copy from `.env.example`):
```env
GEMINI_API_KEY=your_gemini_api_key_here
WHATSAPP_NUMBER=+923001234567
```

### 3. Validate
```bash
python env_validator.py
```

### 4. Run
```bash
# Health check
python run_automation.py --health

# Test run (no sending)
python run_automation.py --dry-run

# Live run
python run_automation.py --run
```

---

## ✨ Features

- **Multi-Source News**: Google News RSS, NewsAPI, GNews
- **AI Summarization**: Google Gemini for intelligent filtering
- **Smart Deduplication**: Removes duplicate articles
- **WhatsApp Delivery**: Automated message sending
- **Circuit Breaker**: API failure protection
- **Analytics Dashboard**: HTML dashboard with charts
- **Health Checks**: Pre-flight system validation
- **Comprehensive Logging**: Rotating file logs
- **Test Suite**: Unit and integration tests

---

## 📁 Project Structure

```
DailyNewsBot/
├── run_automation.py          # Main entry point
├── config.py                  # Configuration (dataclass-based)
├── env_validator.py           # Environment validation
│
├── Core Components/
│   ├── news_fetcher.py        # Multi-source news fetching
│   ├── ai_summarizer.py       # Gemini AI summarization
│   ├── whatsapp_sender.py     # WhatsApp delivery
│   ├── circuit_breaker.py     # Resilience pattern
│   ├── news_clustering.py     # Deduplication
│   └── content_scraper.py     # Article extraction
│
├── Utilities/
│   ├── smart_cache.py         # Caching layer
│   ├── analytics_db.py        # SQLite analytics
│   ├── health_check.py        # System health
│   ├── logging_config.py      # Logging setup
│   ├── rate_limiter.py        # API rate limiting
│   ├── utils.py               # Retry logic & helpers
│   ├── console_utils.py       # Console encoding
│   └── whatsapp_formatter.py  # Message formatting
│
├── Generated/
│   ├── dashboard_generator.py # HTML analytics
│   └── video_generator.py     # Video briefings (optional)
│
└── Tests/
    └── test_suite.py          # Comprehensive tests
```

---

## 🔧 Configuration

### Required Environment Variables
- `GEMINI_API_KEY` - [Get one](https://aistudio.google.com/app/apikey)
- `WHATSAPP_NUMBER` - Your phone number with country code

### Optional Variables
- `NEWS_API_KEY` - [newsapi.org](https://newsapi.org)
- `GNEWS_API_KEY` - [gnews.io](https://gnews.io)

### Topics Configuration
Edit `config.py` to customize news topics:
```python
TOPICS = {
    "ai": TopicConfig(
        name="AI & Machine Learning",
        keywords=["artificial intelligence", "machine learning"],
        priority="HIGH"
    ),
    # ... more topics
}
```

---

## 🧪 Testing

```bash
# Run test suite
python test_suite.py

# Run with coverage
pytest tests/ --cov=. --cov-report=html
```

---

## 📊 Analytics

View the dashboard after running:
```bash
# Generate dashboard
python run_automation.py --dashboard

# Open in browser
open dashboard.html
```

---

## 🛡️ Security

- ✅ `.env` file not tracked in git
- ✅ API keys validated before use
- ✅ Thread-safe circuit breaker
- ✅ Rate limiting on API calls
- ✅ Retry logic with exponential backoff

---

## 📝 Documentation

| File | Description |
|------|-------------|
| `00_START_HERE.txt` | Quick start guide |
| `CRITICAL_BUGS_AND_FIXES.md` | Bug fixes applied |
| `QUICK_START_CHECKLIST.md` | Setup checklist |

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

---

## 📄 License

MIT License - See LICENSE file for details.

---

## 🙏 Author

**Muhammad Ibrahim Salman**

- GitHub: [@hafizmuhammadibrahimsalman-create](https://github.com/hafizmuhammadibrahimsalman-create)
- Project: [DailyNewsBot](https://github.com/hafizmuhammadibrahimsalman-create/DailyNewsBot)

---

## 🐛 Issues & Support

Found a bug? [Open an issue](https://github.com/hafizmuhammadibrahimsalman-create/DailyNewsBot/issues)

---

**Note:** Remember to regenerate your Gemini API key if the previous one was exposed.
