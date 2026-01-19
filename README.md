# DailyNewsBot

DailyNewsBot is an automated intelligence agent that fetches daily news from various sources (Google News, RSS feeds), processes and filters them using Google Gemini AI to identify relevant stories, and delivers a concise, formatted report directly to WhatsApp. It features a robust architecture with rate limiting, circuit breakers, and a monitoring dashboard.

## 🚀 How to Run

1.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Configure Environment**
    Copy `.env.example` to `.env` and fill in your API keys (Gemini, WhatsApp).
    ```bash
    cp .env.example .env
    ```

3.  **Start the Bot**
    ```bash
    python run.py
    ```

## 📂 Project Structure

*   `bot/`: Core application logic (MVC architecture).
    *   `main.py`: Controller and entry point.
    *   `news_fetcher.py`: News aggregation logic.
    *   `summarizer.py`: AI processing (Google Gemini).
    *   `whatsapp_sender.py`: WhatsApp delivery integration.
    *   `utils.py`: Shared utilities.
*   `data/`: Runtime storage (logs, database, cache).
*   `tests/`: Unit and integration tests.
*   `scripts/`: Maintenance and utility scripts.

## 🔮 Roadmap

*   [ ] Migration to Telegram for richer media support.
*   [ ] Interactive chatbot for news querying.
*   [ ] Multi-user support with personalized topic subscriptions.
*   [ ] Web-based configuration dashboard.

---
*Clean Code Architecture implemented by Antigravity*
