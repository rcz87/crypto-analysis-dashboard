import os
import logging
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass

# Initialize db without app
db = SQLAlchemy(model_class=Base)

def create_app(config_name='development'):
    """
    Application Factory Pattern - creates and configures Flask app
    """
    app = Flask(__name__)
    
    # 🔧 CORE CONFIGURATION
    app.secret_key = os.environ.get("SESSION_SECRET", os.environ.get("SECRET_KEY", 'dev-key-change-in-production'))
    app.config['SECRET_KEY'] = app.secret_key
    app.config['API_VERSION'] = '2.0.0'
    
    # 🌐 PROXY FIX - Essential for production with reverse proxy
    app.wsgi_app = ProxyFix(
        app.wsgi_app, 
        x_proto=1, 
        x_host=1, 
        x_for=1  # Add x_for for better IP handling
    )
    
    # 🔒 SECURITY CONFIGURATION
    app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024  # 1MB max payload
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False  # Disable pretty print for performance
    
    # 🗄️ DATABASE CONFIGURATION
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL", 
        "sqlite:///crypto_trading.db"  # Fallback for development
    )
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
        "pool_timeout": 20,
        "max_overflow": 10
    }
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    # Initialize extensions
    db.init_app(app)
    
    # 🔒 Security Headers Middleware
    @app.after_request 
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, private'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    
    # 🚨 Error Handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({
            "success": False,
            "error": "NOT_FOUND",
            "message": "The requested endpoint was not found",
            "status_code": 404
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": "INTERNAL_SERVER_ERROR", 
            "message": "An internal server error occurred",
            "status_code": 500
        }), 500
    
    @app.errorhandler(400)
    def bad_request_error(error):
        return jsonify({
            "success": False,
            "error": "BAD_REQUEST",
            "message": "Invalid request format or parameters",
            "status_code": 400
        }), 400
    
    # 📊 Initialize database tables
    with app.app_context():
        try:
            # Import models to register them
            import models  # noqa: F401
            
            # Create tables (safe for dev, consider migrations for prod)
            db.create_all()
            logger.info("✅ Database tables created/verified")
            
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")
            # Continue anyway for graceful degradation
    
    # 🛣️ Initialize routes using application factory pattern
    from routes import init_routes
    init_routes(app, db)
    
    logger.info(f"🚀 Flask app created successfully (config: {config_name})")
    return app

# Create app instance for compatibility (avoid using this in production)
app = create_app()