"""
News Sentiment Analysis API Endpoints (TradeEasy-like)
Provides REST API for crypto news sentiment analysis with AI
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
import logging
import os

# Import the news sentiment engine
from core.news_sentiment_engine import NewsSentimentEngine

# Import API key requirement decorator
from api.auth import require_api_key

logger = logging.getLogger(__name__)

# Create blueprint
news_sentiment_bp = Blueprint('news_sentiment_analysis', __name__)

# Initialize engine (will be done once on app start)
news_sentiment_engine = None

def init_news_sentiment_engine():
    """Initialize news sentiment engine with API keys"""
    global news_sentiment_engine
    try:
        news_api_key = os.getenv("NEWS_API_KEY")
        cryptopanic_key = os.getenv("CRYPTOPANIC_API_KEY")
        use_ai_model = os.getenv("USE_AI_SENTIMENT", "false").lower() == "true"
        
        news_sentiment_engine = NewsSentimentEngine(
            news_api_key=news_api_key,
            cryptopanic_key=cryptopanic_key,
            use_ai_model=use_ai_model
        )
        logger.info("📰 News Sentiment Engine initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize news sentiment engine: {e}")
        return False

# Initialize on import
init_news_sentiment_engine()

@news_sentiment_bp.route('/api/news-sentiment/analyze', methods=['GET'])
@require_api_key
def analyze_news_sentiment():
    """
    Analyze news sentiment for a crypto asset with AI
    
    Query parameters:
    - symbol: Asset symbol (e.g., BTC, ETH)
    - timeframe: Analysis timeframe (1h, 6h, 24h, 7d)
    """
    try:
        symbol = request.args.get('symbol', 'BTC').upper()
        timeframe = request.args.get('timeframe', '24h')
        
        if not news_sentiment_engine:
            if not init_news_sentiment_engine():
                return jsonify({
                    'error': 'NEWS_SENTIMENT_ENGINE_UNAVAILABLE',
                    'message': 'News sentiment analysis engine is not available'
                }), 503
        
        # Perform sentiment analysis
        result = news_sentiment_engine.fetch_and_analyze(symbol, timeframe)
        
        # Add trading signal based on sentiment
        sentiment_score = result.get('aggregate_sentiment', {}).get('score', 0)
        confidence = result.get('aggregate_sentiment', {}).get('confidence', 0)
        
        if sentiment_score > 0.3 and confidence > 0.6:
            signal = "BUY"
            signal_strength = "Strong" if sentiment_score > 0.5 else "Moderate"
        elif sentiment_score < -0.3 and confidence > 0.6:
            signal = "SELL"
            signal_strength = "Strong" if sentiment_score < -0.5 else "Moderate"
        else:
            signal = "HOLD"
            signal_strength = "Neutral"
        
        result['trading_signal'] = {
            'action': signal,
            'strength': signal_strength,
            'confidence': float(confidence * 100)
        }
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"News sentiment analysis error: {e}")
        return jsonify({
            'error': 'SENTIMENT_ANALYSIS_ERROR',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@news_sentiment_bp.route('/api/news-sentiment/market-mood', methods=['GET'])
@require_api_key
def get_overall_market_mood():
    """
    Get overall market mood across multiple assets
    
    Query parameters:
    - assets: Comma-separated list of assets (default: BTC,ETH,SOL)
    """
    try:
        assets_param = request.args.get('assets', 'BTC,ETH,SOL')
        assets = [a.strip().upper() for a in assets_param.split(',')]
        
        if not news_sentiment_engine:
            if not init_news_sentiment_engine():
                return jsonify({
                    'error': 'NEWS_SENTIMENT_ENGINE_UNAVAILABLE',
                    'message': 'News sentiment analysis engine is not available'
                }), 503
        
        # Get market mood
        mood_data = news_sentiment_engine.get_market_mood(assets)
        
        # Add market recommendation
        avg_score = mood_data.get('average_score', 0)
        if avg_score > 0.2:
            recommendation = "Market sentiment is positive. Consider increasing exposure to quality assets."
        elif avg_score < -0.2:
            recommendation = "Market sentiment is negative. Consider risk management and defensive positions."
        else:
            recommendation = "Market sentiment is mixed. Maintain balanced portfolio allocation."
        
        mood_data['recommendation'] = recommendation
        
        return jsonify(mood_data)
        
    except Exception as e:
        logger.error(f"Market mood error: {e}")
        return jsonify({
            'error': 'MARKET_MOOD_ERROR',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@news_sentiment_bp.route('/api/news-sentiment/trending', methods=['GET'])
@require_api_key
def get_trending_crypto_topics():
    """Get trending crypto topics and their sentiment"""
    try:
        if not news_sentiment_engine:
            if not init_news_sentiment_engine():
                return jsonify({
                    'error': 'NEWS_SENTIMENT_ENGINE_UNAVAILABLE',
                    'message': 'News sentiment analysis engine is not available'
                }), 503
        
        # Get trending topics
        trending = news_sentiment_engine.client.get_trending_topics()
        
        # Analyze sentiment for each trending topic
        trending_with_sentiment = []
        for topic in trending[:5]:  # Top 5 trending
            sentiment = news_sentiment_engine.fetch_and_analyze(topic, "1h")
            trending_with_sentiment.append({
                'asset': topic,
                'sentiment': sentiment.get('aggregate_sentiment', {}).get('label', 'Unknown'),
                'score': sentiment.get('aggregate_sentiment', {}).get('score', 0),
                'article_count': sentiment.get('total_articles', 0)
            })
        
        return jsonify({
            'trending_assets': trending_with_sentiment,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Trending topics error: {e}")
        return jsonify({
            'error': 'TRENDING_ERROR',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@news_sentiment_bp.route('/api/news-sentiment/detailed/<symbol>', methods=['GET'])
@require_api_key
def get_detailed_sentiment_analysis(symbol):
    """
    Get detailed news analysis with individual article sentiments
    
    Path parameters:
    - symbol: Asset symbol (e.g., BTC, ETH)
    """
    try:
        symbol = symbol.upper()
        
        if not news_sentiment_engine:
            if not init_news_sentiment_engine():
                return jsonify({
                    'error': 'NEWS_SENTIMENT_ENGINE_UNAVAILABLE',
                    'message': 'News sentiment analysis engine is not available'
                }), 503
        
        # Get detailed analysis
        analysis = news_sentiment_engine.fetch_and_analyze(symbol, "24h", min_articles=10)
        
        # Group articles by sentiment
        articles_by_sentiment = {
            'bullish': [],
            'neutral': [],
            'bearish': []
        }
        
        for article in analysis.get('articles', []):
            sentiment = article.get('sentiment', 'Neutral').lower()
            if sentiment == 'bullish':
                articles_by_sentiment['bullish'].append(article)
            elif sentiment == 'bearish':
                articles_by_sentiment['bearish'].append(article)
            else:
                articles_by_sentiment['neutral'].append(article)
        
        # Add grouped articles to response
        analysis['articles_grouped'] = articles_by_sentiment
        
        # Add sentiment trend
        analysis['sentiment_trend'] = "Improving" if analysis.get('aggregate_sentiment', {}).get('score', 0) > 0 else "Declining"
        
        return jsonify(analysis)
        
    except Exception as e:
        logger.error(f"Detailed analysis error: {e}")
        return jsonify({
            'error': 'ANALYSIS_ERROR',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@news_sentiment_bp.route('/api/news-sentiment/status', methods=['GET'])
def get_sentiment_engine_status():
    """Get news sentiment engine status"""
    try:
        status = {
            'engine_available': news_sentiment_engine is not None,
            'news_api_configured': bool(os.getenv("NEWS_API_KEY")),
            'cryptopanic_configured': bool(os.getenv("CRYPTOPANIC_API_KEY")),
            'ai_model_enabled': os.getenv("USE_AI_SENTIMENT", "false").lower() == "true",
            'cache_entries': len(news_sentiment_engine.cache) if news_sentiment_engine else 0,
            'timestamp': datetime.now().isoformat()
        }
        
        # Test news fetching
        if news_sentiment_engine:
            try:
                test_articles = news_sentiment_engine.client.fetch_articles("BTC", page_size=1)
                status['news_fetch_working'] = len(test_articles) > 0
            except:
                status['news_fetch_working'] = False
        else:
            status['news_fetch_working'] = False
        
        return jsonify(status)
        
    except Exception as e:
        logger.error(f"Status check error: {e}")
        return jsonify({
            'error': 'STATUS_ERROR',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@news_sentiment_bp.route('/api/news-sentiment/clear-cache', methods=['POST'])
@require_api_key
def clear_sentiment_cache():
    """Clear news sentiment cache"""
    try:
        if not news_sentiment_engine:
            return jsonify({
                'error': 'NEWS_SENTIMENT_ENGINE_UNAVAILABLE',
                'message': 'News sentiment analysis engine is not available'
            }), 503
        
        # Clear cache
        news_sentiment_engine.cache.clear()
        news_sentiment_engine.client.cache.clear()
        
        return jsonify({
            'status': 'success',
            'message': 'News sentiment cache cleared',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Cache clear error: {e}")
        return jsonify({
            'error': 'CACHE_CLEAR_ERROR',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# Health check endpoint
@news_sentiment_bp.route('/api/news-sentiment/health', methods=['GET'])
def sentiment_health_check():
    """Simple health check for news sentiment service"""
    return jsonify({
        'status': 'healthy',
        'service': 'news_sentiment_analysis',
        'timestamp': datetime.now().isoformat()
    })