"""
OKX API data fetcher with rate limiting and caching
"""

import requests
import pandas as pd
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, List
import time
import os
import hmac
import hashlib
import base64

logger = logging.getLogger(__name__)

# Create OKXFetcher alias after class definition

class OKXAPIManager:
    """OKX API manager with rate limiting and caching"""
    
    def __init__(self):
        self.base_url = "https://www.okx.com"
        self.session = requests.Session()
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
        self.last_request_time = 0
        self.min_request_interval = 0.05  # 50ms between requests
        
        # Load API credentials
        self.api_key = os.environ.get('OKX_API_KEY')
        self.secret_key = os.environ.get('OKX_SECRET_KEY')
        self.passphrase = os.environ.get('OKX_PASSPHRASE')
        
        # Check if credentials are available for authenticated requests
        self.has_credentials = all([self.api_key, self.secret_key, self.passphrase])
        
        if self.has_credentials:
            logger.info("OKX API initialized with authentication credentials")
        else:
            logger.warning("OKX API initialized without authentication credentials (public endpoints only)")
        
    def get_candles(self, symbol: str, timeframe: str = '1H', limit: int = 100) -> Optional[pd.DataFrame]:
        """Get candlestick data from OKX API"""
        
        cache_key = f"{symbol}_{timeframe}_{limit}"
        
        # Check cache first
        if self._is_cached(cache_key):
            logger.debug(f"Returning cached data for {symbol}")
            return self.cache[cache_key]['data']
        
        try:
            # Rate limiting
            self._rate_limit()
            
            # Map timeframe to OKX format - Extended support
            tf_map = {
                '1m': '1m',
                '3m': '3m', 
                '5m': '5m',
                '15m': '15m',
                '30m': '30m',
                '1H': '1H',
                '2H': '2H',
                '4H': '4H',
                '6H': '6H',
                '8H': '8H',
                '12H': '12H',
                '1D': '1D',
                '3D': '3D',
                '1W': '1W',
                '1M': '1M',
                # Aliases for common formats
                '1': '1m',
                '5': '5m', 
                '15': '15m',
                '30': '30m',
                '60': '1H',
                '240': '4H',
                '1440': '1D'
            }
            
            okx_timeframe = tf_map.get(timeframe, '1H')
            
            # Build request URL
            url = f"{self.base_url}/api/v5/market/candles"
            params = {
                'instId': symbol,
                'bar': okx_timeframe,
                'limit': str(limit)
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('code') == '0' and data.get('data'):
                # Convert to DataFrame
                candles = data['data']
                if candles:
                    df = pd.DataFrame(candles)
                    df.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'volCcy', 'volCcyQuote', 'confirm']
                else:
                    return None
                
                # Process data with proper timestamp handling
                df['timestamp'] = pd.to_datetime(df['timestamp'].astype(float), unit='ms')
                df['open'] = df['open'].astype(float)
                df['high'] = df['high'].astype(float)
                df['low'] = df['low'].astype(float)
                df['close'] = df['close'].astype(float)
                df['volume'] = df['volume'].astype(float)
                
                # Sort by timestamp
                df = df.sort_values('timestamp').reset_index(drop=True)
                
                # Cache the result
                self.cache[cache_key] = {
                    'data': df,
                    'timestamp': datetime.now()
                }
                
                logger.debug(f"Fetched {len(df)} candles for {symbol}")
                return df
                
            else:
                logger.error(f"OKX API error for {symbol}: {data}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error for {symbol}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching {symbol}: {e}")
            return None
    
    def _rate_limit(self):
        """Apply rate limiting between requests"""
        now = time.time()
        time_since_last = now - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _is_cached(self, cache_key: str) -> bool:
        """Check if data is cached and still valid"""
        if cache_key not in self.cache:
            return False
            
        cached_time = self.cache[cache_key]['timestamp']
        if datetime.now() - cached_time > timedelta(seconds=self.cache_ttl):
            del self.cache[cache_key]
            return False
            
        return True
    
    def get_ticker(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get ticker data for a symbol"""
        try:
            self._rate_limit()
            
            url = f"{self.base_url}/api/v5/market/ticker"
            params = {'instId': symbol}
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('code') == '0' and data.get('data'):
                return data['data'][0]
            else:
                logger.error(f"Ticker API error for {symbol}: {data}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching ticker for {symbol}: {e}")
            return None
    
    def clear_cache(self):
        """Clear all cached data"""
        self.cache.clear()
        logger.info("Cache cleared")
    
    def get_orderbook(self, symbol: str, depth: int = 20) -> Dict[str, Any]:
        """Get orderbook data for a symbol"""
        try:
            self._rate_limit()
            
            url = f"{self.base_url}/api/v5/market/books"
            params = {
                'instId': symbol,
                'sz': min(depth, 400)  # Max 400 levels
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('code') == '0' and data.get('data'):
                orderbook_data = data['data'][0]
                return {
                    'bids': orderbook_data.get('bids', []),
                    'asks': orderbook_data.get('asks', []),
                    'ts': orderbook_data.get('ts')
                }
            else:
                logger.error(f"Orderbook API error for {symbol}: {data}")
                return {
                    'bids': [],
                    'asks': [],
                    'ts': None
                }
                
        except Exception as e:
            logger.error(f"Error fetching orderbook for {symbol}: {e}")
            return {
                'bids': [],
                'asks': [],
                'ts': None
            }
    
    def _generate_signature(self, method: str, path: str, body: str = '') -> tuple:
        """Generate OKX API signature for authenticated requests"""
        # Generate ISO timestamp
        timestamp = datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')
        
        # Create message to sign
        message = timestamp + method + path + body
        
        # Create signature
        if not self.secret_key:
            raise ValueError("Secret key is required for authentication")
            
        mac = hmac.new(
            bytes(self.secret_key, encoding='utf8'),
            bytes(message, encoding='utf-8'),
            digestmod=hashlib.sha256
        )
        signature = base64.b64encode(mac.digest()).decode('utf-8')
        
        return timestamp, signature
    
    def _get_auth_headers(self, method: str, path: str, body: str = '') -> Dict[str, str]:
        """Generate authentication headers for OKX API"""
        if not self.has_credentials:
            return {}
        
        timestamp, signature = self._generate_signature(method, path, body)
        
        return {
            'OK-ACCESS-KEY': self.api_key,
            'OK-ACCESS-SIGN': signature,
            'OK-ACCESS-TIMESTAMP': timestamp,
            'OK-ACCESS-PASSPHRASE': self.passphrase,
            'Content-Type': 'application/json'
        }
    
    def get_funding_rate(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get current funding rate for futures symbol"""
        try:
            self._rate_limit()
            
            url = f"{self.base_url}/api/v5/public/funding-rate"
            params = {'instId': symbol}
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('code') == '0' and data.get('data'):
                funding_data = data['data'][0]
                return {
                    'funding_rate': float(funding_data.get('fundingRate', 0)),
                    'next_funding_time': funding_data.get('nextFundingTime'),
                    'funding_time': funding_data.get('fundingTime'),
                    'inst_id': funding_data.get('instId')
                }
            else:
                logger.error(f"Funding rate API error for {symbol}: {data}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching funding rate for {symbol}: {e}")
            return None
    
    def get_open_interest(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get open interest for futures symbol"""
        try:
            self._rate_limit()
            
            url = f"{self.base_url}/api/v5/public/open-interest"
            params = {'instId': symbol}
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('code') == '0' and data.get('data'):
                oi_data = data['data'][0]
                return {
                    'open_interest': float(oi_data.get('oi', 0)),
                    'open_interest_ccy': float(oi_data.get('oiCcy', 0)),
                    'timestamp': oi_data.get('ts'),
                    'inst_id': oi_data.get('instId')
                }
            else:
                logger.error(f"Open interest API error for {symbol}: {data}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching open interest for {symbol}: {e}")
            return None
    
    def get_leverage_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get leverage information (requires authentication)"""
        if not self.has_credentials:
            logger.warning("Leverage info requires authentication")
            return None
            
        try:
            self._rate_limit()
            
            url = f"{self.base_url}/api/v5/account/leverage-info"
            params = {'instId': symbol}
            headers = self._get_auth_headers('GET', '/api/v5/account/leverage-info?' + 
                                           '&'.join([f"{k}={v}" for k, v in params.items()]))
            
            response = self.session.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('code') == '0' and data.get('data'):
                lev_data = data['data'][0]
                return {
                    'leverage': float(lev_data.get('lever', 0)),
                    'margin_mode': lev_data.get('mgnMode'),
                    'position_side': lev_data.get('posSide'),
                    'inst_id': lev_data.get('instId')
                }
            else:
                logger.error(f"Leverage info API error for {symbol}: {data}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching leverage info for {symbol}: {e}")
            return None
    
    def get_margin_balance(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get margin balance and requirements (requires authentication)"""
        if not self.has_credentials:
            logger.warning("Margin balance requires authentication")
            return None
            
        try:
            self._rate_limit()
            
            url = f"{self.base_url}/api/v5/account/position/margin-balance"
            params = {'instId': symbol}
            headers = self._get_auth_headers('GET', '/api/v5/account/position/margin-balance?' + 
                                           '&'.join([f"{k}={v}" for k, v in params.items()]))
            
            response = self.session.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('code') == '0' and data.get('data'):
                margin_data = data['data'][0] if data['data'] else {}
                return {
                    'margin_balance': float(margin_data.get('amt', 0)),
                    'margin_ratio': float(margin_data.get('mgnRatio', 0)),
                    'maintenance_margin': float(margin_data.get('mmr', 0)),
                    'initial_margin': float(margin_data.get('imr', 0)),
                    'inst_id': margin_data.get('instId')
                }
            else:
                logger.warning(f"No margin data for {symbol}: {data}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching margin balance for {symbol}: {e}")
            return None
        
        return {
            'OK-ACCESS-KEY': self.api_key,
            'OK-ACCESS-SIGN': signature,
            'OK-ACCESS-TIMESTAMP': timestamp,
            'OK-ACCESS-PASSPHRASE': self.passphrase,
            'Content-Type': 'application/json'
        }
    
    def get_account_balance(self) -> Optional[Dict[str, Any]]:
        """Get account balance (authenticated endpoint)"""
        if not self.has_credentials:
            logger.warning("Cannot get account balance: No credentials provided")
            return None
            
        try:
            self._rate_limit()
            
            method = 'GET'
            path = '/api/v5/account/balance'
            headers = self._get_auth_headers(method, path)
            
            url = f"{self.base_url}{path}"
            response = self.session.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('code') == '0' and data.get('data'):
                return data['data'][0]
            else:
                logger.error(f"Account balance API error: {data}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching account balance: {e}")
            return None
    
    def get_account_config(self) -> Optional[Dict[str, Any]]:
        """Get account configuration (authenticated endpoint)"""
        if not self.has_credentials:
            logger.warning("Cannot get account config: No credentials provided")
            return None
            
        try:
            self._rate_limit()
            
            method = 'GET'
            path = '/api/v5/account/config'
            headers = self._get_auth_headers(method, path)
            
            url = f"{self.base_url}{path}"
            response = self.session.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('code') == '0' and data.get('data'):
                return data['data'][0]
            else:
                logger.error(f"Account config API error: {data}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching account config: {e}")
            return None
    
    def get_positions(self) -> Optional[list]:
        """Get account positions (authenticated endpoint)"""
        if not self.has_credentials:
            logger.warning("Cannot get positions: No credentials provided")
            return None
            
        try:
            self._rate_limit()
            
            method = 'GET'
            path = '/api/v5/account/positions'
            headers = self._get_auth_headers(method, path)
            
            url = f"{self.base_url}{path}"
            response = self.session.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('code') == '0':
                return data.get('data', [])
            else:
                logger.error(f"Positions API error: {data}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching positions: {e}")
            return None
    
    def test_authentication(self) -> bool:
        """Test if authentication is working"""
        if not self.has_credentials:
            logger.warning("Cannot test authentication: No credentials provided")
            return False
            
        try:
            config = self.get_account_config()
            return config is not None
            
        except Exception as e:
            logger.error(f"Authentication test failed: {e}")
            return False
    
    # ===== ENHANCED OKX API FEATURES (ALL FREE) =====
    
    def get_funding_rate_history(self, symbol: str, limit: int = 100) -> Optional[List[Dict[str, Any]]]:
        """Get funding rate history for trend analysis"""
        try:
            self._rate_limit()
            
            url = f"{self.base_url}/api/v5/public/funding-rate-history"
            params = {
                'instId': symbol,
                'limit': str(min(limit, 100))
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('code') == '0' and data.get('data'):
                history = []
                for rate in data['data']:
                    history.append({
                        'inst_id': rate.get('instId'),
                        'funding_rate': float(rate.get('fundingRate', 0)),
                        'funding_time': rate.get('fundingTime'),
                        'realized_rate': float(rate.get('realizedRate', 0))
                    })
                
                logger.info(f"Fetched {len(history)} funding rate history for {symbol}")
                return history
            else:
                logger.error(f"Funding rate history API error for {symbol}: {data}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching funding rate history for {symbol}: {e}")
            return None
    
    def get_price_limit(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get price limits for risk management"""
        try:
            self._rate_limit()
            
            url = f"{self.base_url}/api/v5/public/price-limit"
            params = {'instId': symbol}
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('code') == '0' and data.get('data'):
                limit_data = data['data'][0]
                return {
                    'inst_id': limit_data.get('instId'),
                    'buy_limit': float(limit_data.get('buyLmt', 0)),
                    'sell_limit': float(limit_data.get('sellLmt', 0)),
                    'timestamp': limit_data.get('ts')
                }
            else:
                logger.error(f"Price limit API error for {symbol}: {data}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching price limit for {symbol}: {e}")
            return None
    
    def get_liquidation_orders(self, inst_type: str = "SWAP", state: str = "filled", 
                               uly: str = None, alias: str = None, inst_family: str = None,
                               limit: int = 100) -> Optional[List[Dict[str, Any]]]:
        """Get liquidation orders - KEY FEATURE for market analysis"""
        try:
            self._rate_limit()
            
            url = f"{self.base_url}/api/v5/public/liquidation-orders"
            params = {
                'instType': inst_type,
                'limit': str(min(limit, 100))
            }
            
            # Add optional parameters
            if state:
                params['state'] = state
            if uly:
                params['uly'] = uly
            if alias:
                params['alias'] = alias
            if inst_family:
                params['instFamily'] = inst_family
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('code') == '0' and data.get('data'):
                liquidations = []
                for liq in data['data']:
                    details = liq.get('details', [])
                    total_loss = 0
                    
                    # Calculate total loss from details
                    if details:
                        for detail in details:
                            loss = float(detail.get('sz', 0)) * float(detail.get('bkPx', 0))
                            total_loss += loss
                    
                    liquidations.append({
                        'inst_id': liq.get('instId'),
                        'uly': liq.get('uly'),
                        'total_loss': total_loss,
                        'details': details,
                        'timestamp': datetime.now().isoformat()
                    })
                
                logger.info(f"Fetched {len(liquidations)} liquidation orders")
                return liquidations
            else:
                logger.error(f"Liquidation orders API error: {data}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching liquidation orders: {e}")
            return None
    
    def get_long_short_ratio(self, currency: str = "BTC", period: str = "5m") -> Optional[Dict[str, Any]]:
        """Get long/short position ratio"""
        try:
            self._rate_limit()
            
            url = f"{self.base_url}/api/v5/rubik/stat/contracts/long-short-account-ratio"
            params = {
                'ccy': currency,
                'period': period  # 5m, 1h, 1d
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('code') == '0' and data.get('data'):
                ratio_data = data['data'][0] if data['data'] else {}
                return {
                    'currency': currency,
                    'long_ratio': float(ratio_data.get('longShortPosRatio', 0)),
                    'timestamp': ratio_data.get('ts')
                }
            else:
                logger.error(f"Long/short ratio API error: {data}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching long/short ratio: {e}")
            return None
    
    def get_taker_volume(self, currency: str = "BTC", inst_type: str = "SPOT", period: str = "5m") -> Optional[Dict[str, Any]]:
        """Get taker buy/sell volume"""
        try:
            self._rate_limit()
            
            url = f"{self.base_url}/api/v5/rubik/stat/taker-volume"
            params = {
                'ccy': currency,
                'instType': inst_type,
                'period': period
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('code') == '0' and data.get('data'):
                volume_data = data['data'][0] if data['data'] else {}
                return {
                    'currency': currency,
                    'buy_volume': float(volume_data.get('buyVol', 0)),
                    'sell_volume': float(volume_data.get('sellVol', 0)),
                    'timestamp': volume_data.get('ts')
                }
            else:
                logger.error(f"Taker volume API error: {data}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching taker volume: {e}")
            return None
    
    def get_option_market_data(self, currency: str = "BTC", exp_time: str = None) -> Optional[List[Dict[str, Any]]]:
        """Get option market data for advanced analysis"""
        try:
            self._rate_limit()
            
            url = f"{self.base_url}/api/v5/public/opt-summary"
            params = {
                'uly': f"{currency}-USD"
            }
            
            if exp_time:
                params['expTime'] = exp_time
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('code') == '0' and data.get('data'):
                options = []
                for opt in data['data']:
                    options.append({
                        'inst_id': opt.get('instId'),
                        'uly': opt.get('uly'),
                        'delta': float(opt.get('delta', 0)),
                        'gamma': float(opt.get('gamma', 0)),
                        'vega': float(opt.get('vega', 0)),
                        'theta': float(opt.get('theta', 0)),
                        'mark_vol': float(opt.get('markVol', 0)),
                        'bid_vol': float(opt.get('bidVol', 0)),
                        'ask_vol': float(opt.get('askVol', 0)),
                        'realized_vol': float(opt.get('realVol', 0))
                    })
                
                logger.info(f"Fetched {len(options)} option data for {currency}")
                return options
            else:
                logger.error(f"Option market data API error: {data}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching option market data: {e}")
            return None
    
    def get_index_components(self, index: str = "BTC-USD") -> Optional[List[Dict[str, Any]]]:
        """Get index components and weights"""
        try:
            self._rate_limit()
            
            url = f"{self.base_url}/api/v5/market/index-components"
            params = {'index': index}
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('code') == '0' and data.get('data'):
                components = []
                if 'components' in data['data']:
                    for comp in data['data']['components']:
                        components.append({
                            'symbol': comp.get('symbol'),
                            'weight': float(comp.get('weight', 0)),
                            'exchange': comp.get('exch')
                        })
                
                logger.info(f"Fetched {len(components)} components for {index}")
                return components
            else:
                logger.error(f"Index components API error: {data}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching index components: {e}")
            return None
    
    def get_block_trades(self, inst_type: str = "OPTION", uly: str = None, inst_family: str = None) -> Optional[List[Dict[str, Any]]]:
        """Get block trades data"""
        try:
            self._rate_limit()
            
            url = f"{self.base_url}/api/v5/market/block-trades"
            params = {'instType': inst_type}
            
            if uly:
                params['uly'] = uly
            if inst_family:
                params['instFamily'] = inst_family
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('code') == '0' and data.get('data'):
                trades = []
                for trade in data['data']:
                    trades.append({
                        'inst_id': trade.get('instId'),
                        'trade_id': trade.get('tradeId'),
                        'price': float(trade.get('px', 0)),
                        'size': float(trade.get('sz', 0)),
                        'side': trade.get('side'),
                        'timestamp': trade.get('ts')
                    })
                
                logger.info(f"Fetched {len(trades)} block trades")
                return trades
            else:
                logger.error(f"Block trades API error: {data}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching block trades: {e}")
            return None
    
    def get_support_coin(self) -> Optional[List[str]]:
        """Get list of supported trading currencies"""
        try:
            self._rate_limit()
            
            url = f"{self.base_url}/api/v5/rubik/stat/trading-data/support-coin"
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('code') == '0' and data.get('data'):
                coins = data['data'].get('currency', [])
                logger.info(f"Fetched {len(coins)} supported coins")
                return coins
            else:
                logger.error(f"Support coin API error: {data}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching supported coins: {e}")
            return None

    def get_historical_data(self, symbol: str, timeframe: str = '1H', limit: int = 200) -> Optional[pd.DataFrame]:
        """
        Alias for get_candles - provides historical candlestick data
        Used by trading analysis engines
        """
        return self.get_candles(symbol, timeframe, limit)

# Create alias for backward compatibility
OKXFetcher = OKXAPIManager