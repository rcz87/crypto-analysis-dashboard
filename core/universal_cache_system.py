#!/usr/bin/env python3
"""
Universal Cache System - Priority 1 Implementation
Menggabungkan AILatencyOptimizer dan AdvancedCacheManager dalam satu sistem terpusat
untuk menangani 35+ endpoints dengan performa optimal dan rate limit 120 req/min
"""

import hashlib
import json
import time
import gzip
import pickle
import asyncio
from typing import Dict, Any, Optional, Tuple, List, Union
from datetime import datetime, timedelta
from collections import OrderedDict
from dataclasses import dataclass
from threading import Lock
from concurrent.futures import ThreadPoolExecutor
import logging

logger = logging.getLogger(__name__)

@dataclass
class UniversalCacheEntry:
    """Universal cache entry dengan metadata lengkap"""
    data: Any
    created_at: float
    last_accessed: float
    access_count: int
    ttl: float
    cache_type: str  # 'ai', 'market', 'ml', 'api'
    compressed: bool = False
    size_bytes: int = 0
    priority: int = 1  # 1=high, 2=medium, 3=low


class UniversalCacheSystem:
    """
    Sistem caching universal yang menangani:
    - AI reasoning cache (dengan latency <3s)
    - Market data cache (untuk OKX API rate limit)
    - ML prediction cache (untuk ensemble models)
    - General API response cache
    - Request deduplication
    - Intelligent TTL dan compression
    """
    
    def __init__(self, 
                 max_total_size: int = 5000,
                 default_ttl_minutes: int = 30):
        
        # Cache pools by type
        self.caches = {
            'ai': OrderedDict(),        # AI reasoning responses
            'market': OrderedDict(),    # Market data from OKX
            'ml': OrderedDict(),        # ML predictions
            'api': OrderedDict()        # General API responses
        }
        
        # Configuration
        self.max_total_size = max_total_size
        self.default_ttl = timedelta(minutes=default_ttl_minutes)
        self.lock = Lock()
        
        # AI-specific features (from AILatencyOptimizer)
        self.preview_cache = {}
        self.pending_requests = {}
        self.executor = ThreadPoolExecutor(max_workers=6)
        
        # Performance metrics
        self.metrics = {
            'total_hits': 0,
            'total_misses': 0,
            'cache_hits_by_type': {'ai': 0, 'market': 0, 'ml': 0, 'api': 0},
            'cache_misses_by_type': {'ai': 0, 'market': 0, 'ml': 0, 'api': 0},
            'preview_served': 0,
            'requests_deduplicated': 0,
            'avg_latency_ms': 0,
            'total_size_bytes': 0,
            'evictions': 0,
            'compressions': 0
        }
        
        # TTL by cache type (optimization for different data types)
        self.ttl_by_type = {
            'ai': timedelta(minutes=60),      # AI reasoning dapat cached lebih lama
            'market': timedelta(minutes=5),   # Market data perlu fresh
            'ml': timedelta(minutes=30),      # ML predictions medium TTL
            'api': timedelta(minutes=15)      # General API medium TTL
        }
        
        self.logger = logging.getLogger(f"{__name__}.UniversalCacheSystem")
        self.logger.info("🚀 Universal Cache System initialized - Handling AI, Market, ML, and API caching")
    
    def _generate_cache_key(self, request_data: Dict[str, Any], 
                           cache_type: str = 'api') -> str:
        """Generate unique cache key with type prefix"""
        # Add cache type to key for better organization
        key_data = {'type': cache_type, 'data': request_data}
        sorted_data = json.dumps(key_data, sort_keys=True, default=str)
        hash_key = hashlib.md5(sorted_data.encode()).hexdigest()
        return f"{cache_type}:{hash_key}"
    
    def _calculate_size(self, data: Any) -> int:
        """Calculate data size for memory management"""
        try:
            if isinstance(data, (str, bytes)):
                return len(data)
            elif isinstance(data, dict):
                return len(json.dumps(data, default=str))
            return len(pickle.dumps(data))
        except:
            return 100
    
    def _should_compress(self, data: Any) -> bool:
        """Determine if data should be compressed"""
        try:
            size = self._calculate_size(data)
            # Compress if >2KB and likely to benefit (text/JSON heavy)
            return size > 2048 and isinstance(data, (dict, list, str))
        except:
            return False
    
    def _compress_data(self, data: Any) -> Tuple[Union[bytes, Any], bool]:
        """Compress data if beneficial"""
        if not self._should_compress(data):
            return data, False
            
        try:
            serialized = pickle.dumps(data)
            compressed = gzip.compress(serialized)
            
            # Only keep compression if >25% size reduction
            if len(compressed) < len(serialized) * 0.75:
                self.metrics['compressions'] += 1
                return compressed, True
            return data, False
        except:
            return data, False
    
    def _decompress_data(self, data: Union[bytes, Any], compressed: bool) -> Any:
        """Decompress data if needed"""
        if not compressed:
            return data
            
        try:
            decompressed = gzip.decompress(data)
            return pickle.loads(decompressed)
        except:
            self.logger.warning("Failed to decompress cache data")
            return None
    
    def _is_entry_valid(self, entry: UniversalCacheEntry) -> bool:
        """Check if cache entry is still valid"""
        now = time.time()
        ttl_seconds = self.ttl_by_type.get(
            entry.cache_type, 
            self.default_ttl
        ).total_seconds()
        
        return (now - entry.created_at) < ttl_seconds
    
    def _cleanup_expired(self, cache_type: str = None):
        """Clean up expired entries"""
        with self.lock:
            types_to_clean = [cache_type] if cache_type else self.caches.keys()
            
            for ctype in types_to_clean:
                cache = self.caches[ctype]
                expired_keys = []
                
                for key, entry in cache.items():
                    if not self._is_entry_valid(entry):
                        expired_keys.append(key)
                
                for key in expired_keys:
                    del cache[key]
                    self.metrics['evictions'] += 1
    
    def _evict_lru(self, target_type: str):
        """Evict least recently used entries when cache full"""
        with self.lock:
            cache = self.caches[target_type]
            if not cache:
                return
            
            # Find LRU entry
            lru_key = min(cache.keys(), 
                         key=lambda k: cache[k].last_accessed)
            del cache[lru_key]
            self.metrics['evictions'] += 1
    
    def get(self, request_data: Dict[str, Any], 
            cache_type: str = 'api') -> Optional[Any]:
        """Get cached data"""
        cache_key = self._generate_cache_key(request_data, cache_type)
        
        with self.lock:
            cache = self.caches[cache_type]
            
            if cache_key not in cache:
                self.metrics['total_misses'] += 1
                self.metrics['cache_misses_by_type'][cache_type] += 1
                return None
            
            entry = cache[cache_key]
            
            # Check validity
            if not self._is_entry_valid(entry):
                del cache[cache_key]
                self.metrics['total_misses'] += 1
                self.metrics['cache_misses_by_type'][cache_type] += 1
                return None
            
            # Update access info
            entry.last_accessed = time.time()
            entry.access_count += 1
            
            # Move to end (LRU)
            cache.move_to_end(cache_key)
            
            # Update metrics
            self.metrics['total_hits'] += 1
            self.metrics['cache_hits_by_type'][cache_type] += 1
            
            # Decompress if needed
            return self._decompress_data(entry.data, entry.compressed)
    
    def set(self, request_data: Dict[str, Any], 
            response_data: Any,
            cache_type: str = 'api',
            priority: int = 1,
            custom_ttl: Optional[timedelta] = None) -> bool:
        """Set cached data"""
        cache_key = self._generate_cache_key(request_data, cache_type)
        
        # Compress if beneficial
        compressed_data, is_compressed = self._compress_data(response_data)
        data_size = self._calculate_size(compressed_data)
        
        with self.lock:
            cache = self.caches[cache_type]
            
            # Check if cache is full and evict if needed
            if len(cache) >= (self.max_total_size // 4):  # Split equally between types
                self._evict_lru(cache_type)
            
            # Create cache entry
            entry = UniversalCacheEntry(
                data=compressed_data,
                created_at=time.time(),
                last_accessed=time.time(),
                access_count=1,
                ttl=(custom_ttl or self.ttl_by_type[cache_type]).total_seconds(),
                cache_type=cache_type,
                compressed=is_compressed,
                size_bytes=data_size,
                priority=priority
            )
            
            cache[cache_key] = entry
            self.metrics['total_size_bytes'] += data_size
            
            return True
    
    # AI-specific optimized methods (from AILatencyOptimizer)
    async def get_ai_optimized(self, request_data: Dict[str, Any],
                              ai_function: callable,
                              use_preview: bool = True) -> Tuple[Dict[str, Any], float]:
        """
        AI-optimized caching with <3s latency target
        """
        start_time = time.time()
        
        # Check main AI cache first
        cached_response = self.get(request_data, 'ai')
        if cached_response:
            latency = (time.time() - start_time) * 1000
            self.logger.info(f"✅ AI Cache hit - Latency: {latency:.1f}ms")
            return cached_response, latency
        
        cache_key = self._generate_cache_key(request_data, 'ai')
        
        # Check pending requests (deduplication)
        if cache_key in self.pending_requests:
            self.logger.info("⏳ Deduplicating AI request")
            self.metrics['requests_deduplicated'] += 1
            try:
                response = await asyncio.wait_for(
                    self.pending_requests[cache_key], timeout=30
                )
                latency = (time.time() - start_time) * 1000
                return response, latency
            except asyncio.TimeoutError:
                pass
        
        # Check preview cache for fast response
        if use_preview and cache_key in self.preview_cache:
            preview_entry = self.preview_cache[cache_key]
            if self._is_entry_valid(preview_entry):
                self.metrics['preview_served'] += 1
                
                # Start background full analysis
                asyncio.create_task(self._background_ai_analysis(
                    cache_key, request_data, ai_function
                ))
                
                latency = (time.time() - start_time) * 1000
                self.logger.info(f"🚀 AI Preview served - Latency: {latency:.1f}ms")
                return preview_entry.data, latency
        
        # Generate new AI response
        future = asyncio.Future()
        self.pending_requests[cache_key] = future
        
        try:
            # Run AI function in thread pool
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                self.executor, ai_function, request_data
            )
            
            # Cache the response
            self.set(request_data, response, 'ai', priority=1)
            
            # Also create preview for future requests
            preview_response = self._create_ai_preview(response)
            self.preview_cache[cache_key] = UniversalCacheEntry(
                data=preview_response,
                created_at=time.time(),
                last_accessed=time.time(),
                access_count=1,
                ttl=3600,  # 1 hour for preview
                cache_type='ai_preview'
            )
            
            # Complete pending request
            future.set_result(response)
            
            latency = (time.time() - start_time) * 1000
            self.logger.info(f"🧠 New AI response generated - Latency: {latency:.1f}ms")
            
            return response, latency
            
        except Exception as e:
            self.logger.error(f"AI function failed: {e}")
            future.set_exception(e)
            raise
        finally:
            self.pending_requests.pop(cache_key, None)
    
    async def _background_ai_analysis(self, cache_key: str, 
                                     request_data: Dict[str, Any],
                                     ai_function: callable):
        """Background full AI analysis after preview served"""
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                self.executor, ai_function, request_data
            )
            self.set(request_data, response, 'ai', priority=1)
            self.logger.info("🔄 Background AI analysis completed")
        except Exception as e:
            self.logger.warning(f"Background AI analysis failed: {e}")
    
    def _create_ai_preview(self, full_response: Dict[str, Any]) -> Dict[str, Any]:
        """Create lightweight preview from full AI response"""
        # Extract essential info for quick preview
        preview = {
            'signal': full_response.get('signal'),
            'confidence': full_response.get('confidence'),
            'current_price': full_response.get('current_price'),
            'reasoning_summary': full_response.get('reasoning', '')[:200] + '...',
            'preview': True,
            'timestamp': full_response.get('timestamp')
        }
        return preview
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        total_entries = sum(len(cache) for cache in self.caches.values())
        hit_rate = (
            self.metrics['total_hits'] / 
            max(self.metrics['total_hits'] + self.metrics['total_misses'], 1)
        ) * 100
        
        return {
            'total_entries': total_entries,
            'entries_by_type': {k: len(v) for k, v in self.caches.items()},
            'hit_rate_percent': round(hit_rate, 2),
            'metrics': self.metrics,
            'memory_usage_mb': round(self.metrics['total_size_bytes'] / (1024*1024), 2),
            'preview_cache_size': len(self.preview_cache),
            'pending_requests': len(self.pending_requests)
        }
    
    def clear_cache(self, cache_type: Optional[str] = None):
        """Clear cache by type or all"""
        with self.lock:
            if cache_type:
                self.caches[cache_type].clear()
                self.logger.info(f"🧹 Cleared {cache_type} cache")
            else:
                for cache in self.caches.values():
                    cache.clear()
                self.preview_cache.clear()
                self.pending_requests.clear()
                self.logger.info("🧹 Cleared all caches")


# Singleton instance
_universal_cache = None

def get_universal_cache() -> UniversalCacheSystem:
    """Get singleton instance of universal cache"""
    global _universal_cache
    if _universal_cache is None:
        _universal_cache = UniversalCacheSystem()
    return _universal_cache


def cache_market_data(symbol: str, timeframe: str, data: Any, ttl_minutes: int = 5):
    """Convenience function for caching market data"""
    cache = get_universal_cache()
    request_data = {'symbol': symbol, 'timeframe': timeframe, 'type': 'market_data'}
    cache.set(request_data, data, 'market', priority=2, 
              custom_ttl=timedelta(minutes=ttl_minutes))


def get_cached_market_data(symbol: str, timeframe: str) -> Optional[Any]:
    """Convenience function for getting cached market data"""
    cache = get_universal_cache()
    request_data = {'symbol': symbol, 'timeframe': timeframe, 'type': 'market_data'}
    return cache.get(request_data, 'market')


def cache_ml_prediction(model_name: str, input_data: Dict, prediction: Any):
    """Convenience function for caching ML predictions"""
    cache = get_universal_cache()
    request_data = {'model': model_name, 'input_hash': hashlib.md5(
        json.dumps(input_data, sort_keys=True).encode()).hexdigest()}
    cache.set(request_data, prediction, 'ml', priority=2)


def get_cached_ml_prediction(model_name: str, input_data: Dict) -> Optional[Any]:
    """Convenience function for getting cached ML predictions"""
    cache = get_universal_cache()
    request_data = {'model': model_name, 'input_hash': hashlib.md5(
        json.dumps(input_data, sort_keys=True).encode()).hexdigest()}
    return cache.get(request_data, 'ml')