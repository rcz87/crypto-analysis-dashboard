#!/usr/bin/env python3
"""
Alternative Production Starter for Replit
Ensures proper deployment without WSGI complications
"""
import os
import sys
import logging

# Set production environment variables
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_DEBUG'] = 'False'

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def start_production_server():
    """Start the production server"""
    try:
        # Import Flask app
        from main import create_app
        
        app = create_app()
        
        # Get port from environment (Replit deployment)
        port = int(os.environ.get('PORT', 5000))
        host = '0.0.0.0'
        
        logger.info(f"🚀 Starting CryptoSage AI Production Server")
        logger.info(f"🌐 Server: {host}:{port}")
        logger.info(f"🔗 URL: https://crypto-analysis-dashboard-rcz887.replit.app")
        
        # Start server
        app.run(
            host=host,
            port=port,
            debug=False,
            threaded=True,
            use_reloader=False
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to start production server: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    start_production_server()