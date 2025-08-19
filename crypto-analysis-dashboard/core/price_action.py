"""
Price Action Analyzer - Candlestick Pattern Detection
Enhanced with improved scoring system and pattern visualization
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class PriceActionAnalyzer:
    """
    Enhanced Price Action Analyzer with multiple candlestick pattern detection
    Provides confidence scoring and pattern visualization capabilities
    """
    
    def __init__(self):
        self.patterns = {
            'hammer': {'strength': 0.7, 'type': 'bullish'},
            'hanging_man': {'strength': 0.7, 'type': 'bearish'},
            'shooting_star': {'strength': 0.8, 'type': 'bearish'},
            'inverted_hammer': {'strength': 0.6, 'type': 'bullish'},
            'bullish_engulfing': {'strength': 0.9, 'type': 'bullish'},
            'bearish_engulfing': {'strength': 0.9, 'type': 'bearish'},
            'morning_star': {'strength': 0.9, 'type': 'bullish'},
            'evening_star': {'strength': 0.9, 'type': 'bearish'},
            'doji': {'strength': 0.5, 'type': 'neutral'},
            'spinning_top': {'strength': 0.4, 'type': 'neutral'}
        }
        
    def analyze_price_action(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze price action patterns in the given DataFrame
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            Dictionary containing detected patterns and signals
        """
        
        # Validate and convert input data
        if df is None:
            return self._empty_analysis()
            
        # Convert list to DataFrame if needed
        if isinstance(df, list):
            try:
                # Assume list of dicts with OHLCV data
                df = pd.DataFrame(df)
            except Exception as e:
                logger.error(f"Failed to convert list to DataFrame: {e}")
                return self._empty_analysis()
        
        # Ensure it's a DataFrame
        if not isinstance(df, pd.DataFrame):
            logger.error(f"Expected DataFrame, got {type(df)}")
            return self._empty_analysis()
        
        if len(df) < 3:
            return self._empty_analysis()
        
        try:
            # Ensure we have the required columns
            required_columns = ['open', 'high', 'low', 'close', 'volume']
            if not all(col in df.columns for col in required_columns):
                return self._empty_analysis()
            
            # Convert to float to ensure numeric operations
            for col in required_columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Remove any NaN values
            df = df.dropna()
            
            if len(df) < 3:
                return self._empty_analysis()
            
            # Detect patterns
            patterns_detected = self._detect_patterns(df)
            
            # Add advanced pattern analysis
            advanced_patterns = self.analyze_advanced_patterns(df)
            
            # Generate signals
            signals = self._generate_signals(patterns_detected)
            
            # Calculate confidence
            confidence = self._calculate_confidence(patterns_detected)
            
            # Analyze trend strength
            trend_strength = self._analyze_trend_strength(df)
            
            # Identify support/resistance levels
            support_resistance = self._identify_support_resistance(df)
            
            return {
                'patterns_detected': patterns_detected,
                'signals': signals,
                'confidence': confidence,
                'trend_strength': trend_strength,
                'support_resistance': support_resistance,
                'total_patterns': len(patterns_detected),
                'bullish_patterns': len([p for p in patterns_detected if p['type'] == 'bullish']),
                'bearish_patterns': len([p for p in patterns_detected if p['type'] == 'bearish']),
                'advanced_patterns': advanced_patterns
            }
            
        except Exception as e:
            logger.error(f"Error in price action analysis: {e}")
            return self._empty_analysis()
    
    def _detect_patterns(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect various candlestick patterns"""
        patterns = []
        
        for i in range(2, len(df)):
            current = df.iloc[i]
            prev = df.iloc[i-1]
            prev2 = df.iloc[i-2]
            
            # Hammer pattern
            if self._is_hammer(current):
                patterns.append({
                    'name': 'hammer',
                    'type': 'bullish',
                    'strength': 0.7,
                    'index': i,
                    'description': 'Hammer pattern detected - potential bullish reversal'
                })
            
            # Shooting star pattern
            if self._is_shooting_star(current):
                patterns.append({
                    'name': 'shooting_star',
                    'type': 'bearish',
                    'strength': 0.8,
                    'index': i,
                    'description': 'Shooting star pattern detected - potential bearish reversal'
                })
            
            # Bullish engulfing pattern
            if self._is_bullish_engulfing(prev, current):
                patterns.append({
                    'name': 'bullish_engulfing',
                    'type': 'bullish',
                    'strength': 0.9,
                    'index': i,
                    'description': 'Bullish engulfing pattern detected - strong bullish signal'
                })
            
            # Bearish engulfing pattern
            if self._is_bearish_engulfing(prev, current):
                patterns.append({
                    'name': 'bearish_engulfing',
                    'type': 'bearish',
                    'strength': 0.9,
                    'index': i,
                    'description': 'Bearish engulfing pattern detected - strong bearish signal'
                })
            
            # Doji pattern
            if self._is_doji(current):
                patterns.append({
                    'name': 'doji',
                    'type': 'neutral',
                    'strength': 0.5,
                    'index': i,
                    'description': 'Doji pattern detected - market indecision'
                })
        
        return patterns
    
    def _is_hammer(self, candle) -> bool:
        """Check if candle is a hammer pattern"""
        body = abs(candle['close'] - candle['open'])
        lower_shadow = candle['open'] - candle['low'] if candle['close'] > candle['open'] else candle['close'] - candle['low']
        upper_shadow = candle['high'] - candle['close'] if candle['close'] > candle['open'] else candle['high'] - candle['open']
        
        return (
            lower_shadow > 2 * body and
            upper_shadow < 0.5 * body and
            body > 0
        )
    
    def _is_shooting_star(self, candle) -> bool:
        """Check if candle is a shooting star pattern"""
        body = abs(candle['close'] - candle['open'])
        lower_shadow = candle['open'] - candle['low'] if candle['close'] > candle['open'] else candle['close'] - candle['low']
        upper_shadow = candle['high'] - candle['close'] if candle['close'] > candle['open'] else candle['high'] - candle['open']
        
        return (
            upper_shadow > 2 * body and
            lower_shadow < 0.5 * body and
            body > 0
        )
    
    def _is_bullish_engulfing(self, prev_candle, current_candle) -> bool:
        """Check if current candle engulfs previous bearish candle"""
        return (
            prev_candle['close'] < prev_candle['open'] and  # Previous candle is bearish
            current_candle['close'] > current_candle['open'] and  # Current candle is bullish
            current_candle['open'] < prev_candle['close'] and  # Current opens below previous close
            current_candle['close'] > prev_candle['open']  # Current closes above previous open
        )
    
    def _is_bearish_engulfing(self, prev_candle, current_candle) -> bool:
        """Check if current candle engulfs previous bullish candle"""
        return (
            prev_candle['close'] > prev_candle['open'] and  # Previous candle is bullish
            current_candle['close'] < current_candle['open'] and  # Current candle is bearish
            current_candle['open'] > prev_candle['close'] and  # Current opens above previous close
            current_candle['close'] < prev_candle['open']  # Current closes below previous open
        )
    
    def _is_doji(self, candle) -> bool:
        """Check if candle is a doji pattern"""
        body = abs(candle['close'] - candle['open'])
        total_range = candle['high'] - candle['low']
        
        return body < 0.1 * total_range if total_range > 0 else False
    
    def _generate_signals(self, patterns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate trading signals from detected patterns"""
        signals = []
        
        # Group patterns by type
        bullish_patterns = [p for p in patterns if p['type'] == 'bullish']
        bearish_patterns = [p for p in patterns if p['type'] == 'bearish']
        
        # Generate bullish signal if bullish patterns are stronger
        if bullish_patterns:
            bullish_strength = sum(p['strength'] for p in bullish_patterns)
            signals.append({
                'signal': 'BUY',
                'confidence': min(bullish_strength, 1.0),
                'patterns': [p['name'] for p in bullish_patterns],
                'reason': f"Strong bullish patterns detected: {', '.join(p['name'] for p in bullish_patterns)}"
            })
        
        # Generate bearish signal if bearish patterns are stronger
        if bearish_patterns:
            bearish_strength = sum(p['strength'] for p in bearish_patterns)
            signals.append({
                'signal': 'SELL',
                'confidence': min(bearish_strength, 1.0),
                'patterns': [p['name'] for p in bearish_patterns],
                'reason': f"Strong bearish patterns detected: {', '.join(p['name'] for p in bearish_patterns)}"
            })
        
        return signals
    
    def _calculate_confidence(self, patterns: List[Dict[str, Any]]) -> float:
        """Calculate overall confidence based on detected patterns"""
        if not patterns:
            return 0.0
        
        total_strength = sum(p['strength'] for p in patterns)
        return min(total_strength / len(patterns), 1.0)
    
    def _analyze_trend_strength(self, df: pd.DataFrame) -> str:
        """Analyze trend strength from price action"""
        if len(df) < 10:
            return 'weak'
        
        # Calculate recent price movement
        recent_close = df['close'].iloc[-1]
        past_close = df['close'].iloc[-10]
        
        price_change = (recent_close - past_close) / past_close * 100
        
        if abs(price_change) > 5:
            return 'strong'
        elif abs(price_change) > 2:
            return 'moderate'
        else:
            return 'weak'
    
    def _identify_support_resistance(self, df: pd.DataFrame) -> Dict[str, float]:
        """Identify key support and resistance levels"""
        if len(df) < 20:
            return {}
        
        # Simple support/resistance based on recent highs and lows
        recent_data = df.tail(20)
        
        support = float(recent_data['low'].min())
        resistance = float(recent_data['high'].max())
        current_price = float(df['close'].iloc[-1])
        
        return {
            'support': support,
            'resistance': resistance,
            'current_price': current_price,
            'distance_to_support': ((current_price - support) / current_price) * 100,
            'distance_to_resistance': ((resistance - current_price) / current_price) * 100
        }
    
    def _empty_analysis(self) -> Dict[str, Any]:
        """Return empty analysis structure"""
        return {
            'patterns_detected': [],
            'signals': [],
            'confidence': 0.0,
            'trend_strength': 'weak',
            'support_resistance': {},
            'total_patterns': 0,
            'bullish_patterns': 0,
            'bearish_patterns': 0,
            'advanced_patterns': []
        }
    
    # ======================================================================
    # 🕯️ ADVANCED PRICE ACTION FEATURES - FITUR LANJUTAN
    # ======================================================================
    
    def analyze_advanced_patterns(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        🚀 Advanced Price Action Pattern Analysis
        
        Menganalisis pattern kompleks yang membutuhkan kombinasi candle
        dan pattern lanjutan untuk trading yang lebih presisi
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            List of advanced pattern detections
        """
        advanced_patterns = []
        
        if len(df) < 10:
            return advanced_patterns
        
        # 1. Pattern Stacking - Multi-candle patterns
        stacked_patterns = self._detect_pattern_stacking(df)
        advanced_patterns.extend(stacked_patterns)
        
        # 2. SNR Flip Detection - Support/Resistance flips
        snr_flips = self._detect_snr_flips(df)
        advanced_patterns.extend(snr_flips)
        
        # 3. Wick Trap Detector - Long wick patterns
        wick_traps = self._detect_wick_traps(df)
        advanced_patterns.extend(wick_traps)
        
        # 4. Momentum Candle Detection - Marubozu patterns
        momentum_candles = self._detect_momentum_candles(df)
        advanced_patterns.extend(momentum_candles)
        
        # 5. Compression Pattern - Volatility compression
        compression_patterns = self._detect_compression_patterns(df)
        advanced_patterns.extend(compression_patterns)
        
        return advanced_patterns
    
    def _detect_pattern_stacking(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        🕯️ Pattern Stacking Detection
        
        Gabungkan 2-3 candle untuk mengenali pola kompleks:
        - Morning Star, Evening Star
        - Three White Soldiers, Three Black Crows
        - Abandoned Baby, etc.
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            List of stacked pattern detections
        """
        stacked_patterns = []
        
        if len(df) < 3:
            return stacked_patterns
        
        # Convert to list of dicts for easier processing
        candles = []
        for i in range(len(df)):
            candles.append({
                'timestamp': df.index[i] if hasattr(df.index, '__getitem__') else i,
                'open': float(df['open'].iloc[i]),
                'high': float(df['high'].iloc[i]),
                'low': float(df['low'].iloc[i]),
                'close': float(df['close'].iloc[i]),
                'volume': float(df['volume'].iloc[i])
            })
        
        # Check for 3-candle patterns
        for i in range(2, len(candles)):
            first = candles[i-2]
            second = candles[i-1]
            third = candles[i]
            
            # Morning Star Pattern
            if self._is_morning_star(first, second, third):
                stacked_patterns.append({
                    'type': 'morning_star',
                    'direction': 'bullish',
                    'confidence_score': 0.85,
                    'timestamp': third['timestamp'],
                    'price_level': third['close'],
                    'candle_count': 3,
                    'description': 'Morning Star - Strong bullish reversal pattern'
                })
            
            # Evening Star Pattern
            elif self._is_evening_star(first, second, third):
                stacked_patterns.append({
                    'type': 'evening_star',
                    'direction': 'bearish',
                    'confidence_score': 0.85,
                    'timestamp': third['timestamp'],
                    'price_level': third['close'],
                    'candle_count': 3,
                    'description': 'Evening Star - Strong bearish reversal pattern'
                })
            
            # Three White Soldiers
            elif self._is_three_white_soldiers(first, second, third):
                stacked_patterns.append({
                    'type': 'three_white_soldiers',
                    'direction': 'bullish',
                    'confidence_score': 0.8,
                    'timestamp': third['timestamp'],
                    'price_level': third['close'],
                    'candle_count': 3,
                    'description': 'Three White Soldiers - Strong bullish momentum'
                })
            
            # Three Black Crows
            elif self._is_three_black_crows(first, second, third):
                stacked_patterns.append({
                    'type': 'three_black_crows',
                    'direction': 'bearish',
                    'confidence_score': 0.8,
                    'timestamp': third['timestamp'],
                    'price_level': third['close'],
                    'candle_count': 3,
                    'description': 'Three Black Crows - Strong bearish momentum'
                })
        
        return stacked_patterns
    
    def _detect_snr_flips(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        🔄 SNR Flip Detection
        
        Deteksi area support yang berubah jadi resistance (dan sebaliknya)
        berdasarkan level sebelumnya yang tertembus dan di-retest
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            List of SNR flip detections
        """
        snr_flips = []
        
        if len(df) < 20:
            return snr_flips
        
        # Get recent price levels
        recent_data = df.tail(20)
        
        # Find potential support/resistance levels
        highs = recent_data['high'].values
        lows = recent_data['low'].values
        closes = recent_data['close'].values
        
        # Look for level breaks and retests
        for i in range(10, len(recent_data) - 5):
            current_close = closes[i]
            
            # Check for support flip (support becomes resistance)
            prev_support = min(lows[i-10:i])
            if (current_close > prev_support * 1.01 and  # Price broke above support
                any(closes[i+1:i+5] < prev_support * 1.005)):  # Later rejected at level
                
                confidence = 0.7 + (0.2 * (current_close - prev_support) / prev_support)
                confidence = min(confidence, 0.9)
                
                snr_flips.append({
                    'type': 'support_to_resistance_flip',
                    'direction': 'bearish',
                    'confidence_score': confidence,
                    'timestamp': recent_data.index[i],
                    'flip_level': prev_support,
                    'break_price': current_close,
                    'description': f'Support level {prev_support:.4f} flipped to resistance'
                })
            
            # Check for resistance flip (resistance becomes support)
            prev_resistance = max(highs[i-10:i])
            if (current_close < prev_resistance * 0.99 and  # Price broke below resistance
                any(closes[i+1:i+5] > prev_resistance * 0.995)):  # Later supported at level
                
                confidence = 0.7 + (0.2 * (prev_resistance - current_close) / prev_resistance)
                confidence = min(confidence, 0.9)
                
                snr_flips.append({
                    'type': 'resistance_to_support_flip',
                    'direction': 'bullish',
                    'confidence_score': confidence,
                    'timestamp': recent_data.index[i],
                    'flip_level': prev_resistance,
                    'break_price': current_close,
                    'description': f'Resistance level {prev_resistance:.4f} flipped to support'
                })
        
        return snr_flips
    
    def _detect_wick_traps(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        🪤 Wick Trap Detector
        
        Identifikasi candle dengan wick panjang dan body kecil
        yang menyentuh level penting lalu memantul (indikasi stop hunt)
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            List of wick trap detections
        """
        wick_traps = []
        
        if len(df) < 5:
            return wick_traps
        
        # Analyze recent candles for wick traps
        for i in range(2, len(df) - 2):
            candle = {
                'open': float(df['open'].iloc[i]),
                'high': float(df['high'].iloc[i]),
                'low': float(df['low'].iloc[i]),
                'close': float(df['close'].iloc[i]),
                'timestamp': df.index[i] if hasattr(df.index, '__getitem__') else i
            }
            
            # Calculate body and wick sizes
            body_size = abs(candle['close'] - candle['open'])
            upper_wick = candle['high'] - max(candle['open'], candle['close'])
            lower_wick = min(candle['open'], candle['close']) - candle['low']
            total_range = candle['high'] - candle['low']
            
            if total_range == 0:
                continue
            
            # Check for upper wick trap (rejection at high)
            if (upper_wick > 3 * body_size and 
                upper_wick > 0.6 * total_range and
                body_size > 0):
                
                # Check if it's near a significant level
                prev_highs = [float(df['high'].iloc[j]) for j in range(max(0, i-10), i)]
                if prev_highs:
                    resistance_level = max(prev_highs)
                    if candle['high'] >= resistance_level * 0.998:
                        
                        confidence = 0.6 + (upper_wick / total_range) * 0.3
                        
                        wick_traps.append({
                            'type': 'upper_wick_trap',
                            'direction': 'bearish',
                            'confidence_score': confidence,
                            'timestamp': candle['timestamp'],
                            'trap_level': candle['high'],
                            'body_size': body_size,
                            'wick_size': upper_wick,
                            'wick_to_body_ratio': upper_wick / body_size if body_size > 0 else 0,
                            'description': f'Upper wick trap at {candle["high"]:.4f} - rejection of resistance'
                        })
            
            # Check for lower wick trap (rejection at low)
            if (lower_wick > 3 * body_size and 
                lower_wick > 0.6 * total_range and
                body_size > 0):
                
                # Check if it's near a significant level
                prev_lows = [float(df['low'].iloc[j]) for j in range(max(0, i-10), i)]
                if prev_lows:
                    support_level = min(prev_lows)
                    if candle['low'] <= support_level * 1.002:
                        
                        confidence = 0.6 + (lower_wick / total_range) * 0.3
                        
                        wick_traps.append({
                            'type': 'lower_wick_trap',
                            'direction': 'bullish',
                            'confidence_score': confidence,
                            'timestamp': candle['timestamp'],
                            'trap_level': candle['low'],
                            'body_size': body_size,
                            'wick_size': lower_wick,
                            'wick_to_body_ratio': lower_wick / body_size if body_size > 0 else 0,
                            'description': f'Lower wick trap at {candle["low"]:.4f} - rejection of support'
                        })
        
        return wick_traps
    
    def _detect_momentum_candles(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        🚀 Momentum Candle Detection
        
        Deteksi candle dengan body besar tanpa wick (marubozu)
        seringkali sebagai candle validasi breakout
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            List of momentum candle detections
        """
        momentum_candles = []
        
        if len(df) < 3:
            return momentum_candles
        
        # Analyze each candle for momentum characteristics
        for i in range(1, len(df) - 1):
            candle = {
                'open': float(df['open'].iloc[i]),
                'high': float(df['high'].iloc[i]),
                'low': float(df['low'].iloc[i]),
                'close': float(df['close'].iloc[i]),
                'volume': float(df['volume'].iloc[i]),
                'timestamp': df.index[i] if hasattr(df.index, '__getitem__') else i
            }
            
            # Calculate body and wick sizes
            body_size = abs(candle['close'] - candle['open'])
            upper_wick = candle['high'] - max(candle['open'], candle['close'])
            lower_wick = min(candle['open'], candle['close']) - candle['low']
            total_range = candle['high'] - candle['low']
            
            if total_range == 0 or body_size == 0:
                continue
            
            # Check for Marubozu characteristics
            body_percentage = body_size / total_range
            max_wick_size = max(upper_wick, lower_wick)
            
            if (body_percentage > 0.85 and  # Body is >85% of total range
                max_wick_size < 0.1 * total_range):  # Minimal wicks
                
                direction = 'bullish' if candle['close'] > candle['open'] else 'bearish'
                
                # Check if it's breaking out of a range
                prev_candles = df.iloc[max(0, i-5):i]
                if len(prev_candles) >= 3:
                    prev_high = prev_candles['high'].max()
                    prev_low = prev_candles['low'].min()
                    
                    is_breakout = False
                    if direction == 'bullish' and candle['close'] > prev_high:
                        is_breakout = True
                    elif direction == 'bearish' and candle['close'] < prev_low:
                        is_breakout = True
                    
                    # Check volume confirmation
                    avg_volume = prev_candles['volume'].mean()
                    volume_surge = candle['volume'] > avg_volume * 1.5
                    
                    confidence = 0.6 + (body_percentage * 0.2) + (0.1 if is_breakout else 0) + (0.1 if volume_surge else 0)
                    confidence = min(confidence, 0.9)
                    
                    momentum_candles.append({
                        'type': 'momentum_candle',
                        'direction': direction,
                        'confidence_score': confidence,
                        'timestamp': candle['timestamp'],
                        'price_level': candle['close'],
                        'body_percentage': body_percentage,
                        'is_breakout': is_breakout,
                        'volume_surge': volume_surge,
                        'description': f'{direction.title()} momentum candle with {body_percentage:.1%} body size'
                    })
        
        return momentum_candles
    
    def _detect_compression_patterns(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        🔄 Compression Pattern Detection
        
        Deteksi rangkaian candle yang semakin kecil dengan low volatility
        kemungkinan breakout besar (expansion phase)
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            List of compression pattern detections
        """
        compression_patterns = []
        
        if len(df) < 10:
            return compression_patterns
        
        # Calculate Average True Range (ATR) for volatility measurement
        atr_values = []
        for i in range(1, len(df)):
            high = float(df['high'].iloc[i])
            low = float(df['low'].iloc[i])
            prev_close = float(df['close'].iloc[i-1])
            
            tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
            atr_values.append(tr)
        
        # Look for compression patterns
        lookback = 8
        for i in range(lookback, len(atr_values) - 2):
            current_atr = atr_values[i]
            recent_atr = atr_values[i-lookback:i]
            
            if len(recent_atr) >= lookback:
                # Check for decreasing volatility
                avg_early_atr = sum(recent_atr[:4]) / 4
                avg_recent_atr = sum(recent_atr[4:]) / 4
                
                volatility_decrease = (avg_early_atr - avg_recent_atr) / avg_early_atr if avg_early_atr > 0 else 0
                
                # Check for tight range
                recent_candles = df.iloc[i-4:i+1]
                price_range = recent_candles['high'].max() - recent_candles['low'].min()
                avg_price = recent_candles['close'].mean()
                range_percentage = price_range / avg_price if avg_price > 0 else 0
                
                # Compression criteria
                if (volatility_decrease > 0.3 and  # 30% decrease in volatility
                    range_percentage < 0.02 and  # Tight 2% range
                    current_atr < avg_early_atr * 0.6):  # Current ATR is 40% lower
                    
                    # Calculate compression strength
                    compression_strength = volatility_decrease * 0.7 + (1 - range_percentage * 50) * 0.3
                    compression_strength = min(compression_strength, 0.9)
                    
                    # Determine potential breakout direction
                    last_candle = df.iloc[i]
                    mid_price = (recent_candles['high'].max() + recent_candles['low'].min()) / 2
                    
                    if float(last_candle['close']) > mid_price:
                        bias = 'bullish'
                    else:
                        bias = 'bearish'
                    
                    compression_patterns.append({
                        'type': 'compression_pattern',
                        'direction': 'neutral',  # Compression is neutral until breakout
                        'breakout_bias': bias,
                        'confidence_score': compression_strength,
                        'timestamp': last_candle.name if hasattr(last_candle, 'name') else i,
                        'price_level': float(last_candle['close']),
                        'volatility_decrease': volatility_decrease,
                        'range_percentage': range_percentage,
                        'compression_strength': compression_strength,
                        'description': f'Compression pattern with {volatility_decrease:.1%} volatility decrease, {bias} bias'
                    })
        
        return compression_patterns
    
    # Helper methods for pattern stacking
    def _is_morning_star(self, first, second, third):
        """Check for Morning Star pattern"""
        return (
            first['close'] < first['open'] and  # First candle is bearish
            abs(second['close'] - second['open']) < abs(first['close'] - first['open']) * 0.3 and  # Second is small
            third['close'] > third['open'] and  # Third is bullish
            third['close'] > (first['open'] + first['close']) / 2  # Third closes above midpoint of first
        )
    
    def _is_evening_star(self, first, second, third):
        """Check for Evening Star pattern"""
        return (
            first['close'] > first['open'] and  # First candle is bullish
            abs(second['close'] - second['open']) < abs(first['close'] - first['open']) * 0.3 and  # Second is small
            third['close'] < third['open'] and  # Third is bearish
            third['close'] < (first['open'] + first['close']) / 2  # Third closes below midpoint of first
        )
    
    def _is_three_white_soldiers(self, first, second, third):
        """Check for Three White Soldiers pattern"""
        return (
            first['close'] > first['open'] and  # All bullish
            second['close'] > second['open'] and
            third['close'] > third['open'] and
            second['close'] > first['close'] and  # Each closes higher
            third['close'] > second['close'] and
            abs(first['close'] - first['open']) > 0 and  # Reasonable body sizes
            abs(second['close'] - second['open']) > 0 and
            abs(third['close'] - third['open']) > 0
        )
    
    def _is_three_black_crows(self, first, second, third):
        """Check for Three Black Crows pattern"""
        return (
            first['close'] < first['open'] and  # All bearish
            second['close'] < second['open'] and
            third['close'] < third['open'] and
            second['close'] < first['close'] and  # Each closes lower
            third['close'] < second['close'] and
            abs(first['close'] - first['open']) > 0 and  # Reasonable body sizes
            abs(second['close'] - second['open']) > 0 and
            abs(third['close'] - third['open']) > 0
        )