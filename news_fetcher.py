#!/usr/bin/env python3
"""
DailyNewsBot - News Fetcher
============================
Fetches news from multiple sources with caching and circuit breaker.
"""

import requests
import feedparser
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from config import TOPICS, MAX_ARTICLES_PER_TOPIC, CACHE_DIR
from secure_config import SecureConfig
from smart_cache import SmartCache
from circuit_breaker import circuit

logger = logging.getLogger(__name__)


class NewsFetcher:
    """Fetches news from NewsAPI, GNews, and Google RSS."""
    
    def __init__(self):
        self.news_api = self._get_api_key("NEWS_API_KEY")
        self.gnews_api = self._get_api_key("GNEWS_API_KEY")
        self.cache = SmartCache(CACHE_DIR)
        self.sess = requests.Session()
        self.sess.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def _get_api_key(self, key_name: str) -> Optional[str]:
        """Safely get API key with validation."""
        try:
            key = SecureConfig.get_credential(key_name)
            if key and len(key) > 10 and "YOUR_" not in key:
                return key
        except Exception as e:
            logger.debug(f"Could not load {key_name}: {e}")
        return None

    def fetch_all_news(self) -> Dict[str, List[Dict]]:
        """Fetch news for all configured topics."""
        all_news = {}
        for tid, cfg in TOPICS.items():
            try:
                # Access dataclass attributes (not dict keys)
                topic_name = cfg.name if hasattr(cfg, 'name') else cfg.get('name', tid)
                logger.info(f"Fetching: {topic_name}")
                all_news[tid] = self._fetch_topic_news(tid, cfg)[:MAX_ARTICLES_PER_TOPIC]
            except Exception as e:
                logger.error(f"Failed to fetch topic {tid}: {e}")
                all_news[tid] = []
        return all_news

    def _fetch_topic_news(self, tid: str, cfg: Any) -> List[Dict]:
        """Fetch news for a single topic."""
        key = f"news_{tid}"
        cached = self.cache.get(key, max_age_minutes=60)
        if cached:
            return cached

        arts = []
        
        # Get keywords - handle both dataclass and dict
        keywords = cfg.keywords if hasattr(cfg, 'keywords') else cfg.get('keywords', [tid])
        
        # Try NewsAPI
        if self.news_api:
            try:
                arts.extend(self._fetch_newsapi(keywords))
            except Exception as e:
                logger.warning(f"NewsAPI error for {tid}: {e}")
        
        # Try GNews
        if self.gnews_api:
            try:
                arts.extend(self._fetch_gnews(keywords))
            except Exception as e:
                logger.warning(f"GNews error for {tid}: {e}")
        
        # Always try Google RSS (free)
        try:
            arts.extend(self._fetch_google_rss(keywords))
        except Exception as e:
            logger.warning(f"Google RSS error for {tid}: {e}")
        
        # Pakistan-specific feeds
        if tid in ["pakistan", "ijt"]:
            try:
                arts.extend(self._fetch_pak_rss(cfg))
            except Exception as e:
                logger.warning(f"Pakistan RSS error: {e}")

        unique = self._deduplicate(arts)
        if unique:
            self.cache.set(key, unique)
        return unique

    @circuit("newsapi", threshold=3, timeout=300)
    def _fetch_newsapi(self, kws: List[str]) -> List[Dict]:
        """Fetch from NewsAPI."""
        try:
            url = "https://newsapi.org/v2/everything"
            params = {
                'q': " OR ".join(kws[:3]),
                'apiKey': self.news_api,
                'language': 'en',
                'sortBy': 'publishedAt',
                'pageSize': 10
            }
            resp = self.sess.get(url, params=params, timeout=10)
            if resp.status_code == 200:
                articles = resp.json().get('articles', [])
                return [
                    {
                        'title': a.get('title'),
                        'source': a.get('source', {}).get('name'),
                        'url': a.get('url')
                    }
                    for a in articles if a.get('title')
                ]
        except Exception as e:
            logger.warning(f"NewsAPI fetch failed: {e}")
        return []

    @circuit("gnews", threshold=3, timeout=300)
    def _fetch_gnews(self, kws: List[str]) -> List[Dict]:
        """Fetch from GNews."""
        try:
            url = "https://gnews.io/api/v4/search"
            params = {
                'q': " ".join(kws[:2]),
                'token': self.gnews_api,
                'lang': 'en',
                'max': 10
            }
            resp = self.sess.get(url, params=params, timeout=10)
            if resp.status_code == 200:
                articles = resp.json().get('articles', [])
                return [
                    {
                        'title': a.get('title'),
                        'source': a.get('source', {}).get('name'),
                        'url': a.get('url')
                    }
                    for a in articles if a.get('title')
                ]
        except Exception as e:
            logger.warning(f"GNews fetch failed: {e}")
        return []

    def _fetch_google_rss(self, kws: List[str]) -> List[Dict]:
        """Fetch from Google News RSS (always free)."""
        arts = []
        try:
            for k in kws[:3]:
                query = k.replace(' ', '+')
                url = f"https://news.google.com/rss/search?q={query}&hl=en-PK&gl=PK&ceid=PK:en"
                feed = feedparser.parse(url)
                for e in feed.entries[:5]:
                    source = e.get('source', {})
                    source_name = source.get('title', 'Google News') if isinstance(source, dict) else 'Google News'
                    arts.append({
                        'title': e.get('title'),
                        'source': source_name,
                        'url': e.get('link')
                    })
        except Exception as e:
            logger.warning(f"Google RSS error: {e}")
        return arts

    def _fetch_pak_rss(self, cfg: Any) -> List[Dict]:
        """Fetch from Pakistan news RSS feeds."""
        arts = []
        feeds = [
            "https://www.dawn.com/feeds/home",
            "https://tribune.com.pk/feed/home",
            "https://www.geo.tv/rss/1/1"
        ]
        
        # Get cities - handle both dataclass and dict
        cities_raw = cfg.cities if hasattr(cfg, 'cities') else cfg.get('cities', [])
        cities = [c.lower() for c in cities_raw] if cities_raw else []
        
        for feed_url in feeds:
            try:
                feed = feedparser.parse(feed_url)
                src = feed.feed.get('title', 'PK News')
                for e in feed.entries[:5]:
                    title = e.get('title', '')
                    summary = e.get('summary', '')
                    
                    # Filter by cities if specified
                    if cities:
                        content = (title + summary).lower()
                        if not any(c in content for c in cities):
                            continue
                    
                    arts.append({
                        'title': title,
                        'source': src,
                        'url': e.get('link')
                    })
            except Exception as e:
                logger.debug(f"Feed {feed_url} error: {e}")
        return arts

    def _deduplicate(self, arts: List[Dict]) -> List[Dict]:
        """Remove duplicate articles by title similarity."""
        seen = set()
        unique = []
        for a in arts:
            if not a.get('title'):
                continue
            t = a['title'].lower()[:50]
            if t not in seen:
                seen.add(t)
                unique.append(a)
        return unique


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    f = NewsFetcher()
    print(f"Fetched {len(f._fetch_google_rss(['test']))} test articles")
