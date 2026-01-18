import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any

# Force UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from news_fetcher import NewsFetcher
from ai_summarizer import GeminiSummarizer
from smart_cache import SmartCache
from secure_config import SecureConfig

class AntigravityQuery:
    """
    On-demand research system.
    Can be triggered via n8n webhook or CLI.
    """
    
    def __init__(self):
        self.fetcher = NewsFetcher()
        self.summarizer = GeminiSummarizer()
        self.cache = SmartCache()

    def query(self, topic: str) -> Dict[str, Any]:
        """
        Execute a research query on a specific topic.
        1. Check Cache
        2. Fetch Fresh News
        3. Synthesize Answer with Gemini
        """
        response = {
            "topic": topic,
            "status": "success",
            "cached": False,
            "answer": "",
            "sources": []
        }

        # 1. Fetch News (Fetcher handles caching implicitly now)
        # We construct a temporary config for the fetcher
        temp_config = {
            "keywords": topic.split(),
            "sources": ["newsapi", "gnews", "google_rss"]
        }
        
        # We bypass the standard fetch_all and use internal methods for specific query
        # But for reliability, we'll use the public fetch method with a temporary filter
        print(f"🔍 Researching: {topic}...")
        
        # Helper to just get raw articles for this query
        articles = self.fetcher._fetch_from_google_news_rss(topic.split())
        
        # Expand sources if needed
        if len(articles) < 3:
             if self.fetcher.news_api_key:
                 articles.extend(self.fetcher._fetch_from_newsapi(topic.split()))
        
        response["sources"] = articles[:5] # Top 5 sources
        
        if not articles:
            response["status"] = "no_data"
            response["answer"] = f"I couldn't find any recent news about '{topic}'."
            return response

        # 2. AI Synthesis
        print("🤖 Synthesizing answer...")
        # We reuse the summarizer but with a custom prompt for Q&A
        full_text = "\n\n".join([f"{a['title']} - {a['description']}" for a in articles])
        
        prompt = f"""
        You are a highly intelligent news analyst. 
        User Query: "{topic}"
        
        Based ONLY on the following news snippets, provide a concise, 
        direct answer or summary. Do not hallucinate.
        
        News Data:
        {full_text[:5000]}
        """
        
        try:
            model = self.summarizer.model
            result = model.generate_content(prompt)
            response["answer"] = result.text.strip()
        except Exception as e:
            response["status"] = "ai_error"
            response["answer"] = f"Error generating answer: {e}"

        return response

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Antigravity Interactive Query")
    parser.add_argument("query", type=str, help="Topic to research")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    
    args = parser.parse_args()
    
    aq = AntigravityQuery()
    result = aq.query(args.query)
    
    if args.json:
        print(json.dumps(result))
    else:
        print("\n" + "="*50)
        print(f"📢 REPORT: {result['topic'].upper()}")
        print("-" * 50)
        print(result['answer'])
        print("\nSources:")
        for i, s in enumerate(result['sources'], 1):
            print(f"{i}. {s['title']} ({s['source']})")
        print("="*50)
