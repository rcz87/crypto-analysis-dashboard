#!/usr/bin/env python3
"""
Intelligent Resource Pool Management
Advanced resource management untuk 50+ endpoints dengan:
- Smart connection pooling
- Resource prioritization  
- Adaptive scaling
- Memory optimization
- Queue management
"""

import threading
import time
import logging
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from queue import Queue, PriorityQueue
from concurrent.futures import ThreadPoolExecutor, Future
from collections import defaultdict
import psutil
import gc

logger = logging.getLogger(__name__)

@dataclass
class ResourceRequest:
    """Request untuk resource dengan prioritas"""
    priority: int  # 1=highest, 4=lowest
    endpoint_id: str
    resource_type: str  # 'db', 'api', 'cache', 'compute'
    callback: Callable
    args: tuple
    kwargs: dict
    timestamp: float
    timeout: float = 30.0
    
    def __lt__(self, other):
        return self.priority < other.priority

class ConnectionPool:
    """Advanced connection pool dengan smart management"""
    
    def __init__(self, pool_name: str, 
                 min_connections: int = 5, 
                 max_connections: int = 50,
                 idle_timeout: int = 300):
        self.pool_name = pool_name
        self.min_connections = min_connections
        self.max_connections = max_connections
        self.idle_timeout = idle_timeout
        
        self.available_connections = Queue(maxsize=max_connections)
        self.active_connections = set()
        self.connection_metrics = defaultdict(dict)
        self.lock = threading.RLock()
        
        # Performance tracking
        self.pool_hits = 0
        self.pool_misses = 0
        self.connections_created = 0
        self.connections_destroyed = 0
        
        # Initialize minimum connections
        self._initialize_pool()
        
        # Start maintenance thread
        self._start_maintenance_thread()
    
    def _initialize_pool(self):
        """Initialize pool dengan minimum connections"""
        for _ in range(self.min_connections):
            conn = self._create_connection()
            if conn:
                self.available_connections.put(conn)
    
    def _create_connection(self):
        """Create new connection - override dalam subclass"""
        # Mock connection untuk example
        connection_id = f"{self.pool_name}_conn_{self.connections_created}"
        self.connections_created += 1
        
        connection = {
            'id': connection_id,
            'created_at': time.time(),
            'last_used': time.time(),
            'use_count': 0,
            'pool_name': self.pool_name
        }
        
        return connection
    
    def get_connection(self, timeout: float = 10.0):
        """Get connection dari pool dengan timeout"""
        start_time = time.time()
        
        while (time.time() - start_time) < timeout:
            try:
                # Try to get existing connection
                if not self.available_connections.empty():
                    conn = self.available_connections.get_nowait()
                    
                    # Validate connection
                    if self._is_connection_valid(conn):
                        with self.lock:
                            self.active_connections.add(conn['id'])
                            conn['last_used'] = time.time()
                            conn['use_count'] += 1
                            self.pool_hits += 1
                        
                        return conn
                    else:
                        # Connection tidak valid, destroy dan coba lagi
                        self._destroy_connection(conn)
                
                # No available connections, try to create new one
                if len(self.active_connections) < self.max_connections:
                    new_conn = self._create_connection()
                    if new_conn:
                        with self.lock:
                            self.active_connections.add(new_conn['id'])
                            self.pool_misses += 1
                        return new_conn
                
                # Pool is full, wait a bit
                time.sleep(0.1)
                
            except Exception as e:
                logger.warning(f"Error getting connection from pool {self.pool_name}: {e}")
        
        raise Exception(f"Timeout getting connection from pool {self.pool_name}")
    
    def return_connection(self, connection):
        """Return connection ke pool"""
        if not connection:
            return
        
        with self.lock:
            conn_id = connection['id']
            if conn_id in self.active_connections:
                self.active_connections.remove(conn_id)
                
                # Check if connection is still good
                if self._is_connection_valid(connection):
                    try:
                        self.available_connections.put_nowait(connection)
                    except:
                        # Queue full, destroy connection
                        self._destroy_connection(connection)
                else:
                    self._destroy_connection(connection)
    
    def _is_connection_valid(self, connection) -> bool:
        """Check if connection is still valid"""
        if not connection:
            return False
        
        # Check age
        age = time.time() - connection['created_at']
        if age > self.idle_timeout:
            return False
        
        # Check if connection is working (mock check)
        return True
    
    def _destroy_connection(self, connection):
        """Destroy connection dan cleanup resources"""
        if connection:
            self.connections_destroyed += 1
            # Actual cleanup would happen here
    
    def _start_maintenance_thread(self):
        """Start background maintenance thread"""
        def maintenance_worker():
            while True:
                try:
                    self._cleanup_idle_connections()
                    self._ensure_minimum_connections()
                    time.sleep(60)  # Run every minute
                except Exception as e:
                    logger.error(f"Connection pool maintenance error: {e}")
        
        thread = threading.Thread(target=maintenance_worker, daemon=True)
        thread.start()
    
    def _cleanup_idle_connections(self):
        """Cleanup idle connections"""
        current_time = time.time()
        connections_to_remove = []
        
        # Check available connections
        temp_queue = Queue()
        while not self.available_connections.empty():
            try:
                conn = self.available_connections.get_nowait()
                if (current_time - conn['last_used']) > self.idle_timeout:
                    connections_to_remove.append(conn)
                else:
                    temp_queue.put(conn)
            except:
                break
        
        # Put back valid connections
        while not temp_queue.empty():
            self.available_connections.put(temp_queue.get())
        
        # Destroy idle connections
        for conn in connections_to_remove:
            self._destroy_connection(conn)
    
    def _ensure_minimum_connections(self):
        """Ensure minimum connections are maintained"""
        current_total = self.available_connections.qsize() + len(self.active_connections)
        
        if current_total < self.min_connections:
            needed = self.min_connections - current_total
            for _ in range(needed):
                conn = self._create_connection()
                if conn:
                    self.available_connections.put(conn)
    
    def get_pool_stats(self) -> Dict[str, Any]:
        """Get pool statistics"""
        return {
            'pool_name': self.pool_name,
            'available_connections': self.available_connections.qsize(),
            'active_connections': len(self.active_connections),
            'total_connections': self.available_connections.qsize() + len(self.active_connections),
            'max_connections': self.max_connections,
            'min_connections': self.min_connections,
            'pool_hits': self.pool_hits,
            'pool_misses': self.pool_misses,
            'hit_rate_percent': (self.pool_hits / max(self.pool_hits + self.pool_misses, 1)) * 100,
            'connections_created': self.connections_created,
            'connections_destroyed': self.connections_destroyed
        }

class IntelligentResourcePool:
    """
    Intelligent Resource Pool Management System
    Handles multiple resource types dengan prioritization dan smart scaling
    """
    
    def __init__(self):
        # Resource pools by type
        self.connection_pools: Dict[str, ConnectionPool] = {}
        
        # Request queues dengan prioritas
        self.request_queue = PriorityQueue(maxsize=1000)
        self.processing_threads = {}
        
        # Resource monitoring
        self.resource_usage = {
            'cpu_percent': 0.0,
            'memory_percent': 0.0,
            'active_requests': 0,
            'queued_requests': 0,
            'thread_pool_utilization': 0.0
        }
        
        # Thread pools untuk berbagai jenis task
        self.thread_pools = {
            'critical': ThreadPoolExecutor(max_workers=10, thread_name_prefix='critical'),
            'high': ThreadPoolExecutor(max_workers=15, thread_name_prefix='high'),  
            'medium': ThreadPoolExecutor(max_workers=20, thread_name_prefix='medium'),
            'low': ThreadPoolExecutor(max_workers=10, thread_name_prefix='low')
        }
        
        # Performance tracking
        self.performance_metrics = {
            'total_requests_processed': 0,
            'avg_processing_time_ms': 0.0,
            'queue_wait_time_ms': 0.0,
            'resource_efficiency_score': 100.0,
            'auto_scaling_actions': 0
        }
        
        # Configuration
        self.max_queue_size = 1000
        self.auto_scaling_enabled = False  # DISABLED: Preventing infinite scaling loop
        self.memory_threshold_percent = 85
        self.cpu_threshold_percent = 80
        
        # Initialize default pools
        self._initialize_default_pools()
        
        # Start monitoring
        self._start_resource_monitoring()
        
        self.logger = logging.getLogger(f"{__name__}.IntelligentResourcePool")
        self.logger.info("🧠 Intelligent Resource Pool initialized - Smart resource management active")
    
    def _initialize_default_pools(self):
        """Initialize default connection pools"""
        # Database connections
        self.connection_pools['database'] = ConnectionPool(
            'database', min_connections=10, max_connections=50
        )
        
        # External API connections (OKX, etc)
        self.connection_pools['external_api'] = ConnectionPool(
            'external_api', min_connections=5, max_connections=30
        )
        
        # Cache connections
        self.connection_pools['cache'] = ConnectionPool(
            'cache', min_connections=3, max_connections=20
        )
        
        # Internal API connections
        self.connection_pools['internal_api'] = ConnectionPool(
            'internal_api', min_connections=5, max_connections=40
        )
    
    def submit_request(self, endpoint_id: str, priority: int, 
                      resource_type: str, callback: Callable,
                      *args, **kwargs) -> Future:
        """Submit request dengan prioritas dan resource type"""
        
        if self.request_queue.full():
            raise Exception("Request queue is full - system overloaded")
        
        request = ResourceRequest(
            priority=priority,
            endpoint_id=endpoint_id,
            resource_type=resource_type,
            callback=callback,
            args=args,
            kwargs=kwargs,
            timestamp=time.time()
        )
        
        # Add ke priority queue
        self.request_queue.put(request)
        
        # Get appropriate thread pool
        pool_name = self._get_thread_pool_name(priority)
        thread_pool = self.thread_pools[pool_name]
        
        # Submit untuk processing
        future = thread_pool.submit(self._process_request, request)
        
        self.resource_usage['queued_requests'] = self.request_queue.qsize()
        
        return future
    
    def _get_thread_pool_name(self, priority: int) -> str:
        """Map priority ke thread pool name"""
        if priority == 1:
            return 'critical'
        elif priority == 2:
            return 'high'
        elif priority == 3:
            return 'medium'
        else:
            return 'low'
    
    def _process_request(self, request: ResourceRequest) -> Any:
        """Process individual request dengan resource management"""
        start_time = time.time()
        queue_wait_time = start_time - request.timestamp
        
        try:
            # Get resource connection
            connection = None
            if request.resource_type in self.connection_pools:
                pool = self.connection_pools[request.resource_type]
                connection = pool.get_connection(timeout=request.timeout)
            
            # Update active request count
            self.resource_usage['active_requests'] += 1
            
            # Execute callback dengan connection
            if connection:
                # Pass connection as first argument
                result = request.callback(connection, *request.args, **request.kwargs)
            else:
                result = request.callback(*request.args, **request.kwargs)
            
            # Update metrics
            processing_time = (time.time() - start_time) * 1000
            self._update_performance_metrics(processing_time, queue_wait_time * 1000)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Request processing failed for {request.endpoint_id}: {e}")
            raise
        
        finally:
            # Return connection ke pool
            if connection and request.resource_type in self.connection_pools:
                pool = self.connection_pools[request.resource_type]
                pool.return_connection(connection)
            
            # Update active request count
            self.resource_usage['active_requests'] -= 1
    
    def _update_performance_metrics(self, processing_time_ms: float, queue_wait_time_ms: float):
        """Update performance metrics"""
        self.performance_metrics['total_requests_processed'] += 1
        
        # Update averages (simple moving average)
        total = self.performance_metrics['total_requests_processed']
        
        self.performance_metrics['avg_processing_time_ms'] = (
            (self.performance_metrics['avg_processing_time_ms'] * (total - 1) + processing_time_ms) / total
        )
        
        self.performance_metrics['queue_wait_time_ms'] = (
            (self.performance_metrics['queue_wait_time_ms'] * (total - 1) + queue_wait_time_ms) / total
        )
        
        # Calculate efficiency score
        self._calculate_efficiency_score()
    
    def _calculate_efficiency_score(self):
        """Calculate overall resource efficiency score"""
        # Base score
        score = 100.0
        
        # Penalize high queue wait times
        if self.performance_metrics['queue_wait_time_ms'] > 1000:  # > 1 second
            score -= 20
        elif self.performance_metrics['queue_wait_time_ms'] > 500:  # > 0.5 seconds
            score -= 10
        
        # Penalize high processing times
        if self.performance_metrics['avg_processing_time_ms'] > 5000:  # > 5 seconds
            score -= 15
        elif self.performance_metrics['avg_processing_time_ms'] > 2000:  # > 2 seconds
            score -= 8
        
        # Penalize high resource usage
        if self.resource_usage['memory_percent'] > 85:
            score -= 15
        if self.resource_usage['cpu_percent'] > 80:
            score -= 10
        
        # Penalize full queues
        if self.resource_usage['queued_requests'] > (self.max_queue_size * 0.8):
            score -= 20
        
        self.performance_metrics['resource_efficiency_score'] = max(score, 0)
    
    def _start_resource_monitoring(self):
        """Start background resource monitoring"""
        def monitor_resources():
            while True:
                try:
                    # Update system resource usage
                    self.resource_usage['cpu_percent'] = psutil.cpu_percent(interval=1)
                    self.resource_usage['memory_percent'] = psutil.virtual_memory().percent
                    
                    # Update queue info
                    self.resource_usage['queued_requests'] = self.request_queue.qsize()
                    
                    # Calculate thread pool utilization
                    total_threads = sum(pool._max_workers for pool in self.thread_pools.values())
                    active_threads = sum(len(pool._threads) for pool in self.thread_pools.values())
                    self.resource_usage['thread_pool_utilization'] = (active_threads / total_threads) * 100
                    
                    # Check for auto-scaling opportunities
                    if self.auto_scaling_enabled:
                        self._check_auto_scaling()
                    
                    # Memory cleanup
                    self._perform_memory_cleanup()
                    
                    time.sleep(10)  # Monitor every 10 seconds
                    
                except Exception as e:
                    self.logger.error(f"Resource monitoring error: {e}")
        
        thread = threading.Thread(target=monitor_resources, daemon=True)
        thread.start()
    
    def _check_auto_scaling(self):
        """Check dan perform auto-scaling jika diperlukan"""
        cpu = self.resource_usage['cpu_percent']
        memory = self.resource_usage['memory_percent'] 
        queue_size = self.resource_usage['queued_requests']
        
        # Scale up conditions
        if (cpu > self.cpu_threshold_percent or 
            memory > self.memory_threshold_percent or
            queue_size > (self.max_queue_size * 0.7)):
            
            self._scale_up_resources()
        
        # Scale down conditions
        elif (cpu < 30 and memory < 50 and queue_size < (self.max_queue_size * 0.1)):
            self._scale_down_resources()
    
    def _scale_up_resources(self):
        """Scale up resources"""
        if not self.auto_scaling_enabled:
            return  # Skip scaling when disabled
        self.logger.info("🚀 Auto-scaling UP: Increasing resource capacity")
        
        # Increase thread pool sizes (if not at max)
        for pool_name, pool in self.thread_pools.items():
            if hasattr(pool, '_max_workers') and pool._max_workers < 30:
                # Can't dynamically change ThreadPoolExecutor size easily
                # In production, you'd recreate the pool or use a custom implementation
                pass
        
        # Increase connection pool sizes
        for pool_name, pool in self.connection_pools.items():
            if pool.max_connections < 100:
                pool.max_connections += 10
                self.logger.info(f"Increased {pool_name} connection pool to {pool.max_connections}")
        
        self.performance_metrics['auto_scaling_actions'] += 1
    
    def _scale_down_resources(self):
        """Scale down resources untuk efficiency"""
        self.logger.info("🎯 Auto-scaling DOWN: Optimizing resource usage")
        
        # Decrease connection pool sizes if usage is low
        for pool_name, pool in self.connection_pools.items():
            if pool.max_connections > pool.min_connections + 10:
                pool.max_connections -= 5
                self.logger.info(f"Decreased {pool_name} connection pool to {pool.max_connections}")
        
        self.performance_metrics['auto_scaling_actions'] += 1
    
    def _perform_memory_cleanup(self):
        """Perform periodic memory cleanup"""
        if self.resource_usage['memory_percent'] > 80:
            self.logger.info("🧹 Performing memory cleanup")
            gc.collect()
    
    def get_resource_status(self) -> Dict[str, Any]:
        """Get comprehensive resource status"""
        pool_stats = {}
        for pool_name, pool in self.connection_pools.items():
            pool_stats[pool_name] = pool.get_pool_stats()
        
        thread_pool_stats = {}
        for pool_name, pool in self.thread_pools.items():
            thread_pool_stats[pool_name] = {
                'max_workers': getattr(pool, '_max_workers', 0),
                'active_threads': len(getattr(pool, '_threads', [])),
                'pending_tasks': getattr(pool, '_work_queue', Queue()).qsize()
            }
        
        return {
            'resource_usage': self.resource_usage,
            'performance_metrics': self.performance_metrics,
            'connection_pools': pool_stats,
            'thread_pools': thread_pool_stats,
            'auto_scaling': {
                'enabled': self.auto_scaling_enabled,
                'actions_taken': self.performance_metrics['auto_scaling_actions'],
                'cpu_threshold': self.cpu_threshold_percent,
                'memory_threshold': self.memory_threshold_percent
            },
            'system_capacity': {
                'max_queue_size': self.max_queue_size,
                'current_queue_size': self.request_queue.qsize(),
                'queue_utilization_percent': (self.request_queue.qsize() / self.max_queue_size) * 100
            }
        }

# Singleton instance
_resource_pool = None

def get_intelligent_resource_pool() -> IntelligentResourcePool:
    """Get singleton instance"""
    global _resource_pool
    if _resource_pool is None:
        _resource_pool = IntelligentResourcePool()
    return _resource_pool