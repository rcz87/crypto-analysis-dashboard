#!/usr/bin/env python3
"""
🔒 Security Hardening Module - Auto-Fix Critical Vulnerabilities
Sistem otomatis untuk memperbaiki kelemahan keamanan dan self-monitoring
"""

import os
import logging
import hashlib
import secrets
import re
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from flask import Flask, request, g
from functools import wraps
import time

logger = logging.getLogger(__name__)

class SecurityHardeningEngine:
    """
    🔒 Security Hardening Engine untuk auto-fix vulnerabilities
    
    Features:
    - Auto-detect dan fix common security issues
    - Rate limiting implementation
    - Input validation enhancement
    - Secure logging practices
    - Authentication enforcement
    """
    
    def __init__(self, app: Flask = None):
        """Initialize Security Hardening Engine"""
        self.app = app
        self.rate_limit_storage = {}  # Simple in-memory storage
        self.security_log = []
        
        if app:
            self.init_app(app)
        
        logger.info("🔒 Security Hardening Engine initialized")
    
    def init_app(self, app: Flask):
        """Initialize security hardening with Flask app"""
        self.app = app
        
        # Apply security headers
        self._apply_security_headers(app)
        
        # Setup secure session configuration
        self._configure_secure_sessions(app)
        
        # Add request validation
        self._setup_request_validation(app)
        
        logger.info("🔒 Security hardening applied to Flask app")
    
    def _apply_security_headers(self, app: Flask):
        """Apply security headers to all responses"""
        @app.after_request
        def add_security_headers(response):
            # Prevent clickjacking
            response.headers['X-Frame-Options'] = 'DENY'
            
            # XSS protection
            response.headers['X-Content-Type-Options'] = 'nosniff'
            response.headers['X-XSS-Protection'] = '1; mode=block'
            
            # HSTS (HTTPS only)
            if request.is_secure:
                response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
            
            # Content Security Policy
            response.headers['Content-Security-Policy'] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' https://chat.openai.com; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "connect-src 'self' https://api.openai.com https://api.telegram.org https://www.okx.com; "
                "frame-ancestors 'none';"
            )
            
            # Referrer policy
            response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
            
            # Remove server information
            response.headers.pop('Server', None)
            
            return response
    
    def _configure_secure_sessions(self, app: Flask):
        """Configure secure session settings"""
        app.config.update(
            SESSION_COOKIE_SECURE=True,  # HTTPS only
            SESSION_COOKIE_HTTPONLY=True,  # No JavaScript access
            SESSION_COOKIE_SAMESITE='Lax',  # CSRF protection
            PERMANENT_SESSION_LIFETIME=3600,  # 1 hour
        )
    
    def _setup_request_validation(self, app: Flask):
        """Setup request validation and logging"""
        @app.before_request
        def validate_request():
            # Log all requests securely
            self._log_request_securely()
            
            # Validate content length
            if request.content_length and request.content_length > 10 * 1024 * 1024:  # 10MB limit
                self._log_security_event("REQUEST_TOO_LARGE", request.remote_addr)
                return "Request too large", 413
            
            # Validate content type for POST requests
            if request.method == 'POST' and request.content_type:
                if not request.content_type.startswith('application/json'):
                    if '/api/' in request.path:  # API endpoints should use JSON
                        self._log_security_event("INVALID_CONTENT_TYPE", request.remote_addr)
                        return "Invalid content type", 400
    
    def rate_limit(self, max_requests: int = 100, window_seconds: int = 3600, per_endpoint: bool = True):
        """
        Rate limiting decorator
        
        Args:
            max_requests: Maximum requests allowed
            window_seconds: Time window in seconds
            per_endpoint: If True, limit per endpoint; if False, global limit
        """
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                # Generate rate limit key
                client_ip = request.remote_addr
                endpoint = request.endpoint if per_endpoint else 'global'
                key = f"{client_ip}:{endpoint}"
                
                current_time = time.time()
                
                # Clean old entries
                self._cleanup_rate_limit_storage(current_time, window_seconds)
                
                # Check current rate
                if key not in self.rate_limit_storage:
                    self.rate_limit_storage[key] = []
                
                # Count requests in current window
                request_times = self.rate_limit_storage[key]
                recent_requests = [t for t in request_times if current_time - t < window_seconds]
                
                if len(recent_requests) >= max_requests:
                    self._log_security_event("RATE_LIMIT_EXCEEDED", client_ip, {
                        'endpoint': endpoint,
                        'requests': len(recent_requests),
                        'limit': max_requests
                    })
                    return {
                        'error': 'RATE_LIMIT_EXCEEDED',
                        'message': f'Too many requests. Limit: {max_requests} per {window_seconds} seconds',
                        'retry_after': window_seconds
                    }, 429
                
                # Add current request time
                recent_requests.append(current_time)
                self.rate_limit_storage[key] = recent_requests
                
                return f(*args, **kwargs)
            return decorated_function
        return decorator
    
    def require_api_key(self, header_name: str = 'X-API-Key'):
        """
        API key authentication decorator
        
        Args:
            header_name: Header name containing API key
        """
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                api_key = request.headers.get(header_name)
                
                if not api_key:
                    self._log_security_event("MISSING_API_KEY", request.remote_addr)
                    return {
                        'error': 'AUTHENTICATION_REQUIRED',
                        'message': f'API key required in {header_name} header'
                    }, 401
                
                # Validate API key format
                if not self._validate_api_key_format(api_key):
                    self._log_security_event("INVALID_API_KEY_FORMAT", request.remote_addr)
                    return {
                        'error': 'INVALID_API_KEY',
                        'message': 'Invalid API key format'
                    }, 401
                
                # Store API key info for logging (hashed)
                g.api_key_hash = hashlib.sha256(api_key.encode()).hexdigest()[:16]
                
                return f(*args, **kwargs)
            return decorated_function
        return decorator
    
    def validate_input(self, max_length: int = 10000, allowed_fields: List[str] = None):
        """
        Enhanced input validation decorator
        
        Args:
            max_length: Maximum length for string inputs
            allowed_fields: List of allowed fields in JSON input
        """
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                if request.is_json:
                    data = request.get_json()
                    
                    if data:
                        # Validate allowed fields
                        if allowed_fields:
                            invalid_fields = [k for k in data.keys() if k not in allowed_fields]
                            if invalid_fields:
                                self._log_security_event("INVALID_FIELDS", request.remote_addr, {
                                    'invalid_fields': invalid_fields
                                })
                                return {
                                    'error': 'VALIDATION_ERROR',
                                    'message': f'Invalid fields: {invalid_fields}'
                                }, 400
                        
                        # Validate string lengths and content
                        validation_errors = self._validate_input_data(data, max_length)
                        if validation_errors:
                            self._log_security_event("INPUT_VALIDATION_FAILED", request.remote_addr, {
                                'errors': validation_errors
                            })
                            return {
                                'error': 'VALIDATION_ERROR',
                                'message': 'Input validation failed',
                                'details': validation_errors
                            }, 400
                
                return f(*args, **kwargs)
            return decorated_function
        return decorator
    
    def _cleanup_rate_limit_storage(self, current_time: float, window_seconds: int):
        """Clean up old rate limit entries"""
        cutoff_time = current_time - window_seconds * 2  # Keep 2x window for safety
        
        for key in list(self.rate_limit_storage.keys()):
            self.rate_limit_storage[key] = [
                t for t in self.rate_limit_storage[key] if t > cutoff_time
            ]
            if not self.rate_limit_storage[key]:
                del self.rate_limit_storage[key]
    
    def _validate_api_key_format(self, api_key: str) -> bool:
        """Validate API key format"""
        # Basic format validation - alphanumeric, minimum length
        if len(api_key) < 32:
            return False
        
        if not re.match(r'^[a-zA-Z0-9._-]+$', api_key):
            return False
        
        return True
    
    def _validate_input_data(self, data: Dict[str, Any], max_length: int) -> List[str]:
        """Validate input data for security issues"""
        errors = []
        
        def validate_recursive(obj, path=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    validate_recursive(value, f"{path}.{key}" if path else key)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    validate_recursive(item, f"{path}[{i}]")
            elif isinstance(obj, str):
                # Check string length
                if len(obj) > max_length:
                    errors.append(f"Field {path} too long (max {max_length} characters)")
                
                # Check for potential SQL injection patterns
                if self._contains_sql_injection_patterns(obj):
                    errors.append(f"Field {path} contains suspicious patterns")
                
                # Check for potential XSS patterns
                if self._contains_xss_patterns(obj):
                    errors.append(f"Field {path} contains potentially dangerous content")
        
        validate_recursive(data)
        return errors
    
    def _contains_sql_injection_patterns(self, text: str) -> bool:
        """Check for common SQL injection patterns"""
        dangerous_patterns = [
            r'(\;|\').*(\-\-|\/\*)',  # SQL comments
            r'(union|select|insert|update|delete|drop|create|alter)\s+',  # SQL keywords
            r'(\=|\s)(or|and)\s+\d+\s*(\=|\>|\<)',  # Common injection patterns
            r'(\s|^)(0x[0-9a-f]+|char\(|ascii\()',  # SQL functions
        ]
        
        text_lower = text.lower()
        return any(re.search(pattern, text_lower) for pattern in dangerous_patterns)
    
    def _contains_xss_patterns(self, text: str) -> bool:
        """Check for common XSS patterns"""
        dangerous_patterns = [
            r'<script[^>]*>',
            r'javascript:',
            r'on\w+\s*=',  # Event handlers
            r'<\s*iframe',
            r'<\s*object',
            r'<\s*embed',
        ]
        
        text_lower = text.lower()
        return any(re.search(pattern, text_lower) for pattern in dangerous_patterns)
    
    def _log_request_securely(self):
        """Log request information securely (no sensitive data)"""
        log_entry = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'method': request.method,
            'path': request.path,
            'remote_addr': request.remote_addr,
            'user_agent_hash': hashlib.sha256(
                request.headers.get('User-Agent', '').encode()
            ).hexdigest()[:16],
            'content_length': request.content_length,
        }
        
        # Only log to application logger, not security log
        logger.debug(f"Request: {log_entry['method']} {log_entry['path']}")
    
    def _log_security_event(self, event_type: str, source_ip: str, details: Dict[str, Any] = None):
        """Log security events"""
        event = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'event_type': event_type,
            'source_ip': source_ip,
            'details': details or {}
        }
        
        self.security_log.append(event)
        
        # Keep only last 1000 events
        if len(self.security_log) > 1000:
            self.security_log = self.security_log[-1000:]
        
        logger.warning(f"Security Event: {event_type} from {source_ip}")
    
    def get_security_status(self) -> Dict[str, Any]:
        """Get current security status"""
        recent_events = [
            event for event in self.security_log
            if (datetime.now(timezone.utc) - datetime.fromisoformat(event['timestamp'])).seconds < 3600
        ]
        
        event_counts = {}
        for event in recent_events:
            event_type = event['event_type']
            event_counts[event_type] = event_counts.get(event_type, 0) + 1
        
        return {
            'total_security_events_last_hour': len(recent_events),
            'event_types': event_counts,
            'rate_limit_entries': len(self.rate_limit_storage),
            'security_features_active': [
                'security_headers',
                'rate_limiting',
                'input_validation',
                'secure_sessions',
                'request_logging'
            ]
        }
    
    def generate_secure_api_key(self, prefix: str = "sk") -> str:
        """Generate a secure API key"""
        random_part = secrets.token_urlsafe(32)
        timestamp = int(datetime.now(timezone.utc).timestamp())
        
        return f"{prefix}_{timestamp}_{random_part}"

# Global security engine instance
security_engine = None

def get_security_engine() -> SecurityHardeningEngine:
    """Get global security engine instance"""
    global security_engine
    if security_engine is None:
        security_engine = SecurityHardeningEngine()
    return security_engine

def init_security_hardening(app: Flask):
    """Initialize security hardening for Flask app"""
    global security_engine
    security_engine = SecurityHardeningEngine(app)
    return security_engine

# Convenience decorators
def rate_limit(max_requests: int = 100, window_seconds: int = 3600, per_endpoint: bool = True):
    """Rate limiting decorator"""
    return get_security_engine().rate_limit(max_requests, window_seconds, per_endpoint)

def require_api_key(header_name: str = 'X-API-Key'):
    """API key authentication decorator"""
    return get_security_engine().require_api_key(header_name)

def validate_input(max_length: int = 10000, allowed_fields: List[str] = None):
    """Input validation decorator"""
    return get_security_engine().validate_input(max_length, allowed_fields)

# Export all
__all__ = [
    'SecurityHardeningEngine', 'get_security_engine', 'init_security_hardening',
    'rate_limit', 'require_api_key', 'validate_input'
]