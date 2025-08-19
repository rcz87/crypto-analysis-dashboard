"""
Enhanced Auth System - Security untuk API Endpoints
Mengatasi masalah: Tidak ada validasi token, bisa dieksploitasi
"""

import os
import jwt
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from functools import wraps
from flask import request, jsonify
import secrets
import time

class EnhancedAuthSystem:
    """
    Enhanced authentication system dengan multiple security layers
    """
    
    def __init__(self):
        self.secret_key = os.environ.get('JWT_SECRET_KEY', self._generate_secret_key())
        self.api_keys = self._load_api_keys()
        self.rate_limits = {}
        self.blocked_ips = set()
        
        # Security settings
        self.max_requests_per_minute = 60
        self.max_requests_per_hour = 1000
        self.token_expiry_hours = 24
        
        print("🔐 Enhanced Auth System initialized")
    
    def _generate_secret_key(self) -> str:
        """Generate secure secret key"""
        return secrets.token_urlsafe(32)
    
    def _load_api_keys(self) -> Dict[str, Dict]:
        """Load API keys dari environment atau generate default"""
        api_keys = {}
        
        # Default API key untuk development
        default_key = os.environ.get('DEFAULT_API_KEY', 'gpts_api_key_2025')
        api_keys[default_key] = {
            'name': 'Default GPTs API',
            'permissions': ['read', 'write'],
            'rate_limit': 1000,
            'created_at': datetime.now().isoformat()
        }
        
        # Admin API key
        admin_key = os.environ.get('ADMIN_API_KEY', 'admin_gpts_2025_secure')
        api_keys[admin_key] = {
            'name': 'Admin Access',
            'permissions': ['read', 'write', 'admin'],
            'rate_limit': 10000,
            'created_at': datetime.now().isoformat()
        }
        
        print(f"🔑 Loaded {len(api_keys)} API keys")
        return api_keys
    
    def generate_jwt_token(self, payload: Dict) -> str:
        """Generate JWT token"""
        payload.update({
            'exp': datetime.utcnow() + timedelta(hours=self.token_expiry_hours),
            'iat': datetime.utcnow(),
            'iss': 'gpts-crypto-api'
        })
        
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
    
    def verify_jwt_token(self, token: str) -> Optional[Dict]:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def verify_api_key(self, api_key: str) -> Optional[Dict]:
        """Verify API key"""
        return self.api_keys.get(api_key)
    
    def check_rate_limit(self, client_id: str, endpoint: str) -> Dict[str, Any]:
        """Check rate limiting"""
        current_time = time.time()
        
        # Create unique key untuk client + endpoint
        key = f"{client_id}:{endpoint}"
        
        if key not in self.rate_limits:
            self.rate_limits[key] = {
                'requests': [],
                'blocked_until': 0
            }
        
        client_data = self.rate_limits[key]
        
        # Check if still blocked
        if current_time < client_data['blocked_until']:
            return {
                'allowed': False,
                'reason': 'Rate limit exceeded',
                'retry_after': client_data['blocked_until'] - current_time
            }
        
        # Clean old requests (older than 1 hour)
        client_data['requests'] = [
            req_time for req_time in client_data['requests']
            if current_time - req_time < 3600
        ]
        
        # Check hourly limit
        if len(client_data['requests']) >= self.max_requests_per_hour:
            client_data['blocked_until'] = current_time + 3600  # Block for 1 hour
            return {
                'allowed': False,
                'reason': 'Hourly rate limit exceeded',
                'retry_after': 3600
            }
        
        # Check minute limit
        minute_requests = [
            req_time for req_time in client_data['requests']
            if current_time - req_time < 60
        ]
        
        if len(minute_requests) >= self.max_requests_per_minute:
            client_data['blocked_until'] = current_time + 60  # Block for 1 minute
            return {
                'allowed': False,
                'reason': 'Minute rate limit exceeded',
                'retry_after': 60
            }
        
        # Add current request
        client_data['requests'].append(current_time)
        
        return {
            'allowed': True,
            'remaining_hour': self.max_requests_per_hour - len(client_data['requests']),
            'remaining_minute': self.max_requests_per_minute - len(minute_requests) - 1
        }
    
    def get_client_id(self, request) -> str:
        """Get client identifier dari request"""
        # Priority: API key > JWT token > IP address
        api_key = request.headers.get('X-API-Key') or request.args.get('api_key')
        if api_key:
            return f"api_key:{hashlib.md5(api_key.encode()).hexdigest()[:8]}"
        
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]
            payload = self.verify_jwt_token(token)
            if payload:
                return f"jwt:{payload.get('sub', 'unknown')}"
        
        return f"ip:{request.remote_addr}"
    
    def is_ip_blocked(self, ip: str) -> bool:
        """Check if IP is blocked"""
        return ip in self.blocked_ips
    
    def block_ip(self, ip: str, reason: str = "Security violation"):
        """Block IP address"""
        self.blocked_ips.add(ip)
        print(f"🚫 Blocked IP {ip}: {reason}")

def require_auth(permissions: List[str] = None, rate_limit: bool = True):
    """Authentication decorator"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            auth_system = enhanced_auth_system
            
            # Check blocked IP
            client_ip = request.remote_addr
            if auth_system.is_ip_blocked(client_ip):
                return jsonify({
                    'status': 'error',
                    'message': 'Access denied: IP blocked',
                    'error_code': 'IP_BLOCKED'
                }), 403
            
            # Get client ID untuk rate limiting
            client_id = auth_system.get_client_id(request)
            
            # Check rate limit
            if rate_limit:
                rate_check = auth_system.check_rate_limit(client_id, request.endpoint or 'unknown')
                if not rate_check['allowed']:
                    response = jsonify({
                        'status': 'error',
                        'message': f"Rate limit exceeded: {rate_check['reason']}",
                        'error_code': 'RATE_LIMIT_EXCEEDED',
                        'retry_after': rate_check['retry_after']
                    })
                    response.headers['Retry-After'] = str(int(rate_check['retry_after']))
                    return response, 429
            
            # Check authentication
            authenticated = False
            user_permissions = []
            
            # Method 1: API Key
            api_key = request.headers.get('X-API-Key') or request.args.get('api_key')
            if api_key:
                key_data = auth_system.verify_api_key(api_key)
                if key_data:
                    authenticated = True
                    user_permissions = key_data.get('permissions', [])
                    print(f"🔑 API Key auth: {key_data['name']}")
            
            # Method 2: JWT Token
            if not authenticated:
                auth_header = request.headers.get('Authorization', '')
                if auth_header.startswith('Bearer '):
                    token = auth_header[7:]
                    payload = auth_system.verify_jwt_token(token)
                    if payload:
                        authenticated = True
                        user_permissions = payload.get('permissions', ['read'])
                        print(f"🎫 JWT auth: {payload.get('sub', 'unknown')}")
            
            # Method 3: Development mode (no auth required)
            if not authenticated and os.environ.get('DEVELOPMENT_MODE', 'true').lower() == 'true':
                authenticated = True
                user_permissions = ['read', 'write']
                print("🔓 Development mode: Auth bypassed")
            
            if not authenticated:
                return jsonify({
                    'status': 'error',
                    'message': 'Authentication required',
                    'error_code': 'AUTH_REQUIRED',
                    'auth_methods': ['API Key (X-API-Key header)', 'JWT Token (Bearer)', 'Query param (?api_key=)']
                }), 401
            
            # Check permissions
            if permissions:
                if not any(perm in user_permissions for perm in permissions):
                    return jsonify({
                        'status': 'error',
                        'message': f'Insufficient permissions. Required: {permissions}',
                        'error_code': 'INSUFFICIENT_PERMISSIONS',
                        'user_permissions': user_permissions
                    }), 403
            
            # Add auth info ke request context
            request.auth_info = {
                'authenticated': True,
                'permissions': user_permissions,
                'client_id': client_id,
                'rate_limit_remaining': rate_check.get('remaining_hour', 0) if rate_limit else None
            }
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

def optional_auth():
    """Optional authentication - don't block if no auth"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            auth_system = enhanced_auth_system
            
            authenticated = False
            user_permissions = []
            
            # Try authentication
            api_key = request.headers.get('X-API-Key') or request.args.get('api_key')
            if api_key:
                key_data = auth_system.verify_api_key(api_key)
                if key_data:
                    authenticated = True
                    user_permissions = key_data.get('permissions', [])
            
            if not authenticated:
                auth_header = request.headers.get('Authorization', '')
                if auth_header.startswith('Bearer '):
                    token = auth_header[7:]
                    payload = auth_system.verify_jwt_token(token)
                    if payload:
                        authenticated = True
                        user_permissions = payload.get('permissions', ['read'])
            
            # Add auth info ke request context
            request.auth_info = {
                'authenticated': authenticated,
                'permissions': user_permissions,
                'client_id': auth_system.get_client_id(request)
            }
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

def admin_required():
    """Require admin permissions"""
    return require_auth(['admin'])

def read_only():
    """Require read permissions"""
    return require_auth(['read'])

def write_access():
    """Require write permissions"""
    return require_auth(['write'])

# Global auth system instance
enhanced_auth_system = EnhancedAuthSystem()

# Utility functions
def get_auth_info():
    """Get current request auth info"""
    return getattr(request, 'auth_info', {
        'authenticated': False,
        'permissions': [],
        'client_id': 'unknown'
    })

def generate_api_key(name: str, permissions: List[str] = None) -> str:
    """Generate new API key"""
    api_key = f"gpts_{secrets.token_urlsafe(16)}"
    enhanced_auth_system.api_keys[api_key] = {
        'name': name,
        'permissions': permissions or ['read'],
        'rate_limit': 1000,
        'created_at': datetime.now().isoformat()
    }
    return api_key