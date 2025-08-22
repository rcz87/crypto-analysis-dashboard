#!/usr/bin/env python3
"""
Database Query Optimizer - Advanced database performance optimization
Connection pooling, query caching, index optimization, dan transaction management
"""

import logging
import time
import sqlite3
import threading
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from contextlib import contextmanager
import queue
import hashlib
import json
from collections import defaultdict, deque
import os

logger = logging.getLogger(__name__)

@dataclass
class QueryMetrics:
    query_hash: str
    execution_time_ms: float
    rows_affected: int
    cache_hit: bool
    timestamp: float

@dataclass
class ConnectionPoolConfig:
    min_connections: int = 2
    max_connections: int = 10
    connection_timeout: int = 30
    idle_timeout: int = 300
    retry_attempts: int = 3

class ConnectionPool:
    """
    Advanced database connection pool dengan intelligent management
    """
    
    def __init__(self, database_url: str, config: ConnectionPoolConfig):
        self.database_url = database_url
        self.config = config
        self.available_connections = queue.Queue(maxsize=config.max_connections)
        self.active_connections = {}
        self.connection_metrics = defaultdict(list)
        self.lock = threading.RLock()
        self.logger = logging.getLogger(__name__)
        
        # Initialize minimum connections
        self._initialize_pool()
        
        # Start cleanup thread
        self.cleanup_thread = threading.Thread(target=self._cleanup_idle_connections, daemon=True)
        self.cleanup_thread.start()
        
        self.logger.info(f"💾 Connection Pool initialized: {config.min_connections}-{config.max_connections} connections")
    
    def _initialize_pool(self):
        """Initialize minimum number of connections"""
        for _ in range(self.config.min_connections):
            try:
                conn = self._create_connection()
                self.available_connections.put(conn)
            except Exception as e:
                self.logger.error(f"Error initializing connection: {e}")
    
    def _create_connection(self):
        """Create new database connection using SQLAlchemy"""
        try:
            import sqlalchemy as sa
            # Create engine from database URL with proper connection settings
            engine = sa.create_engine(
                self.database_url, 
                pool_pre_ping=True,
                connect_args={"connect_timeout": self.config.connection_timeout}
            )
            # Return raw connection for pool management
            conn = engine.raw_connection()
            conn.autocommit = True
            return conn
        except Exception as e:
            self.logger.error(f"Failed to create SQLAlchemy connection: {e}")
            # Fallback to sqlite only for development/testing
            if 'sqlite' in self.database_url or ':memory:' in self.database_url:
                conn = sqlite3.connect(':memory:', check_same_thread=False)
                conn.row_factory = sqlite3.Row
                return conn
            else:
                raise Exception(f"Database connection failed: {e}")
    
    @contextmanager
    def get_connection(self):
        """Get connection from pool with automatic cleanup"""
        conn = None
        conn_id = None
        start_time = time.time()
        
        try:
            # Try to get available connection
            try:
                conn = self.available_connections.get(timeout=1)
            except queue.Empty:
                # Create new connection if under max limit
                with self.lock:
                    if len(self.active_connections) < self.config.max_connections:
                        conn = self._create_connection()
                    else:
                        # Wait for available connection
                        conn = self.available_connections.get(timeout=self.config.connection_timeout)
            
            # Track active connection
            conn_id = id(conn)
            with self.lock:
                self.active_connections[conn_id] = {
                    'connection': conn,
                    'acquired_at': time.time(),
                    'thread_id': threading.current_thread().ident
                }
            
            yield conn
            
        except Exception as e:
            self.logger.error(f"Connection error: {e}")
            # Close bad connection
            if conn:
                try:
                    conn.close()
                except:
                    pass
                conn = None
            raise
            
        finally:
            # Return connection to pool or close if error
            if conn and conn_id:
                with self.lock:
                    self.active_connections.pop(conn_id, None)
                
                try:
                    # Check if connection is still usable
                    if hasattr(conn, 'execute'):
                        try:
                            conn.execute('SELECT 1')  # Test query
                        except:
                            raise  # Will be caught by outer except
                    
                    # Return to available pool
                    self.available_connections.put(conn)
                    
                    # Record metrics
                    usage_time = time.time() - start_time
                    self.connection_metrics[conn_id].append(usage_time)
                    
                except:
                    # Close bad connection
                    try:
                        conn.close()
                    except:
                        pass
    
    def _cleanup_idle_connections(self):
        """Cleanup idle connections periodically"""
        while True:
            try:
                time.sleep(60)  # Check every minute
                
                current_time = time.time()
                connections_to_close = []
                
                with self.lock:
                    for conn_id, conn_info in self.active_connections.items():
                        if current_time - conn_info['acquired_at'] > self.config.idle_timeout:
                            connections_to_close.append(conn_id)
                    
                    # Close idle connections
                    for conn_id in connections_to_close:
                        conn_info = self.active_connections.pop(conn_id, None)
                        if conn_info:
                            try:
                                conn_info['connection'].close()
                            except:
                                pass
                
            except Exception as e:
                self.logger.error(f"Error in connection cleanup: {e}")
    
    def get_pool_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics"""
        with self.lock:
            return {
                'available_connections': self.available_connections.qsize(),
                'active_connections': len(self.active_connections),
                'max_connections': self.config.max_connections,
                'min_connections': self.config.min_connections,
                'pool_utilization_percent': (len(self.active_connections) / self.config.max_connections) * 100
            }

class QueryCache:
    """
    Intelligent query result caching dengan TTL dan invalidation
    """
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        self.cache = {}
        self.cache_metadata = {}
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.stats = {'hits': 0, 'misses': 0, 'sets': 0, 'evictions': 0}
        self.lock = threading.RLock()
        self.logger = logging.getLogger(__name__)
        
        self.logger.info(f"🧠 Query Cache initialized: max_size={max_size}, ttl={default_ttl}s")
    
    def _generate_key(self, query: str, params: Optional[Tuple] = None) -> str:
        """Generate cache key untuk query dan parameters"""
        key_data = query.strip().lower()
        if params:
            key_data += str(params)
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, query: str, params: Optional[Tuple] = None) -> Optional[Any]:
        """Get cached query result"""
        cache_key = self._generate_key(query, params)
        
        with self.lock:
            if cache_key in self.cache:
                metadata = self.cache_metadata.get(cache_key, {})
                created_at = metadata.get('created_at', 0)
                ttl = metadata.get('ttl', self.default_ttl)
                
                if time.time() - created_at < ttl:
                    self.stats['hits'] += 1
                    return self.cache[cache_key]
                else:
                    # Expired, remove from cache
                    del self.cache[cache_key]
                    del self.cache_metadata[cache_key]
            
            self.stats['misses'] += 1
            return None
    
    def set(self, query: str, result: Any, params: Optional[Tuple] = None, ttl: Optional[int] = None) -> bool:
        """Cache query result"""
        cache_key = self._generate_key(query, params)
        ttl = ttl or self.default_ttl
        
        with self.lock:
            # Evict oldest entries if cache is full
            if len(self.cache) >= self.max_size:
                self._evict_oldest()
            
            self.cache[cache_key] = result
            self.cache_metadata[cache_key] = {
                'created_at': time.time(),
                'ttl': ttl,
                'query': query[:100],  # Store partial query for debugging
                'result_size': len(str(result))
            }
            
            self.stats['sets'] += 1
            return True
    
    def _evict_oldest(self):
        """Evict oldest cache entries"""
        if not self.cache:
            return
        
        # Find oldest entry
        oldest_key = min(
            self.cache_metadata.keys(),
            key=lambda k: self.cache_metadata[k].get('created_at', 0)
        )
        
        # Remove oldest entry
        self.cache.pop(oldest_key, None)
        self.cache_metadata.pop(oldest_key, None)
        self.stats['evictions'] += 1
    
    def invalidate_pattern(self, pattern: str):
        """Invalidate cache entries menggunakan pattern"""
        with self.lock:
            keys_to_remove = []
            for key, metadata in self.cache_metadata.items():
                if pattern.lower() in metadata.get('query', '').lower():
                    keys_to_remove.append(key)
            
            for key in keys_to_remove:
                self.cache.pop(key, None)
                self.cache_metadata.pop(key, None)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self.lock:
            total_requests = self.stats['hits'] + self.stats['misses']
            hit_rate = (self.stats['hits'] / max(1, total_requests)) * 100
            
            return {
                'hit_rate_percent': round(hit_rate, 2),
                'total_hits': self.stats['hits'],
                'total_misses': self.stats['misses'],
                'total_sets': self.stats['sets'],
                'total_evictions': self.stats['evictions'],
                'cache_size': len(self.cache),
                'max_size': self.max_size,
                'cache_utilization_percent': (len(self.cache) / self.max_size) * 100
            }

class QueryOptimizer:
    """
    Query analysis dan optimization engine
    """
    
    def __init__(self):
        self.slow_queries = deque(maxlen=100)
        self.query_patterns = defaultdict(list)
        self.optimization_suggestions = {}
        self.logger = logging.getLogger(__name__)
        
        self.logger.info("🔍 Query Optimizer initialized")
    
    def analyze_query(self, query: str, execution_time_ms: float, rows_affected: int = 0) -> Dict[str, Any]:
        """Analyze query performance dan provide suggestions"""
        analysis = {
            'query_hash': hashlib.md5(query.encode()).hexdigest()[:8],
            'execution_time_ms': execution_time_ms,
            'rows_affected': rows_affected,
            'issues': [],
            'suggestions': []
        }
        
        # Detect slow queries
        if execution_time_ms > 1000:  # 1 second
            analysis['issues'].append('SLOW_QUERY')
            analysis['suggestions'].append('Consider adding indexes or optimizing WHERE clause')
            
            self.slow_queries.append({
                'query': query[:200],
                'execution_time_ms': execution_time_ms,
                'timestamp': time.time()
            })
        
        # Detect SELECT * queries
        if 'SELECT *' in query.upper():
            analysis['issues'].append('SELECT_ALL')
            analysis['suggestions'].append('Specify only needed columns instead of SELECT *')
        
        # Detect missing WHERE clause in UPDATE/DELETE
        query_upper = query.upper().strip()
        if (query_upper.startswith('UPDATE') or query_upper.startswith('DELETE')) and 'WHERE' not in query_upper:
            analysis['issues'].append('UNSAFE_OPERATION')
            analysis['suggestions'].append('Add WHERE clause to prevent accidental mass operations')
        
        # Detect potential N+1 query pattern
        query_pattern = self._extract_query_pattern(query)
        self.query_patterns[query_pattern].append(time.time())
        
        # Check for repeated patterns in short time
        recent_patterns = [t for t in self.query_patterns[query_pattern] if time.time() - t < 60]
        if len(recent_patterns) > 10:
            analysis['issues'].append('POTENTIAL_N_PLUS_ONE')
            analysis['suggestions'].append('Consider batch queries or eager loading')
        
        return analysis
    
    def _extract_query_pattern(self, query: str) -> str:
        """Extract query pattern untuk N+1 detection"""
        # Remove specific values dan normalize query
        import re
        pattern = re.sub(r'\b\d+\b', 'NUM', query.upper())
        pattern = re.sub(r"'[^']*'", 'STR', pattern)
        pattern = re.sub(r'"[^"]*"', 'STR', pattern)
        return pattern[:100]
    
    def get_slow_queries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent slow queries"""
        return list(self.slow_queries)[-limit:]
    
    def get_optimization_report(self) -> Dict[str, Any]:
        """Generate comprehensive optimization report"""
        return {
            'slow_queries_count': len(self.slow_queries),
            'pattern_analysis': {
                pattern: len(timestamps) 
                for pattern, timestamps in self.query_patterns.items()
            },
            'top_slow_queries': self.get_slow_queries(5),
            'recommendations': [
                'Add database indexes untuk frequent WHERE clauses',
                'Use connection pooling untuk better connection management',
                'Implement query result caching untuk repeated queries',
                'Monitor N+1 query patterns dalam aplikasi',
                'Use EXPLAIN ANALYZE untuk analyze slow queries'
            ]
        }

class DatabaseOptimizer:
    """
    Main Database Optimization Engine
    """
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        
        # Initialize components
        pool_config = ConnectionPoolConfig(
            min_connections=3,
            max_connections=15,
            connection_timeout=30,
            idle_timeout=300
        )
        
        self.connection_pool = ConnectionPool(database_url, pool_config)
        self.query_cache = QueryCache(max_size=500, default_ttl=300)
        self.query_optimizer = QueryOptimizer()
        
        # Metrics tracking
        self.query_metrics = deque(maxlen=1000)
        self.total_queries = 0
        self.total_cache_hits = 0
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("🚀 Database Optimizer initialized")
    
    def execute_query(self, query: str, params: Optional[Tuple] = None, cache_ttl: Optional[int] = None) -> Any:
        """Execute query dengan caching dan optimization"""
        start_time = time.time()
        cache_hit = False
        result = None
        
        try:
            # Try cache first untuk SELECT queries
            if query.strip().upper().startswith('SELECT'):
                cached_result = self.query_cache.get(query, params)
                if cached_result is not None:
                    cache_hit = True
                    result = cached_result
                    self.total_cache_hits += 1
            
            if result is None:
                # Execute query
                with self.connection_pool.get_connection() as conn:
                    if hasattr(conn, 'execute'):
                        # SQLite
                        cursor = conn.execute(query, params or ())
                        if query.strip().upper().startswith('SELECT'):
                            result = cursor.fetchall()
                        else:
                            result = cursor.rowcount
                    else:
                        # PostgreSQL
                        with conn.cursor() as cursor:
                            cursor.execute(query, params)
                            if query.strip().upper().startswith('SELECT'):
                                result = cursor.fetchall()
                            else:
                                result = cursor.rowcount
                
                # Cache SELECT results
                if query.strip().upper().startswith('SELECT') and result is not None:
                    self.query_cache.set(query, result, params, cache_ttl)
            
            execution_time_ms = (time.time() - start_time) * 1000
            
            # Record metrics
            self.total_queries += 1
            metrics = QueryMetrics(
                query_hash=hashlib.md5(query.encode()).hexdigest()[:8],
                execution_time_ms=execution_time_ms,
                rows_affected=len(result) if isinstance(result, list) else result or 0,
                cache_hit=cache_hit,
                timestamp=time.time()
            )
            self.query_metrics.append(metrics)
            
            # Analyze query performance
            if not cache_hit:
                self.query_optimizer.analyze_query(query, execution_time_ms, metrics.rows_affected)
            
            return result
            
        except Exception as e:
            execution_time_ms = (time.time() - start_time) * 1000
            self.logger.error(f"Query execution error: {e}")
            
            # Record failed query metrics
            self.query_metrics.append(QueryMetrics(
                query_hash=hashlib.md5(query.encode()).hexdigest()[:8],
                execution_time_ms=execution_time_ms,
                rows_affected=0,
                cache_hit=False,
                timestamp=time.time()
            ))
            
            raise
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive database performance statistics"""
        if not self.query_metrics:
            return {
                'total_queries': 0,
                'cache_hit_rate_percent': 0.0,
                'avg_execution_time_ms': 0.0,
                'min_execution_time_ms': 0.0,
                'max_execution_time_ms': 0.0,
                'p95_execution_time_ms': 0.0,
                'connection_pool_stats': self.connection_pool.get_pool_stats(),
                'query_cache_stats': self.query_cache.get_stats(),
                'slow_queries': [],
                'optimization_recommendations': [
                    "No query metrics available yet",
                    "Execute some database queries to see statistics",
                    "Database optimizer ready to track performance"
                ]
            }
        
        recent_metrics = list(self.query_metrics)
        
        # Calculate statistics
        total_queries = len(recent_metrics)
        cache_hits = sum(1 for m in recent_metrics if m.cache_hit)
        cache_hit_rate = (cache_hits / total_queries) * 100 if total_queries > 0 else 0
        
        execution_times = [m.execution_time_ms for m in recent_metrics]
        avg_execution_time = sum(execution_times) / len(execution_times)
        max_execution_time = max(execution_times)
        min_execution_time = min(execution_times)
        
        # P95 percentile
        sorted_times = sorted(execution_times)
        p95_index = int(len(sorted_times) * 0.95)
        p95_time = sorted_times[p95_index] if sorted_times else 0
        
        return {
            'total_queries': total_queries,
            'cache_hit_rate_percent': round(cache_hit_rate, 2),
            'avg_execution_time_ms': round(avg_execution_time, 2),
            'min_execution_time_ms': round(min_execution_time, 2),
            'max_execution_time_ms': round(max_execution_time, 2),
            'p95_execution_time_ms': round(p95_time, 2),
            'connection_pool_stats': self.connection_pool.get_pool_stats(),
            'query_cache_stats': self.query_cache.get_stats(),
            'slow_queries': self.query_optimizer.get_slow_queries(3),
            'optimization_recommendations': [
                f"Cache hit rate: {cache_hit_rate:.1f}%" + (" (excellent)" if cache_hit_rate > 80 else " (needs improvement)"),
                f"Avg query time: {avg_execution_time:.1f}ms" + (" (fast)" if avg_execution_time < 100 else " (slow)"),
                f"Connection pool utilization: {self.connection_pool.get_pool_stats()['pool_utilization_percent']:.1f}%"
            ]
        }

# Global instance
database_optimizer = None

def get_database_optimizer(database_url: Optional[str] = None):
    """Get atau create global database optimizer instance"""
    global database_optimizer
    
    if database_optimizer is None and database_url:
        database_optimizer = DatabaseOptimizer(database_url)
    
    return database_optimizer

def init_database_optimizer(database_url: str):
    """Initialize database optimizer dengan specific database URL"""
    global database_optimizer
    database_optimizer = DatabaseOptimizer(database_url)
    return database_optimizer

logger.info("💾 Database Optimization Engine module initialized")