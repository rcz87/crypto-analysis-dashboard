"""
Signal Generator - VPS Production Ready
Simplified signal generation for reliable deployment
"""

import logging
from typing import Dict, Any
import time

logger = logging.getLogger(__name__)

class SignalGenerator:
    """Professional signal generator optimized for VPS deployment"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.SignalGenerator")
        self.logger.info("Signal Generator initialized")
    
    def generate_signal(self, market_data: Dict[str, Any], smc_analysis: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate trading signal based on market data and SMC analysis
        
        Args:
            market_data: Market data from OKX
            smc_analysis: SMC analysis results
            
        Returns:
            Trading signal with entry, TP, SL
        """
        try:
            candles = market_data.get('candles', [])
            if not candles:
                return self._get_fallback_signal()
            
            current_candle = candles[-1]
            current_price = current_candle['close']
            
            # Simple signal generation logic
            signal = self._analyze_price_action(candles, smc_analysis)
            
            # Add risk management levels
            signal['entry_price'] = current_price
            signal['timestamp'] = int(time.time())
            signal['symbol'] = market_data.get('symbol', 'UNKNOWN')
            signal['timeframe'] = market_data.get('timeframe', '1H')
            
            # Calculate TP and SL based on direction
            if signal['direction'] == 'BUY':
                signal['take_profit'] = current_price * 1.02  # 2% TP
                signal['stop_loss'] = current_price * 0.985   # 1.5% SL
            else:
                signal['take_profit'] = current_price * 0.98  # 2% TP
                signal['stop_loss'] = current_price * 1.015   # 1.5% SL
            
            self.logger.info(f"Generated {signal['direction']} signal for {signal['symbol']}")
            return signal
            
        except Exception as e:
            self.logger.error(f"Signal generation error: {e}")
            return self._get_fallback_signal()
    
    def _analyze_price_action(self, candles: list, smc_analysis: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze price action to determine signal direction"""
        try:
            if len(candles) < 5:
                return {'direction': 'HOLD', 'confidence': 0.3, 'reasoning': 'Insufficient data'}
            
            # Get recent candles
            recent_candles = candles[-5:]
            current_candle = candles[-1]
            previous_candle = candles[-2]
            
            # Simple trend analysis
            closes = [c['close'] for c in recent_candles]
            highs = [c['high'] for c in recent_candles]
            lows = [c['low'] for c in recent_candles]
            
            # Calculate basic indicators
            trend_up = closes[-1] > closes[0]  # Price higher than 5 candles ago
            volume_increasing = current_candle['volume'] > previous_candle['volume']
            strong_candle = abs(current_candle['close'] - current_candle['open']) > (current_candle['high'] - current_candle['low']) * 0.7
            
            # Determine signal direction
            bullish_signals = 0
            bearish_signals = 0
            
            if trend_up:
                bullish_signals += 1
            else:
                bearish_signals += 1
            
            if volume_increasing:
                if current_candle['close'] > current_candle['open']:
                    bullish_signals += 1
                else:
                    bearish_signals += 1
            
            if strong_candle:
                if current_candle['close'] > current_candle['open']:
                    bullish_signals += 1
                else:
                    bearish_signals += 1
            
            # Include SMC bias if available
            if smc_analysis and 'market_bias' in smc_analysis:
                if smc_analysis['market_bias'] == 'bullish':
                    bullish_signals += 2
                elif smc_analysis['market_bias'] == 'bearish':
                    bearish_signals += 2
            
            # Determine final signal
            if bullish_signals > bearish_signals + 1:
                direction = 'BUY'
                confidence = min(bullish_signals / 5.0, 0.9)
                reasoning = f"Bullish signals: {bullish_signals}, trend up, volume confirmation"
            elif bearish_signals > bullish_signals + 1:
                direction = 'SELL'
                confidence = min(bearish_signals / 5.0, 0.9)
                reasoning = f"Bearish signals: {bearish_signals}, trend down, volume confirmation"
            else:
                direction = 'HOLD'
                confidence = 0.4
                reasoning = "Mixed signals, waiting for clearer direction"
            
            return {
                'direction': direction,
                'confidence': round(confidence, 2),
                'reasoning': reasoning,
                'bullish_signals': bullish_signals,
                'bearish_signals': bearish_signals
            }
            
        except Exception as e:
            self.logger.error(f"Price action analysis error: {e}")
            return {
                'direction': 'HOLD',
                'confidence': 0.3,
                'reasoning': f'Analysis error: {str(e)}'
            }
    
    def _get_fallback_signal(self) -> Dict[str, Any]:
        """Fallback signal when generation fails"""
        return {
            'direction': 'HOLD',
            'confidence': 0.2,
            'entry_price': 0.0,
            'take_profit': 0.0,
            'stop_loss': 0.0,
            'reasoning': 'Fallback signal - insufficient data or system error',
            'timestamp': int(time.time()),
            'symbol': 'UNKNOWN',
            'timeframe': '1H',
            'status': 'fallback'
        }