"""
Multi-Timeframe Analysis Engine
Provides confirmation signals from multiple timeframes for higher accuracy
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class MultiTimeframeAnalyzer:
    """
    Analyzes multiple timeframes to provide stronger signal confirmation
    HTF (Higher Time Frame): 4H/1D for trend direction
    MTF (Medium Time Frame): 1H for entry timing  
    LTF (Lower Time Frame): 15M for precise entry
    """
    
    def __init__(self, okx_fetcher=None):
        self.okx_fetcher = okx_fetcher
        self.timeframe_weights = {
            '15M': 0.2,  # Precise entry weight
            '1H': 0.5,   # Main signal weight
            '4H': 0.3    # Trend confirmation weight
        }
        
        logger.info("🔍 Multi-Timeframe Analyzer initialized")
    
    def analyze_multiple_timeframes(self, symbol: str, primary_tf: str = '1H') -> Dict[str, Any]:
        """
        Analyze multiple timeframes and provide comprehensive confirmation
        """
        try:
            logger.info(f"🔍 Analyzing multiple timeframes for {symbol}")
            
            # Define timeframes to analyze
            timeframes = self._get_analysis_timeframes(primary_tf)
            
            # Collect data from all timeframes
            tf_analysis = {}
            for tf in timeframes:
                df = self._fetch_timeframe_data(symbol, tf)
                if df is not None and not df.empty:
                    tf_analysis[tf] = self._analyze_timeframe(df, tf)
            
            # Calculate confluence score
            confluence = self._calculate_confluence(tf_analysis)
            
            # Generate MTF recommendation
            recommendation = self._generate_mtf_recommendation(tf_analysis, confluence)
            
            return {
                'timeframe_analysis': tf_analysis,
                'confluence_score': confluence['score'],
                'confluence_details': confluence['details'],
                'recommendation': recommendation,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Multi-timeframe analysis error: {e}")
            return {
                'error': str(e),
                'confluence_score': 50,
                'recommendation': 'NEUTRAL'
            }
    
    def _get_analysis_timeframes(self, primary_tf: str) -> List[str]:
        """Get relevant timeframes based on primary timeframe"""
        tf_groups = {
            '15M': ['15M', '1H', '4H'],
            '30M': ['15M', '30M', '2H'],
            '1H': ['15M', '1H', '4H'],
            '2H': ['30M', '2H', '1D'],
            '4H': ['1H', '4H', '1D'],
            '1D': ['4H', '1D', '1W']
        }
        
        return tf_groups.get(primary_tf, ['15M', '1H', '4H'])
    
    def _fetch_timeframe_data(self, symbol: str, timeframe: str) -> Optional[pd.DataFrame]:
        """Fetch data for specific timeframe"""
        try:
            if self.okx_fetcher:
                return self.okx_fetcher.get_candles(symbol, timeframe, limit=100)
            return None
        except Exception as e:
            logger.error(f"Error fetching {timeframe} data: {e}")
            return None
    
    def _analyze_timeframe(self, df: pd.DataFrame, timeframe: str) -> Dict[str, Any]:
        """Analyze single timeframe data"""
        try:
            # Calculate basic indicators
            sma_20 = df['close'].rolling(20).mean()
            sma_50 = df['close'].rolling(50).mean()
            rsi = self._calculate_rsi(df['close'])
            
            # Current values
            current_price = float(df['close'].iloc[-1])
            current_sma_20 = float(sma_20.iloc[-1])
            current_sma_50 = float(sma_50.iloc[-1])
            current_rsi = float(rsi.iloc[-1])
            
            # Determine trend
            if current_price > current_sma_20 > current_sma_50:
                trend = 'BULLISH'
                trend_strength = 85
            elif current_price < current_sma_20 < current_sma_50:
                trend = 'BEARISH'
                trend_strength = 85
            else:
                trend = 'NEUTRAL'
                trend_strength = 50
            
            # Momentum analysis
            if current_rsi > 70:
                momentum = 'OVERBOUGHT'
            elif current_rsi < 30:
                momentum = 'OVERSOLD'
            else:
                momentum = 'NEUTRAL'
            
            return {
                'timeframe': timeframe,
                'trend': trend,
                'trend_strength': trend_strength,
                'momentum': momentum,
                'rsi': round(current_rsi, 2),
                'price_vs_sma20': round((current_price - current_sma_20) / current_sma_20 * 100, 2),
                'price_vs_sma50': round((current_price - current_sma_50) / current_sma_50 * 100, 2),
                'support': round(df['low'].rolling(20).min().iloc[-1], 6),
                'resistance': round(df['high'].rolling(20).max().iloc[-1], 6)
            }
            
        except Exception as e:
            logger.error(f"Timeframe analysis error: {e}")
            return {
                'timeframe': timeframe,
                'trend': 'UNKNOWN',
                'error': str(e)
            }
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI indicator"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _calculate_confluence(self, tf_analysis: Dict[str, Dict]) -> Dict[str, Any]:
        """Calculate confluence score from multiple timeframes"""
        if not tf_analysis:
            return {'score': 50, 'details': 'No data available'}
        
        bullish_count = 0
        bearish_count = 0
        total_weight = 0
        weighted_score = 0
        
        for tf, analysis in tf_analysis.items():
            if 'error' in analysis:
                continue
                
            weight = self.timeframe_weights.get(tf, 0.3)
            total_weight += weight
            
            # Count trend directions
            if analysis['trend'] == 'BULLISH':
                bullish_count += 1
                weighted_score += analysis['trend_strength'] * weight
            elif analysis['trend'] == 'BEARISH':
                bearish_count += 1
                weighted_score += (100 - analysis['trend_strength']) * weight
            else:
                weighted_score += 50 * weight
        
        # Calculate final confluence score
        if total_weight > 0:
            final_score = weighted_score / total_weight
        else:
            final_score = 50
        
        # Generate confluence details
        if bullish_count >= 2:
            details = f"Strong bullish confluence ({bullish_count}/3 timeframes)"
        elif bearish_count >= 2:
            details = f"Strong bearish confluence ({bearish_count}/3 timeframes)"
        else:
            details = "Mixed signals across timeframes"
        
        return {
            'score': round(final_score, 1),
            'details': details,
            'bullish_count': bullish_count,
            'bearish_count': bearish_count
        }
    
    def _generate_mtf_recommendation(self, tf_analysis: Dict[str, Dict], 
                                   confluence: Dict[str, Any]) -> Dict[str, Any]:
        """Generate recommendation based on multi-timeframe analysis"""
        score = confluence['score']
        
        # Strong signals require high confluence
        if score >= 75:
            action = 'STRONG_BUY'
            confidence = min(90, score + 10)
        elif score >= 65:
            action = 'BUY'
            confidence = score + 5
        elif score <= 25:
            action = 'STRONG_SELL'
            confidence = min(90, 100 - score + 10)
        elif score <= 35:
            action = 'SELL'
            confidence = 100 - score + 5
        else:
            action = 'WAIT'
            confidence = 50
        
        # Check for divergences
        divergence = self._check_divergence(tf_analysis)
        
        return {
            'action': action,
            'confidence': round(confidence, 1),
            'reasoning': confluence['details'],
            'divergence': divergence,
            'optimal_entry': self._suggest_optimal_entry(tf_analysis)
        }
    
    def _check_divergence(self, tf_analysis: Dict[str, Dict]) -> Optional[str]:
        """Check for divergences between timeframes"""
        trends = [analysis.get('trend') for analysis in tf_analysis.values() if 'trend' in analysis]
        
        if len(set(trends)) > 1:
            if 'BULLISH' in trends and 'BEARISH' in trends:
                return "⚠️ Timeframe divergence detected - Use caution"
        
        return None
    
    def _suggest_optimal_entry(self, tf_analysis: Dict[str, Dict]) -> Dict[str, Any]:
        """Suggest optimal entry based on LTF analysis"""
        # Get 15M timeframe data for precise entry
        ltf_data = tf_analysis.get('15M', {})
        
        if ltf_data and 'support' in ltf_data:
            return {
                'wait_for_pullback': ltf_data.get('momentum') == 'OVERBOUGHT',
                'suggested_zone': {
                    'support': ltf_data.get('support'),
                    'resistance': ltf_data.get('resistance')
                }
            }
        
        return {'wait_for_pullback': False}