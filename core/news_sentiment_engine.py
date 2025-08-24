"""
News Sentiment Analysis Engine for Crypto Assets
Provides sentiment analysis, impact assessment, and market narrative generation
"""

import os
import logging
from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta
import re
from collections import Counter
import numpy as np

# Import news API client
from core.utils.news_api_client import NewsAPIClient

# Setup logger
logger = logging.getLogger(__name__)

# For sentiment analysis - using lightweight VADER as default
try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    VADER_AVAILABLE = True
except ImportError:
    VADER_AVAILABLE = False
    logger.warning("VADER sentiment not available, using basic analysis")

# Optional: Use transformers for advanced sentiment (heavier dependency)
try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

logger = logging.getLogger(__name__)

class NewsSentimentEngine:
    """
    Advanced news sentiment analysis engine for crypto trading
    Features: Multi-source aggregation, sentiment scoring, impact assessment
    """
    
    def __init__(self, news_api_key: str = None, cryptopanic_key: str = None, use_ai_model: bool = False):
        # Initialize news client
        self.client = NewsAPIClient(news_api_key, cryptopanic_key)
        
        # Sentiment analyzer selection
        self.use_ai_model = use_ai_model and TRANSFORMERS_AVAILABLE
        
        if self.use_ai_model:
            # Use transformer model for advanced sentiment
            self.sentiment_model = pipeline(
                "sentiment-analysis", 
                model="ProsusAI/finbert"  # Financial sentiment model
            )
            logger.info("Using FinBERT transformer for sentiment analysis")
        elif VADER_AVAILABLE:
            # Use VADER for lightweight sentiment
            self.sentiment_analyzer = SentimentIntensityAnalyzer()
            logger.info("Using VADER for sentiment analysis")
        else:
            # Fallback to basic keyword-based sentiment
            self.sentiment_analyzer = None
            logger.info("Using basic keyword sentiment analysis")
        
        # Keywords for crypto sentiment
        self.bullish_keywords = {
            'surge', 'rally', 'bullish', 'breakout', 'soar', 'moon', 'pump',
            'adoption', 'institutional', 'upgrade', 'partnership', 'integration',
            'record high', 'all-time high', 'breakthrough', 'positive', 'growth'
        }
        
        self.bearish_keywords = {
            'crash', 'dump', 'bearish', 'plunge', 'collapse', 'correction',
            'hack', 'exploit', 'regulation', 'ban', 'lawsuit', 'investigation',
            'selloff', 'fear', 'uncertainty', 'negative', 'decline', 'warning'
        }
        
        # High impact sources
        self.high_impact_sources = {
            'reuters', 'bloomberg', 'coindesk', 'cointelegraph', 'wsj',
            'financial times', 'cnbc', 'forbes', 'sec', 'fed'
        }
        
        # Cache for results
        self.cache = {}
        self.cache_duration = 600  # 10 minutes
    
    def fetch_and_analyze(self, asset_keyword: str, 
                         timeframe: str = "24h",
                         min_articles: int = 5) -> Dict:
        """
        Main method: Fetch news and perform comprehensive sentiment analysis
        """
        try:
            # Check cache
            cache_key = f"{asset_keyword}_{timeframe}"
            if cache_key in self.cache:
                cached_time, cached_data = self.cache[cache_key]
                if datetime.now().timestamp() - cached_time < self.cache_duration:
                    logger.info(f"Using cached sentiment for {asset_keyword}")
                    cached_data["cached"] = True
                    return cached_data
            
            # Fetch articles
            articles = self.client.fetch_articles(asset_keyword, page_size=20)
            
            if len(articles) < min_articles:
                logger.warning(f"Only {len(articles)} articles found for {asset_keyword}")
            
            # Analyze each article
            analyzed_articles = []
            sentiments = []
            impacts = []
            
            for article in articles:
                analysis = self._analyze_article(article)
                analyzed_articles.append(analysis)
                sentiments.append(analysis["sentiment_score"])
                impacts.append(analysis["impact_score"])
            
            # Calculate aggregate metrics
            aggregate = self._calculate_aggregate_sentiment(sentiments, impacts)
            
            # Generate market narrative
            narrative = self._generate_narrative(asset_keyword, analyzed_articles, aggregate)
            
            # Identify key themes
            themes = self._extract_themes(analyzed_articles)
            
            result = {
                "asset": asset_keyword,
                "timestamp": datetime.now().isoformat(),
                "timeframe": timeframe,
                "total_articles": len(analyzed_articles),
                "aggregate_sentiment": aggregate,
                "market_narrative": narrative,
                "key_themes": themes,
                "articles": analyzed_articles[:10],  # Top 10 articles
                "cached": False
            }
            
            # Cache the result
            self.cache[cache_key] = (datetime.now().timestamp(), result)
            
            return result
            
        except Exception as e:
            logger.error(f"News sentiment analysis error: {e}")
            return self._get_fallback_response(asset_keyword)
    
    def _analyze_article(self, article: Dict) -> Dict:
        """Analyze individual article for sentiment and impact"""
        try:
            # Combine title and description for analysis
            text = f"{article.get('title', '')} {article.get('description', '')}"
            
            # Sentiment analysis
            sentiment_data = self._calculate_sentiment(text)
            
            # Impact assessment
            impact_score = self._estimate_impact(article)
            
            # Extract key points
            key_points = self._extract_key_points(text)
            
            return {
                "title": article.get("title", ""),
                "url": article.get("url", ""),
                "source": article.get("source", "Unknown"),
                "published_at": article.get("published_at", ""),
                "sentiment": sentiment_data["label"],
                "sentiment_score": sentiment_data["score"],
                "confidence": sentiment_data["confidence"],
                "impact": self._score_to_impact_label(impact_score),
                "impact_score": impact_score,
                "key_points": key_points,
                "summary": article.get("description", "")[:200]
            }
        except Exception as e:
            logger.warning(f"Article analysis error: {e}")
            return {
                "title": article.get("title", ""),
                "url": article.get("url", ""),
                "sentiment": "Neutral",
                "sentiment_score": 0,
                "impact": "Low",
                "impact_score": 0.3
            }
    
    def _calculate_sentiment(self, text: str) -> Dict:
        """Calculate sentiment score and label"""
        if self.use_ai_model:
            # Use transformer model
            try:
                result = self.sentiment_model(text[:512])[0]
                label = result["label"]
                score = result["score"]
                
                # Map FinBERT labels to our schema
                if "positive" in label.lower():
                    return {"label": "Bullish", "score": score, "confidence": score}
                elif "negative" in label.lower():
                    return {"label": "Bearish", "score": -score, "confidence": score}
                else:
                    return {"label": "Neutral", "score": 0, "confidence": score}
            except:
                pass
        
        if VADER_AVAILABLE and self.sentiment_analyzer:
            # Use VADER sentiment
            scores = self.sentiment_analyzer.polarity_scores(text)
            compound = scores['compound']
            
            if compound >= 0.1:
                label = "Bullish"
            elif compound <= -0.1:
                label = "Bearish"
            else:
                label = "Neutral"
            
            confidence = abs(compound)
            return {"label": label, "score": compound, "confidence": confidence}
        
        # Fallback: Keyword-based sentiment
        text_lower = text.lower()
        bullish_count = sum(1 for word in self.bullish_keywords if word in text_lower)
        bearish_count = sum(1 for word in self.bearish_keywords if word in text_lower)
        
        if bullish_count > bearish_count:
            score = min(bullish_count * 0.2, 1.0)
            return {"label": "Bullish", "score": score, "confidence": 0.6}
        elif bearish_count > bullish_count:
            score = -min(bearish_count * 0.2, 1.0)
            return {"label": "Bearish", "score": score, "confidence": 0.6}
        else:
            return {"label": "Neutral", "score": 0, "confidence": 0.5}
    
    def _estimate_impact(self, article: Dict) -> float:
        """Estimate article impact (0-1 scale)"""
        impact_score = 0.3  # Base score
        
        # Source credibility
        source = article.get("source", "").lower()
        for high_impact in self.high_impact_sources:
            if high_impact in source:
                impact_score += 0.3
                break
        
        # Content length (longer = more detailed = higher impact)
        content_length = len(article.get("content", ""))
        if content_length > 1000:
            impact_score += 0.2
        elif content_length > 500:
            impact_score += 0.1
        
        # Recency (newer = higher impact)
        try:
            published = article.get("published_at", "")
            if published:
                pub_date = datetime.fromisoformat(published.replace("Z", "+00:00"))
                hours_ago = (datetime.now() - pub_date.replace(tzinfo=None)).total_seconds() / 3600
                if hours_ago < 1:
                    impact_score += 0.2
                elif hours_ago < 6:
                    impact_score += 0.1
        except:
            pass
        
        # Engagement (if available from CryptoPanic)
        votes = article.get("votes", {})
        if votes:
            total_votes = sum(votes.values())
            if total_votes > 100:
                impact_score += 0.2
            elif total_votes > 50:
                impact_score += 0.1
        
        return min(impact_score, 1.0)
    
    def _score_to_impact_label(self, score: float) -> str:
        """Convert impact score to label"""
        if score >= 0.7:
            return "High"
        elif score >= 0.4:
            return "Medium"
        else:
            return "Low"
    
    def _extract_key_points(self, text: str) -> List[str]:
        """Extract key points from article text"""
        key_points = []
        
        # Look for price mentions
        price_pattern = r'\$[\d,]+\.?\d*'
        prices = re.findall(price_pattern, text)
        if prices:
            key_points.append(f"Price mentioned: {', '.join(prices[:2])}")
        
        # Look for percentage changes
        percent_pattern = r'[\d]+\.?\d*%'
        percentages = re.findall(percent_pattern, text)
        if percentages:
            key_points.append(f"Change: {', '.join(percentages[:2])}")
        
        # Look for important keywords
        important_keywords = ['partnership', 'acquisition', 'regulation', 'hack', 
                             'launch', 'upgrade', 'adoption', 'institutional']
        for keyword in important_keywords:
            if keyword in text.lower():
                key_points.append(f"Topic: {keyword.capitalize()}")
                break
        
        return key_points[:3]  # Max 3 key points
    
    def _calculate_aggregate_sentiment(self, sentiments: List[float], 
                                      impacts: List[float]) -> Dict:
        """Calculate weighted aggregate sentiment"""
        if not sentiments:
            return {
                "score": 0,
                "label": "Neutral",
                "confidence": 0,
                "distribution": {"bullish": 0, "neutral": 100, "bearish": 0}
            }
        
        # Weight sentiments by impact
        weights = np.array(impacts) if impacts else np.ones(len(sentiments))
        weighted_sentiment = np.average(sentiments, weights=weights)
        
        # Count distribution
        bullish = sum(1 for s in sentiments if s > 0.1)
        bearish = sum(1 for s in sentiments if s < -0.1)
        neutral = len(sentiments) - bullish - bearish
        
        total = len(sentiments)
        distribution = {
            "bullish": int(bullish / total * 100),
            "neutral": int(neutral / total * 100),
            "bearish": int(bearish / total * 100)
        }
        
        # Determine label
        if weighted_sentiment > 0.1:
            label = "Bullish"
        elif weighted_sentiment < -0.1:
            label = "Bearish"
        else:
            label = "Neutral"
        
        # Calculate confidence
        confidence = min(abs(weighted_sentiment) * 2, 1.0)
        
        return {
            "score": float(weighted_sentiment),
            "label": label,
            "confidence": float(confidence),
            "distribution": distribution
        }
    
    def _generate_narrative(self, asset: str, articles: List[Dict], 
                          aggregate: Dict) -> str:
        """Generate market narrative based on sentiment analysis"""
        sentiment_label = aggregate["label"]
        confidence = aggregate["confidence"]
        distribution = aggregate["distribution"]
        
        # Start with overall sentiment
        if sentiment_label == "Bullish":
            narrative = f"Market sentiment for {asset} is currently BULLISH"
        elif sentiment_label == "Bearish":
            narrative = f"Market sentiment for {asset} is currently BEARISH"
        else:
            narrative = f"Market sentiment for {asset} is currently NEUTRAL"
        
        narrative += f" with {confidence*100:.0f}% confidence. "
        
        # Add distribution info
        narrative += f"News analysis shows {distribution['bullish']}% positive, "
        narrative += f"{distribution['neutral']}% neutral, and {distribution['bearish']}% negative coverage. "
        
        # Add high impact article summary
        high_impact = [a for a in articles if a.get("impact_score", 0) > 0.6]
        if high_impact:
            top_article = high_impact[0]
            narrative += f"Key headline: '{top_article['title'][:100]}...' "
            narrative += f"from {top_article.get('source', 'news source')}."
        
        return narrative
    
    def _extract_themes(self, articles: List[Dict]) -> List[str]:
        """Extract common themes from articles"""
        all_text = " ".join([a.get("title", "") + " " + a.get("summary", "") 
                           for a in articles])
        
        # Common crypto themes to look for
        themes = []
        theme_keywords = {
            "Institutional Adoption": ["institutional", "etf", "fund", "investment"],
            "Regulatory News": ["regulation", "sec", "government", "legal"],
            "Technical Development": ["upgrade", "update", "launch", "development"],
            "Market Movement": ["rally", "crash", "surge", "correction"],
            "Partnership/Integration": ["partnership", "integration", "collaboration"],
            "Security Concerns": ["hack", "exploit", "security", "breach"]
        }
        
        text_lower = all_text.lower()
        for theme, keywords in theme_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                themes.append(theme)
        
        return themes[:3]  # Top 3 themes
    
    def _get_fallback_response(self, asset: str) -> Dict:
        """Fallback response when analysis fails"""
        return {
            "asset": asset,
            "timestamp": datetime.now().isoformat(),
            "aggregate_sentiment": {
                "score": 0,
                "label": "Neutral",
                "confidence": 0,
                "distribution": {"bullish": 33, "neutral": 34, "bearish": 33}
            },
            "market_narrative": f"Unable to fetch news sentiment for {asset} at this time.",
            "articles": [],
            "error": True
        }
    
    def get_market_mood(self, assets: List[str] = None) -> Dict:
        """Get overall market mood across multiple assets"""
        if not assets:
            assets = ["BTC", "ETH", "SOL"]
        
        results = []
        for asset in assets:
            sentiment = self.fetch_and_analyze(asset)
            results.append({
                "asset": asset,
                "sentiment": sentiment["aggregate_sentiment"]["label"],
                "score": sentiment["aggregate_sentiment"]["score"]
            })
        
        # Calculate overall mood
        avg_score = np.mean([r["score"] for r in results])
        
        if avg_score > 0.1:
            mood = "Bullish"
        elif avg_score < -0.1:
            mood = "Bearish"
        else:
            mood = "Neutral"
        
        return {
            "overall_mood": mood,
            "average_score": float(avg_score),
            "assets_analyzed": results,
            "timestamp": datetime.now().isoformat()
        }