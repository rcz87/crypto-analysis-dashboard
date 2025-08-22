#!/usr/bin/env python3
"""
Shared Service Layer - Priority 2 Implementation
Eliminates code duplication between signal endpoints and provides reusable services
"""

import logging
from typing import Dict, Any, Optional, List
import pandas as pd
from datetime import datetime

from core.professional_smc_analyzer import ProfessionalSMCAnalyzer
from core.personalized_risk_profiles import PersonalizedRiskProfiles
from core.advanced_ml_ensemble import AdvancedMLEnsemble
from core.okx_fetcher import OKXFetcher
from core.universal_cache_system import get_universal_cache, cache_market_data, get_cached_market_data

logger = logging.getLogger(__name__)


class SharedTradingServices:
    """
    Centralized trading services to eliminate duplication across endpoints:
    - signal_top_endpoints.py
    - enhanced_signal_endpoints.py  
    - ai_reasoning_endpoints.py
    """
    
    def __init__(self):
        # Initialize core components
        self.smc_analyzer = ProfessionalSMCAnalyzer()
        self.risk_profiler = PersonalizedRiskProfiles()
        self.ml_ensemble = AdvancedMLEnsemble()
        self.okx_fetcher = OKXFetcher()
        self.cache = get_universal_cache()
        
        self.logger = logging.getLogger(f"{__name__}.SharedTradingServices")
        self.logger.info("🔧 Shared Trading Services initialized - Eliminating code duplication")
    
    def get_market_data_cached(self, symbol: str, timeframe: str, 
                              limit: int = 100) -> Optional[Dict[str, Any]]:
        """
        Get market data with intelligent caching
        Reduces OKX API calls and respects 120 req/min rate limit
        """
        # Check cache first
        cached_data = get_cached_market_data(symbol, timeframe)
        if cached_data:
            self.logger.info(f"📊 Market data cache hit: {symbol} {timeframe}")
            return cached_data
        
        # Fetch fresh data
        try:
            market_data = self.okx_fetcher.get_historical_data(symbol, timeframe, limit)
            if market_data:
                # Cache with appropriate TTL based on timeframe
                ttl_minutes = self._get_market_data_ttl(timeframe)
                cache_market_data(symbol, timeframe, market_data, ttl_minutes)
                self.logger.info(f"📊 Fresh market data cached: {symbol} {timeframe}")
                return market_data
        except Exception as e:
            self.logger.error(f"Failed to fetch market data: {e}")
            
        return None
    
    def _get_market_data_ttl(self, timeframe: str) -> int:
        """Get appropriate TTL based on timeframe"""
        ttl_map = {
            '1m': 1, '3m': 2, '5m': 3, '15m': 5, '30m': 8,
            '1H': 10, '2H': 15, '4H': 20, '6H': 25, '12H': 30,
            '1D': 60, '3D': 180, '1W': 360
        }
        return ttl_map.get(timeframe, 5)  # Default 5 minutes
    
    def analyze_smc_cached(self, symbol: str, timeframe: str, 
                          market_data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        SMC analysis with caching to avoid recalculation
        """
        # Create cache key
        cache_key = {'symbol': symbol, 'timeframe': timeframe, 'type': 'smc_analysis'}
        
        # Check cache
        cached_analysis = self.cache.get(cache_key, 'api')
        if cached_analysis:
            self.logger.info(f"📈 SMC analysis cache hit: {symbol}")
            return cached_analysis
        
        # Get market data if not provided
        if not market_data:
            market_data = self.get_market_data_cached(symbol, timeframe)
            if not market_data:
                return {'error': 'No market data available'}
        
        # Perform SMC analysis
        try:
            smc_analysis = self.smc_analyzer.analyze_smart_money_concept(
                candles=market_data.get('candles', []),
                symbol=symbol,
                timeframe=timeframe
            )
            
            # Cache the analysis
            self.cache.set(cache_key, smc_analysis, 'api', priority=2)
            self.logger.info(f"📈 SMC analysis completed and cached: {symbol}")
            
            return smc_analysis
            
        except Exception as e:
            self.logger.error(f"SMC analysis failed: {e}")
            return {'error': f'SMC analysis failed: {e}'}
    
    def apply_risk_management(self, signal_data: Dict[str, Any],
                             risk_profile: str = 'MODERATE',
                             account_balance: float = 10000,
                             market_data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Apply personalized risk management to trading signal
        Centralized logic to avoid duplication
        """
        try:
            # Update risk profile if needed
            if risk_profile != self.risk_profiler.current_profile:
                self.risk_profiler.change_profile(risk_profile)
            
            if account_balance != self.risk_profiler.account_balance:
                self.risk_profiler.account_balance = account_balance
            
            # Create dataframe for risk calculation
            if market_data and market_data.get('candles'):
                df = pd.DataFrame(market_data['candles'])
                # Ensure numeric types
                for col in ['open', 'high', 'low', 'close', 'volume']:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
            else:
                # Create minimal dataframe
                df = pd.DataFrame({
                    'close': [signal_data.get('entry_price', 0)] * 20,
                    'high': [signal_data.get('entry_price', 0) * 1.01] * 20,
                    'low': [signal_data.get('entry_price', 0) * 0.99] * 20,
                    'open': [signal_data.get('entry_price', 0)] * 20,
                    'volume': [1000000] * 20
                })
            
            # Calculate personalized risk
            risk_params = self.risk_profiler.calculate_personalized_risk(
                df=df,
                signal_type=signal_data.get('signal', 'BUY'),
                confidence=signal_data.get('confidence', 70),
                entry_price=signal_data.get('entry_price')
            )
            
            if risk_params.get('allowed'):
                # Enhance signal with risk management
                enhanced_signal = signal_data.copy()
                enhanced_signal.update({
                    'risk_management': risk_params,
                    'position_sizing': risk_params.get('position_sizing', {}),
                    'risk_profile': risk_profile,
                    'account_balance': account_balance
                })
                
                self.logger.info(f"✅ Risk management applied - Profile: {risk_profile}")
                return enhanced_signal
            else:
                self.logger.warning(f"⚠️ Signal rejected by risk management: {risk_params.get('reason', 'Unknown')}")
                return {
                    **signal_data,
                    'risk_rejected': True,
                    'rejection_reason': risk_params.get('reason', 'Risk criteria not met'),
                    'risk_profile': risk_profile
                }
                
        except Exception as e:
            self.logger.error(f"Risk management failed: {e}")
            return {
                **signal_data,
                'risk_error': True,
                'risk_error_message': str(e)
            }
    
    def apply_ml_ensemble(self, signal_data: Dict[str, Any],
                         market_data: Optional[Dict] = None,
                         use_ensemble: bool = True) -> Dict[str, Any]:
        """
        Apply ML ensemble prediction to enhance signal
        Centralized ML logic with caching
        """
        if not use_ensemble or not market_data:
            return signal_data
        
        try:
            # Create cache key for ML prediction
            input_hash = hash(str(market_data.get('candles', [])[-20:]))  # Last 20 candles
            cache_key = {'type': 'ml_ensemble', 'input_hash': input_hash, 
                        'symbol': signal_data.get('symbol', 'unknown')}
            
            # Check ML cache
            cached_prediction = self.cache.get(cache_key, 'ml')
            if cached_prediction:
                self.logger.info("🤖 ML ensemble cache hit")
                enhanced_signal = signal_data.copy()
                enhanced_signal['ml_ensemble'] = cached_prediction
                return enhanced_signal
            
            # Create dataframe
            df = pd.DataFrame(market_data['candles'])
            for col in ['open', 'high', 'low', 'close', 'volume']:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Get ensemble prediction
            ensemble_result = self.ml_ensemble.get_ensemble_prediction(df)
            
            # Cache ML prediction
            self.cache.set(cache_key, ensemble_result, 'ml', priority=2)
            
            # Merge with existing signal
            enhanced_signal = signal_data.copy()
            enhanced_signal['ml_ensemble'] = ensemble_result
            
            # Combine confidence scores
            if 'confidence' in signal_data and 'ensemble_prediction' in ensemble_result:
                original_conf = signal_data.get('confidence', 70)
                ensemble_conf = ensemble_result['ensemble_prediction'].get('confidence', 0.7) * 100
                combined_conf = (original_conf + ensemble_conf) / 2
                
                enhanced_signal.update({
                    'confidence': combined_conf,
                    'confidence_sources': {
                        'original': original_conf,
                        'ensemble': ensemble_conf,
                        'combined': combined_conf
                    }
                })
            
            self.logger.info("🤖 ML ensemble applied successfully")
            return enhanced_signal
            
        except Exception as e:
            self.logger.warning(f"ML ensemble failed: {e}")
            return signal_data
    
    def generate_unified_signal(self, symbol: str, timeframe: str,
                               risk_profile: str = 'MODERATE',
                               account_balance: float = 10000,
                               use_ml_ensemble: bool = True,
                               use_smc: bool = True) -> Dict[str, Any]:
        """
        Generate unified trading signal using all shared services
        This replaces duplicated logic across endpoints
        """
        try:
            # 1. Get market data (cached)
            market_data = self.get_market_data_cached(symbol, timeframe)
            if not market_data:
                return {
                    'error': 'Failed to fetch market data',
                    'symbol': symbol,
                    'timeframe': timeframe,
                    'timestamp': datetime.now().isoformat()
                }
            
            # 2. Basic signal structure
            current_price = float(market_data.get('current_price', 0))
            signal_data = {
                'symbol': symbol,
                'timeframe': timeframe,
                'current_price': current_price,
                'entry_price': current_price,
                'signal': 'NEUTRAL',  # Default
                'confidence': 60,     # Default
                'timestamp': datetime.now().isoformat()
            }
            
            # 3. Apply SMC analysis if requested
            if use_smc:
                smc_analysis = self.analyze_smc_cached(symbol, timeframe, market_data)
                signal_data['smc_analysis'] = smc_analysis
                
                # Extract signal from SMC if available
                if 'signal' in smc_analysis and smc_analysis['signal'] != 'NEUTRAL':
                    signal_data['signal'] = smc_analysis['signal']
                    signal_data['confidence'] = smc_analysis.get('confidence', 60)
            
            # 4. Apply ML ensemble if requested
            if use_ml_ensemble:
                signal_data = self.apply_ml_ensemble(signal_data, market_data, True)
            
            # 5. Apply risk management
            signal_data = self.apply_risk_management(
                signal_data, risk_profile, account_balance, market_data
            )
            
            self.logger.info(f"🎯 Unified signal generated: {symbol} {signal_data.get('signal', 'NEUTRAL')}")
            return signal_data
            
        except Exception as e:
            self.logger.error(f"Unified signal generation failed: {e}")
            return {
                'error': f'Signal generation failed: {e}',
                'symbol': symbol,
                'timeframe': timeframe,
                'timestamp': datetime.now().isoformat()
            }
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get shared services performance statistics"""
        cache_stats = self.cache.get_cache_stats()
        
        return {
            'shared_services': {
                'smc_analyzer': 'active',
                'risk_profiler': f"profile_{self.risk_profiler.current_profile}",
                'ml_ensemble': 'active',
                'okx_fetcher': 'active'
            },
            'cache_performance': cache_stats,
            'status': 'operational'
        }


# Singleton instance
_shared_services = None

def get_shared_services() -> SharedTradingServices:
    """Get singleton instance of shared services"""
    global _shared_services
    if _shared_services is None:
        _shared_services = SharedTradingServices()
    return _shared_services