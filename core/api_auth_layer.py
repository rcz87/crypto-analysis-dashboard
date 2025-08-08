#!/usr/bin/env python3
"""
🔑 API Authentication Layer - Secure Access Control
Sistem otentikasi minimal untuk membatasi akses bot ke internal API
"""

import os
import logging
import hashlib
import hmac
import time
import jwt
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Tuple
from functools import wraps
from flask import request, jsonify, g

logger = logging.getLogger(__name__)

class APIAuthLayer:
    """
    🔑 API Authentication Layer untuk secure access control
    
    Features:
    - API Key authentication
    - JWT token support
    - HMAC signature verification
    - Rate limiting per API key
    - Access logging dan monitoring
    - Key rotation support
    """
    
    def __init__(self, redis_manager=None):
        """Initialize API Authentication Layer"""
        self.redis_manager = redis_manager
        self.secret_key = os.environ.get('API_SECRET_KEY', 'default-secret-key-change-in-production')
        self.jwt_secret = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
        
        # Default API keys (should be moved to database/redis in production)
        self.default_api_keys = {
            'INTERNAL_BOT': {
                'key': os.environ.get('INTERNAL_BOT_API_KEY', 'sk_bot_internal_2025'),
                'permissions': ['signal_read', 'signal_write', 'analytics_read'],
                'rate_limit': 1000,  # requests per hour
                'description': 'Internal bot access'
            },
            'TELEGRAM_BOT': {
                'key': os.environ.get('TELEGRAM_BOT_API_KEY', 'sk_tg_bot_2025'),
                'permissions': ['signal_read', 'notification_write'],
                'rate_limit': 500,
                'description': 'Telegram bot access'
            },
            'GPTS_SERVICE': {
                'key': os.environ.get('GPTS_SERVICE_API_KEY', 'sk_gpts_service_2025'),
                'permissions': ['signal_read', 'signal_write', 'analytics_read', 'backtest_run', 'news_read', 'gpts_access'],
                'rate_limit': 2000,
                'description': 'GPTs service access'
            }
        }
        
        logger.info("🔑 API Authentication Layer initialized")
    
    def authenticate_api_key(self, require_permissions: List[str] = None):
        """
        Decorator untuk API key authentication
        
        Args:
            require_permissions: List of required permissions
        """
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                try:
                    # Extract API key
                    api_key = self._extract_api_key()
                    if not api_key:
                        return self._auth_error("API key required", 401)
                    
                    # Validate API key
                    key_info = self._validate_api_key(api_key)
                    if not key_info:
                        return self._auth_error("Invalid API key", 401)
                    
                    # Check permissions
                    if require_permissions:
                        if not self._check_permissions(key_info, require_permissions):
                            return self._auth_error("Insufficient permissions", 403)
                    
                    # Check rate limiting
                    if not self._check_rate_limit(key_info):
                        return self._auth_error("Rate limit exceeded", 429)
                    
                    # Store auth info untuk access logging
                    g.auth_info = {
                        'api_key_id': key_info['id'],
                        'permissions': key_info['permissions'],
                        'authenticated': True
                    }
                    
                    # Log successful access
                    self._log_api_access(key_info, success=True)
                    
                    return f(*args, **kwargs)
                    
                except Exception as e:
                    logger.error(f"Authentication error: {e}")
                    return self._auth_error("Authentication failed", 500)
            
            return decorated_function
        return decorator
    
    def authenticate_jwt(self, require_permissions: List[str] = None):
        """
        Decorator untuk JWT token authentication
        
        Args:
            require_permissions: List of required permissions
        """
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                try:
                    # Extract JWT token
                    token = self._extract_jwt_token()
                    if not token:
                        return self._auth_error("JWT token required", 401)
                    
                    # Validate and decode JWT
                    payload = self._validate_jwt_token(token)
                    if not payload:
                        return self._auth_error("Invalid JWT token", 401)
                    
                    # Check permissions
                    token_permissions = payload.get('permissions', [])
                    if require_permissions:
                        if not all(perm in token_permissions for perm in require_permissions):
                            return self._auth_error("Insufficient permissions", 403)
                    
                    # Store auth info
                    g.auth_info = {
                        'user_id': payload.get('user_id'),
                        'permissions': token_permissions,
                        'authenticated': True,
                        'auth_type': 'JWT'
                    }
                    
                    return f(*args, **kwargs)
                    
                except Exception as e:
                    logger.error(f"JWT authentication error: {e}")
                    return self._auth_error("JWT authentication failed", 500)
            
            return decorated_function
        return decorator
    
    def verify_hmac_signature(self, secret_key: str = None):
        """
        Decorator untuk HMAC signature verification
        
        Args:
            secret_key: Secret key untuk HMAC verification
        """
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                try:
                    # Extract signature
                    signature = request.headers.get('X-Signature')
                    if not signature:
                        return self._auth_error("HMAC signature required", 401)
                    
                    # Verify signature
                    if not self._verify_hmac_signature(signature, secret_key):
                        return self._auth_error("Invalid HMAC signature", 401)
                    
                    # Store auth info
                    g.auth_info = {
                        'authenticated': True,
                        'auth_type': 'HMAC'
                    }
                    
                    return f(*args, **kwargs)
                    
                except Exception as e:
                    logger.error(f"HMAC verification error: {e}")
                    return self._auth_error("HMAC verification failed", 500)
            
            return decorated_function
        return decorator
    
    def generate_api_key(self, key_id: str, permissions: List[str], 
                        rate_limit: int = 1000, description: str = "") -> str:
        """
        Generate new API key
        
        Args:
            key_id: Unique identifier untuk key
            permissions: List of permissions
            rate_limit: Rate limit per hour
            description: Key description
            
        Returns:
            api_key: Generated API key
        """
        try:
            # Generate secure API key
            import secrets
            api_key = f"sk_{key_id}_{secrets.token_urlsafe(32)}"
            
            # Store key info
            key_info = {
                'id': key_id,
                'key': api_key,
                'permissions': permissions,
                'rate_limit': rate_limit,
                'description': description,
                'created_at': datetime.now(timezone.utc).isoformat(),
                'last_used': None,
                'is_active': True
            }
            
            if self.redis_manager:
                cache_key = f"api_key:{api_key}"
                self.redis_manager.set_cache(cache_key, key_info)
            
            logger.info(f"🔑 API key generated: {key_id}")
            return api_key
            
        except Exception as e:
            logger.error(f"Error generating API key: {e}")
            raise
    
    def generate_jwt_token(self, user_id: str, permissions: List[str], 
                          expires_hours: int = 24) -> str:
        """
        Generate JWT token
        
        Args:
            user_id: User identifier
            permissions: List of permissions
            expires_hours: Token expiration in hours
            
        Returns:
            jwt_token: Generated JWT token
        """
        try:
            payload = {
                'user_id': user_id,
                'permissions': permissions,
                'iat': datetime.now(timezone.utc),
                'exp': datetime.now(timezone.utc) + timedelta(hours=expires_hours)
            }
            
            token = jwt.encode(payload, self.jwt_secret, algorithm='HS256')
            
            logger.info(f"🔑 JWT token generated for user: {user_id}")
            return token
            
        except Exception as e:
            logger.error(f"Error generating JWT token: {e}")
            raise
    
    def revoke_api_key(self, api_key: str) -> bool:
        """
        Revoke API key
        
        Args:
            api_key: API key to revoke
            
        Returns:
            success: Boolean indicating success
        """
        try:
            if self.redis_manager:
                cache_key = f"api_key:{api_key}"
                key_info = self.redis_manager.get_cache(cache_key)
                
                if key_info:
                    key_info['is_active'] = False
                    key_info['revoked_at'] = datetime.now(timezone.utc).isoformat()
                    self.redis_manager.set_cache(cache_key, key_info)
                    
                    logger.info(f"🔑 API key revoked: {key_info.get('id', 'unknown')}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error revoking API key: {e}")
            return False
    
    def get_api_key_usage(self, api_key: str) -> Dict[str, Any]:
        """Get API key usage statistics"""
        try:
            if not self.redis_manager:
                return {'error': 'Redis not available'}
            
            # Get key info
            cache_key = f"api_key:{api_key}"
            key_info = self.redis_manager.get_cache(cache_key)
            
            if not key_info:
                return {'error': 'API key not found'}
            
            # Get usage stats
            usage_key = f"api_usage:{api_key}"
            usage_stats = self.redis_manager.get_cache(usage_key) or {}
            
            return {
                'key_id': key_info.get('id'),
                'description': key_info.get('description'),
                'permissions': key_info.get('permissions'),
                'rate_limit': key_info.get('rate_limit'),
                'created_at': key_info.get('created_at'),
                'last_used': key_info.get('last_used'),
                'is_active': key_info.get('is_active'),
                'usage_stats': usage_stats
            }
            
        except Exception as e:
            logger.error(f"Error getting API key usage: {e}")
            return {'error': str(e)}
    
    def _extract_api_key(self) -> Optional[str]:
        """Extract API key dari request"""
        # Check Authorization header
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            return auth_header[7:]
        
        # Check X-API-Key header
        api_key = request.headers.get('X-API-Key')
        if api_key:
            return api_key
        
        # Check query parameter
        api_key = request.args.get('api_key')
        if api_key:
            return api_key
        
        return None
    
    def _extract_jwt_token(self) -> Optional[str]:
        """Extract JWT token dari request"""
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]
            # Simple check to distinguish JWT from API key
            if '.' in token:  # JWT has dots
                return token
        
        return None
    
    def _validate_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Validate API key dan return key info"""
        try:
            # Check default keys first
            for key_id, key_data in self.default_api_keys.items():
                if key_data['key'] == api_key:
                    return {
                        'id': key_id,
                        'permissions': key_data['permissions'],
                        'rate_limit': key_data['rate_limit'],
                        'description': key_data['description'],
                        'is_active': True
                    }
            
            # Check Redis cache
            if self.redis_manager:
                cache_key = f"api_key:{api_key}"
                key_info = self.redis_manager.get_cache(cache_key)
                
                if key_info and key_info.get('is_active', False):
                    # Update last used
                    key_info['last_used'] = datetime.now(timezone.utc).isoformat()
                    self.redis_manager.set_cache(cache_key, key_info)
                    
                    return key_info
            
            return None
            
        except Exception as e:
            logger.error(f"Error validating API key: {e}")
            return None
    
    def _validate_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate JWT token dan return payload"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
            
            # Check expiration
            exp = payload.get('exp')
            if exp and datetime.fromtimestamp(exp, timezone.utc) < datetime.now(timezone.utc):
                return None
            
            return payload
            
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid JWT token: {e}")
            return None
        except Exception as e:
            logger.error(f"Error validating JWT token: {e}")
            return None
    
    def _verify_hmac_signature(self, signature: str, secret_key: str = None) -> bool:
        """Verify HMAC signature"""
        try:
            if not secret_key:
                secret_key = self.secret_key
            
            # Get request data
            timestamp = request.headers.get('X-Timestamp', '')
            if not timestamp:
                return False
            
            # Check timestamp (prevent replay attacks)
            try:
                request_time = float(timestamp)
                current_time = time.time()
                if abs(current_time - request_time) > 300:  # 5 minutes tolerance
                    return False
            except ValueError:
                return False
            
            # Get request body
            if request.is_json:
                body = request.get_data()
            else:
                body = b''
            
            # Build message to verify
            message = f"{request.method}{request.path}{timestamp}".encode() + body
            
            # Calculate expected signature
            expected_signature = hmac.new(
                secret_key.encode(),
                message,
                hashlib.sha256
            ).hexdigest()
            
            # Compare signatures
            return hmac.compare_digest(signature, expected_signature)
            
        except Exception as e:
            logger.error(f"Error verifying HMAC signature: {e}")
            return False
    
    def _check_permissions(self, key_info: Dict[str, Any], required_permissions: List[str]) -> bool:
        """Check if API key has required permissions"""
        key_permissions = key_info.get('permissions', [])
        return all(perm in key_permissions for perm in required_permissions)
    
    def _check_rate_limit(self, key_info: Dict[str, Any]) -> bool:
        """Check rate limiting untuk API key"""
        try:
            if not self.redis_manager:
                return True  # No rate limiting if Redis not available
            
            key_id = key_info.get('id')
            rate_limit = key_info.get('rate_limit', 1000)
            
            # Rate limiting key
            rate_key = f"rate_limit:{key_id}"
            current_hour = int(time.time() / 3600)
            rate_key_with_hour = f"{rate_key}:{current_hour}"
            
            # Get current count
            current_count = self.redis_manager.get_cache(rate_key_with_hour) or 0
            
            if current_count >= rate_limit:
                return False
            
            # Increment count
            self.redis_manager.set_cache(rate_key_with_hour, current_count + 1, expire_seconds=3600)
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking rate limit: {e}")
            return True  # Allow on error
    
    def _log_api_access(self, key_info: Dict[str, Any], success: bool = True):
        """Log API access untuk monitoring"""
        try:
            access_log = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'key_id': key_info.get('id'),
                'endpoint': request.path,
                'method': request.method,
                'ip_address': request.remote_addr,
                'user_agent': request.headers.get('User-Agent', ''),
                'success': success
            }
            
            if self.redis_manager:
                # Store recent access logs
                log_key = f"access_log:{key_info.get('id')}"
                recent_logs = self.redis_manager.get_cache(log_key) or []
                recent_logs.append(access_log)
                
                # Keep only last 100 logs
                if len(recent_logs) > 100:
                    recent_logs = recent_logs[-100:]
                
                self.redis_manager.set_cache(log_key, recent_logs, expire_seconds=86400)  # 24 hours
            
            logger.info(f"🔑 API access: {key_info.get('id')} -> {request.method} {request.path}")
            
        except Exception as e:
            logger.error(f"Error logging API access: {e}")
    
    def _auth_error(self, message: str, status_code: int) -> Tuple[Dict[str, Any], int]:
        """Return authentication error response"""
        return {
            'error': 'AUTHENTICATION_ERROR',
            'message': message,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }, status_code

# Global auth layer instance
auth_layer = None

def get_auth_layer():
    """Get global auth layer instance"""
    global auth_layer
    if auth_layer is None:
        try:
            from core.redis_manager import RedisManager
            redis_manager = RedisManager()
            auth_layer = APIAuthLayer(redis_manager=redis_manager)
        except Exception as e:
            logger.error(f"Failed to initialize auth layer: {e}")
            auth_layer = APIAuthLayer()  # Fallback without Redis
    
    return auth_layer

# Convenience decorators
def require_api_key(permissions: List[str] = None):
    """Require API key authentication"""
    return get_auth_layer().authenticate_api_key(permissions)

def require_jwt(permissions: List[str] = None):
    """Require JWT authentication"""
    return get_auth_layer().authenticate_jwt(permissions)

def require_hmac(secret_key: str = None):
    """Require HMAC signature verification"""
    return get_auth_layer().verify_hmac_signature(secret_key)

# Export
__all__ = [
    'APIAuthLayer', 'get_auth_layer', 'require_api_key', 'require_jwt', 'require_hmac'
]