"""
Confluence checker for multi-indicator analysis
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class ConfluenceChecker:
    """Multi-indicator confluence analysis"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.weights = {
            'rsi': 0.25,
            'ema': 0.3,
            'macd': 0.25,
            'volume': 0.2
        }
    
    def check_confluence(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check confluence across multiple indicators"""
        
        try:
            indicators = analysis_data.get('indicators', {})
            
            # Calculate confluence score
            confluence_score = 0
            supporting_indicators = []
            
            # RSI confluence
            rsi_data = indicators.get('rsi', {})
            if rsi_data.get('oversold', False):
                confluence_score += self.weights['rsi']
                supporting_indicators.append('RSI oversold')
            elif rsi_data.get('overbought', False):
                confluence_score -= self.weights['rsi']
                supporting_indicators.append('RSI overbought')
            
            # EMA confluence
            ema_data = indicators.get('ema', {})
            if ema_data.get('trend') == 'bullish':
                confluence_score += self.weights['ema']
                supporting_indicators.append('EMA bullish')
            elif ema_data.get('trend') == 'bearish':
                confluence_score -= self.weights['ema']
                supporting_indicators.append('EMA bearish')
            
            # MACD confluence
            macd_data = indicators.get('macd', {})
            if macd_data.get('bullish', False):
                confluence_score += self.weights['macd']
                supporting_indicators.append('MACD bullish')
            else:
                confluence_score -= self.weights['macd']
                supporting_indicators.append('MACD bearish')
            
            # Volume confluence
            volume_data = indicators.get('volume', {})
            if volume_data.get('above_average', False):
                confluence_score += self.weights['volume']
                supporting_indicators.append('Volume confirmation')
            
            # Determine confluence level
            confluence_level = 'LOW'
            if abs(confluence_score) > 0.7:
                confluence_level = 'HIGH'
            elif abs(confluence_score) > 0.5:
                confluence_level = 'MEDIUM'
            
            return {
                'confluence_score': confluence_score,
                'confluence_level': confluence_level,
                'supporting_indicators': supporting_indicators,
                'signal_strength': min(abs(confluence_score), 1.0),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error checking confluence: {e}")
            return {
                'confluence_score': 0,
                'confluence_level': 'LOW',
                'supporting_indicators': [],
                'signal_strength': 0,
                'timestamp': datetime.now().isoformat()
            }
    
    def get_historical_performance(self) -> Dict[str, Any]:
        """Get historical performance statistics"""
        
        # Mock data for now - would be replaced with actual database queries
        return {
            'total_signals': 150,
            'win_rate': 68.5,
            'avg_confidence': 0.72,
            'best_timeframe': '1H',
            'most_accurate_pattern': 'EMA + RSI confluence'
        }