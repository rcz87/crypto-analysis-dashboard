#!/usr/bin/env python
"""
Run Flask app with SocketIO support using eventlet
Optimized for WebSocket performance
"""

import os
import sys
import logging
import eventlet

# Monkey patch for async support
eventlet.monkey_patch()

from app import create_app

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_socketio_server():
    """
    Run the Flask app with SocketIO using eventlet
    """
    try:
        # Create Flask app with WebSocket integration
        app = create_app('development')
        
        # Get SocketIO instance from app
        if hasattr(app, 'ws_server'):
            socketio = app.ws_server.socketio
            
            # Initialize WebSocket connections on startup
            from core.websocket_app_integration import initialize_websocket_connections
            initialize_websocket_connections()
            
            # Get port from environment or default
            port = int(os.environ.get('PORT', 5000))
            host = '0.0.0.0'  # Bind to all interfaces
            
            logger.info(f"🚀 Starting SocketIO server on {host}:{port}")
            logger.info("✅ WebSocket support enabled with eventlet")
            logger.info("📡 Real-time data streaming active")
            
            # Run with SocketIO and eventlet
            socketio.run(
                app,
                host=host,
                port=port,
                debug=False,  # Don't use debug in production
                use_reloader=False,  # Disable reloader for stability
                log_output=True
            )
        else:
            logger.error("❌ WebSocket server not initialized")
            # Fallback to regular Flask app
            app.run(host='0.0.0.0', port=5000)
            
    except Exception as e:
        logger.error(f"Failed to start SocketIO server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    run_socketio_server()