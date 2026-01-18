import requests
from bs4 import BeautifulSoup
import logging
from concurrent.futures import ThreadPoolExecutor
import re

logger = logging.getLogger(__name__)

class ContentScraper:
    """
    Robust scraper to fetch main article content.
    Uses generic heuristics to find article bodies without site-specific parsers.
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def fetch_content(self, url: str) -> str:
        """Fetch and extract main text from a URL."""
        if not url: return ""
        
        try:
            # Simple timeout prevention
            resp = self.session.get(url, timeout=5)
            if resp.status_code != 200:
                logger.warning(f"Failed to fetch {url}: Status {resp.status_code}")
                return ""
                
            soup = BeautifulSoup(resp.content, 'html.parser')
            
            # Remove junk
            for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'iframe', 'form']):
                tag.decompose()
            
            # Strategy 1: Look for <article> tag
            article = soup.find('article')
            if article:
                text = article.get_text(separator='\n\n')
                if len(text) > 200:
                    return self._clean_text(text)
            
            # Strategy 2: Look for common class names
            common_classes = ['article-body', 'story-body', 'content-body', 'post-content', 'entry-content', 'main-content']
            for cls in common_classes:
                div = soup.find('div', class_=re.compile(cls, re.I))
                if div:
                    text = div.get_text(separator='\n\n')
                    if len(text) > 200:
                        return self._clean_text(text)
                        
            # Strategy 3: Find all paragraphs and join them
            paragraphs = soup.find_all('p')
            text = '\n\n'.join([p.get_text() for p in paragraphs])
            
            return self._clean_text(text)
            
        except Exception as e:
            logger.warning(f"Scraping error for {url}: {e}")
            return ""

    def _clean_text(self, text: str) -> str:
        """Clean up whitespace and common clutter."""
        # Collapse multiple newlines
        text = re.sub(r'\n\s*\n', '\n\n', text)
        # Remove massive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Limit length to avoid token connection issues
        return text[:5000].strip()

    def fetch_parallel(self, urls: list, max_workers=5) -> dict:
        """Fetch multiple URLs in parallel."""
        results = {}
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {executor.submit(self.fetch_content, url): url for url in urls}
            for future in future_to_url:
                url = future_to_url[future]
                try:
                    results[url] = future.result()
                except Exception:
                    results[url] = ""
        return results

if __name__ == "__main__":
    # Test
    scraper = ContentScraper()
    test_url = "https://www.bbc.com" # Just a test, might not have an article body on home
    print(f"Test scrape: {len(scraper.fetch_content(test_url))} chars")
