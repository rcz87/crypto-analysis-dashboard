#!/usr/bin/env python3
"""
Performance Optimization API Endpoints
Cache management, monitoring, metrics, dan optimization controls
"""

from flask import Blueprint, jsonify, request, g
import logging
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from functools import wraps

# Import performance components
from core.performance_optimizer import get_performance_optimizer, cache_response
from core.audit_logger import get_audit_logger, AuditEventType, AuditSeverity

logger = logging.getLogger(__name__)

# Create blueprint
performance_bp = Blueprint('performance_optimization', __name__, url_prefix='/api/performance')

# Initialize components
performance_optimizer = get_performance_optimizer()
audit_logger = get_audit_logger()

def monitor_performance(f):
    """Decorator untuk monitoring performance semua endpoints"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        success = True
        error_message = None
        
        try:
            result = f(*args, **kwargs)
            return result
            
        except Exception as e:
            success = False
            error_message = str(e)
            raise
            
        finally:
            execution_time_ms = (time.time() - start_time) * 1000
            
            # Record performance metrics
            performance_optimizer.monitor.record_request(
                f.__name__, 
                execution_time_ms, 
                success
            )
            
            # Log untuk slow requests (>1 second)
            if execution_time_ms > 1000:
                audit_logger.log_event(
                    event_type=AuditEventType.SYSTEM_EVENT,
                    severity=AuditSeverity.WARNING,
                    endpoint=request.endpoint or f.__name__,
                    method=request.method,
                    user_id=getattr(g, 'user_id', None),
                    source_ip=request.remote_addr or "unknown",
                    execution_time_ms=execution_time_ms,
                    success=success,
                    error_message=error_message,
                    additional_context={'performance_issue': 'slow_response'}
                )
    
    return wrapper

@performance_bp.route('/status', methods=['GET'])
@monitor_performance
def get_performance_status():
    """
    Comprehensive performance status overview
    """
    try:
        status = performance_optimizer.get_comprehensive_status()
        
        return jsonify({
            "status": "active",
            "performance_health": "healthy" if status['performance_summary'].get('health_status') == 'healthy' else "degraded",
            "optimization_status": status,
            "timestamp": time.time()
        })
        
    except Exception as e:
        logger.error(f"Error getting performance status: {e}")
        return jsonify({"error": str(e)}), 500

@performance_bp.route('/cache/stats', methods=['GET'])
@monitor_performance
def get_cache_stats():
    """
    Cache performance statistics
    """
    try:
        stats = performance_optimizer.cache.get_stats()
        
        return jsonify({
            "cache_statistics": stats,
            "recommendations": [
                "✅ Cache operational" if stats['redis_available'] else "⚠️ Redis unavailable - using local cache",
                f"Hit rate: {stats['hit_rate_percent']:.1f}%" + (" (excellent)" if stats['hit_rate_percent'] > 80 else " (needs improvement)" if stats['hit_rate_percent'] < 50 else " (good)"),
                f"Local cache: {stats['local_cache_entries']} entries",
                f"Cache types available: {len(stats['cache_types'])}"
            ],
            "timestamp": time.time()
        })
        
    except Exception as e:
        logger.error(f"Error getting cache stats: {e}")
        return jsonify({"error": str(e)}), 500

@performance_bp.route('/cache/clear', methods=['POST'])
@monitor_performance
def clear_cache():
    """
    Clear cache untuk specific type atau all
    """
    try:
        data = request.get_json() if request.is_json else {}
        cache_type = data.get('cache_type')
        
        if cache_type:
            success = performance_optimizer.cache.clear_type(cache_type)
            message = f"Cache cleared for type: {cache_type}"
        else:
            # Clear all cache types
            cache_types = performance_optimizer.cache.cache_configs.keys()
            success = True
            for ct in cache_types:
                if not performance_optimizer.cache.clear_type(ct):
                    success = False
            message = "All cache types cleared"
        
        # Log cache clear event
        audit_logger.log_event(
            event_type=AuditEventType.SYSTEM_EVENT,
            severity=AuditSeverity.INFO,
            endpoint='/performance/cache/clear',
            method='POST',
            user_id=getattr(g, 'user_id', None),
            source_ip=request.remote_addr or "unknown",
            additional_context={'cache_type': cache_type or 'all'}
        )
        
        return jsonify({
            "success": success,
            "message": message,
            "cache_type": cache_type or "all",
            "timestamp": time.time()
        })
        
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        return jsonify({"error": str(e)}), 500

@performance_bp.route('/cache/set', methods=['POST'])
@monitor_performance
def set_cache_data():
    """
    Manually set cache data (untuk testing)
    """
    try:
        data = request.get_json()
        cache_type = data.get('cache_type', 'api_responses')
        key = data.get('key')
        value = data.get('value')
        ttl = data.get('ttl')
        
        if not key or value is None:
            return jsonify({"error": "Key and value are required"}), 400
        
        success = performance_optimizer.cache.set(cache_type, key, value, ttl)
        
        return jsonify({
            "success": success,
            "message": f"Cache data set for key: {key}",
            "cache_type": cache_type,
            "ttl": ttl,
            "timestamp": time.time()
        })
        
    except Exception as e:
        logger.error(f"Error setting cache data: {e}")
        return jsonify({"error": str(e)}), 500

@performance_bp.route('/metrics/summary', methods=['GET'])
@monitor_performance
def get_metrics_summary():
    """
    Performance metrics summary
    """
    try:
        minutes = int(request.args.get('minutes', 5))
        summary = performance_optimizer.monitor.get_performance_summary(minutes)
        
        return jsonify({
            "metrics_summary": summary,
            "timestamp": time.time()
        })
        
    except Exception as e:
        logger.error(f"Error getting metrics summary: {e}")
        return jsonify({"error": str(e)}), 500

@performance_bp.route('/metrics/endpoints', methods=['GET'])
@monitor_performance
def get_endpoint_metrics():
    """
    Detailed endpoint performance metrics
    """
    try:
        # Get endpoint metrics dari performance monitor
        endpoint_metrics = {}
        for endpoint, metrics_list in performance_optimizer.monitor.endpoint_metrics.items():
            if metrics_list:
                # Calculate statistics untuk each endpoint
                recent_metrics = metrics_list[-100:]  # Last 100 requests
                
                total_requests = len(recent_metrics)
                successful_requests = sum(1 for m in recent_metrics if m['success'])
                
                response_times = [m['response_time_ms'] for m in recent_metrics]
                avg_response_time = sum(response_times) / len(response_times)
                min_response_time = min(response_times)
                max_response_time = max(response_times)
                
                # Calculate percentiles
                sorted_times = sorted(response_times)
                p50 = sorted_times[len(sorted_times) // 2]
                p95 = sorted_times[int(len(sorted_times) * 0.95)]
                p99 = sorted_times[int(len(sorted_times) * 0.99)]
                
                endpoint_metrics[endpoint] = {
                    'total_requests': total_requests,
                    'success_rate_percent': round((successful_requests / total_requests) * 100, 2),
                    'avg_response_time_ms': round(avg_response_time, 2),
                    'min_response_time_ms': round(min_response_time, 2),
                    'max_response_time_ms': round(max_response_time, 2),
                    'p50_response_time_ms': round(p50, 2),
                    'p95_response_time_ms': round(p95, 2),
                    'p99_response_time_ms': round(p99, 2),
                    'error_rate_percent': round(((total_requests - successful_requests) / total_requests) * 100, 2)
                }
        
        return jsonify({
            "endpoint_metrics": endpoint_metrics,
            "total_endpoints": len(endpoint_metrics),
            "timestamp": time.time()
        })
        
    except Exception as e:
        logger.error(f"Error getting endpoint metrics: {e}")
        return jsonify({"error": str(e)}), 500

@performance_bp.route('/optimize/response', methods=['POST'])
@monitor_performance
def optimize_response_test():
    """
    Test response optimization dengan sample data
    """
    try:
        data = request.get_json() if request.is_json else {}
        sample_data = data.get('data', list(range(1000)))  # Default large dataset
        
        # Apply response optimization
        optimized = performance_optimizer.response_optimizer.optimize_response(
            sample_data, 
            dict(request.args)
        )
        
        return jsonify({
            "original_size": len(sample_data) if isinstance(sample_data, list) else 1,
            "optimized_response": optimized,
            "optimization_applied": 'pagination' in optimized or 'data' in optimized,
            "timestamp": time.time()
        })
        
    except Exception as e:
        logger.error(f"Error testing response optimization: {e}")
        return jsonify({"error": str(e)}), 500

@performance_bp.route('/system/resources', methods=['GET'])
@monitor_performance
def get_system_resources():
    """
    System resource utilization
    """
    try:
        import psutil
        
        # Memory information
        memory = psutil.virtual_memory()
        
        # CPU information
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        
        # Disk information
        disk = psutil.disk_usage('/')
        
        # Process information
        process = psutil.Process()
        process_memory = process.memory_info()
        
        return jsonify({
            "system_resources": {
                "memory": {
                    "total_mb": round(memory.total / 1024 / 1024, 2),
                    "used_mb": round(memory.used / 1024 / 1024, 2),
                    "available_mb": round(memory.available / 1024 / 1024, 2),
                    "percent_used": memory.percent
                },
                "cpu": {
                    "percent_used": cpu_percent,
                    "cpu_count": cpu_count
                },
                "disk": {
                    "total_gb": round(disk.total / 1024 / 1024 / 1024, 2),
                    "used_gb": round(disk.used / 1024 / 1024 / 1024, 2),
                    "free_gb": round(disk.free / 1024 / 1024 / 1024, 2),
                    "percent_used": round((disk.used / disk.total) * 100, 2)
                },
                "process": {
                    "memory_rss_mb": round(process_memory.rss / 1024 / 1024, 2),
                    "memory_vms_mb": round(process_memory.vms / 1024 / 1024, 2)
                }
            },
            "resource_alerts": [
                "⚠️ High memory usage" if memory.percent > 80 else "✅ Memory usage normal",
                "⚠️ High CPU usage" if cpu_percent > 80 else "✅ CPU usage normal",
                "⚠️ Low disk space" if (disk.used / disk.total) * 100 > 90 else "✅ Disk space sufficient"
            ],
            "timestamp": time.time()
        })
        
    except Exception as e:
        logger.error(f"Error getting system resources: {e}")
        return jsonify({"error": str(e)}), 500

@performance_bp.route('/health', methods=['GET'])
@cache_response('api_responses', ttl=30)  # Cache untuk 30 seconds
@monitor_performance
def performance_health_check():
    """
    Performance system health check
    """
    try:
        health_checks = {
            "cache_system": False,
            "async_processor": False,
            "response_optimizer": False,
            "performance_monitor": False,
            "system_resources": False
        }
        
        issues = []
        
        # Test cache system
        try:
            test_key = "health_check_test"
            performance_optimizer.cache.set('api_responses', test_key, {'test': True}, 60)
            result = performance_optimizer.cache.get('api_responses', test_key)
            if result and result.get('test'):
                health_checks["cache_system"] = True
            else:
                issues.append("Cache system not responding correctly")
        except Exception as e:
            issues.append(f"Cache system error: {str(e)}")
        
        # Test async processor
        try:
            task_id = performance_optimizer.task_processor.submit_task(
                "health_check", 
                lambda: {"status": "ok"}
            )
            if task_id:
                health_checks["async_processor"] = True
            else:
                issues.append("Async processor not accepting tasks")
        except Exception as e:
            issues.append(f"Async processor error: {str(e)}")
        
        # Test response optimizer
        try:
            test_data = [1, 2, 3, 4, 5]
            optimized = performance_optimizer.response_optimizer.optimize_response(test_data, {})
            if 'data' in optimized:
                health_checks["response_optimizer"] = True
            else:
                issues.append("Response optimizer not working correctly")
        except Exception as e:
            issues.append(f"Response optimizer error: {str(e)}")
        
        # Test performance monitor
        try:
            summary = performance_optimizer.monitor.get_performance_summary(1)
            if 'total_requests' in summary:
                health_checks["performance_monitor"] = True
            else:
                issues.append("Performance monitor not collecting data")
        except Exception as e:
            issues.append(f"Performance monitor error: {str(e)}")
        
        # Test system resources
        try:
            import psutil
            cpu = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            if cpu >= 0 and memory.total > 0:
                health_checks["system_resources"] = True
            else:
                issues.append("System resource monitoring unavailable")
        except Exception as e:
            issues.append(f"System resource error: {str(e)}")
        
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
            "issues": issues,
            "recommendations": [
                "✅ All performance systems operational" if not issues else f"⚠️ {len(issues)} issue(s) detected",
                "Performance optimization active",
                "Monitoring and caching functional" if health_checks["cache_system"] and health_checks["performance_monitor"] else "Check cache and monitoring systems"
            ],
            "timestamp": time.time()
        })
        
    except Exception as e:
        logger.error(f"Error in performance health check: {e}")
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": time.time()
        }), 500

@performance_bp.route('/dashboard', methods=['GET'])
@cache_response('api_responses', ttl=60)  # Cache untuk 1 minute
@monitor_performance
def get_performance_dashboard():
    """
    Comprehensive performance dashboard
    """
    try:
        # Get all performance data
        status = performance_optimizer.get_comprehensive_status()
        cache_stats = performance_optimizer.cache.get_stats()
        metrics_summary = performance_optimizer.monitor.get_performance_summary(15)  # Last 15 minutes
        
        # Calculate performance score
        base_score = 100
        
        # Deduct untuk poor cache hit rate
        if cache_stats['hit_rate_percent'] < 50:
            base_score -= 20
        elif cache_stats['hit_rate_percent'] < 70:
            base_score -= 10
        
        # Deduct untuk slow responses
        if metrics_summary.get('avg_response_time_ms', 0) > 2000:
            base_score -= 30
        elif metrics_summary.get('avg_response_time_ms', 0) > 1000:
            base_score -= 15
        
        # Deduct untuk high error rate
        error_rate = metrics_summary.get('error_rate_percent', 0)
        if error_rate > 5:
            base_score -= 25
        elif error_rate > 2:
            base_score -= 10
        
        # Deduct untuk high resource usage
        memory_percent = status['system_resources']['memory_percent']
        cpu_percent = status['system_resources']['cpu_percent']
        
        if memory_percent > 90:
            base_score -= 20
        elif memory_percent > 80:
            base_score -= 10
        
        if cpu_percent > 90:
            base_score -= 20
        elif cpu_percent > 80:
            base_score -= 10
        
        performance_score = max(0, min(100, base_score))
        
        return jsonify({
            "timestamp": time.time(),
            "performance_score": performance_score,
            "status_overview": status,
            "cache_performance": cache_stats,
            "metrics_summary": metrics_summary,
            "optimization_status": {
                "caching_enabled": True,
                "async_processing_enabled": True,
                "response_optimization_enabled": True,
                "performance_monitoring_enabled": True,
                "redis_available": cache_stats['redis_available']
            },
            "recommendations": [
                f"✅ Performance score: {performance_score}/100" if performance_score > 80 else f"⚠️ Performance needs attention: {performance_score}/100",
                f"Cache hit rate: {cache_stats['hit_rate_percent']:.1f}%" + (" (excellent)" if cache_stats['hit_rate_percent'] > 80 else " (needs improvement)"),
                f"Avg response time: {metrics_summary.get('avg_response_time_ms', 0):.1f}ms" + (" (fast)" if metrics_summary.get('avg_response_time_ms', 0) < 500 else " (slow)" if metrics_summary.get('avg_response_time_ms', 0) > 2000 else " (acceptable)"),
                f"Error rate: {error_rate:.1f}%" + (" (excellent)" if error_rate < 1 else " (high)" if error_rate > 5 else " (acceptable)"),
                "✅ All optimization features active" if cache_stats['redis_available'] else "⚠️ Redis unavailable - using local cache only"
            ]
        })
        
    except Exception as e:
        logger.error(f"Error generating performance dashboard: {e}")
        return jsonify({"error": str(e)}), 500

# Register blueprint (akan dilakukan di routes.py)
logger.info("🚀 Performance Optimization API endpoints initialized")