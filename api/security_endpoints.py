#!/usr/bin/env python3
"""
Security Enhancement API Endpoints
Rate limiting, input validation, audit logging, dan security monitoring
"""

from flask import Blueprint, jsonify, request, g
import logging
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from functools import wraps

# Import security components
from core.security_manager import get_security_manager, rate_limit, validate_input_security, SecurityLevel, ThreatType
from core.audit_logger import get_audit_logger, AuditEventType, AuditSeverity

logger = logging.getLogger(__name__)

# Create blueprint
security_bp = Blueprint('security', __name__, url_prefix='/api/security')

# Initialize components
security_manager = get_security_manager()
audit_logger = get_audit_logger()

def log_api_call(f):
    """Decorator untuk audit logging semua API calls"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        success = True
        error_message = None
        response_data = {}
        
        try:
            # Execute function
            result = f(*args, **kwargs)
            
            # Extract response data
            if hasattr(result, 'get_json'):
                try:
                    response_data = result.get_json() or {}
                except:
                    response_data = {"status": "response_not_json"}
            elif isinstance(result, tuple) and len(result) >= 1:
                response_data = {"status_code": result[1] if len(result) > 1 else 200}
                success = result[1] < 400 if len(result) > 1 else True
            
            return result
            
        except Exception as e:
            success = False
            error_message = str(e)
            response_data = {"error": error_message}
            raise
            
        finally:
            execution_time_ms = (time.time() - start_time) * 1000
            
            # Log API call
            audit_logger.log_api_call(
                endpoint=request.endpoint or f.__name__,
                method=request.method,
                user_id=getattr(g, 'user_id', None),
                source_ip=request.remote_addr or "unknown",
                user_agent=request.headers.get('User-Agent', ''),
                request_data=request.get_json() if request.is_json else dict(request.args),
                response_data=response_data,
                execution_time_ms=execution_time_ms,
                success=success,
                error_message=error_message
            )
    
    return wrapper

@security_bp.route('/status', methods=['GET'])
@rate_limit('admin')
@log_api_call
def get_security_status():
    """
    Security system status overview
    """
    try:
        # Get security dashboard
        dashboard = security_manager.get_security_dashboard()
        
        # Get audit summary
        audit_summary = audit_logger.get_audit_summary(days=1)
        
        # Security health score
        total_events = dashboard['summary']['total_events_24h']
        blocked_attempts = dashboard['summary']['blocked_attempts']
        
        if total_events > 0:
            block_rate = (blocked_attempts / total_events) * 100
            if block_rate > 50:
                security_health = "CRITICAL"
            elif block_rate > 20:
                security_health = "WARNING"
            elif block_rate > 5:
                security_health = "CAUTION"
            else:
                security_health = "HEALTHY"
        else:
            security_health = "HEALTHY"
        
        return jsonify({
            "status": "active",
            "timestamp": time.time(),
            "security_health": security_health,
            "dashboard": dashboard,
            "audit_summary": {
                "total_events": audit_summary.get('total_events', 0),
                "error_rate": audit_summary.get('error_rate_percentage', 0),
                "unique_users": audit_summary.get('unique_users', 0),
                "unique_ips": audit_summary.get('unique_ips', 0)
            },
            "features": {
                "rate_limiting": True,
                "input_validation": True,
                "audit_logging": True,
                "ip_filtering": True,
                "encryption": True
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting security status: {e}")
        return jsonify({"error": str(e)}), 500

@security_bp.route('/rate-limits/check', methods=['POST'])
@validate_input_security(strict_mode=True)
@log_api_call
def check_rate_limits():
    """
    Check rate limits untuk specific identifier
    """
    try:
        data = request.get_json()
        identifier = data.get('identifier', request.remote_addr)
        category = data.get('category', 'default')
        
        # Check rate limit
        allowed, info = security_manager.rate_limit_check(identifier, category)
        
        return jsonify({
            "identifier": identifier,
            "category": category,
            "allowed": allowed,
            "details": info,
            "timestamp": time.time()
        })
        
    except Exception as e:
        logger.error(f"Error checking rate limits: {e}")
        return jsonify({"error": str(e)}), 500

@security_bp.route('/validate-input', methods=['POST'])
@rate_limit('admin')
@log_api_call
def validate_input_endpoint():
    """
    Test input validation
    """
    try:
        data = request.get_json()
        test_data = data.get('data')
        endpoint = data.get('endpoint', 'test')
        strict_mode = data.get('strict_mode', False)
        
        # Validate input
        is_valid, issues, cleaned_data = security_manager.validate_input(test_data, endpoint, strict_mode)
        
        return jsonify({
            "input_data": test_data,
            "is_valid": is_valid,
            "issues": issues,
            "cleaned_data": cleaned_data,
            "validation_config": {
                "endpoint": endpoint,
                "strict_mode": strict_mode
            },
            "timestamp": time.time()
        })
        
    except Exception as e:
        logger.error(f"Error validating input: {e}")
        return jsonify({"error": str(e)}), 500

@security_bp.route('/ip-management', methods=['GET'])
@rate_limit('admin')
@log_api_call
def get_ip_management():
    """
    Get IP whitelist/blacklist status
    """
    try:
        return jsonify({
            "whitelist": list(security_manager.ip_whitelist),
            "blacklist": list(security_manager.ip_blacklist),
            "suspicious_ips": [
                {
                    "ip": ip,
                    "violations": count,
                    "last_seen": last_seen,
                    "last_seen_formatted": datetime.fromtimestamp(last_seen).isoformat()
                }
                for ip, (count, last_seen) in security_manager.suspicious_ips.items()
            ],
            "timestamp": time.time()
        })
        
    except Exception as e:
        logger.error(f"Error getting IP management data: {e}")
        return jsonify({"error": str(e)}), 500

@security_bp.route('/ip-management/blacklist', methods=['POST'])
@rate_limit('admin')
@validate_input_security(strict_mode=True)
@log_api_call
def add_ip_to_blacklist():
    """
    Add IP to blacklist
    """
    try:
        data = request.get_json()
        ip_address = data.get('ip_address')
        
        if not ip_address:
            return jsonify({"error": "IP address required"}), 400
        
        # Validate IP format
        import ipaddress
        try:
            ipaddress.ip_address(ip_address)
        except ValueError:
            return jsonify({"error": "Invalid IP address format"}), 400
        
        # Add to blacklist
        security_manager.add_ip_to_blacklist(ip_address)
        
        # Log security event
        audit_logger.log_event(
            event_type=AuditEventType.SECURITY_EVENT,
            severity=AuditSeverity.WARNING,
            endpoint='/security/ip-management/blacklist',
            method='POST',
            user_id=getattr(g, 'user_id', None),
            source_ip=request.remote_addr or "unknown",
            additional_context={'blacklisted_ip': ip_address}
        )
        
        return jsonify({
            "message": f"IP {ip_address} added to blacklist",
            "ip_address": ip_address,
            "timestamp": time.time()
        })
        
    except Exception as e:
        logger.error(f"Error adding IP to blacklist: {e}")
        return jsonify({"error": str(e)}), 500

@security_bp.route('/ip-management/whitelist', methods=['POST'])
@rate_limit('admin')
@validate_input_security(strict_mode=True)
@log_api_call
def add_ip_to_whitelist():
    """
    Add IP to whitelist
    """
    try:
        data = request.get_json()
        ip_address = data.get('ip_address')
        
        if not ip_address:
            return jsonify({"error": "IP address required"}), 400
        
        # Validate IP format
        import ipaddress
        try:
            ipaddress.ip_address(ip_address)
        except ValueError:
            return jsonify({"error": "Invalid IP address format"}), 400
        
        # Add to whitelist
        security_manager.add_ip_to_whitelist(ip_address)
        
        # Log security event
        audit_logger.log_event(
            event_type=AuditEventType.SECURITY_EVENT,
            severity=AuditSeverity.INFO,
            endpoint='/security/ip-management/whitelist',
            method='POST',
            user_id=getattr(g, 'user_id', None),
            source_ip=request.remote_addr or "unknown",
            additional_context={'whitelisted_ip': ip_address}
        )
        
        return jsonify({
            "message": f"IP {ip_address} added to whitelist",
            "ip_address": ip_address,
            "timestamp": time.time()
        })
        
    except Exception as e:
        logger.error(f"Error adding IP to whitelist: {e}")
        return jsonify({"error": str(e)}), 500

@security_bp.route('/audit/events', methods=['GET'])
@rate_limit('admin')
@log_api_call
def get_audit_events():
    """
    Get audit events dengan filtering
    """
    try:
        # Parse query parameters
        hours = int(request.args.get('hours', 24))
        event_type = request.args.get('event_type')
        user_id = request.args.get('user_id')
        source_ip = request.args.get('source_ip')
        endpoint = request.args.get('endpoint')
        limit = int(request.args.get('limit', 100))
        
        # Calculate time range
        end_time = time.time()
        start_time = end_time - (hours * 3600)
        
        # Convert event_type string to enum
        event_type_enum = None
        if event_type:
            try:
                event_type_enum = AuditEventType(event_type)
            except ValueError:
                return jsonify({"error": f"Invalid event type: {event_type}"}), 400
        
        # Get events
        events = audit_logger.get_events(
            start_time=start_time,
            end_time=end_time,
            event_type=event_type_enum,
            user_id=user_id,
            source_ip=source_ip,
            endpoint=endpoint,
            limit=limit
        )
        
        return jsonify({
            "events": events,
            "filters": {
                "hours": hours,
                "event_type": event_type,
                "user_id": user_id,
                "source_ip": source_ip,
                "endpoint": endpoint,
                "limit": limit
            },
            "total_events": len(events),
            "timestamp": time.time()
        })
        
    except Exception as e:
        logger.error(f"Error getting audit events: {e}")
        return jsonify({"error": str(e)}), 500

@security_bp.route('/audit/summary', methods=['GET'])
@rate_limit('admin')
@log_api_call
def get_audit_summary():
    """
    Get audit summary untuk dashboard
    """
    try:
        days = int(request.args.get('days', 7))
        
        # Get audit summary
        summary = audit_logger.get_audit_summary(days)
        
        return jsonify({
            "summary": summary,
            "period_days": days,
            "timestamp": time.time()
        })
        
    except Exception as e:
        logger.error(f"Error getting audit summary: {e}")
        return jsonify({"error": str(e)}), 500

@security_bp.route('/audit/verify/<int:event_id>', methods=['GET'])
@rate_limit('admin')
@log_api_call
def verify_audit_event(event_id):
    """
    Verify integrity audit event
    """
    try:
        # Verify event integrity
        is_valid, message = audit_logger.verify_event_integrity(event_id)
        
        return jsonify({
            "event_id": event_id,
            "is_valid": is_valid,
            "message": message,
            "timestamp": time.time()
        })
        
    except Exception as e:
        logger.error(f"Error verifying audit event: {e}")
        return jsonify({"error": str(e)}), 500

@security_bp.route('/encryption/test', methods=['POST'])
@rate_limit('admin')
@validate_input_security(strict_mode=True)
@log_api_call
def test_encryption():
    """
    Test encryption/decryption functionality
    """
    try:
        data = request.get_json()
        test_data = data.get('data', 'test encryption data')
        
        # Encrypt data
        encrypted = security_manager.encrypt_sensitive_data(test_data)
        
        # Decrypt data
        decrypted = security_manager.decrypt_sensitive_data(encrypted)
        
        return jsonify({
            "original_data": test_data,
            "encrypted_data": encrypted,
            "decrypted_data": decrypted,
            "encryption_successful": test_data == decrypted,
            "timestamp": time.time()
        })
        
    except Exception as e:
        logger.error(f"Error testing encryption: {e}")
        return jsonify({"error": str(e)}), 500

@security_bp.route('/dashboard', methods=['GET'])
@rate_limit('admin')
@log_api_call
def get_security_dashboard():
    """
    Comprehensive security dashboard
    """
    try:
        # Get security dashboard
        security_dashboard = security_manager.get_security_dashboard()
        
        # Get audit summary
        audit_summary = audit_logger.get_audit_summary(days=7)
        
        # Rate limiting stats (example data structure)
        if security_manager.redis:
            try:
                # Get current minute key untuk sample rate limiting info
                current_minute = int(time.time()) // 60
                sample_key = f"rate_limit:*:minute:{current_minute}"
                rate_limit_keys = security_manager.redis.keys(sample_key) or []
                active_rate_limits = len(list(rate_limit_keys))
            except:
                active_rate_limits = 0
        else:
            active_rate_limits = 0
        
        # Security score calculation
        recent_events = security_dashboard['summary']['total_events_24h']
        blocked_attempts = security_dashboard['summary']['blocked_attempts']
        
        if recent_events > 0:
            threat_ratio = blocked_attempts / recent_events
            base_score = 100
            
            # Deduct points berdasarkan threats
            if threat_ratio > 0.5:
                base_score -= 50
            elif threat_ratio > 0.2:
                base_score -= 30
            elif threat_ratio > 0.1:
                base_score -= 15
            elif threat_ratio > 0.05:
                base_score -= 5
            
            # Deduct untuk error rate
            error_rate = audit_summary.get('error_rate_percentage', 0)
            if error_rate > 10:
                base_score -= 20
            elif error_rate > 5:
                base_score -= 10
            
            security_score = max(0, min(100, base_score))
        else:
            security_score = 100
        
        return jsonify({
            "timestamp": time.time(),
            "security_score": security_score,
            "security_dashboard": security_dashboard,
            "audit_summary": audit_summary,
            "system_status": {
                "rate_limiting_active": security_manager.redis is not None,
                "active_rate_limits": active_rate_limits,
                "encryption_enabled": True,
                "audit_logging_enabled": True,
                "ip_filtering_enabled": len(security_manager.ip_blacklist) > 0 or len(security_manager.ip_whitelist) > 0
            },
            "recommendations": [
                "✅ Security monitoring active" if security_score > 80 else "⚠️ Security issues detected",
                "✅ Rate limiting operational" if security_manager.redis else "⚠️ Rate limiting disabled (Redis unavailable)",
                "✅ Audit logging active",
                "✅ Encryption enabled",
                f"Monitor {len(security_dashboard.get('top_suspicious_ips', []))} suspicious IPs" if security_dashboard.get('top_suspicious_ips') else "No suspicious IP activity"
            ]
        })
        
    except Exception as e:
        logger.error(f"Error generating security dashboard: {e}")
        return jsonify({"error": str(e)}), 500

@security_bp.route('/health', methods=['GET'])
@log_api_call
def security_health_check():
    """
    Security system health check
    """
    try:
        health_checks = {
            "security_manager": False,
            "audit_logger": False,
            "rate_limiting": False,
            "encryption": False,
            "input_validation": False
        }
        
        # Test security manager
        try:
            security_manager.get_security_dashboard()
            health_checks["security_manager"] = True
        except:
            pass
        
        # Test audit logger
        try:
            audit_logger.get_audit_summary(1)
            health_checks["audit_logger"] = True
        except:
            pass
        
        # Test rate limiting
        try:
            if security_manager.redis:
                security_manager.redis.ping()
                health_checks["rate_limiting"] = True
        except:
            pass
        
        # Test encryption
        try:
            test_data = "test"
            encrypted = security_manager.encrypt_sensitive_data(test_data)
            decrypted = security_manager.decrypt_sensitive_data(encrypted)
            health_checks["encryption"] = (test_data == decrypted)
        except:
            pass
        
        # Test input validation
        try:
            is_valid, _, _ = security_manager.validate_input("test", "test")
            health_checks["input_validation"] = True
        except:
            pass
        
        # Calculate health score
        passed_checks = sum(health_checks.values())
        total_checks = len(health_checks)
        health_score = (passed_checks / total_checks) * 100
        
        status = "healthy" if health_score >= 80 else "degraded" if health_score >= 60 else "critical"
        
        return jsonify({
            "status": status,
            "health_score": round(health_score, 1),
            "checks_passed": passed_checks,
            "total_checks": total_checks,
            "component_health": health_checks,
            "timestamp": time.time()
        })
        
    except Exception as e:
        logger.error(f"Error in security health check: {e}")
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": time.time()
        }), 500

# Register blueprint (akan dilakukan di routes.py)
logger.info("🔒 Security Enhancement API endpoints initialized")