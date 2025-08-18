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
            "/api/gpts/market-data", 
            "/api/gpts/smc-analysis",
            "/api/gpts/ticker/<symbol>",
            "/api/gpts/orderbook/<symbol>",
            "/api/gpts/smc-zones/<symbol>",
            "/api/smc/zones",
            "/api/promptbook/",
            "/api/performance/stats",
            "/api/news/status",
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

# Enhanced GPTs API will be imported from gpts_routes.py

# Import and register the enhanced GPTs blueprint
from gpts_routes import gpts_api

# Import SMC zones blueprint
from api.smc_zones_endpoints import smc_zones_bp

# Import additional blueprints for comprehensive API coverage
try:
    from api.promptbook import promptbook_bp
    promptbook_available = True
except ImportError:
    promptbook_available = False

try:
    from api.performance_endpoints import performance_bp
    performance_available = True
except ImportError:
    performance_available = False

try:
    from api.news_endpoints import news_api
    news_available = True
except ImportError:
    news_available = False

# Register core blueprints with the app
app.register_blueprint(main_bp)
app.register_blueprint(gpts_api)  # Use enhanced GPTs API from gpts_routes.py
app.register_blueprint(smc_zones_bp)  # Register SMC zones endpoint

# Register additional blueprints if available
if promptbook_available:
    app.register_blueprint(promptbook_bp)
    logger.info("✅ Promptbook blueprint registered")

if performance_available:
    app.register_blueprint(performance_bp)
    logger.info("✅ Performance blueprint registered")

if news_available:
    app.register_blueprint(news_api)
    logger.info("✅ News API blueprint registered")