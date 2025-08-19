#!/usr/bin/env python3
"""
Ultra-simple WSGI for deployment - GUARANTEED to work
"""
import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Production environment
os.environ['FLASK_ENV'] = 'production'

# Import and create application
from main import app

# Set as WSGI application
application = app
application.config['DEBUG'] = False

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    application.run(host='0.0.0.0', port=port, debug=False)