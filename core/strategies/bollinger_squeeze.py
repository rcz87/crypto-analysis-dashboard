"""
Bollinger Bands Squeeze Strategy
Identifies periods of low volatility (squeeze) followed by breakouts
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List
from .base_strategy import BaseStrategy

class Strategy(BaseStrategy):
    """Bollinger Bands Squeeze Strategy"""
    
    def __init__(self):
        super().__init__("Bollinger Squeeze")
        self.parameters = {
            'bb_period': 20,
            'bb_std': 2.0,
            'squeeze_threshold': 0.02,  # 2% bandwidth threshold for squeeze
            'breakout_threshold': 1.5,  # Breakout strength multiplier
            'min_confidence': 70
        }
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate Bollinger Bands and squeeze indicators"""
        df = data.copy()
        
        # Calculate Bollinger Bands
        df['bb_middle'] = df['close'].rolling(window=self.parameters['bb_period']).mean()
        bb_std = df['close'].rolling(window=self.parameters['bb_period']).std()
        
        df['bb_upper'] = df['bb_middle'] + (bb_std * self.parameters['bb_std'])
        df['bb_lower'] = df['bb_middle'] - (bb_std * self.parameters['bb_std'])
        
        # Calculate bandwidth (squeeze indicator)
        df['bb_bandwidth'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']
        df['bb_bandwidth_ma'] = df['bb_bandwidth'].rolling(window=10).mean()
        
        # Identify squeeze periods
        df['is_squeeze'] = df['bb_bandwidth'] < self.parameters['squeeze_threshold']
        df['squeeze_ending'] = (df['is_squeeze'].shift(1) == True) & (df['is_squeeze'] == False)
        
        # Calculate price position relative to bands
        df['bb_position'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
        
        # Identify breakouts
        df['upper_breakout'] = (df['close'] > df['bb_upper']) & (df['close'].shift(1) <= df['bb_upper'].shift(1))
        df['lower_breakout'] = (df['close'] < df['bb_lower']) & (df['close'].shift(1) >= df['bb_lower'].shift(1))
        
        # Calculate volatility expansion
        df['volatility_expansion'] = df['bb_bandwidth'] / df['bb_bandwidth'].shift(1)
        
        return df
    
    def generate_signals(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Generate Bollinger Squeeze signals"""
        if not self.validate_data(data):
            return []
        
        df = self.calculate_indicators(data)
        signals = []
        
        for i, row in df.iterrows():
            timestamp = row.get('timestamp', i)
            
            # Skip if we don't have enough data
            if pd.isna(row['bb_bandwidth']) or pd.isna(row['bb_position']):
                continue
            
            action = 'HOLD'
            confidence = 50
            reason = "No clear squeeze signal"
            
            # Check for bullish breakout after squeeze
            if row['upper_breakout'] and not pd.isna(row['volatility_expansion']):
                action = 'BUY'
                
                base_confidence = self.parameters['min_confidence']
                
                # Volatility expansion bonus
                vol_bonus = min((row['volatility_expansion'] - 1) * 20, 15)
                
                # Volume confirmation
                volume_bonus = 0
                if 'volume' in row and not pd.isna(row['volume']):
                    avg_volume = df['volume'].rolling(window=20).mean().iloc[i]
                    if not pd.isna(avg_volume) and avg_volume > 0:
                        volume_ratio = row['volume'] / avg_volume
                        volume_bonus = min((volume_ratio - 1) * 10, 10)
                
                # Squeeze context bonus
                squeeze_bonus = 5 if row['squeeze_ending'] else 0
                
                confidence = min(int(base_confidence + vol_bonus + volume_bonus + squeeze_bonus), 90)
                reason = f"Bullish BB breakout - Price: {row['close']:.2f}, Upper Band: {row['bb_upper']:.2f}"
            
            # Check for bearish breakout after squeeze
            elif row['lower_breakout'] and not pd.isna(row['volatility_expansion']):
                action = 'SELL'
                
                base_confidence = self.parameters['min_confidence']
                
                # Volatility expansion bonus
                vol_bonus = min((row['volatility_expansion'] - 1) * 20, 15)
                
                # Volume confirmation
                volume_bonus = 0
                if 'volume' in row and not pd.isna(row['volume']):
                    avg_volume = df['volume'].rolling(window=20).mean().iloc[i]
                    if not pd.isna(avg_volume) and avg_volume > 0:
                        volume_ratio = row['volume'] / avg_volume
                        volume_bonus = min((volume_ratio - 1) * 10, 10)
                
                # Squeeze context bonus
                squeeze_bonus = 5 if row['squeeze_ending'] else 0
                
                confidence = min(int(base_confidence + vol_bonus + volume_bonus + squeeze_bonus), 90)
                reason = f"Bearish BB breakout - Price: {row['close']:.2f}, Lower Band: {row['bb_lower']:.2f}"
            
            # Check for squeeze ending with direction bias
            elif row['squeeze_ending']:
                # Determine direction based on price position and momentum
                price_momentum = (row['close'] - df['close'].iloc[max(0, i-5)]) / df['close'].iloc[max(0, i-5)]
                
                if row['bb_position'] > 0.6 and price_momentum > 0:
                    action = 'BUY'
                    confidence = self.parameters['min_confidence'] - 10
                    reason = f"Squeeze ending with bullish bias - Position: {row['bb_position']:.2f}"
                elif row['bb_position'] < 0.4 and price_momentum < 0:
                    action = 'SELL'
                    confidence = self.parameters['min_confidence'] - 10
                    reason = f"Squeeze ending with bearish bias - Position: {row['bb_position']:.2f}"
            
            # Only add signals with meaningful actions or at key points
            if action != 'HOLD' or i == len(df) - 1:
                signals.append({
                    'timestamp': timestamp,
                    'action': action,
                    'price': float(row['close']),
                    'confidence': confidence,
                    'reason': reason,
                    'bb_bandwidth': float(row['bb_bandwidth']),
                    'bb_position': float(row['bb_position']),
                    'is_squeeze': bool(row['is_squeeze'])
                })
        
        return signals