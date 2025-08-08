"""
Enhanced AI Signal Logic Engine
Mengatasi masalah confidence rendah dan transparansi reasoning
Dengan weight matrix, scoring system, dan rolling window analysis
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class EnhancedSignalLogic:
    """
    Enhanced Signal Logic dengan Weight Matrix dan Scoring System
    Mengatasi masalah confidence rendah dan transparansi reasoning
    """
    
    def __init__(self):
        # Weight Matrix untuk berbagai komponen signal
        self.weight_matrix = {
            # Technical Indicators
            'rsi_oversold': {'weight': 0.25, 'priority': 'high'},
            'rsi_overbought': {'weight': 0.25, 'priority': 'high'},
            'macd_bullish_cross': {'weight': 0.20, 'priority': 'medium'},
            'macd_bearish_cross': {'weight': 0.20, 'priority': 'medium'},
            'macd_histogram_momentum': {'weight': 0.15, 'priority': 'medium'},
            'ema_alignment': {'weight': 0.15, 'priority': 'medium'},
            'volume_confirmation': {'weight': 0.20, 'priority': 'high'},
            
            # SMC Analysis (Prioritized untuk high confidence)
            'bos_bullish': {'weight': 0.35, 'priority': 'critical'},
            'bos_bearish': {'weight': 0.35, 'priority': 'critical'},
            'choch_bullish': {'weight': 0.30, 'priority': 'critical'},
            'choch_bearish': {'weight': 0.30, 'priority': 'critical'},
            'order_block_bullish': {'weight': 0.25, 'priority': 'high'},
            'order_block_bearish': {'weight': 0.25, 'priority': 'high'},
            'fvg_bullish': {'weight': 0.20, 'priority': 'medium'},
            'fvg_bearish': {'weight': 0.20, 'priority': 'medium'},
            'liquidity_sweep': {'weight': 0.15, 'priority': 'medium'},
            
            # Price Action
            'trend_continuation': {'weight': 0.18, 'priority': 'medium'},
            'trend_reversal': {'weight': 0.22, 'priority': 'medium'},
            'support_resistance': {'weight': 0.15, 'priority': 'medium'}
        }
        
        # Confidence Scoring System
        self.confidence_thresholds = {
            'very_strong': 85,  # > 85%
            'strong': 70,       # 70-85%
            'moderate': 55,     # 55-70%
            'weak': 40,         # 40-55%
            'very_weak': 25     # < 40%
        }
        
        # Rolling Window Settings
        self.rolling_windows = {
            'rsi_window': 3,        # 3 candles untuk RSI trend
            'macd_window': 3,       # 3 candles untuk MACD momentum
            'volume_window': 5,     # 5 candles untuk volume analysis
            'price_window': 5       # 5 candles untuk price action
        }
        
        logger.info("🧠 Enhanced Signal Logic initialized with Weight Matrix & Scoring System")
    
    def analyze_signal_with_reasoning(self, df: pd.DataFrame, symbol: str, 
                                    technical_data: Dict, smc_data: Dict) -> Dict[str, Any]:
        """
        Analyze signal dengan transparent reasoning dan scoring
        """
        try:
            logger.info(f"🔍 Analyzing signal with enhanced logic for {symbol}")
            
            # 1. Calculate Individual Component Scores
            component_scores = self._calculate_component_scores(df, technical_data, smc_data)
            
            # 2. Apply Weight Matrix
            weighted_scores = self._apply_weight_matrix(component_scores)
            
            # 3. Calculate Final Confidence dengan Rolling Window Analysis
            final_confidence, confidence_breakdown = self._calculate_final_confidence(
                weighted_scores, df
            )
            
            # 4. Generate Signal Direction
            signal_direction = self._determine_signal_direction(weighted_scores, final_confidence)
            
            # 5. Generate Transparent Reasoning
            reasoning = self._generate_transparent_reasoning(
                component_scores, weighted_scores, final_confidence, signal_direction
            )
            
            # 6. SMC Priority Boost (untuk high confidence signals)
            if final_confidence >= 70:
                smc_boost = self._apply_smc_priority_boost(smc_data, weighted_scores)
                final_confidence = min(95, final_confidence + smc_boost)
                reasoning['smc_priority_boost'] = smc_boost
            
            result = {
                'signal': signal_direction,
                'confidence': round(final_confidence, 1),
                'confidence_level': self._get_confidence_level(final_confidence),
                'component_scores': component_scores,
                'weighted_scores': weighted_scores,
                'confidence_breakdown': confidence_breakdown,
                'reasoning': reasoning,
                'transparency_score': 100,  # Full transparency dengan detailed breakdown
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"✅ Enhanced signal analysis completed: {signal_direction} with {final_confidence}% confidence")
            return result
            
        except Exception as e:
            logger.error(f"Enhanced signal analysis error: {e}")
            return {
                'signal': 'NEUTRAL',
                'confidence': 0,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _calculate_component_scores(self, df: pd.DataFrame, technical_data: Dict, 
                                  smc_data: Dict) -> Dict[str, float]:
        """Calculate scores untuk setiap komponen dengan rolling window"""
        scores = {}
        
        # Technical Indicators dengan Rolling Window
        scores.update(self._score_technical_indicators(df, technical_data))
        
        # SMC Analysis Scores
        scores.update(self._score_smc_analysis(smc_data))
        
        # Price Action Scores
        scores.update(self._score_price_action(df))
        
        return scores
    
    def _score_technical_indicators(self, df: pd.DataFrame, technical_data: Dict) -> Dict[str, float]:
        """Score technical indicators dengan rolling window analysis"""
        scores = {}
        
        # RSI Analysis dengan 3-candle rolling window
        rsi_values = self._calculate_rolling_rsi(df, window=self.rolling_windows['rsi_window'])
        if rsi_values:
            current_rsi = rsi_values[-1]
            rsi_trend = self._calculate_trend(rsi_values)
            
            if current_rsi < 30:
                # RSI Oversold - berikan score tinggi untuk BUY
                scores['rsi_oversold'] = min(90, 70 + (30 - current_rsi) * 2)
                if rsi_trend > 0:  # RSI trending up dari oversold
                    scores['rsi_oversold'] += 10
            elif current_rsi > 70:
                # RSI Overbought - berikan score tinggi untuk SELL
                scores['rsi_overbought'] = min(90, 70 + (current_rsi - 70) * 2)
                if rsi_trend < 0:  # RSI trending down dari overbought
                    scores['rsi_overbought'] += 10
            else:
                scores['rsi_oversold'] = 0
                scores['rsi_overbought'] = 0
        
        # MACD Analysis dengan rolling window
        macd_data = self._calculate_rolling_macd(df, window=self.rolling_windows['macd_window'])
        if macd_data:
            macd_line = macd_data['macd']
            signal_line = macd_data['signal']
            histogram = macd_data['histogram']
            
            # MACD Bullish Cross
            if len(macd_line) >= 2 and macd_line[-1] > signal_line[-1] and macd_line[-2] <= signal_line[-2]:
                scores['macd_bullish_cross'] = 85
            else:
                scores['macd_bullish_cross'] = 0
            
            # MACD Bearish Cross
            if len(macd_line) >= 2 and macd_line[-1] < signal_line[-1] and macd_line[-2] >= signal_line[-2]:
                scores['macd_bearish_cross'] = 85
            else:
                scores['macd_bearish_cross'] = 0
            
            # MACD Histogram Momentum
            histogram_trend = self._calculate_trend(histogram[-3:])
            if histogram_trend > 0:
                scores['macd_histogram_momentum'] = min(80, 50 + histogram_trend * 30)
            elif histogram_trend < 0:
                scores['macd_histogram_momentum'] = max(-80, -50 + histogram_trend * 30)
            else:
                scores['macd_histogram_momentum'] = 0
        
        # Volume Confirmation dengan rolling window
        volume_data = self._analyze_volume_confirmation(df, window=self.rolling_windows['volume_window'])
        scores['volume_confirmation'] = volume_data.get('score', 0)
        
        # EMA Alignment
        ema_alignment = self._analyze_ema_alignment(df)
        scores['ema_alignment'] = ema_alignment.get('score', 0)
        
        return scores
    
    def _score_smc_analysis(self, smc_data: Dict) -> Dict[str, float]:
        """Score SMC analysis dengan prioritas tinggi"""
        scores = {}
        
        # Break of Structure (BOS) - Critical Priority
        if smc_data.get('break_of_structure'):
            if smc_data.get('trend') == 'BULLISH':
                scores['bos_bullish'] = 90  # Very high score
            elif smc_data.get('trend') == 'BEARISH':
                scores['bos_bearish'] = 90
        else:
            scores['bos_bullish'] = 0
            scores['bos_bearish'] = 0
        
        # Change of Character (CHoCH) - Critical Priority
        if smc_data.get('change_of_character'):
            if smc_data.get('trend') == 'BULLISH':
                scores['choch_bullish'] = 85
            elif smc_data.get('trend') == 'BEARISH':
                scores['choch_bearish'] = 85
        else:
            scores['choch_bullish'] = 0
            scores['choch_bearish'] = 0
        
        # Order Blocks
        order_blocks = smc_data.get('order_blocks', {})
        scores['order_block_bullish'] = len(order_blocks.get('bullish', [])) * 20
        scores['order_block_bearish'] = len(order_blocks.get('bearish', [])) * 20
        
        # Fair Value Gaps
        fvg_data = smc_data.get('fair_value_gaps', [])
        bullish_fvg = sum(1 for fvg in fvg_data if 'bullish' in str(fvg.get('type', '')).lower())
        bearish_fvg = sum(1 for fvg in fvg_data if 'bearish' in str(fvg.get('type', '')).lower())
        
        scores['fvg_bullish'] = bullish_fvg * 25
        scores['fvg_bearish'] = bearish_fvg * 25
        
        # Liquidity Sweep
        liquidity_sweep = smc_data.get('liquidity_sweep', {})
        if liquidity_sweep.get('detected'):
            scores['liquidity_sweep'] = 60
        else:
            scores['liquidity_sweep'] = 0
        
        return scores
    
    def _score_price_action(self, df: pd.DataFrame) -> Dict[str, float]:
        """Score price action dengan rolling window"""
        scores = {}
        
        # Trend Analysis
        price_trend = self._analyze_price_trend(df, window=self.rolling_windows['price_window'])
        scores['trend_continuation'] = price_trend.get('continuation_score', 0)
        scores['trend_reversal'] = price_trend.get('reversal_score', 0)
        
        # Support/Resistance
        sr_analysis = self._analyze_support_resistance(df)
        scores['support_resistance'] = sr_analysis.get('score', 0)
        
        return scores
    
    def _apply_weight_matrix(self, component_scores: Dict[str, float]) -> Dict[str, float]:
        """Apply weight matrix untuk setiap komponen"""
        weighted_scores = {}
        
        for component, score in component_scores.items():
            if component in self.weight_matrix:
                weight = self.weight_matrix[component]['weight']
                weighted_scores[component] = score * weight
            else:
                weighted_scores[component] = score * 0.1  # Default weight
        
        return weighted_scores
    
    def _calculate_final_confidence(self, weighted_scores: Dict[str, float], 
                                  df: pd.DataFrame) -> Tuple[float, Dict[str, Any]]:
        """Calculate final confidence dengan breakdown"""
        
        # Separate bullish and bearish signals
        bullish_signals = [
            'rsi_oversold', 'macd_bullish_cross', 'bos_bullish', 'choch_bullish',
            'order_block_bullish', 'fvg_bullish', 'trend_continuation'
        ]
        
        bearish_signals = [
            'rsi_overbought', 'macd_bearish_cross', 'bos_bearish', 'choch_bearish',
            'order_block_bearish', 'fvg_bearish', 'trend_reversal'
        ]
        
        bullish_score = sum(weighted_scores.get(signal, 0) for signal in bullish_signals)
        bearish_score = sum(abs(weighted_scores.get(signal, 0)) for signal in bearish_signals)
        
        # Add neutral/supporting signals
        neutral_boost = sum(weighted_scores.get(signal, 0) for signal in 
                          ['volume_confirmation', 'ema_alignment', 'support_resistance', 'liquidity_sweep'])
        
        # Calculate confidence
        total_bullish = bullish_score + (neutral_boost if bullish_score > bearish_score else 0)
        total_bearish = bearish_score + (neutral_boost if bearish_score > bullish_score else 0)
        
        final_confidence = max(total_bullish, total_bearish)
        
        # Apply rolling window momentum boost
        momentum_boost = self._calculate_momentum_boost(df)
        final_confidence += momentum_boost
        
        # Confidence breakdown for transparency
        breakdown = {
            'bullish_score': round(bullish_score, 2),
            'bearish_score': round(bearish_score, 2),
            'neutral_boost': round(neutral_boost, 2),
            'momentum_boost': round(momentum_boost, 2),
            'final_confidence': round(final_confidence, 2)
        }
        
        return min(95, max(0, final_confidence)), breakdown
    
    def _determine_signal_direction(self, weighted_scores: Dict[str, float], 
                                  confidence: float) -> str:
        """Determine signal direction berdasarkan weighted scores"""
        
        bullish_signals = [
            'rsi_oversold', 'macd_bullish_cross', 'bos_bullish', 'choch_bullish',
            'order_block_bullish', 'fvg_bullish'
        ]
        
        bearish_signals = [
            'rsi_overbought', 'macd_bearish_cross', 'bos_bearish', 'choch_bearish',
            'order_block_bearish', 'fvg_bearish'
        ]
        
        bullish_score = sum(weighted_scores.get(signal, 0) for signal in bullish_signals)
        bearish_score = sum(abs(weighted_scores.get(signal, 0)) for signal in bearish_signals)
        
        # Confidence threshold untuk signal generation
        min_confidence = 55
        
        if confidence < min_confidence:
            return 'NEUTRAL'
        elif bullish_score > bearish_score:
            if confidence >= 80:
                return 'STRONG_BUY'
            elif confidence >= 65:
                return 'BUY'
            else:
                return 'WEAK_BUY'
        elif bearish_score > bullish_score:
            if confidence >= 80:
                return 'STRONG_SELL'
            elif confidence >= 65:
                return 'SELL'
            else:
                return 'WEAK_SELL'
        else:
            return 'NEUTRAL'
    
    def _apply_smc_priority_boost(self, smc_data: Dict, weighted_scores: Dict[str, float]) -> float:
        """Apply SMC priority boost untuk high confidence signals"""
        boost = 0
        
        # BOS/CHoCH detected - Major boost
        if smc_data.get('break_of_structure') or smc_data.get('change_of_character'):
            boost += 10
        
        # Order Block confluence
        order_blocks = smc_data.get('order_blocks', {})
        if len(order_blocks.get('bullish', [])) > 0 or len(order_blocks.get('bearish', [])) > 0:
            boost += 5
        
        # FVG confluence
        fvg_data = smc_data.get('fair_value_gaps', [])
        if len(fvg_data) > 0:
            boost += 3
        
        return boost
    
    def _generate_transparent_reasoning(self, component_scores: Dict, weighted_scores: Dict,
                                      confidence: float, signal_direction: str) -> Dict[str, Any]:
        """Generate transparent reasoning untuk signal decision"""
        
        reasoning = {
            'decision_factors': [],
            'supporting_evidence': [],
            'conflicting_signals': [],
            'confidence_explanation': '',
            'risk_factors': []
        }
        
        # Identify key decision factors
        significant_factors = {k: v for k, v in weighted_scores.items() if abs(v) > 5}
        reasoning['decision_factors'] = [
            f"{factor}: {score:.1f}" for factor, score in significant_factors.items()
        ]
        
        # Supporting evidence
        if signal_direction in ['BUY', 'STRONG_BUY', 'WEAK_BUY']:
            bullish_factors = [k for k, v in weighted_scores.items() 
                             if v > 5 and ('bullish' in k or 'oversold' in k)]
            reasoning['supporting_evidence'] = bullish_factors
        elif signal_direction in ['SELL', 'STRONG_SELL', 'WEAK_SELL']:
            bearish_factors = [k for k, v in weighted_scores.items() 
                             if v > 5 and ('bearish' in k or 'overbought' in k)]
            reasoning['supporting_evidence'] = bearish_factors
        
        # Conflicting signals
        if signal_direction.startswith('BUY'):
            conflicts = [k for k, v in weighted_scores.items() 
                        if v > 3 and ('bearish' in k or 'overbought' in k)]
        elif signal_direction.startswith('SELL'):
            conflicts = [k for k, v in weighted_scores.items() 
                        if v > 3 and ('bullish' in k or 'oversold' in k)]
        else:
            conflicts = []
        
        reasoning['conflicting_signals'] = conflicts
        
        # Confidence explanation
        confidence_level = self._get_confidence_level(confidence)
        reasoning['confidence_explanation'] = f"Confidence level: {confidence_level} ({confidence:.1f}%) based on weighted analysis of {len(significant_factors)} key factors"
        
        # Risk factors
        risk_factors = []
        if len(conflicts) > 0:
            risk_factors.append(f"Conflicting signals detected: {len(conflicts)} factors")
        if confidence < 70:
            risk_factors.append("Moderate confidence - monitor closely")
        if signal_direction == 'NEUTRAL':
            risk_factors.append("No clear directional bias - wait for better setup")
        
        reasoning['risk_factors'] = risk_factors
        
        return reasoning
    
    def _get_confidence_level(self, confidence: float) -> str:
        """Get confidence level string"""
        if confidence >= self.confidence_thresholds['very_strong']:
            return 'VERY_STRONG'
        elif confidence >= self.confidence_thresholds['strong']:
            return 'STRONG'
        elif confidence >= self.confidence_thresholds['moderate']:
            return 'MODERATE'
        elif confidence >= self.confidence_thresholds['weak']:
            return 'WEAK'
        else:
            return 'VERY_WEAK'
    
    # Helper Methods untuk Rolling Window Analysis
    def _calculate_rolling_rsi(self, df: pd.DataFrame, window: int = 3) -> List[float]:
        """Calculate RSI dengan rolling window"""
        try:
            closes = df['close'].values[-20:]  # Last 20 values untuk RSI calculation
            if len(closes) < 14:
                return []
            
            rsi_values = []
            for i in range(14, len(closes)):
                prices = closes[max(0, i-14):i+1]
                rsi = self._calculate_single_rsi(prices)
                rsi_values.append(rsi)
            
            return rsi_values[-window:] if len(rsi_values) >= window else rsi_values
        except:
            return []
    
    def _calculate_single_rsi(self, prices: List[float], period: int = 14) -> float:
        """Calculate single RSI value"""
        if len(prices) < period + 1:
            return 50.0
        
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        gains = [d if d > 0 else 0 for d in deltas]
        losses = [-d if d < 0 else 0 for d in deltas]
        
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def _calculate_rolling_macd(self, df: pd.DataFrame, window: int = 3) -> Dict[str, List[float]]:
        """Calculate MACD dengan rolling window"""
        try:
            closes = df['close'].values[-50:]  # Last 50 values
            if len(closes) < 26:
                return {}
            
            # Calculate EMA
            ema_12 = self._calculate_ema_series(closes, 12)
            ema_26 = self._calculate_ema_series(closes, 26)
            
            # MACD Line
            macd_line = [ema_12[i] - ema_26[i] for i in range(len(ema_26))]
            
            # Signal Line (EMA of MACD)
            signal_line = self._calculate_ema_series(macd_line, 9)
            
            # Histogram
            histogram = [macd_line[i] - signal_line[i] for i in range(len(signal_line))]
            
            return {
                'macd': macd_line[-window:],
                'signal': signal_line[-window:],
                'histogram': histogram[-window:]
            }
        except:
            return {}
    
    def _calculate_ema_series(self, prices: List[float], period: int) -> List[float]:
        """Calculate EMA series"""
        if len(prices) < period:
            return []
        
        ema_values = []
        multiplier = 2 / (period + 1)
        
        # Start with SMA
        sma = np.mean(prices[:period])
        ema_values.append(sma)
        
        # Calculate EMA
        for i in range(period, len(prices)):
            ema = (prices[i] * multiplier) + (ema_values[-1] * (1 - multiplier))
            ema_values.append(ema)
        
        return ema_values
    
    def _calculate_trend(self, values: List[float]) -> float:
        """Calculate trend dari series of values"""
        if len(values) < 2:
            return 0
        
        # Simple linear regression slope
        x = list(range(len(values)))
        n = len(values)
        
        sum_x = sum(x)
        sum_y = sum(values)
        sum_xy = sum(x[i] * values[i] for i in range(n))
        sum_x2 = sum(x[i] ** 2 for i in range(n))
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
        return slope
    
    def _analyze_volume_confirmation(self, df: pd.DataFrame, window: int = 5) -> Dict[str, Any]:
        """Analyze volume confirmation dengan rolling window"""
        try:
            volumes = df['volume'].values[-window:]
            closes = df['close'].values[-window:]
            
            if len(volumes) < window or len(closes) < window:
                return {'score': 0}
            
            # Volume trend
            volume_trend = self._calculate_trend(volumes)
            price_trend = self._calculate_trend(closes)
            
            # Volume confirmation score
            if volume_trend > 0 and price_trend > 0:  # Volume up, Price up
                score = 70
            elif volume_trend > 0 and price_trend < 0:  # Volume up, Price down
                score = 60
            elif volume_trend < 0:  # Low volume
                score = 20
            else:
                score = 40
            
            return {
                'score': score,
                'volume_trend': volume_trend,
                'price_trend': price_trend
            }
        except:
            return {'score': 0}
    
    def _analyze_ema_alignment(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze EMA alignment"""
        try:
            closes = df['close'].values[-50:]
            if len(closes) < 50:
                return {'score': 0}
            
            # Calculate EMAs
            ema_9 = self._calculate_ema_series(closes, 9)[-1]
            ema_21 = self._calculate_ema_series(closes, 21)[-1]
            ema_50 = self._calculate_ema_series(closes, 50)[-1]
            current_price = closes[-1]
            
            # Bullish alignment: Price > EMA9 > EMA21 > EMA50
            if current_price > ema_9 > ema_21 > ema_50:
                score = 80
            # Bearish alignment: Price < EMA9 < EMA21 < EMA50
            elif current_price < ema_9 < ema_21 < ema_50:
                score = -80
            else:
                score = 0
            
            return {
                'score': score,
                'ema_9': ema_9,
                'ema_21': ema_21,
                'ema_50': ema_50
            }
        except:
            return {'score': 0}
    
    def _analyze_price_trend(self, df: pd.DataFrame, window: int = 5) -> Dict[str, Any]:
        """Analyze price trend dengan rolling window"""
        try:
            closes = df['close'].values[-window:]
            highs = df['high'].values[-window:]
            lows = df['low'].values[-window:]
            
            if len(closes) < window:
                return {'continuation_score': 0, 'reversal_score': 0}
            
            # Trend continuation
            price_trend = self._calculate_trend(closes)
            if abs(price_trend) > 0.5:
                continuation_score = min(70, abs(price_trend) * 100)
            else:
                continuation_score = 0
            
            # Trend reversal signals
            recent_high = max(highs)
            recent_low = min(lows)
            current_price = closes[-1]
            
            # Simple reversal detection
            if current_price > recent_high * 0.99:  # Near recent high
                reversal_score = 60 if price_trend < 0 else 0
            elif current_price < recent_low * 1.01:  # Near recent low
                reversal_score = 60 if price_trend > 0 else 0
            else:
                reversal_score = 0
            
            return {
                'continuation_score': continuation_score,
                'reversal_score': reversal_score,
                'price_trend': price_trend
            }
        except:
            return {'continuation_score': 0, 'reversal_score': 0}
    
    def _analyze_support_resistance(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze support/resistance levels"""
        try:
            closes = df['close'].values[-20:]
            highs = df['high'].values[-20:]
            lows = df['low'].values[-20:]
            
            if len(closes) < 20:
                return {'score': 0}
            
            current_price = closes[-1]
            
            # Find recent support/resistance levels
            resistance_levels = [h for h in highs if h > current_price * 1.001]
            support_levels = [l for l in lows if l < current_price * 0.999]
            
            # Score based on proximity to key levels
            if resistance_levels:
                nearest_resistance = min(resistance_levels)
                resistance_distance = (nearest_resistance - current_price) / current_price
                if resistance_distance < 0.005:  # Within 0.5%
                    score = -60  # Bearish at resistance
                else:
                    score = 0
            elif support_levels:
                nearest_support = max(support_levels)
                support_distance = (current_price - nearest_support) / current_price
                if support_distance < 0.005:  # Within 0.5%
                    score = 60  # Bullish at support
                else:
                    score = 0
            else:
                score = 0
            
            return {'score': score}
        except:
            return {'score': 0}
    
    def _calculate_momentum_boost(self, df: pd.DataFrame) -> float:
        """Calculate momentum boost dari rolling analysis"""
        try:
            closes = df['close'].values[-10:]
            volumes = df['volume'].values[-10:]
            
            if len(closes) < 10:
                return 0
            
            # Price momentum
            price_momentum = self._calculate_trend(closes[-5:])
            
            # Volume momentum
            volume_momentum = self._calculate_trend(volumes[-5:])
            
            # Combined momentum boost
            if price_momentum > 0 and volume_momentum > 0:
                boost = min(15, abs(price_momentum) * 10 + abs(volume_momentum) * 5)
            elif price_momentum < 0 and volume_momentum > 0:
                boost = min(10, abs(volume_momentum) * 8)
            else:
                boost = 0
            
            return boost
        except:
            return 0

# Global instance
enhanced_signal_logic = EnhancedSignalLogic()