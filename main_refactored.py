#!/usr/bin/env python3
"""
Main Flask Application - Refactored & Modular
Advanced Cryptocurrency GPTs & Telegram Bot API
"""

import os
import sys
import logging
from flask import Flask
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup logging early
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app():
    """
    Create and configure Flask application - Refactored & Modular
    """
    app = Flask(__name__)
    
    logger.info("🚀 Starting Advanced Cryptocurrency GPTs & Telegram Bot API v2.0")
    
    # Import modular setup functions
    from config.app_setup import (
        setup_database, setup_security, setup_cors, setup_logging,
        setup_blueprints, setup_routes, setup_telegram_integration,
        check_dependencies
    )
    from config.keep_alive import setup_keep_alive
    from config.api_protection import setup_protected_endpoints
    
    # 1. Check dependencies first
    logger.info("🔍 Checking dependencies...")
    dependencies = check_dependencies()
    missing_deps = [dep for dep, available in dependencies.items() if not available]
    
    if missing_deps:
        logger.warning(f"⚠️ Missing dependencies: {missing_deps}")
        logger.info("📦 Consider running: pip install pandas numpy sqlalchemy requests tensorflow")
    
    # 2. Setup core configurations
    logger.info("⚙️ Setting up core configurations...")
    
    setup_success = {
        'logging': setup_logging(app),
        'database': setup_database(app),
        'security': setup_security(app),
        'cors': setup_cors(app),
        'routes': setup_routes(app)
    }
    
    # 3. Setup API protection
    logger.info("🔒 Setting up API protection...")
    try:
        setup_protected_endpoints(app)
        setup_success['api_protection'] = True
    except Exception as e:
        logger.error(f"❌ API protection setup failed: {e}", exc_info=True)
        setup_success['api_protection'] = False
    
    # 4. Register blueprints
    logger.info("📋 Registering blueprints...")
    try:
        blueprints_status = setup_blueprints(app)
        setup_success['blueprints'] = len(blueprints_status['loaded']) > 0
        
        # Log blueprint summary
        logger.info(f"📊 Blueprint Summary:")
        logger.info(f"   ✅ Loaded: {len(blueprints_status['loaded'])}")
        logger.info(f"   ❌ Failed: {len(blueprints_status['failed'])}")  
        logger.info(f"   ⚠️ Skipped: {len(blueprints_status['skipped'])}")
        
        if blueprints_status['failed']:
            logger.error(f"❌ Critical blueprint failures: {blueprints_status['failed']}")
        
    except Exception as e:
        logger.error(f"❌ Blueprint setup failed: {e}", exc_info=True)
        setup_success['blueprints'] = False
    
    # 5. Setup Telegram integration
    logger.info("🤖 Setting up Telegram integration...")
    try:
        telegram_result = setup_telegram_integration(app)
        setup_success['telegram'] = telegram_result['status'] == 'active'
        logger.info(f"🤖 Telegram status: {telegram_result['status']}")
    except Exception as e:
        logger.error(f"❌ Telegram setup failed: {e}", exc_info=True)
        setup_success['telegram'] = False
    
    # 6. Setup keep-alive system
    logger.info("⏰ Setting up keep-alive system...")
    try:
        setup_keep_alive(app, enable=True)
        setup_success['keep_alive'] = True
    except Exception as e:
        logger.error(f"❌ Keep-alive setup failed: {e}", exc_info=True)
        setup_success['keep_alive'] = False
    
    # 7. Initialize enhanced systems
    logger.info("🔧 Initializing enhanced systems...")
    try:
        from core.enhanced_logging_system import enhanced_logger, log_success, log_info
        from core.auth_system import enhanced_auth_system
        
        log_success("Enhanced Logging System initialized in main app")
        log_success("Enhanced Auth System initialized in main app")
        log_info("Refactored Flask app created", {'components': list(setup_success.keys())})
        setup_success['enhanced_systems'] = True
        
    except Exception as e:
        logger.error(f"❌ Enhanced systems initialization failed: {e}", exc_info=True)
        setup_success['enhanced_systems'] = False
    
    # 8. Final setup summary
    successful_components = sum(setup_success.values())
    total_components = len(setup_success)
    
    logger.info(f"🎯 Application Setup Complete:")
    logger.info(f"   ✅ Successful: {successful_components}/{total_components} components")
    
    for component, success in setup_success.items():
        status = "✅" if success else "❌"
        logger.info(f"   {status} {component.replace('_', ' ').title()}")
    
    if successful_components < total_components:
        logger.warning(f"⚠️ Some components failed to initialize")
    else:
        logger.info("🚀 All components initialized successfully!")
    
    return app

# Create Flask app instance
app = create_app()

if __name__ == "__main__":
    try:
        port = int(os.environ.get('PORT', 5000))
        host = os.environ.get('HOST', '0.0.0.0')
        debug = os.environ.get('DEBUG', 'false').lower() == 'true'
        
        logger.info(f"🌟 Starting server on {host}:{port} (debug={debug})")
        
        app.run(
            host=host,
            port=port, 
            debug=debug,
            threaded=True
        )
        
    except Exception as e:
        logger.error(f"❌ Server startup failed: {e}", exc_info=True)
        sys.exit(1)