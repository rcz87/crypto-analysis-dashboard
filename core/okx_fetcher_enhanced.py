"""
Enhanced OKX API Fetcher - Enterprise Grade with Request Wrapper
Features: Rate limiting, retry/backoff, consistent auth, TTL cache, standardized responses
"""

import requests
import pandas as pd
import logging
import hmac
import hashlib
import base64
import time
import os
import json
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, List, Tuple
from functools import wraps
import threading
from collections import defaultdict

logger = logging.getLogger(__name__)

class RequestWrapper:
    """
    Robust request wrapper with rate limiting, retry/backoff, and consistent auth
    """
    
    def __init__(self, base_url: str, api_key: str = None, secret_key: str = None, passphrase: str = None):
        self.base_url = base_url
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase
        self.authenticated = bool(api_key and secret_key and passphrase)
        
        # Session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'OKX-Enhanced-Fetcher/2.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
        
        if self.authenticated:
            self.session.headers.update({
                'OK-ACCESS-KEY': self.api_key,
                'OK-ACCESS-PASSPHRASE': self.passphrase,
            })
        
        # Rate limiting
        self.rate_limits = defaultdict(list)  # endpoint -> [timestamps]
        self.rate_lock = threading.Lock()
        self.request_interval = 0.1 if self.authenticated else 0.2  # 10 req/s vs 5 req/s
        self.max_retries = 3
        self.base_backoff = 1.0
        
    def _generate_signature(self, timestamp: str, method: str, request_path: str, body: str = '') -> str:
        """Generate OKX API signature"""
        if not self.secret_key:
            return ''
            
        message = f"{timestamp}{method.upper()}{request_path}{body}"
        signature = base64.b64encode(
            hmac.new(
                self.secret_key.encode('utf-8'),
                message.encode('utf-8'),
                hashlib.sha256
            ).digest()
        ).decode('utf-8')
        return signature
    
    def _rate_limit(self, endpoint: str):
        """Smart rate limiting per endpoint"""
        with self.rate_lock:
            now = time.time()
            # Clean old timestamps (older than 60 seconds)
            self.rate_limits[endpoint] = [
                ts for ts in self.rate_limits[endpoint] 
                if now - ts < 60
            ]
            
            # Check if we need to wait
            if len(self.rate_limits[endpoint]) > 0:
                last_request = self.rate_limits[endpoint][-1]
                elapsed = now - last_request
                if elapsed < self.request_interval:
                    sleep_time = self.request_interval - elapsed
                    time.sleep(sleep_time)
            
            # Record this request
            self.rate_limits[endpoint].append(time.time())
    
    def _build_request_path(self, endpoint: str, params: Dict[str, Any] = None) -> Tuple[str, str]:
        """Build request path and query string for signature"""
        if not params:
            return endpoint, ''
            
        # Sort parameters for consistent signature
        sorted_params = sorted(params.items())
        query_string = '&'.join([f"{k}={v}" for k, v in sorted_params])
        
        if query_string:
            request_path = f"{endpoint}?{query_string}"
        else:
            request_path = endpoint
            
        return request_path, query_string
    
    def request(self, method: str, endpoint: str, params: Dict[str, Any] = None, retries: int = None) -> Dict[str, Any]:
        """
        Enhanced request method with retry/backoff and consistent response format
        
        Returns:
            {
                "ok": True/False,
                "data": response_data,
                "error": error_message,
                "status_code": http_status,
                "timestamp": iso_timestamp
            }
        """
        if retries is None:
            retries = self.max_retries
            
        # Rate limiting
        self._rate_limit(endpoint)
        
        # Build request path
        request_path, query_string = self._build_request_path(endpoint, params)
        
        # Prepare request
        url = f"{self.base_url}{endpoint}"
        headers = self.session.headers.copy()
        
        # Add authentication if available
        if self.authenticated:
            timestamp = str(int(time.time() * 1000))
            body = json.dumps(params) if params and method.upper() == 'POST' else ''
            signature = self._generate_signature(timestamp, method, request_path, body)
            
            headers.update({
                'OK-ACCESS-TIMESTAMP': timestamp,
                'OK-ACCESS-SIGN': signature
            })
        
        # Make request with retry logic
        for attempt in range(retries + 1):
            try:
                if method.upper() == 'GET':
                    response = self.session.get(url, params=params, headers=headers, timeout=30)
                elif method.upper() == 'POST':
                    response = self.session.post(url, json=params, headers=headers, timeout=30)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                # Check response
                response.raise_for_status()
                
                # Parse JSON
                try:
                    data = response.json()
                except json.JSONDecodeError:
                    data = {"raw_response": response.text}
                
                # Return standardized success response
                return {
                    "ok": True,
                    "data": data,
                    "error": None,
                    "status_code": response.status_code,
                    "timestamp": datetime.now().isoformat()
                }
                
            except requests.exceptions.RequestException as e:
                error_msg = f"Request failed (attempt {attempt + 1}/{retries + 1}): {str(e)}"
                logger.warning(error_msg)
                
                if attempt < retries:
                    # Exponential backoff with jitter
                    backoff = self.base_backoff * (2 ** attempt) + (time.time() % 1)
                    time.sleep(min(backoff, 30))  # Max 30 seconds
                    continue
                
                # Final failure
                return {
                    "ok": False,
                    "data": None,
                    "error": error_msg,
                    "status_code": getattr(e.response, 'status_code', 0) if hasattr(e, 'response') else 0,
                    "timestamp": datetime.now().isoformat()
                }
            
            except Exception as e:
                error_msg = f"Unexpected error (attempt {attempt + 1}/{retries + 1}): {str(e)}"
                logger.error(error_msg)
                
                if attempt < retries:
                    backoff = self.base_backoff * (2 ** attempt)
                    time.sleep(min(backoff, 10))
                    continue
                
                return {
                    "ok": False,
                    "data": None,
                    "error": error_msg,
                    "status_code": 0,
                    "timestamp": datetime.now().isoformat()
                }
        
        # This should never be reached
        return {
            "ok": False,
            "data": None,
            "error": "Maximum retries exceeded",
            "status_code": 0,
            "timestamp": datetime.now().isoformat()
        }

class InMemoryCache:
    """
    Thread-safe in-memory cache with TTL
    """
    
    def __init__(self, default_ttl: int = 30):
        self.cache = {}
        self.timestamps = {}
        self.default_ttl = default_ttl
        self.lock = threading.Lock()
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached value if still valid"""
        with self.lock:
            if key not in self.cache:
                return None
                
            # Check TTL
            if time.time() - self.timestamps[key] > self.default_ttl:
                del self.cache[key]
                del self.timestamps[key]
                return None
                
            return self.cache[key]
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set cached value with optional custom TTL"""
        with self.lock:
            self.cache[key] = value
            self.timestamps[key] = time.time()
    
    def clear(self):
        """Clear all cached values"""
        with self.lock:
            self.cache.clear()
            self.timestamps.clear()
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self.lock:
            return {
                "entries": len(self.cache),
                "memory_kb": len(str(self.cache)) / 1024
            }

class OKXFetcherEnhanced:
    """
    Enhanced OKX API fetcher with enterprise-grade features
    """
    
    def __init__(self):
        self.base_url = "https://www.okx.com"
        
        # Load API credentials
        self.api_key = os.getenv('OKX_API_KEY')
        self.secret_key = os.getenv('OKX_SECRET_KEY')
        self.passphrase = os.getenv('OKX_PASSPHRASE')
        
        # Initialize request wrapper
        self.client = RequestWrapper(
            base_url=self.base_url,
            api_key=self.api_key,
            secret_key=self.secret_key,
            passphrase=self.passphrase
        )
        
        # Initialize cache with shorter TTL for authenticated users
        cache_ttl = 15 if self.client.authenticated else 30
        self.cache = InMemoryCache(default_ttl=cache_ttl)
        
        # Symbol normalization rules
        self.symbol_mapping = {
            'BTCUSDT': 'BTC-USDT',
            'ETHUSDT': 'ETH-USDT',
            'BNBUSDT': 'BNB-USDT',
            'ADAUSDT': 'ADA-USDT',
            'SOLUSDT': 'SOL-USDT',
            'DOTUSDT': 'DOT-USDT',
            'LINKUSDT': 'LINK-USDT',
        }
        
        # Timeframe mapping
        self.timeframe_mapping = {
            '1m': '1m', '3m': '3m', '5m': '5m', '15m': '15m', '30m': '30m',
            '1h': '1H', '1H': '1H', '2h': '2H', '2H': '2H', '4h': '4H', '4H': '4H',
            '6h': '6H', '6H': '6H', '8h': '8H', '8H': '8H', '12h': '12H', '12H': '12H',
            '1d': '1D', '1D': '1D', '3d': '3D', '3D': '3D', '1w': '1W', '1W': '1W',
            '1M': '1M', '1y': '1Y', '1Y': '1Y'
        }
        
        logger.info(f"🚀 Enhanced OKX Fetcher initialized (authenticated: {self.client.authenticated})")
    
    def normalize_symbol(self, symbol: str) -> str:
        """Normalize symbol to OKX format (BTC-USDT)"""
        if symbol in self.symbol_mapping:
            return self.symbol_mapping[symbol]
        
        # Handle various formats
        if '-' in symbol:
            return symbol  # Already in correct format
        elif symbol.endswith('USDT'):
            base = symbol[:-4]
            return f"{base}-USDT"
        elif '/' in symbol:
            return symbol.replace('/', '-')
        else:
            return f"{symbol}-USDT"  # Default to USDT pair
    
    def normalize_timeframe(self, timeframe: str) -> str:
        """Normalize timeframe to OKX format"""
        return self.timeframe_mapping.get(timeframe, timeframe)
    
    def get_historical_data(self, symbol: str, timeframe: str, limit: int = 100) -> Dict[str, Any]:
        """
        Get historical OHLCV data with caching and standardized response
        """
        # Normalize inputs
        symbol = self.normalize_symbol(symbol)
        timeframe = self.normalize_timeframe(timeframe)
        
        # Check cache first
        cache_key = f"candles_{symbol}_{timeframe}_{limit}"
        cached_data = self.cache.get(cache_key)
        if cached_data:
            logger.debug(f"Cache hit for {symbol} {timeframe}")
            return cached_data
        
        # Prepare request parameters
        params = {
            'instId': symbol,
            'bar': timeframe,
            'limit': min(limit, 300)  # OKX max limit
        }
        
        # Make request
        response = self.client.request('GET', '/api/v5/market/candles', params)
        
        if not response["ok"]:
            logger.error(f"Failed to fetch candles for {symbol}: {response['error']}")
            return {
                "ok": False,
                "symbol": symbol,
                "timeframe": timeframe,
                "candles": [],
                "count": 0,
                "error": response["error"],
                "timestamp": response["timestamp"]
            }
        
        # Parse OKX response
        api_data = response["data"]
        if api_data.get('code') != '0':
            error_msg = api_data.get('msg', 'Unknown OKX API error')
            logger.error(f"OKX API error for {symbol}: {error_msg}")
            return {
                "ok": False,
                "symbol": symbol,
                "timeframe": timeframe,
                "candles": [],
                "count": 0,
                "error": error_msg,
                "timestamp": response["timestamp"]
            }
        
        # Convert to standardized format
        candles_raw = api_data.get('data', [])
        candles = []
        
        for candle in candles_raw:
            try:
                candles.append({
                    'timestamp': int(candle[0]),
                    'open': float(candle[1]),
                    'high': float(candle[2]),
                    'low': float(candle[3]),
                    'close': float(candle[4]),
                    'volume': float(candle[5]) if candle[5] else 0.0
                })
            except (ValueError, IndexError) as e:
                logger.warning(f"Invalid candle data skipped: {candle} ({e})")
                continue
        
        # Prepare standardized response
        result = {
            "ok": True,
            "symbol": symbol,
            "timeframe": timeframe,
            "candles": candles,
            "count": len(candles),
            "error": None,
            "timestamp": response["timestamp"]
        }
        
        # Cache the result
        self.cache.set(cache_key, result)
        
        logger.info(f"✅ Fetched {len(candles)} candles for {symbol} {timeframe}")
        return result
    
    def get_ticker_data(self, symbol: str) -> Dict[str, Any]:
        """Get real-time ticker data with standardized response"""
        symbol = self.normalize_symbol(symbol)
        
        params = {'instId': symbol}
        response = self.client.request('GET', '/api/v5/market/ticker', params)
        
        if not response["ok"]:
            return {
                "ok": False,
                "symbol": symbol,
                "data": None,
                "error": response["error"],
                "timestamp": response["timestamp"]
            }
        
        api_data = response["data"]
        if api_data.get('code') != '0' or not api_data.get('data'):
            return {
                "ok": False,
                "symbol": symbol,
                "data": None,
                "error": api_data.get('msg', 'No ticker data available'),
                "timestamp": response["timestamp"]
            }
        
        ticker = api_data['data'][0]
        
        return {
            "ok": True,
            "symbol": symbol,
            "data": {
                'last_price': float(ticker['last']),
                'bid_price': float(ticker.get('bidPx', ticker['last'])),
                'ask_price': float(ticker.get('askPx', ticker['last'])),
                'volume_24h': float(ticker.get('vol24h', 0)),
                'change_24h': float(ticker.get('chg24h', 0)),
                'high_24h': float(ticker.get('high24h', ticker['last'])),
                'low_24h': float(ticker.get('low24h', ticker['last'])),
                'timestamp': int(ticker['ts'])
            },
            "error": None,
            "timestamp": response["timestamp"]
        }
    
    def get_order_book(self, symbol: str, depth: int = 20) -> Dict[str, Any]:
        """Get order book data with standardized response"""
        symbol = self.normalize_symbol(symbol)
        
        params = {
            'instId': symbol, 
            'sz': min(depth, 400)  # OKX max depth
        }
        
        response = self.client.request('GET', '/api/v5/market/books', params)
        
        if not response["ok"]:
            return {
                "ok": False,
                "symbol": symbol,
                "data": None,
                "error": response["error"],
                "timestamp": response["timestamp"]
            }
        
        api_data = response["data"]
        if api_data.get('code') != '0' or not api_data.get('data'):
            return {
                "ok": False,
                "symbol": symbol,
                "data": None,
                "error": api_data.get('msg', 'No order book data available'),
                "timestamp": response["timestamp"]
            }
        
        book = api_data['data'][0]
        
        return {
            "ok": True,
            "symbol": symbol,
            "data": {
                'bids': [[float(bid[0]), float(bid[1])] for bid in book.get('bids', [])],
                'asks': [[float(ask[0]), float(ask[1])] for ask in book.get('asks', [])],
                'timestamp': int(book['ts'])
            },
            "error": None,
            "timestamp": response["timestamp"]
        }
    
    def test_connection(self) -> Dict[str, Any]:
        """Test OKX API connection"""
        try:
            result = self.get_historical_data('BTC-USDT', '1H', 2)
            
            if result["ok"]:
                return {
                    "status": "connected",
                    "message": "OKX API connection successful",
                    "candles_received": result["count"],
                    "authenticated": self.client.authenticated
                }
            else:
                return {
                    "status": "error",
                    "message": f"OKX API connection failed: {result['error']}",
                    "authenticated": self.client.authenticated
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"Connection test failed: {str(e)}",
                "authenticated": self.client.authenticated
            }
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return self.cache.stats()

# Backward compatibility
OKXFetcher = OKXFetcherEnhanced