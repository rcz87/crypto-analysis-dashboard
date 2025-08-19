#!/usr/bin/env python3
"""
Performance Optimization Engine - Comprehensive API performance optimization
Caching, connection pooling, async processing, response optimization
"""

import logging
import time
import asyncio
import threading
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
import redis
import json
import hashlib
import pickle
import gzip
from functools import wraps, lru_cache
import queue
import concurrent.futures
from collections import defaultdict, deque
import psutil
import os

logger = logging.getLogger(__name__)

@dataclass
class CacheConfig:
    ttl: int  # Time to live in seconds
    max_size: int  # Maximum cache size
    compress: bool = False  # Gzip compression
    serialize: str = "json"  # json, pickle, or msgpack

@dataclass
class PerformanceMetrics:
    response_time_ms: float
    cache_hit_rate: float
    memory_usage_mb: float
    cpu_usage_percent: float
    active_connections: int
    queue_size: int
    errors_per_minute: int

class SmartCache:
    """
    Intelligent caching system dengan compression dan smart invalidation
    """
    
    def __init__(self, redis_client=None, default_ttl=300):
        self.logger = logging.getLogger(__name__)
        
        # Redis setup untuk distributed caching
        try:
            if redis_client:
                self.redis = redis_client
            else:
                self.redis = redis.Redis(host='localhost', port=6379, db=1, decode_responses=False)
            self.redis.ping()
            self.redis_available = True
        except Exception as e:
            self.logger.warning(f"Redis not available for caching: {e}")
            self.redis = None
            self.redis_available = False
        
        # Local memory cache sebagai fallback
        self.local_cache = {}
        self.cache_metadata = {}  # {key: {'created': timestamp, 'ttl': seconds, 'size': bytes}}
        self.default_ttl = default_ttl
        self.max_local_cache_size = 1000
        
        # Cache configurations untuk different data types
        self.cache_configs = {
            'trading_signals': CacheConfig(ttl=60, max_size=100, compress=True),
            'market_data': CacheConfig(ttl=30, max_size=500, compress=False),
            'smc_analysis': CacheConfig(ttl=120, max_size=200, compress=True),
            'user_sessions': CacheConfig(ttl=1800, max_size=1000, compress=False),
            'api_responses': CacheConfig(ttl=300, max_size=1000, compress=True),
            'data_quality': CacheConfig(ttl=180, max_size=100, compress=False)
        }
        
        # Cache hit/miss statistics
        self.stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0,
            'errors': 0
        }
        
        self.logger.info("🚀 Smart Cache initialized")
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate consistent cache key"""
        key_data = f"{prefix}:{':'.join(map(str, args))}"
        if kwargs:
            key_data += f":{json.dumps(kwargs, sort_keys=True)}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _serialize_data(self, data: Any, config: CacheConfig) -> bytes:
        """Serialize data berdasarkan configuration"""
        try:
            if config.serialize == "json":
                serialized = json.dumps(data, ensure_ascii=False).encode('utf-8')
            elif config.serialize == "pickle":
                serialized = pickle.dumps(data)
            else:
                serialized = json.dumps(data, ensure_ascii=False).encode('utf-8')
            
            if config.compress:
                serialized = gzip.compress(serialized)
            
            return serialized
        except Exception as e:
            self.logger.error(f"Serialization error: {e}")
            return b""
    
    def _deserialize_data(self, data: bytes, config: CacheConfig) -> Any:
        """Deserialize data berdasarkan configuration"""
        try:
            if config.compress:
                data = gzip.decompress(data)
            
            if config.serialize == "json":
                return json.loads(data.decode('utf-8'))
            elif config.serialize == "pickle":
                return pickle.loads(data)
            else:
                return json.loads(data.decode('utf-8'))
        except Exception as e:
            self.logger.error(f"Deserialization error: {e}")
            return None
    
    def get(self, cache_type: str, key: str) -> Optional[Any]:
        """Get data from cache"""
        try:
            full_key = f"{cache_type}:{key}"
            config = self.cache_configs.get(cache_type, CacheConfig(ttl=self.default_ttl, max_size=100))
            
            # Try Redis first
            if self.redis_available and self.redis:
                try:
                    data = self.redis.get(full_key)
                    if data and isinstance(data, bytes):
                        result = self._deserialize_data(data, config)
                        if result is not None:
                            self.stats['hits'] += 1
                            return result
                except Exception as e:
                    self.logger.error(f"Redis get error: {e}")
            
            # Fallback to local cache
            if full_key in self.local_cache:
                metadata = self.cache_metadata.get(full_key, {})
                created = metadata.get('created', 0)
                ttl = metadata.get('ttl', self.default_ttl)
                
                if time.time() - created < ttl:
                    self.stats['hits'] += 1
                    return self.local_cache[full_key]
                else:
                    # Expired, remove from local cache
                    del self.local_cache[full_key]
                    del self.cache_metadata[full_key]
            
            self.stats['misses'] += 1
            return None
            
        except Exception as e:
            self.logger.error(f"Cache get error: {e}")
            self.stats['errors'] += 1
            return None
    
    def set(self, cache_type: str, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set data in cache"""
        try:
            full_key = f"{cache_type}:{key}"
            config = self.cache_configs.get(cache_type, CacheConfig(ttl=self.default_ttl, max_size=100))
            ttl = ttl or config.ttl
            
            # Try Redis first
            if self.redis_available and self.redis:
                try:
                    serialized = self._serialize_data(value, config)
                    if serialized:
                        self.redis.setex(full_key, ttl, serialized)
                        self.stats['sets'] += 1
                        return True
                except Exception as e:
                    self.logger.error(f"Redis set error: {e}")
            
            # Fallback to local cache
            if len(self.local_cache) >= self.max_local_cache_size:
                # Remove oldest entries
                oldest_keys = sorted(
                    self.cache_metadata.keys(),
                    key=lambda k: self.cache_metadata[k].get('created', 0)
                )[:10]
                for old_key in oldest_keys:
                    self.local_cache.pop(old_key, None)
                    self.cache_metadata.pop(old_key, None)
            
            self.local_cache[full_key] = value
            self.cache_metadata[full_key] = {
                'created': time.time(),
                'ttl': ttl,
                'size': len(str(value))
            }
            self.stats['sets'] += 1
            return True
            
        except Exception as e:
            self.logger.error(f"Cache set error: {e}")
            self.stats['errors'] += 1
            return False
    
    def delete(self, cache_type: str, key: str) -> bool:
        """Delete data from cache"""
        try:
            full_key = f"{cache_type}:{key}"
            
            # Delete from Redis
            if self.redis_available and self.redis:
                try:
                    self.redis.delete(full_key)
                except Exception as e:
                    self.logger.error(f"Redis delete error: {e}")
            
            # Delete from local cache
            self.local_cache.pop(full_key, None)
            self.cache_metadata.pop(full_key, None)
            
            self.stats['deletes'] += 1
            return True
            
        except Exception as e:
            self.logger.error(f"Cache delete error: {e}")
            self.stats['errors'] += 1
            return False
    
    def clear_type(self, cache_type: str) -> bool:
        """Clear all cache data untuk specific type"""
        try:
            pattern = f"{cache_type}:*"
            
            # Clear from Redis
            if self.redis_available and self.redis:
                try:
                    keys = self.redis.keys(pattern)
                    if keys and isinstance(keys, list) and len(keys) > 0:
                        self.redis.delete(*keys)
                except Exception as e:
                    self.logger.error(f"Redis clear error: {e}")
            
            # Clear from local cache
            keys_to_remove = [k for k in self.local_cache.keys() if k.startswith(f"{cache_type}:")]
            for key in keys_to_remove:
                self.local_cache.pop(key, None)
                self.cache_metadata.pop(key, None)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Cache clear error: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.stats['hits'] + self.stats['misses']
        hit_rate = (self.stats['hits'] / max(1, total_requests)) * 100
        
        local_cache_size = sum(
            metadata.get('size', 0) 
            for metadata in self.cache_metadata.values()
        )
        
        return {
            'hit_rate_percent': round(hit_rate, 2),
            'total_hits': self.stats['hits'],
            'total_misses': self.stats['misses'],
            'total_sets': self.stats['sets'],
            'total_deletes': self.stats['deletes'],
            'total_errors': self.stats['errors'],
            'redis_available': self.redis_available,
            'local_cache_entries': len(self.local_cache),
            'local_cache_size_bytes': local_cache_size,
            'cache_types': list(self.cache_configs.keys())
        }

class AsyncTaskProcessor:
    """
    Background task processor untuk non-blocking operations
    """
    
    def __init__(self, max_workers=4):
        self.max_workers = max_workers
        self.task_queue = queue.Queue()
        self.result_cache = {}
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        self.background_thread = threading.Thread(target=self._process_tasks, daemon=True)
        self.background_thread.start()
        self.running = True
        
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"🔄 Async Task Processor initialized with {max_workers} workers")
    
    def submit_task(self, task_id: str, func: Callable, *args, **kwargs) -> Optional[str]:
        """Submit task untuk background processing"""
        try:
            future = self.executor.submit(func, *args, **kwargs)
            self.task_queue.put((task_id, future))
            return task_id
        except Exception as e:
            self.logger.error(f"Error submitting task {task_id}: {e}")
            return None
    
    def get_result(self, task_id: str) -> Optional[Any]:
        """Get task result if available"""
        return self.result_cache.get(task_id)
    
    def _process_tasks(self):
        """Background task processing"""
        while self.running:
            try:
                if not self.task_queue.empty():
                    task_id, future = self.task_queue.get(timeout=1)
                    
                    if future.done():
                        try:
                            result = future.result()
                            self.result_cache[task_id] = result
                        except Exception as e:
                            self.result_cache[task_id] = {"error": str(e)}
                    else:
                        # Put back in queue if not done
                        self.task_queue.put((task_id, future))
                
                time.sleep(0.1)
                
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Error in task processor: {e}")

class ResponseOptimizer:
    """
    Response optimization dengan compression dan pagination
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("📦 Response Optimizer initialized")
    
    def optimize_response(self, data: Any, request_args: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize API response"""
        try:
            # Pagination
            if isinstance(data, list) and len(data) > 100:
                page = int(request_args.get('page', 1))
                per_page = min(int(request_args.get('per_page', 50)), 1000)
                
                start_idx = (page - 1) * per_page
                end_idx = start_idx + per_page
                
                paginated_data = data[start_idx:end_idx]
                
                return {
                    'data': paginated_data,
                    'pagination': {
                        'page': page,
                        'per_page': per_page,
                        'total_items': len(data),
                        'total_pages': (len(data) + per_page - 1) // per_page,
                        'has_next': end_idx < len(data),
                        'has_prev': page > 1
                    }
                }
            
            # Field selection
            fields = request_args.get('fields')
            if fields and isinstance(data, (list, dict)):
                selected_fields = fields.split(',')
                if isinstance(data, list):
                    data = [
                        {field: item.get(field) for field in selected_fields if field in item}
                        for item in data if isinstance(item, dict)
                    ]
                elif isinstance(data, dict):
                    data = {field: data.get(field) for field in selected_fields if field in data}
            
            return {'data': data}
            
        except Exception as e:
            self.logger.error(f"Response optimization error: {e}")
            return {'data': data}

class PerformanceMonitor:
    """
    Real-time performance monitoring
    """
    
    def __init__(self):
        self.metrics_history = deque(maxlen=1000)
        self.endpoint_metrics = defaultdict(list)
        self.alert_thresholds = {
            'response_time_ms': 5000,
            'memory_usage_mb': 1000,
            'cpu_usage_percent': 80,
            'error_rate_percent': 5
        }
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("📊 Performance Monitor initialized")
    
    def record_request(self, endpoint: str, response_time_ms: float, success: bool):
        """Record request metrics"""
        timestamp = time.time()
        
        # Record endpoint-specific metrics
        self.endpoint_metrics[endpoint].append({
            'timestamp': timestamp,
            'response_time_ms': response_time_ms,
            'success': success
        })
        
        # Keep only recent metrics (last 1000 requests per endpoint)
        if len(self.endpoint_metrics[endpoint]) > 1000:
            self.endpoint_metrics[endpoint] = self.endpoint_metrics[endpoint][-1000:]
        
        # Record system metrics
        memory_usage = psutil.virtual_memory().used / 1024 / 1024  # MB
        cpu_usage = psutil.cpu_percent()
        
        metrics = PerformanceMetrics(
            response_time_ms=response_time_ms,
            cache_hit_rate=0,  # Will be updated by cache
            memory_usage_mb=memory_usage,
            cpu_usage_percent=cpu_usage,
            active_connections=0,  # Will be updated by connection pool
            queue_size=0,  # Will be updated by task processor
            errors_per_minute=0  # Will be calculated
        )
        
        self.metrics_history.append({
            'timestamp': timestamp,
            'endpoint': endpoint,
            'metrics': metrics,
            'success': success
        })
    
    def get_performance_summary(self, minutes: int = 5) -> Dict[str, Any]:
        """Get performance summary untuk last N minutes"""
        try:
            cutoff_time = time.time() - (minutes * 60)
            recent_metrics = [
                m for m in self.metrics_history 
                if m['timestamp'] > cutoff_time
            ]
            
            if not recent_metrics:
                return {'error': 'No recent metrics available'}
            
            # Calculate averages
            total_requests = len(recent_metrics)
            successful_requests = sum(1 for m in recent_metrics if m['success'])
            error_rate = ((total_requests - successful_requests) / total_requests) * 100
            
            avg_response_time = sum(m['metrics'].response_time_ms for m in recent_metrics) / total_requests
            avg_memory = sum(m['metrics'].memory_usage_mb for m in recent_metrics) / total_requests
            avg_cpu = sum(m['metrics'].cpu_usage_percent for m in recent_metrics) / total_requests
            
            # Endpoint breakdown
            endpoint_stats = {}
            for endpoint, metrics_list in self.endpoint_metrics.items():
                recent_endpoint_metrics = [
                    m for m in metrics_list 
                    if m['timestamp'] > cutoff_time
                ]
                
                if recent_endpoint_metrics:
                    endpoint_total = len(recent_endpoint_metrics)
                    endpoint_success = sum(1 for m in recent_endpoint_metrics if m['success'])
                    endpoint_avg_time = sum(m['response_time_ms'] for m in recent_endpoint_metrics) / endpoint_total
                    
                    endpoint_stats[endpoint] = {
                        'total_requests': endpoint_total,
                        'success_rate': (endpoint_success / endpoint_total) * 100,
                        'avg_response_time_ms': round(endpoint_avg_time, 2),
                        'error_rate': ((endpoint_total - endpoint_success) / endpoint_total) * 100
                    }
            
            # Performance alerts
            alerts = []
            if avg_response_time > self.alert_thresholds['response_time_ms']:
                alerts.append(f"High response time: {avg_response_time:.1f}ms")
            if avg_memory > self.alert_thresholds['memory_usage_mb']:
                alerts.append(f"High memory usage: {avg_memory:.1f}MB")
            if avg_cpu > self.alert_thresholds['cpu_usage_percent']:
                alerts.append(f"High CPU usage: {avg_cpu:.1f}%")
            if error_rate > self.alert_thresholds['error_rate_percent']:
                alerts.append(f"High error rate: {error_rate:.1f}%")
            
            return {
                'period_minutes': minutes,
                'total_requests': total_requests,
                'success_rate_percent': round((successful_requests / total_requests) * 100, 2),
                'error_rate_percent': round(error_rate, 2),
                'avg_response_time_ms': round(avg_response_time, 2),
                'avg_memory_usage_mb': round(avg_memory, 2),
                'avg_cpu_usage_percent': round(avg_cpu, 2),
                'endpoint_breakdown': endpoint_stats,
                'performance_alerts': alerts,
                'health_status': 'healthy' if not alerts else 'warning' if len(alerts) < 3 else 'critical'
            }
            
        except Exception as e:
            self.logger.error(f"Error generating performance summary: {e}")
            return {'error': str(e)}

class PerformanceOptimizer:
    """
    Main Performance Optimization Engine
    """
    
    def __init__(self):
        self.cache = SmartCache()
        self.task_processor = AsyncTaskProcessor()
        self.response_optimizer = ResponseOptimizer()
        self.monitor = PerformanceMonitor()
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("🚀 Performance Optimizer Engine initialized")
    
    def get_comprehensive_status(self) -> Dict[str, Any]:
        """Get comprehensive performance status"""
        return {
            'timestamp': time.time(),
            'cache_stats': self.cache.get_stats(),
            'performance_summary': self.monitor.get_performance_summary(),
            'system_resources': {
                'memory_usage_mb': psutil.virtual_memory().used / 1024 / 1024,
                'memory_percent': psutil.virtual_memory().percent,
                'cpu_percent': psutil.cpu_percent(),
                'disk_usage_percent': psutil.disk_usage('/').percent
            },
            'optimization_features': {
                'smart_caching': True,
                'async_processing': True,
                'response_optimization': True,
                'performance_monitoring': True
            }
        }

# Global instance
performance_optimizer = PerformanceOptimizer()

def get_performance_optimizer():
    """Get global performance optimizer instance"""
    return performance_optimizer

# Decorator untuk caching API responses
def cache_response(cache_type: str = 'api_responses', ttl: Optional[int] = None):
    """Decorator untuk caching API responses"""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # Generate cache key berdasarkan function name dan arguments
            cache_key = f"{f.__name__}:{hashlib.md5(str(args).encode() + str(kwargs).encode()).hexdigest()}"
            
            # Try to get from cache
            cached_result = performance_optimizer.cache.get(cache_type, cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function
            start_time = time.time()
            success = True
            try:
                result = f(*args, **kwargs)
                
                # Cache the result
                performance_optimizer.cache.set(cache_type, cache_key, result, ttl)
                
                return result
                
            except Exception as e:
                success = False
                raise
            finally:
                # Record performance metrics
                response_time_ms = (time.time() - start_time) * 1000
                performance_optimizer.monitor.record_request(f.__name__, response_time_ms, success)
        
        return wrapper
    return decorator

# Decorator untuk async task processing
def async_task(task_type: str = 'default'):
    """Decorator untuk async task processing"""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            task_id = f"{task_type}_{int(time.time() * 1000)}"
            return performance_optimizer.task_processor.submit_task(task_id, f, *args, **kwargs)
        return wrapper
    return decorator

logger.info("🚀 Performance Optimization Engine module initialized")