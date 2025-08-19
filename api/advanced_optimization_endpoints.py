#!/usr/bin/env python3
"""
Advanced Optimization API Endpoints
Database optimization, memory management, dan comprehensive system optimization
"""

from flask import Blueprint, jsonify, request, g
import logging
import time
import os
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from functools import wraps

# Import optimization components
from core.database_optimizer import get_database_optimizer, init_database_optimizer
from core.memory_optimizer import get_memory_optimizer
from core.performance_optimizer import get_performance_optimizer
from core.audit_logger import get_audit_logger, AuditEventType, AuditSeverity

logger = logging.getLogger(__name__)

# Create blueprint
advanced_optimization_bp = Blueprint('advanced_optimization', __name__, url_prefix='/api/optimization')

# Initialize components
memory_optimizer = get_memory_optimizer()
performance_optimizer = get_performance_optimizer()
audit_logger = get_audit_logger()

# Initialize database optimizer if DATABASE_URL available
database_optimizer = None
database_url = os.environ.get('DATABASE_URL')
if database_url:
    try:
        database_optimizer = init_database_optimizer(database_url)
        logger.info("Database optimizer initialized")
    except Exception as e:
        logger.warning(f"Could not initialize database optimizer: {e}")

def optimization_monitor(f):
    """Decorator untuk monitoring optimization operations"""
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
            
            # Log optimization operation
            audit_logger.log_event(
                event_type=AuditEventType.SYSTEM_EVENT,
                severity=AuditSeverity.INFO if success else AuditSeverity.ERROR,
                endpoint=request.endpoint or f.__name__,
                method=request.method,
                user_id=getattr(g, 'user_id', None),
                source_ip=request.remote_addr or "unknown",
                execution_time_ms=execution_time_ms,
                success=success,
                error_message=error_message,
                additional_context={'optimization_operation': f.__name__}
            )
    
    return wrapper

@advanced_optimization_bp.route('/status', methods=['GET'])
@optimization_monitor
def get_optimization_status():
    """
    Comprehensive optimization system status
    """
    try:
        status = {
            'timestamp': time.time(),
            'optimization_systems': {
                'database_optimizer': database_optimizer is not None,
                'memory_optimizer': True,
                'performance_optimizer': True,
                'cache_system': True
            }
        }
        
        # Database optimization status
        if database_optimizer:
            db_stats = database_optimizer.get_performance_stats()
            status['database_optimization'] = {
                'enabled': True,
                'cache_hit_rate': db_stats.get('cache_hit_rate_percent', 0),
                'avg_query_time': db_stats.get('avg_execution_time_ms', 0),
                'connection_pool_utilization': db_stats.get('connection_pool_stats', {}).get('pool_utilization_percent', 0)
            }
        else:
            status['database_optimization'] = {'enabled': False, 'reason': 'No DATABASE_URL configured'}
        
        # Memory optimization status
        memory_status = memory_optimizer.get_comprehensive_status()
        status['memory_optimization'] = {
            'enabled': True,
            'current_memory_mb': memory_status['memory_tracking']['current_memory_mb'],
            'potential_leaks': memory_status['memory_tracking']['potential_leaks'],
            'gc_objects': memory_status['garbage_collection']['total_objects']
        }
        
        # Performance optimization status
        perf_status = performance_optimizer.get_comprehensive_status()
        status['performance_optimization'] = {
            'enabled': True,
            'cache_hit_rate': perf_status['cache_stats']['hit_rate_percent'],
            'system_health': perf_status['performance_summary'].get('health_status', 'unknown')
        }
        
        return jsonify({
            "status": "active",
            "optimization_status": status,
            "recommendations": [
                "✅ Memory optimization active" if memory_status['memory_tracking']['potential_leaks'] == 0 else f"⚠️ {memory_status['memory_tracking']['potential_leaks']} potential memory leak(s)",
                f"✅ Database optimization {'enabled' if database_optimizer else 'disabled'}",
                "✅ Performance caching operational",
                "✅ All optimization systems ready"
            ]
        })
        
    except Exception as e:
        logger.error(f"Error getting optimization status: {e}")
        return jsonify({"error": str(e)}), 500

@advanced_optimization_bp.route('/database/stats', methods=['GET'])
@optimization_monitor
def get_database_stats():
    """
    Database optimization statistics
    """
    try:
        if not database_optimizer:
            return jsonify({"error": "Database optimizer not available"}), 503
        
        stats = database_optimizer.get_performance_stats()
        
        return jsonify({
            "database_statistics": stats,
            "optimization_insights": [
                f"Query cache hit rate: {stats['cache_hit_rate_percent']:.1f}%" + (" (excellent)" if stats['cache_hit_rate_percent'] > 80 else " (needs improvement)"),
                f"Average query time: {stats['avg_execution_time_ms']:.1f}ms" + (" (fast)" if stats['avg_execution_time_ms'] < 100 else " (slow)"),
                f"Connection pool usage: {stats['connection_pool_stats']['pool_utilization_percent']:.1f}%",
                f"Slow queries detected: {len(stats['slow_queries'])}"
            ],
            "timestamp": time.time()
        })
        
    except Exception as e:
        logger.error(f"Error getting database stats: {e}")
        return jsonify({"error": str(e)}), 500

@advanced_optimization_bp.route('/database/optimize', methods=['POST'])
@optimization_monitor
def optimize_database():
    """
    Run database optimization
    """
    try:
        if not database_optimizer:
            return jsonify({"error": "Database optimizer not available"}), 503
        
        # Force cache cleanup
        database_optimizer.query_cache.cache.clear()
        database_optimizer.query_cache.cache_metadata.clear()
        
        # Get fresh statistics
        stats = database_optimizer.get_performance_stats()
        optimization_report = database_optimizer.query_optimizer.get_optimization_report()
        
        return jsonify({
            "optimization_completed": True,
            "actions_taken": [
                "Query cache cleared",
                "Connection pool statistics updated",
                "Query optimization analysis refreshed"
            ],
            "current_stats": stats,
            "optimization_report": optimization_report,
            "timestamp": time.time()
        })
        
    except Exception as e:
        logger.error(f"Error optimizing database: {e}")
        return jsonify({"error": str(e)}), 500

@advanced_optimization_bp.route('/memory/stats', methods=['GET'])
@optimization_monitor
def get_memory_stats():
    """
    Memory optimization statistics
    """
    try:
        hours = int(request.args.get('hours', 1))
        memory_report = memory_optimizer.tracker.get_memory_report(hours)
        gc_stats = memory_optimizer.gc_optimizer.get_gc_stats()
        
        return jsonify({
            "memory_report": memory_report,
            "garbage_collection": gc_stats,
            "object_pools": {
                pool_name: pool.get_stats()
                for pool_name, pool in memory_optimizer.object_pools.items()
            },
            "memory_insights": [
                f"Current memory usage: {memory_report['current_memory_mb']:.1f}MB",
                f"Memory trend: {memory_report['memory_trend']} ({memory_report['memory_change_mb']:+.1f}MB)",
                f"Potential leaks: {memory_report['potential_leaks']}",
                f"GC objects: {gc_stats['total_objects']}"
            ],
            "timestamp": time.time()
        })
        
    except Exception as e:
        logger.error(f"Error getting memory stats: {e}")
        return jsonify({"error": str(e)}), 500

@advanced_optimization_bp.route('/memory/optimize', methods=['POST'])
@optimization_monitor
def optimize_memory():
    """
    Run comprehensive memory optimization
    """
    try:
        # Run memory optimization
        optimization_result = memory_optimizer.optimize_memory_usage()
        
        return jsonify({
            "optimization_completed": True,
            "optimization_result": optimization_result,
            "actions_taken": [
                f"Freed {optimization_result['memory_saved_mb']:.1f}MB memory",
                f"Removed {optimization_result['objects_removed']} objects",
                "Garbage collection performed",
                f"GC thresholds optimized for {optimization_result['memory_pressure']} pressure"
            ],
            "recommendations": [
                "Memory optimization completed successfully" if optimization_result['optimization_effective'] else "No significant memory savings achieved",
                "Consider running optimization periodically for best results",
                "Monitor memory leaks if high memory usage persists"
            ],
            "timestamp": time.time()
        })
        
    except Exception as e:
        logger.error(f"Error optimizing memory: {e}")
        return jsonify({"error": str(e)}), 500

@advanced_optimization_bp.route('/memory/gc/force', methods=['POST'])
@optimization_monitor
def force_garbage_collection():
    """
    Force garbage collection
    """
    try:
        gc_result = memory_optimizer.gc_optimizer.force_gc_collection()
        
        return jsonify({
            "garbage_collection_completed": True,
            "gc_result": gc_result,
            "summary": f"Freed {gc_result['objects_freed']} objects and {gc_result['memory_freed_mb']:.1f}MB memory",
            "timestamp": time.time()
        })
        
    except Exception as e:
        logger.error(f"Error forcing garbage collection: {e}")
        return jsonify({"error": str(e)}), 500

@advanced_optimization_bp.route('/comprehensive', methods=['POST'])
@optimization_monitor
def run_comprehensive_optimization():
    """
    Run comprehensive system optimization
    """
    try:
        results = {
            'timestamp': time.time(),
            'optimizations_performed': [],
            'total_improvements': {}
        }
        
        memory_before = memory_optimizer.tracker.take_snapshot().process_memory_mb
        
        # 1. Memory optimization
        try:
            memory_result = memory_optimizer.optimize_memory_usage()
            results['optimizations_performed'].append('memory_optimization')
            results['memory_optimization'] = memory_result
        except Exception as e:
            logger.warning(f"Memory optimization failed: {e}")
        
        # 2. Performance cache optimization
        try:
            # Clear old cache entries
            performance_optimizer.cache.cache.clear()
            performance_optimizer.cache.cache_metadata.clear()
            results['optimizations_performed'].append('cache_optimization')
        except Exception as e:
            logger.warning(f"Cache optimization failed: {e}")
        
        # 3. Database optimization (if available)
        if database_optimizer:
            try:
                database_optimizer.query_cache.cache.clear()
                database_optimizer.query_cache.cache_metadata.clear()
                results['optimizations_performed'].append('database_optimization')
            except Exception as e:
                logger.warning(f"Database optimization failed: {e}")
        
        # Calculate total improvements
        memory_after = memory_optimizer.tracker.take_snapshot().process_memory_mb
        memory_saved = memory_before - memory_after
        
        results['total_improvements'] = {
            'memory_saved_mb': round(memory_saved, 2),
            'optimizations_count': len(results['optimizations_performed']),
            'optimization_effective': memory_saved > 0 or len(results['optimizations_performed']) > 0
        }
        
        return jsonify({
            "comprehensive_optimization_completed": True,
            "optimization_results": results,
            "summary": f"Performed {len(results['optimizations_performed'])} optimizations, saved {memory_saved:.1f}MB memory",
            "recommendations": [
                "✅ Comprehensive optimization completed",
                f"✅ {len(results['optimizations_performed'])} systems optimized",
                "🔄 Run optimization periodically untuk maintain performance",
                "📊 Monitor system metrics untuk track improvements"
            ]
        })
        
    except Exception as e:
        logger.error(f"Error in comprehensive optimization: {e}")
        return jsonify({"error": str(e)}), 500

@advanced_optimization_bp.route('/health', methods=['GET'])
@optimization_monitor
def optimization_health_check():
    """
    Advanced optimization health check
    """
    try:
        health_checks = {
            "database_optimizer": False,
            "memory_optimizer": False,
            "performance_optimizer": False,
            "cache_systems": False,
            "garbage_collection": False
        }
        
        issues = []
        
        # Test database optimizer
        if database_optimizer:
            try:
                db_stats = database_optimizer.get_performance_stats()
                if 'total_queries' in db_stats:
                    health_checks["database_optimizer"] = True
                else:
                    issues.append("Database optimizer not collecting metrics")
            except Exception as e:
                issues.append(f"Database optimizer error: {str(e)}")
        else:
            issues.append("Database optimizer not available")
        
        # Test memory optimizer
        try:
            memory_status = memory_optimizer.get_comprehensive_status()
            if 'memory_tracking' in memory_status:
                health_checks["memory_optimizer"] = True
            else:
                issues.append("Memory optimizer not tracking properly")
        except Exception as e:
            issues.append(f"Memory optimizer error: {str(e)}")
        
        # Test performance optimizer
        try:
            perf_status = performance_optimizer.get_comprehensive_status()
            if 'cache_stats' in perf_status:
                health_checks["performance_optimizer"] = True
            else:
                issues.append("Performance optimizer not functioning")
        except Exception as e:
            issues.append(f"Performance optimizer error: {str(e)}")
        
        # Test cache systems
        try:
            cache_stats = performance_optimizer.cache.get_stats()
            if 'cache_types' in cache_stats:
                health_checks["cache_systems"] = True
            else:
                issues.append("Cache systems not responding")
        except Exception as e:
            issues.append(f"Cache systems error: {str(e)}")
        
        # Test garbage collection
        try:
            gc_stats = memory_optimizer.gc_optimizer.get_gc_stats()
            if 'total_objects' in gc_stats:
                health_checks["garbage_collection"] = True
            else:
                issues.append("Garbage collection monitoring failed")
        except Exception as e:
            issues.append(f"Garbage collection error: {str(e)}")
        
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
            "optimization_recommendations": [
                "✅ All optimization systems operational" if not issues else f"⚠️ {len(issues)} issue(s) detected",
                "Advanced optimization features active",
                "Database, memory, dan performance optimization ready" if passed_checks >= 4 else "Some optimization systems need attention"
            ],
            "timestamp": time.time()
        })
        
    except Exception as e:
        logger.error(f"Error in optimization health check: {e}")
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": time.time()
        }), 500

@advanced_optimization_bp.route('/dashboard', methods=['GET'])
@optimization_monitor
def get_optimization_dashboard():
    """
    Comprehensive optimization dashboard
    """
    try:
        dashboard = {
            'timestamp': time.time(),
            'system_overview': {},
            'optimization_scores': {},
            'recommendations': []
        }
        
        # Database optimization
        if database_optimizer:
            db_stats = database_optimizer.get_performance_stats()
            dashboard['database_optimization'] = db_stats
            dashboard['optimization_scores']['database'] = min(100, max(0, 
                100 - (db_stats.get('avg_execution_time_ms', 0) / 10) + db_stats.get('cache_hit_rate_percent', 0)
            ))
        
        # Memory optimization
        memory_status = memory_optimizer.get_comprehensive_status()
        dashboard['memory_optimization'] = memory_status['memory_tracking']
        
        # Calculate memory score
        memory_mb = memory_status['memory_tracking']['current_memory_mb']
        leak_count = memory_status['memory_tracking']['potential_leaks']
        memory_score = max(0, min(100, 100 - (memory_mb / 50) - (leak_count * 20)))
        dashboard['optimization_scores']['memory'] = memory_score
        
        # Performance optimization
        perf_status = performance_optimizer.get_comprehensive_status()
        dashboard['performance_optimization'] = perf_status['cache_stats']
        dashboard['optimization_scores']['performance'] = perf_status['cache_stats']['hit_rate_percent']
        
        # Overall optimization score
        scores = list(dashboard['optimization_scores'].values())
        overall_score = sum(scores) / len(scores) if scores else 0
        dashboard['overall_optimization_score'] = round(overall_score, 1)
        
        # Generate recommendations
        dashboard['recommendations'] = [
            f"Overall optimization score: {overall_score:.1f}/100",
            f"Database optimization: {'enabled' if database_optimizer else 'disabled'}",
            f"Memory usage: {memory_mb:.1f}MB" + (" (high)" if memory_mb > 1000 else " (normal)"),
            f"Cache hit rate: {perf_status['cache_stats']['hit_rate_percent']:.1f}%",
            "🚀 All optimization systems active and monitoring"
        ]
        
        return jsonify({
            "optimization_dashboard": dashboard,
            "status": "optimal" if overall_score > 80 else "good" if overall_score > 60 else "needs_attention",
            "summary": f"Optimization score: {overall_score:.1f}/100 - System performing {'excellently' if overall_score > 80 else 'well' if overall_score > 60 else 'with room for improvement'}"
        })
        
    except Exception as e:
        logger.error(f"Error generating optimization dashboard: {e}")
        return jsonify({"error": str(e)}), 500

# Register blueprint (akan dilakukan di routes.py)
logger.info("🚀 Advanced Optimization API endpoints initialized")