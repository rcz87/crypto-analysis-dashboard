"""
API Endpoints untuk Crypto News Analyzer
Integrasi dengan GPTs system
"""

from flask import Blueprint, jsonify, request
from core.crypto_news_analyzer import get_news_analyzer
from core.api_auth_layer import require_api_key
import logging
import asyncio

logger = logging.getLogger(__name__)

# Create blueprint
news_api = Blueprint('news_api', __name__)

@news_api.route('/api/news/status', methods=['GET'])
def news_status():
    """
    Get news analyzer status - No auth required
    """
    try:
        analyzer = get_news_analyzer()
        
        # Basic health check
        return jsonify({
            "status": "active",
            "analyzer_initialized": True,
            "openai_available": bool(analyzer.openai_api_key),
            "available_sources": ["cryptopanic", "coindesk", "cointelegraph"],
            "features": [
                "sentiment_analysis",
                "trending_topics", 
                "performance_tracking",
                "cache_management"
            ],
            "api_version": "1.0.0"
        })
        
    except Exception as e:
        logger.error(f"Error in news status: {e}")
        return jsonify({
            "status": "error", 
            "message": str(e),
            "analyzer_initialized": False,
            "api_version": "1.0.0"
        })

@news_api.route('/api/news/latest', methods=['GET'])  
def news_latest():
    """
    Get latest crypto news - No auth required, limited data
    """
    try:
        # Get parameters
        limit = min(int(request.args.get('limit', 3)), 5)  # Max 5 for public
        
        # Get news analyzer
        analyzer = get_news_analyzer()
        
        # Get basic news (without sentiment analysis to avoid OpenAI costs)
        news_list = analyzer.fetch_crypto_news('cryptopanic', limit)
        
        return jsonify({
            "status": "success",
            "data": news_list,
            "count": len(news_list),
            "note": "Basic news data. Use /api/news/sentiment for AI analysis"
        })
        
    except Exception as e:
        logger.error(f"Error in news latest: {e}")
        return jsonify({
            "status": "error",
            "message": "Internal server error"
        }), 500

@news_api.route('/api/news/sentiment', methods=['GET'])
def get_news_sentiment():
    """
    Get crypto news dengan sentiment analysis
    
    Query Parameters:
    - limit: jumlah berita (default: 5, max: 20)
    - source: news source (default: cryptopanic)
    """
    try:
        # Get parameters
        limit = min(int(request.args.get('limit', 5)), 20)
        source = request.args.get('source', 'cryptopanic')
        
        # Get news analyzer
        analyzer = get_news_analyzer()
        
        # Get news dengan sentiment
        result = asyncio.run(analyzer.get_news_sentiment(limit=limit, source=source))
        
        return jsonify(result)
        
    except ValueError as e:
        return jsonify({
            "status": "error",
            "message": f"Invalid parameter: {str(e)}"
        }), 400
    except Exception as e:
        logger.error(f"Error in get_news_sentiment endpoint: {e}")
        return jsonify({
            "status": "error",
            "message": "Internal server error"
        }), 500

@news_api.route('/api/news/trending', methods=['GET'])
def get_trending_topics():
    """
    Get trending crypto topics dengan sentiment
    """
    try:
        # Get parameters
        limit = min(int(request.args.get('limit', 5)), 10)
        top_n = min(int(request.args.get('top_n', 5)), 10)
        
        # Get news analyzer
        analyzer = get_news_analyzer()
        
        # Get news first
        news_result = asyncio.run(analyzer.get_news_sentiment(limit=limit))
        
        if news_result['status'] != 'success':
            return jsonify(news_result), 400
        
        # Extract trending topics
        trending = analyzer.get_trending_topics(news_result['data'], top_n=top_n)
        
        return jsonify({
            "status": "success",
            "data": trending,
            "timestamp": news_result['timestamp']
        })
        
    except Exception as e:
        logger.error(f"Error in get_trending_topics endpoint: {e}")
        return jsonify({
            "status": "error",
            "message": "Internal server error"
        }), 500

@news_api.route('/api/news/performance', methods=['GET'])
@require_api_key(['news_read', 'admin'])
def get_news_performance():
    """
    Get news analyzer performance metrics
    """
    try:
        analyzer = get_news_analyzer()
        performance = analyzer.get_sentiment_performance()
        
        return jsonify({
            "status": "success",
            "data": performance
        })
        
    except Exception as e:
        logger.error(f"Error in get_news_performance endpoint: {e}")
        return jsonify({
            "status": "error",
            "message": "Internal server error"
        }), 500

@news_api.route('/api/news/clear-cache', methods=['POST'])
@require_api_key(['admin'])
def clear_news_cache():
    """
    Clear news analyzer cache (admin only)
    """
    try:
        analyzer = get_news_analyzer()
        analyzer.clear_cache()
        
        return jsonify({
            "status": "success",
            "message": "News cache cleared successfully"
        })
        
    except Exception as e:
        logger.error(f"Error clearing news cache: {e}")
        return jsonify({
            "status": "error",
            "message": "Internal server error"
        }), 500

@news_api.route('/api/gpts/news-analysis', methods=['POST'])
@require_api_key(['gpts_access', 'news_read'])
def gpts_news_analysis():
    """
    Special endpoint untuk GPTs integration
    Analyze news impact untuk trading decisions
    """
    try:
        data = request.get_json()
        
        # Parameters
        symbol = data.get('symbol', 'BTC')
        timeframe = data.get('timeframe', '1H')
        
        # Get news analyzer
        analyzer = get_news_analyzer()
        
        # Get latest news
        news_result = asyncio.run(analyzer.get_news_sentiment(limit=10))
        
        if news_result['status'] != 'success':
            return jsonify(news_result), 400
        
        # Analyze news impact untuk symbol
        aggregate = news_result['aggregate']
        
        # Create trading context berdasarkan news
        news_context = {
            "symbol": symbol,
            "timeframe": timeframe,
            "news_sentiment": aggregate['overall_sentiment'],
            "sentiment_strength": aggregate['average_confidence'],
            "high_impact_count": aggregate['high_impact_news'],
            "market_context": _determine_market_context(aggregate),
            "trading_bias": _determine_trading_bias(aggregate),
            "risk_adjustment": _calculate_risk_adjustment(aggregate)
        }
        
        # Get trending topics related to symbol
        trending = analyzer.get_trending_topics(news_result['data'], top_n=3)
        
        return jsonify({
            "status": "success",
            "data": {
                "news_context": news_context,
                "latest_news": news_result['data'][:5],  # Top 5 news
                "trending_topics": trending,
                "aggregate_sentiment": aggregate,
                "recommendation": _generate_recommendation(news_context, aggregate)
            }
        })
        
    except Exception as e:
        logger.error(f"Error in gpts_news_analysis: {e}")
        return jsonify({
            "status": "error",
            "message": "Internal server error"
        }), 500

def _determine_market_context(aggregate: dict) -> str:
    """Determine market context dari news sentiment"""
    if aggregate['overall_sentiment'] == 'BULLISH' and aggregate['average_confidence'] > 0.7:
        return "STRONG_BULLISH_NEWS"
    elif aggregate['overall_sentiment'] == 'BEARISH' and aggregate['average_confidence'] > 0.7:
        return "STRONG_BEARISH_NEWS"
    elif aggregate['high_impact_news'] >= 3:
        return "HIGH_VOLATILITY_EXPECTED"
    else:
        return "NORMAL_MARKET_CONDITIONS"

def _determine_trading_bias(aggregate: dict) -> str:
    """Determine trading bias dari news"""
    bullish_ratio = aggregate['bullish_ratio']
    bearish_ratio = aggregate['bearish_ratio']
    
    if bullish_ratio > 0.7:
        return "STRONG_LONG_BIAS"
    elif bullish_ratio > 0.55:
        return "MODERATE_LONG_BIAS"
    elif bearish_ratio > 0.7:
        return "STRONG_SHORT_BIAS"
    elif bearish_ratio > 0.55:
        return "MODERATE_SHORT_BIAS"
    else:
        return "NEUTRAL_BIAS"

def _calculate_risk_adjustment(aggregate: dict) -> float:
    """Calculate risk adjustment factor berdasarkan news"""
    base_risk = 1.0
    
    # High impact news increase risk
    if aggregate['high_impact_news'] >= 3:
        base_risk *= 1.3
    elif aggregate['high_impact_news'] >= 1:
        base_risk *= 1.1
    
    # Low confidence increase risk
    if aggregate['average_confidence'] < 0.5:
        base_risk *= 1.2
    
    # Mixed sentiment increase risk
    if aggregate['overall_sentiment'] == 'NEUTRAL':
        base_risk *= 1.1
    
    return round(min(base_risk, 1.5), 2)  # Cap at 1.5x

def _generate_recommendation(context: dict, aggregate: dict) -> dict:
    """Generate trading recommendation based on news"""
    recommendation = {
        "action": "WAIT",
        "confidence": 0.5,
        "reasoning": ""
    }
    
    market_context = context['market_context']
    trading_bias = context['trading_bias']
    
    if market_context == "STRONG_BULLISH_NEWS" and trading_bias in ["STRONG_LONG_BIAS", "MODERATE_LONG_BIAS"]:
        recommendation = {
            "action": "CONSIDER_LONG",
            "confidence": aggregate['average_confidence'],
            "reasoning": f"Strong bullish news sentiment ({aggregate['bullish_ratio']*100:.0f}% bullish) supports long positions"
        }
    elif market_context == "STRONG_BEARISH_NEWS" and trading_bias in ["STRONG_SHORT_BIAS", "MODERATE_SHORT_BIAS"]:
        recommendation = {
            "action": "CONSIDER_SHORT",
            "confidence": aggregate['average_confidence'],
            "reasoning": f"Strong bearish news sentiment ({aggregate['bearish_ratio']*100:.0f}% bearish) supports short positions"
        }
    elif market_context == "HIGH_VOLATILITY_EXPECTED":
        recommendation = {
            "action": "REDUCE_POSITION_SIZE",
            "confidence": 0.8,
            "reasoning": f"{aggregate['high_impact_news']} high-impact news detected, expect increased volatility"
        }
    else:
        recommendation = {
            "action": "WAIT_FOR_CLARITY",
            "confidence": 0.6,
            "reasoning": "Mixed news sentiment suggests waiting for clearer market direction"
        }
    
    return recommendation