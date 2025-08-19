#!/usr/bin/env python3
"""
Advanced Cache Manager - Sistem caching yang canggih dengan TTL, LRU, dan compression
"""

import logging
import time
import json
import gzip
import pickle
import hashlib
from typing import Dict, Any, Optional, List, Tuple
from collections import OrderedDict
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from threading import Lock
import os

logger = logging.getLogger(__name__)

@dataclass
class CacheEntry:
    """Entry cache dengan metadata lengkap"""
    data: Any
    created_at: float
    last_accessed: float
    access_count: int
    ttl: float
    compressed: bool = False
    size_bytes: int = 0
    cache_key: str = ""

class LRUCache:
    """LRU Cache dengan TTL support dan automatic cleanup"""
    
    def __init__(self, max_size: int = 1000, default_ttl: float = 300):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.lock = Lock()
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'total_size_bytes': 0,
            'last_cleanup': time.time()
        }
        
    def _calculate_size(self, data: Any) -> int:
        """Calculate approximate size of data"""
        try:
            if isinstance(data, (str, bytes)):
                return len(data)
            elif isinstance(data, dict):
                return len(json.dumps(data, default=str))
            else:
                return len(pickle.dumps(data))
        except:
            return 100  # Default size estimate
    
    def _compress_data(self, data: Any) -> Tuple[bytes, bool]:
        """Compress data if beneficial"""
        try:
            serialized = pickle.dumps(data)
            if len(serialized) > 1024:  # Only compress if >1KB
                compressed = gzip.compress(serialized)
                if len(compressed) < len(serialized) * 0.8:  # 20% compression benefit
                    return compressed, True
            return serialized, False
        except:
            return pickle.dumps(data), False
    
    def _decompress_data(self, data: bytes, compressed: bool) -> Any:
        """Decompress data if needed"""
        try:
            if compressed:
                data = gzip.decompress(data)
            return pickle.loads(data)
        except:
            return None
    
    def get(self, key: str) -> Optional[Any]:
        """Get item from cache"""
        with self.lock:
            if key not in self.cache:
                self.stats['misses'] += 1
                return None
                
            entry = self.cache[key]
            
            # Check TTL
            if time.time() - entry.created_at > entry.ttl:
                del self.cache[key]
                self.stats['misses'] += 1
                return None
            
            # Update access info
            entry.last_accessed = time.time()
            entry.access_count += 1
            
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            
            self.stats['hits'] += 1
            
            # Decompress if needed
            if isinstance(entry.data, bytes):
                return self._decompress_data(entry.data, entry.compressed)
            return entry.data
    
    def set(self, key: str, value: Any, ttl: Optional[float] = None) -> bool:
        """Set item in cache"""
        with self.lock:
            ttl = ttl or self.default_ttl
            
            # Compress data if beneficial
            compressed_data, is_compressed = self._compress_data(value)
            data_size = len(compressed_data) if isinstance(compressed_data, bytes) else self._calculate_size(value)
            
            # Create cache entry
            entry = CacheEntry(
                data=compressed_data if is_compressed else value,
                created_at=time.time(),
                last_accessed=time.time(),
                access_count=1,
                ttl=ttl,
                compressed=is_compressed,
                size_bytes=data_size,
                cache_key=key
            )
            
            # Remove existing entry if present
            if key in self.cache:
                old_entry = self.cache[key]
                self.stats['total_size_bytes'] -= old_entry.size_bytes
                del self.cache[key]
            
            # Add new entry
            self.cache[key] = entry
            self.stats['total_size_bytes'] += data_size
            
            # Evict if necessary
            while len(self.cache) > self.max_size:
                oldest_key = next(iter(self.cache))
                oldest_entry = self.cache[oldest_key]
                self.stats['total_size_bytes'] -= oldest_entry.size_bytes
                del self.cache[oldest_key]
                self.stats['evictions'] += 1
            
            return True
    
    def delete(self, key: str) -> bool:
        """Delete item from cache"""
        with self.lock:
            if key in self.cache:
                entry = self.cache[key]
                self.stats['total_size_bytes'] -= entry.size_bytes
                del self.cache[key]
                return True
            return False
    
    def clear(self):
        """Clear all cache"""
        with self.lock:
            self.cache.clear()
            self.stats['total_size_bytes'] = 0
    
    def cleanup_expired(self) -> int:
        """Clean up expired entries"""
        with self.lock:
            current_time = time.time()
            expired_keys = []
            
            for key, entry in self.cache.items():
                if current_time - entry.created_at > entry.ttl:
                    expired_keys.append(key)
            
            for key in expired_keys:
                entry = self.cache[key]
                self.stats['total_size_bytes'] -= entry.size_bytes
                del self.cache[key]
            
            self.stats['last_cleanup'] = current_time
            return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self.lock:
            hit_rate = self.stats['hits'] / (self.stats['hits'] + self.stats['misses']) if (self.stats['hits'] + self.stats['misses']) > 0 else 0
            
            return {
                'size': len(self.cache),
                'max_size': self.max_size,
                'hits': self.stats['hits'],
                'misses': self.stats['misses'],
                'hit_rate': f"{hit_rate:.2%}",
                'evictions': self.stats['evictions'],
                'total_size_bytes': self.stats['total_size_bytes'],
                'total_size_mb': f"{self.stats['total_size_bytes'] / 1024 / 1024:.2f}",
                'last_cleanup': datetime.fromtimestamp(self.stats['last_cleanup']).isoformat()
            }

class AdvancedCacheManager:
    """Advanced cache manager dengan multiple cache pools"""
    
    def __init__(self):
        # Different cache pools for different data types
        self.market_data_cache = LRUCache(max_size=500, default_ttl=30)     # Market data: 30s TTL
        self.analysis_cache = LRUCache(max_size=200, default_ttl=300)       # Analysis: 5min TTL  
        self.api_response_cache = LRUCache(max_size=1000, default_ttl=60)   # API responses: 1min TTL
        self.user_session_cache = LRUCache(max_size=100, default_ttl=3600)  # User sessions: 1h TTL
        
        self.cache_pools = {
            'market_data': self.market_data_cache,
            'analysis': self.analysis_cache,
            'api_response': self.api_response_cache,
            'user_session': self.user_session_cache
        }
        
        logger.info("🗄️ Advanced Cache Manager initialized with 4 pools")
    
    def _generate_cache_key(self, pool: str, identifier: str, params: Optional[Dict] = None) -> str:
        """Generate unique cache key"""
        key_parts = [pool, identifier]
        if params:
            # Sort params for consistent keys
            param_str = json.dumps(params, sort_keys=True, default=str)
            key_parts.append(hashlib.md5(param_str.encode()).hexdigest()[:8])
        return ":".join(key_parts)
    
    def get(self, pool: str, identifier: str, params: Optional[Dict] = None) -> Optional[Any]:
        """Get item from specific cache pool"""
        if pool not in self.cache_pools:
            logger.warning(f"Unknown cache pool: {pool}")
            return None
            
        cache_key = self._generate_cache_key(pool, identifier, params)
        return self.cache_pools[pool].get(cache_key)
    
    def set(self, pool: str, identifier: str, data: Any, ttl: Optional[float] = None, params: Optional[Dict] = None) -> bool:
        """Set item in specific cache pool"""
        if pool not in self.cache_pools:
            logger.warning(f"Unknown cache pool: {pool}")
            return False
            
        cache_key = self._generate_cache_key(pool, identifier, params)
        return self.cache_pools[pool].set(cache_key, data, ttl)
    
    def delete(self, pool: str, identifier: str, params: Optional[Dict] = None) -> bool:
        """Delete item from specific cache pool"""
        if pool not in self.cache_pools:
            return False
            
        cache_key = self._generate_cache_key(pool, identifier, params)
        return self.cache_pools[pool].delete(cache_key)
    
    def clear_pool(self, pool: str):
        """Clear specific cache pool"""
        if pool in self.cache_pools:
            self.cache_pools[pool].clear()
            logger.info(f"🗑️ Cleared cache pool: {pool}")
    
    def clear_all(self):
        """Clear all cache pools"""
        for pool in self.cache_pools.values():
            pool.clear()
        logger.info("🗑️ Cleared all cache pools")
    
    def cleanup_all_expired(self) -> Dict[str, int]:
        """Clean up expired entries in all pools"""
        results = {}
        for pool_name, pool in self.cache_pools.items():
            expired_count = pool.cleanup_expired()
            results[pool_name] = expired_count
        
        total_expired = sum(results.values())
        if total_expired > 0:
            logger.info(f"🧹 Cleaned up {total_expired} expired cache entries")
        
        return results
    
    def get_comprehensive_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics for all pools"""
        stats = {
            'pools': {},
            'total_entries': 0,
            'total_size_bytes': 0,
            'overall_hit_rate': 0.0,
            'timestamp': datetime.now().isoformat()
        }
        
        total_hits = 0
        total_requests = 0
        
        for pool_name, pool in self.cache_pools.items():
            pool_stats = pool.get_stats()
            stats['pools'][pool_name] = pool_stats
            stats['total_entries'] += pool_stats['size']
            stats['total_size_bytes'] += pool_stats['total_size_bytes']
            total_hits += pool_stats['hits']
            total_requests += pool_stats['hits'] + pool_stats['misses']
        
        if total_requests > 0:
            stats['overall_hit_rate'] = f"{total_hits / total_requests:.2%}"
        
        stats['total_size_mb'] = f"{stats['total_size_bytes'] / 1024 / 1024:.2f}"
        
        return stats

# Global cache manager instance
cache_manager = AdvancedCacheManager()

def get_cache_manager() -> AdvancedCacheManager:
    """Get global cache manager instance"""
    return cache_manager

logger.info("🗄️ Advanced Cache Manager module initialized")