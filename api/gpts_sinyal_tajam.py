"""
GPTs Sinyal Tajam Endpoint - Sharp Trading Signals for ChatGPT
"""

from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
import logging
from datetime import datetime

# Blueprint initialization
gpts_sinyal_bp = Blueprint("gpts_sinyal", __name__)
logger = logging.getLogger(__name__)

@gpts_sinyal_bp.route("/api/gpts/sinyal/tajam", methods=["GET", "POST"])
@cross_origin()
def get_sinyal_tajam():
    """
    Get sharp trading signal dengan real-time data
    Supports both GET and POST methods for ChatGPT compatibility
    """
    try:
        # Handle both GET and POST requests
        if request.method == 'POST':
            data = request.get_json() or {}
            symbol = data.get('symbol', 'BTC-USDT')
            timeframe = data.get('timeframe', '1H')
        else:
            symbol = request.args.get('symbol', 'BTC-USDT')
            timeframe = request.args.get('timeframe', '1H')
        
        # Get real-time data from OKX
        from core.okx_hybrid_fetcher import OKXHybridFetcher
        fetcher = OKXHybridFetcher()
        
        # Normalize symbol for OKX
        okx_symbol = symbol.replace('USDT', '-USDT') if '-' not in symbol else symbol
        price_data = fetcher.get_price_data(okx_symbol)
        
        if price_data:
            market_data = {
                'last': price_data.price,
                'changePercent24h': price_data.price_change_24h,
                'volume24h': price_data.volume_24h
            }
        else:
            market_data = None
        
        if not market_data:
            return jsonify({
                "status": "error",
                "message": "Could not fetch market data"
            }), 500
        
        # Generate sharp signal based on real-time data
        current_price = float(market_data.get('last', 0))
        change_24h = float(market_data.get('changePercent24h', 0))
        volume_24h = float(market_data.get('volume24h', 0))
        
        # Determine signal based on market conditions
        if change_24h > 5:
            signal = "STRONG_BUY"
            confidence = min(85 + (change_24h / 2), 95)
            action = "LONG"
        elif change_24h > 2:
            signal = "BUY"
            confidence = 70 + change_24h
            action = "LONG"
        elif change_24h < -5:
            signal = "STRONG_SELL"
            confidence = min(85 + abs(change_24h / 2), 95)
            action = "SHORT"
        elif change_24h < -2:
            signal = "SELL"
            confidence = 70 + abs(change_24h)
            action = "SHORT"
        else:
            signal = "NEUTRAL"
            confidence = 60
            action = "WAIT"
        
        # Calculate levels
        stop_loss_pct = 2.0 if confidence > 80 else 3.0
        take_profit_pct = 4.0 if confidence > 80 else 3.0
        
        if action == "LONG":
            stop_loss = current_price * (1 - stop_loss_pct / 100)
            take_profit = current_price * (1 + take_profit_pct / 100)
        elif action == "SHORT":
            stop_loss = current_price * (1 + stop_loss_pct / 100)
            take_profit = current_price * (1 - take_profit_pct / 100)
        else:
            stop_loss = current_price * 0.97
            take_profit = current_price * 1.03
        
        response = {
            "status": "success",
            "symbol": symbol,
            "timeframe": timeframe,
            "signal": {
                "action": action,
                "signal": signal,
                "confidence": round(confidence, 1),
                "entry_price": round(current_price, 2),
                "stop_loss": round(stop_loss, 2),
                "take_profit": round(take_profit, 2),
                "risk_reward_ratio": round(take_profit_pct / stop_loss_pct, 2)
            },
            "market_data": {
                "current_price": round(current_price, 2),
                "change_24h": round(change_24h, 2),
                "volume_24h": round(volume_24h, 2)
            },
            "analysis": {
                "trend": "BULLISH" if change_24h > 0 else "BEARISH",
                "volatility": "HIGH" if abs(change_24h) > 5 else "MEDIUM" if abs(change_24h) > 2 else "LOW",
                "volume_status": "HIGH" if volume_24h > 1000000 else "NORMAL"
            },
            "reasoning": f"{'Strong bullish momentum' if signal.startswith('STRONG_BUY') else 'Bullish trend' if signal == 'BUY' else 'Strong bearish pressure' if signal.startswith('STRONG_SELL') else 'Bearish trend' if signal == 'SELL' else 'Sideways market'} with {round(change_24h, 1)}% 24h change",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error in sinyal tajam: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500