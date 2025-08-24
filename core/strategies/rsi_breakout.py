"""
RSI Breakout Strategy
Buy when RSI breaks above oversold level (30) with momentum
Sell when RSI breaks below overbought level (70) with momentum
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List
from .base_strategy import BaseStrategy

class Strategy(BaseStrategy):
    """RSI Breakout Strategy"""
    
    def __init__(self):
        super().__init__("RSI Breakout")
        self.parameters = {
            'rsi_period': 14,
            'oversold_level': 30,
            'overbought_level': 70,
            'momentum_threshold': 5,  # RSI momentum required for signal
            'min_confidence': 65
        }
    
    def calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI indicator"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate RSI and related indicators"""
        df = data.copy()
        
        # Calculate RSI
        df['rsi'] = self.calculate_rsi(df['close'], self.parameters['rsi_period'])
        df['rsi_prev'] = df['rsi'].shift(1)
        df['rsi_momentum'] = df['rsi'] - df['rsi_prev']
        
        # Calculate price momentum
        df['price_change'] = df['close'].pct_change()
        df['price_momentum'] = df['close'].rolling(window=3).mean().pct_change()
        
        # Identify breakout conditions
        df['oversold_breakout'] = (
            (df['rsi'] > self.parameters['oversold_level']) & 
            (df['rsi_prev'] <= self.parameters['oversold_level']) &
            (df['rsi_momentum'] >= self.parameters['momentum_threshold'])
        )
        
        df['overbought_breakout'] = (
            (df['rsi'] < self.parameters['overbought_level']) & 
            (df['rsi_prev'] >= self.parameters['overbought_level']) &
            (df['rsi_momentum'] <= -self.parameters['momentum_threshold'])
        )
        
        return df
    
    def generate_signals(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Generate RSI breakout signals"""
        if not self.validate_data(data):
            return []
        
        df = self.calculate_indicators(data)
        signals = []
        
        for i, row in df.iterrows():
            timestamp = row.get('timestamp', i)
            
            # Skip if we don't have enough data
            if pd.isna(row['rsi']) or pd.isna(row['rsi_prev']):
                continue
            
            action = 'HOLD'
            confidence = 50
            reason = "No clear RSI signal"
            
            # Check for oversold breakout (bullish)
            if row['oversold_breakout']:
                action = 'BUY'
                
                # Calculate confidence based on multiple factors
                base_confidence = self.parameters['min_confidence']
                
                # RSI momentum factor
                momentum_bonus = min(abs(row['rsi_momentum']) * 2, 15)
                
                # Price momentum alignment
                price_alignment = 5 if row['price_momentum'] > 0 else -5
                
                # Volume factor
                volume_bonus = 0
                if 'volume' in row and not pd.isna(row['volume']):
                    avg_volume = df['volume'].rolling(window=10).mean().iloc[i]
                    if not pd.isna(avg_volume) and avg_volume > 0:
                        volume_ratio = row['volume'] / avg_volume
                        volume_bonus = min((volume_ratio - 1) * 10, 10)
                
                confidence = min(int(base_confidence + momentum_bonus + price_alignment + volume_bonus), 90)
                
                reason = f"RSI oversold breakout - RSI: {row['rsi']:.1f}, Momentum: {row['rsi_momentum']:.1f}"
            
            # Check for overbought breakout (bearish)
            elif row['overbought_breakout']:
                action = 'SELL'
                
                # Calculate confidence
                base_confidence = self.parameters['min_confidence']
                
                # RSI momentum factor
                momentum_bonus = min(abs(row['rsi_momentum']) * 2, 15)
                
                # Price momentum alignment
                price_alignment = 5 if row['price_momentum'] < 0 else -5
                
                # Volume factor
                volume_bonus = 0
                if 'volume' in row and not pd.isna(row['volume']):
                    avg_volume = df['volume'].rolling(window=10).mean().iloc[i]
                    if not pd.isna(avg_volume) and avg_volume > 0:
                        volume_ratio = row['volume'] / avg_volume
                        volume_bonus = min((volume_ratio - 1) * 10, 10)
                
                confidence = min(int(base_confidence + momentum_bonus + price_alignment + volume_bonus), 90)
                
                reason = f"RSI overbought breakout - RSI: {row['rsi']:.1f}, Momentum: {row['rsi_momentum']:.1f}"
            
            # Check for extreme RSI levels (additional signals)
            elif row['rsi'] < 20 and row['rsi_momentum'] > 2:
                action = 'BUY'
                confidence = min(self.parameters['min_confidence'] + 10, 85)
                reason = f"RSI extremely oversold reversal - RSI: {row['rsi']:.1f}"
            
            elif row['rsi'] > 80 and row['rsi_momentum'] < -2:
                action = 'SELL'
                confidence = min(self.parameters['min_confidence'] + 10, 85)
                reason = f"RSI extremely overbought reversal - RSI: {row['rsi']:.1f}"
            
            # Only add signals with meaningful actions or at key points
            if action != 'HOLD' or i == len(df) - 1:
                signals.append({
                    'timestamp': timestamp,
                    'action': action,
                    'price': float(row['close']),
                    'confidence': confidence,
                    'reason': reason,
                    'rsi': float(row['rsi']),
                    'rsi_momentum': float(row['rsi_momentum']) if not pd.isna(row['rsi_momentum']) else 0
                })
        
        return signals