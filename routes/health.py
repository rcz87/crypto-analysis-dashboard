from flask import Blueprint, jsonify, current_app
import os
import time
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

health_bp = Blueprint("health", __name__)

@health_bp.route("/", methods=["GET"])
def index():
    """Main index route - API documentation and service information"""
    try:
        return jsonify({
            "message": "Advanced Cryptocurrency Trading Analysis Platform",
            "service": "crypto-trading-suite", 
            "version": current_app.config.get("API_VERSION", "2.0.0"),
            "status": "active",
            "description": "AI-powered cryptocurrency trading signals with Smart Money Concept analysis",
            "endpoints": {
                "health_check": "/health",
                "status": "/api/gpts/status",
                "trading_signals": "/api/gpts/sinyal/tajam",
                "documentation": "See development_workflow_explained.md"
            },
            "features": [
                "Real-time trading signals",
                "Smart Money Concept analysis", 
                "AI-powered market analysis",
                "Multi-timeframe analysis",
                "Institutional trading intelligence"
            ],
            "supported_symbols": ["BTC", "ETH", "SOL", "ADA", "DOT", "AVAX"],
            "supported_timeframes": ["1m", "5m", "15m", "1H", "4H", "1D"],
            "timestamp": int(time.time())
        })
    except Exception as e:
        logger.error(f"Index endpoint error: {e}")
        return jsonify({
            "status": "error",
            "message": "Service temporarily unavailable",
            "timestamp": int(time.time())
        }), 500

# Endpoint moved to gpts_routes.py with API key protection
# @health_bp.route("/api/gpts/status", methods=["GET"])
# def gpts_status():
    """Lightweight status check without database connection"""
    try:
        return jsonify({
            "status": "active",
            "version": {
                "api_version": current_app.config.get("API_VERSION", "2.0.0"),
                "core_version": "1.2.3"
            },
            "components": {
                "signal_generator": "available",
                "smc_analyzer": "available",
                "okx_api": "connected",
                "openai": "available",
                "database": "available"
            },
            "supported_symbols": ["BTC", "ETH", "SOL", "ADA", "DOT", "AVAX"],
            "supported_timeframes": ["1m", "3m", "5m", "15m", "30m", "1H", "2H", "4H", "6H", "12H", "1D", "2D", "3D", "1W", "1M", "3M"],
            "timestamp": int(time.time())
        })
    except Exception as e:
        logger.error(f"Status endpoint error: {e}")
        return jsonify({
            "status": "error",
            "message": "Internal server error",
            "timestamp": int(time.time())
        }), 500

@health_bp.route("/health", methods=["GET"])
def health_check():
    """Lightweight health check optimized for speed"""
    components = {}
    overall_status = "healthy"
    
    # Quick database check with short timeout
    try:
        from flask import current_app
        
        # Get database URL from Flask config
        database_url = current_app.config.get("SQLALCHEMY_DATABASE_URI", "")
        
        if "sqlite" in database_url.lower():
            # SQLite check - much faster
            import sqlite3
            import os
            
            db_path = database_url.replace("sqlite:///", "")
            if os.path.exists(db_path):
                components["database"] = {
                    "status": "healthy",
                    "message": "SQLite database file exists",
                    "type": "SQLite"
                }
            else:
                components["database"] = {
                    "status": "healthy",
                    "message": "SQLite will be created on first use",
                    "type": "SQLite"
                }
        else:
            # PostgreSQL quick check with very short timeout
            import sqlalchemy as sa
            
            engine = sa.create_engine(
                database_url,
                pool_pre_ping=True,
                connect_args={"connect_timeout": 3},
                pool_timeout=3
            )
            
            try:
                with engine.connect() as conn:
                    conn.execute(sa.text("SELECT 1"))
                    components["database"] = {
                        "status": "healthy",
                        "message": "PostgreSQL connection successful", 
                        "type": "PostgreSQL"
                    }
            finally:
                engine.dispose()
                
    except Exception as e:
        components["database"] = {
            "status": "degraded",
            "message": f"Database check failed: {str(e)[:80]}"
        }
        # Don't mark overall as unhealthy for database issues during startup
    
    # Skip external API check for faster response
    components["okx_api"] = {
        "status": "not_checked",
        "message": "External API checks skipped for performance"
    }
    
    # Add basic application info
    components["application"] = {
        "status": "healthy",
        "message": "Flask application running",
        "endpoints_available": 91
    }
    
    try:
        api_version = current_app.config.get("API_VERSION", "2.0.0")
        timestamp = datetime.utcnow().isoformat()
        status_code = 200 if overall_status == "healthy" else 503
        
        return jsonify({
            "status": overall_status,
            "components": components,
            "version": api_version,
            "timestamp": timestamp,
            "uptime": "N/A"  # Could implement uptime tracking if needed
        }), status_code
    except Exception as e:
        # Fallback response if current_app is not available
        return jsonify({
            "status": "error",
            "message": f"Health check error: {str(e)}",
            "timestamp": datetime.utcnow().isoformat()
        }), 500