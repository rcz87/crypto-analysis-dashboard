"""
Enhanced Technical analysis engine for cryptocurrency trading
Integrated with Professional SMC Analysis
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, Optional, List
import ta
from .professional_smc_analyzer import ProfessionalSMCAnalyzer
from .enhanced_ai_engine import EnhancedAIEngine

logger = logging.getLogger(__name__)

class TechnicalAnalyzer:
    """Enhanced technical analysis engine with SMC integration"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.smc_analyzer = ProfessionalSMCAnalyzer()
        self.enhanced_ai = EnhancedAIEngine()
        self.symbols = ['BTC-USDT', 'ETH-USDT', 'SOL-USDT', 'TIA-USDT', 'RENDER-USDT']
        
    def analyze(self, df: pd.DataFrame, symbol: str, timeframe: str) -> Dict[str, Any]:
        """Perform comprehensive technical analysis with professional SMC integration"""
        
        try:
            if df is None or df.empty:
                return self._empty_analysis()
            
            # Calculate traditional indicators
            indicators = self._calculate_indicators(df)
            
            # Generate traditional signals
            signals = self._generate_signals(df, indicators)
            
            # Professional SMC Analysis
            smc_analysis = self.smc_analyzer.analyze_comprehensive(df, symbol, timeframe)
            
            # Create enhanced analysis summary
            analysis = {
                'symbol': symbol,
                'timeframe': timeframe,
                'timestamp': df['timestamp'].iloc[-1].replace(microsecond=0).isoformat() if 'timestamp' in df.columns and hasattr(df['timestamp'].iloc[-1], 'isoformat') else datetime.now().replace(microsecond=0).isoformat(),
                'current_price': float(df['close'].iloc[-1]),
                'price_change_24h': self._calculate_price_change(df),
                'indicators': indicators,
                'signals': signals,
                'trend': self._determine_trend(df, indicators),
                'volume_status': self._analyze_volume(df),
                'summary': self._create_summary(indicators, signals),
                # Professional SMC Analysis Integration
                'smc_analysis': smc_analysis,
                'professional_signals': self._merge_signals(signals, smc_analysis.get('trading_signals', [])),
                'confidence_score': self._calculate_enhanced_confidence(signals, smc_analysis),
                'market_structure': smc_analysis.get('market_structure', {'trend': 'neutral', 'strength': 0})
            }
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Enhanced analysis error for {symbol}: {e}")
            return self._empty_analysis()
    
    def _calculate_indicators(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate technical indicators"""
        
        indicators = {}
        
        try:
            # RSI
            rsi = ta.momentum.RSIIndicator(df['close'], window=14).rsi()
            indicators['rsi'] = {
                'value': float(rsi.iloc[-1]) if not rsi.empty else 50.0,
                'overbought': bool(rsi.iloc[-1] > 70) if not rsi.empty else False,
                'oversold': bool(rsi.iloc[-1] < 30) if not rsi.empty else False
            }
            
            # Moving Averages
            ema_20 = ta.trend.EMAIndicator(df['close'], window=20).ema_indicator()
            ema_50 = ta.trend.EMAIndicator(df['close'], window=50).ema_indicator()
            
            indicators['ema'] = {
                'ema_20': float(ema_20.iloc[-1]) if not ema_20.empty else float(df['close'].iloc[-1]),
                'ema_50': float(ema_50.iloc[-1]) if not ema_50.empty else float(df['close'].iloc[-1]),
                'trend': 'bullish' if ema_20.iloc[-1] > ema_50.iloc[-1] else 'bearish'
            }
            
            # MACD
            macd_indicator = ta.trend.MACD(df['close'])
            macd_line = macd_indicator.macd()
            macd_signal = macd_indicator.macd_signal()
            macd_histogram = macd_indicator.macd_diff()
            
            if not macd_line.empty and not macd_signal.empty:
                indicators['macd'] = {
                    'macd': float(macd_line.iloc[-1]),
                    'signal': float(macd_signal.iloc[-1]),
                    'histogram': float(macd_histogram.iloc[-1]),
                    'bullish': bool(macd_line.iloc[-1] > macd_signal.iloc[-1])
                }
            
            # Bollinger Bands
            bb_indicator = ta.volatility.BollingerBands(df['close'])
            bb_upper = bb_indicator.bollinger_hband()
            bb_middle = bb_indicator.bollinger_mavg()
            bb_lower = bb_indicator.bollinger_lband()
            
            if not bb_upper.empty and not bb_middle.empty and not bb_lower.empty:
                indicators['bollinger'] = {
                    'upper': float(bb_upper.iloc[-1]),
                    'middle': float(bb_middle.iloc[-1]),
                    'lower': float(bb_lower.iloc[-1]),
                    'squeeze': bool(abs(bb_upper.iloc[-1] - bb_lower.iloc[-1]) < (bb_middle.iloc[-1] * 0.1))
                }
            
            # Volume indicators
            volume_sma = ta.trend.SMAIndicator(df['volume'], window=20).sma_indicator()
            indicators['volume'] = {
                'current': float(df['volume'].iloc[-1]),
                'average': float(volume_sma.iloc[-1]) if not volume_sma.empty else float(df['volume'].iloc[-1]),
                'above_average': bool(df['volume'].iloc[-1] > volume_sma.iloc[-1]) if not volume_sma.empty else False
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating indicators: {e}")
            indicators = self._default_indicators()
        
        return indicators
    
    def _generate_signals(self, df: pd.DataFrame, indicators: Dict[str, Any]) -> Dict[str, Any]:
        """Generate trading signals based on indicators"""
        
        signals = {
            'action': 'HOLD',
            'confidence': 0.0,
            'reason': [],
            'entry_price': None,
            'stop_loss': None,
            'take_profit': None
        }
        
        try:
            current_price = df['close'].iloc[-1]
            confidence_score = 0
            reasons = []
            
            # RSI signals
            if indicators.get('rsi', {}).get('oversold', False):
                confidence_score += 0.3
                reasons.append("RSI oversold")
            elif indicators.get('rsi', {}).get('overbought', False):
                confidence_score -= 0.3
                reasons.append("RSI overbought")
            
            # EMA trend
            if indicators.get('ema', {}).get('trend') == 'bullish':
                confidence_score += 0.2
                reasons.append("EMA bullish trend")
            elif indicators.get('ema', {}).get('trend') == 'bearish':
                confidence_score -= 0.2
                reasons.append("EMA bearish trend")
            
            # MACD signals
            if indicators.get('macd', {}).get('bullish', False):
                confidence_score += 0.25
                reasons.append("MACD bullish crossover")
            else:
                confidence_score -= 0.25
                reasons.append("MACD bearish")
            
            # Volume confirmation
            if indicators.get('volume', {}).get('above_average', False):
                confidence_score += 0.15
                reasons.append("Volume above average")
            
            # Determine action
            if confidence_score > 0.5:
                signals['action'] = 'BUY'
                signals['entry_price'] = current_price
                signals['stop_loss'] = current_price * 0.95  # 5% stop loss
                signals['take_profit'] = current_price * 1.10  # 10% take profit
            elif confidence_score < -0.5:
                signals['action'] = 'SELL'
                signals['entry_price'] = current_price
                signals['stop_loss'] = current_price * 1.05  # 5% stop loss
                signals['take_profit'] = current_price * 0.90  # 10% take profit
            
            signals['confidence'] = min(abs(confidence_score), 1.0)
            signals['reason'] = reasons
            
        except Exception as e:
            self.logger.error(f"Error generating signals: {e}")
        
        return signals
    
    def _determine_trend(self, df: pd.DataFrame, indicators: Dict[str, Any]) -> str:
        """Determine overall trend"""
        
        try:
            ema_trend = indicators.get('ema', {}).get('trend', 'neutral')
            macd_bullish = indicators.get('macd', {}).get('bullish', False)
            
            if ema_trend == 'bullish' and macd_bullish:
                return 'BULLISH'
            elif ema_trend == 'bearish' and not macd_bullish:
                return 'BEARISH'
            else:
                return 'NEUTRAL'
                
        except Exception:
            return 'NEUTRAL'
    
    def _analyze_volume(self, df: pd.DataFrame) -> str:
        """Analyze volume patterns"""
        
        try:
            recent_volume = df['volume'].tail(5).mean()
            older_volume = df['volume'].tail(20).mean()
            
            if recent_volume > older_volume * 1.2:
                return 'INCREASING'
            elif recent_volume < older_volume * 0.8:
                return 'DECREASING'
            else:
                return 'STABLE'
                
        except Exception:
            return 'STABLE'
    
    def _calculate_price_change(self, df: pd.DataFrame) -> float:
        """Calculate 24h price change percentage"""
        
        try:
            if len(df) >= 24:
                old_price = df['close'].iloc[-24]
                current_price = df['close'].iloc[-1]
                return ((current_price - old_price) / old_price) * 100
            else:
                return 0.0
        except Exception:
            return 0.0
    
    def _create_summary(self, indicators: Dict[str, Any], signals: Dict[str, Any]) -> str:
        """Create analysis summary"""
        
        try:
            action = signals.get('action', 'HOLD')
            confidence = signals.get('confidence', 0) * 100
            trend = indicators.get('ema', {}).get('trend', 'neutral')
            rsi = indicators.get('rsi', {}).get('value', 50)
            
            return f"Signal: {action} (Confidence: {confidence:.0f}%) | Trend: {trend} | RSI: {rsi:.1f}"
            
        except Exception:
            return "Analysis unavailable"
    
    def _empty_analysis(self) -> Dict[str, Any]:
        """Return empty analysis structure with SMC integration"""
        
        return {
            'symbol': '',
            'timeframe': '',
            'timestamp': None,
            'current_price': 0.0,
            'price_change_24h': 0.0,
            'indicators': self._default_indicators(),
            'signals': {
                'action': 'HOLD',
                'confidence': 0.0,
                'reason': [],
                'entry_price': None,
                'stop_loss': None,
                'take_profit': None
            },
            'trend': 'NEUTRAL',
            'volume_status': 'STABLE',
            'summary': 'No data available',
            # Enhanced SMC Analysis fields
            'smc_analysis': {
                'swing_points': {'swing_highs': [], 'swing_lows': []},
                'choch_bos_signals': [],
                'order_blocks': [],
                'fvg_signals': [],
                'liquidity_sweeps': [],
                'eqh_eql_signals': [],
                'market_structure': {'trend': 'neutral', 'strength': 0},
                'smc_summary': {
                    'total_choch_bos': 0,
                    'total_order_blocks': 0,
                    'total_fvg': 0,
                    'total_liquidity_sweeps': 0,
                    'total_eqh_eql': 0,
                    'bullish_signals': 0,
                    'bearish_signals': 0,
                    'recent_activity': 0,
                    'pattern_diversity': 0
                },
                'trading_signals': [],
                'confidence_score': 0.0
            },
            'professional_signals': [],
            'confidence_score': 0.0,
            'market_structure': {'trend': 'neutral', 'strength': 0}
        }
    
    def _default_indicators(self) -> Dict[str, Any]:
        """Return default indicators"""
        
        return {
            'rsi': {'value': 50, 'overbought': False, 'oversold': False},
            'ema': {'ema_20': 0, 'ema_50': 0, 'trend': 'neutral'},
            'macd': {'macd': 0, 'signal': 0, 'histogram': 0, 'bullish': False},
            'bollinger': {'upper': 0, 'middle': 0, 'lower': 0, 'squeeze': False},
            'volume': {'current': 0, 'average': 0, 'above_average': False}
        }
    
    def get_indicator_summary(self, indicators: Dict[str, Any]) -> Dict[str, Any]:
        """Get simplified indicator summary for UI"""
        
        return {
            'rsi': indicators.get('rsi', {}).get('value', 50),
            'trend': indicators.get('ema', {}).get('trend', 'neutral'),
            'macd_bullish': indicators.get('macd', {}).get('bullish', False),
            'volume_above_avg': indicators.get('volume', {}).get('above_average', False)
        }
    
    def _merge_signals(self, traditional_signals: Dict[str, Any], smc_signals: List[Dict]) -> List[Dict]:
        """Merge traditional and SMC signals for enhanced trading signals"""
        
        merged_signals = []
        
        try:
            # Add traditional signals
            if traditional_signals.get('buy_signal'):
                merged_signals.append({
                    'type': 'traditional',
                    'action': 'BUY',
                    'reason': 'Traditional technical indicators',
                    'confidence': 60,
                    'source': 'indicators'
                })
            
            if traditional_signals.get('sell_signal'):
                merged_signals.append({
                    'type': 'traditional',
                    'action': 'SELL',
                    'reason': 'Traditional technical indicators',
                    'confidence': 60,
                    'source': 'indicators'
                })
            
            # Add SMC signals with higher priority
            for smc_signal in smc_signals:
                merged_signals.append({
                    'type': 'smc',
                    'action': smc_signal.get('action', 'HOLD'),
                    'reason': f"SMC {smc_signal.get('pattern_type', 'pattern')} detected",
                    'confidence': smc_signal.get('confidence', 70),
                    'source': 'smc_analysis',
                    'entry_price': smc_signal.get('entry_price'),
                    'supporting_patterns': smc_signal.get('supporting_patterns', [])
                })
            
            # Sort by confidence (highest first)
            merged_signals.sort(key=lambda x: x.get('confidence', 0), reverse=True)
            
        except Exception as e:
            self.logger.error(f"Error merging signals: {e}")
            
        return merged_signals
    
    def generate_enhanced_ai_narrative(self, analysis_data: Dict[str, Any], 
                                     language: str = "indonesian", 
                                     quick_mode: bool = False) -> str:
        """Generate enhanced AI narrative using advanced AI engine"""
        
        try:
            symbol = analysis_data.get('symbol', 'UNKNOWN')
            narrative = self.enhanced_ai.generate_enhanced_analysis(
                symbol=symbol,
                analysis_data=analysis_data,
                language=language,
                quick_mode=quick_mode
            )
            
            return narrative
            
        except Exception as e:
            self.logger.error(f"Error generating enhanced AI narrative: {e}")
            return f"Enhanced AI narrative generation failed: {str(e)}"
    
    def get_enhanced_ai_stats(self) -> Dict[str, Any]:
        """Get enhanced AI engine statistics"""
        return self.enhanced_ai.get_usage_stats()
    
    def test_enhanced_ai_connection(self) -> Dict[str, Any]:
        """Test enhanced AI connection"""
        return self.enhanced_ai.test_ai_connection()
    
    def _calculate_enhanced_confidence(self, traditional_signals: Dict[str, Any], smc_analysis: Dict[str, Any]) -> float:
        """Calculate enhanced confidence score combining traditional and SMC analysis"""
        
        try:
            # Base confidence from traditional analysis
            base_confidence = 50
            
            # Traditional signals boost
            if traditional_signals.get('buy_signal') or traditional_signals.get('sell_signal'):
                base_confidence += 15
            
            # SMC analysis boost
            smc_confidence = smc_analysis.get('confidence_score', 0)
            smc_boost = smc_confidence * 0.4  # 40% weight for SMC
            
            # Market structure boost
            market_structure = smc_analysis.get('market_structure', {})
            structure_strength = market_structure.get('strength', 0)
            structure_boost = structure_strength * 0.2  # 20% weight for market structure
            
            # Pattern diversity boost
            smc_summary = smc_analysis.get('smc_summary', {})
            pattern_diversity = smc_summary.get('pattern_diversity', 0)
            diversity_boost = pattern_diversity * 2  # Each pattern type adds 2 points
            
            # Signal confluence boost
            traditional_signal_count = sum(1 for key in ['buy_signal', 'sell_signal'] if traditional_signals.get(key))
            smc_signal_count = len(smc_analysis.get('trading_signals', []))
            if traditional_signal_count > 0 and smc_signal_count > 0:
                confluence_boost = 10  # Bonus for signal confluence
            else:
                confluence_boost = 0
            
            # Calculate total confidence
            total_confidence = base_confidence + smc_boost + structure_boost + diversity_boost + confluence_boost
            
            # Cap at 100
            return min(total_confidence, 100)
            
        except Exception as e:
            self.logger.error(f"Error calculating enhanced confidence: {e}")
            return 50.0