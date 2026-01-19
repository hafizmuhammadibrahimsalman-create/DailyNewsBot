#!/usr/bin/env python3
"""
DailyNewsBot - Content Scraper
===============================
Robust web scraper to extract article content from URLs.
"""

import requests
from bs4 import BeautifulSoup
import logging
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from typing import Dict, List, Optional
import re

logger = logging.getLogger(__name__)


class ContentScraper:
    """
    Robust scraper to fetch main article content.
    Uses generic heuristics to find article bodies without site-specific parsers.
    """
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
    
    def fetch_content(self, url: str) -> str:
        """
        Fetch and extract main text from a URL.
        
        Args:
            url: URL to scrape
        
        Returns:
            Extracted text content (max 5000 chars)
        """
        if not url:
            return ""
        
        try:
            resp = self.session.get(url, timeout=self.timeout)
            
            if resp.status_code != 200:
                logger.warning(f"Failed to fetch {url}: Status {resp.status_code}")
                return ""
            
            soup = BeautifulSoup(resp.content, 'html.parser')
            
            # Remove junk elements
            for tag in soup(['script', 'style', 'nav', 'header', 'footer', 
                           'aside', 'iframe', 'form', 'noscript', 'svg']):
                tag.decompose()
            
            # Strategy 1: <article> tag
            article = soup.find('article')
            if article:
                text = article.get_text(separator='\n\n')
                if len(text) > 200:
                    return self._clean_text(text)
            
            # Strategy 2: Common class names
            common_classes = [
                'article-body', 'story-body', 'content-body', 
                'post-content', 'entry-content', 'main-content',
                'article-content', 'story-content', 'news-body'
            ]
            for cls in common_classes:
                div = soup.find('div', class_=re.compile(cls, re.I))
                if div:
                    text = div.get_text(separator='\n\n')
                    if len(text) > 200:
                        return self._clean_text(text)
            
            # Strategy 3: Join all paragraphs
            paragraphs = soup.find_all('p')
            if paragraphs:
                text = '\n\n'.join([p.get_text() for p in paragraphs])
                return self._clean_text(text)
            
            return ""
            
        except requests.Timeout:
            logger.warning(f"Timeout fetching {url}")
            return ""
        except requests.RequestException as e:
            logger.warning(f"Request error for {url}: {e}")
            return ""
        except Exception as e:
            logger.error(f"Scraping error for {url}: {type(e).__name__}: {e}")
            return ""

    def _clean_text(self, text: str) -> str:
        """Clean up whitespace and common clutter."""
        # Collapse multiple newlines
        text = re.sub(r'\n\s*\n', '\n\n', text)
        # Remove massive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Limit length
        return text[:5000].strip()

    def fetch_parallel(self, urls: List[str], max_workers: int = 5, 
                       timeout_per_url: int = 10) -> Dict[str, str]:
        """
        Fetch multiple URLs in parallel with timeout protection.
        
        Args:
            urls: List of URLs to scrape
            max_workers: Maximum concurrent threads
            timeout_per_url: Timeout in seconds for each URL
        
        Returns:
            Dict mapping URL to extracted content
        """
        results = {}
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {
                executor.submit(self.fetch_content, url): url 
                for url in urls
            }
            
            for future in future_to_url:
                url = future_to_url[future]
                try:
                    # CRITICAL: Add timeout to prevent hanging
                    results[url] = future.result(timeout=timeout_per_url)
                except FuturesTimeoutError:
                    logger.warning(f"Timeout waiting for {url}")
                    results[url] = ""
                except Exception as e:
                    logger.error(f"Error fetching {url}: {type(e).__name__}: {e}")
                    results[url] = ""
        
        return results
    
    def fetch_for_articles(self, articles: List[Dict], max_articles: int = 5) -> List[Dict]:
        """
        Fetch content for a list of article dicts (in-place update).
        
        Args:
            articles: List of article dicts with 'url' key
            max_articles: Maximum number to fetch
        
        Returns:
            Articles with 'content' field added
        """
        urls = [a.get('url') for a in articles[:max_articles] if a.get('url')]
        contents = self.fetch_parallel(urls)
        
        for article in articles[:max_articles]:
            url = article.get('url')
            if url:
                article['content'] = contents.get(url, '')
        
        return articles


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    scraper = ContentScraper()
    
    # Test single fetch
    test_url = "https://www.bbc.com/news"
    print(f"Single fetch: {len(scraper.fetch_content(test_url))} chars")
    
    # Test parallel fetch
    test_urls = [
        "https://www.bbc.com/news",
        "https://www.cnn.com",
    ]
    results = scraper.fetch_parallel(test_urls)
    for url, content in results.items():
        print(f"Parallel: {url[:30]}... -> {len(content)} chars")
