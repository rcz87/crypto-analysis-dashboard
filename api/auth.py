"""
Simple API authentication decorator for protected endpoints
"""

from flask import request, jsonify
from functools import wraps
import os
import logging

logger = logging.getLogger(__name__)

def require_api_key(f):
    """
    Decorator to require API key for endpoint access
    Checks for API key in headers or query parameters
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if API key is required
        if os.getenv('API_KEY_REQUIRED', 'false').lower() != 'true':
            # API key not required, allow access
            return f(*args, **kwargs)
        
        # Get expected API key from environment
        expected_key = os.getenv('API_KEY')
        if not expected_key:
            # No API key configured, allow access
            logger.warning("API_KEY_REQUIRED is true but no API_KEY is set")
            return f(*args, **kwargs)
        
        # Check for API key in headers
        api_key = request.headers.get('X-API-KEY')
        
        # Also check Authorization header
        if not api_key:
            auth_header = request.headers.get('Authorization', '')
            if auth_header.startswith('Bearer '):
                api_key = auth_header[7:]
        
        # Also check query parameters as fallback
        if not api_key:
            api_key = request.args.get('api_key')
        
        # Validate API key
        if not api_key:
            return jsonify({
                'error': 'API_KEY_REQUIRED',
                'message': 'API key is required'
            }), 401
        
        if api_key != expected_key:
            return jsonify({
                'error': 'INVALID_API_KEY',
                'message': 'Invalid API key'
            }), 401
        
        # API key is valid, proceed
        return f(*args, **kwargs)
    
    return decorated_function