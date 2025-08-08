#!/usr/bin/env python3
"""
Advanced Technical Indicator Calculator
Comprehensive technical indicator calculation with enhanced features
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
import logging
from dataclasses import dataclass
from enum import Enum

# Technical analysis library
try:
    import ta
    TA_AVAILABLE = True
except ImportError:
    TA_AVAILABLE = False
    logging.warning("TA library not available - some indicators may not work")

logger = logging.getLogger(__name__)

class IndicatorType(Enum):
    TREND = "trend"
    MOMENTUM = "momentum"
    VOLUME = "volume"
    VOLATILITY = "volatility"
    CUSTOM = "custom"

@dataclass
class IndicatorResult:
    """Result of indicator calculation"""
    name: str
    type: IndicatorType
    values: Any
    signal: str
    strength: float
    description: str
    parameters: Dict[str, Any]
    interpretation: str = ""  # Add interpretation field

class AdvancedIndicatorCalculator:
    """Advanced technical indicator calculator with comprehensive features"""
    
    def __init__(self):
        self.indicators_cache = {}
        self.supported_indicators = {
            # Trend indicators
            'sma': self._calculate_sma,
            'ema': self._calculate_ema,
            'wma': self._calculate_wma,
            'vwma': self._calculate_vwma,
            'hma': self._calculate_hma,
            'tema': self._calculate_tema,
            'kama': self._calculate_kama,
            
            # Momentum indicators
            'rsi': self._calculate_rsi,
            'macd': self._calculate_macd,
            'stoch': self._calculate_stochastic,
            'stoch_rsi': self._calculate_stochastic_rsi,
            'williams_r': self._calculate_williams_r,
            'roc': self._calculate_roc,
            'momentum': self._calculate_momentum,
            'tsi': self._calculate_tsi,
            'cci': self._calculate_cci,
            
            # Volume indicators
            'obv': self._calculate_obv,
            'ad': self._calculate_ad,
            'cmf': self._calculate_cmf,
            'fi': self._calculate_fi,
            'nvi': self._calculate_nvi,
            'pvi': self._calculate_pvi,
            'vpt': self._calculate_vpt,
            'mfi': self._calculate_mfi,
            'volume_profile': self._calculate_volume_profile,
            
            # Volatility indicators
            'bb': self._calculate_bollinger_bands,
            'kc': self._calculate_keltner_channels,
            'dc': self._calculate_donchian_channels,
            'atr': self._calculate_atr,
            'natr': self._calculate_natr,
            'trange': self._calculate_true_range,
            'vhf': self._calculate_vhf,
            
            # Custom indicators
            'market_cipher': self._calculate_market_cipher,
            'whale_activity': self._calculate_whale_activity,
            'smart_money_flow': self._calculate_smart_money_flow,
            'liquidity_heatmap': self._calculate_liquidity_heatmap,
            'support_resistance': self._calculate_support_resistance,
            'pattern_recognition': self._calculate_pattern_recognition
        }
        
        logger.info(f"AdvancedIndicatorCalculator initialized with {len(self.supported_indicators)} indicators")
    
    def calculate_indicator(self, df: pd.DataFrame, indicator_name: str, 
                          **kwargs) -> IndicatorResult:
        """
        Calculate specific technical indicator
        
        Args:
            df: OHLCV dataframe
            indicator_name: Name of indicator to calculate
            **kwargs: Additional parameters for indicator
            
        Returns:
            IndicatorResult object
        """
        try:
            if indicator_name not in self.supported_indicators:
                raise ValueError(f"Indicator {indicator_name} not supported")
            
            # Generate cache key
            cache_key = f"{indicator_name}_{hash(str(df.values.tobytes()))}_{hash(str(kwargs))}"
            
            if cache_key in self.indicators_cache:
                return self.indicators_cache[cache_key]
            
            # Calculate indicator
            result = self.supported_indicators[indicator_name](df, **kwargs)
            
            # Cache result
            self.indicators_cache[cache_key] = result
            
            return result
            
        except Exception as e:
            logger.error(f"Error calculating indicator {indicator_name}: {e}")
            return IndicatorResult(
                name=indicator_name,
                type=IndicatorType.CUSTOM,
                values=[],
                signal="ERROR",
                strength=0.0,
                description=f"Error calculating {indicator_name}: {str(e)}",
                parameters=kwargs
            )
    
    def calculate_all_indicators(self, df: pd.DataFrame, 
                               selected_indicators: List[str] = None) -> Dict[str, IndicatorResult]:
        """Calculate multiple indicators"""
        try:
            if selected_indicators is None:
                selected_indicators = list(self.supported_indicators.keys())
            
            results = {}
            for indicator_name in selected_indicators:
                try:
                    result = self.calculate_indicator(df, indicator_name)
                    results[indicator_name] = result
                except Exception as e:
                    logger.error(f"Error calculating {indicator_name}: {e}")
                    continue
            
            return results
            
        except Exception as e:
            logger.error(f"Error calculating multiple indicators: {e}")
            return {}
    
    def get_indicator_signals(self, df: pd.DataFrame, 
                            confidence_threshold: float = 0.6) -> Dict[str, Dict[str, Any]]:
        """Get trading signals from indicators"""
        try:
            # Calculate key indicators
            indicators = self.calculate_all_indicators(df, [
                'rsi', 'macd', 'stoch', 'bb', 'obv', 'atr'
            ])
            
            signals = {}
            
            # RSI signals
            if 'rsi' in indicators:
                rsi_result = indicators['rsi']
                if rsi_result.values is not None:
                    try:
                        current_rsi = float(rsi_result.values.iloc[-1] if hasattr(rsi_result.values, 'iloc') else rsi_result.values)
                        if current_rsi > 70:
                            signals['rsi'] = {'signal': 'SELL', 'strength': 0.8, 'reason': 'Overbought'}
                        elif current_rsi < 30:
                            signals['rsi'] = {'signal': 'BUY', 'strength': 0.8, 'reason': 'Oversold'}
                        else:
                            signals['rsi'] = {'signal': 'NEUTRAL', 'strength': 0.5, 'reason': 'Normal range'}
                    except Exception as e:
                        logger.error(f"Error processing RSI signal: {e}")
                        signals['rsi'] = {'signal': 'NEUTRAL', 'strength': 0.5, 'reason': 'Error processing'}
            
            # MACD signals
            if 'macd' in indicators:
                macd_result = indicators['macd']
                if macd_result.values is not None:
                    try:
                        macd_data = macd_result.values
                        if isinstance(macd_data, dict):
                            macd_line = float(macd_data.get('macd', pd.Series()).iloc[-1] if hasattr(macd_data.get('macd'), 'iloc') else 0)
                            signal_line = float(macd_data.get('signal', pd.Series()).iloc[-1] if hasattr(macd_data.get('signal'), 'iloc') else 0)
                            
                            if macd_line > signal_line:
                                signals['macd'] = {'signal': 'BUY', 'strength': 0.7, 'reason': 'MACD above signal'}
                            else:
                                signals['macd'] = {'signal': 'SELL', 'strength': 0.7, 'reason': 'MACD below signal'}
                    except Exception as e:
                        logger.error(f"Error processing MACD signal: {e}")
                        signals['macd'] = {'signal': 'NEUTRAL', 'strength': 0.5, 'reason': 'Error processing'}
            
            # Bollinger Bands signals
            if 'bb' in indicators:
                bb_result = indicators['bb']
                if bb_result.values is not None:
                    try:
                        bb_data = bb_result.values
                        if isinstance(bb_data, dict):
                            current_price = float(df['close'].iloc[-1])
                            upper_band = bb_data.get('upper', pd.Series())
                            lower_band = bb_data.get('lower', pd.Series())
                            
                            if hasattr(upper_band, 'iloc') and hasattr(lower_band, 'iloc'):
                                upper_value = float(upper_band.iloc[-1])
                                lower_value = float(lower_band.iloc[-1])
                                
                                if current_price > upper_value:
                                    signals['bb'] = {'signal': 'SELL', 'strength': 0.6, 'reason': 'Price above upper band'}
                                elif current_price < lower_value:
                                    signals['bb'] = {'signal': 'BUY', 'strength': 0.6, 'reason': 'Price below lower band'}
                                else:
                                    signals['bb'] = {'signal': 'NEUTRAL', 'strength': 0.4, 'reason': 'Price within bands'}
                    except Exception as e:
                        logger.error(f"Error processing Bollinger Bands signal: {e}")
                        signals['bb'] = {'signal': 'NEUTRAL', 'strength': 0.4, 'reason': 'Error processing'}
            
            return signals
            
        except Exception as e:
            logger.error(f"Error getting indicator signals: {e}")
            return {}
    
    # =================== TREND INDICATORS ===================
    
    def _calculate_sma(self, df: pd.DataFrame, period: int = 20) -> IndicatorResult:
        """Simple Moving Average"""
        try:
            sma = df['close'].rolling(window=period).mean()
            
            # Determine signal
            current_price = df['close'].iloc[-1]
            current_sma = sma.iloc[-1]
            
            signal = "BUY" if current_price > current_sma else "SELL"
            strength = abs(current_price - current_sma) / current_sma
            
            return IndicatorResult(
                name="SMA",
                type=IndicatorType.TREND,
                values=sma,
                signal=signal,
                strength=min(strength, 1.0),
                description=f"Simple Moving Average ({period} periods)",
                parameters={'period': period}
            )
        except Exception as e:
            raise Exception(f"SMA calculation error: {e}")
    
    def _calculate_ema(self, df: pd.DataFrame, period: int = 20) -> IndicatorResult:
        """Exponential Moving Average"""
        try:
            ema = df['close'].ewm(span=period).mean()
            
            current_price = df['close'].iloc[-1]
            current_ema = ema.iloc[-1]
            
            signal = "BUY" if current_price > current_ema else "SELL"
            strength = abs(current_price - current_ema) / current_ema
            
            return IndicatorResult(
                name="EMA",
                type=IndicatorType.TREND,
                values=ema,
                signal=signal,
                strength=min(strength, 1.0),
                description=f"Exponential Moving Average ({period} periods)",
                parameters={'period': period}
            )
        except Exception as e:
            raise Exception(f"EMA calculation error: {e}")
    
    def _calculate_wma(self, df: pd.DataFrame, period: int = 20) -> IndicatorResult:
        """Weighted Moving Average"""
        try:
            weights = np.arange(1, period + 1)
            wma = df['close'].rolling(window=period).apply(
                lambda x: np.dot(x, weights) / weights.sum(), raw=True
            )
            
            current_price = df['close'].iloc[-1]
            current_wma = wma.iloc[-1]
            
            signal = "BUY" if current_price > current_wma else "SELL"
            strength = abs(current_price - current_wma) / current_wma
            
            return IndicatorResult(
                name="WMA",
                type=IndicatorType.TREND,
                values=wma,
                signal=signal,
                strength=min(strength, 1.0),
                description=f"Weighted Moving Average ({period} periods)",
                parameters={'period': period}
            )
        except Exception as e:
            raise Exception(f"WMA calculation error: {e}")
    
    def _calculate_vwma(self, df: pd.DataFrame, period: int = 20) -> IndicatorResult:
        """Volume Weighted Moving Average"""
        try:
            vwma = (df['close'] * df['volume']).rolling(window=period).sum() / df['volume'].rolling(window=period).sum()
            
            current_price = df['close'].iloc[-1]
            current_vwma = vwma.iloc[-1]
            
            signal = "BUY" if current_price > current_vwma else "SELL"
            strength = abs(current_price - current_vwma) / current_vwma
            
            return IndicatorResult(
                name="VWMA",
                type=IndicatorType.TREND,
                values=vwma,
                signal=signal,
                strength=min(strength, 1.0),
                description=f"Volume Weighted Moving Average ({period} periods)",
                parameters={'period': period}
            )
        except Exception as e:
            raise Exception(f"VWMA calculation error: {e}")
    
    def _calculate_hma(self, df: pd.DataFrame, period: int = 20) -> IndicatorResult:
        """Hull Moving Average"""
        try:
            half_period = period // 2
            sqrt_period = int(np.sqrt(period))
            
            wma1 = df['close'].rolling(window=half_period).apply(
                lambda x: np.dot(x, np.arange(1, half_period + 1)) / np.arange(1, half_period + 1).sum(), raw=True
            )
            wma2 = df['close'].rolling(window=period).apply(
                lambda x: np.dot(x, np.arange(1, period + 1)) / np.arange(1, period + 1).sum(), raw=True
            )
            
            raw_hma = 2 * wma1 - wma2
            hma = raw_hma.rolling(window=sqrt_period).apply(
                lambda x: np.dot(x, np.arange(1, sqrt_period + 1)) / np.arange(1, sqrt_period + 1).sum(), raw=True
            )
            
            current_price = df['close'].iloc[-1]
            current_hma = hma.iloc[-1]
            
            signal = "BUY" if current_price > current_hma else "SELL"
            strength = abs(current_price - current_hma) / current_hma
            
            return IndicatorResult(
                name="HMA",
                type=IndicatorType.TREND,
                values=hma,
                signal=signal,
                strength=min(strength, 1.0),
                description=f"Hull Moving Average ({period} periods)",
                parameters={'period': period}
            )
        except Exception as e:
            raise Exception(f"HMA calculation error: {e}")
    
    def _calculate_tema(self, df: pd.DataFrame, period: int = 20) -> IndicatorResult:
        """Triple Exponential Moving Average"""
        try:
            ema1 = df['close'].ewm(span=period).mean()
            ema2 = ema1.ewm(span=period).mean()
            ema3 = ema2.ewm(span=period).mean()
            
            tema = 3 * ema1 - 3 * ema2 + ema3
            
            current_price = df['close'].iloc[-1]
            current_tema = tema.iloc[-1]
            
            signal = "BUY" if current_price > current_tema else "SELL"
            strength = abs(current_price - current_tema) / current_tema
            
            return IndicatorResult(
                name="TEMA",
                type=IndicatorType.TREND,
                values=tema,
                signal=signal,
                strength=min(strength, 1.0),
                description=f"Triple Exponential Moving Average ({period} periods)",
                parameters={'period': period}
            )
        except Exception as e:
            raise Exception(f"TEMA calculation error: {e}")
    
    def _calculate_kama(self, df: pd.DataFrame, period: int = 20) -> IndicatorResult:
        """Kaufman Adaptive Moving Average"""
        try:
            if not TA_AVAILABLE:
                raise Exception("TA library required for KAMA calculation")
            
            kama = ta.trend.KAMAIndicator(close=df['close'], window=period).kama()
            
            current_price = df['close'].iloc[-1]
            current_kama = kama.iloc[-1]
            
            signal = "BUY" if current_price > current_kama else "SELL"
            strength = abs(current_price - current_kama) / current_kama
            
            return IndicatorResult(
                name="KAMA",
                type=IndicatorType.TREND,
                values=kama,
                signal=signal,
                strength=min(strength, 1.0),
                description=f"Kaufman Adaptive Moving Average ({period} periods)",
                parameters={'period': period}
            )
        except Exception as e:
            raise Exception(f"KAMA calculation error: {e}")
    
    # =================== MOMENTUM INDICATORS ===================
    
    def _calculate_rsi(self, df: pd.DataFrame, period: int = 14) -> IndicatorResult:
        """Relative Strength Index"""
        try:
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            current_rsi = rsi.iloc[-1]
            
            if current_rsi > 70:
                signal = "SELL"
                strength = (current_rsi - 70) / 30
            elif current_rsi < 30:
                signal = "BUY"
                strength = (30 - current_rsi) / 30
            else:
                signal = "NEUTRAL"
                strength = 0.5
            
            return IndicatorResult(
                name="RSI",
                type=IndicatorType.MOMENTUM,
                values=rsi,
                signal=signal,
                strength=min(strength, 1.0),
                description=f"Relative Strength Index ({period} periods)",
                parameters={'period': period}
            )
        except Exception as e:
            raise Exception(f"RSI calculation error: {e}")
    
    def _calculate_macd(self, df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> IndicatorResult:
        """Moving Average Convergence Divergence"""
        try:
            ema_fast = df['close'].ewm(span=fast).mean()
            ema_slow = df['close'].ewm(span=slow).mean()
            
            macd_line = ema_fast - ema_slow
            signal_line = macd_line.ewm(span=signal).mean()
            histogram = macd_line - signal_line
            
            macd_data = {
                'macd': macd_line,
                'signal': signal_line,
                'histogram': histogram
            }
            
            current_macd = macd_line.iloc[-1]
            current_signal = signal_line.iloc[-1]
            
            signal_str = "BUY" if current_macd > current_signal else "SELL"
            strength = abs(current_macd - current_signal) / abs(current_signal) if current_signal != 0 else 0
            
            return IndicatorResult(
                name="MACD",
                type=IndicatorType.MOMENTUM,
                values=macd_data,
                signal=signal_str,
                strength=min(strength, 1.0),
                description=f"MACD ({fast}, {slow}, {signal})",
                parameters={'fast': fast, 'slow': slow, 'signal': signal}
            )
        except Exception as e:
            raise Exception(f"MACD calculation error: {e}")
    
    def _calculate_cci(self, df: pd.DataFrame, period: int = 20) -> IndicatorResult:
        """Commodity Channel Index"""
        try:
            # Calculate typical price
            typical_price = (df['high'] + df['low'] + df['close']) / 3
            
            # Calculate moving average of typical price
            sma = typical_price.rolling(window=period).mean()
            
            # Calculate mean absolute deviation
            mad = typical_price.rolling(window=period).apply(
                lambda x: np.mean(np.abs(x - np.mean(x))), raw=True
            )
            
            # Calculate CCI
            cci = (typical_price - sma) / (0.015 * mad)
            
            # Handle division by zero
            cci = cci.fillna(0)
            
            current_cci = cci.iloc[-1]
            
            # Determine signal
            if current_cci > 100:
                signal_str = "SELL"
                strength = min(abs(current_cci - 100) / 100, 1.0)
            elif current_cci < -100:
                signal_str = "BUY"
                strength = min(abs(current_cci + 100) / 100, 1.0)
            else:
                signal_str = "NEUTRAL"
                strength = 0.5
            
            return IndicatorResult(
                name="CCI",
                type=IndicatorType.MOMENTUM,
                values=cci,
                signal=signal_str,
                strength=strength,
                description=f"Commodity Channel Index ({period} periods)",
                parameters={'period': period},
                interpretation=f"CCI at {current_cci:.2f} - {'Overbought' if current_cci > 100 else 'Oversold' if current_cci < -100 else 'Neutral'}"
            )
        except Exception as e:
            raise Exception(f"CCI calculation error: {e}")
    
    def _calculate_stochastic(self, df: pd.DataFrame, k_period: int = 14, d_period: int = 3) -> IndicatorResult:
        """Stochastic Oscillator"""
        try:
            low_min = df['low'].rolling(window=k_period).min()
            high_max = df['high'].rolling(window=k_period).max()
            
            k_percent = 100 * (df['close'] - low_min) / (high_max - low_min)
            d_percent = k_percent.rolling(window=d_period).mean()
            
            stoch_data = {
                'k': k_percent,
                'd': d_percent
            }
            
            current_k = k_percent.iloc[-1]
            current_d = d_percent.iloc[-1]
            
            if current_k > 80 and current_d > 80:
                signal_str = "SELL"
                strength = 0.8
            elif current_k < 20 and current_d < 20:
                signal_str = "BUY"
                strength = 0.8
            else:
                signal_str = "NEUTRAL"
                strength = 0.5
            
            return IndicatorResult(
                name="STOCH",
                type=IndicatorType.MOMENTUM,
                values=stoch_data,
                signal=signal_str,
                strength=strength,
                description=f"Stochastic Oscillator ({k_period}, {d_period})",
                parameters={'k_period': k_period, 'd_period': d_period}
            )
        except Exception as e:
            raise Exception(f"Stochastic calculation error: {e}")
    
    def _calculate_stochastic_rsi(self, df: pd.DataFrame, period: int = 14) -> IndicatorResult:
        """Stochastic RSI"""
        try:
            if not TA_AVAILABLE:
                raise Exception("TA library required for Stochastic RSI calculation")
            
            stoch_rsi = ta.momentum.StochRSIIndicator(close=df['close'], window=period)
            
            stoch_rsi_data = {
                'stoch_rsi': stoch_rsi.stochrsi(),
                'stoch_rsi_k': stoch_rsi.stochrsi_k(),
                'stoch_rsi_d': stoch_rsi.stochrsi_d()
            }
            
            current_stoch_rsi = stoch_rsi.stochrsi().iloc[-1]
            
            if current_stoch_rsi > 0.8:
                signal_str = "SELL"
                strength = 0.8
            elif current_stoch_rsi < 0.2:
                signal_str = "BUY"
                strength = 0.8
            else:
                signal_str = "NEUTRAL"
                strength = 0.5
            
            return IndicatorResult(
                name="STOCH_RSI",
                type=IndicatorType.MOMENTUM,
                values=stoch_rsi_data,
                signal=signal_str,
                strength=strength,
                description=f"Stochastic RSI ({period} periods)",
                parameters={'period': period}
            )
        except Exception as e:
            raise Exception(f"Stochastic RSI calculation error: {e}")
    
    def _calculate_williams_r(self, df: pd.DataFrame, period: int = 14) -> IndicatorResult:
        """Williams %R"""
        try:
            high_max = df['high'].rolling(window=period).max()
            low_min = df['low'].rolling(window=period).min()
            
            williams_r = -100 * (high_max - df['close']) / (high_max - low_min)
            
            current_wr = williams_r.iloc[-1]
            
            if current_wr > -20:
                signal_str = "SELL"
                strength = 0.8
            elif current_wr < -80:
                signal_str = "BUY"
                strength = 0.8
            else:
                signal_str = "NEUTRAL"
                strength = 0.5
            
            return IndicatorResult(
                name="WILLIAMS_R",
                type=IndicatorType.MOMENTUM,
                values=williams_r,
                signal=signal_str,
                strength=strength,
                description=f"Williams %R ({period} periods)",
                parameters={'period': period}
            )
        except Exception as e:
            raise Exception(f"Williams %R calculation error: {e}")
    
    def _calculate_roc(self, df: pd.DataFrame, period: int = 12) -> IndicatorResult:
        """Rate of Change"""
        try:
            roc = ((df['close'] - df['close'].shift(period)) / df['close'].shift(period)) * 100
            
            current_roc = roc.iloc[-1]
            
            signal_str = "BUY" if current_roc > 0 else "SELL"
            strength = abs(current_roc) / 10  # Normalize to 0-1 range
            
            return IndicatorResult(
                name="ROC",
                type=IndicatorType.MOMENTUM,
                values=roc,
                signal=signal_str,
                strength=min(strength, 1.0),
                description=f"Rate of Change ({period} periods)",
                parameters={'period': period}
            )
        except Exception as e:
            raise Exception(f"ROC calculation error: {e}")
    
    def _calculate_momentum(self, df: pd.DataFrame, period: int = 10) -> IndicatorResult:
        """Momentum"""
        try:
            momentum = df['close'] - df['close'].shift(period)
            
            current_momentum = momentum.iloc[-1]
            
            signal_str = "BUY" if current_momentum > 0 else "SELL"
            strength = abs(current_momentum) / df['close'].iloc[-1]
            
            return IndicatorResult(
                name="MOMENTUM",
                type=IndicatorType.MOMENTUM,
                values=momentum,
                signal=signal_str,
                strength=min(strength, 1.0),
                description=f"Momentum ({period} periods)",
                parameters={'period': period}
            )
        except Exception as e:
            raise Exception(f"Momentum calculation error: {e}")
    
    def _calculate_tsi(self, df: pd.DataFrame, long: int = 25, short: int = 13) -> IndicatorResult:
        """True Strength Index"""
        try:
            if not TA_AVAILABLE:
                raise Exception("TA library required for TSI calculation")
            
            tsi = ta.momentum.TSIIndicator(close=df['close'], window_slow=long, window_fast=short).tsi()
            
            current_tsi = tsi.iloc[-1]
            
            if current_tsi > 0:
                signal_str = "BUY"
                strength = abs(current_tsi) / 100
            else:
                signal_str = "SELL"
                strength = abs(current_tsi) / 100
            
            return IndicatorResult(
                name="TSI",
                type=IndicatorType.MOMENTUM,
                values=tsi,
                signal=signal_str,
                strength=min(strength, 1.0),
                description=f"True Strength Index ({long}, {short})",
                parameters={'long': long, 'short': short}
            )
        except Exception as e:
            raise Exception(f"TSI calculation error: {e}")
    
    # =================== VOLUME INDICATORS ===================
    
    def _calculate_obv(self, df: pd.DataFrame) -> IndicatorResult:
        """On-Balance Volume"""
        try:
            obv = pd.Series(index=df.index, dtype=float)
            obv.iloc[0] = df['volume'].iloc[0]
            
            for i in range(1, len(df)):
                if df['close'].iloc[i] > df['close'].iloc[i-1]:
                    obv.iloc[i] = obv.iloc[i-1] + df['volume'].iloc[i]
                elif df['close'].iloc[i] < df['close'].iloc[i-1]:
                    obv.iloc[i] = obv.iloc[i-1] - df['volume'].iloc[i]
                else:
                    obv.iloc[i] = obv.iloc[i-1]
            
            # Calculate OBV trend
            obv_ma = obv.rolling(window=20).mean()
            current_obv = obv.iloc[-1]
            current_obv_ma = obv_ma.iloc[-1]
            
            signal_str = "BUY" if current_obv > current_obv_ma else "SELL"
            strength = abs(current_obv - current_obv_ma) / current_obv_ma if current_obv_ma != 0 else 0
            
            return IndicatorResult(
                name="OBV",
                type=IndicatorType.VOLUME,
                values=obv,
                signal=signal_str,
                strength=min(strength, 1.0),
                description="On-Balance Volume",
                parameters={}
            )
        except Exception as e:
            raise Exception(f"OBV calculation error: {e}")
    
    def _calculate_ad(self, df: pd.DataFrame) -> IndicatorResult:
        """Accumulation/Distribution Line"""
        try:
            clv = ((df['close'] - df['low']) - (df['high'] - df['close'])) / (df['high'] - df['low'])
            clv = clv.fillna(0)
            
            ad = (clv * df['volume']).cumsum()
            
            # Calculate AD trend
            ad_ma = ad.rolling(window=20).mean()
            current_ad = ad.iloc[-1]
            current_ad_ma = ad_ma.iloc[-1]
            
            signal_str = "BUY" if current_ad > current_ad_ma else "SELL"
            strength = abs(current_ad - current_ad_ma) / abs(current_ad_ma) if current_ad_ma != 0 else 0
            
            return IndicatorResult(
                name="AD",
                type=IndicatorType.VOLUME,
                values=ad,
                signal=signal_str,
                strength=min(strength, 1.0),
                description="Accumulation/Distribution Line",
                parameters={}
            )
        except Exception as e:
            raise Exception(f"AD calculation error: {e}")
    
    def _calculate_cmf(self, df: pd.DataFrame, period: int = 20) -> IndicatorResult:
        """Chaikin Money Flow"""
        try:
            if not TA_AVAILABLE:
                raise Exception("TA library required for CMF calculation")
            
            cmf = ta.volume.ChaikinMoneyFlowIndicator(
                high=df['high'], low=df['low'], close=df['close'], volume=df['volume'], window=period
            ).chaikin_money_flow()
            
            current_cmf = cmf.iloc[-1]
            
            if current_cmf > 0.1:
                signal_str = "BUY"
                strength = min(current_cmf, 1.0)
            elif current_cmf < -0.1:
                signal_str = "SELL"
                strength = min(abs(current_cmf), 1.0)
            else:
                signal_str = "NEUTRAL"
                strength = 0.5
            
            return IndicatorResult(
                name="CMF",
                type=IndicatorType.VOLUME,
                values=cmf,
                signal=signal_str,
                strength=strength,
                description=f"Chaikin Money Flow ({period} periods)",
                parameters={'period': period}
            )
        except Exception as e:
            raise Exception(f"CMF calculation error: {e}")
    
    def _calculate_fi(self, df: pd.DataFrame, period: int = 13) -> IndicatorResult:
        """Force Index"""
        try:
            if not TA_AVAILABLE:
                raise Exception("TA library required for FI calculation")
            
            fi = ta.volume.ForceIndexIndicator(
                close=df['close'], volume=df['volume'], window=period
            ).force_index()
            
            current_fi = fi.iloc[-1]
            
            signal_str = "BUY" if current_fi > 0 else "SELL"
            strength = abs(current_fi) / df['volume'].iloc[-1]
            
            return IndicatorResult(
                name="FI",
                type=IndicatorType.VOLUME,
                values=fi,
                signal=signal_str,
                strength=min(strength, 1.0),
                description=f"Force Index ({period} periods)",
                parameters={'period': period}
            )
        except Exception as e:
            raise Exception(f"FI calculation error: {e}")
    
    def _calculate_nvi(self, df: pd.DataFrame) -> IndicatorResult:
        """Negative Volume Index"""
        try:
            if not TA_AVAILABLE:
                raise Exception("TA library required for NVI calculation")
            
            nvi = ta.volume.NegativeVolumeIndexIndicator(
                close=df['close'], volume=df['volume']
            ).negative_volume_index()
            
            current_nvi = nvi.iloc[-1]
            previous_nvi = nvi.iloc[-2]
            
            signal_str = "BUY" if current_nvi > previous_nvi else "SELL"
            strength = abs(current_nvi - previous_nvi) / previous_nvi if previous_nvi != 0 else 0
            
            return IndicatorResult(
                name="NVI",
                type=IndicatorType.VOLUME,
                values=nvi,
                signal=signal_str,
                strength=min(strength, 1.0),
                description="Negative Volume Index",
                parameters={}
            )
        except Exception as e:
            raise Exception(f"NVI calculation error: {e}")
    
    def _calculate_pvi(self, df: pd.DataFrame) -> IndicatorResult:
        """Positive Volume Index"""
        try:
            pvi = pd.Series(index=df.index, dtype=float)
            pvi.iloc[0] = 1000  # Starting value
            
            for i in range(1, len(df)):
                if df['volume'].iloc[i] > df['volume'].iloc[i-1]:
                    pvi.iloc[i] = pvi.iloc[i-1] * (df['close'].iloc[i] / df['close'].iloc[i-1])
                else:
                    pvi.iloc[i] = pvi.iloc[i-1]
            
            current_pvi = pvi.iloc[-1]
            previous_pvi = pvi.iloc[-2]
            
            signal_str = "BUY" if current_pvi > previous_pvi else "SELL"
            strength = abs(current_pvi - previous_pvi) / previous_pvi if previous_pvi != 0 else 0
            
            return IndicatorResult(
                name="PVI",
                type=IndicatorType.VOLUME,
                values=pvi,
                signal=signal_str,
                strength=min(strength, 1.0),
                description="Positive Volume Index",
                parameters={}
            )
        except Exception as e:
            raise Exception(f"PVI calculation error: {e}")
    
    def _calculate_vpt(self, df: pd.DataFrame) -> IndicatorResult:
        """Volume-Price Trend"""
        try:
            if not TA_AVAILABLE:
                raise Exception("TA library required for VPT calculation")
            
            vpt = ta.volume.VolumePriceTrendIndicator(
                close=df['close'], volume=df['volume']
            ).volume_price_trend()
            
            current_vpt = vpt.iloc[-1]
            previous_vpt = vpt.iloc[-2]
            
            signal_str = "BUY" if current_vpt > previous_vpt else "SELL"
            strength = abs(current_vpt - previous_vpt) / abs(previous_vpt) if previous_vpt != 0 else 0
            
            return IndicatorResult(
                name="VPT",
                type=IndicatorType.VOLUME,
                values=vpt,
                signal=signal_str,
                strength=min(strength, 1.0),
                description="Volume-Price Trend",
                parameters={}
            )
        except Exception as e:
            raise Exception(f"VPT calculation error: {e}")
    
    def _calculate_mfi(self, df: pd.DataFrame, period: int = 14) -> IndicatorResult:
        """Money Flow Index"""
        try:
            if not TA_AVAILABLE:
                raise Exception("TA library required for MFI calculation")
            
            mfi = ta.volume.MFIIndicator(
                high=df['high'], low=df['low'], close=df['close'], volume=df['volume'], window=period
            ).money_flow_index()
            
            current_mfi = mfi.iloc[-1]
            
            if current_mfi > 80:
                signal_str = "SELL"
                strength = (current_mfi - 80) / 20
            elif current_mfi < 20:
                signal_str = "BUY"
                strength = (20 - current_mfi) / 20
            else:
                signal_str = "NEUTRAL"
                strength = 0.5
            
            return IndicatorResult(
                name="MFI",
                type=IndicatorType.VOLUME,
                values=mfi,
                signal=signal_str,
                strength=min(strength, 1.0),
                description=f"Money Flow Index ({period} periods)",
                parameters={'period': period}
            )
        except Exception as e:
            raise Exception(f"MFI calculation error: {e}")
    
    def _calculate_volume_profile(self, df: pd.DataFrame, bins: int = 20) -> IndicatorResult:
        """Volume Profile"""
        try:
            price_min = df['low'].min()
            price_max = df['high'].max()
            
            # Create price levels
            price_levels = np.linspace(price_min, price_max, bins + 1)
            volume_profile = np.zeros(bins)
            
            # Calculate volume at each price level
            for i in range(len(df)):
                high_price = df['high'].iloc[i]
                low_price = df['low'].iloc[i]
                volume = df['volume'].iloc[i]
                
                # Find which bins this candle touches
                high_bin = np.searchsorted(price_levels, high_price) - 1
                low_bin = np.searchsorted(price_levels, low_price) - 1
                
                # Distribute volume across bins
                if high_bin == low_bin:
                    if 0 <= high_bin < bins:
                        volume_profile[high_bin] += volume
                else:
                    bins_touched = high_bin - low_bin + 1
                    volume_per_bin = volume / bins_touched
                    for bin_idx in range(low_bin, high_bin + 1):
                        if 0 <= bin_idx < bins:
                            volume_profile[bin_idx] += volume_per_bin
            
            # Find POC (Point of Control)
            poc_idx = np.argmax(volume_profile)
            poc_price = (price_levels[poc_idx] + price_levels[poc_idx + 1]) / 2
            
            # Calculate Value Area (70% of volume)
            total_volume = volume_profile.sum()
            target_volume = total_volume * 0.7
            
            # Start from POC and expand
            value_area_volume = volume_profile[poc_idx]
            value_area_low = poc_idx
            value_area_high = poc_idx
            
            while value_area_volume < target_volume and (value_area_low > 0 or value_area_high < bins - 1):
                # Choose direction with higher volume
                left_volume = volume_profile[value_area_low - 1] if value_area_low > 0 else 0
                right_volume = volume_profile[value_area_high + 1] if value_area_high < bins - 1 else 0
                
                if left_volume >= right_volume and value_area_low > 0:
                    value_area_low -= 1
                    value_area_volume += left_volume
                elif value_area_high < bins - 1:
                    value_area_high += 1
                    value_area_volume += right_volume
                else:
                    break
            
            vah_price = (price_levels[value_area_high] + price_levels[value_area_high + 1]) / 2
            val_price = (price_levels[value_area_low] + price_levels[value_area_low + 1]) / 2
            
            volume_profile_data = {
                'price_levels': price_levels[:-1],
                'volume_profile': volume_profile,
                'poc_price': poc_price,
                'vah_price': vah_price,
                'val_price': val_price
            }
            
            # Determine signal based on current price vs POC
            current_price = df['close'].iloc[-1]
            if current_price > poc_price:
                signal_str = "BUY"
                strength = min((current_price - poc_price) / poc_price, 1.0)
            else:
                signal_str = "SELL"
                strength = min((poc_price - current_price) / poc_price, 1.0)
            
            return IndicatorResult(
                name="VOLUME_PROFILE",
                type=IndicatorType.VOLUME,
                values=volume_profile_data,
                signal=signal_str,
                strength=strength,
                description=f"Volume Profile ({bins} levels)",
                parameters={'bins': bins}
            )
        except Exception as e:
            raise Exception(f"Volume Profile calculation error: {e}")
    
    # =================== VOLATILITY INDICATORS ===================
    
    def _calculate_bollinger_bands(self, df: pd.DataFrame, period: int = 20, std_dev: float = 2.0) -> IndicatorResult:
        """Bollinger Bands"""
        try:
            sma = df['close'].rolling(window=period).mean()
            std = df['close'].rolling(window=period).std()
            
            upper_band = sma + (std * std_dev)
            lower_band = sma - (std * std_dev)
            
            bb_data = {
                'upper': upper_band,
                'middle': sma,
                'lower': lower_band,
                'width': (upper_band - lower_band) / sma,
                'position': (df['close'] - lower_band) / (upper_band - lower_band)
            }
            
            current_price = df['close'].iloc[-1]
            current_upper = upper_band.iloc[-1]
            current_lower = lower_band.iloc[-1]
            current_middle = sma.iloc[-1]
            
            if current_price > current_upper:
                signal_str = "SELL"
                strength = (current_price - current_upper) / current_upper
            elif current_price < current_lower:
                signal_str = "BUY"
                strength = (current_lower - current_price) / current_lower
            else:
                signal_str = "NEUTRAL"
                strength = 0.5
            
            return IndicatorResult(
                name="BB",
                type=IndicatorType.VOLATILITY,
                values=bb_data,
                signal=signal_str,
                strength=min(strength, 1.0),
                description=f"Bollinger Bands ({period}, {std_dev})",
                parameters={'period': period, 'std_dev': std_dev}
            )
        except Exception as e:
            raise Exception(f"Bollinger Bands calculation error: {e}")
    
    def _calculate_keltner_channels(self, df: pd.DataFrame, period: int = 20, multiplier: float = 2.0) -> IndicatorResult:
        """Keltner Channels"""
        try:
            if not TA_AVAILABLE:
                raise Exception("TA library required for Keltner Channels calculation")
            
            kc = ta.volatility.KeltnerChannel(
                high=df['high'], low=df['low'], close=df['close'], window=period, window_atr=period
            )
            
            kc_data = {
                'upper': kc.keltner_channel_hband(),
                'middle': kc.keltner_channel_mband(),
                'lower': kc.keltner_channel_lband()
            }
            
            current_price = df['close'].iloc[-1]
            current_upper = kc.keltner_channel_hband().iloc[-1]
            current_lower = kc.keltner_channel_lband().iloc[-1]
            
            if current_price > current_upper:
                signal_str = "SELL"
                strength = (current_price - current_upper) / current_upper
            elif current_price < current_lower:
                signal_str = "BUY"
                strength = (current_lower - current_price) / current_lower
            else:
                signal_str = "NEUTRAL"
                strength = 0.5
            
            return IndicatorResult(
                name="KC",
                type=IndicatorType.VOLATILITY,
                values=kc_data,
                signal=signal_str,
                strength=min(strength, 1.0),
                description=f"Keltner Channels ({period}, {multiplier})",
                parameters={'period': period, 'multiplier': multiplier}
            )
        except Exception as e:
            raise Exception(f"Keltner Channels calculation error: {e}")
    
    def _calculate_donchian_channels(self, df: pd.DataFrame, period: int = 20) -> IndicatorResult:
        """Donchian Channels"""
        try:
            if not TA_AVAILABLE:
                raise Exception("TA library required for Donchian Channels calculation")
            
            dc = ta.volatility.DonchianChannel(
                high=df['high'], low=df['low'], close=df['close'], window=period
            )
            
            dc_data = {
                'upper': dc.donchian_channel_hband(),
                'middle': dc.donchian_channel_mband(),
                'lower': dc.donchian_channel_lband()
            }
            
            current_price = df['close'].iloc[-1]
            current_upper = dc.donchian_channel_hband().iloc[-1]
            current_lower = dc.donchian_channel_lband().iloc[-1]
            
            if current_price > current_upper:
                signal_str = "SELL"
                strength = (current_price - current_upper) / current_upper
            elif current_price < current_lower:
                signal_str = "BUY"
                strength = (current_lower - current_price) / current_lower
            else:
                signal_str = "NEUTRAL"
                strength = 0.5
            
            return IndicatorResult(
                name="DC",
                type=IndicatorType.VOLATILITY,
                values=dc_data,
                signal=signal_str,
                strength=min(strength, 1.0),
                description=f"Donchian Channels ({period} periods)",
                parameters={'period': period}
            )
        except Exception as e:
            raise Exception(f"Donchian Channels calculation error: {e}")
    
    def _calculate_atr(self, df: pd.DataFrame, period: int = 14) -> IndicatorResult:
        """Average True Range"""
        try:
            high_low = df['high'] - df['low']
            high_close = np.abs(df['high'] - df['close'].shift())
            low_close = np.abs(df['low'] - df['close'].shift())
            
            tr = np.maximum(high_low, np.maximum(high_close, low_close))
            atr = tr.rolling(window=period).mean()
            
            current_atr = atr.iloc[-1]
            current_price = df['close'].iloc[-1]
            
            # Calculate volatility percentage
            volatility_pct = (current_atr / current_price) * 100
            
            if volatility_pct > 5:
                signal_str = "HIGH_VOLATILITY"
                strength = min(volatility_pct / 10, 1.0)
            elif volatility_pct < 2:
                signal_str = "LOW_VOLATILITY"
                strength = 1.0 - (volatility_pct / 2)
            else:
                signal_str = "NORMAL_VOLATILITY"
                strength = 0.5
            
            return IndicatorResult(
                name="ATR",
                type=IndicatorType.VOLATILITY,
                values=atr,
                signal=signal_str,
                strength=strength,
                description=f"Average True Range ({period} periods)",
                parameters={'period': period}
            )
        except Exception as e:
            raise Exception(f"ATR calculation error: {e}")
    
    def _calculate_natr(self, df: pd.DataFrame, period: int = 14) -> IndicatorResult:
        """Normalized Average True Range"""
        try:
            atr_result = self._calculate_atr(df, period)
            atr = atr_result.values
            
            natr = (atr / df['close']) * 100
            
            current_natr = natr.iloc[-1]
            
            if current_natr > 3:
                signal_str = "HIGH_VOLATILITY"
                strength = min(current_natr / 6, 1.0)
            elif current_natr < 1:
                signal_str = "LOW_VOLATILITY"
                strength = 1.0 - current_natr
            else:
                signal_str = "NORMAL_VOLATILITY"
                strength = 0.5
            
            return IndicatorResult(
                name="NATR",
                type=IndicatorType.VOLATILITY,
                values=natr,
                signal=signal_str,
                strength=strength,
                description=f"Normalized Average True Range ({period} periods)",
                parameters={'period': period}
            )
        except Exception as e:
            raise Exception(f"NATR calculation error: {e}")
    
    def _calculate_true_range(self, df: pd.DataFrame) -> IndicatorResult:
        """True Range"""
        try:
            high_low = df['high'] - df['low']
            high_close = np.abs(df['high'] - df['close'].shift())
            low_close = np.abs(df['low'] - df['close'].shift())
            
            tr = np.maximum(high_low, np.maximum(high_close, low_close))
            
            current_tr = tr.iloc[-1]
            current_price = df['close'].iloc[-1]
            
            # Calculate volatility percentage
            volatility_pct = (current_tr / current_price) * 100
            
            if volatility_pct > 3:
                signal_str = "HIGH_VOLATILITY"
                strength = min(volatility_pct / 6, 1.0)
            elif volatility_pct < 1:
                signal_str = "LOW_VOLATILITY"
                strength = 1.0 - volatility_pct
            else:
                signal_str = "NORMAL_VOLATILITY"
                strength = 0.5
            
            return IndicatorResult(
                name="TRANGE",
                type=IndicatorType.VOLATILITY,
                values=tr,
                signal=signal_str,
                strength=strength,
                description="True Range",
                parameters={}
            )
        except Exception as e:
            raise Exception(f"True Range calculation error: {e}")
    
    def _calculate_vhf(self, df: pd.DataFrame, period: int = 28) -> IndicatorResult:
        """Vertical Horizontal Filter"""
        try:
            # Calculate VHF
            highest_high = df['high'].rolling(window=period).max()
            lowest_low = df['low'].rolling(window=period).min()
            
            price_changes = df['close'].diff().abs().rolling(window=period).sum()
            
            vhf = (highest_high - lowest_low) / price_changes
            
            current_vhf = vhf.iloc[-1]
            
            if current_vhf > 0.35:
                signal_str = "TRENDING"
                strength = min(current_vhf, 1.0)
            elif current_vhf < 0.25:
                signal_str = "RANGING"
                strength = 1.0 - (current_vhf / 0.25)
            else:
                signal_str = "NEUTRAL"
                strength = 0.5
            
            return IndicatorResult(
                name="VHF",
                type=IndicatorType.VOLATILITY,
                values=vhf,
                signal=signal_str,
                strength=strength,
                description=f"Vertical Horizontal Filter ({period} periods)",
                parameters={'period': period}
            )
        except Exception as e:
            raise Exception(f"VHF calculation error: {e}")
    
    # =================== CUSTOM INDICATORS ===================
    
    def _calculate_market_cipher(self, df: pd.DataFrame) -> IndicatorResult:
        """Market Cipher Indicator (Custom)"""
        try:
            # Combine multiple indicators for market cipher
            rsi_result = self._calculate_rsi(df, 14)
            macd_result = self._calculate_macd(df)
            bb_result = self._calculate_bollinger_bands(df)
            
            # Calculate composite score
            cipher_score = 0
            
            # RSI component
            if rsi_result.values is not None:
                current_rsi = rsi_result.values.iloc[-1]
                if current_rsi > 70:
                    cipher_score -= 2
                elif current_rsi < 30:
                    cipher_score += 2
            
            # MACD component
            if macd_result.values is not None:
                macd_data = macd_result.values
                if isinstance(macd_data, dict):
                    macd_line = macd_data.get('macd', pd.Series()).iloc[-1] if hasattr(macd_data.get('macd', pd.Series()), 'iloc') else 0
                    signal_line = macd_data.get('signal', pd.Series()).iloc[-1] if hasattr(macd_data.get('signal', pd.Series()), 'iloc') else 0
                    
                    if macd_line > signal_line:
                        cipher_score += 1
                    else:
                        cipher_score -= 1
            
            # Bollinger Bands component
            if bb_result.values is not None:
                bb_data = bb_result.values
                if isinstance(bb_data, dict):
                    current_price = df['close'].iloc[-1]
                    upper_band = bb_data.get('upper', pd.Series()).iloc[-1] if hasattr(bb_data.get('upper', pd.Series()), 'iloc') else current_price
                    lower_band = bb_data.get('lower', pd.Series()).iloc[-1] if hasattr(bb_data.get('lower', pd.Series()), 'iloc') else current_price
                    
                    if current_price > upper_band:
                        cipher_score -= 1
                    elif current_price < lower_band:
                        cipher_score += 1
            
            # Determine signal
            if cipher_score >= 2:
                signal_str = "STRONG_BUY"
                strength = min(cipher_score / 4, 1.0)
            elif cipher_score >= 1:
                signal_str = "BUY"
                strength = cipher_score / 4
            elif cipher_score <= -2:
                signal_str = "STRONG_SELL"
                strength = min(abs(cipher_score) / 4, 1.0)
            elif cipher_score <= -1:
                signal_str = "SELL"
                strength = abs(cipher_score) / 4
            else:
                signal_str = "NEUTRAL"
                strength = 0.5
            
            return IndicatorResult(
                name="MARKET_CIPHER",
                type=IndicatorType.CUSTOM,
                values=cipher_score,
                signal=signal_str,
                strength=strength,
                description="Market Cipher Composite Indicator",
                parameters={}
            )
        except Exception as e:
            raise Exception(f"Market Cipher calculation error: {e}")
    
    def _calculate_whale_activity(self, df: pd.DataFrame) -> IndicatorResult:
        """Whale Activity Indicator (Custom)"""
        try:
            # Calculate unusual volume patterns
            volume_ma = df['volume'].rolling(window=20).mean()
            volume_std = df['volume'].rolling(window=20).std()
            
            # Identify whale activity based on volume spikes
            whale_threshold = volume_ma + (2 * volume_std)
            whale_activity = df['volume'] > whale_threshold
            
            # Calculate whale pressure score
            recent_whale_count = whale_activity.tail(5).sum()
            total_whale_volume = df.loc[whale_activity, 'volume'].tail(5).sum()
            
            # Determine if whales are buying or selling
            whale_price_moves = df.loc[whale_activity, 'close'].pct_change().tail(5)
            avg_whale_move = whale_price_moves.mean()
            
            if recent_whale_count >= 2 and avg_whale_move > 0.01:
                signal_str = "WHALE_BUYING"
                strength = min(recent_whale_count / 5, 1.0)
            elif recent_whale_count >= 2 and avg_whale_move < -0.01:
                signal_str = "WHALE_SELLING"
                strength = min(recent_whale_count / 5, 1.0)
            else:
                signal_str = "NORMAL_ACTIVITY"
                strength = 0.5
            
            whale_data = {
                'whale_activity': whale_activity,
                'whale_count': recent_whale_count,
                'whale_volume': total_whale_volume,
                'whale_pressure': avg_whale_move
            }
            
            return IndicatorResult(
                name="WHALE_ACTIVITY",
                type=IndicatorType.CUSTOM,
                values=whale_data,
                signal=signal_str,
                strength=strength,
                description="Whale Activity Detection",
                parameters={}
            )
        except Exception as e:
            raise Exception(f"Whale Activity calculation error: {e}")
    
    def _calculate_smart_money_flow(self, df: pd.DataFrame) -> IndicatorResult:
        """Smart Money Flow Indicator (Custom)"""
        try:
            # Calculate smart money flow based on price action and volume
            price_changes = df['close'].pct_change()
            volume_changes = df['volume'].pct_change()
            
            # Smart money characteristics: high volume with small price moves
            smart_money_ratio = volume_changes / (price_changes.abs() + 0.001)  # Add small value to avoid division by zero
            
            # Calculate smart money flow
            smart_money_flow = (smart_money_ratio * df['volume']).rolling(window=10).sum()
            
            # Normalize to percentage
            smart_money_pct = smart_money_flow.pct_change(10) * 100
            
            current_flow = smart_money_pct.iloc[-1]
            
            if current_flow > 20:
                signal_str = "SMART_MONEY_BUYING"
                strength = min(current_flow / 50, 1.0)
            elif current_flow < -20:
                signal_str = "SMART_MONEY_SELLING"
                strength = min(abs(current_flow) / 50, 1.0)
            else:
                signal_str = "BALANCED_FLOW"
                strength = 0.5
            
            return IndicatorResult(
                name="SMART_MONEY_FLOW",
                type=IndicatorType.CUSTOM,
                values=smart_money_flow,
                signal=signal_str,
                strength=strength,
                description="Smart Money Flow Detection",
                parameters={}
            )
        except Exception as e:
            raise Exception(f"Smart Money Flow calculation error: {e}")
    
    def _calculate_liquidity_heatmap(self, df: pd.DataFrame) -> IndicatorResult:
        """Liquidity Heatmap Indicator (Custom)"""
        try:
            # Calculate liquidity zones based on volume and price clusters
            price_levels = np.linspace(df['low'].min(), df['high'].max(), 50)
            liquidity_map = np.zeros(len(price_levels))
            
            # Calculate liquidity at each price level
            for i in range(len(df)):
                high_price = df['high'].iloc[i]
                low_price = df['low'].iloc[i]
                volume = df['volume'].iloc[i]
                
                # Find price levels within this candle's range
                for j, level in enumerate(price_levels):
                    if low_price <= level <= high_price:
                        liquidity_map[j] += volume
            
            # Find high liquidity zones
            liquidity_threshold = np.percentile(liquidity_map, 80)
            high_liquidity_zones = price_levels[liquidity_map > liquidity_threshold]
            
            # Determine signal based on current price vs liquidity zones
            current_price = df['close'].iloc[-1]
            
            # Find nearest liquidity zone
            if len(high_liquidity_zones) > 0:
                nearest_zone = high_liquidity_zones[np.argmin(np.abs(high_liquidity_zones - current_price))]
                distance_to_zone = abs(current_price - nearest_zone) / current_price
                
                if distance_to_zone < 0.01:  # Within 1% of liquidity zone
                    signal_str = "LIQUIDITY_ZONE"
                    strength = 1.0 - distance_to_zone
                elif current_price > nearest_zone:
                    signal_str = "ABOVE_LIQUIDITY"
                    strength = distance_to_zone
                else:
                    signal_str = "BELOW_LIQUIDITY"
                    strength = distance_to_zone
            else:
                signal_str = "NO_LIQUIDITY_ZONES"
                strength = 0.5
            
            heatmap_data = {
                'price_levels': price_levels,
                'liquidity_map': liquidity_map,
                'high_liquidity_zones': high_liquidity_zones,
                'current_price': current_price
            }
            
            return IndicatorResult(
                name="LIQUIDITY_HEATMAP",
                type=IndicatorType.CUSTOM,
                values=heatmap_data,
                signal=signal_str,
                strength=min(strength, 1.0),
                description="Liquidity Heatmap Analysis",
                parameters={}
            )
        except Exception as e:
            raise Exception(f"Liquidity Heatmap calculation error: {e}")
    
    def _calculate_support_resistance(self, df: pd.DataFrame, window: int = 20) -> IndicatorResult:
        """Support and Resistance Levels (Custom)"""
        try:
            # Find local highs and lows
            highs = df['high'].rolling(window=window, center=True).max()
            lows = df['low'].rolling(window=window, center=True).min()
            
            # Identify peaks and troughs
            peaks = (df['high'] == highs)
            troughs = (df['low'] == lows)
            
            # Extract support and resistance levels
            resistance_levels = df.loc[peaks, 'high'].dropna().values
            support_levels = df.loc[troughs, 'low'].dropna().values
            
            # Get recent levels (last 10)
            recent_resistance = resistance_levels[-10:] if len(resistance_levels) >= 10 else resistance_levels
            recent_support = support_levels[-10:] if len(support_levels) >= 10 else support_levels
            
            # Determine signal based on current price vs levels
            current_price = df['close'].iloc[-1]
            
            # Find nearest resistance and support
            if len(recent_resistance) > 0:
                nearest_resistance = recent_resistance[np.argmin(np.abs(recent_resistance - current_price))]
                resistance_distance = abs(current_price - nearest_resistance) / current_price
            else:
                nearest_resistance = current_price
                resistance_distance = 1.0
            
            if len(recent_support) > 0:
                nearest_support = recent_support[np.argmin(np.abs(recent_support - current_price))]
                support_distance = abs(current_price - nearest_support) / current_price
            else:
                nearest_support = current_price
                support_distance = 1.0
            
            # Determine signal
            if resistance_distance < 0.02:  # Within 2% of resistance
                signal_str = "NEAR_RESISTANCE"
                strength = 1.0 - resistance_distance
            elif support_distance < 0.02:  # Within 2% of support
                signal_str = "NEAR_SUPPORT"
                strength = 1.0 - support_distance
            else:
                signal_str = "NEUTRAL"
                strength = 0.5
            
            sr_data = {
                'resistance_levels': recent_resistance.tolist(),
                'support_levels': recent_support.tolist(),
                'nearest_resistance': nearest_resistance,
                'nearest_support': nearest_support,
                'resistance_distance': resistance_distance,
                'support_distance': support_distance
            }
            
            return IndicatorResult(
                name="SUPPORT_RESISTANCE",
                type=IndicatorType.CUSTOM,
                values=sr_data,
                signal=signal_str,
                strength=min(strength, 1.0),
                description=f"Support/Resistance Analysis ({window} window)",
                parameters={'window': window}
            )
        except Exception as e:
            raise Exception(f"Support/Resistance calculation error: {e}")
    
    def _calculate_pattern_recognition(self, df: pd.DataFrame) -> IndicatorResult:
        """Pattern Recognition Indicator (Custom)"""
        try:
            patterns_detected = []
            
            # Doji pattern
            body_size = abs(df['close'] - df['open'])
            total_range = df['high'] - df['low']
            doji_ratio = body_size / (total_range + 0.001)  # Avoid division by zero
            
            recent_doji = (doji_ratio.tail(5) < 0.1).any()
            if recent_doji:
                patterns_detected.append("DOJI")
            
            # Hammer pattern
            lower_shadow = df['low'] - np.minimum(df['open'], df['close'])
            upper_shadow = df['high'] - np.maximum(df['open'], df['close'])
            
            hammer_condition = (lower_shadow > 2 * body_size) & (upper_shadow < 0.1 * lower_shadow)
            recent_hammer = hammer_condition.tail(3).any()
            if recent_hammer:
                patterns_detected.append("HAMMER")
            
            # Engulfing pattern
            bullish_engulfing = (
                (df['open'] < df['close']) &  # Current candle is green
                (df['open'].shift(1) > df['close'].shift(1)) &  # Previous candle is red
                (df['open'] < df['close'].shift(1)) &  # Current open < previous close
                (df['close'] > df['open'].shift(1))  # Current close > previous open
            )
            
            bearish_engulfing = (
                (df['open'] > df['close']) &  # Current candle is red
                (df['open'].shift(1) < df['close'].shift(1)) &  # Previous candle is green
                (df['open'] > df['close'].shift(1)) &  # Current open > previous close
                (df['close'] < df['open'].shift(1))  # Current close < previous open
            )
            
            if bullish_engulfing.tail(2).any():
                patterns_detected.append("BULLISH_ENGULFING")
            if bearish_engulfing.tail(2).any():
                patterns_detected.append("BEARISH_ENGULFING")
            
            # Determine overall signal
            bullish_patterns = ["HAMMER", "BULLISH_ENGULFING"]
            bearish_patterns = ["BEARISH_ENGULFING"]
            neutral_patterns = ["DOJI"]
            
            bullish_count = sum(1 for p in patterns_detected if p in bullish_patterns)
            bearish_count = sum(1 for p in patterns_detected if p in bearish_patterns)
            neutral_count = sum(1 for p in patterns_detected if p in neutral_patterns)
            
            if bullish_count > bearish_count:
                signal_str = "BULLISH_PATTERN"
                strength = bullish_count / len(bullish_patterns)
            elif bearish_count > bullish_count:
                signal_str = "BEARISH_PATTERN"
                strength = bearish_count / len(bearish_patterns)
            elif neutral_count > 0:
                signal_str = "NEUTRAL_PATTERN"
                strength = 0.5
            else:
                signal_str = "NO_PATTERN"
                strength = 0.3
            
            pattern_data = {
                'patterns_detected': patterns_detected,
                'bullish_count': bullish_count,
                'bearish_count': bearish_count,
                'neutral_count': neutral_count
            }
            
            return IndicatorResult(
                name="PATTERN_RECOGNITION",
                type=IndicatorType.CUSTOM,
                values=pattern_data,
                signal=signal_str,
                strength=min(strength, 1.0),
                description="Candlestick Pattern Recognition",
                parameters={}
            )
        except Exception as e:
            raise Exception(f"Pattern Recognition calculation error: {e}")
    
    def clear_cache(self):
        """Clear indicators cache"""
        self.indicators_cache.clear()
        logger.info("Indicators cache cleared")
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get cache information"""
        return {
            'cached_indicators': len(self.indicators_cache),
            'cache_size_mb': sum(len(str(v)) for v in self.indicators_cache.values()) / (1024 * 1024),
            'supported_indicators': list(self.supported_indicators.keys())
        }

def create_indicator_calculator() -> AdvancedIndicatorCalculator:
    """Factory function to create indicator calculator"""
    return AdvancedIndicatorCalculator()

# Global instance
indicator_calculator = create_indicator_calculator()