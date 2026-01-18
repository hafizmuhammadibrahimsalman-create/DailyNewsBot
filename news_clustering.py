from difflib import SequenceMatcher
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class NewsClusterer:
    """
    Intelligently groups similar news articles to avoid duplicates.
    Uses SequenceMatcher for fuzzy title comparison.
    """
    
    def __init__(self, similarity_threshold: float = 0.65):
        self.threshold = similarity_threshold
        
    def cluster_news(self, all_news: Dict[str, List[Dict]]) -> Dict[str, List[Dict]]:
        """Process all topics and remove duplicates."""
        cleaned_news = {}
        
        total_removed = 0
        
        for topic, articles in all_news.items():
            if not articles:
                cleaned_news[topic] = []
                continue
                
            unique_articles = []
            
            for article in articles:
                is_duplicate = False
                title = article['title'].lower()
                
                for existing in unique_articles:
                    existing_title = existing['title'].lower()
                    
                    # Check similarity
                    ratio = SequenceMatcher(None, title, existing_title).ratio()
                    
                    if ratio > self.threshold:
                        is_duplicate = True
                        # Optional: Keep the one with better description or image?
                        # For now, keep the first one (usually higher rank from API)
                        logger.debug(f"found duplicate: '{title}' == '{existing_title}' ({ratio:.2f})")
                        break
                
                if not is_duplicate:
                    unique_articles.append(article)
                else:
                    total_removed += 1
            
            cleaned_news[topic] = unique_articles
            
        logger.info(f"[CLEAN] Deduplication removed {total_removed} redundant articles.")
        return cleaned_news

if __name__ == "__main__":
    # Test
    clusterer = NewsClusterer()
    test_data = {
        "tech": [
            {"title": "iPhone 16 Released Today"},
            {"title": "Apple releases new iPhone 16"}, # Duplicate
            {"title": "Android 15 is coming soon"}
        ]
    }
    result = clusterer.cluster_news(test_data)
    print(f"Original: 3 -> Result: {len(result['tech'])}")
    for r in result['tech']: print(f"- {r['title']}")
