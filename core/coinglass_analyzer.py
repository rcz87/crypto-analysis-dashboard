#!/usr/bin/env python3
"""
CoinGlass Data Analyzer Module
Integrates liquidation heatmaps, open interest, and funding rates into our SMC system
"""

import requests
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import time
import logging
from dataclasses import dataclass
import json

@dataclass
class LiquidationZone:
    """Liquidation cluster zone data"""
    price: float
    volume: float
    side: str  # 'long' or 'short'
    strength: float  # 0-100 intensity score
    timestamp: datetime

@dataclass
class OpenInterestData:
    """Open Interest metrics"""
    symbol: str
    total_oi: float
    oi_change_24h: float
    oi_change_percent: float
    long_ratio: float
    short_ratio: float
    timestamp: datetime

@dataclass
class FundingRateData:
    """Funding rate information"""
    symbol: str
    exchange: str
    funding_rate: float
    next_funding_time: datetime
    predicted_rate: float
    timestamp: datetime

class CoinGlassAnalyzer:
    """
    CoinGlass API Integration for Advanced Market Structure Analysis
    
    Features:
    - Liquidation heatmap analysis
    - Open Interest tracking
    - Long/Short ratio monitoring  
    - Funding rate analysis
    - SMC zone correlation
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = "https://api.coinglass.com/v2"
        self.session = requests.Session()
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 0.1  # 100ms between requests
        
        # Cache settings
        self.cache_duration = {
            'liquidation': 30,  # 30 seconds
            'open_interest': 60,  # 1 minute
            'funding_rates': 300  # 5 minutes
        }
        self.cache = {}
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Headers for authenticated requests
        if self.api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            })
    
    def _rate_limit(self):
        """Implement rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
        
        self.last_request_time = time.time()
    
    def _get_cached_data(self, cache_key: str, cache_type: str) -> Optional[Dict]:
        """Get cached data if still valid"""
        if cache_key in self.cache:
            cached_data = self.cache[cache_key]
            cache_age = time.time() - cached_data['timestamp']
            
            if cache_age < self.cache_duration[cache_type]:
                return cached_data['data']
        
        return None
    
    def _cache_data(self, cache_key: str, data: Dict):
        """Cache data with timestamp"""
        self.cache[cache_key] = {
            'data': data,
            'timestamp': time.time()
        }
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """Make authenticated API request with error handling"""
        if not self.api_key:
            self.logger.warning("CoinGlass API key not provided - using demo mode")
            return self._get_demo_data(endpoint)
        
        try:
            self._rate_limit()
            
            url = f"{self.base_url}/{endpoint}"
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"CoinGlass API request failed: {e}")
            return None
        except Exception as e:
            self.logger.error(f"CoinGlass API error: {e}")
            return None
    
    def _get_demo_data(self, endpoint: str) -> Dict:
        """Return demo data structure when API key not available"""
        demo_structures = {
            'liquidation/heatmap': {
                'success': True,
                'data': {
                    'liquidation_zones': [],
                    'total_liquidations_24h': 0,
                    'message': 'Demo mode - API key required for real data'
                }
            },
            'open_interest': {
                'success': True, 
                'data': {
                    'open_interest': 0,
                    'oi_change_24h': 0,
                    'long_ratio': 50.0,
                    'short_ratio': 50.0,
                    'message': 'Demo mode - API key required for real data'
                }
            },
            'funding_rates': {
                'success': True,
                'data': {
                    'funding_rates': [],
                    'weighted_average': 0,
                    'message': 'Demo mode - API key required for real data'
                }
            }
        }
        
        return demo_structures.get(endpoint, {'success': False, 'error': 'Unknown endpoint'})
    
    def get_liquidation_heatmap(self, symbol: str = "BTCUSDT") -> List[LiquidationZone]:
        """
        Get liquidation heatmap data
        Returns zones where liquidations are clustered
        """
        cache_key = f"liquidation_{symbol}"
        cached = self._get_cached_data(cache_key, 'liquidation')
        
        if cached:
            return self._parse_liquidation_zones(cached)
        
        # API call
        params = {'symbol': symbol}
        response = self._make_request('liquidation/heatmap', params)
        
        if not response or not response.get('success'):
            return []
        
        data = response.get('data', {})
        self._cache_data(cache_key, data)
        
        return self._parse_liquidation_zones(data)
    
    def _parse_liquidation_zones(self, data: Dict) -> List[LiquidationZone]:
        """Parse liquidation data into structured zones"""
        zones = []
        
        liquidation_data = data.get('liquidation_zones', [])
        for zone_data in liquidation_data:
            zone = LiquidationZone(
                price=float(zone_data.get('price', 0)),
                volume=float(zone_data.get('volume', 0)),
                side=zone_data.get('side', 'unknown'),
                strength=float(zone_data.get('strength', 0)),
                timestamp=datetime.now()
            )
            zones.append(zone)
        
        return zones
    
    def get_open_interest_data(self, symbol: str = "BTCUSDT") -> Optional[OpenInterestData]:
        """
        Get open interest metrics
        Shows market positioning and sentiment
        """
        cache_key = f"oi_{symbol}"
        cached = self._get_cached_data(cache_key, 'open_interest')
        
        if cached:
            return self._parse_open_interest(cached, symbol)
        
        # API call
        params = {'symbol': symbol}
        response = self._make_request('open_interest', params)
        
        if not response or not response.get('success'):
            return None
        
        data = response.get('data', {})
        self._cache_data(cache_key, data)
        
        return self._parse_open_interest(data, symbol)
    
    def _parse_open_interest(self, data: Dict, symbol: str) -> Optional[OpenInterestData]:
        """Parse open interest data"""
        try:
            return OpenInterestData(
                symbol=symbol,
                total_oi=float(data.get('open_interest', 0)),
                oi_change_24h=float(data.get('oi_change_24h', 0)),
                oi_change_percent=float(data.get('oi_change_percent', 0)),
                long_ratio=float(data.get('long_ratio', 50.0)),
                short_ratio=float(data.get('short_ratio', 50.0)),
                timestamp=datetime.now()
            )
        except Exception as e:
            self.logger.error(f"Error parsing open interest data: {e}")
            return None
    
    def get_funding_rates(self, symbol: str = "BTCUSDT") -> List[FundingRateData]:
        """
        Get funding rates across exchanges
        Shows cost of holding leveraged positions
        """
        cache_key = f"funding_{symbol}"
        cached = self._get_cached_data(cache_key, 'funding_rates')
        
        if cached:
            return self._parse_funding_rates(cached, symbol)
        
        # API call
        params = {'symbol': symbol}
        response = self._make_request('funding_rates', params)
        
        if not response or not response.get('success'):
            return []
        
        data = response.get('data', {})
        self._cache_data(cache_key, data)
        
        return self._parse_funding_rates(data, symbol)
    
    def _parse_funding_rates(self, data: Dict, symbol: str) -> List[FundingRateData]:
        """Parse funding rates data"""
        rates = []
        
        funding_data = data.get('funding_rates', [])
        for rate_data in funding_data:
            try:
                rate = FundingRateData(
                    symbol=symbol,
                    exchange=rate_data.get('exchange', 'unknown'),
                    funding_rate=float(rate_data.get('funding_rate', 0)),
                    next_funding_time=datetime.now() + timedelta(hours=8),  # Default 8h cycle
                    predicted_rate=float(rate_data.get('predicted_rate', 0)),
                    timestamp=datetime.now()
                )
                rates.append(rate)
            except Exception as e:
                self.logger.error(f"Error parsing funding rate: {e}")
        
        return rates
    
    def analyze_liquidation_confluence(self, 
                                    liquidation_zones: List[LiquidationZone],
                                    current_price: float,
                                    smc_zones: List[Dict]) -> Dict[str, Any]:
        """
        Analyze confluence between liquidation zones and SMC levels
        Critical for timing entries and exits
        """
        analysis = {
            'nearby_liquidation_zones': [],
            'smc_liquidity_confluence': [],
            'liquidation_magnet_levels': [],
            'risk_assessment': 'low'
        }
        
        # Find zones within 5% of current price
        price_range = current_price * 0.05
        nearby_zones = [
            zone for zone in liquidation_zones
            if abs(zone.price - current_price) <= price_range
        ]
        
        analysis['nearby_liquidation_zones'] = [
            {
                'price': zone.price,
                'volume': zone.volume,
                'side': zone.side,
                'strength': zone.strength,
                'distance_percent': ((zone.price - current_price) / current_price) * 100
            }
            for zone in nearby_zones
        ]
        
        # Check confluence with SMC zones
        for smc_zone in smc_zones:
            smc_price = smc_zone.get('price', 0)
            
            for liq_zone in nearby_zones:
                price_diff = abs(liq_zone.price - smc_price)
                if price_diff <= (current_price * 0.002):  # Within 0.2%
                    analysis['smc_liquidity_confluence'].append({
                        'smc_zone': smc_zone.get('type', 'unknown'),
                        'smc_price': smc_price,
                        'liquidation_price': liq_zone.price,
                        'liquidation_volume': liq_zone.volume,
                        'confluence_strength': liq_zone.strength * 1.5  # Boost for confluence
                    })
        
        # Identify liquidation magnet levels (high volume clusters)
        high_volume_zones = sorted(
            [zone for zone in liquidation_zones if zone.strength > 70],
            key=lambda x: x.volume,
            reverse=True
        )[:3]
        
        analysis['liquidation_magnet_levels'] = [
            {
                'price': zone.price,
                'volume': zone.volume,
                'magnet_strength': zone.strength,
                'side': zone.side
            }
            for zone in high_volume_zones
        ]
        
        # Risk assessment based on liquidation density
        total_nearby_volume = sum(zone.volume for zone in nearby_zones)
        if total_nearby_volume > 100000000:  # $100M threshold
            analysis['risk_assessment'] = 'high'
        elif total_nearby_volume > 50000000:  # $50M threshold
            analysis['risk_assessment'] = 'medium'
        
        return analysis
    
    def get_market_sentiment_score(self, symbol: str = "BTCUSDT") -> Dict[str, Any]:
        """
        Calculate overall market sentiment from CoinGlass data
        Combines OI, funding rates, and liquidation patterns
        """
        try:
            # Get all data sources
            oi_data = self.get_open_interest_data(symbol)
            funding_rates = self.get_funding_rates(symbol)
            liquidation_zones = self.get_liquidation_heatmap(symbol)
            
            sentiment_score = 50  # Neutral baseline
            factors = []
            
            # Open Interest sentiment
            if oi_data:
                if oi_data.long_ratio > 60:
                    sentiment_score += 10
                    factors.append("High long ratio (bullish)")
                elif oi_data.short_ratio > 60:
                    sentiment_score -= 10
                    factors.append("High short ratio (bearish)")
                
                if oi_data.oi_change_percent > 10:
                    sentiment_score += 5
                    factors.append("Growing open interest (increasing conviction)")
                elif oi_data.oi_change_percent < -10:
                    sentiment_score -= 5
                    factors.append("Declining open interest (weakening conviction)")
            
            # Funding rates sentiment
            if funding_rates:
                avg_funding = np.mean([rate.funding_rate for rate in funding_rates])
                
                if avg_funding > 0.01:  # 1% funding
                    sentiment_score -= 15
                    factors.append("High positive funding (extremely bullish, contrarian bearish)")
                elif avg_funding < -0.005:  # -0.5% funding
                    sentiment_score += 15
                    factors.append("Negative funding (bearish sentiment, contrarian bullish)")
            
            # Liquidation zones sentiment
            if liquidation_zones:
                long_liq_volume = sum(zone.volume for zone in liquidation_zones if zone.side == 'long')
                short_liq_volume = sum(zone.volume for zone in liquidation_zones if zone.side == 'short')
                
                if long_liq_volume > short_liq_volume * 1.5:
                    sentiment_score -= 8
                    factors.append("Heavy long liquidation zones (vulnerable longs)")
                elif short_liq_volume > long_liq_volume * 1.5:
                    sentiment_score += 8
                    factors.append("Heavy short liquidation zones (vulnerable shorts)")
            
            # Clamp score between 0-100
            sentiment_score = max(0, min(100, sentiment_score))
            
            # Determine sentiment label
            if sentiment_score >= 70:
                sentiment_label = "Extremely Bullish"
            elif sentiment_score >= 60:
                sentiment_label = "Bullish"
            elif sentiment_score >= 40:
                sentiment_label = "Neutral"
            elif sentiment_score >= 30:
                sentiment_label = "Bearish"
            else:
                sentiment_label = "Extremely Bearish"
            
            return {
                'sentiment_score': sentiment_score,
                'sentiment_label': sentiment_label,
                'contributing_factors': factors,
                'data_sources_used': {
                    'open_interest': oi_data is not None,
                    'funding_rates': len(funding_rates) > 0,
                    'liquidation_zones': len(liquidation_zones) > 0
                },
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating sentiment score: {e}")
            return {
                'sentiment_score': 50,
                'sentiment_label': "Unknown",
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get CoinGlass integration system status"""
        return {
            'api_key_configured': self.api_key is not None,
            'cache_size': len(self.cache),
            'last_request_time': datetime.fromtimestamp(self.last_request_time).isoformat() if self.last_request_time > 0 else None,
            'rate_limit_interval': self.min_request_interval,
            'supported_endpoints': [
                'liquidation_heatmap',
                'open_interest', 
                'funding_rates',
                'sentiment_analysis'
            ],
            'integration_ready': True
        }

# Global instance (will be properly initialized when API key available)
coinglass_analyzer = CoinGlassAnalyzer()

def get_coinglass_analyzer():
    """Get the global CoinGlass analyzer instance"""
    return coinglass_analyzer

if __name__ == "__main__":
    # Demo/testing mode
    analyzer = CoinGlassAnalyzer()
    
    print("CoinGlass Analyzer Demo")
    print("=" * 40)
    
    # Test basic functionality
    status = analyzer.get_system_status()
    print(f"System Status: {json.dumps(status, indent=2)}")
    
    # Test data retrieval (demo mode)
    liquidation_zones = analyzer.get_liquidation_heatmap("BTCUSDT")
    print(f"\nLiquidation Zones Found: {len(liquidation_zones)}")
    
    oi_data = analyzer.get_open_interest_data("BTCUSDT")
    print(f"Open Interest Data Available: {oi_data is not None}")
    
    sentiment = analyzer.get_market_sentiment_score("BTCUSDT")
    print(f"\nMarket Sentiment: {sentiment['sentiment_label']} ({sentiment['sentiment_score']}/100)")