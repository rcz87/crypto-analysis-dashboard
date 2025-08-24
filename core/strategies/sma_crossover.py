"""
Simple Moving Average Crossover Strategy
Buy when fast SMA crosses above slow SMA, sell when it crosses below
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List
from .base_strategy import BaseStrategy

class Strategy(BaseStrategy):
    """SMA Crossover Strategy"""
    
    def __init__(self):
        super().__init__("SMA Crossover")
        self.parameters = {
            'fast_period': 10,
            'slow_period': 30,
            'min_confidence': 60
        }
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate SMA indicators"""
        df = data.copy()
        
        # Calculate SMAs
        df['sma_fast'] = df['close'].rolling(window=self.parameters['fast_period']).mean()
        df['sma_slow'] = df['close'].rolling(window=self.parameters['slow_period']).mean()
        
        # Calculate crossover signals
        df['sma_fast_prev'] = df['sma_fast'].shift(1)
        df['sma_slow_prev'] = df['sma_slow'].shift(1)
        
        # Identify crossovers
        df['bullish_cross'] = (
            (df['sma_fast'] > df['sma_slow']) & 
            (df['sma_fast_prev'] <= df['sma_slow_prev'])
        )
        
        df['bearish_cross'] = (
            (df['sma_fast'] < df['sma_slow']) & 
            (df['sma_fast_prev'] >= df['sma_slow_prev'])
        )
        
        return df
    
    def generate_signals(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Generate SMA crossover signals"""
        if not self.validate_data(data):
            return []
        
        df = self.calculate_indicators(data)
        signals = []
        
        for i, row in df.iterrows():
            timestamp = row.get('timestamp', i)
            
            # Skip if we don't have enough data
            if pd.isna(row['sma_fast']) or pd.isna(row['sma_slow']):
                continue
            
            action = 'HOLD'
            confidence = 50
            reason = "No clear signal"
            
            # Check for bullish crossover
            if row['bullish_cross']:
                action = 'BUY'
                
                # Calculate confidence based on trend strength
                sma_distance = abs(row['sma_fast'] - row['sma_slow']) / row['close']
                volume_factor = 1.0
                
                if 'volume' in row and not pd.isna(row['volume']):
                    # Higher volume increases confidence
                    avg_volume = df['volume'].rolling(window=20).mean().iloc[i]
                    if not pd.isna(avg_volume) and avg_volume > 0:
                        volume_factor = min(row['volume'] / avg_volume, 2.0)
                
                confidence = min(int(self.parameters['min_confidence'] + 
                                   sma_distance * 10000 + 
                                   (volume_factor - 1) * 10), 90)
                
                reason = f"Bullish SMA crossover - Fast({self.parameters['fast_period']}) > Slow({self.parameters['slow_period']})"
            
            # Check for bearish crossover
            elif row['bearish_cross']:
                action = 'SELL'
                
                # Calculate confidence
                sma_distance = abs(row['sma_fast'] - row['sma_slow']) / row['close']
                volume_factor = 1.0
                
                if 'volume' in row and not pd.isna(row['volume']):
                    avg_volume = df['volume'].rolling(window=20).mean().iloc[i]
                    if not pd.isna(avg_volume) and avg_volume > 0:
                        volume_factor = min(row['volume'] / avg_volume, 2.0)
                
                confidence = min(int(self.parameters['min_confidence'] + 
                                   sma_distance * 10000 + 
                                   (volume_factor - 1) * 10), 90)
                
                reason = f"Bearish SMA crossover - Fast({self.parameters['fast_period']}) < Slow({self.parameters['slow_period']})"
            
            # Only add signals with meaningful actions or at key points
            if action != 'HOLD' or i == len(df) - 1:  # Always include the last signal
                signals.append({
                    'timestamp': timestamp,
                    'action': action,
                    'price': float(row['close']),
                    'confidence': confidence,
                    'reason': reason,
                    'sma_fast': float(row['sma_fast']),
                    'sma_slow': float(row['sma_slow'])
                })
        
        return signals