#!/usr/bin/env python3
"""
Enhanced OKX API Fetcher
Memaksimalkan semua fitur gratis OKX API untuk analisis trading yang lebih komprehensif
"""

import requests
import pandas as pd
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import time
import json

logger = logging.getLogger(__name__)

class EnhancedOKXFetcher:
    """
    Enhanced OKX API client dengan fitur lengkap
    Menggunakan semua endpoint gratis untuk analisis maksimal
    """
    
    def __init__(self):
        self.base_url = "https://www.okx.com"
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 GPTs-System/1.0'
        })
        self.last_request_time = 0
        self.rate_limit_delay = 0.1  # 100ms between requests
        
        logger.info("🔄 Enhanced OKX Fetcher initialized")
    
    def _rate_limit(self):
        """Rate limiting untuk menghindari ban"""
        current_time = time.time()
        elapsed = current_time - self.last_request_time
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)
        self.last_request_time = time.time()
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Helper untuk membuat request dengan error handling"""
        try:
            self._rate_limit()
            
            url = f"{self.base_url}{endpoint}"
            response = self.session.get(url, params=params or {}, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('code') == '0':
                return data.get('data', [])
            else:
                logger.error(f"OKX API error: {data}")
                return None
                
        except Exception as e:
            logger.error(f"Request error for {endpoint}: {e}")
            return None

    # ===== MARKET DATA ENDPOINTS =====
    
    def get_liquidation_orders(self, inst_type: str = "SWAP", state: str = "filled", limit: int = 100) -> Optional[List[Dict]]:
        """
        🔥 Get liquidation orders - KEY FEATURE untuk analisis liquidation
        """
        params = {
            'instType': inst_type,  # SPOT, SWAP, FUTURES, OPTION
            'state': state,         # filled, unfilled
            'limit': str(min(limit, 100))
        }
        
        data = self._make_request('/api/v5/public/liquidation-orders', params)
        
        if data:
            liquidations = []
            for liq in data:
                liquidations.append({
                    'inst_id': liq.get('instId'),
                    'side': liq.get('side'),
                    'total_loss': float(liq.get('totalLoss', 0)),
                    'details': liq.get('details', []),
                    'timestamp': liq.get('ts')
                })
            
            logger.info(f"📊 Fetched {len(liquidations)} liquidation orders")
            return liquidations
        
        return None
    
    def get_position_tiers(self, inst_type: str = "SWAP", symbol: str = "BTC-USDT-SWAP") -> Optional[List[Dict]]:
        """
        📊 Get position tiers - untuk risk management
        """
        params = {
            'instType': inst_type,
            'instId': symbol
        }
        
        data = self._make_request('/api/v5/public/position-tiers', params)
        
        if data:
            tiers = []
            for tier in data:
                tiers.append({
                    'base_max_loan': float(tier.get('baseMaxLoan', 0)),
                    'imr': float(tier.get('imr', 0)),  # Initial Margin Ratio
                    'max_leverage': float(tier.get('maxLever', 0)),
                    'max_size': float(tier.get('maxSz', 0)),
                    'min_size': float(tier.get('minSz', 0)),
                    'mmr': float(tier.get('mmr', 0)),  # Maintenance Margin Ratio
                    'opt_mgnr': float(tier.get('optMgnr', 0)),
                    'quote_max_loan': float(tier.get('quoteMaxLoan', 0)),
                    'tier': tier.get('tier'),
                    'uly': tier.get('uly')
                })
            
            logger.info(f"📊 Fetched {len(tiers)} position tiers for {symbol}")
            return tiers
        
        return None
    
    def get_interest_rate_loan_quota(self, currency: str = "BTC") -> Optional[List[Dict]]:
        """
        💰 Get interest rates and loan quotas
        """
        data = self._make_request('/api/v5/public/interest-rate-loan-quota')
        
        if data:
            rates = []
            for rate in data:
                if not currency or rate.get('ccy', '').upper() == currency.upper():
                    rates.append({
                        'currency': rate.get('ccy'),
                        'interest_rate': float(rate.get('rate', 0)),
                        'loan_quota': float(rate.get('loanQuota', 0)),
                        'surplus_quota': float(rate.get('surplusQuota', 0))
                    })
            
            logger.info(f"💰 Fetched interest rates for {len(rates)} currencies")
            return rates
        
        return None
    
    def get_vip_interest_rate_loan_quota(self) -> Optional[List[Dict]]:
        """
        ⭐ Get VIP interest rates and loan quotas
        """
        data = self._make_request('/api/v5/public/vip-interest-rate-loan-quota')
        
        if data:
            vip_rates = []
            for rate in data:
                vip_rates.append({
                    'currency': rate.get('ccy'),
                    'irDiscount': float(rate.get('irDiscount', 0)),
                    'loanQuotaCoef': float(rate.get('loanQuotaCoef', 0)),
                    'level': rate.get('level')
                })
            
            logger.info(f"⭐ Fetched VIP rates for {len(vip_rates)} currencies")
            return vip_rates
        
        return None
    
    def get_underlying(self, inst_type: str = "SWAP") -> Optional[List[str]]:
        """
        📋 Get list of underlying assets
        """
        params = {'instType': inst_type}
        data = self._make_request('/api/v5/public/underlying', params)
        
        if data:
            underlying_list = [item for item in data if item]
            logger.info(f"📋 Fetched {len(underlying_list)} underlying assets")
            return underlying_list
        
        return None
    
    def get_insurance_fund(self, inst_type: str = "SWAP", currency: str = "BTC") -> Optional[List[Dict]]:
        """
        🛡️ Get insurance fund data
        """
        params = {
            'instType': inst_type,
            'ccy': currency
        }
        
        data = self._make_request('/api/v5/public/insurance-fund', params)
        
        if data:
            insurance_data = []
            for fund in data:
                insurance_data.append({
                    'currency': fund.get('ccy'),
                    'amount': float(fund.get('amt', 0)),
                    'inst_type': fund.get('instType'),
                    'timestamp': fund.get('ts')
                })
            
            logger.info(f"🛡️ Fetched insurance fund data for {currency}")
            return insurance_data
        
        return None
    
    def get_option_summary(self, currency: str = "BTC") -> Optional[List[Dict]]:
        """
        📊 Get option market summary
        """
        params = {'ccy': currency}
        data = self._make_request('/api/v5/public/opt-summary', params)
        
        if data:
            option_summary = []
            for opt in data:
                option_summary.append({
                    'currency': opt.get('ccy'),
                    'inst_id': opt.get('instId'),
                    'delta': float(opt.get('delta', 0)),
                    'gamma': float(opt.get('gamma', 0)),
                    'theta': float(opt.get('theta', 0)),
                    'vega': float(opt.get('vega', 0)),
                    'mark_vol': float(opt.get('markVol', 0)),
                    'bid_vol': float(opt.get('bidVol', 0)),
                    'ask_vol': float(opt.get('askVol', 0)),
                    'realized_vol': float(opt.get('realVol', 0)),
                    'timestamp': opt.get('ts')
                })
            
            logger.info(f"📊 Fetched option summary for {currency}")
            return option_summary
        
        return None
    
    def get_funding_rate_history(self, symbol: str, limit: int = 100) -> Optional[List[Dict]]:
        """
        📈 Get funding rate history - untuk analisis tren
        """
        params = {
            'instId': symbol,
            'limit': str(min(limit, 100))
        }
        
        data = self._make_request('/api/v5/public/funding-rate-history', params)
        
        if data:
            funding_history = []
            for rate in data:
                funding_history.append({
                    'inst_id': rate.get('instId'),
                    'funding_rate': float(rate.get('fundingRate', 0)),
                    'funding_time': rate.get('fundingTime'),
                    'realized_rate': float(rate.get('realizedRate', 0))
                })
            
            logger.info(f"📈 Fetched {len(funding_history)} funding rate history for {symbol}")
            return funding_history
        
        return None
    
    def get_price_limit(self, symbol: str) -> Optional[Dict]:
        """
        ⚡ Get price limits - untuk risk management
        """
        params = {'instId': symbol}
        data = self._make_request('/api/v5/public/price-limit', params)
        
        if data and len(data) > 0:
            limit_data = data[0]
            return {
                'inst_id': limit_data.get('instId'),
                'buy_limit': float(limit_data.get('buyLmt', 0)),
                'sell_limit': float(limit_data.get('sellLmt', 0)),
                'timestamp': limit_data.get('ts')
            }
        
        return None
    
    def get_option_trades(self, symbol: str, limit: int = 100) -> Optional[List[Dict]]:
        """
        📊 Get option trades data
        """
        params = {
            'instId': symbol,
            'limit': str(min(limit, 100))
        }
        
        data = self._make_request('/api/v5/public/option-trades', params)
        
        if data:
            trades = []
            for trade in data:
                trades.append({
                    'inst_id': trade.get('instId'),
                    'trade_id': trade.get('tradeId'),
                    'price': float(trade.get('px', 0)),
                    'size': float(trade.get('sz', 0)),
                    'side': trade.get('side'),
                    'timestamp': trade.get('ts'),
                    'fill_vol': float(trade.get('fillVol', 0)),
                    'forward_price': float(trade.get('fwdPx', 0)),
                    'index_price': float(trade.get('idxPx', 0)),
                    'mark_price': float(trade.get('markPx', 0))
                })
            
            logger.info(f"📊 Fetched {len(trades)} option trades for {symbol}")
            return trades
        
        return None
    
    def get_comprehensive_market_data(self, symbol: str) -> Dict[str, Any]:
        """
        🔥 COMPREHENSIVE MARKET ANALYSIS
        Mengumpulkan semua data market dalam satu fungsi
        """
        logger.info(f"🔍 Fetching comprehensive market data for {symbol}")
        
        market_data = {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'data': {}
        }
        
        # Basic market data
        market_data['data']['ticker'] = self._make_request('/api/v5/market/ticker', {'instId': symbol})
        market_data['data']['orderbook'] = self._make_request('/api/v5/market/books', {'instId': symbol, 'sz': '20'})
        
        # Derivatives data (jika applicable)
        if 'SWAP' in symbol or 'FUTURES' in symbol:
            market_data['data']['funding_rate'] = self._make_request('/api/v5/public/funding-rate', {'instId': symbol})
            market_data['data']['open_interest'] = self._make_request('/api/v5/public/open-interest', {'instId': symbol})
            market_data['data']['price_limit'] = self._make_request('/api/v5/public/price-limit', {'instId': symbol})
            market_data['data']['position_tiers'] = self.get_position_tiers(symbol=symbol)
            market_data['data']['funding_history'] = self.get_funding_rate_history(symbol, limit=20)
        
        # Market-wide data
        market_data['data']['liquidations'] = self.get_liquidation_orders(limit=50)
        
        # Options data (jika BTC atau ETH)
        if 'BTC' in symbol or 'ETH' in symbol:
            base_currency = symbol.split('-')[0]
            market_data['data']['option_summary'] = self.get_option_summary(base_currency)
            market_data['data']['insurance_fund'] = self.get_insurance_fund(currency=base_currency)
        
        logger.info(f"✅ Comprehensive market data compiled for {symbol}")
        return market_data
    
    def get_enhanced_liquidation_analysis(self, inst_type: str = "SWAP", limit: int = 100) -> Dict[str, Any]:
        """
        🔥 ENHANCED LIQUIDATION ANALYSIS
        Analisis liquidation yang mendalam untuk prediksi market movement
        """
        logger.info("🔍 Performing enhanced liquidation analysis")
        
        liquidations = self.get_liquidation_orders(inst_type, limit=limit)
        
        if not liquidations:
            return {'status': 'error', 'message': 'No liquidation data available'}
        
        analysis = {
            'total_liquidations': len(liquidations),
            'total_loss': 0,
            'long_liquidations': 0,
            'short_liquidations': 0,
            'top_symbols': {},
            'liquidation_timeline': [],
            'analysis_timestamp': datetime.now().isoformat()
        }
        
        for liq in liquidations:
            # Calculate totals
            loss = liq.get('total_loss', 0)
            analysis['total_loss'] += loss
            
            # Count sides
            side = liq.get('side', '').lower()
            if side == 'long':
                analysis['long_liquidations'] += 1
            elif side == 'short':
                analysis['short_liquidations'] += 1
            
            # Track symbols
            symbol = liq.get('inst_id', 'unknown')
            if symbol not in analysis['top_symbols']:
                analysis['top_symbols'][symbol] = {'count': 0, 'total_loss': 0}
            
            analysis['top_symbols'][symbol]['count'] += 1
            analysis['top_symbols'][symbol]['total_loss'] += loss
            
            # Timeline
            analysis['liquidation_timeline'].append({
                'timestamp': liq.get('timestamp'),
                'symbol': symbol,
                'side': side,
                'loss': loss
            })
        
        # Sort symbols by total loss
        analysis['top_symbols'] = dict(sorted(
            analysis['top_symbols'].items(),
            key=lambda x: x[1]['total_loss'],
            reverse=True
        )[:10])  # Top 10
        
        # Calculate ratios
        total_sided = analysis['long_liquidations'] + analysis['short_liquidations']
        if total_sided > 0:
            analysis['long_ratio'] = analysis['long_liquidations'] / total_sided
            analysis['short_ratio'] = analysis['short_liquidations'] / total_sided
        else:
            analysis['long_ratio'] = 0
            analysis['short_ratio'] = 0
        
        logger.info(f"✅ Enhanced liquidation analysis completed: {analysis['total_liquidations']} liquidations analyzed")
        return analysis

# Global instance
enhanced_okx_fetcher = EnhancedOKXFetcher()

def get_enhanced_okx_fetcher():
    """Get global enhanced OKX fetcher instance"""
    return enhanced_okx_fetcher