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
            "/api/v1/ai-reasoning/health",
            "/api/v1/ai-reasoning/test-reasoning",
            "/api/v1/ai-reasoning/analyze-market",
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

@main_bp.route('/api/gpts/health')
def gpts_health():
    """GPTs Health check endpoint (alias for /health)"""
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

# OpenAPI schema will be handled by the dedicated blueprint

# Enhanced GPTs API will be imported from gpts_routes.py

# Import and register the enhanced GPTs blueprint
from gpts_routes import gpts_api

# Import OpenAPI schema blueprint
from gpts_openapi_ultra_complete import openapi_bp

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

# Import webhook endpoints
try:
    from api.webhook_endpoints import webhook_bp
    webhook_available = True
except ImportError as e:
    logger.warning(f"Webhook blueprint not available: {e}")
    webhook_available = False
    webhook_bp = None

# Import sharp scoring endpoints
try:
    from api.sharp_scoring_endpoints import sharp_scoring_bp
    sharp_scoring_available = True
except ImportError as e:
    logger.warning(f"Sharp scoring blueprint not available: {e}")
    sharp_scoring_available = False
    sharp_scoring_bp = None

# Import telegram endpoints
try:
    from api.telegram_endpoints import telegram_bp
    telegram_available = True
except ImportError as e:
    logger.warning(f"Telegram blueprint not available: {e}")
    telegram_available = False
    telegram_bp = None

# Import ALL missing blueprint endpoints
try:
    from api.backtest_endpoints import backtest_api
    backtest_available = True
except ImportError as e:
    logger.warning(f"Backtest blueprint not available: {e}")
    backtest_available = False
    backtest_api = None

try:
    from api.chart_endpoints import chart_bp
    chart_available = True
except ImportError as e:
    logger.warning(f"Chart blueprint not available: {e}")
    chart_available = False
    chart_bp = None

try:
    from api.enhanced_gpts_endpoints import enhanced_gpts
    enhanced_gpts_available = True
except ImportError as e:
    logger.warning(f"Enhanced GPTs blueprint not available: {e}")
    enhanced_gpts_available = False
    enhanced_gpts = None

try:
    from api.gpts_coinglass_endpoints import gpts_coinglass_bp
    gpts_coinglass_available = True
except ImportError as e:
    logger.warning(f"GPTs CoinGlass blueprint not available: {e}")
    gpts_coinglass_available = False
    gpts_coinglass_bp = None

try:
    from api.improvement_endpoints import improvement_bp
    improvement_available = True
except ImportError as e:
    logger.warning(f"Improvement blueprint not available: {e}")
    improvement_available = False
    improvement_bp = None

try:
    from api.missing_endpoints import missing_bp
    missing_endpoints_available = True
except ImportError as e:
    logger.warning(f"Missing endpoints blueprint not available: {e}")
    missing_endpoints_available = False
    missing_bp = None

try:
    from api.modular_endpoints import modular_bp
    modular_available = True
except ImportError as e:
    logger.warning(f"Modular blueprint not available: {e}")
    modular_available = False
    modular_bp = None

try:
    from api.sharp_signal_endpoint import sharp_signal_bp
    sharp_signal_available = True
except ImportError as e:
    logger.warning(f"Sharp signal blueprint not available: {e}")
    sharp_signal_available = False
    sharp_signal_bp = None

try:
    from api.signal_engine_endpoint import signal_bp
    signal_engine_available = True
except ImportError as e:
    logger.warning(f"Signal engine blueprint not available: {e}")
    signal_engine_available = False
    signal_bp = None

try:
    from api.signal_top_endpoints import signal_top_bp
    signal_top_available = True
except ImportError as e:
    logger.warning(f"Signal top blueprint not available: {e}")
    signal_top_available = False
    signal_top_bp = None

try:
    from api.smc_pattern_endpoints import smc_pattern
    smc_pattern_available = True
except ImportError as e:
    logger.warning(f"SMC pattern blueprint not available: {e}")
    smc_pattern_available = False
    smc_pattern = None

try:
    from api.state_endpoints import state_api
    state_available = True
except ImportError as e:
    logger.warning(f"State blueprint not available: {e}")
    state_available = False
    state_api = None

# Register core blueprints with the app
app.register_blueprint(main_bp)
app.register_blueprint(gpts_api)  # Use enhanced GPTs API from gpts_routes.py
app.register_blueprint(openapi_bp)  # Register OpenAPI schema blueprint
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

if webhook_available and webhook_bp:
    app.register_blueprint(webhook_bp)
    logger.info("✅ Webhook blueprint registered")

if sharp_scoring_available and sharp_scoring_bp:
    app.register_blueprint(sharp_scoring_bp)
    logger.info("✅ Sharp scoring blueprint registered")

if telegram_available and telegram_bp:
    app.register_blueprint(telegram_bp)
    logger.info("✅ Telegram blueprint registered")

# Register ALL missing blueprints
if backtest_available and backtest_api:
    app.register_blueprint(backtest_api)
    logger.info("✅ Backtest API blueprint registered")

if chart_available and chart_bp:
    app.register_blueprint(chart_bp)
    logger.info("✅ Chart blueprint registered")

if enhanced_gpts_available and enhanced_gpts:
    app.register_blueprint(enhanced_gpts)
    logger.info("✅ Enhanced GPTs blueprint registered")

if gpts_coinglass_available and gpts_coinglass_bp:
    app.register_blueprint(gpts_coinglass_bp)
    logger.info("✅ GPTs CoinGlass blueprint registered")

if improvement_available and improvement_bp:
    app.register_blueprint(improvement_bp)
    logger.info("✅ Improvement blueprint registered")

if missing_endpoints_available and missing_bp:
    app.register_blueprint(missing_bp)
    logger.info("✅ Missing endpoints blueprint registered")

if modular_available and modular_bp:
    app.register_blueprint(modular_bp)
    logger.info("✅ Modular blueprint registered")

if sharp_signal_available and sharp_signal_bp:
    app.register_blueprint(sharp_signal_bp)
    logger.info("✅ Sharp signal blueprint registered")

if signal_engine_available and signal_bp:
    app.register_blueprint(signal_bp)
    logger.info("✅ Signal engine blueprint registered")

if signal_top_available and signal_top_bp:
    app.register_blueprint(signal_top_bp)
    logger.info("✅ Signal top blueprint registered")

if smc_pattern_available and smc_pattern:
    app.register_blueprint(smc_pattern)
    logger.info("✅ SMC pattern blueprint registered")

if state_available and state_api:
    app.register_blueprint(state_api)
    logger.info("✅ State API blueprint registered")

# Register Data Quality Enhancement blueprint
try:
    from api.data_quality_endpoints import data_quality_bp
    app.register_blueprint(data_quality_bp)
    logger.info("✅ Data Quality Enhancement blueprint registered")
except ImportError as e:
    logger.warning(f"⚠️ Data Quality Enhancement blueprint not available: {e}")
except Exception as e:
    logger.error(f"❌ Error registering Data Quality Enhancement blueprint: {e}")

# Register Security Enhancement blueprint
try:
    from api.security_endpoints import security_bp
    app.register_blueprint(security_bp)
    logger.info("✅ Security Enhancement blueprint registered")
except ImportError as e:
    logger.warning(f"⚠️ Security Enhancement blueprint not available: {e}")
except Exception as e:
    logger.error(f"❌ Error registering Security Enhancement blueprint: {e}")

# Register Performance Optimization blueprint
try:
    from api.performance_endpoints import performance_bp
    app.register_blueprint(performance_bp)
    logger.info("✅ Performance Optimization blueprint registered")
except ImportError as e:
    logger.warning(f"⚠️ Performance Optimization blueprint not available: {e}")
except Exception as e:
    logger.error(f"❌ Error registering Performance Optimization blueprint: {e}")

# Register Advanced Optimization blueprint
try:
    from api.advanced_optimization_endpoints import advanced_optimization_bp
    app.register_blueprint(advanced_optimization_bp)
    logger.info("✅ Advanced Optimization blueprint registered")
except ImportError as e:
    logger.warning(f"⚠️ Advanced Optimization blueprint not available: {e}")
except Exception as e:
    logger.error(f"❌ Error registering Advanced Optimization blueprint: {e}")

# Register AI Reasoning blueprint
try:
    from api.ai_reasoning_endpoints import ai_reasoning_bp
    app.register_blueprint(ai_reasoning_bp)
    logger.info("✅ AI Reasoning blueprint registered")
except ImportError as e:
    logger.warning(f"⚠️ AI Reasoning blueprint not available: {e}")
except Exception as e:
    logger.error(f"❌ Error registering AI Reasoning blueprint: {e}")
        

