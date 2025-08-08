"""
Keep Alive System - Prevent Replit from sleeping
"""

import os
import threading
import time
import requests
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class KeepAliveManager:
    """
    Manager untuk keep Replit app tetap aktif
    """
    
    def __init__(self, app_url=None, interval=300):  # 5 minutes
        self.app_url = app_url or self._get_app_url()
        self.interval = interval
        self.running = False
        self.thread = None
        
    def _get_app_url(self):
        """Get app URL dari environment"""
        repl_slug = os.environ.get('REPL_SLUG', 'gpts-crypto-api')
        repl_owner = os.environ.get('REPL_OWNER', 'user')
        
        # Try different URL patterns
        possible_urls = [
            f"https://{repl_slug}.{repl_owner}.repl.co",
            f"https://{repl_slug}--{repl_owner}.repl.co", 
            "http://127.0.0.1:5000",
            "http://0.0.0.0:5000"
        ]
        
        return possible_urls[0]  # Use first as primary
    
    def ping_self(self):
        """Ping ke health endpoint"""
        try:
            response = requests.get(f"{self.app_url}/health", timeout=10)
            if response.status_code == 200:
                logger.info(f"✅ Keep-alive ping successful at {datetime.now()}")
                return True
            else:
                logger.warning(f"⚠️ Keep-alive ping failed: {response.status_code}")
                return False
        except Exception as e:
            logger.warning(f"⚠️ Keep-alive ping error: {e}")
            return False
    
    def keep_alive_loop(self):
        """Main keep-alive loop"""
        while self.running:
            try:
                self.ping_self()
                time.sleep(self.interval)
            except Exception as e:
                logger.error(f"❌ Keep-alive loop error: {e}")
                time.sleep(60)  # Wait 1 minute on error
    
    def start(self):
        """Start keep-alive system"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self.keep_alive_loop, daemon=True)
            self.thread.start()
            logger.info(f"🚀 Keep-alive system started: {self.app_url} every {self.interval}s")
    
    def stop(self):
        """Stop keep-alive system"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("🛑 Keep-alive system stopped")

# Global keep-alive manager
keep_alive_manager = None

def setup_keep_alive(app, enable=True):
    """Setup keep-alive system"""
    global keep_alive_manager
    
    if not enable or os.environ.get('DISABLE_KEEP_ALIVE', 'false').lower() == 'true':
        logger.info("🔕 Keep-alive system disabled")
        return
    
    try:
        keep_alive_manager = KeepAliveManager()
        
        # Start after app is ready
        @app.before_first_request
        def start_keep_alive():
            if keep_alive_manager:
                keep_alive_manager.start()
        
        # Add keep-alive status endpoint
        @app.route('/keep-alive/status')
        def keep_alive_status():
            from flask import jsonify
            
            if keep_alive_manager:
                return jsonify({
                    'status': 'active' if keep_alive_manager.running else 'inactive',
                    'url': keep_alive_manager.app_url,
                    'interval': keep_alive_manager.interval,
                    'last_ping': datetime.now().isoformat()
                })
            else:
                return jsonify({'status': 'disabled'})
        
        logger.info("✅ Keep-alive system setup completed")
        
    except Exception as e:
        logger.error(f"❌ Keep-alive setup failed: {e}")

# External ping suggestions
def get_external_ping_suggestions():
    """Get suggestions untuk external monitoring"""
    suggestions = [
        {
            'service': 'UptimeRobot',
            'url': 'https://uptimerobot.com',
            'method': 'HTTP',
            'target': '/health',
            'interval': '5 minutes'
        },
        {
            'service': 'Pingdom',
            'url': 'https://pingdom.com', 
            'method': 'HTTP',
            'target': '/health',
            'interval': '1 minute'
        },
        {
            'service': 'StatusCake',
            'url': 'https://statuscake.com',
            'method': 'HTTP', 
            'target': '/health/detailed',
            'interval': '5 minutes'
        }
    ]
    
    return suggestions