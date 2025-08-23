# auth.py
import os
from functools import wraps
from flask import request, jsonify
import logging

logger = logging.getLogger(__name__)

def require_api_key(func):
    """Decorator untuk memeriksa API key - mendukung X-API-KEY dan Authorization Bearer"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        api_key_required = os.environ.get('API_KEY_REQUIRED', 'false').lower() == 'true'
        expected_key = os.environ.get("API_KEY")
        
        if not api_key_required:
            return func(*args, **kwargs)  # bypass if disabled
        
        if not expected_key:
            logger.warning("API_KEY environment variable not set but API_KEY_REQUIRED=true")
            return jsonify({
                "success": False,
                "error": "CONFIGURATION_ERROR", 
                "message": "API key validation not properly configured"
            }), 500
        
        # Check X-API-KEY header first (primary method)
        provided_key = request.headers.get("X-API-KEY")
        
        # Fallback to Authorization Bearer format 
        if not provided_key:
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                provided_key = auth_header[7:]  # Remove "Bearer " prefix
        
        if not provided_key:
            return jsonify({
                "success": False,
                "error": "UNAUTHORIZED",
                "message": "API key required. Use X-API-KEY header or Authorization: Bearer token."
            }), 401
        
        # Clean both keys for comparison (strip whitespace)
        expected_clean = expected_key.strip()
        provided_clean = provided_key.strip()
        
        if provided_clean != expected_clean:
            logger.warning(f"Invalid API key attempt from {request.remote_addr}")
            return jsonify({
                "success": False,
                "error": "UNAUTHORIZED", 
                "message": "Invalid API key provided"
            }), 401
            
        return func(*args, **kwargs)
    return wrapper