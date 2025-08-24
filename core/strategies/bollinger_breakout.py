"""
Bollinger Bands Breakout Strategy
Buy when price breaks above upper band, sell when price breaks below lower band
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List
from .base_strategy import BaseStrategy

class Strategy(BaseStrategy):
    """Bollinger Bands Breakout Strategy"""
    
    def __init__(self):
        super().__init__("Bollinger Breakout")
        self.parameters = {
            'period': 20,
            'std_dev': 2.0,
            'min_volume_ratio': 1.2,  # Minimum volume increase for confirmation
            'min_confidence': 72
        }
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate Bollinger Bands and breakout indicators"""
        df = data.copy()
        
        # Calculate Bollinger Bands
        df['bb_middle'] = df['close'].rolling(window=self.parameters['period']).mean()
        bb_std = df['close'].rolling(window=self.parameters['period']).std()
        
        df['bb_upper'] = df['bb_middle'] + (bb_std * self.parameters['std_dev'])
        df['bb_lower'] = df['bb_middle'] - (bb_std * self.parameters['std_dev'])
        
        # Calculate bandwidth and %B
        df['bb_bandwidth'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']
        df['bb_percent'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
        
        # Previous values for breakout detection
        df['close_prev'] = df['close'].shift(1)
        df['bb_upper_prev'] = df['bb_upper'].shift(1)
        df['bb_lower_prev'] = df['bb_lower'].shift(1)
        
        # Identify breakouts
        df['upper_breakout'] = (
            (df['close'] > df['bb_upper']) & 
            (df['close_prev'] <= df['bb_upper_prev'])
        )
        
        df['lower_breakout'] = (
            (df['close'] < df['bb_lower']) & 
            (df['close_prev'] >= df['bb_lower_prev'])
        )
        
        # Calculate momentum for breakout strength
        df['price_momentum'] = df['close'].pct_change(3)  # 3-period momentum
        df['rsi'] = self.calculate_rsi(df['close'], 14)  # RSI for overbought/oversold
        
        # Volume analysis
        if 'volume' in df.columns:
            df['volume_sma'] = df['volume'].rolling(window=20).mean()
            df['volume_ratio'] = df['volume'] / df['volume_sma']
        else:
            df['volume_ratio'] = 1.0
        
        return df
    
    def calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI for additional confirmation"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def generate_signals(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Generate Bollinger Bands breakout signals"""
        if not self.validate_data(data):
            return []
        
        df = self.calculate_indicators(data)
        signals = []
        
        for i, row in df.iterrows():
            timestamp = row.get('timestamp', i)
            
            # Skip if we don't have enough data
            if pd.isna(row['bb_upper']) or pd.isna(row['bb_lower']):
                continue
            
            action = 'HOLD'
            confidence = 50
            reason = "No clear breakout signal"
            
            # Check for upper breakout (bullish)
            if row['upper_breakout']:
                action = 'BUY'
                base_confidence = self.parameters['min_confidence']
                
                # Volume confirmation bonus
                volume_bonus = 0
                if not pd.isna(row['volume_ratio']) and row['volume_ratio'] >= self.parameters['min_volume_ratio']:
                    volume_bonus = min((row['volume_ratio'] - 1) * 10, 15)
                
                # Momentum bonus
                momentum_bonus = 0
                if not pd.isna(row['price_momentum']) and row['price_momentum'] > 0:
                    momentum_bonus = min(row['price_momentum'] * 200, 10)
                
                # RSI condition (not extremely overbought)
                rsi_penalty = 0
                if not pd.isna(row['rsi']) and row['rsi'] > 80:
                    rsi_penalty = -10
                
                # Bandwidth bonus (wider bands = stronger breakout)
                bandwidth_bonus = 0
                if not pd.isna(row['bb_bandwidth']):
                    avg_bandwidth = df['bb_bandwidth'].rolling(window=50).mean().iloc[i]
                    if not pd.isna(avg_bandwidth) and row['bb_bandwidth'] > avg_bandwidth:
                        bandwidth_bonus = 5
                
                confidence = max(min(int(base_confidence + volume_bonus + momentum_bonus + 
                                    rsi_penalty + bandwidth_bonus), 95), 50)
                
                reason = f"Bullish BB breakout - Price: {row['close']:.2f}, Upper: {row['bb_upper']:.2f}, Volume: {row['volume_ratio']:.1f}x"
            
            # Check for lower breakout (bearish)
            elif row['lower_breakout']:
                action = 'SELL'
                base_confidence = self.parameters['min_confidence']
                
                # Volume confirmation bonus
                volume_bonus = 0
                if not pd.isna(row['volume_ratio']) and row['volume_ratio'] >= self.parameters['min_volume_ratio']:
                    volume_bonus = min((row['volume_ratio'] - 1) * 10, 15)
                
                # Momentum bonus
                momentum_bonus = 0
                if not pd.isna(row['price_momentum']) and row['price_momentum'] < 0:
                    momentum_bonus = min(abs(row['price_momentum']) * 200, 10)
                
                # RSI condition (not extremely oversold)
                rsi_penalty = 0
                if not pd.isna(row['rsi']) and row['rsi'] < 20:
                    rsi_penalty = -10
                
                # Bandwidth bonus
                bandwidth_bonus = 0
                if not pd.isna(row['bb_bandwidth']):
                    avg_bandwidth = df['bb_bandwidth'].rolling(window=50).mean().iloc[i]
                    if not pd.isna(avg_bandwidth) and row['bb_bandwidth'] > avg_bandwidth:
                        bandwidth_bonus = 5
                
                confidence = max(min(int(base_confidence + volume_bonus + momentum_bonus + 
                                    rsi_penalty + bandwidth_bonus), 95), 50)
                
                reason = f"Bearish BB breakout - Price: {row['close']:.2f}, Lower: {row['bb_lower']:.2f}, Volume: {row['volume_ratio']:.1f}x"
            
            # Check for mean reversion opportunities
            elif not pd.isna(row['bb_percent']):
                if row['bb_percent'] > 0.95 and not pd.isna(row['rsi']) and row['rsi'] > 70:
                    # Potential reversal from upper band
                    action = 'SELL'
                    confidence = self.parameters['min_confidence'] - 15
                    reason = f"BB mean reversion signal - Price extended above upper band"
                
                elif row['bb_percent'] < 0.05 and not pd.isna(row['rsi']) and row['rsi'] < 30:
                    # Potential reversal from lower band
                    action = 'BUY'
                    confidence = self.parameters['min_confidence'] - 15
                    reason = f"BB mean reversion signal - Price extended below lower band"
            
            # Only add signals with meaningful actions or at key points
            if action != 'HOLD' or i == len(df) - 1:
                signals.append({
                    'timestamp': timestamp,
                    'action': action,
                    'price': float(row['close']),
                    'confidence': confidence,
                    'reason': reason,
                    'bb_upper': float(row['bb_upper']) if not pd.isna(row['bb_upper']) else 0,
                    'bb_lower': float(row['bb_lower']) if not pd.isna(row['bb_lower']) else 0,
                    'bb_middle': float(row['bb_middle']) if not pd.isna(row['bb_middle']) else 0,
                    'bb_percent': float(row['bb_percent']) if not pd.isna(row['bb_percent']) else 0.5
                })
        
        return signals