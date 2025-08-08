"""
Flask App Setup - Modular Configuration
Memisahkan logika setup dari main.py untuk maintainability
"""

import os
import logging
import asyncio
from datetime import timedelta
from flask import Flask, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

def setup_database(app: Flask):
    """Setup database configuration"""
    try:
        app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
            "pool_recycle": 300,
            "pool_pre_ping": True,
        }
        
        db.init_app(app)
        
        with app.app_context():
            try:
                import models  # Import models module
                db.create_all()
                logger.info("✅ Database tables created successfully")
            except Exception as e:
                logger.warning(f"Database table creation warning: {e}")
        
        logger.info("✅ Database setup completed")
        return True
    except Exception as e:
        logger.error(f"❌ Database setup failed: {e}", exc_info=True)
        return False

def setup_security(app: Flask):
    """Setup security configurations"""
    try:
        # Secret key configuration
        app.secret_key = os.environ.get("SESSION_SECRET") or os.environ.get("FLASK_SECRET_KEY") or "dev_secret_2025"
        
        # Security headers
        @app.after_request
        def after_request(response):
            response.headers['X-Content-Type-Options'] = 'nosniff'
            response.headers['X-Frame-Options'] = 'DENY'
            response.headers['X-XSS-Protection'] = '1; mode=block'
            return response
        
        # Initialize security hardening if available
        try:
            from core.security_hardening import init_security_hardening
            init_security_hardening(app)
            logger.info("✅ Security hardening initialized")
        except ImportError:
            logger.warning("⚠️ Security hardening module not available")
        
        logger.info("✅ Security setup completed")
        return True
    except Exception as e:
        logger.error(f"❌ Security setup failed: {e}", exc_info=True)
        return False

def setup_cors(app: Flask):
    """Setup CORS configuration with production-ready settings"""
    try:
        # Production-ready CORS configuration
        is_production = os.environ.get('ENVIRONMENT', 'development').lower() == 'production'
        
        if is_production:
            allowed_origins = [
                "https://chat.openai.com",
                "https://chatgpt.com",
                "https://platform.openai.com",
                "https://*.replit.app",
                "https://*.replit.dev"
            ]
            logger.info("✅ Production CORS: Limited to GPTs domains")
        else:
            allowed_origins = "*"
            logger.info("✅ Development CORS: All origins allowed")
        
        CORS(app, 
             origins=allowed_origins,
             methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
             allow_headers=['Content-Type', 'Authorization', 'X-API-Key', 'User-Agent'],
             supports_credentials=True,
             max_age=timedelta(days=1))
        
        return True
    except Exception as e:
        logger.error(f"❌ CORS setup failed: {e}", exc_info=True)
        return False

def setup_logging(app: Flask):
    """Setup comprehensive logging"""
    try:
        # Basic logging configuration
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('logs/app.log', mode='a')
            ]
        )
        
        # Ensure logs directory exists
        os.makedirs('logs', exist_ok=True)
        
        # Initialize enhanced logging if available
        try:
            from core.enhanced_logging_system import enhanced_logger
            enhanced_logger.log_system_health("startup", {"component": "logging_setup"})
            logger.info("✅ Enhanced logging system initialized")
        except ImportError:
            logger.warning("⚠️ Enhanced logging system not available")
        
        logger.info("✅ Logging setup completed")
        return True
    except Exception as e:
        print(f"❌ Logging setup failed: {e}")
        return False

def setup_blueprints(app: Flask):
    """Setup and register all blueprints with error handling"""
    blueprints_status = {
        'loaded': [],
        'failed': [],
        'skipped': []
    }
    
    # Blueprint configurations with dependencies check
    blueprint_configs = [
        # Core APIs (Critical)
        {
            'name': 'GPTs API Simple',
            'import_path': 'gpts_api_simple',
            'blueprint_name': 'gpts_simple',
            'critical': True
        },
        {
            'name': 'GPTs API Minimal',
            'import_path': 'gpts_api_minimal', 
            'blueprint_name': 'gpts_minimal',
            'critical': True
        },
        {
            'name': 'Modular Endpoints',
            'import_path': 'api.modular_endpoints',
            'blueprint_name': 'modular_bp',
            'critical': True
        },
        
        # Enhanced APIs
        {
            'name': 'OpenAPI Schema',
            'import_path': 'openapi_schema',
            'blueprint_name': 'openapi_bp',
            'critical': False
        },
        {
            'name': 'Prompt Book',
            'import_path': 'api.promptbook',
            'blueprint_name': 'promptbook_bp',
            'critical': False
        },
        {
            'name': 'SMC Context Endpoints',
            'import_path': 'api.smc_endpoints',
            'blueprint_name': 'smc_context_bp',
            'critical': False
        },
        {
            'name': 'Enhanced GPTs Endpoints',
            'import_path': 'api.enhanced_gpts_endpoints',
            'blueprint_name': 'enhanced_gpts',
            'critical': False
        },
        {
            'name': 'SMC Pattern Endpoints',
            'import_path': 'api.smc_pattern_endpoints', 
            'blueprint_name': 'smc_pattern',
            'critical': False
        },
        {
            'name': 'SMC Zones Endpoints',
            'import_path': 'api.smc_zones_endpoints',
            'blueprint_name': 'smc_zones_bp',
            'critical': False
        },
        {
            'name': 'Signal Top Endpoints',
            'import_path': 'api.signal_top_endpoints',
            'blueprint_name': 'signal_top_bp',
            'critical': False
        },
        {
            'name': 'Performance Endpoints',
            'import_path': 'api.performance_endpoints',
            'blueprint_name': None,  # Uses init function
            'init_function': 'init_performance_endpoints',
            'critical': False
        },
        {
            'name': 'Advanced Performance API',
            'import_path': 'api.performance_api',
            'blueprint_name': 'performance_api',
            'critical': False
        },
        {
            'name': 'Chart Endpoints',
            'import_path': 'api.chart_endpoints',
            'blueprint_name': 'chart_bp',
            'url_prefix': '/api/chart',
            'critical': False
        },
        {
            'name': 'Missing Endpoints',
            'import_path': 'api.missing_endpoints',
            'blueprint_name': 'missing_bp',
            'critical': False
        },
        {
            'name': 'State Endpoints',
            'import_path': 'api.state_endpoints',
            'blueprint_name': 'state_api',
            'critical': False
        },
        {
            'name': 'Self-Learning Signal Engine',
            'import_path': 'core.signal_self_learning',
            'blueprint_name': 'self_learning_bp',
            'critical': False
        },
        {
            'name': 'Enhanced Signal Engine Endpoint',
            'import_path': 'api.signal_engine_endpoint',
            'blueprint_name': 'signal_bp',
            'critical': True
        },
        {
            'name': 'Sharp Signal Engine Endpoint',
            'import_path': 'api.sharp_signal_endpoint',
            'blueprint_name': 'sharp_signal_bp',
            'critical': True
        }
    ]
    
    # Register blueprints
    for config in blueprint_configs:
        try:
            module = __import__(config['import_path'], fromlist=[''])
            
            if config.get('init_function'):
                # Special case for init functions
                init_func = getattr(module, config['init_function'])
                init_func(app)
                blueprints_status['loaded'].append(config['name'])
                logger.info(f"✅ {config['name']} initialized via function")
            else:
                # Regular blueprint registration
                blueprint = getattr(module, config['blueprint_name'])
                
                if config.get('url_prefix'):
                    app.register_blueprint(blueprint, url_prefix=config['url_prefix'])
                else:
                    app.register_blueprint(blueprint)
                
                blueprints_status['loaded'].append(config['name'])
                logger.info(f"✅ {config['name']} blueprint registered")
                
        except ImportError as e:
            if config.get('critical', False):
                logger.error(f"❌ Critical blueprint failed: {config['name']} - {e}", exc_info=True)
                blueprints_status['failed'].append(config['name'])
            else:
                logger.warning(f"⚠️ Optional blueprint skipped: {config['name']} - {e}")
                blueprints_status['skipped'].append(config['name'])
        except Exception as e:
            logger.error(f"❌ Blueprint registration error: {config['name']} - {e}", exc_info=True)
            blueprints_status['failed'].append(config['name'])
    
    # Summary
    logger.info(f"📊 Blueprints Summary: {len(blueprints_status['loaded'])} loaded, "
               f"{len(blueprints_status['failed'])} failed, {len(blueprints_status['skipped'])} skipped")
    
    return blueprints_status

def setup_routes(app: Flask):
    """Setup core application routes"""
    try:
        # Health check endpoints - always available
        @app.route("/health")
        def health():
            """Lightweight health check"""
            from datetime import datetime
            return jsonify({
                "status": "ok", 
                "time": datetime.utcnow().isoformat(),
                "service": "GPTs & Telegram Bot API"
            })

        @app.route('/health/detailed', methods=['GET'])
        def health_detailed():
            """Detailed health check with system status"""
            try:
                # Get telegram status
                telegram_status = "inactive"
                try:
                    from core.telegram_bot import get_telegram_bot
                    bot = get_telegram_bot()
                    telegram_status = "active" if bot else "inactive"
                except:
                    telegram_status = "error"
                
                return jsonify({
                    "status": "healthy",
                    "services": {
                        "gpts_api": "active",
                        "telegram_bot": telegram_status,
                        "core_systems": "operational",
                        "database": "connected" if db else "disconnected"
                    },
                    "focus": "GPTs_and_Telegram_only",
                    "version": "2.0.0"
                })
            except Exception as e:
                logger.error(f"Health check error: {e}")
                return jsonify({
                    "status": "degraded",
                    "error": str(e)
                }), 500

        # Improvement status endpoint - always available
        @app.route('/api/improvement/status', methods=['GET'])
        def improvement_status():
            """Get improvement system status"""
            try:
                from core.comprehensive_self_improvement import get_improvement_status
                status = get_improvement_status()
                return jsonify({'success': True, 'status': status})
            except Exception as e:
                return jsonify({'success': False, 'error': f'Improvement status error: {str(e)}'})

        # Root endpoint
        @app.route('/')
        def index():
            """Root endpoint with system info"""
            return jsonify({
                "service": "Advanced Cryptocurrency GPTs & Telegram Bot",
                "version": "2.0.0", 
                "status": "active",
                "focus": "GPTs API Integration & Telegram Bot",
                "endpoints": {
                    "health": "/health",
                    "gpts_api": "/api/gpts/",
                    "modular_v2": "/api/v2/",
                    "improvement": "/api/improvement/status"
                }
            })
        
        logger.info("✅ Core routes setup completed")
        return True
    except Exception as e:
        logger.error(f"❌ Routes setup failed: {e}", exc_info=True)
        return False

def setup_telegram_integration(app: Flask):
    """Setup Telegram bot integration"""
    try:
        from core.telegram_bot import initialize_telegram_bot
        telegram_bot = initialize_telegram_bot()
        
        telegram_status = "active" if telegram_bot else "inactive"
        logger.info(f"✅ Telegram Bot integration: {telegram_status}")
        
        return {"status": telegram_status, "bot": telegram_bot}
    except Exception as e:
        logger.warning(f"⚠️ Telegram Bot integration failed: {e}")
        return {"status": "error", "error": str(e)}

def check_dependencies():
    """Check critical dependencies"""
    dependencies = {
        'flask': True,
        'pandas': False,
        'numpy': False,
        'sqlalchemy': False,
        'requests': False,
        'tensorflow': False
    }
    
    for dep in dependencies:
        try:
            __import__(dep)
            dependencies[dep] = True
        except ImportError:
            logger.warning(f"⚠️ Dependency missing: {dep}")
    
    missing = [dep for dep, available in dependencies.items() if not available]
    if missing:
        logger.warning(f"⚠️ Missing dependencies: {missing}")
    else:
        logger.info("✅ All dependencies available")
    
    return dependencies