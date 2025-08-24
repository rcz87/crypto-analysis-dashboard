"""
News API Client for fetching crypto news from multiple sources
Supports NewsAPI, CryptoPanic, and other news aggregators
"""

import requests
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import hashlib
import json

logger = logging.getLogger(__name__)

class NewsAPIClient:
    """Multi-source news aggregator client"""
    
    def __init__(self, news_api_key: str = None, cryptopanic_key: str = None):
        self.news_api_key = news_api_key
        self.cryptopanic_key = cryptopanic_key
        self.cache = {}
        self.cache_duration = 300  # 5 minutes cache
        
    def fetch_articles(self, query: str, language: str = "en", page_size: int = 20) -> List[Dict]:
        """
        Fetch news articles from multiple sources
        Priority: CryptoPanic (crypto-specific) > NewsAPI (general)
        """
        articles = []
        
        # Try CryptoPanic first (crypto-specific news)
        if self.cryptopanic_key:
            crypto_articles = self._fetch_cryptopanic(query, page_size)
            articles.extend(crypto_articles)
        
        # Supplement with NewsAPI if needed
        if self.news_api_key and len(articles) < page_size:
            news_articles = self._fetch_newsapi(query, language, page_size - len(articles))
            articles.extend(news_articles)
        
        # Fallback to free crypto news sources if no API keys
        if not articles:
            articles = self._fetch_free_sources(query, page_size)
        
        return articles[:page_size]
    
    def _fetch_newsapi(self, query: str, language: str, page_size: int) -> List[Dict]:
        """Fetch from NewsAPI.org"""
        try:
            # Check cache first
            cache_key = f"newsapi_{query}_{language}_{page_size}"
            cached = self._get_cached(cache_key)
            if cached:
                return cached
            
            url = "https://newsapi.org/v2/everything"
            params = {
                "q": f"{query} cryptocurrency OR crypto OR bitcoin",
                "language": language,
                "pageSize": page_size,
                "sortBy": "publishedAt",
                "apiKey": self.news_api_key,
                "from": (datetime.now() - timedelta(days=7)).isoformat()
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            articles = []
            for article in data.get("articles", []):
                articles.append({
                    "title": article.get("title", ""),
                    "description": article.get("description", ""),
                    "url": article.get("url", ""),
                    "source": article.get("source", {}).get("name", "Unknown"),
                    "published_at": article.get("publishedAt", ""),
                    "content": article.get("content", ""),
                    "author": article.get("author", ""),
                    "image_url": article.get("urlToImage", "")
                })
            
            self._set_cache(cache_key, articles)
            return articles
            
        except Exception as e:
            logger.warning(f"NewsAPI fetch error: {e}")
            return []
    
    def _fetch_cryptopanic(self, query: str, page_size: int) -> List[Dict]:
        """Fetch from CryptoPanic API"""
        try:
            # Check cache
            cache_key = f"cryptopanic_{query}_{page_size}"
            cached = self._get_cached(cache_key)
            if cached:
                return cached
            
            url = "https://cryptopanic.com/api/v1/posts/"
            params = {
                "auth_token": self.cryptopanic_key,
                "currencies": query.upper(),
                "kind": "news",
                "filter": "rising|hot|important",
                "public": "true"
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            articles = []
            for post in data.get("results", [])[:page_size]:
                articles.append({
                    "title": post.get("title", ""),
                    "description": post.get("title", ""),  # CryptoPanic doesn't have description
                    "url": post.get("url", ""),
                    "source": post.get("source", {}).get("title", "CryptoPanic"),
                    "published_at": post.get("published_at", ""),
                    "content": post.get("title", ""),
                    "author": post.get("source", {}).get("title", ""),
                    "image_url": "",
                    "votes": post.get("votes", {}),  # Unique to CryptoPanic
                    "kind": post.get("kind", "news")
                })
            
            self._set_cache(cache_key, articles)
            return articles
            
        except Exception as e:
            logger.warning(f"CryptoPanic fetch error: {e}")
            return []
    
    def _fetch_free_sources(self, query: str, page_size: int) -> List[Dict]:
        """Fetch from free crypto news RSS feeds and APIs"""
        articles = []
        
        try:
            # CoinDesk RSS (free, no API key required)
            coindesk_url = "https://api.rss2json.com/v1/api.json"
            params = {
                "rss_url": "https://www.coindesk.com/arc/outboundfeeds/rss/",
                "count": page_size
            }
            
            response = requests.get(coindesk_url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                for item in data.get("items", []):
                    if query.lower() in item.get("title", "").lower() or \
                       query.lower() in item.get("description", "").lower():
                        articles.append({
                            "title": item.get("title", ""),
                            "description": item.get("description", ""),
                            "url": item.get("link", ""),
                            "source": "CoinDesk",
                            "published_at": item.get("pubDate", ""),
                            "content": item.get("content", ""),
                            "author": item.get("author", "CoinDesk"),
                            "image_url": item.get("thumbnail", "")
                        })
        except Exception as e:
            logger.warning(f"Free source fetch error: {e}")
        
        return articles[:page_size]
    
    def _get_cached(self, key: str) -> Optional[List[Dict]]:
        """Get cached data if still valid"""
        if key in self.cache:
            cached_time, data = self.cache[key]
            if datetime.now().timestamp() - cached_time < self.cache_duration:
                logger.info(f"Using cached news for {key}")
                return data
        return None
    
    def _set_cache(self, key: str, data: List[Dict]):
        """Cache data with timestamp"""
        self.cache[key] = (datetime.now().timestamp(), data)
    
    def get_trending_topics(self) -> List[str]:
        """Get trending crypto topics"""
        try:
            if self.cryptopanic_key:
                url = "https://cryptopanic.com/api/v1/posts/"
                params = {
                    "auth_token": self.cryptopanic_key,
                    "filter": "trending",
                    "public": "true"
                }
                response = requests.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    topics = set()
                    for post in data.get("results", [])[:10]:
                        for currency in post.get("currencies", []):
                            topics.add(currency.get("code", ""))
                    return list(topics)
        except Exception as e:
            logger.warning(f"Trending topics error: {e}")
        
        # Default trending topics
        return ["BTC", "ETH", "SOL", "XRP", "DOGE"]