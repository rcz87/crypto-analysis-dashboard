"""
MACD Divergence Strategy
Identifies bullish/bearish divergences between price and MACD for reversal signals
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List
from .base_strategy import BaseStrategy

class Strategy(BaseStrategy):
    """MACD Divergence Strategy"""
    
    def __init__(self):
        super().__init__("MACD Divergence")
        self.parameters = {
            'fast_period': 12,
            'slow_period': 26,
            'signal_period': 9,
            'divergence_lookback': 10,
            'min_confidence': 75
        }
    
    def calculate_macd(self, prices: pd.Series) -> Dict[str, pd.Series]:
        """Calculate MACD indicator"""
        # Calculate EMAs
        ema_fast = prices.ewm(span=self.parameters['fast_period']).mean()
        ema_slow = prices.ewm(span=self.parameters['slow_period']).mean()
        
        # MACD line
        macd_line = ema_fast - ema_slow
        
        # Signal line
        signal_line = macd_line.ewm(span=self.parameters['signal_period']).mean()
        
        # Histogram
        histogram = macd_line - signal_line
        
        return {
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram
        }
    
    def find_peaks_valleys(self, series: pd.Series, window: int = 5) -> Dict[str, List]:
        """Find peaks and valleys in a series"""
        peaks = []
        valleys = []
        
        for i in range(window, len(series) - window):
            # Check for peak
            if all(series.iloc[i] >= series.iloc[i-j] for j in range(1, window+1)) and \
               all(series.iloc[i] >= series.iloc[i+j] for j in range(1, window+1)):
                peaks.append(i)
            
            # Check for valley
            elif all(series.iloc[i] <= series.iloc[i-j] for j in range(1, window+1)) and \
                 all(series.iloc[i] <= series.iloc[i+j] for j in range(1, window+1)):
                valleys.append(i)
        
        return {'peaks': peaks, 'valleys': valleys}
    
    def detect_divergence(self, price_extremes: List, macd_extremes: List, 
                         price_series: pd.Series, macd_series: pd.Series) -> List[Dict]:
        """Detect divergences between price and MACD"""
        divergences = []
        
        # Need at least 2 points for divergence
        if len(price_extremes) < 2 or len(macd_extremes) < 2:
            return divergences
        
        # Check recent extremes
        for i in range(len(price_extremes) - 1):
            for j in range(len(macd_extremes) - 1):
                p1_idx, p2_idx = price_extremes[i], price_extremes[i + 1]
                m1_idx, m2_idx = macd_extremes[j], macd_extremes[j + 1]
                
                # Check if timeframes are reasonably aligned
                if abs(p1_idx - m1_idx) > 5 or abs(p2_idx - m2_idx) > 5:
                    continue
                
                p1_val, p2_val = price_series.iloc[p1_idx], price_series.iloc[p2_idx]
                m1_val, m2_val = macd_series.iloc[m1_idx], macd_series.iloc[m2_idx]
                
                # Bullish divergence: price makes lower low, MACD makes higher low
                if p2_val < p1_val and m2_val > m1_val:
                    divergences.append({
                        'type': 'bullish',
                        'strength': abs(m2_val - m1_val) / abs(p2_val - p1_val) * 100,
                        'recent_index': max(p2_idx, m2_idx)
                    })
                
                # Bearish divergence: price makes higher high, MACD makes lower high
                elif p2_val > p1_val and m2_val < m1_val:
                    divergences.append({
                        'type': 'bearish',
                        'strength': abs(m1_val - m2_val) / abs(p2_val - p1_val) * 100,
                        'recent_index': max(p2_idx, m2_idx)
                    })
        
        return divergences
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate MACD and divergence indicators"""
        df = data.copy()
        
        # Calculate MACD
        macd_data = self.calculate_macd(df['close'])
        df['macd'] = macd_data['macd']
        df['macd_signal'] = macd_data['signal']
        df['macd_histogram'] = macd_data['histogram']
        
        # Find peaks and valleys
        price_extremes = self.find_peaks_valleys(df['close'])
        macd_extremes = self.find_peaks_valleys(df['macd'])
        
        # Detect divergences
        peaks_divergences = self.detect_divergence(
            price_extremes['peaks'], macd_extremes['peaks'], 
            df['close'], df['macd']
        )
        
        valleys_divergences = self.detect_divergence(
            price_extremes['valleys'], macd_extremes['valleys'], 
            df['close'], df['macd']
        )
        
        # Mark divergences in dataframe
        df['bullish_divergence'] = False
        df['bearish_divergence'] = False
        df['divergence_strength'] = 0.0
        
        for div in peaks_divergences + valleys_divergences:
            idx = div['recent_index']
            if div['type'] == 'bullish':
                df.iloc[idx, df.columns.get_loc('bullish_divergence')] = True
            else:
                df.iloc[idx, df.columns.get_loc('bearish_divergence')] = True
            df.iloc[idx, df.columns.get_loc('divergence_strength')] = div['strength']
        
        # MACD crossovers
        df['macd_bullish_cross'] = (df['macd'] > df['macd_signal']) & (df['macd'].shift(1) <= df['macd_signal'].shift(1))
        df['macd_bearish_cross'] = (df['macd'] < df['macd_signal']) & (df['macd'].shift(1) >= df['macd_signal'].shift(1))
        
        return df
    
    def generate_signals(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Generate MACD divergence signals"""
        if not self.validate_data(data):
            return []
        
        df = self.calculate_indicators(data)
        signals = []
        
        for i, row in df.iterrows():
            timestamp = row.get('timestamp', i)
            
            # Skip if we don't have enough data
            if pd.isna(row['macd']) or pd.isna(row['macd_signal']):
                continue
            
            action = 'HOLD'
            confidence = 50
            reason = "No clear MACD signal"
            
            # Priority 1: Divergence signals (strongest)
            if row['bullish_divergence']:
                action = 'BUY'
                base_confidence = self.parameters['min_confidence']
                
                # Strength bonus
                strength_bonus = min(row['divergence_strength'] * 0.1, 10)
                
                # MACD position bonus
                macd_bonus = 5 if row['macd'] < 0 else 0  # Better if MACD is below zero
                
                confidence = min(int(base_confidence + strength_bonus + macd_bonus), 95)
                reason = f"Bullish MACD divergence detected - Strength: {row['divergence_strength']:.1f}"
            
            elif row['bearish_divergence']:
                action = 'SELL'
                base_confidence = self.parameters['min_confidence']
                
                # Strength bonus
                strength_bonus = min(row['divergence_strength'] * 0.1, 10)
                
                # MACD position bonus
                macd_bonus = 5 if row['macd'] > 0 else 0  # Better if MACD is above zero
                
                confidence = min(int(base_confidence + strength_bonus + macd_bonus), 95)
                reason = f"Bearish MACD divergence detected - Strength: {row['divergence_strength']:.1f}"
            
            # Priority 2: MACD crossovers (medium strength)
            elif row['macd_bullish_cross']:
                action = 'BUY'
                base_confidence = self.parameters['min_confidence'] - 15
                
                # Histogram strength
                hist_bonus = min(abs(row['macd_histogram']) * 1000, 10) if not pd.isna(row['macd_histogram']) else 0
                
                # Volume confirmation
                volume_bonus = 0
                if 'volume' in row and not pd.isna(row['volume']):
                    avg_volume = df['volume'].rolling(window=10).mean().iloc[i]
                    if not pd.isna(avg_volume) and avg_volume > 0:
                        volume_ratio = row['volume'] / avg_volume
                        volume_bonus = min((volume_ratio - 1) * 5, 8)
                
                confidence = min(int(base_confidence + hist_bonus + volume_bonus), 85)
                reason = f"MACD bullish crossover - MACD: {row['macd']:.4f}, Signal: {row['macd_signal']:.4f}"
            
            elif row['macd_bearish_cross']:
                action = 'SELL'
                base_confidence = self.parameters['min_confidence'] - 15
                
                # Histogram strength
                hist_bonus = min(abs(row['macd_histogram']) * 1000, 10) if not pd.isna(row['macd_histogram']) else 0
                
                # Volume confirmation
                volume_bonus = 0
                if 'volume' in row and not pd.isna(row['volume']):
                    avg_volume = df['volume'].rolling(window=10).mean().iloc[i]
                    if not pd.isna(avg_volume) and avg_volume > 0:
                        volume_ratio = row['volume'] / avg_volume
                        volume_bonus = min((volume_ratio - 1) * 5, 8)
                
                confidence = min(int(base_confidence + hist_bonus + volume_bonus), 85)
                reason = f"MACD bearish crossover - MACD: {row['macd']:.4f}, Signal: {row['macd_signal']:.4f}"
            
            # Only add signals with meaningful actions or at key points
            if action != 'HOLD' or i == len(df) - 1:
                signals.append({
                    'timestamp': timestamp,
                    'action': action,
                    'price': float(row['close']),
                    'confidence': confidence,
                    'reason': reason,
                    'macd': float(row['macd']) if not pd.isna(row['macd']) else 0,
                    'macd_signal': float(row['macd_signal']) if not pd.isna(row['macd_signal']) else 0,
                    'macd_histogram': float(row['macd_histogram']) if not pd.isna(row['macd_histogram']) else 0
                })
        
        return signals