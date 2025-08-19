#!/usr/bin/env python3
"""
Multi-Source Data Manager - Backup data sources dan data quality management
Mengelola multiple data sources untuk reliability dan redundancy
"""

import logging
import requests
import time
import json
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)

class DataSource(Enum):
    OKX = "okx"
    BINANCE = "binance"
    BYBIT = "bybit"
    COINBASE = "coinbase"
    KUCOIN = "kucoin"

@dataclass
class DataSourceStatus:
    source: DataSource
    is_available: bool
    latency_ms: float
    error_rate: float
    last_successful_call: float
    quality_score: float

@dataclass
class MarketDataResponse:
    source: DataSource
    data: Dict[str, Any]
    timestamp: float
    latency_ms: float
    is_primary: bool
    quality_score: float

class MultiSourceDataManager:
    """
    Manager untuk multiple data sources dengan failover capabilities
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.primary_source = DataSource.OKX
        self.backup_sources = [DataSource.BINANCE, DataSource.BYBIT, DataSource.COINBASE]
        
        # Data source configurations
        self.source_configs = {
            DataSource.OKX: {
                'base_url': 'https://www.okx.com',
                'endpoints': {
                    'ticker': '/api/v5/market/ticker',
                    'kline': '/api/v5/market/candles',
                    'orderbook': '/api/v5/market/books'
                },
                'rate_limit': 0.1,  # 10 requests per second
                'timeout': 5
            },
            DataSource.BINANCE: {
                'base_url': 'https://api.binance.com',
                'endpoints': {
                    'ticker': '/api/v3/ticker/24hr',
                    'kline': '/api/v3/klines',
                    'orderbook': '/api/v3/depth'
                },
                'rate_limit': 0.1,
                'timeout': 5
            },
            DataSource.BYBIT: {
                'base_url': 'https://api.bybit.com',
                'endpoints': {
                    'ticker': '/v5/market/tickers',
                    'kline': '/v5/market/kline',
                    'orderbook': '/v5/market/orderbook'
                },
                'rate_limit': 0.1,
                'timeout': 5
            },
            DataSource.COINBASE: {
                'base_url': 'https://api.pro.coinbase.com',
                'endpoints': {
                    'ticker': '/products/{symbol}/ticker',
                    'kline': '/products/{symbol}/candles',
                    'orderbook': '/products/{symbol}/book'
                },
                'rate_limit': 0.1,
                'timeout': 5
            }
        }
        
        # Track source performance
        self.source_stats = {}
        for source in DataSource:
            self.source_stats[source] = {
                'total_requests': 0,
                'successful_requests': 0,
                'failed_requests': 0,
                'total_latency': 0,
                'last_request_time': 0,
                'consecutive_failures': 0,
                'last_successful_call': 0
            }
        
        # Failover settings
        self.max_consecutive_failures = 3
        self.failover_timeout = 300  # 5 minutes before retry failed source
        
        # Data cache untuk backup
        self.data_cache = {}
        self.cache_ttl = 60  # 1 minute cache
        
        self.logger.info("🔄 Multi-Source Data Manager initialized")
    
    def get_market_data(self, 
                       symbol: str, 
                       data_type: str = 'ticker',
                       force_source: Optional[DataSource] = None) -> Optional[MarketDataResponse]:
        """
        Get market data dengan automatic failover
        """
        if force_source:
            sources_to_try = [force_source]
        else:
            sources_to_try = self._get_prioritized_sources()
        
        for source in sources_to_try:
            try:
                # Check if source is currently in failover mode
                if self._is_source_in_failover(source):
                    self.logger.warning(f"Source {source.value} in failover mode, skipping")
                    continue
                
                # Attempt to get data
                data_response = self._fetch_from_source(source, symbol, data_type)
                
                if data_response:
                    self._update_source_stats(source, success=True, latency=data_response.latency_ms)
                    self.logger.info(f"✅ Data fetched from {source.value} for {symbol}")
                    
                    # Cache successful response
                    self._cache_data(symbol, data_type, data_response)
                    
                    return data_response
                else:
                    self._update_source_stats(source, success=False)
                    
            except Exception as e:
                self.logger.error(f"Error fetching from {source.value}: {e}")
                self._update_source_stats(source, success=False)
        
        # All sources failed, try cache
        cached_data = self._get_cached_data(symbol, data_type)
        if cached_data:
            self.logger.warning(f"⚠️ Using cached data for {symbol} - all sources failed")
            return cached_data
        
        self.logger.error(f"❌ All data sources failed for {symbol}")
        return None
    
    def get_multiple_symbols_data(self, 
                                 symbols: List[str], 
                                 data_type: str = 'ticker') -> Dict[str, MarketDataResponse]:
        """
        Get data untuk multiple symbols secara concurrent
        """
        results = {}
        
        # Use ThreadPoolExecutor untuk parallel requests
        with ThreadPoolExecutor(max_workers=5) as executor:
            # Submit all requests
            future_to_symbol = {
                executor.submit(self.get_market_data, symbol, data_type): symbol 
                for symbol in symbols
            }
            
            # Collect results
            for future in as_completed(future_to_symbol, timeout=30):
                symbol = future_to_symbol[future]
                try:
                    result = future.result()
                    if result:
                        results[symbol] = result
                    else:
                        self.logger.warning(f"No data returned for {symbol}")
                except Exception as e:
                    self.logger.error(f"Error fetching data for {symbol}: {e}")
        
        return results
    
    def _fetch_from_source(self, 
                          source: DataSource, 
                          symbol: str, 
                          data_type: str) -> Optional[MarketDataResponse]:
        """
        Fetch data dari specific source
        """
        try:
            config = self.source_configs[source]
            
            # Apply rate limiting
            self._apply_rate_limit(source)
            
            # Normalize symbol format untuk each exchange
            normalized_symbol = self._normalize_symbol_for_source(symbol, source)
            
            # Build URL
            endpoint = config['endpoints'].get(data_type)
            if not endpoint:
                self.logger.error(f"Endpoint {data_type} not configured for {source.value}")
                return None
            
            url = f"{config['base_url']}{endpoint}"
            
            # Build parameters
            params = self._build_params_for_source(source, normalized_symbol, data_type)
            
            # Make request
            start_time = time.time()
            response = requests.get(url, params=params, timeout=config['timeout'])
            latency_ms = (time.time() - start_time) * 1000
            
            response.raise_for_status()
            data = response.json()
            
            # Normalize response data
            normalized_data = self._normalize_response_data(source, data, data_type)
            
            if normalized_data:
                # Calculate quality score
                quality_score = self._calculate_data_quality_score(normalized_data, source)
                
                return MarketDataResponse(
                    source=source,
                    data=normalized_data,
                    timestamp=time.time(),
                    latency_ms=latency_ms,
                    is_primary=(source == self.primary_source),
                    quality_score=quality_score
                )
            
        except Exception as e:
            self.logger.error(f"Error fetching from {source.value}: {e}")
        
        return None
    
    def _normalize_symbol_for_source(self, symbol: str, source: DataSource) -> str:
        """
        Normalize symbol format untuk different exchanges
        """
        # Remove common suffixes and clean
        clean_symbol = symbol.upper().replace("-", "").replace("/", "").replace("_", "")
        
        if source == DataSource.OKX:
            # OKX format: BTC-USDT
            if "USDT" in clean_symbol:
                base = clean_symbol.replace("USDT", "")
                return f"{base}-USDT"
            return clean_symbol
        
        elif source == DataSource.BINANCE:
            # Binance format: BTCUSDT
            return clean_symbol
        
        elif source == DataSource.BYBIT:
            # Bybit format: BTCUSDT
            return clean_symbol
        
        elif source == DataSource.COINBASE:
            # Coinbase format: BTC-USD
            if "USDT" in clean_symbol:
                base = clean_symbol.replace("USDT", "")
                return f"{base}-USD"
            return clean_symbol
        
        return clean_symbol
    
    def _build_params_for_source(self, 
                                source: DataSource, 
                                symbol: str, 
                                data_type: str) -> Dict[str, Any]:
        """
        Build parameters untuk specific source dan endpoint
        """
        params = {}
        
        if source == DataSource.OKX:
            if data_type == 'ticker':
                params['instId'] = symbol
            elif data_type == 'kline':
                params['instId'] = symbol
                params['bar'] = '1m'
                params['limit'] = '100'
            elif data_type == 'orderbook':
                params['instId'] = symbol
                params['sz'] = '50'
        
        elif source == DataSource.BINANCE:
            if data_type == 'ticker':
                params['symbol'] = symbol
            elif data_type == 'kline':
                params['symbol'] = symbol
                params['interval'] = '1m'
                params['limit'] = 100
            elif data_type == 'orderbook':
                params['symbol'] = symbol
                params['limit'] = 50
        
        elif source == DataSource.BYBIT:
            if data_type == 'ticker':
                params['symbol'] = symbol
            elif data_type == 'kline':
                params['symbol'] = symbol
                params['interval'] = '1'
                params['limit'] = 100
            elif data_type == 'orderbook':
                params['symbol'] = symbol
                params['limit'] = 50
        
        elif source == DataSource.COINBASE:
            # Coinbase uses path parameters
            if data_type in ['ticker', 'kline', 'orderbook']:
                # Symbol akan digunakan dalam URL path
                pass
        
        return params
    
    def _normalize_response_data(self, 
                                source: DataSource, 
                                raw_data: Dict[str, Any], 
                                data_type: str) -> Optional[Dict[str, Any]]:
        """
        Normalize response data dari different sources ke standard format
        """
        try:
            if data_type == 'ticker':
                return self._normalize_ticker_data(source, raw_data)
            elif data_type == 'kline':
                return self._normalize_kline_data(source, raw_data)
            elif data_type == 'orderbook':
                return self._normalize_orderbook_data(source, raw_data)
        
        except Exception as e:
            self.logger.error(f"Error normalizing {data_type} data from {source.value}: {e}")
        
        return None
    
    def _normalize_ticker_data(self, source: DataSource, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize ticker data ke standard format
        """
        normalized = {
            'symbol': '',
            'price': 0,
            'volume': 0,
            'change_24h': 0,
            'change_24h_percentage': 0,
            'high_24h': 0,
            'low_24h': 0,
            'timestamp': time.time()
        }
        
        if source == DataSource.OKX:
            data = raw_data.get('data', [])
            if data:
                item = data[0]
                normalized.update({
                    'symbol': item.get('instId', ''),
                    'price': float(item.get('last', 0)),
                    'volume': float(item.get('vol24h', 0)),
                    'change_24h_percentage': float(item.get('changePct', 0)) * 100,
                    'high_24h': float(item.get('high24h', 0)),
                    'low_24h': float(item.get('low24h', 0))
                })
        
        elif source == DataSource.BINANCE:
            normalized.update({
                'symbol': raw_data.get('symbol', ''),
                'price': float(raw_data.get('lastPrice', 0)),
                'volume': float(raw_data.get('volume', 0)),
                'change_24h_percentage': float(raw_data.get('priceChangePercent', 0)),
                'high_24h': float(raw_data.get('highPrice', 0)),
                'low_24h': float(raw_data.get('lowPrice', 0))
            })
        
        elif source == DataSource.BYBIT:
            result = raw_data.get('result', {})
            data = result.get('list', [])
            if data:
                item = data[0]
                normalized.update({
                    'symbol': item.get('symbol', ''),
                    'price': float(item.get('lastPrice', 0)),
                    'volume': float(item.get('volume24h', 0)),
                    'change_24h_percentage': float(item.get('price24hPcnt', 0)) * 100,
                    'high_24h': float(item.get('highPrice24h', 0)),
                    'low_24h': float(item.get('lowPrice24h', 0))
                })
        
        # Add quality indicators
        normalized['data_source'] = source.value
        normalized['data_freshness'] = time.time()
        
        return normalized
    
    def _normalize_kline_data(self, source: DataSource, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize kline/candlestick data
        """
        normalized = {
            'symbol': '',
            'timeframe': '1m',
            'candles': [],
            'timestamp': time.time()
        }
        
        try:
            if source == DataSource.OKX:
                data = raw_data.get('data', [])
                for candle in data:
                    # OKX format: [timestamp, open, high, low, close, volume, ...]
                    normalized['candles'].append([
                        int(candle[0]),     # timestamp
                        float(candle[1]),   # open
                        float(candle[2]),   # high
                        float(candle[3]),   # low
                        float(candle[4]),   # close
                        float(candle[5])    # volume
                    ])
            
            elif source == DataSource.BINANCE:
                # Binance returns array directly
                for candle in raw_data:
                    normalized['candles'].append([
                        int(candle[0]),     # timestamp
                        float(candle[1]),   # open
                        float(candle[2]),   # high
                        float(candle[3]),   # low
                        float(candle[4]),   # close
                        float(candle[5])    # volume
                    ])
            
            elif source == DataSource.BYBIT:
                result = raw_data.get('result', {})
                data = result.get('list', [])
                for candle in data:
                    normalized['candles'].append([
                        int(candle[0]),     # timestamp
                        float(candle[1]),   # open
                        float(candle[2]),   # high
                        float(candle[3]),   # low
                        float(candle[4]),   # close
                        float(candle[5])    # volume
                    ])
        
        except Exception as e:
            self.logger.error(f"Error normalizing kline data from {source.value}: {e}")
        
        normalized['data_source'] = source.value
        return normalized
    
    def _normalize_orderbook_data(self, source: DataSource, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize orderbook data
        """
        normalized = {
            'symbol': '',
            'bids': [],  # [[price, quantity], ...]
            'asks': [],  # [[price, quantity], ...]
            'timestamp': time.time()
        }
        
        try:
            if source == DataSource.OKX:
                data = raw_data.get('data', [])
                if data:
                    book = data[0]
                    normalized['bids'] = [[float(bid[0]), float(bid[1])] for bid in book.get('bids', [])]
                    normalized['asks'] = [[float(ask[0]), float(ask[1])] for ask in book.get('asks', [])]
            
            elif source == DataSource.BINANCE:
                normalized['bids'] = [[float(bid[0]), float(bid[1])] for bid in raw_data.get('bids', [])]
                normalized['asks'] = [[float(ask[0]), float(ask[1])] for ask in raw_data.get('asks', [])]
            
            elif source == DataSource.BYBIT:
                result = raw_data.get('result', {})
                normalized['bids'] = [[float(bid[0]), float(bid[1])] for bid in result.get('b', [])]
                normalized['asks'] = [[float(ask[0]), float(ask[1])] for ask in result.get('a', [])]
        
        except Exception as e:
            self.logger.error(f"Error normalizing orderbook data from {source.value}: {e}")
        
        normalized['data_source'] = source.value
        return normalized
    
    def _calculate_data_quality_score(self, data: Dict[str, Any], source: DataSource) -> float:
        """
        Calculate quality score untuk data
        """
        score = 100.0
        
        try:
            # Check for missing critical fields
            if 'symbol' not in data or not data['symbol']:
                score -= 20
            
            if 'price' in data:
                if data['price'] <= 0:
                    score -= 30
            
            if 'volume' in data:
                if data['volume'] < 0:
                    score -= 10
            
            # Check data freshness
            current_time = time.time()
            data_timestamp = data.get('timestamp', current_time)
            age_seconds = current_time - data_timestamp
            
            if age_seconds > 60:  # Data older than 1 minute
                score -= (age_seconds / 60) * 5  # 5 points per minute
            
            # Source reliability bonus
            source_stats = self.source_stats.get(source, {})
            success_rate = (source_stats.get('successful_requests', 0) / 
                          max(1, source_stats.get('total_requests', 1)))
            
            if success_rate > 0.95:
                score += 5
            elif success_rate < 0.8:
                score -= 10
            
            # Ensure score bounds
            score = max(0, min(100, score))
        
        except Exception as e:
            self.logger.error(f"Error calculating quality score: {e}")
            score = 50  # Default medium score
        
        return score
    
    def _get_prioritized_sources(self) -> List[DataSource]:
        """
        Get list of sources berdasarkan performance priority
        """
        # Start dengan primary source
        sources = [self.primary_source]
        
        # Add backup sources sorted by performance
        backup_with_scores = []
        for source in self.backup_sources:
            stats = self.source_stats[source]
            total_requests = stats['total_requests']
            if total_requests > 0:
                success_rate = stats['successful_requests'] / total_requests
                avg_latency = stats['total_latency'] / stats['successful_requests'] if stats['successful_requests'] > 0 else 999
                
                # Score = success_rate * 100 - avg_latency_seconds * 10
                score = success_rate * 100 - (avg_latency / 1000) * 10
            else:
                score = 50  # Default score for untested sources
            
            backup_with_scores.append((source, score))
        
        # Sort by score (highest first)
        backup_with_scores.sort(key=lambda x: x[1], reverse=True)
        sources.extend([source for source, score in backup_with_scores])
        
        return sources
    
    def _is_source_in_failover(self, source: DataSource) -> bool:
        """
        Check if source is currently in failover mode
        """
        stats = self.source_stats[source]
        
        # Check consecutive failures
        if stats['consecutive_failures'] >= self.max_consecutive_failures:
            # Check if enough time has passed for retry
            time_since_last_request = time.time() - stats['last_request_time']
            return time_since_last_request < self.failover_timeout
        
        return False
    
    def _apply_rate_limit(self, source: DataSource):
        """
        Apply rate limiting untuk source
        """
        config = self.source_configs[source]
        stats = self.source_stats[source]
        
        elapsed = time.time() - stats['last_request_time']
        if elapsed < config['rate_limit']:
            sleep_time = config['rate_limit'] - elapsed
            time.sleep(sleep_time)
        
        stats['last_request_time'] = time.time()
    
    def _update_source_stats(self, source: DataSource, success: bool, latency: float = 0):
        """
        Update statistics untuk source
        """
        stats = self.source_stats[source]
        stats['total_requests'] += 1
        
        if success:
            stats['successful_requests'] += 1
            stats['consecutive_failures'] = 0
            stats['last_successful_call'] = time.time()
            if latency > 0:
                stats['total_latency'] += latency
        else:
            stats['failed_requests'] += 1
            stats['consecutive_failures'] += 1
    
    def _cache_data(self, symbol: str, data_type: str, response: MarketDataResponse):
        """
        Cache successful data response
        """
        cache_key = f"{symbol}_{data_type}"
        self.data_cache[cache_key] = {
            'response': response,
            'cached_at': time.time()
        }
        
        # Clean old cache entries
        current_time = time.time()
        expired_keys = [k for k, v in self.data_cache.items() 
                       if current_time - v['cached_at'] > self.cache_ttl]
        for key in expired_keys:
            del self.data_cache[key]
    
    def _get_cached_data(self, symbol: str, data_type: str) -> Optional[MarketDataResponse]:
        """
        Get cached data if still valid
        """
        cache_key = f"{symbol}_{data_type}"
        
        if cache_key in self.data_cache:
            cached_entry = self.data_cache[cache_key]
            age = time.time() - cached_entry['cached_at']
            
            if age < self.cache_ttl:
                # Mark as cached data
                response = cached_entry['response']
                response.data['is_cached'] = True
                response.data['cache_age_seconds'] = age
                return response
        
        return None
    
    def get_all_sources_status(self) -> Dict[str, DataSourceStatus]:
        """
        Get status semua data sources
        """
        status_dict = {}
        
        for source in DataSource:
            stats = self.source_stats[source]
            total_requests = stats['total_requests']
            
            if total_requests > 0:
                error_rate = stats['failed_requests'] / total_requests
                avg_latency = stats['total_latency'] / max(1, stats['successful_requests'])
            else:
                error_rate = 0
                avg_latency = 0
            
            is_available = (stats['consecutive_failures'] < self.max_consecutive_failures and
                          not self._is_source_in_failover(source))
            
            # Calculate quality score
            if total_requests > 0:
                success_rate = stats['successful_requests'] / total_requests
                quality_score = (success_rate * 70) + max(0, (5000 - avg_latency) / 5000 * 30)
            else:
                quality_score = 50  # Default for untested sources
            
            status_dict[source.value] = DataSourceStatus(
                source=source,
                is_available=is_available,
                latency_ms=avg_latency,
                error_rate=error_rate,
                last_successful_call=stats['last_successful_call'],
                quality_score=min(100, quality_score)
            )
        
        return status_dict
    
    def test_all_sources(self, test_symbol: str = "BTC-USDT") -> Dict[str, Dict[str, Any]]:
        """
        Test semua data sources dengan symbol tertentu
        """
        results = {}
        
        for source in DataSource:
            try:
                start_time = time.time()
                response = self._fetch_from_source(source, test_symbol, 'ticker')
                end_time = time.time()
                
                if response:
                    results[source.value] = {
                        'status': 'success',
                        'latency_ms': response.latency_ms,
                        'quality_score': response.quality_score,
                        'data_available': bool(response.data)
                    }
                else:
                    results[source.value] = {
                        'status': 'failed',
                        'latency_ms': (end_time - start_time) * 1000,
                        'quality_score': 0,
                        'data_available': False
                    }
            
            except Exception as e:
                results[source.value] = {
                    'status': 'error',
                    'error': str(e),
                    'latency_ms': 0,
                    'quality_score': 0,
                    'data_available': False
                }
        
        return results

# Global instance
multi_source_data_manager = MultiSourceDataManager()

def get_multi_source_data_manager():
    """Get global multi-source data manager instance"""
    return multi_source_data_manager