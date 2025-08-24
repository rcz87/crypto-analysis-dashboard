"""
MACD Line Crossover Strategy
Buy when MACD line crosses above signal line, sell when it crosses below
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List
from .base_strategy import BaseStrategy

class Strategy(BaseStrategy):
    """MACD Line Crossover Strategy"""
    
    def __init__(self):
        super().__init__("MACD Crossover")
        self.parameters = {
            'fast_period': 12,
            'slow_period': 26,
            'signal_period': 9,
            'min_confidence': 70
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
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate MACD and crossover indicators"""
        df = data.copy()
        
        # Calculate MACD
        macd_data = self.calculate_macd(df['close'])
        df['macd'] = macd_data['macd']
        df['macd_signal'] = macd_data['signal']
        df['macd_histogram'] = macd_data['histogram']
        
        # Calculate crossovers
        df['macd_prev'] = df['macd'].shift(1)
        df['signal_prev'] = df['macd_signal'].shift(1)
        
        # Identify crossovers
        df['bullish_cross'] = (
            (df['macd'] > df['macd_signal']) & 
            (df['macd_prev'] <= df['signal_prev'])
        )
        
        df['bearish_cross'] = (
            (df['macd'] < df['macd_signal']) & 
            (df['macd_prev'] >= df['signal_prev'])
        )
        
        # MACD zero line crossovers (stronger signals)
        df['macd_above_zero'] = df['macd'] > 0
        df['macd_zero_cross_up'] = (df['macd'] > 0) & (df['macd_prev'] <= 0)
        df['macd_zero_cross_down'] = (df['macd'] < 0) & (df['macd_prev'] >= 0)
        
        return df
    
    def generate_signals(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Generate MACD crossover signals"""
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
            
            # Check for bullish crossover
            if row['bullish_cross']:
                action = 'BUY'
                base_confidence = self.parameters['min_confidence']
                
                # Bonus for zero line position
                zero_bonus = 10 if row['macd_above_zero'] else 0
                
                # Histogram strength bonus
                hist_bonus = min(abs(row['macd_histogram']) * 5000, 10) if not pd.isna(row['macd_histogram']) else 0
                
                # Volume confirmation
                volume_bonus = 0
                if 'volume' in row and not pd.isna(row['volume']):
                    avg_volume = df['volume'].rolling(window=20).mean().iloc[i]
                    if not pd.isna(avg_volume) and avg_volume > 0:
                        volume_ratio = row['volume'] / avg_volume
                        volume_bonus = min((volume_ratio - 1) * 8, 10)
                
                confidence = min(int(base_confidence + zero_bonus + hist_bonus + volume_bonus), 95)
                reason = f"MACD bullish crossover - MACD: {row['macd']:.4f}, Signal: {row['macd_signal']:.4f}"
            
            # Check for bearish crossover
            elif row['bearish_cross']:
                action = 'SELL'
                base_confidence = self.parameters['min_confidence']
                
                # Bonus for zero line position
                zero_bonus = 10 if not row['macd_above_zero'] else 0
                
                # Histogram strength bonus
                hist_bonus = min(abs(row['macd_histogram']) * 5000, 10) if not pd.isna(row['macd_histogram']) else 0
                
                # Volume confirmation
                volume_bonus = 0
                if 'volume' in row and not pd.isna(row['volume']):
                    avg_volume = df['volume'].rolling(window=20).mean().iloc[i]
                    if not pd.isna(avg_volume) and avg_volume > 0:
                        volume_ratio = row['volume'] / avg_volume
                        volume_bonus = min((volume_ratio - 1) * 8, 10)
                
                confidence = min(int(base_confidence + zero_bonus + hist_bonus + volume_bonus), 95)
                reason = f"MACD bearish crossover - MACD: {row['macd']:.4f}, Signal: {row['macd_signal']:.4f}"
            
            # Check for zero line crossovers (stronger signals)
            elif row['macd_zero_cross_up']:
                action = 'BUY'
                confidence = min(self.parameters['min_confidence'] + 15, 90)
                reason = f"MACD bullish zero line crossover - Strong momentum signal"
            
            elif row['macd_zero_cross_down']:
                action = 'SELL'
                confidence = min(self.parameters['min_confidence'] + 15, 90)
                reason = f"MACD bearish zero line crossover - Strong momentum signal"
            
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