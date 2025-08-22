"""
Enhanced Multi-Timeframe Analysis with Confluence
Analyzes 1H, 4H, and Daily timeframes for stronger signals
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class EnhancedMultiTimeframe:
    """
    Professional multi-timeframe analysis with:
    - 1H for entry timing
    - 4H for trend confirmation  
    - Daily for major trend direction
    - Confluence scoring across timeframes
    """
    
    def __init__(self, okx_fetcher=None):
        self.okx_fetcher = okx_fetcher
        self.timeframe_weights = {
            '1H': 0.3,   # Entry timing
            '4H': 0.4,   # Trend confirmation
            '1D': 0.3    # Major trend
        }
        self.timeframes = ['1H', '4H', '1D']
        self.logger = logging.getLogger(f"{__name__}.EnhancedMultiTimeframe")
        self.logger.info("📊 Enhanced Multi-Timeframe Analyzer initialized (1H + 4H + Daily)")
    
    def analyze_all_timeframes(self, symbol: str) -> Dict[str, Any]:
        """
        Comprehensive multi-timeframe analysis with confluence
        """
        try:
            self.logger.info(f"🔍 Starting multi-timeframe analysis for {symbol}")
            
            # Collect analysis from all timeframes
            timeframe_data = {}
            for tf in self.timeframes:
                data = self._fetch_and_analyze_timeframe(symbol, tf)
                if data:
                    timeframe_data[tf] = data
            
            if not timeframe_data:
                return self._get_empty_analysis()
            
            # Calculate confluence and alignment
            confluence = self._calculate_confluence(timeframe_data)
            alignment = self._check_timeframe_alignment(timeframe_data)
            
            # Generate comprehensive recommendation
            recommendation = self._generate_mtf_recommendation(
                timeframe_data, confluence, alignment
            )
            
            # Identify key levels across timeframes
            key_levels = self._identify_key_levels(timeframe_data)
            
            return {
                'symbol': symbol,
                'timeframe_analysis': timeframe_data,
                'confluence': confluence,
                'alignment': alignment,
                'key_levels': key_levels,
                'recommendation': recommendation,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Multi-timeframe analysis error: {e}")
            return self._get_empty_analysis()
    
    def _fetch_and_analyze_timeframe(self, symbol: str, timeframe: str) -> Optional[Dict[str, Any]]:
        """
        Fetch and analyze single timeframe data
        """
        try:
            # Get candle data
            if self.okx_fetcher:
                from core.okx_fetcher import OKXFetcher
                fetcher = OKXFetcher() if not self.okx_fetcher else self.okx_fetcher
                
                # Normalize symbol for OKX
                okx_symbol = symbol if '-' in symbol else symbol.replace('USDT', '-USDT')
                market_data = fetcher.get_historical_data(okx_symbol, timeframe, limit=100)
                
                if not market_data or 'candles' not in market_data:
                    self.logger.warning(f"No data for {symbol} {timeframe}")
                    return None
                
                # Convert to DataFrame
                df = pd.DataFrame(market_data['candles'])
                if df.empty:
                    return None
                
                # Ensure numeric types
                for col in ['open', 'high', 'low', 'close', 'volume']:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
            else:
                # Fallback if no fetcher available
                return None
            
            # Perform technical analysis
            analysis = self._analyze_timeframe(df, timeframe)
            
            # Add SMC analysis for this timeframe
            smc_analysis = self._analyze_smc_timeframe(df)
            analysis['smc'] = smc_analysis
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing {timeframe}: {e}")
            return None
    
    def _analyze_timeframe(self, df: pd.DataFrame, timeframe: str) -> Dict[str, Any]:
        """
        Technical analysis for single timeframe
        """
        try:
            # Calculate indicators
            sma_20 = df['close'].rolling(20).mean()
            sma_50 = df['close'].rolling(50).mean()
            ema_9 = df['close'].ewm(span=9, adjust=False).mean()
            ema_21 = df['close'].ewm(span=21, adjust=False).mean()
            
            # RSI
            rsi = self._calculate_rsi(df['close'])
            
            # MACD
            macd, signal, histogram = self._calculate_macd(df['close'])
            
            # Bollinger Bands
            bb_upper, bb_middle, bb_lower = self._calculate_bollinger_bands(df['close'])
            
            # Current values
            current_price = float(df['close'].iloc[-1])
            current_volume = float(df['volume'].iloc[-1])
            avg_volume = float(df['volume'].rolling(20).mean().iloc[-1])
            
            # Trend determination
            trend = self._determine_trend(
                current_price, sma_20.iloc[-1], sma_50.iloc[-1],
                ema_9.iloc[-1], ema_21.iloc[-1]
            )
            
            # Support and Resistance
            support = float(df['low'].rolling(20).min().iloc[-1])
            resistance = float(df['high'].rolling(20).max().iloc[-1])
            
            # Price position
            price_position = self._calculate_price_position(
                current_price, bb_upper.iloc[-1], bb_lower.iloc[-1]
            )
            
            return {
                'timeframe': timeframe,
                'price': current_price,
                'trend': trend,
                'indicators': {
                    'rsi': float(rsi.iloc[-1]),
                    'macd': float(macd.iloc[-1]),
                    'macd_signal': float(signal.iloc[-1]),
                    'macd_histogram': float(histogram.iloc[-1]),
                    'sma_20': float(sma_20.iloc[-1]),
                    'sma_50': float(sma_50.iloc[-1]),
                    'ema_9': float(ema_9.iloc[-1]),
                    'ema_21': float(ema_21.iloc[-1]),
                    'bb_upper': float(bb_upper.iloc[-1]),
                    'bb_lower': float(bb_lower.iloc[-1])
                },
                'levels': {
                    'support': support,
                    'resistance': resistance,
                    'pivot': (df['high'].iloc[-1] + df['low'].iloc[-1] + df['close'].iloc[-1]) / 3
                },
                'volume': {
                    'current': current_volume,
                    'average': avg_volume,
                    'ratio': current_volume / avg_volume if avg_volume > 0 else 1
                },
                'momentum': self._determine_momentum(rsi.iloc[-1], macd.iloc[-1], histogram.iloc[-1]),
                'price_position': price_position
            }
            
        except Exception as e:
            self.logger.error(f"Timeframe analysis error: {e}")
            return {'timeframe': timeframe, 'error': str(e)}
    
    def _analyze_smc_timeframe(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        SMC analysis for single timeframe
        """
        try:
            # Identify swing points
            swing_highs, swing_lows = self._identify_swing_points(df)
            
            # Market structure
            structure = 'RANGING'
            if len(swing_highs) >= 2 and len(swing_lows) >= 2:
                if (swing_highs[-1] > swing_highs[-2] and swing_lows[-1] > swing_lows[-2]):
                    structure = 'BULLISH'
                elif (swing_highs[-1] < swing_highs[-2] and swing_lows[-1] < swing_lows[-2]):
                    structure = 'BEARISH'
            
            # Check for structure break
            current_price = float(df['close'].iloc[-1])
            structure_break = None
            if swing_highs and current_price > swing_highs[-1]:
                structure_break = 'BOS_UP'
            elif swing_lows and current_price < swing_lows[-1]:
                structure_break = 'BOS_DOWN'
            
            return {
                'structure': structure,
                'structure_break': structure_break,
                'swing_high': swing_highs[-1] if swing_highs else None,
                'swing_low': swing_lows[-1] if swing_lows else None
            }
            
        except Exception as e:
            self.logger.error(f"SMC timeframe analysis error: {e}")
            return {'structure': 'UNKNOWN'}
    
    def _identify_swing_points(self, df: pd.DataFrame, lookback: int = 5) -> tuple:
        """Identify swing highs and lows"""
        swing_highs = []
        swing_lows = []
        
        highs = df['high'].values
        lows = df['low'].values
        
        for i in range(lookback, len(df) - lookback):
            if highs[i] == max(highs[i-lookback:i+lookback+1]):
                swing_highs.append(float(highs[i]))
            if lows[i] == min(lows[i-lookback:i+lookback+1]):
                swing_lows.append(float(lows[i]))
        
        return swing_highs, swing_lows
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _calculate_macd(self, prices: pd.Series) -> tuple:
        """Calculate MACD"""
        ema_12 = prices.ewm(span=12, adjust=False).mean()
        ema_26 = prices.ewm(span=26, adjust=False).mean()
        macd = ema_12 - ema_26
        signal = macd.ewm(span=9, adjust=False).mean()
        histogram = macd - signal
        return macd, signal, histogram
    
    def _calculate_bollinger_bands(self, prices: pd.Series, period: int = 20, std_dev: int = 2) -> tuple:
        """Calculate Bollinger Bands"""
        middle = prices.rolling(period).mean()
        std = prices.rolling(period).std()
        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)
        return upper, middle, lower
    
    def _determine_trend(self, price: float, sma20: float, sma50: float, 
                        ema9: float, ema21: float) -> Dict[str, Any]:
        """Determine trend direction and strength"""
        trend_score = 0
        
        # Price vs MAs
        if price > sma20:
            trend_score += 1
        if price > sma50:
            trend_score += 1
        if sma20 > sma50:
            trend_score += 2
        
        # EMAs
        if ema9 > ema21:
            trend_score += 2
        if price > ema9:
            trend_score += 1
        
        # Determine trend
        if trend_score >= 5:
            direction = 'STRONG_BULLISH'
            strength = 90
        elif trend_score >= 3:
            direction = 'BULLISH'
            strength = 70
        elif trend_score <= -5:
            direction = 'STRONG_BEARISH'
            strength = 90
        elif trend_score <= -3:
            direction = 'BEARISH'
            strength = 70
        else:
            direction = 'NEUTRAL'
            strength = 50
        
        return {
            'direction': direction,
            'strength': strength,
            'score': trend_score
        }
    
    def _determine_momentum(self, rsi: float, macd: float, histogram: float) -> Dict[str, Any]:
        """Determine momentum status"""
        momentum_type = 'NEUTRAL'
        strength = 50
        
        if rsi > 70 and macd > 0 and histogram > 0:
            momentum_type = 'STRONG_BULLISH'
            strength = 85
        elif rsi > 60 and macd > 0:
            momentum_type = 'BULLISH'
            strength = 70
        elif rsi < 30 and macd < 0 and histogram < 0:
            momentum_type = 'STRONG_BEARISH'
            strength = 85
        elif rsi < 40 and macd < 0:
            momentum_type = 'BEARISH'
            strength = 70
        elif rsi > 70:
            momentum_type = 'OVERBOUGHT'
            strength = 60
        elif rsi < 30:
            momentum_type = 'OVERSOLD'
            strength = 60
        
        return {
            'type': momentum_type,
            'strength': strength
        }
    
    def _calculate_price_position(self, price: float, upper: float, lower: float) -> Dict[str, Any]:
        """Calculate price position within range"""
        if upper == lower:
            position_pct = 50
        else:
            position_pct = ((price - lower) / (upper - lower)) * 100
        
        zone = 'MIDDLE'
        if position_pct > 80:
            zone = 'UPPER'
        elif position_pct < 20:
            zone = 'LOWER'
        
        return {
            'percentage': float(position_pct),
            'zone': zone
        }
    
    def _calculate_confluence(self, timeframe_data: Dict[str, Dict]) -> Dict[str, Any]:
        """
        Calculate confluence score across timeframes
        """
        confluence_score = 0
        bullish_count = 0
        bearish_count = 0
        factors = []
        
        for tf, data in timeframe_data.items():
            if 'error' in data:
                continue
            
            weight = self.timeframe_weights.get(tf, 0.3)
            
            # Check trend direction
            if data['trend']['direction'] in ['STRONG_BULLISH', 'BULLISH']:
                bullish_count += 1
                confluence_score += 30 * weight
                factors.append(f"{tf} bullish trend")
            elif data['trend']['direction'] in ['STRONG_BEARISH', 'BEARISH']:
                bearish_count += 1
                confluence_score -= 30 * weight
                factors.append(f"{tf} bearish trend")
            
            # Check momentum
            if data['momentum']['type'] in ['STRONG_BULLISH', 'BULLISH']:
                confluence_score += 20 * weight
                factors.append(f"{tf} bullish momentum")
            elif data['momentum']['type'] in ['STRONG_BEARISH', 'BEARISH']:
                confluence_score -= 20 * weight
                factors.append(f"{tf} bearish momentum")
            
            # Check SMC structure
            if 'smc' in data:
                if data['smc']['structure'] == 'BULLISH':
                    confluence_score += 15 * weight
                    factors.append(f"{tf} bullish structure")
                elif data['smc']['structure'] == 'BEARISH':
                    confluence_score -= 15 * weight
                    factors.append(f"{tf} bearish structure")
        
        # Normalize score to 0-100
        normalized_score = 50 + confluence_score
        normalized_score = max(0, min(100, normalized_score))
        
        # Determine overall bias
        if bullish_count > bearish_count and normalized_score > 60:
            bias = 'BULLISH'
        elif bearish_count > bullish_count and normalized_score < 40:
            bias = 'BEARISH'
        else:
            bias = 'NEUTRAL'
        
        return {
            'score': float(normalized_score),
            'bias': bias,
            'bullish_timeframes': bullish_count,
            'bearish_timeframes': bearish_count,
            'factors': factors,
            'strength': 'HIGH' if normalized_score > 75 or normalized_score < 25 else 'MEDIUM' if normalized_score > 60 or normalized_score < 40 else 'LOW'
        }
    
    def _check_timeframe_alignment(self, timeframe_data: Dict[str, Dict]) -> Dict[str, Any]:
        """
        Check if timeframes are aligned
        """
        trends = []
        structures = []
        
        for tf in ['1D', '4H', '1H']:  # Check from higher to lower
            if tf in timeframe_data and 'error' not in timeframe_data[tf]:
                trends.append(timeframe_data[tf]['trend']['direction'])
                if 'smc' in timeframe_data[tf]:
                    structures.append(timeframe_data[tf]['smc']['structure'])
        
        # Check trend alignment
        all_bullish = all('BULLISH' in t for t in trends)
        all_bearish = all('BEARISH' in t for t in trends)
        
        # Check structure alignment
        structure_aligned = len(set(structures)) == 1 if structures else False
        
        alignment_score = 0
        if all_bullish or all_bearish:
            alignment_score = 100
        elif len(set(trends)) == 2:  # Partial alignment
            alignment_score = 60
        else:
            alignment_score = 30
        
        return {
            'aligned': all_bullish or all_bearish,
            'score': alignment_score,
            'trend_alignment': 'FULL' if all_bullish or all_bearish else 'PARTIAL' if len(set(trends)) == 2 else 'NONE',
            'structure_alignment': 'ALIGNED' if structure_aligned else 'MIXED',
            'details': {
                '1D': trends[0] if len(trends) > 0 else 'N/A',
                '4H': trends[1] if len(trends) > 1 else 'N/A',
                '1H': trends[2] if len(trends) > 2 else 'N/A'
            }
        }
    
    def _identify_key_levels(self, timeframe_data: Dict[str, Dict]) -> Dict[str, Any]:
        """
        Identify key support/resistance levels across timeframes
        """
        all_supports = []
        all_resistances = []
        
        for tf, data in timeframe_data.items():
            if 'levels' in data:
                all_supports.append({
                    'level': data['levels']['support'],
                    'timeframe': tf,
                    'strength': 'HIGH' if tf == '1D' else 'MEDIUM' if tf == '4H' else 'LOW'
                })
                all_resistances.append({
                    'level': data['levels']['resistance'],
                    'timeframe': tf,
                    'strength': 'HIGH' if tf == '1D' else 'MEDIUM' if tf == '4H' else 'LOW'
                })
        
        # Sort by level
        all_supports.sort(key=lambda x: x['level'], reverse=True)
        all_resistances.sort(key=lambda x: x['level'])
        
        return {
            'major_support': all_supports[0] if all_supports else None,
            'major_resistance': all_resistances[0] if all_resistances else None,
            'all_supports': all_supports[:3],  # Top 3
            'all_resistances': all_resistances[:3]  # Top 3
        }
    
    def _generate_mtf_recommendation(self, timeframe_data: Dict, 
                                     confluence: Dict, alignment: Dict) -> Dict[str, Any]:
        """
        Generate comprehensive trading recommendation
        """
        action = 'HOLD'
        confidence = 50
        reasoning = []
        entry_timeframe = None
        
        # Strong bullish setup
        if (confluence['bias'] == 'BULLISH' and confluence['score'] > 70 and 
            alignment['aligned'] and alignment['trend_alignment'] == 'FULL'):
            action = 'STRONG_BUY'
            confidence = min(95, confluence['score'])
            reasoning.append("All timeframes aligned bullish")
            reasoning.append(f"Confluence score: {confluence['score']:.1f}")
            entry_timeframe = '1H'
        
        # Moderate bullish setup
        elif confluence['bias'] == 'BULLISH' and confluence['score'] > 60:
            action = 'BUY'
            confidence = confluence['score']
            reasoning.append("Bullish bias across timeframes")
            reasoning.append(f"{confluence['bullish_timeframes']} of {len(timeframe_data)} timeframes bullish")
            entry_timeframe = '1H'
        
        # Strong bearish setup
        elif (confluence['bias'] == 'BEARISH' and confluence['score'] < 30 and 
              alignment['aligned'] and alignment['trend_alignment'] == 'FULL'):
            action = 'STRONG_SELL'
            confidence = min(95, 100 - confluence['score'])
            reasoning.append("All timeframes aligned bearish")
            reasoning.append(f"Confluence score: {confluence['score']:.1f}")
            entry_timeframe = '1H'
        
        # Moderate bearish setup
        elif confluence['bias'] == 'BEARISH' and confluence['score'] < 40:
            action = 'SELL'
            confidence = 100 - confluence['score']
            reasoning.append("Bearish bias across timeframes")
            reasoning.append(f"{confluence['bearish_timeframes']} of {len(timeframe_data)} timeframes bearish")
            entry_timeframe = '1H'
        
        # Neutral/conflicting signals
        else:
            reasoning.append("Mixed signals across timeframes")
            reasoning.append(f"Alignment score: {alignment['score']}")
            if confluence['score'] > 50:
                reasoning.append("Slight bullish bias, wait for confirmation")
            elif confluence['score'] < 50:
                reasoning.append("Slight bearish bias, wait for confirmation")
        
        return {
            'action': action,
            'confidence': float(confidence),
            'entry_timeframe': entry_timeframe,
            'reasoning': reasoning,
            'risk_level': 'LOW' if confidence > 80 else 'MEDIUM' if confidence > 60 else 'HIGH',
            'suggested_weight': min(100, confidence) / 100  # Position sizing suggestion
        }
    
    def _get_empty_analysis(self) -> Dict[str, Any]:
        """Return empty analysis structure"""
        return {
            'symbol': 'UNKNOWN',
            'timeframe_analysis': {},
            'confluence': {'score': 50, 'bias': 'NEUTRAL'},
            'alignment': {'aligned': False, 'score': 0},
            'key_levels': {},
            'recommendation': {
                'action': 'HOLD',
                'confidence': 50,
                'reasoning': ['Insufficient data']
            },
            'timestamp': datetime.now().isoformat()
        }