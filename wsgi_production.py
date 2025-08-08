#!/usr/bin/env python3
"""
WSGI Production Entry Point for Replit Deployment
"""
import os
import sys
import logging

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set production environment
os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('PYTHONPATH', os.path.dirname(os.path.abspath(__file__)))

# Configure logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Ensure proper import path
import sys
import os
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Production WSGI - Absolute simplest approach
import sys
import os

# Ensure we can import from current directory
current_dir = os.path.abspath(os.path.dirname(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Set production environment
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_DEBUG'] = 'False'

# Import Flask app with error handling
try:
    from main import app as application
    
    # Configure for production
    application.config['DEBUG'] = False
    application.config['TESTING'] = False
    application.config['ENV'] = 'production'
    
    logging.info(f"✅ WSGI Production application loaded: {application.name}")
    
except Exception as e:
    logging.error(f"❌ WSGI import failed: {e}")
    # Create minimal fallback app
    from flask import Flask, jsonify
    application = Flask(__name__)
    
    @application.route('/')
    def root():
        return jsonify({"status": "fallback_active", "message": "Import failed, using fallback"})
    
    @application.route('/api/gpts/status')
    def status():
        return jsonify({"status": "fallback", "error": "Main app import failed"})
    
    logging.info("✅ WSGI Fallback application created")

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    application.run(host='0.0.0.0', port=port, debug=False)