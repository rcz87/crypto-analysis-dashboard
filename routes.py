from flask import Blueprint, jsonify, request, g
import logging
import os
from functools import wraps

# Create a main blueprint for core routes
main_bp = Blueprint('main', __name__)
logger = logging.getLogger(__name__)

# API Key Authentication Decorator
def require_api_key(f):
    """Simple API key protection to prevent scraping/abuse"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if API key protection is enabled
        api_key_required = os.environ.get('API_KEY_REQUIRED', 'false').lower() == 'true'
        expected_api_key = os.environ.get('API_KEY')
        
        if api_key_required and expected_api_key:
            provided_key = request.headers.get('X-API-KEY')
            if not provided_key or provided_key != expected_api_key:
                return jsonify({
                    "error": "UNAUTHORIZED",
                    "message": "Valid API key required in X-API-KEY header",
                    "status_code": 401
                }), 401
        
        return f(*args, **kwargs)
    return decorated_function

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
@require_api_key
def health():
    """Enhanced health check endpoint with proper status determination"""
    from datetime import datetime
    
    health_status = "healthy"
    components = {}
    
    # Test database connection
    try:
        from sqlalchemy import text
        from flask import current_app
        
        with current_app.app_context():
            from app import db
            db.session.execute(text('SELECT 1'))
            db.session.commit()
        components["database"] = {"status": "healthy", "message": "Connected"}
    except Exception as e:
        components["database"] = {"status": "unhealthy", "message": f"Error: {str(e)}"}
        health_status = "degraded"
    
    # Test core components availability
    try:
        from core.okx_fetcher import OKXFetcher
        okx = OKXFetcher()
        test_result = okx.test_connection()
        components["okx_api"] = {
            "status": "healthy" if test_result.get('status') == 'connected' else "degraded",
            "message": test_result.get('message', 'Unknown')
        }
    except Exception as e:
        components["okx_api"] = {"status": "degraded", "message": f"Error: {str(e)}"}
        if health_status == "healthy":
            health_status = "degraded"
    
    # Determine overall status
    if any(comp.get("status") == "unhealthy" for comp in components.values()):
        health_status = "unhealthy"
    elif any(comp.get("status") == "degraded" for comp in components.values()):
        health_status = "degraded"
    
    # Return appropriate HTTP status code
    status_code = 200 if health_status == "healthy" else (503 if health_status == "unhealthy" else 200)
    
    return jsonify({
        "status": health_status,
        "components": components,
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat(),
        "uptime": "N/A"  # Could be enhanced with actual uptime tracking
    }), status_code

@main_bp.route('/api/gpts/health')
@require_api_key
def gpts_health():
    """GPTs Health check endpoint - standardized under /api prefix"""
    # Redirect to main health check for consistency
    return health()

# Application Factory Pattern Implementation
def init_routes(app, db):
    """
    Initialize and register all blueprints safely using application factory pattern.
    This prevents circular imports and double registration issues.
    
    Args:
        app: Flask application instance
        db: Database instance
    """
    
    # Store db in app context for health checks
    app.db = db
    
    # Register core blueprint first
    app.register_blueprint(main_bp)
    logger.info("✅ Main blueprint registered")
    
    # Standard API prefix for consistency: /api/
    api_prefix = "/api"
    
    # Register GPTs API blueprint (primary functionality)
    try:
        from gpts_routes import gpts_api
        app.register_blueprint(gpts_api, url_prefix=f"{api_prefix}/gpts")
        logger.info("✅ GPTs API blueprint registered with standardized prefix")
    except ImportError as e:
        logger.error(f"❌ Failed to import GPTs routes: {e}")
    
    # Register optional blueprints with consistent prefixes and error handling
    optional_blueprints = [
        # Core functionality blueprints
        ("openapi_schema", "openapi_bp", f"{api_prefix}/schema"),
        ("api.smc_zones_endpoints", "smc_zones_bp", f"{api_prefix}/smc"),
        
        # Enhanced functionality
        ("api.data_quality_endpoints", "data_quality_bp", f"{api_prefix}/quality"), 
        ("api.security_endpoints", "security_bp", f"{api_prefix}/security"),
        ("api.performance_endpoints", "performance_bp", f"{api_prefix}/performance"),
        ("api.advanced_optimization_endpoints", "advanced_optimization_bp", f"{api_prefix}/optimization"),
        ("api.ai_reasoning_endpoints", "ai_reasoning_bp", f"{api_prefix}/v1/ai-reasoning"),
        
        # Optional features
        ("api.promptbook_endpoints", "promptbook_bp", f"{api_prefix}/promptbook"),
        ("api.news_endpoints", "news_api", f"{api_prefix}/news"),
        ("api.telegram_endpoints", "telegram_bp", f"{api_prefix}/telegram"),
        ("api.webhook_endpoints", "webhook_bp", f"{api_prefix}/webhook"),
    ]
    
    for module_name, blueprint_name, url_prefix in optional_blueprints:
        try:
            module = __import__(module_name, fromlist=[blueprint_name])
            blueprint = getattr(module, blueprint_name)
            
            # Handle duplicate blueprint name errors
            try:
                app.register_blueprint(blueprint, url_prefix=url_prefix)
                logger.info(f"✅ {blueprint_name} registered at {url_prefix}")
            except ValueError as ve:
                if "already registered" in str(ve):
                    logger.warning(f"⚠️ {blueprint_name} already registered, skipping")
                else:
                    raise ve
                    
        except ImportError:
            logger.debug(f"⚠️ Optional blueprint {blueprint_name} not available")
        except Exception as e:
            logger.error(f"❌ Error registering {blueprint_name}: {e}")
    
    logger.info("🚀 All available blueprints registered successfully with standardized /api prefix")