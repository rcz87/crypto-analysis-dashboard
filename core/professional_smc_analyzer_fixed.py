"""
Professional SMC Analyzer - VPS Production Ready
Simplified but powerful SMC analysis for deployment
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class ProfessionalSMCAnalyzer:
    """Professional SMC analysis optimized for VPS deployment"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.ProfessionalSMCAnalyzer")
        self.logger.info("Professional SMC Analyzer initialized")
    
    def analyze_market_structure(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze market structure using SMC principles
        
        Args:
            market_data: Dictionary containing candles data
            
        Returns:
            SMC analysis results
        """
        try:
            candles = market_data.get('candles', [])
            if not candles or len(candles) < 20:
                return self._get_fallback_smc_analysis()
            
            # Convert to DataFrame for analysis
            df = pd.DataFrame(candles)
            if df.empty:
                return self._get_fallback_smc_analysis()
            
            # Ensure numeric types
            numeric_cols = ['open', 'high', 'low', 'close', 'volume']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Calculate SMC indicators
            smc_analysis = {
                'structure_analysis': self._analyze_structure(df),
                'order_blocks': self._identify_order_blocks(df),
                'fair_value_gaps': self._identify_fvg(df),
                'liquidity_analysis': self._analyze_liquidity(df),
                'market_bias': self._determine_market_bias(df),
                'confidence': self._calculate_confidence(df),
                'key_levels': self._identify_key_levels(df)
            }
            
            self.logger.info("SMC analysis completed successfully")
            return smc_analysis
            
        except Exception as e:
            self.logger.error(f"SMC analysis error: {e}")
            return self._get_fallback_smc_analysis()
    
    def _analyze_structure(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze market structure for CHoCH and BOS"""
        try:
            # Calculate swing highs and lows
            highs = df['high'].values
            lows = df['low'].values
            closes = df['close'].values
            
            # Simple structure analysis
            recent_high = np.max(highs[-10:])
            recent_low = np.min(lows[-10:])
            current_price = closes[-1]
            
            # Determine structure break
            structure_break = "none"
            if current_price > recent_high:
                structure_break = "bullish_bos"
            elif current_price < recent_low:
                structure_break = "bearish_bos"
            
            return {
                'structure_break': structure_break,
                'recent_high': float(recent_high),
                'recent_low': float(recent_low),
                'current_price': float(current_price),
                'trend': 'bullish' if current_price > recent_low * 1.02 else 'bearish'
            }
            
        except Exception as e:
            self.logger.error(f"Structure analysis error: {e}")
            return {'structure_break': 'none', 'trend': 'neutral'}
    
    def _identify_order_blocks(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Identify order blocks"""
        try:
            order_blocks = []
            
            # Simple order block identification
            for i in range(10, len(df) - 5):
                candle = df.iloc[i]
                
                # Look for strong candles with high volume
                body_size = abs(candle['close'] - candle['open'])
                avg_volume = df['volume'].rolling(20).mean().iloc[i]
                
                if candle['volume'] > avg_volume * 1.5 and body_size > 0:
                    order_blocks.append({
                        'type': 'bullish' if candle['close'] > candle['open'] else 'bearish',
                        'price_high': float(candle['high']),
                        'price_low': float(candle['low']),
                        'timestamp': candle.get('timestamp', i),
                        'strength': min(candle['volume'] / avg_volume, 3.0)
                    })
            
            # Return most recent order blocks
            return order_blocks[-5:] if order_blocks else []
            
        except Exception as e:
            self.logger.error(f"Order block identification error: {e}")
            return []
    
    def _identify_fvg(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Identify Fair Value Gaps"""
        try:
            fvgs = []
            
            for i in range(2, len(df)):
                candle1 = df.iloc[i-2]
                candle2 = df.iloc[i-1] 
                candle3 = df.iloc[i]
                
                # Bullish FVG: candle1.high < candle3.low
                if candle1['high'] < candle3['low']:
                    fvgs.append({
                        'type': 'bullish',
                        'high': float(candle1['high']),
                        'low': float(candle3['low']),
                        'timestamp': candle2.get('timestamp', i-1)
                    })
                
                # Bearish FVG: candle1.low > candle3.high
                elif candle1['low'] > candle3['high']:
                    fvgs.append({
                        'type': 'bearish',
                        'high': float(candle1['low']),
                        'low': float(candle3['high']),
                        'timestamp': candle2.get('timestamp', i-1)
                    })
            
            return fvgs[-3:] if fvgs else []
            
        except Exception as e:
            self.logger.error(f"FVG identification error: {e}")
            return []
    
    def _analyze_liquidity(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze liquidity levels"""
        try:
            highs = df['high'].values
            lows = df['low'].values
            volumes = df['volume'].values
            
            # Find high volume areas (potential liquidity)
            avg_volume = np.mean(volumes)
            high_volume_indices = np.where(volumes > avg_volume * 1.5)[0]
            
            liquidity_levels = []
            for idx in high_volume_indices[-5:]:  # Last 5 high volume areas
                liquidity_levels.append({
                    'price': float(highs[idx]),
                    'type': 'resistance',
                    'strength': float(volumes[idx] / avg_volume)
                })
                liquidity_levels.append({
                    'price': float(lows[idx]),
                    'type': 'support',
                    'strength': float(volumes[idx] / avg_volume)
                })
            
            return {
                'levels': liquidity_levels,
                'total_levels': len(liquidity_levels)
            }
            
        except Exception as e:
            self.logger.error(f"Liquidity analysis error: {e}")
            return {'levels': [], 'total_levels': 0}
    
    def _determine_market_bias(self, df: pd.DataFrame) -> str:
        """Determine overall market bias"""
        try:
            closes = df['close'].values
            
            # Simple bias calculation
            short_ma = np.mean(closes[-5:])  # 5-period average
            long_ma = np.mean(closes[-20:])  # 20-period average
            
            if short_ma > long_ma * 1.01:
                return 'bullish'
            elif short_ma < long_ma * 0.99:
                return 'bearish'
            else:
                return 'neutral'
                
        except Exception as e:
            self.logger.error(f"Market bias calculation error: {e}")
            return 'neutral'
    
    def _calculate_confidence(self, df: pd.DataFrame) -> float:
        """Calculate analysis confidence"""
        try:
            # Simple confidence based on data quality
            data_quality = len(df) / 100.0  # More data = higher confidence
            volume_consistency = 1.0 if df['volume'].std() > 0 else 0.5
            
            confidence = min(data_quality * volume_consistency, 1.0)
            return round(confidence, 2)
            
        except Exception as e:
            self.logger.error(f"Confidence calculation error: {e}")
            return 0.5
    
    def _identify_key_levels(self, df: pd.DataFrame) -> Dict[str, float]:
        """Identify key support and resistance levels"""
        try:
            highs = df['high'].values
            lows = df['low'].values
            
            return {
                'resistance': float(np.max(highs[-20:])),
                'support': float(np.min(lows[-20:])),
                'current_price': float(df['close'].iloc[-1])
            }
            
        except Exception as e:
            self.logger.error(f"Key levels identification error: {e}")
            return {'resistance': 0.0, 'support': 0.0, 'current_price': 0.0}
    
    def _get_fallback_smc_analysis(self) -> Dict[str, Any]:
        """Fallback SMC analysis when data is insufficient"""
        return {
            'structure_analysis': {
                'structure_break': 'none',
                'trend': 'neutral'
            },
            'order_blocks': [],
            'fair_value_gaps': [],
            'liquidity_analysis': {
                'levels': [],
                'total_levels': 0
            },
            'market_bias': 'neutral',
            'confidence': 0.3,
            'key_levels': {
                'resistance': 0.0,
                'support': 0.0,
                'current_price': 0.0
            }
        }