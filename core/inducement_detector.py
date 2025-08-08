"""
Advanced Inducement Detector for Smart Money Concept (SMC)
Detects sophisticated institutional manipulation patterns:
- False breakouts with immediate reversal
- Volume-confirmed inducements
- Wick-based trap detection
- Multiple failed attempts at key levels
- Time-based inducement patterns
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class InducementDetector:
    """Advanced Inducement Detection for institutional manipulation"""
    
    # Class constants for better maintainability
    MIN_DATA_LENGTH = 20
    LEVEL_PROXIMITY_THRESHOLD = 0.01  # 1% proximity to key levels
    MULTIPLE_ATTEMPT_LOWER_BOUND = 0.998  # 99.8% of key level
    MULTIPLE_ATTEMPT_UPPER_BOUND = 1.003  # 100.3% of key level
    MIN_ATTEMPTS_FOR_INDUCEMENT = 3
    
    def __init__(self, 
                 false_breakout_threshold: float = 0.005,  # 0.5% for false breakout
                 volume_spike_multiplier: float = 1.8,    # 1.8x volume for confirmation
                 reversal_candles: int = 3,               # Max candles for reversal
                 min_wick_ratio: float = 0.6,             # 60% wick-to-body ratio
                 multiple_attempt_window: int = 20):      # 20 candles for multiple attempts
        
        self.false_breakout_threshold = false_breakout_threshold
        self.volume_spike_multiplier = volume_spike_multiplier
        self.reversal_candles = reversal_candles
        self.min_wick_ratio = min_wick_ratio
        self.multiple_attempt_window = multiple_attempt_window
        self.logger = logging.getLogger(__name__)
    
    def detect_inducements(self, data: List[Dict], swing_points: Dict[str, List[Dict]]) -> List[Dict]:
        """Main method to detect all types of inducements"""
        
        try:
            if not data or len(data) < self.MIN_DATA_LENGTH:
                return []
            
            inducements = []
            
            # 1. False Breakout Inducements
            false_breakouts = self._detect_false_breakouts(data, swing_points)
            inducements.extend(false_breakouts)
            
            # 2. Volume-based Inducements
            volume_inducements = self._detect_volume_inducements(data, swing_points)
            inducements.extend(volume_inducements)
            
            # 3. Wick-based Trap Inducements
            wick_inducements = self._detect_wick_inducements(data, swing_points)
            inducements.extend(wick_inducements)
            
            # 4. Multiple Attempt Inducements
            multiple_attempts = self._detect_multiple_attempts(data, swing_points)
            inducements.extend(multiple_attempts)
            
            # 5. Time-based Inducements (Session open/close)
            time_inducements = self._detect_time_based_inducements(data, swing_points)
            inducements.extend(time_inducements)
            
            # Sort by timestamp and add confidence scores
            inducements.sort(key=lambda x: x['timestamp'])
            
            # Calculate final confidence scores
            for inducement in inducements:
                inducement['confidence_score'] = self._calculate_inducement_confidence(inducement, data)
            
            return inducements
            
        except Exception as e:
            self.logger.error(f"Error detecting inducements: {e}")
            return []
    
    def _detect_false_breakouts(self, data: List[Dict], swing_points: Dict[str, List[Dict]]) -> List[Dict]:
        """Detect false breakouts that reverse quickly"""
        
        false_breakouts = []
        
        if not swing_points:
            return false_breakouts
        
        # Check swing highs for false breakouts
        for swing_high in swing_points.get('swing_highs', []):
            idx = swing_high.get('index', 0)
            if idx >= len(data) - 5:
                continue
            
            # Look for false breakout above swing high
            for i in range(idx + 1, min(idx + 6, len(data))):
                current_candle = data[i]
                
                # Check if price breaks above swing high
                if current_candle['high'] > swing_high['price'] * (1 + self.false_breakout_threshold):
                    
                    # Check for quick reversal
                    reversal_found = False
                    for j in range(i + 1, min(i + self.reversal_candles + 1, len(data))):
                        if data[j]['close'] < swing_high['price']:
                            reversal_found = True
                            break
                    
                    if reversal_found:
                        false_breakouts.append({
                            'timestamp': int(current_candle['timestamp']) if isinstance(current_candle['timestamp'], (int, float)) else int(current_candle['timestamp'].timestamp() * 1000),
                            'type': 'false_breakout',
                            'direction': 'bearish_inducement',
                            'breakout_price': current_candle['high'],
                            'key_level': swing_high['price'],
                            'reversal_candles': j - i,
                            'strength': self._calculate_false_breakout_strength(current_candle, swing_high, data),
                            'description': f"False breakout above ${swing_high['price']:.2f}, reversed in {j-i} candles"
                        })
                        break
        
        # Check swing lows for false breakouts
        for swing_low in swing_points.get('swing_lows', []):
            idx = swing_low.get('index', 0)
            if idx >= len(data) - 5:
                continue
            
            # Look for false breakout below swing low
            for i in range(idx + 1, min(idx + 6, len(data))):
                current_candle = data[i]
                
                # Check if price breaks below swing low
                if current_candle['low'] < swing_low['price'] * (1 - self.false_breakout_threshold):
                    
                    # Check for quick reversal
                    reversal_found = False
                    for j in range(i + 1, min(i + self.reversal_candles + 1, len(data))):
                        if data[j]['close'] > swing_low['price']:
                            reversal_found = True
                            break
                    
                    if reversal_found:
                        false_breakouts.append({
                            'timestamp': int(current_candle['timestamp']) if isinstance(current_candle['timestamp'], (int, float)) else int(current_candle['timestamp'].timestamp() * 1000),
                            'type': 'false_breakout',
                            'direction': 'bullish_inducement',
                            'breakout_price': current_candle['low'],
                            'key_level': swing_low['price'],
                            'reversal_candles': j - i,
                            'strength': self._calculate_false_breakout_strength(current_candle, swing_low, data),
                            'description': f"False breakout below ${swing_low['price']:.2f}, reversed in {j-i} candles"
                        })
                        break
        
        return false_breakouts
    
    def _detect_volume_inducements(self, data: List[Dict], swing_points: Dict[str, List[Dict]]) -> List[Dict]:
        """Detect inducements with volume confirmation"""
        
        volume_inducements = []
        avg_volume = self._calculate_average_volume(data)
        
        if not swing_points or avg_volume == 0:
            return volume_inducements
        
        # Look for volume spikes at key levels with reversal
        for swing_high in swing_points.get('swing_highs', []):
            idx = swing_high.get('index', 0)
            if idx >= len(data) - 5:
                continue
            
            # Check for volume spike near swing high
            for i in range(max(0, idx - 2), min(idx + 5, len(data))):
                candle = data[i]
                
                # Volume spike detection
                if candle['volume'] > avg_volume * self.volume_spike_multiplier:
                    
                    # Check if price approaches key level
                    if abs(candle['high'] - swing_high['price']) / swing_high['price'] < 0.01:  # Within 1%
                        
                        # Look for reversal after volume spike
                        for j in range(i + 1, min(i + 4, len(data))):
                            if data[j]['close'] < swing_high['price'] * 0.995:  # 0.5% below
                                volume_inducements.append({
                                    'timestamp': int(candle['timestamp']) if isinstance(candle['timestamp'], (int, float)) else int(candle['timestamp'].timestamp() * 1000),
                                    'type': 'volume_inducement',
                                    'direction': 'bearish_inducement',
                                    'volume': candle['volume'],
                                    'avg_volume': avg_volume,
                                    'volume_ratio': candle['volume'] / avg_volume,
                                    'key_level': swing_high['price'],
                                    'reversal_price': data[j]['close'],
                                    'strength': self._calculate_volume_inducement_strength(candle, avg_volume),
                                    'description': f"Volume spike ({candle['volume']/avg_volume:.1f}x) at ${swing_high['price']:.2f} with bearish reversal"
                                })
                                break
        
        return volume_inducements
    
    def _detect_wick_inducements(self, data: List[Dict], swing_points: Dict[str, List[Dict]]) -> List[Dict]:
        """Detect inducements based on significant wicks"""
        
        wick_inducements = []
        
        if not swing_points:
            return wick_inducements
        
        # Check for significant wicks at key levels
        for swing_high in swing_points.get('swing_highs', []):
            idx = swing_high.get('index', 0)
            
            # Check candles around swing high
            for i in range(max(0, idx - 3), min(idx + 5, len(data))):
                candle = data[i]
                
                # Calculate wick ratios
                body_size = abs(candle['close'] - candle['open'])
                upper_wick = candle['high'] - max(candle['close'], candle['open'])
                lower_wick = min(candle['close'], candle['open']) - candle['low']
                
                # Check for significant upper wick at resistance
                if (body_size > 0 and upper_wick / body_size > self.min_wick_ratio and
                    candle['high'] > swing_high['price'] and candle['close'] < swing_high['price']):
                    
                    wick_inducements.append({
                        'timestamp': int(candle['timestamp']) if isinstance(candle['timestamp'], (int, float)) else int(candle['timestamp'].timestamp() * 1000),
                        'type': 'wick_inducement',
                        'direction': 'bearish_inducement',
                        'wick_high': candle['high'],
                        'close_price': candle['close'],
                        'key_level': swing_high['price'],
                        'wick_ratio': upper_wick / body_size,
                        'strength': self._calculate_wick_inducement_strength(candle, swing_high),
                        'description': f"Significant upper wick at ${swing_high['price']:.2f} resistance, ratio: {upper_wick/body_size:.1f}x"
                    })
        
        # Check swing lows for lower wicks
        for swing_low in swing_points.get('swing_lows', []):
            idx = swing_low.get('index', 0)
            
            # Check candles around swing low
            for i in range(max(0, idx - 3), min(idx + 5, len(data))):
                candle = data[i]
                
                # Calculate wick ratios
                body_size = abs(candle['close'] - candle['open'])
                lower_wick = min(candle['close'], candle['open']) - candle['low']
                
                # Check for significant lower wick at support
                if (body_size > 0 and lower_wick / body_size > self.min_wick_ratio and
                    candle['low'] < swing_low['price'] and candle['close'] > swing_low['price']):
                    
                    wick_inducements.append({
                        'timestamp': int(candle['timestamp']) if isinstance(candle['timestamp'], (int, float)) else int(candle['timestamp'].timestamp() * 1000),
                        'type': 'wick_inducement',
                        'direction': 'bullish_inducement',
                        'wick_low': candle['low'],
                        'close_price': candle['close'],
                        'key_level': swing_low['price'],
                        'wick_ratio': lower_wick / body_size,
                        'strength': self._calculate_wick_inducement_strength(candle, swing_low),
                        'description': f"Significant lower wick at ${swing_low['price']:.2f} support, ratio: {lower_wick/body_size:.1f}x"
                    })
        
        return wick_inducements
    
    def _detect_multiple_attempts(self, data: List[Dict], swing_points: Dict[str, List[Dict]]) -> List[Dict]:
        """Detect multiple failed attempts at key levels"""
        
        multiple_attempts = []
        
        if not swing_points:
            return multiple_attempts
        
        # Check for multiple attempts at swing highs
        for swing_high in swing_points.get('swing_highs', []):
            idx = swing_high.get('index', 0)
            key_level = swing_high['price']
            
            # Count attempts within window
            attempts = []
            for i in range(max(0, idx - self.multiple_attempt_window), min(idx + self.multiple_attempt_window, len(data))):
                candle = data[i]
                
                # Check if price approaches level but fails to break
                if (candle['high'] > key_level * 0.998 and  # Within 0.2% of level
                    candle['high'] < key_level * 1.003 and  # But not breaking significantly
                    candle['close'] < key_level):           # Closes below level
                    
                    attempts.append({
                        'index': i,
                        'timestamp': int(candle['timestamp']) if isinstance(candle['timestamp'], (int, float)) else int(candle['timestamp'].timestamp() * 1000),
                        'high': candle['high'],
                        'close': candle['close']
                    })
            
            # If multiple attempts found, mark as inducement
            if len(attempts) >= 3:
                multiple_attempts.append({
                    'timestamp': attempts[-1]['timestamp'],
                    'type': 'multiple_attempts',
                    'direction': 'bearish_inducement',
                    'key_level': key_level,
                    'attempt_count': len(attempts),
                    'attempts': attempts,
                    'strength': self._calculate_multiple_attempts_strength(attempts, key_level),
                    'description': f"{len(attempts)} failed attempts at ${key_level:.2f} resistance"
                })
        
        return multiple_attempts
    
    def _detect_time_based_inducements(self, data: List[Dict], swing_points: Dict[str, List[Dict]]) -> List[Dict]:
        """Detect inducements that occur at specific times (session opens/closes)"""
        
        time_inducements = []
        
        # This is a simplified version - in real implementation, you'd need timezone handling
        # and specific session time detection
        
        return time_inducements  # Placeholder for now
    
    def _calculate_false_breakout_strength(self, breakout_candle: Dict, swing_point: Dict, data: List[Dict]) -> float:
        """Calculate strength of false breakout"""
        
        try:
            # Distance factor
            distance = abs(breakout_candle['high'] - swing_point['price']) / swing_point['price']
            distance_factor = min(distance * 100, 2.0)  # Cap at 2%
            
            # Volume factor
            avg_volume = self._calculate_average_volume(data)
            volume_factor = min(breakout_candle['volume'] / avg_volume, 3.0)
            
            # Reversal speed factor (faster reversal = stronger inducement)
            reversal_speed = 1.0  # Placeholder - would need reversal candle count
            
            strength = (distance_factor + volume_factor + reversal_speed) * 25
            return min(max(strength, 30), 100)
            
        except:
            return 50.0
    
    def _calculate_volume_inducement_strength(self, candle: Dict, avg_volume: float) -> float:
        """Calculate strength of volume inducement"""
        
        try:
            volume_ratio = candle['volume'] / avg_volume
            strength = min(volume_ratio * 30, 100)
            return max(strength, 40)
        except:
            return 50.0
    
    def _calculate_wick_inducement_strength(self, candle: Dict, swing_point: Dict) -> float:
        """Calculate strength of wick inducement"""
        
        try:
            body_size = abs(candle['close'] - candle['open'])
            if body_size == 0:
                return 50.0
            
            upper_wick = candle['high'] - max(candle['close'], candle['open'])
            lower_wick = min(candle['close'], candle['open']) - candle['low']
            
            max_wick = max(upper_wick, lower_wick)
            wick_ratio = max_wick / body_size
            
            strength = min(wick_ratio * 20, 100)
            return max(strength, 35)
            
        except:
            return 50.0
    
    def _calculate_multiple_attempts_strength(self, attempts: List[Dict], key_level: float) -> float:
        """Calculate strength of multiple attempts inducement"""
        
        try:
            # More attempts = stronger inducement
            attempt_factor = min(len(attempts) * 15, 60)
            
            # Precision factor (closer to level = stronger)
            precision_sum = 0
            for attempt in attempts:
                distance = abs(attempt['high'] - key_level) / key_level
                precision_sum += 1.0 / (1.0 + distance * 100)
            
            precision_factor = (precision_sum / len(attempts)) * 40
            
            strength = attempt_factor + precision_factor
            return min(max(strength, 50), 100)
            
        except:
            return 50.0
    
    def _calculate_inducement_confidence(self, inducement: Dict, data: List[Dict]) -> float:
        """Calculate final confidence score for inducement"""
        
        base_strength = inducement.get('strength', 50)
        
        # Type-based confidence adjustment
        type_multipliers = {
            'false_breakout': 1.2,
            'volume_inducement': 1.1,
            'wick_inducement': 1.0,
            'multiple_attempts': 1.3,
            'time_based': 0.9
        }
        
        multiplier = type_multipliers.get(inducement['type'], 1.0)
        confidence = base_strength * multiplier
        
        return min(max(confidence, 0), 100)
    
    def _calculate_average_volume(self, data: List[Dict]) -> float:
        """Calculate average volume"""
        
        if not data:
            return 1.0
        
        try:
            volumes = [candle['volume'] for candle in data if 'volume' in candle]
            return sum(volumes) / len(volumes) if volumes else 1.0
        except:
            return 1.0
    
    def get_inducement_summary(self, inducements: List[Dict]) -> Dict[str, Any]:
        """Generate summary of detected inducements"""
        
        if not inducements:
            return {
                'total_inducements': 0,
                'bullish_inducements': 0,
                'bearish_inducements': 0,
                'strongest_inducement': None,
                'most_recent_inducement': None,
                'visualization_data': []
            }
        
        bullish_count = sum(1 for ind in inducements if 'bullish' in ind.get('direction', ''))
        bearish_count = sum(1 for ind in inducements if 'bearish' in ind.get('direction', ''))
        
        # Find strongest inducement
        strongest = max(inducements, key=lambda x: x.get('confidence_score', 0))
        
        # Find most recent inducement
        most_recent = max(inducements, key=lambda x: x.get('timestamp', 0))
        
        return {
            'total_inducements': len(inducements),
            'bullish_inducements': bullish_count,
            'bearish_inducements': bearish_count,
            'strongest_inducement': strongest,
            'most_recent_inducement': most_recent,
            'inducement_types': {
                'false_breakout': sum(1 for ind in inducements if ind.get('type') == 'false_breakout'),
                'volume_inducement': sum(1 for ind in inducements if ind.get('type') == 'volume_inducement'),
                'wick_inducement': sum(1 for ind in inducements if ind.get('type') == 'wick_inducement'),
                'multiple_attempts': sum(1 for ind in inducements if ind.get('type') == 'multiple_attempts'),
                'time_based': sum(1 for ind in inducements if ind.get('type') == 'time_based')
            },
            'visualization_data': self._prepare_visualization_data(inducements)
        }
    
    def _prepare_visualization_data(self, inducements: List[Dict]) -> List[Dict]:
        """Prepare visualization data for chart display"""
        
        visualization_data = []
        
        for inducement in inducements:
            viz_data = {
                'timestamp': inducement.get('timestamp'),
                'type': inducement.get('type'),
                'direction': inducement.get('direction'),
                'key_level': inducement.get('key_level'),
                'confidence': inducement.get('confidence_score', 50),
                'description': inducement.get('description'),
                'chart_annotation': {
                    'type': 'zone',
                    'color': '#FF5722' if 'bearish' in inducement.get('direction', '') else '#4CAF50',
                    'opacity': 0.3,
                    'label': f"{inducement.get('type', '').title()} - {inducement.get('confidence_score', 50):.0f}%"
                }
            }
            
            # Add specific visualization data based on inducement type
            if inducement.get('type') == 'false_breakout':
                viz_data['chart_annotation']['marker'] = {
                    'symbol': 'triangle-up' if 'bullish' in inducement.get('direction', '') else 'triangle-down',
                    'size': 8,
                    'color': viz_data['chart_annotation']['color']
                }
            elif inducement.get('type') == 'wick_inducement':
                viz_data['chart_annotation']['line'] = {
                    'width': 2,
                    'dash': 'dash',
                    'color': viz_data['chart_annotation']['color']
                }
            
            visualization_data.append(viz_data)
        
        return visualization_data
    
    def log_inducement_for_analysis(self, inducement: Dict, symbol: str, timeframe: str) -> None:
        """Log inducement for manual analysis"""
        
        log_message = f"""
        🎯 INDUCEMENT DETECTED - {symbol} {timeframe}
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        Type: {inducement.get('type', 'unknown').upper()}
        Direction: {inducement.get('direction', 'unknown').upper()}
        Key Level: ${inducement.get('key_level', 0):.4f}
        Confidence: {inducement.get('confidence_score', 0):.1f}%
        Description: {inducement.get('description', 'No description')}
        
        📊 Technical Details:
        - Timestamp: {inducement.get('timestamp', 0)}
        - Strength: {inducement.get('strength', 0):.1f}
        
        📈 Market Context:
        - Volume Ratio: {inducement.get('volume_ratio', 'N/A')}
        - Reversal Candles: {inducement.get('reversal_candles', 'N/A')}
        - Attempts: {inducement.get('attempt_count', 'N/A')}
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """
        
        self.logger.info(log_message)