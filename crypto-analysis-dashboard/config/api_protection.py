"""
API Protection - Setup API key protection untuk endpoint penting
"""

import os
import logging
from functools import wraps
from flask import request, jsonify

logger = logging.getLogger(__name__)

def require_api_key(required_permissions=None):
    """
    Decorator untuk require API key pada endpoint penting
    """
    if required_permissions is None:
        required_permissions = ['read']
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get API key from header or query param
            api_key = request.headers.get('X-API-Key') or request.args.get('api_key')
            
            if not api_key:
                return jsonify({
                    'status': 'error',
                    'message': 'API key required',
                    'error_code': 'API_KEY_REQUIRED',
                    'required_permissions': required_permissions
                }), 401
            
            # Validate API key
            valid_keys = {
                os.environ.get('DEFAULT_API_KEY', 'gpts_api_key_2025'): ['read', 'write'],
                os.environ.get('ADMIN_API_KEY', 'admin_gpts_2025_secure'): ['read', 'write', 'admin'],
                'signal_read_key_2025': ['signal_read'],
                'smc_analysis_key_2025': ['smc_read'],
                'performance_key_2025': ['performance_read'],
                'news_analysis_key_2025': ['news_read']
            }
            
            if api_key not in valid_keys:
                return jsonify({
                    'status': 'error',
                    'message': 'Invalid API key',
                    'error_code': 'INVALID_API_KEY'
                }), 401
            
            user_permissions = valid_keys[api_key]
            
            # Check permissions
            if not any(perm in user_permissions for perm in required_permissions):
                return jsonify({
                    'status': 'error',
                    'message': f'Insufficient permissions. Required: {required_permissions}',
                    'error_code': 'INSUFFICIENT_PERMISSIONS',
                    'user_permissions': user_permissions
                }), 403
            
            # Add API info to request context
            request.api_info = {
                'authenticated': True,
                'permissions': user_permissions,
                'required_permissions': required_permissions
            }
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

def setup_protected_endpoints(app):
    """
    Setup API key protection untuk endpoint penting
    """
    protected_endpoints = [
        # Signal endpoints
        {'path': '/api/signal/<path:subpath>', 'permissions': ['signal_read']},
        {'path': '/api/gpts/sinyal/<path:subpath>', 'permissions': ['signal_read']},
        
        # SMC endpoints  
        {'path': '/api/smc/<path:subpath>', 'permissions': ['smc_read']},
        {'path': '/api/smc_*', 'permissions': ['smc_read']},
        
        # Performance endpoints
        {'path': '/api/performance/<path:subpath>', 'permissions': ['performance_read']},
        
        # News endpoints
        {'path': '/api/news/<path:subpath>', 'permissions': ['news_read']},
        
        # Admin endpoints
        {'path': '/api/improvement/run-cycle', 'permissions': ['admin']},
        {'path': '/api/ml/train', 'permissions': ['admin']}
    ]
    
    # Register before_request handler untuk protected paths
    @app.before_request
    def check_api_protection():
        if request.endpoint and any(
            request.path.startswith(ep['path'].replace('<path:subpath>', '').replace('*', ''))
            for ep in protected_endpoints
        ):
            # Find matching endpoint config
            matching_config = None
            for ep_config in protected_endpoints:
                path_pattern = ep_config['path'].replace('<path:subpath>', '').replace('*', '')
                if request.path.startswith(path_pattern):
                    matching_config = ep_config
                    break
            
            if matching_config:
                # Apply protection
                api_key = request.headers.get('X-API-Key') or request.args.get('api_key')
                
                # Allow development mode bypass
                if os.environ.get('DEVELOPMENT_MODE', 'true').lower() == 'true':
                    logger.info(f"🔓 Development mode: API protection bypassed for {request.path}")
                    return
                
                if not api_key:
                    return jsonify({
                        'status': 'error',
                        'message': 'API key required for this endpoint',
                        'error_code': 'API_KEY_REQUIRED',
                        'endpoint': request.path,
                        'required_permissions': matching_config['permissions']
                    }), 401
    
    logger.info(f"✅ API protection setup for {len(protected_endpoints)} endpoint patterns")
    return True