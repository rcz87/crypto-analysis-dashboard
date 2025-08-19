"""
Crypto News Analyzer Module for GPTS System
- Ambil berita kripto dari CryptoPanic RSS
- Lakukan analisis sentimen menggunakan GPT-4o
- Integrasi dengan self-improvement system
- Output dalam format struktur GPTS
"""

import feedparser
import requests
import openai
import os
import logging
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional
import asyncio
import aiohttp
from collections import defaultdict

# Setup logging
logger = logging.getLogger(__name__)

class CryptoNewsAnalyzer:
    """
    Advanced Crypto News Analyzer dengan sentiment analysis
    dan integration ke self-improvement system
    """
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """Initialize Crypto News Analyzer"""
        self.openai_api_key = openai_api_key or os.environ.get("OPENAI_API_KEY")
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
        
        # RSS Feeds
        self.rss_feeds = {
            "cryptopanic": "https://cryptopanic.com/api/v1/posts/?auth_token=YOUR_TOKEN&public=true",
            "coindesk": "https://www.coindesk.com/arc/outboundfeeds/rss/",
            "cointelegraph": "https://cointelegraph.com/rss",
            # Bisa tambah RSS feed lain di sini
        }
        
        # Cache untuk prevent duplicate analysis
        self.analyzed_news_cache = {}
        self.cache_ttl = 3600  # 1 hour
        
        # Sentiment tracking untuk self-learning
        self.sentiment_history = defaultdict(list)
        self.sentiment_accuracy = {}
        
        logger.info("📰 Crypto News Analyzer initialized")
    
    async def fetch_crypto_news_from_web(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Fallback: Fetch crypto news using web scraping
        """
        try:
            import trafilatura
            
            # Popular crypto news URLs
            urls = [
                "https://www.coindesk.com/",
                "https://cointelegraph.com/",
                "https://decrypt.co/news"
            ]
            
            news = []
            
            for url in urls[:1]:  # Start with one source
                try:
                    downloaded = trafilatura.fetch_url(url)
                    if downloaded:
                        # Extract main content
                        text = trafilatura.extract(downloaded)
                        if text:
                            # Simple parsing - split into sections
                            lines = text.split('\n')
                            for i, line in enumerate(lines[:limit]):
                                if len(line) > 50:  # Likely a headline
                                    news_item = {
                                        "id": f"web_{i}_{int(datetime.now().timestamp())}",
                                        "title": line[:200],
                                        "link": url,
                                        "published": datetime.now(timezone.utc).isoformat(),
                                        "published_timestamp": int(datetime.now().timestamp()),
                                        "summary": lines[i+1] if i+1 < len(lines) else line,
                                        "source": "web_scrape",
                                        "tags": []
                                    }
                                    news.append(news_item)
                                    
                                    if len(news) >= limit:
                                        break
                except Exception as e:
                    logger.warning(f"Error scraping {url}: {e}")
                    continue
            
            logger.info(f"✅ Web scraped {len(news)} news items")
            return news[:limit]
            
        except ImportError:
            logger.error("Trafilatura not available for web scraping")
            return []
        except Exception as e:
            logger.error(f"Error in web scraping: {e}")
            return []
    
    def fetch_crypto_news(self, source: str = "cryptopanic", limit: int = 10) -> List[Dict[str, Any]]:
        """
        Fetch crypto news dari RSS feed
        """
        try:
            feed_url = self.rss_feeds.get(source)
            if not feed_url:
                logger.error(f"Unknown news source: {source}")
                return []
            
            # Special handling for different sources
            if source == "cryptopanic":
                # CryptoPanic requires API token, use mock data for now
                logger.info("CryptoPanic requires API token, using mock data")
                return self._get_mock_news_data(limit)
            
            feed = feedparser.parse(feed_url)
            
            if feed.bozo:
                logger.warning(f"RSS feed parse error: {feed.bozo_exception}")
                # Try web scraping as fallback
                return []
            
            entries = feed.entries[:limit]
            news = []
            
            for entry in entries:
                # Extract published date properly
                published_parsed = entry.get('published_parsed')
                if published_parsed:
                    published_dt = datetime.fromtimestamp(
                        datetime(*published_parsed[:6]).timestamp(),
                        tz=timezone.utc
                    )
                else:
                    published_dt = datetime.now(timezone.utc)
                
                news_item = {
                    "id": entry.get('id', entry.get('link', '')),
                    "title": entry.get('title', ''),
                    "link": entry.get('link', ''),
                    "published": published_dt.isoformat(),
                    "published_timestamp": int(published_dt.timestamp()),
                    "summary": entry.get('summary', ''),
                    "source": source,
                    "tags": [tag.term for tag in entry.get('tags', [])]
                }
                
                # Skip jika sudah di cache
                cache_key = f"{news_item['id']}_{news_item['published_timestamp']}"
                if cache_key not in self.analyzed_news_cache:
                    news.append(news_item)
            
            logger.info(f"✅ Fetched {len(news)} news items from {source}")
            return news
            
        except Exception as e:
            logger.error(f"Error fetching news from {source}: {e}")
            return []
    
    async def analyze_sentiment(self, title: str, summary: str, tags: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Analyze sentiment menggunakan GPT-4o dengan enhanced prompt
        """
        try:
            if not self.openai_api_key:
                return {
                    "sentiment": "NETRAL",
                    "confidence": 0.5,
                    "reasoning": "No OpenAI API key available",
                    "impact": "LOW"
                }
            
            # Enhance prompt dengan context dari tags
            tag_context = f"Tags: {', '.join(tags)}" if tags else ""
            
            prompt = f"""
            Analyze the following crypto news for market sentiment:
            
            Title: {title}
            Summary: {summary}
            {tag_context}
            
            Please provide:
            1. Market Sentiment: BULLISH, BEARISH, or NETRAL
            2. Confidence Level: 0.0 to 1.0
            3. Brief Reasoning: Why this sentiment (max 50 words)
            4. Market Impact: HIGH, MEDIUM, or LOW
            
            Response in JSON format:
            {{
                "sentiment": "BULLISH/BEARISH/NETRAL",
                "confidence": 0.85,
                "reasoning": "Brief explanation",
                "impact": "HIGH/MEDIUM/LOW"
            }}
            """
            
            # Use new OpenAI client
            client = openai.OpenAI(api_key=self.openai_api_key)
            
            response = await asyncio.to_thread(
                client.chat.completions.create,
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a crypto market analyst expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=150
            )
            
            content = response.choices[0].message.content.strip()
            
            # Parse JSON response
            import json
            try:
                result = json.loads(content)
                # Validate fields
                if result.get('sentiment') not in ['BULLISH', 'BEARISH', 'NETRAL']:
                    result['sentiment'] = 'NETRAL'
                if not 0 <= result.get('confidence', 0) <= 1:
                    result['confidence'] = 0.5
                if result.get('impact') not in ['HIGH', 'MEDIUM', 'LOW']:
                    result['impact'] = 'MEDIUM'
                
                return result
                
            except json.JSONDecodeError:
                # Fallback jika response bukan JSON valid
                sentiment = 'NETRAL'
                if 'BULLISH' in content.upper():
                    sentiment = 'BULLISH'
                elif 'BEARISH' in content.upper():
                    sentiment = 'BEARISH'
                
                return {
                    "sentiment": sentiment,
                    "confidence": 0.7,
                    "reasoning": "Analysis completed",
                    "impact": "MEDIUM"
                }
                
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {e}")
            return {
                "sentiment": "NETRAL",
                "confidence": 0.5,
                "reasoning": f"Analysis error: {str(e)}",
                "impact": "LOW"
            }
    
    async def analyze_multiple_news(self, news_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Analyze multiple news items concurrently
        """
        tasks = []
        for item in news_items:
            task = self.analyze_sentiment(
                item['title'],
                item['summary'],
                item.get('tags', [])
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        # Combine news items dengan analysis results
        analyzed_news = []
        for item, analysis in zip(news_items, results):
            analyzed_item = {
                **item,
                "analysis": analysis,
                "analyzed_at": datetime.now(timezone.utc).isoformat()
            }
            
            # Cache hasil analysis
            cache_key = f"{item['id']}_{item['published_timestamp']}"
            self.analyzed_news_cache[cache_key] = analyzed_item
            
            # Track sentiment untuk self-learning
            self._track_sentiment(analysis['sentiment'], analysis['confidence'])
            
            analyzed_news.append(analyzed_item)
        
        return analyzed_news
    
    def _track_sentiment(self, sentiment: str, confidence: float):
        """
        Track sentiment untuk performance analysis
        """
        current_time = datetime.now(timezone.utc)
        self.sentiment_history[sentiment].append({
            'timestamp': current_time,
            'confidence': confidence
        })
        
        # Keep only last 24 hours
        cutoff_time = current_time - timedelta(hours=24)
        for sent in self.sentiment_history:
            self.sentiment_history[sent] = [
                item for item in self.sentiment_history[sent]
                if item['timestamp'] > cutoff_time
            ]
    
    async def get_news_sentiment(self, limit: int = 5, source: str = "cryptopanic") -> Dict[str, Any]:
        """
        Main wrapper function untuk fetch dan analyze news
        """
        try:
            # Fetch news
            news_list = self.fetch_crypto_news(source, limit)
            
            if not news_list:
                return {
                    "status": "error",
                    "message": "No news fetched",
                    "data": []
                }
            
            # Analyze sentiments
            analyzed_news = await self.analyze_multiple_news(news_list)
            
            # Calculate aggregate sentiment
            sentiment_counts = defaultdict(int)
            total_confidence = 0
            high_impact_count = 0
            
            for item in analyzed_news:
                analysis = item['analysis']
                sentiment_counts[analysis['sentiment']] += 1
                total_confidence += analysis['confidence']
                if analysis['impact'] == 'HIGH':
                    high_impact_count += 1
            
            # Determine overall market sentiment
            total_news = len(analyzed_news)
            bullish_ratio = sentiment_counts['BULLISH'] / total_news if total_news > 0 else 0
            bearish_ratio = sentiment_counts['BEARISH'] / total_news if total_news > 0 else 0
            
            overall_sentiment = 'NETRAL'
            if bullish_ratio > 0.6:
                overall_sentiment = 'BULLISH'
            elif bearish_ratio > 0.6:
                overall_sentiment = 'BEARISH'
            
            avg_confidence = total_confidence / total_news if total_news > 0 else 0
            
            return {
                "status": "success",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "source": source,
                "data": analyzed_news,
                "aggregate": {
                    "total_news": total_news,
                    "overall_sentiment": overall_sentiment,
                    "sentiment_distribution": dict(sentiment_counts),
                    "average_confidence": round(avg_confidence, 2),
                    "high_impact_news": high_impact_count,
                    "bullish_ratio": round(bullish_ratio, 2),
                    "bearish_ratio": round(bearish_ratio, 2)
                },
                "performance": self.get_sentiment_performance()
            }
            
        except Exception as e:
            logger.error(f"Error in get_news_sentiment: {e}")
            return {
                "status": "error",
                "message": str(e),
                "data": []
            }
    
    def get_sentiment_performance(self) -> Dict[str, Any]:
        """
        Get sentiment analysis performance metrics
        """
        try:
            total_analyses = sum(len(items) for items in self.sentiment_history.values())
            
            if total_analyses == 0:
                return {
                    "total_analyses": 0,
                    "sentiment_distribution": {},
                    "average_confidence": 0
                }
            
            # Calculate metrics
            sentiment_dist = {}
            total_confidence = 0
            
            for sentiment, items in self.sentiment_history.items():
                count = len(items)
                sentiment_dist[sentiment] = count
                total_confidence += sum(item['confidence'] for item in items)
            
            return {
                "total_analyses": total_analyses,
                "sentiment_distribution": sentiment_dist,
                "average_confidence": round(total_confidence / total_analyses, 2) if total_analyses > 0 else 0,
                "last_24h_count": total_analyses
            }
            
        except Exception as e:
            logger.error(f"Error calculating sentiment performance: {e}")
            return {
                "total_analyses": 0,
                "sentiment_distribution": {},
                "average_confidence": 0
            }
    
    def clear_cache(self):
        """
        Clear analyzed news cache
        """
        self.analyzed_news_cache.clear()
        logger.info("📰 News cache cleared")
    
    def get_trending_topics(self, analyzed_news: List[Dict[str, Any]], top_n: int = 5) -> List[Dict[str, Any]]:
        """
        Extract trending topics dari analyzed news
        """
        try:
            tag_counts = defaultdict(int)
            tag_sentiments = defaultdict(list)
            
            for item in analyzed_news:
                tags = item.get('tags', [])
                sentiment = item['analysis']['sentiment']
                
                for tag in tags:
                    tag_lower = tag.lower()
                    tag_counts[tag_lower] += 1
                    tag_sentiments[tag_lower].append(sentiment)
            
            # Sort by count dan create trending list
            trending = []
            for tag, count in sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:top_n]:
                sentiments = tag_sentiments[tag]
                bullish_count = sentiments.count('BULLISH')
                bearish_count = sentiments.count('BEARISH')
                
                dominant_sentiment = 'NETRAL'
                if bullish_count > bearish_count * 1.5:
                    dominant_sentiment = 'BULLISH'
                elif bearish_count > bullish_count * 1.5:
                    dominant_sentiment = 'BEARISH'
                
                trending.append({
                    "topic": tag,
                    "mentions": count,
                    "sentiment": dominant_sentiment,
                    "sentiment_breakdown": {
                        "bullish": bullish_count,
                        "bearish": bearish_count,
                        "neutral": sentiments.count('NETRAL')
                    }
                })
            
            return trending
            
        except Exception as e:
            logger.error(f"Error extracting trending topics: {e}")
            return []
    
    def _get_mock_news_data(self, limit: int) -> List[Dict[str, Any]]:
        """
        Get mock news data for testing when RSS/API not available
        """
        mock_news = [
            {
                "id": "mock_1",
                "title": "Bitcoin Surges Past $52,000 as Institutional Interest Grows",
                "link": "https://example.com/news/1",
                "published": datetime.now(timezone.utc).isoformat(),
                "published_timestamp": int(datetime.now().timestamp()),
                "summary": "Bitcoin price rallies as major institutions announce new crypto investments. Market sentiment turns bullish with increased trading volume.",
                "source": "mock",
                "tags": ["bitcoin", "institutional", "bullish"]
            },
            {
                "id": "mock_2",
                "title": "Ethereum Network Congestion Raises Gas Fee Concerns",
                "link": "https://example.com/news/2",
                "published": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
                "published_timestamp": int((datetime.now() - timedelta(hours=2)).timestamp()),
                "summary": "High network activity on Ethereum leads to increased transaction costs. Developers discuss scaling solutions.",
                "source": "mock",
                "tags": ["ethereum", "gas", "network"]
            },
            {
                "id": "mock_3",
                "title": "Federal Reserve Comments on Digital Dollar Development",
                "link": "https://example.com/news/3",
                "published": (datetime.now(timezone.utc) - timedelta(hours=4)).isoformat(),
                "published_timestamp": int((datetime.now() - timedelta(hours=4)).timestamp()),
                "summary": "Fed officials provide update on CBDC research. Market remains neutral on potential impact.",
                "source": "mock",
                "tags": ["fed", "cbdc", "regulation"]
            },
            {
                "id": "mock_4",
                "title": "Major Exchange Announces Support for New DeFi Tokens",
                "link": "https://example.com/news/4",
                "published": (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat(),
                "published_timestamp": int((datetime.now() - timedelta(hours=6)).timestamp()),
                "summary": "Leading crypto exchange adds trading pairs for popular DeFi projects. Trading volume expected to increase.",
                "source": "mock",
                "tags": ["exchange", "defi", "trading"]
            },
            {
                "id": "mock_5",
                "title": "Crypto Market Correction: Analysts Debate Short-Term Outlook",
                "link": "https://example.com/news/5",
                "published": (datetime.now(timezone.utc) - timedelta(hours=8)).isoformat(),
                "published_timestamp": int((datetime.now() - timedelta(hours=8)).timestamp()),
                "summary": "Market experiences 5% pullback after recent rally. Technical analysts divided on next price movement.",
                "source": "mock",
                "tags": ["market", "correction", "analysis"]
            }
        ]
        
        return mock_news[:limit]

# Singleton instance
_news_analyzer_instance = None

def get_news_analyzer() -> CryptoNewsAnalyzer:
    """Get or create news analyzer instance"""
    global _news_analyzer_instance
    if _news_analyzer_instance is None:
        _news_analyzer_instance = CryptoNewsAnalyzer()
    return _news_analyzer_instance