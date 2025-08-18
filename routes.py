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

@main_bp.route('/api/openapi_schema')
def api_openapi_schema():
    """OpenAPI schema endpoint with fixed path"""
    return jsonify({
        "openapi": "3.1.0",
        "info": {
            "title": "Cryptocurrency Trading Signals API",
            "description": "API untuk analisis trading cryptocurrency dengan Smart Money Concept",
            "version": "1.0.0"
        },
        "servers": [{"url": "https://your-replit-url.replit.dev"}],
        "paths": {
            "/api/gpts/status": {"get": {"summary": "System status"}},
            "/api/gpts/signal": {"get": {"summary": "Trading signals"}},
            "/api/gpts/market-data": {"get": {"summary": "Market data"}},
            "/api/gpts/smc-analysis": {"get": {"summary": "SMC analysis"}},
            "/api/smc/zones": {"get": {"summary": "SMC zones"}}
        }
    })

@main_bp.route('/openapi.json')
def openapi_json():
    """Redirect to proper schema endpoint"""
    return jsonify({
        "message": "Use /api/openapi_schema for OpenAPI schema",
        "schema_url": "/api/openapi_schema"
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
except ImportError as e:
    logger.warning(f"Promptbook blueprint not available: {e}")
    promptbook_available = False
    promptbook_bp = None

try:
    from api.performance_endpoints import performance_bp
    performance_available = True
except ImportError as e:
    logger.warning(f"Performance blueprint not available: {e}")
    performance_available = False
    performance_bp = None

try:
    from api.news_endpoints import news_api
    news_available = True
except ImportError as e:
    logger.warning(f"News API blueprint not available: {e}")
    news_available = False
    news_api = None

try:
    from api.missing_gpts_endpoints import missing_gpts_bp
    missing_gpts_available = True
except ImportError as e:
    logger.warning(f"Missing GPTs endpoints not available: {e}")
    missing_gpts_available = False
    missing_gpts_bp = None

try:
    from api.smc_endpoints import smc_context_bp
    smc_context_available = True
except ImportError as e:
    logger.warning(f"SMC context blueprint not available: {e}")
    smc_context_available = False
    smc_context_bp = None

try:
    from api.enhanced_signal_endpoints import enhanced_signals_bp
    enhanced_signals_available = True
except ImportError as e:
    logger.warning(f"Enhanced signals blueprint not available: {e}")
    enhanced_signals_available = False
    enhanced_signals_bp = None

try:
    from api.institutional_endpoints import institutional_bp
    institutional_available = True
except ImportError as e:
    logger.warning(f"Institutional blueprint not available: {e}")
    institutional_available = False
    institutional_bp = None

# Register core blueprints with the app
app.register_blueprint(main_bp)
app.register_blueprint(gpts_api)  # Use enhanced GPTs API from gpts_routes.py
app.register_blueprint(smc_zones_bp)  # Register SMC zones endpoint

# Register additional blueprints if available
if promptbook_available and promptbook_bp:
    app.register_blueprint(promptbook_bp)
    logger.info("✅ Promptbook blueprint registered")

if performance_available and performance_bp:
    app.register_blueprint(performance_bp)
    logger.info("✅ Performance blueprint registered")

if news_available and news_api:
    app.register_blueprint(news_api)
    logger.info("✅ News API blueprint registered")

if missing_gpts_available and missing_gpts_bp:
    app.register_blueprint(missing_gpts_bp)
    logger.info("✅ Missing GPTs endpoints registered")

if smc_context_available and smc_context_bp:
    app.register_blueprint(smc_context_bp)
    logger.info("✅ SMC context blueprint registered")

if enhanced_signals_available and enhanced_signals_bp:
    app.register_blueprint(enhanced_signals_bp)
    logger.info("✅ Enhanced signals blueprint registered")

if institutional_available and institutional_bp:
    app.register_blueprint(institutional_bp)
    logger.info("✅ Institutional blueprint registered")