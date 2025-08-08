#!/usr/bin/env python3
"""
OKX API Maximizer
Memaksimalkan fitur-fitur OKX API gratis yang terbukti bekerja
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from core.okx_fetcher import OKXFetcher

logger = logging.getLogger(__name__)

class OKXMaximizer:
    """
    Maximizer untuk OKX API dengan fokus pada fitur yang terbukti working
    """
    
    def __init__(self):
        self.okx_fetcher = OKXFetcher()
        logger.info("🚀 OKX Maximizer initialized")
    
    def get_funding_rate_trends(self, symbol: str, limit: int = 50) -> Dict[str, Any]:
        """
        📈 Analisis trend funding rate untuk prediksi sentiment
        """
        try:
            # Get funding rate history
            funding_history = []
            current_funding = self.okx_fetcher.get_funding_rate(symbol)
            
            if current_funding:
                funding_history.append({
                    'funding_rate': current_funding['funding_rate'],
                    'timestamp': datetime.now().isoformat(),
                    'next_funding_time': current_funding['next_funding_time']
                })
            
            # Analisis trend
            analysis = {
                'symbol': symbol,
                'current_funding_rate': current_funding['funding_rate'] if current_funding else 0,
                'funding_rate_percent': (current_funding['funding_rate'] * 100) if current_funding else 0,
                'next_funding_time': current_funding['next_funding_time'] if current_funding else None,
                'sentiment_analysis': self._analyze_funding_sentiment(current_funding['funding_rate'] if current_funding else 0),
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"📈 Funding rate analysis completed for {symbol}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing funding rates for {symbol}: {e}")
            return {'error': str(e)}
    
    def _analyze_funding_sentiment(self, funding_rate: float) -> Dict[str, Any]:
        """
        Analisis sentiment berdasarkan funding rate
        """
        rate_percent = funding_rate * 100
        
        if rate_percent > 0.05:
            sentiment = "VERY_BULLISH"
            description = "Sangat bullish - Long traders bayar funding tinggi"
        elif rate_percent > 0.01:
            sentiment = "BULLISH"
            description = "Bullish - Long traders dominan"
        elif rate_percent > -0.01:
            sentiment = "NEUTRAL"
            description = "Neutral - Funding rate seimbang"
        elif rate_percent > -0.05:
            sentiment = "BEARISH"
            description = "Bearish - Short traders dominan"
        else:
            sentiment = "VERY_BEARISH"
            description = "Sangat bearish - Short traders bayar funding tinggi"
        
        return {
            'sentiment': sentiment,
            'description': description,
            'rate_percent': round(rate_percent, 4),
            'strength': min(abs(rate_percent) * 20, 100)  # 0-100 scale
        }
    
    def get_price_risk_analysis(self, symbol: str) -> Dict[str, Any]:
        """
        ⚡ Analisis risiko berdasarkan price limits
        """
        try:
            # Get current price and limits
            ticker = self.okx_fetcher.get_ticker(symbol)
            
            if not ticker:
                return {'error': 'Failed to get ticker data'}
            
            current_price = float(ticker.get('last', 0))
            
            # Get price limits (menggunakan request langsung karena method belum ada)
            import requests
            url = f"{self.okx_fetcher.base_url}/api/v5/public/price-limit"
            params = {'instId': symbol}
            
            response = requests.get(url, params=params, timeout=10)
            price_limit_data = response.json()
            
            if price_limit_data.get('code') == '0' and price_limit_data.get('data'):
                limit_data = price_limit_data['data'][0]
                buy_limit = float(limit_data.get('buyLmt', 0))
                sell_limit = float(limit_data.get('sellLmt', 0))
            else:
                return {'error': 'Failed to get price limits'}
            
            # Calculate risk metrics
            upside_risk = ((buy_limit - current_price) / current_price) * 100
            downside_risk = ((current_price - sell_limit) / current_price) * 100
            
            risk_analysis = {
                'symbol': symbol,
                'current_price': current_price,
                'buy_limit': buy_limit,
                'sell_limit': sell_limit,
                'upside_limit_percent': round(upside_risk, 2),
                'downside_limit_percent': round(downside_risk, 2),
                'risk_assessment': self._assess_price_risk(upside_risk, downside_risk),
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"⚡ Price risk analysis completed for {symbol}")
            return risk_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing price risk for {symbol}: {e}")
            return {'error': str(e)}
    
    def _assess_price_risk(self, upside: float, downside: float) -> Dict[str, Any]:
        """
        Assess price risk berdasarkan jarak ke limit
        """
        avg_risk = (upside + downside) / 2
        
        if avg_risk > 5:
            risk_level = "LOW"
            description = "Harga jauh dari limit, risiko rendah"
        elif avg_risk > 2:
            risk_level = "MEDIUM"
            description = "Harga mendekati limit, waspada"
        else:
            risk_level = "HIGH"
            description = "Harga sangat dekat limit, risiko tinggi"
        
        return {
            'risk_level': risk_level,
            'description': description,
            'average_distance_percent': round(avg_risk, 2)
        }
    
    def get_market_depth_analysis(self, symbol: str, depth: int = 20) -> Dict[str, Any]:
        """
        📊 Analisis kedalaman market dari orderbook
        """
        try:
            orderbook = self.okx_fetcher.get_orderbook(symbol, depth)
            
            if not orderbook or not orderbook.get('bids') or not orderbook.get('asks'):
                return {'error': 'Failed to get orderbook data'}
            
            bids = orderbook['bids'][:depth]
            asks = orderbook['asks'][:depth]
            
            # Calculate depth metrics
            total_bid_volume = sum(float(bid[1]) for bid in bids)
            total_ask_volume = sum(float(ask[1]) for ask in asks)
            
            best_bid = float(bids[0][0]) if bids else 0
            best_ask = float(asks[0][0]) if asks else 0
            
            spread = best_ask - best_bid
            spread_percent = (spread / best_bid) * 100 if best_bid > 0 else 0
            
            # Bid/Ask imbalance
            total_volume = total_bid_volume + total_ask_volume
            bid_dominance = (total_bid_volume / total_volume) * 100 if total_volume > 0 else 50
            ask_dominance = (total_ask_volume / total_volume) * 100 if total_volume > 0 else 50
            
            depth_analysis = {
                'symbol': symbol,
                'best_bid': best_bid,
                'best_ask': best_ask,
                'spread': spread,
                'spread_percent': round(spread_percent, 4),
                'total_bid_volume': total_bid_volume,
                'total_ask_volume': total_ask_volume,
                'bid_dominance_percent': round(bid_dominance, 2),
                'ask_dominance_percent': round(ask_dominance, 2),
                'market_sentiment': self._analyze_orderbook_sentiment(bid_dominance),
                'liquidity_assessment': self._assess_liquidity(total_volume, spread_percent),
                'depth_levels': len(bids),
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"📊 Market depth analysis completed for {symbol}")
            return depth_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing market depth for {symbol}: {e}")
            return {'error': str(e)}
    
    def _analyze_orderbook_sentiment(self, bid_dominance: float) -> Dict[str, Any]:
        """
        Analisis sentiment dari orderbook imbalance
        """
        if bid_dominance > 60:
            sentiment = "BULLISH"
            description = "Bid volume dominan - tekanan beli kuat"
        elif bid_dominance > 55:
            sentiment = "SLIGHTLY_BULLISH"
            description = "Bid volume sedikit dominan"
        elif bid_dominance > 45:
            sentiment = "NEUTRAL"
            description = "Bid/Ask volume seimbang"
        elif bid_dominance > 40:
            sentiment = "SLIGHTLY_BEARISH"
            description = "Ask volume sedikit dominan"
        else:
            sentiment = "BEARISH"
            description = "Ask volume dominan - tekanan jual kuat"
        
        return {
            'sentiment': sentiment,
            'description': description,
            'strength': abs(bid_dominance - 50) * 2  # 0-100 scale
        }
    
    def _assess_liquidity(self, total_volume: float, spread_percent: float) -> Dict[str, Any]:
        """
        Assess liquidity berdasarkan volume dan spread
        """
        if spread_percent < 0.01 and total_volume > 1000:
            liquidity = "HIGH"
            description = "Likuiditas tinggi - spread ketat, volume besar"
        elif spread_percent < 0.05 and total_volume > 100:
            liquidity = "MEDIUM"
            description = "Likuiditas sedang"
        else:
            liquidity = "LOW"
            description = "Likuiditas rendah - spread lebar atau volume kecil"
        
        return {
            'liquidity_level': liquidity,
            'description': description
        }
    
    def get_comprehensive_okx_analysis(self, symbol: str) -> Dict[str, Any]:
        """
        🔥 Analisis komprehensif menggunakan semua fitur OKX yang working
        """
        logger.info(f"🔍 Starting comprehensive OKX analysis for {symbol}")
        
        analysis = {
            'symbol': symbol,
            'analysis_timestamp': datetime.now().isoformat(),
            'components': {}
        }
        
        # 1. Basic market data
        ticker = self.okx_fetcher.get_ticker(symbol)
        if ticker:
            analysis['components']['market_data'] = {
                'price': float(ticker.get('last', 0)),
                'volume_24h': float(ticker.get('vol24h', 0)),
                'change_24h': float(ticker.get('chg24h', 0)),
                'high_24h': float(ticker.get('high24h', 0)),
                'low_24h': float(ticker.get('low24h', 0))
            }
        
        # 2. Funding rate analysis
        analysis['components']['funding_analysis'] = self.get_funding_rate_trends(symbol)
        
        # 3. Price risk analysis
        analysis['components']['risk_analysis'] = self.get_price_risk_analysis(symbol)
        
        # 4. Market depth analysis
        analysis['components']['depth_analysis'] = self.get_market_depth_analysis(symbol)
        
        # 5. Open interest (jika futures/swap)
        if 'SWAP' in symbol or 'FUTURES' in symbol:
            oi = self.okx_fetcher.get_open_interest(symbol)
            if oi:
                analysis['components']['open_interest'] = {
                    'open_interest': oi['open_interest'],
                    'open_interest_ccy': oi['open_interest_ccy']
                }
        
        # 6. Overall assessment
        analysis['overall_assessment'] = self._generate_overall_assessment(analysis['components'])
        
        logger.info(f"✅ Comprehensive OKX analysis completed for {symbol}")
        return analysis
    
    def _generate_overall_assessment(self, components: Dict) -> Dict[str, Any]:
        """
        Generate overall assessment dari semua komponen analisis
        """
        assessment = {
            'overall_sentiment': 'NEUTRAL',
            'confidence': 0,
            'key_insights': [],
            'risk_factors': [],
            'opportunities': []
        }
        
        # Analyze funding sentiment
        funding = components.get('funding_analysis', {})
        if funding and 'sentiment_analysis' in funding:
            funding_sentiment = funding['sentiment_analysis']['sentiment']
            assessment['key_insights'].append(
                f"Funding rate sentiment: {funding_sentiment}"
            )
        
        # Analyze orderbook sentiment
        depth = components.get('depth_analysis', {})
        if depth and 'market_sentiment' in depth:
            ob_sentiment = depth['market_sentiment']['sentiment']
            assessment['key_insights'].append(
                f"Orderbook sentiment: {ob_sentiment}"
            )
        
        # Risk analysis
        risk = components.get('risk_analysis', {})
        if risk and 'risk_assessment' in risk:
            risk_level = risk['risk_assessment']['risk_level']
            if risk_level == 'HIGH':
                assessment['risk_factors'].append("Price near limits - high volatility risk")
            elif risk_level == 'LOW':
                assessment['opportunities'].append("Price far from limits - room for movement")
        
        return assessment

# Global instance
okx_maximizer = OKXMaximizer()

def get_okx_maximizer():
    """Get global OKX maximizer instance"""
    return okx_maximizer