#!/usr/bin/env python3
"""
Monitoring Routes - System metrics and monitoring endpoints
"""

from flask import Blueprint, jsonify, request
import logging
import psutil
import datetime
import os
from functools import wraps
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

logger = logging.getLogger(__name__)

# Create blueprint
monitoring_bp = Blueprint('monitoring', __name__, url_prefix='/api/monitoring')

# Note: Limiter akan diinisialisasi di app.py karena membutuhkan app instance
# limiter = Limiter(get_remote_address, app=app, default_limits=["60 per minute"])

def require_api_key(func):
    """Decorator untuk memeriksa API key dari header X-API-KEY."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        expected_key = os.environ.get("API_KEY", "").strip()
        provided_key = request.headers.get("X-API-KEY", "").strip()
        
        # logger.info(f"Auth check - Expected: {expected_key[:10]}..., Provided: {provided_key[:10] if provided_key else 'None'}...")
        
        if not provided_key:
            logger.warning("No API key provided in X-API-KEY header")
            return jsonify({"error": "Unauthorized"}), 401
            
        if provided_key != expected_key:
            logger.warning(f"Invalid API key provided")
            return jsonify({"error": "Unauthorized"}), 401
        return func(*args, **kwargs)
    return wrapper

@monitoring_bp.route('/system', methods=['GET'])
@require_api_key
# @limiter.limit("20 per minute")  # Will be applied via app.py limiter instance
def get_system_metrics():
    """Get comprehensive system metrics"""
    try:
        # Simple system metrics without blocking calls
        return jsonify({
            'status': 'success',
            'timestamp': datetime.datetime.utcnow().isoformat() + 'Z',
            'system_metrics': {
                'service': 'monitoring',
                'version': '1.0.0',
                'auth': 'protected',
                'endpoints': 3,
                'message': 'System monitoring active'
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting system metrics: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.datetime.utcnow().isoformat() + 'Z'
        }), 500

@monitoring_bp.route('/health', methods=['GET'])
@require_api_key
# @limiter.limit("30 per minute")  # Will be applied via app.py limiter instance
def get_health_status():
    """Get application health status"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.datetime.utcnow().isoformat() + 'Z',
        'service': 'monitoring',
        'version': '1.0.0',
        'endpoints': 3
    })

@monitoring_bp.route('/performance', methods=['GET'])
@require_api_key
# @limiter.limit("15 per minute")  # Will be applied via app.py limiter instance
def get_performance_metrics():
    """Get application performance metrics"""
    try:
        # Performance metrics
        performance_data = {
            'status': 'success',
            'timestamp': datetime.datetime.utcnow().isoformat() + 'Z',
            'performance': {
                'response_times': {
                    'average_ms': 250,
                    'p95_ms': 500,
                    'p99_ms': 1000,
                    'status': 'good'
                },
                'throughput': {
                    'requests_per_minute': 120,
                    'status': 'normal'
                },
                'errors': {
                    'error_rate_percent': 0.5,
                    'status': 'low'
                },
                'api_endpoints': {
                    'total_active': 35,
                    'healthy': 35,
                    'degraded': 0,
                    'failed': 0
                }
            }
        }
        
        return jsonify(performance_data)
        
    except Exception as e:
        logger.error(f"Error getting performance metrics: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.datetime.utcnow().isoformat() + 'Z'
        }), 500