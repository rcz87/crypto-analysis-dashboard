from flask import Blueprint, jsonify, request, current_app
import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

# Core blueprint (no circular import, no global app)
core_bp = Blueprint("core", __name__)

def _require_api_key() -> Optional[tuple]:
    """Return a Flask response tuple if unauthorized, else None."""
    api_key_required = os.environ.get('API_KEY_REQUIRED', 'false').lower() == 'true'
    expected_key = os.environ.get("API_KEY")
    
    if not api_key_required or not expected_key:
        return None  # gate disabled
    
    provided_key = request.headers.get("X-API-KEY")
    if provided_key != expected_key:
        payload = {
            "success": False, 
            "error": "UNAUTHORIZED",
            "message": "Valid API key required in X-API-KEY header"
        }
        return jsonify(payload), 401
    return None

@core_bp.route("/", methods=["GET"])
def index():
    """Main index route with comprehensive API information"""
    gate = _require_api_key()
    if gate: 
        return gate

    from datetime import datetime
        
    # Dynamically collect all registered blueprints and their prefixes
    all_endpoints = []
    blueprint_info = {}
    
    # Get all registered blueprints
    for blueprint_name, blueprint in current_app.blueprints.items():
        if hasattr(blueprint, 'url_prefix') and blueprint.url_prefix:
            prefix = blueprint.url_prefix
            all_endpoints.append(f"{prefix}/*")
            blueprint_info[blueprint_name] = prefix
    
    # Add core endpoints
    core_endpoints = ["/health", "/api/gpts/status", "/api/gpts/sinyal/tajam"]
    all_endpoints.extend(core_endpoints)
    all_endpoints = sorted(list(set(all_endpoints)))
        
    return jsonify({
        "message": "Advanced Cryptocurrency Trading Analysis Platform",
        "service": "crypto-trading-suite",
        "version": current_app.config.get("API_VERSION", "2.0.0"),
        "status": "active",
        "description": "AI-powered cryptocurrency trading signals with institutional-grade analysis",
        "features": [
            "Smart Money Concept Analysis",
            "AI-Powered Trading Signals", 
            "Real-time Market Data",
            "Technical Analysis",
            "Risk Management",
            "ChatGPT Integration",
            "Enhanced Signal Generation",
            "Institutional Analysis",
            "Performance Monitoring",
            "Security Features",
            "Data Quality Management"
        ],
        "endpoints": all_endpoints,
        "registered_blueprints": len(current_app.blueprints),
        "total_endpoints": len(all_endpoints),
        "blueprint_prefixes": blueprint_info,
        "documentation": "/api/schema",
        "timestamp": datetime.now().isoformat()
    })

@core_bp.route("/health", methods=["GET"])
def health_check():
    """Enhanced health check with component status determination"""
    gate = _require_api_key()
    if gate: 
        return gate

    from datetime import datetime
    
    health_status = "healthy"
    components = {}
    
    # Test database connection
    try:
        # Safe database access using current_app
        if hasattr(current_app, 'extensions') and 'sqlalchemy' in current_app.extensions:
            db = current_app.extensions['sqlalchemy'].db
            from sqlalchemy import text
            db.session.execute(text("SELECT 1"))
            db.session.commit()
            components["database"] = {"status": "healthy", "message": "Connected"}
        else:
            # Fallback to direct import
            from app import db
            from sqlalchemy import text
            db.session.execute(text("SELECT 1"))
            db.session.commit()
            components["database"] = {"status": "healthy", "message": "Connected"}
    except Exception as e:
        logger.warning(f"Database health check failed: {e}")
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
        if components["okx_api"]["status"] == "degraded" and health_status == "healthy":
            health_status = "degraded"
    except Exception as e:
        logger.warning(f"OKX API health check failed: {e}")
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
        "version": current_app.config.get("API_VERSION", "2.0.0"),
        "timestamp": datetime.now().isoformat(),
        "uptime": "N/A"
    }), status_code

@core_bp.route("/api/gpts/health", methods=["GET"])
def gpts_health():
    """GPTs Health check endpoint - standardized under /api prefix"""
    return health_check()

def _register_optional_blueprint(app, import_path: str, attr: str, url_prefix: Optional[str] = None):
    """Safely import and register a blueprint once, preventing duplicates."""
    try:
        mod = __import__(import_path, fromlist=[attr])
        bp = getattr(mod, attr)
        name = getattr(bp, "name", attr)

        # Prevent duplicate registration
        if name in app.blueprints:
            logger.debug(f"↺ Blueprint already registered: {name}")
            return False

        app.register_blueprint(bp, url_prefix=url_prefix)
        logger.info(f"✅ Registered blueprint: {name} (prefix={url_prefix})")
        return True

    except ImportError as e:
        logger.debug(f"⚠️ Optional blueprint not available: {import_path}.{attr}")
    except Exception as e:
        logger.error(f"❌ Error registering blueprint {import_path}.{attr}: {e}")
    return False

def init_routes(app, db=None):
    """
    Initialize and register all blueprints safely using application factory pattern.
    Call this inside create_app() after app and db initialization.
    
    Args:
        app: Flask application instance
        db: Database instance (optional)
    """
    
    # Set API version configuration
    app.config.setdefault("API_VERSION", "2.0.0")
    
    # Store db reference if provided
    if db:
        app.db = db

    # Register core blueprint first
    if "core" not in app.blueprints:
        app.register_blueprint(core_bp)
        logger.info("✅ Core routes registered")

    # Standard API prefix for consistency
    api_prefix = "/api"
    
    # Register primary GPTs API blueprint
    _register_optional_blueprint(app, "gpts_routes", "gpts_api", url_prefix=f"{api_prefix}/gpts")
    
    # 🤖 AUTO-DISCOVERED BLUEPRINTS - All user's endpoints
    auto_discovered_blueprints = [
        ("api.advanced_optimization_endpoints", "advanced_optimization_bp", "/api/advanced_optimization"),
        ("api.ai_reasoning_endpoints", "ai_reasoning_bp", "/api/ai"),
        ("api.backtest_endpoints", "backtest_bp", "/api/backtest"),
        ("api.chart_endpoints", "chart_bp", "/api/charts"),
        ("api.data_quality_endpoints", "data_quality_bp", "/api/data_quality"),
        ("api.enhanced_gpts_endpoints", "enhanced_gpts_bp", "/api/gpts"),
        ("api.enhanced_signal_endpoints", "enhanced_signals_bp", "/api/signals"),
        ("api.gpts_coinglass_endpoints", "coinglass_bp", "/api/coinglass"),
        ("api.gpts_coinglass_simple", "coinglass_simple_bp", "/api/coinglass-simple"),
        ("api.improvement_endpoints", "improvement_bp", "/api/improvements"),
        ("api.institutional_endpoints", "institutional_bp", "/api/institutional"),
        ("api.missing_endpoints", "missing_bp", "/api/missing"),
        ("api.missing_gpts_endpoints", "missing_gpts_bp", "/api/missing-gpts"),
        ("api.modular_endpoints", "modular_bp", "/api/modular"),
        ("api.news_endpoints", "news_api", "/api/news"),
        ("api.performance_api", "performance_api_bp", "/api/performance-api"),
        ("api.performance_endpoints", "performance_bp", "/api/performance"),
        ("api.promptbook", "promptbook_bp", "/api/promptbook"),
        ("api.security_endpoints", "security_bp", "/api/security"),
        ("api.sharp_scoring_endpoints", "sharp_scoring_bp", "/api/sharp-scoring"),
        ("api.sharp_signal_endpoint", "sharp_signal_bp", "/api/signals"),
        ("api.signal_engine_endpoint", "signal_engine_bp", "/api/signal-engine"),
        ("api.signal_top_endpoints", "signal_top_bp", "/api/signal-top"),
        ("api.smc_endpoints", "smc_bp", "/api/smc"),
        ("api.smc_pattern_endpoints", "smc_pattern_bp", "/api/smc-patterns"),
        ("api.smc_zones_endpoints", "smc_zones_bp", "/api/smc-zones"),
        ("api.state_endpoints", "state_bp", "/api/state"),
        ("api.telegram_endpoints", "telegram_bp", "/api/telegram"),
        ("api.webhook_endpoints", "webhook_bp", "/api/webhook"),
        # Legacy/root blueprints
        ("openapi_schema", "openapi_bp", f"{api_prefix}/schema"),
    ]
    
    # Register all auto-discovered blueprints
    successful_registrations = 0
    for import_path, attr, url_prefix in auto_discovered_blueprints:
        if _register_optional_blueprint(app, import_path, attr, url_prefix):
            successful_registrations += 1
    
    logger.info(f"🤖 Auto-discovery: {successful_registrations}/{len(auto_discovered_blueprints)} blueprints registered")
    logger.info(f"🚀 Routes initialized: ALL user endpoints discovered and registered")
    logger.info("🎯 Application factory pattern successfully implemented")