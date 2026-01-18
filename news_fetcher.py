
import requests, feedparser, logging
from datetime import datetime, timedelta
from typing import List, Dict
from config import TOPICS, MAX_ARTICLES_PER_TOPIC, CACHE_DIR
from secure_config import SecureConfig
from smart_cache import SmartCache
from circuit_breaker import circuit

logger = logging.getLogger(__name__)

class NewsFetcher:
    def __init__(self):
        self.news_api = SecureConfig.get_credential("NEWS_API_KEY")
        self.gnews_api = SecureConfig.get_credential("GNEWS_API_KEY")
        self.cache = SmartCache(CACHE_DIR)
        self.sess = requests.Session()
        self.sess.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})

    def fetch_all_news(self) -> Dict[str, List[Dict]]:
        all_news = {}
        for tid, cfg in TOPICS.items():
            logger.info(f"Fetching: {cfg['name']}")
            all_news[tid] = self._fetch_topic_news(tid, cfg)[:MAX_ARTICLES_PER_TOPIC]
        return all_news

    def _fetch_topic_news(self, tid: str, cfg: Dict) -> List[Dict]:
        key = f"news_{tid}"
        if (cached := self.cache.get(key, max_age_minutes=60)): return cached

        arts = []
        if self.news_api and "YOUR_NEWSAPI" not in self.news_api:
            try:
                arts.extend(self._fetch_newsapi(cfg['keywords']))
            except Exception: pass
        if self.gnews_api and "YOUR_GNEWS" not in self.gnews_api:
            try:
                arts.extend(self._fetch_gnews(cfg['keywords']))
            except Exception: pass
            
        arts.extend(self._fetch_google_rss(cfg['keywords']))
        if tid in ["pakistan", "ijt"]: arts.extend(self._fetch_pak_rss(cfg))

        unique = self._deduplicate(arts)
        if unique: self.cache.set(key, unique)
        return unique

    @circuit("newsapi", threshold=3, timeout=300)
    def _fetch_newsapi(self, kws: List[str]) -> List[Dict]:
        try:
            url = "https://newsapi.org/v2/everything"
            p = {'q': " OR ".join(kws[:3]), 'apiKey': self.news_api, 'language': 'en', 'sortBy': 'publishedAt', 'pageSize': 10}
            r = self.sess.get(url, params=p, timeout=10)
            if r.status_code == 200:
                return [{'title': a.get('title'), 'source': a.get('source', {}).get('name'), 'url': a.get('url')} for a in r.json().get('articles', [])]
        except Exception as e: logger.warn(f"NewsAPI: {e}")
        return []

    @circuit("gnews", threshold=3, timeout=300)
    def _fetch_gnews(self, kws: List[str]) -> List[Dict]:
        try:
            url = "https://gnews.io/api/v4/search"
            p = {'q': " ".join(kws[:2]), 'token': self.gnews_api, 'lang': 'en', 'max': 10}
            r = self.sess.get(url, params=p, timeout=10)
            if r.status_code == 200:
                return [{'title': a.get('title'), 'source': a.get('source', {}).get('name'), 'url': a.get('url')} for a in r.json().get('articles', [])]
        except Exception as e: logger.warn(f"GNews: {e}")
        return []

    def _fetch_google_rss(self, kws: List[str]) -> List[Dict]:
        arts = []
        try:
            for k in kws[:3]:
                url = f"https://news.google.com/rss/search?q={k.replace(' ', '+')}&hl=en-PK&gl=PK&ceid=PK:en"
                for e in feedparser.parse(url).entries[:5]:
                    arts.append({'title': e.get('title'), 'source': e.get('source', {}).get('title', 'Google'), 'url': e.get('link')})
        except Exception as e: logger.warn(f"GoogleRSS: {e}")
        return arts

    def _fetch_pak_rss(self, cfg: Dict) -> List[Dict]:
        arts = []
        feeds = ["https://www.dawn.com/feeds/home", "https://tribune.com.pk/feed/home", "https://www.geo.tv/rss/1/1"]
        cities = [c.lower() for c in cfg.get('cities', [])]
        
        for f in feeds:
            try:
                feed = feedparser.parse(f)
                src = feed.feed.get('title', 'PK News')
                for e in feed.entries[:5]:
                    if cities and not any(c in e.get('title', '').lower() or c in e.get('summary', '').lower() for c in cities): continue
                    arts.append({'title': e.get('title'), 'source': src, 'url': e.get('link')})
            except: pass
        return arts

    def _deduplicate(self, arts: List[Dict]) -> List[Dict]:
        seen, out = set(), []
        for a in arts:
            t = a['title'].lower()[:50]
            if t not in seen:
                seen.add(t); out.append(a)
        return out

if __name__ == "__main__":
    f = NewsFetcher()
    print(f"Fetched {len(f._fetch_google_rss(['test']))} test articles")
