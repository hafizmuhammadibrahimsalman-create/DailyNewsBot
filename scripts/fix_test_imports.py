import os

MAPPINGS = {
    "from config": "from bot.config",
    "from utils": "from bot.utils",
    "from whatsapp_sender": "from bot.whatsapp_sender",
    "from whatsapp_formatter": "from bot.whatsapp_formatter",
    "from ai_summarizer": "from bot.ai_summarizer",
    "from news_fetcher": "from bot.news_fetcher",
    "from dashboard_generator": "from bot.dashboard_generator",
    "from analytics_db": "from bot.analytics_db",
    "from rate_limiter": "from bot.rate_limiter",
    "from circuit_breaker": "from bot.circuit_breaker",
    "from smart_cache": "from bot.smart_cache",
    "from news_clustering": "from bot.news_clustering",
    "from run_automation": "from bot.main",
}

def fix_test_imports():
    path = "tests/test_suite.py"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    for old, new in MAPPINGS.items():
        # Replace checking for word boundaries roughly
        content = content.replace(f"{old} ", f"{new} ")
        content = content.replace(f"{old}\n", f"{new}\n")
    
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Fixed imports in tests/test_suite.py")

if __name__ == "__main__":
    fix_test_imports()
