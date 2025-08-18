from flask import Blueprint, jsonify, request
from app import app, db
from models import TradingSignal, TelegramUser
import logging
import os

# Create a main blueprint for core routes
main_bp = Blueprint('main', __name__)
logger = logging.getLogger(__name__)

@main_bp.route('/')
def index():
    """Main index route"""
    return jsonify({
        "message": "Advanced Cryptocurrency GPTs & Telegram Bot API",
        "version": "2.0.0",
        "status": "active",
        "endpoints": [
            "/api/gpts/status",
            "/api/gpts/sinyal/tajam", 
            "/health"
        ]
    })

@main_bp.route('/health')
def health():
    """Health check endpoint"""
    try:
        # Test database connection
        from sqlalchemy import text
        db.session.execute(text('SELECT 1'))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return jsonify({
        "status": "healthy",
        "database": db_status,
        "version": "2.0.0"
    })

# GPTs API Blueprint
gpts_bp = Blueprint('gpts', __name__, url_prefix='/api/gpts')

@gpts_bp.route('/status')
def gpts_status():
    """GPTs API status endpoint"""
    return jsonify({
        "status": "active",
        "api_version": "2.0.0",
        "features": ["signal_analysis", "telegram_integration"],
        "supported_symbols": ["BTC-USDT", "ETH-USDT", "SOL-USDT"]
    })

@gpts_bp.route('/sinyal/tajam', methods=['POST'])
def get_sharp_signal():
    """Sharp signal analysis endpoint for GPTs"""
    try:
        data = request.get_json() or {}
        symbol = data.get('symbol', 'BTC-USDT')
        timeframe = data.get('timeframe', '1H')
        
        # Basic response for now - will be enhanced with actual signal logic
        response = {
            "status": "success",
            "symbol": symbol,
            "timeframe": timeframe,
            "signal": {
                "direction": "BUY",
                "confidence": 0.75,
                "entry_price": 45000.0,
                "take_profit": 47000.0,
                "stop_loss": 43000.0
            },
            "analysis": {
                "technical": "RSI oversold, MACD bullish crossover",
                "smc": "Price at premium discount zone",
                "reasoning": "Strong buy signal based on technical confluence"
            },
            "timestamp": "2025-08-18T11:45:00Z"
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error in sharp signal endpoint: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Failed to generate signal",
            "error": str(e)
        }), 500

# Register blueprints with the app
app.register_blueprint(main_bp)
app.register_blueprint(gpts_bp)