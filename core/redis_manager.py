"""
Redis Manager untuk caching dan deduplication
"""
import redis
import os
import json
import logging
from typing import Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class RedisManager:
    def __init__(self):
        """Initialize Redis connection"""
        try:
            # Use environment variable or default to localhost
            redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
            
            # Try to connect to Redis
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            
            # Test connection
            self.redis_client.ping()
            self.connected = True
            logger.info("✅ Redis connected successfully")
            
        except Exception as e:
            logger.warning(f"⚠️ Redis connection failed: {e}. Using in-memory cache.")
            self.redis_client = None
            self.connected = False
            # In-memory fallback
            self.memory_cache = {}
            self.signal_cache = {}
    
    def is_signal_sent(self, signal_id: str) -> bool:
        """Check if signal already sent"""
        if not self.connected:
            # Use in-memory cache
            self._cleanup_expired_signals()
            return signal_id in self.signal_cache
            
        try:
            return bool(self.redis_client.get(f"signal:{signal_id}"))
        except Exception as e:
            logger.error(f"Redis error checking signal: {e}")
            # Fallback to in-memory
            self._cleanup_expired_signals()
            return signal_id in self.signal_cache
    
    def mark_signal_sent(self, signal_id: str, expire_seconds: int = 3600):
        """Mark signal as sent with expiration"""
        if not self.connected:
            # Use in-memory cache
            self.signal_cache[signal_id] = {
                'timestamp': datetime.now().isoformat(),
                'sent': True,
                'expire_at': datetime.now().timestamp() + expire_seconds
            }
            logger.info(f"✅ Signal {signal_id} marked as sent (in-memory)")
            return
            
        try:
            key = f"signal:{signal_id}"
            value = {
                'timestamp': datetime.now().isoformat(),
                'sent': True
            }
            self.redis_client.setex(
                key, 
                expire_seconds, 
                json.dumps(value)
            )
            logger.info(f"✅ Signal {signal_id} marked as sent")
        except Exception as e:
            logger.error(f"Redis error marking signal: {e}")
            # Fallback to in-memory
            self.signal_cache[signal_id] = {
                'timestamp': datetime.now().isoformat(),
                'sent': True,
                'expire_at': datetime.now().timestamp() + expire_seconds
            }
    
    def generate_signal_id(self, symbol: str, signal_type: str, entry_price: float) -> str:
        """Generate unique signal ID"""
        # Create unique ID based on symbol, signal type, and price range
        price_range = int(entry_price / 100) * 100  # Round to nearest 100
        timestamp = datetime.now().strftime("%Y%m%d%H")  # Hourly bucket
        
        return f"{symbol}:{signal_type}:{price_range}:{timestamp}"
    
    def get_cache(self, key: str) -> Optional[Any]:
        """Get cached value"""
        if not self.connected:
            return None
            
        try:
            value = self.redis_client.get(f"cache:{key}")
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Redis error getting cache: {e}")
            return None
    
    def set_cache(self, key: str, value: Any, expire_seconds: int = 300):
        """Set cache value with expiration"""
        if not self.connected:
            return
            
        try:
            cache_key = f"cache:{key}"
            self.redis_client.setex(
                cache_key,
                expire_seconds,
                json.dumps(value)
            )
        except Exception as e:
            logger.error(f"Redis error setting cache: {e}")
    
    def clear_signal_history(self, pattern: str = "signal:*"):
        """Clear signal history (for testing)"""
        if not self.connected:
            return
            
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
                logger.info(f"Cleared {len(keys)} signal records")
        except Exception as e:
            logger.error(f"Redis error clearing history: {e}")

    def _cleanup_expired_signals(self):
        """Clean up expired signals from in-memory cache"""
        if not hasattr(self, 'signal_cache'):
            return
            
        current_time = datetime.now().timestamp()
        expired_keys = []
        
        for signal_id, data in self.signal_cache.items():
            if 'expire_at' in data and data['expire_at'] < current_time:
                expired_keys.append(signal_id)
        
        for key in expired_keys:
            del self.signal_cache[key]
            logger.debug(f"Cleaned expired signal: {key}")

# Singleton instance
redis_manager = RedisManager()