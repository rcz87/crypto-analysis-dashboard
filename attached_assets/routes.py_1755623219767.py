
from flask import Blueprint, jsonify, request, current_app
import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

# Core blueprint (no circular import, no global app)
core_bp = Blueprint("core", __name__)

def _require_api_key() -> Optional[tuple]:
    """Return a Flask response tuple if unauthorized, else None."""
    want = os.getenv("API_KEY")
    if not want:
        return None  # gate disabled
    got = request.headers.get("X-API-KEY")
    if got != want:
        payload = {"success": False, "error": "UNAUTHORIZED"}
        return jsonify(payload), 401
    return None

@core_bp.route("/", methods=["GET"])
def index():
    gate = _require_api_key()
    if gate: 
        return gate
    return jsonify({
        "message": "Advanced Cryptocurrency GPTs & Telegram Bot API",
        "version": current_app.config.get("API_VERSION", "2.0.0"),
        "service": "crypto-trading-suite",
    })

@core_bp.route("/health", methods=["GET"])
def health_check():
    gate = _require_api_key()
    if gate: 
        return gate

    db_status = "unknown"
    try:
        db = current_app.extensions.get("sqlalchemy").db  # expects flask-sqlalchemy init
        from sqlalchemy import text
        db.session.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        logger.warning(f"DB health degraded: {e}")
        db_status = "degraded"

    return jsonify({
        "status": "healthy" if db_status == "connected" else "degraded",
        "database": db_status,
        "version": current_app.config.get("API_VERSION", "2.0.0"),
    })

def _register_optional_blueprint(app, import_path: str, attr: str, url_prefix: Optional[str] = None):
    """Safely import and register a blueprint once."""
    try:
        mod = __import__(import_path, fromlist=[attr])
        bp = getattr(mod, attr)
        name = getattr(bp, "name", attr)

        # prevent duplicate registration
        if name in app.blueprints:
            logger.info(f"↺ Blueprint already registered: {name}")
            return False

        app.register_blueprint(bp, url_prefix=url_prefix)
        logger.info(f"✅ Registered blueprint: {name} (prefix={url_prefix})")
        return True

    except ImportError as e:
        logger.warning(f"⚠️ Optional blueprint not available: {import_path}.{attr} ({e})")
    except Exception as e:
        logger.error(f"❌ Error registering blueprint {import_path}.{attr}: {e}")
    return False

def init_routes(app, db=None):
    """
    Call this inside create_app():
        app = Flask(__name__)
        ...
        init_routes(app, db)
    """
    # attach API version
    app.config.setdefault("API_VERSION", "2.0.0")

    # register core
    if "core" not in app.blueprints:
        app.register_blueprint(core_bp)  # root-level
        logger.info("✅ Core routes registered")

    # Optional blueprints (provide sensible prefixes if module lacks)
    _register_optional_blueprint(app, "api.gpts_api_simple", "gpts_simple", url_prefix="/api/gpts")
    _register_optional_blueprint(app, "api.enhanced_signals", "enhanced_bp", url_prefix="/api/enhanced")
    _register_optional_blueprint(app, "api.institutional_endpoints", "institutional_bp", url_prefix="/api/institutional")
    _register_optional_blueprint(app, "api.ai_reasoning_endpoints", "ai_reasoning_bp", url_prefix="/api/ai")
    _register_optional_blueprint(app, "api.coinglass_demo", "coinglass_bp", url_prefix="/api/coinglass")

    logger.info("🚀 Routes initialized")
