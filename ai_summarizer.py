# Daily News Intelligence System - Gemini AI Summarizer
# Uses Google Gemini API (Google One Pro) for intelligent summarization

import google.generativeai as genai
from typing import List, Dict, Optional
import json
import logging
from config import GEMINI_API_KEY, GEMINI_MODEL, GEMINI_FLASH, SUMMARIZER_PROMPT, INFOGRAPHIC_PROMPT, TOPICS
from content_scraper import ContentScraper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GeminiSummarizer:
    """AI-powered news summarizer using Google Gemini."""
    
    def __init__(self):
        self.scraper = ContentScraper()
        
        if GEMINI_API_KEY and GEMINI_API_KEY != "YOUR_GEMINI_API_KEY_HERE":
            genai.configure(api_key=GEMINI_API_KEY)
            self.model = genai.GenerativeModel(GEMINI_MODEL)
            self.flash_model = genai.GenerativeModel(GEMINI_FLASH)
            self.enabled = True
            logger.info("[OK] Gemini AI initialized successfully")
        else:
            self.enabled = False
            logger.warning("[WARN] Gemini API key not configured. Using basic summaries.")
    
    def create_intelligence_report(self, all_news: Dict[str, List[Dict]]) -> str:
        """Create a comprehensive intelligence report from all news."""
        
        if not self.enabled:
            return self._create_basic_report(all_news)
        
        try:
            # 1. Scrape full content for filtered articles
            logger.info("[AI] Reading full articles for deep analysis...")
            urls_to_scrape = []
            for articles in all_news.values():
                for article in articles:
                    if article.get('url'):
                        urls_to_scrape.append(article['url'])
            
            # Parallel fetch
            scraped_content = self.scraper.fetch_parallel(urls_to_scrape)
            
            # Enhance articles with full text
            enhanced_news = all_news.copy()
            for topic in enhanced_news:
                for article in enhanced_news[topic]:
                    url = article.get('url')
                    if url and scraped_content.get(url):
                        article['full_content'] = scraped_content[url]
                    else:
                        article['full_content'] = article.get('description', '')

            # Prepare news data for AI
            news_json = json.dumps(enhanced_news, indent=2, default=str)
            
            prompt = f"""{SUMMARIZER_PROMPT}

Today's collected news (Full content analysis):
{news_json}

Create a comprehensive but CONCISE daily intelligence report. Format for WhatsApp:

1. Start with a greeting and today's date
2. For each topic category:
   - Use the topic emoji and name as header
   - Synthesize the FULL CONTENT into 2-3 deep insights (not just headlines)
   - Use bullet points (•)
   - Highlight specific numbers, quotes, or implications found in the text
   - Note: For Politics, create a brief infographic-style summary

3. End with:
   - [KEY] Key Takeaways (2-3 actionable insights)
   - [STATS] Quick Stats (if relevant numbers)

IMPORTANT: 
- Use the FULL CONTENT provided to give depth
- Be EXTREMELY selective - only truly important news
- Skip fluff, entertainment, and time-wasters
- Maximum 2500 characters total
- Make it scannable on mobile"""

            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            logger.error(f"Gemini error: {e}")
            return self._create_basic_report(all_news)
    
    def create_politics_infographic(self, politics_news: List[Dict]) -> str:
        """Create text-based infographic for political news."""
        
        if not self.enabled or not politics_news:
            return ""
        
        try:
            news_text = "\n".join([
                f"- {article['title']}: {article['description'][:100]}"
                for article in politics_news[:5]
            ])
            
            prompt = f"""{INFOGRAPHIC_PROMPT}

Political news to visualize:
{news_text}

Create a WhatsApp-friendly text infographic."""

            response = self.flash_model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            logger.error(f"Infographic error: {e}")
            return ""
    
    def filter_relevant_news(self, articles: List[Dict], topic_id: str) -> List[Dict]:
        """Use AI to filter only truly relevant news."""
        
        if not self.enabled or not articles:
            return articles[:3]
        
        try:
            topic_config = TOPICS.get(topic_id, {})
            filter_type = topic_config.get('filter', 'all')
            
            articles_text = "\n".join([
                f"{i+1}. {a['title']}" for i, a in enumerate(articles[:10])
            ])
            
            prompt = f"""From these {topic_config.get('name', 'news')} headlines, select ONLY the most important ones.

Filter criteria: {filter_type}
- beneficial: Must provide practical value or learning
- important: Major events only, skip routine news
- attention_worthy: Requires immediate attention or action
- very_valuable: Exceptional news only
- attention_required: Directly relevant to user's interests

Headlines:
{articles_text}

Return ONLY the numbers of selected headlines (e.g., "1, 3, 5")
Maximum 3 selections. Be VERY selective."""

            response = self.flash_model.generate_content(prompt)
            
            # Parse response to get selected indices
            selected_text = response.text.strip()
            selected_indices = []
            for num in selected_text.replace(',', ' ').split():
                try:
                    idx = int(num.strip()) - 1
                    if 0 <= idx < len(articles):
                        selected_indices.append(idx)
                except ValueError:
                    continue
            
            if selected_indices:
                return [articles[i] for i in selected_indices[:3]]
            return articles[:3]
            
        except Exception as e:
            logger.warning(f"Filter error: {e}")
            return articles[:3]
    
    def _create_basic_report(self, all_news: Dict[str, List[Dict]]) -> str:
        """Create a basic report without AI (fallback)."""
        from datetime import datetime
        
        def sanitize(text):
            """Clean up encoding issues in text."""
            if not text:
                return text
            # Fix common mojibake patterns
            fixes = {
                'â€™': "'", 'â€˜': "'", 'â€œ': '"', 'â€': '"',
                'â€"': '-', 'â€"': '-', 'â€¦': '...', 'Â': '',
                '\u2018': "'", '\u2019': "'", '\u201c': '"', '\u201d': '"',
                '\u2013': '-', '\u2014': '-', '\u2026': '...',
            }
            for bad, good in fixes.items():
                text = text.replace(bad, good)
            # Remove any remaining non-ASCII
            return text.encode('ascii', errors='ignore').decode('ascii')
        
        lines = [
            f"[NEWS] *Daily News Report*",
            f"[DATE] {datetime.now().strftime('%B %d, %Y')}",
            ""
        ]
        
        for topic_id, articles in all_news.items():
            if not articles:
                continue
                
            topic_config = TOPICS.get(topic_id, {})
            topic_name = topic_config.get('name', topic_id.title())
            
            lines.append(f"\n*{sanitize(topic_name)}*")
            
            for article in articles[:3]:
                title = sanitize(article['title'][:80])
                lines.append(f"* {title}")
        
        lines.append("\n---")
        lines.append("_Powered by Daily News Intelligence_")
        
        return "\n".join(lines)


# Test the summarizer
if __name__ == "__main__":
    summarizer = GeminiSummarizer()
    
    # Test with sample data
    sample_news = {
        "ai": [
            {"title": "OpenAI releases GPT-5", "description": "Major AI breakthrough", "url": ""},
            {"title": "Google Gemini 2.0 announced", "description": "New features", "url": ""}
        ],
        "pakistan": [
            {"title": "Islamabad metro project update", "description": "New route", "url": ""}
        ]
    }
    
    print("[TEST] Testing Gemini Summarizer...")
    report = summarizer.create_intelligence_report(sample_news)
    print("\n" + report)
