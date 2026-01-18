# DailyNewsBot

An intelligent, automated news aggregation and delivery system that fetches news from multiple sources, summarizes them using Google Gemini AI, and delivers personalized reports via WhatsApp.

## Features

- **Multi-Source News Fetching**: Google News RSS, NewsAPI, GNews
- **AI-Powered Summarization**: Uses Google Gemini for intelligent filtering and summarization
- **Smart Deduplication**: Removes duplicate articles across sources
- **WhatsApp Delivery**: Automated message delivery using pywhatkit
- **Resilient Architecture**: Circuit breaker pattern for API failure handling
- **Visual Dashboard**: HTML analytics dashboard with Chart.js
- **Caching**: Smart caching to reduce API calls
- **Video Briefings**: Optional video generation with text-to-speech

## Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/YOUR_USERNAME/DailyNewsBot.git
cd DailyNewsBot
pip install -r requirements.txt
```

### 2. Configure

Create a `.env` file:

```env
WHATSAPP_NUMBER=+923001234567
GEMINI_API_KEY=your_gemini_api_key
NEWS_API_KEY=your_newsapi_key  # Optional
GNEWS_API_KEY=your_gnews_key   # Optional
```

### 3. Run

```bash
# Health check
python run_automation.py --health

# Dry run (test without sending)
python run_automation.py --dry-run

# Full run (live WhatsApp delivery)
python run_automation.py --run

# Generate dashboard only
python run_automation.py --dashboard
```

## Project Structure

```
DailyNewsBot/
├── run_automation.py      # Main controller
├── config.py              # Configuration & topics
├── news_fetcher.py        # News source integration
├── ai_summarizer.py       # Gemini AI integration
├── whatsapp_sender.py     # WhatsApp delivery
├── circuit_breaker.py     # Resilience pattern
├── news_clustering.py     # Deduplication
├── smart_cache.py         # Caching layer
├── dashboard_generator.py # Analytics dashboard
├── video_generator.py     # Video briefing (optional)
├── analytics.py           # Usage tracking
├── secure_config.py       # Credential management
├── console_utils.py       # Console encoding fixes
└── content_scraper.py     # Full article extraction
```

## API Keys

| Service | Required | Get Key |
|---------|----------|---------|
| Google Gemini | Yes | [AI Studio](https://aistudio.google.com/app/apikey) |
| NewsAPI | No | [newsapi.org](https://newsapi.org) |
| GNews | No | [gnews.io](https://gnews.io) |

## License

MIT License - See LICENSE file for details.

## Author

Muhammad Ibrahim Salman
