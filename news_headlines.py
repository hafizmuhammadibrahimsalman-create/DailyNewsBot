#!/usr/bin/env python3
"""
DailyNewsBot - Headline Mode (No AI Required)
Demonstrates the full news fetching pipeline without AI summarization.
"""
import sys
from datetime import datetime

# Force UTF-8 for Windows Console
sys.stdout.reconfigure(encoding='utf-8')

from news_fetcher import NewsFetcher

def format_article(article, index):
    """Format a single article beautifully."""
    return f"""
  {index}. 📰 {article['title']}
     🔗 {article['url']}
     📅 {article.get('publishedAt', 'Unknown date')}
"""

def main():
    print("=" * 70)
    print("📰 DAILYNEWSBOT - HEADLINE MODE")
    print("=" * 70)
    print(f"🕐 Report Generated: {datetime.now().strftime('%Y-%m-%d %I:%M %p')}")
    print("⚡ Mode: Fast (No AI Summaries - Headlines Only)")
    print("=" * 70)
    print()
    
    # Initialize fetcher
    fetcher = NewsFetcher()
    
    # Define topics
    topics = [
        ("🤖 AI & Machine Learning", "artificial intelligence"),
        ("💻 Technology", "technology"),
        ("🇵🇰 Pakistan News", "Pakistan"),
        ("🏛️ Politics", "politics"),
        ("💼 Business", "business"),
        ("⚽ Sports", "sports"),
        ("🔬 Science", "science"),
    ]
    
    
    # Fetch all news at once
    all_news = fetcher.fetch_all_news()
    total_articles = 0

    
    for topic_id, articles in all_news.items():
        # Get topic config for display name
        from config import TOPICS
        topic_config = TOPICS.get(topic_id, {})
        emoji_topic = topic_config.get('name', topic_id)
        
        print(f"\n{'─' * 70}")
        print(f"📂 CATEGORY: {emoji_topic}")
        print('─' * 70)
        
        if not articles:
            print("  ⚠️  No articles found for this topic.\n")
            continue
        
        print(f"  Found {len(articles)} articles:\n")
        
        for idx, article in enumerate(articles[:5], 1):
            print(format_article(article, idx))
            total_articles += 1

    
    print("\n" + "=" * 70)
    print(f"✅ REPORT COMPLETE")
    print(f"📊 Total Articles Fetched: {total_articles}")
    print(f"⚡ Execution: Fast (No AI processing)")
    print(f"🎯 System Status: Fully Operational")
    print("=" * 70)
    print()
    print("💡 TIP: Once Gemini API quota is available, run:")
    print("   python bot_core.py")
    print("   (for AI-powered summaries)")
    print()

if __name__ == "__main__":
    main()
