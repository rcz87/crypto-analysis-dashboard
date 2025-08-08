#!/usr/bin/env python3
"""
Alternative server runner for Replit
"""
import os
import sys

# Ensure proper imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_server():
    """Run the production server"""
    # Import Flask app
    from main import app
    
    # Production configuration
    app.config['DEBUG'] = False
    app.config['TESTING'] = False
    
    # Get Replit port
    port = int(os.environ.get('PORT', 5000))
    
    print(f"🚀 Starting CryptoSage AI on port {port}")
    
    # Run server
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False,
        use_reloader=False
    )

if __name__ == "__main__":
    run_server()