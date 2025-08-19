#!/usr/bin/env python3
"""
Security Manager - Comprehensive security hardening untuk trading platform
Rate limiting, input sanitization, audit logging, encrypted storage
"""

import logging
import time
import hashlib
import hmac
import json
import redis
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import re
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os
from functools import wraps
from flask import request, jsonify, g
import ipaddress

logger = logging.getLogger(__name__)

class SecurityLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ThreatType(Enum):
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    SUSPICIOUS_IP = "suspicious_ip"
    INVALID_INPUT = "invalid_input"
    POTENTIAL_INJECTION = "potential_injection"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    BRUTE_FORCE = "brute_force"
    SUSPICIOUS_PATTERN = "suspicious_pattern"

@dataclass
class SecurityEvent:
    timestamp: float
    event_type: ThreatType
    severity: SecurityLevel
    source_ip: str
    user_agent: str
    endpoint: str
    payload: Dict[str, Any]
    blocked: bool
    details: str

@dataclass
class RateLimitConfig:
    requests_per_minute: int
    requests_per_hour: int
    requests_per_day: int
    burst_limit: int
    penalty_duration: int  # seconds

class SecurityManager:
    """
    Comprehensive security manager untuk trading platform
    """
    
    def __init__(self, redis_client=None):
        self.logger = logging.getLogger(__name__)
        
        # Redis untuk rate limiting dan session management
        try:
            if redis_client:
                self.redis = redis_client
            else:
                self.redis = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
            # Test connection
            self.redis.ping()
        except Exception as e:
            self.logger.warning(f"Redis not available for security features: {e}")
            self.redis = None
        
        # Rate limiting configurations
        self.rate_limits = {
            'default': RateLimitConfig(60, 1000, 10000, 10, 300),
            'trading_signals': RateLimitConfig(30, 500, 2000, 5, 600),
            'data_quality': RateLimitConfig(120, 2000, 20000, 20, 180),
            'gpts_api': RateLimitConfig(100, 1500, 15000, 15, 300),
            'admin': RateLimitConfig(200, 5000, 50000, 50, 60)
        }
        
        # Security patterns untuk detection
        self.threat_patterns = {
            'sql_injection': [
                r"(\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b)",
                r"(\b(or|and)\s+\d+\s*=\s*\d+)",
                r"(\b(or|and)\s+\'\w+\'\s*=\s*\'\w+\')",
                r"(\-\-|\#|\/\*|\*\/)",
                r"(\bxp_cmdshell\b|\bsp_executesql\b)"
            ],
            'xss_injection': [
                r"(<script[^>]*>.*?</script>)",
                r"(javascript:)",
                r"(on\w+\s*=)",
                r"(<iframe[^>]*>)",
                r"(<object[^>]*>)"
            ],
            'command_injection': [
                r"(\b(ls|dir|cat|type|wget|curl|nc|netcat|ping|nslookup)\b)",
                r"(\||;|&|\$\(|\`)",
                r"(\.\.\/|\.\.\\\\)",
                r"(\/etc\/passwd|\/etc\/shadow|C:\\\\Windows)"
            ],
            'path_traversal': [
                r"(\.\.\/|\.\.\\\\)",
                r"(\%2e\%2e\%2f|\%2e\%2e\%5c)",
                r"(\.\.%2f|\.\.%5c)"
            ]
        }
        
        # Encryption setup
        self.encryption_key = self._get_or_create_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key)
        
        # IP whitelist/blacklist
        self.ip_whitelist = set()
        self.ip_blacklist = set()
        self.suspicious_ips = {}  # IP -> (count, last_seen)
        
        # Audit log storage
        self.security_events = []
        self.max_events = 10000
        
        self.logger.info("🔒 Security Manager initialized with comprehensive protection")
    
    def _get_or_create_encryption_key(self) -> bytes:
        """Generate atau load encryption key"""
        key_file = "logs/encryption.key"
        
        # Create directory if not exists
        os.makedirs(os.path.dirname(key_file), exist_ok=True)
        
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            # Generate new key
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            return key
    
    def rate_limit_check(self, 
                        identifier: str,
                        endpoint_category: str = 'default',
                        custom_limits: Optional[RateLimitConfig] = None) -> Tuple[bool, Dict[str, Any]]:
        """
        Check rate limiting untuk user/IP
        """
        if not self.redis:
            return True, {"message": "Rate limiting unavailable"}
        
        try:
            config = custom_limits or self.rate_limits.get(endpoint_category, self.rate_limits['default'])
            current_time = int(time.time())
            
            # Keys untuk different time windows
            minute_key = f"rate_limit:{identifier}:minute:{current_time // 60}"
            hour_key = f"rate_limit:{identifier}:hour:{current_time // 3600}"
            day_key = f"rate_limit:{identifier}:day:{current_time // 86400}"
            burst_key = f"rate_limit:{identifier}:burst"
            penalty_key = f"rate_limit:{identifier}:penalty"
            
            # Check if user is in penalty
            if self.redis.exists(penalty_key):
                penalty_remaining = self.redis.ttl(penalty_key)
                return False, {
                    "error": "Rate limit penalty active",
                    "penalty_remaining_seconds": penalty_remaining,
                    "retry_after": penalty_remaining
                }
            
            # Get current counters
            minute_count = int(self.redis.get(minute_key) or "0")
            hour_count = int(self.redis.get(hour_key) or "0")
            day_count = int(self.redis.get(day_key) or "0")
            burst_count = int(self.redis.get(burst_key) or "0")
            
            # Check limits
            if minute_count >= config.requests_per_minute:
                self._apply_penalty(identifier, config.penalty_duration)
                return False, {
                    "error": "Rate limit exceeded: too many requests per minute",
                    "limit": config.requests_per_minute,
                    "current": minute_count,
                    "reset_time": (current_time // 60 + 1) * 60
                }
            
            if hour_count >= config.requests_per_hour:
                self._apply_penalty(identifier, config.penalty_duration)
                return False, {
                    "error": "Rate limit exceeded: too many requests per hour",
                    "limit": config.requests_per_hour,
                    "current": hour_count,
                    "reset_time": (current_time // 3600 + 1) * 3600
                }
            
            if day_count >= config.requests_per_day:
                self._apply_penalty(identifier, config.penalty_duration * 6)
                return False, {
                    "error": "Rate limit exceeded: daily limit reached",
                    "limit": config.requests_per_day,
                    "current": day_count,
                    "reset_time": (current_time // 86400 + 1) * 86400
                }
            
            if burst_count >= config.burst_limit:
                return False, {
                    "error": "Rate limit exceeded: burst limit reached",
                    "limit": config.burst_limit,
                    "current": burst_count,
                    "retry_after": 60
                }
            
            # Increment counters
            pipe = self.redis.pipeline()
            pipe.incr(minute_key)
            pipe.expire(minute_key, 60)
            pipe.incr(hour_key)
            pipe.expire(hour_key, 3600)
            pipe.incr(day_key)
            pipe.expire(day_key, 86400)
            pipe.incr(burst_key)
            pipe.expire(burst_key, 10)  # 10 second burst window
            pipe.execute()
            
            return True, {
                "allowed": True,
                "remaining": {
                    "minute": config.requests_per_minute - minute_count - 1,
                    "hour": config.requests_per_hour - hour_count - 1,
                    "day": config.requests_per_day - day_count - 1
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error in rate limit check: {e}")
            return True, {"error": str(e)}
    
    def _apply_penalty(self, identifier: str, duration: int):
        """Apply penalty untuk rate limit violation"""
        if not self.redis:
            return
        
        penalty_key = f"rate_limit:{identifier}:penalty"
        self.redis.setex(penalty_key, duration, "1")
        
        # Log security event
        self._log_security_event(
            ThreatType.RATE_LIMIT_EXCEEDED,
            SecurityLevel.HIGH,
            identifier,
            "",
            "",
            {},
            True,
            f"Rate limit penalty applied for {duration} seconds"
        )
    
    def validate_input(self, 
                      data: Any, 
                      endpoint: str,
                      strict_mode: bool = False) -> Tuple[bool, List[str], Any]:
        """
        Comprehensive input validation dan sanitization
        """
        issues = []
        cleaned_data = data
        
        try:
            # Convert to string untuk pattern checking
            data_str = json.dumps(data) if isinstance(data, (dict, list)) else str(data)
            
            # Check untuk injection attacks
            for threat_type, patterns in self.threat_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, data_str, re.IGNORECASE):
                        issues.append(f"Potential {threat_type} detected: {pattern}")
                        
                        # Log security event
                        source_ip = request.remote_addr or "unknown" if request else "unknown"
                        user_agent = request.headers.get('User-Agent', '') if request else ""
                        self._log_security_event(
                            ThreatType.POTENTIAL_INJECTION,
                            SecurityLevel.CRITICAL,
                            source_ip,
                            user_agent,
                            endpoint,
                            {"data": data_str[:1000]},  # Limit log size
                            True,
                            f"Injection attempt: {threat_type}"
                        )
            
            # Validate specific data types
            if isinstance(data, dict):
                cleaned_data = self._sanitize_dict(data, strict_mode)
            elif isinstance(data, str):
                cleaned_data = self._sanitize_string(data, strict_mode)
            elif isinstance(data, list):
                cleaned_data = [self.validate_input(item, endpoint, strict_mode)[2] for item in data]
            
            # Additional validation untuk trading endpoints
            if 'trading' in endpoint or 'signal' in endpoint:
                validation_issues = self._validate_trading_data(data)
                issues.extend(validation_issues)
            
            is_valid = len(issues) == 0
            
            return is_valid, issues, cleaned_data
            
        except Exception as e:
            self.logger.error(f"Error in input validation: {e}")
            return False, [f"Validation error: {str(e)}"], data
    
    def _sanitize_dict(self, data: Dict[str, Any], strict_mode: bool) -> Dict[str, Any]:
        """Sanitize dictionary data"""
        sanitized = {}
        
        for key, value in data.items():
            # Sanitize key
            clean_key = self._sanitize_string(str(key), strict_mode)
            
            # Sanitize value
            if isinstance(value, str):
                clean_value = self._sanitize_string(value, strict_mode)
            elif isinstance(value, dict):
                clean_value = self._sanitize_dict(value, strict_mode)
            elif isinstance(value, list):
                clean_value = [self._sanitize_string(str(item), strict_mode) if isinstance(item, str) else item for item in value]
            else:
                clean_value = value
            
            sanitized[clean_key] = clean_value
        
        return sanitized
    
    def _sanitize_string(self, data: str, strict_mode: bool) -> str:
        """Sanitize string data"""
        if not isinstance(data, str):
            return data
        
        # Remove null bytes
        sanitized = data.replace('\x00', '')
        
        # HTML encode dangerous characters
        sanitized = (sanitized
                    .replace('<', '&lt;')
                    .replace('>', '&gt;')
                    .replace('"', '&quot;')
                    .replace("'", '&#x27;'))
        
        if strict_mode:
            # Remove special characters
            sanitized = re.sub(r'[^\w\s\-\.\@\:]', '', sanitized)
        
        return sanitized
    
    def _validate_trading_data(self, data: Any) -> List[str]:
        """Validate trading-specific data"""
        issues = []
        
        if isinstance(data, dict):
            # Validate symbol format
            if 'symbol' in data:
                symbol = data['symbol']
                if not re.match(r'^[A-Z]{2,10}[-/]?[A-Z]{2,10}$', str(symbol).upper()):
                    issues.append(f"Invalid symbol format: {symbol}")
            
            # Validate timeframe
            if 'timeframe' in data:
                timeframe = data['timeframe']
                valid_timeframes = ['1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '12h', '1d', '3d', '1w']
                if timeframe not in valid_timeframes:
                    issues.append(f"Invalid timeframe: {timeframe}")
            
            # Validate numeric values
            for field in ['price', 'volume', 'amount', 'quantity']:
                if field in data:
                    try:
                        value = float(data[field])
                        if value < 0:
                            issues.append(f"Negative value not allowed for {field}: {value}")
                        if value > 1e15:  # Extremely large value
                            issues.append(f"Value too large for {field}: {value}")
                    except (ValueError, TypeError):
                        issues.append(f"Invalid numeric value for {field}: {data[field]}")
        
        return issues
    
    def check_ip_security(self, ip_address: str) -> Tuple[bool, str]:
        """Check IP address security"""
        try:
            # Parse IP address
            ip = ipaddress.ip_address(ip_address)
            
            # Check blacklist
            if ip_address in self.ip_blacklist:
                return False, "IP address is blacklisted"
            
            # Check whitelist (if configured)
            if self.ip_whitelist and ip_address not in self.ip_whitelist:
                return False, "IP address not in whitelist"
            
            # Check for suspicious activity
            if ip_address in self.suspicious_ips:
                count, last_seen = self.suspicious_ips[ip_address]
                if count > 50 and time.time() - last_seen < 3600:  # 50 violations in 1 hour
                    return False, f"IP shows suspicious activity: {count} violations"
            
            # Check for private/local IPs in production
            if ip.is_private and os.getenv('ENVIRONMENT') == 'production':
                return False, "Private IP access not allowed in production"
            
            return True, "IP address allowed"
            
        except ValueError:
            return False, "Invalid IP address format"
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        try:
            return self.cipher_suite.encrypt(data.encode()).decode()
        except Exception as e:
            self.logger.error(f"Encryption error: {e}")
            return data
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        try:
            return self.cipher_suite.decrypt(encrypted_data.encode()).decode()
        except Exception as e:
            self.logger.error(f"Decryption error: {e}")
            return encrypted_data
    
    def _log_security_event(self, 
                           event_type: ThreatType,
                           severity: SecurityLevel,
                           source_ip: str,
                           user_agent: str,
                           endpoint: str,
                           payload: Dict[str, Any],
                           blocked: bool,
                           details: str):
        """Log security event"""
        event = SecurityEvent(
            timestamp=time.time(),
            event_type=event_type,
            severity=severity,
            source_ip=source_ip,
            user_agent=user_agent,
            endpoint=endpoint,
            payload=payload,
            blocked=blocked,
            details=details
        )
        
        # Add to events list
        self.security_events.append(event)
        
        # Limit list size
        if len(self.security_events) > self.max_events:
            self.security_events = self.security_events[-self.max_events//2:]
        
        # Log to file
        log_level = logging.WARNING if severity in [SecurityLevel.HIGH, SecurityLevel.CRITICAL] else logging.INFO
        self.logger.log(log_level, f"Security Event: {event_type.value} from {source_ip} - {details}")
        
        # Update suspicious IP tracking
        if source_ip != "unknown" and event_type in [ThreatType.POTENTIAL_INJECTION, ThreatType.RATE_LIMIT_EXCEEDED]:
            if source_ip in self.suspicious_ips:
                count, _ = self.suspicious_ips[source_ip]
                self.suspicious_ips[source_ip] = (count + 1, time.time())
            else:
                self.suspicious_ips[source_ip] = (1, time.time())
    
    def get_security_dashboard(self) -> Dict[str, Any]:
        """Get security dashboard data"""
        current_time = time.time()
        
        # Recent events (last 24 hours)
        recent_events = [
            event for event in self.security_events 
            if current_time - event.timestamp < 86400
        ]
        
        # Group by severity
        by_severity = {}
        for event in recent_events:
            severity = event.severity.value
            by_severity[severity] = by_severity.get(severity, 0) + 1
        
        # Group by type
        by_type = {}
        for event in recent_events:
            event_type = event.event_type.value
            by_type[event_type] = by_type.get(event_type, 0) + 1
        
        # Top suspicious IPs
        top_suspicious = sorted(
            self.suspicious_ips.items(),
            key=lambda x: x[1][0],
            reverse=True
        )[:10]
        
        # Rate limiting stats
        rate_limit_violations = len([
            event for event in recent_events 
            if event.event_type == ThreatType.RATE_LIMIT_EXCEEDED
        ])
        
        return {
            "summary": {
                "total_events_24h": len(recent_events),
                "blocked_attempts": len([e for e in recent_events if e.blocked]),
                "unique_ips": len(set(e.source_ip for e in recent_events)),
                "rate_limit_violations": rate_limit_violations
            },
            "by_severity": by_severity,
            "by_type": by_type,
            "top_suspicious_ips": [
                {"ip": ip, "violations": count, "last_seen": last_seen}
                for ip, (count, last_seen) in top_suspicious
            ],
            "recent_critical_events": [
                {
                    "timestamp": event.timestamp,
                    "type": event.event_type.value,
                    "source_ip": event.source_ip,
                    "details": event.details
                }
                for event in recent_events[-10:]
                if event.severity == SecurityLevel.CRITICAL
            ]
        }
    
    def add_ip_to_blacklist(self, ip_address: str):
        """Add IP to blacklist"""
        self.ip_blacklist.add(ip_address)
        self.logger.info(f"IP {ip_address} added to blacklist")
    
    def add_ip_to_whitelist(self, ip_address: str):
        """Add IP to whitelist"""
        self.ip_whitelist.add(ip_address)
        self.logger.info(f"IP {ip_address} added to whitelist")

# Global instance
security_manager = SecurityManager()

def get_security_manager():
    """Get global security manager instance"""
    return security_manager

# Decorator untuk rate limiting
def rate_limit(category: str = 'default', custom_limits: Optional[RateLimitConfig] = None):
    """Decorator untuk rate limiting"""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # Get identifier (IP address atau user ID)
            identifier = request.remote_addr or "unknown"
            if hasattr(g, 'user_id'):
                identifier = f"user:{g.user_id}"
            
            # Check rate limit
            allowed, info = security_manager.rate_limit_check(identifier, category, custom_limits)
            
            if not allowed:
                return jsonify(info), 429
            
            # Add rate limit info to response headers
            response = f(*args, **kwargs)
            if hasattr(response, 'headers') and 'remaining' in info:
                response.headers['X-RateLimit-Remaining-Minute'] = str(info['remaining']['minute'])
                response.headers['X-RateLimit-Remaining-Hour'] = str(info['remaining']['hour'])
                response.headers['X-RateLimit-Remaining-Day'] = str(info['remaining']['day'])
            
            return response
        return wrapper
    return decorator

# Decorator untuk input validation
def validate_input_security(strict_mode: bool = False):
    """Decorator untuk input validation"""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            endpoint = request.endpoint or f.__name__
            
            # Validate JSON data
            if request.is_json:
                data = request.get_json()
                is_valid, issues, cleaned_data = security_manager.validate_input(data, endpoint, strict_mode)
                
                if not is_valid:
                    return jsonify({
                        "error": "Input validation failed",
                        "issues": issues
                    }), 400
                
                # Replace request data with cleaned data
                request._cached_json = (cleaned_data, cleaned_data)
            
            # Validate query parameters
            for key, value in request.args.items():
                is_valid, issues, cleaned_value = security_manager.validate_input(value, endpoint, strict_mode)
                if not is_valid:
                    return jsonify({
                        "error": f"Invalid query parameter: {key}",
                        "issues": issues
                    }), 400
            
            return f(*args, **kwargs)
        return wrapper
    return decorator

logger.info("🔒 Security Manager module initialized")