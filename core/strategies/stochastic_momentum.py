"""
Stochastic Momentum Strategy
Uses Stochastic oscillator for momentum-based entry and exit signals
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List
from .base_strategy import BaseStrategy

class Strategy(BaseStrategy):
    """Stochastic Momentum Strategy"""
    
    def __init__(self):
        super().__init__("Stochastic Momentum")
        self.parameters = {
            'k_period': 14,
            'd_period': 3,
            'overbought_level': 80,
            'oversold_level': 20,
            'momentum_period': 5,
            'min_confidence': 68
        }
    
    def calculate_stochastic(self, data: pd.DataFrame) -> Dict[str, pd.Series]:
        """Calculate Stochastic %K and %D"""
        high_period = data['high'].rolling(window=self.parameters['k_period'])
        low_period = data['low'].rolling(window=self.parameters['k_period'])
        
        # %K calculation
        lowest_low = low_period.min()
        highest_high = high_period.max()
        
        k_percent = 100 * ((data['close'] - lowest_low) / (highest_high - lowest_low))
        
        # %D calculation (smoothed %K)
        d_percent = k_percent.rolling(window=self.parameters['d_period']).mean()
        
        return {
            'stoch_k': k_percent,
            'stoch_d': d_percent
        }
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate Stochastic and momentum indicators"""
        df = data.copy()
        
        # Calculate Stochastic
        stoch_data = self.calculate_stochastic(df)
        df['stoch_k'] = stoch_data['stoch_k']
        df['stoch_d'] = stoch_data['stoch_d']
        
        # Previous values for crossover detection
        df['stoch_k_prev'] = df['stoch_k'].shift(1)
        df['stoch_d_prev'] = df['stoch_d'].shift(1)
        
        # Crossover signals
        df['bullish_cross'] = (
            (df['stoch_k'] > df['stoch_d']) & 
            (df['stoch_k_prev'] <= df['stoch_d_prev'])
        )
        
        df['bearish_cross'] = (
            (df['stoch_k'] < df['stoch_d']) & 
            (df['stoch_k_prev'] >= df['stoch_d_prev'])
        )
        
        # Overbought/Oversold conditions
        df['is_oversold'] = (df['stoch_k'] < self.parameters['oversold_level']) & (df['stoch_d'] < self.parameters['oversold_level'])
        df['is_overbought'] = (df['stoch_k'] > self.parameters['overbought_level']) & (df['stoch_d'] > self.parameters['overbought_level'])
        
        # Momentum confirmation
        df['price_momentum'] = df['close'].pct_change(self.parameters['momentum_period'])
        df['stoch_momentum'] = df['stoch_k'] - df['stoch_k'].shift(self.parameters['momentum_period'])
        
        # Divergence detection (simplified)
        price_highs = df['close'].rolling(window=10).max()
        price_lows = df['close'].rolling(window=10).min()
        stoch_highs = df['stoch_k'].rolling(window=10).max()
        stoch_lows = df['stoch_k'].rolling(window=10).min()
        
        df['bullish_divergence'] = (
            (df['close'] == price_lows) & 
            (df['stoch_k'] > stoch_lows.shift(1)) &
            (df['stoch_k'] < self.parameters['oversold_level'] + 10)
        )
        
        df['bearish_divergence'] = (
            (df['close'] == price_highs) & 
            (df['stoch_k'] < stoch_highs.shift(1)) &
            (df['stoch_k'] > self.parameters['overbought_level'] - 10)
        )
        
        return df
    
    def generate_signals(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Generate Stochastic momentum signals"""
        if not self.validate_data(data):
            return []
        
        df = self.calculate_indicators(data)
        signals = []
        
        for i, row in df.iterrows():
            timestamp = row.get('timestamp', i)
            
            # Skip if we don't have enough data
            if pd.isna(row['stoch_k']) or pd.isna(row['stoch_d']):
                continue
            
            action = 'HOLD'
            confidence = 50
            reason = "No clear stochastic signal"
            
            # Priority 1: Divergence signals (strongest)
            if row['bullish_divergence']:
                action = 'BUY'
                confidence = min(self.parameters['min_confidence'] + 15, 90)
                reason = f"Bullish stochastic divergence - %K: {row['stoch_k']:.1f}, %D: {row['stoch_d']:.1f}"
            
            elif row['bearish_divergence']:
                action = 'SELL'
                confidence = min(self.parameters['min_confidence'] + 15, 90)
                reason = f"Bearish stochastic divergence - %K: {row['stoch_k']:.1f}, %D: {row['stoch_d']:.1f}"
            
            # Priority 2: Crossover in oversold/overbought zones
            elif row['bullish_cross'] and row['stoch_k'] < self.parameters['oversold_level'] + 15:
                action = 'BUY'
                base_confidence = self.parameters['min_confidence']
                
                # Momentum confirmation
                momentum_bonus = 0
                if not pd.isna(row['price_momentum']) and row['price_momentum'] > 0:
                    momentum_bonus = min(row['price_momentum'] * 500, 10)
                
                # Stochastic momentum bonus
                stoch_momentum_bonus = 0
                if not pd.isna(row['stoch_momentum']) and row['stoch_momentum'] > 0:
                    stoch_momentum_bonus = min(row['stoch_momentum'] * 0.2, 8)
                
                # Volume confirmation
                volume_bonus = 0
                if 'volume' in row and not pd.isna(row['volume']):
                    avg_volume = df['volume'].rolling(window=20).mean().iloc[i]
                    if not pd.isna(avg_volume) and avg_volume > 0:
                        volume_ratio = row['volume'] / avg_volume
                        volume_bonus = min((volume_ratio - 1) * 8, 10)
                
                confidence = min(int(base_confidence + momentum_bonus + stoch_momentum_bonus + volume_bonus), 90)
                reason = f"Bullish stochastic crossover in oversold zone - %K: {row['stoch_k']:.1f}, %D: {row['stoch_d']:.1f}"
            
            elif row['bearish_cross'] and row['stoch_k'] > self.parameters['overbought_level'] - 15:
                action = 'SELL'
                base_confidence = self.parameters['min_confidence']
                
                # Momentum confirmation
                momentum_bonus = 0
                if not pd.isna(row['price_momentum']) and row['price_momentum'] < 0:
                    momentum_bonus = min(abs(row['price_momentum']) * 500, 10)
                
                # Stochastic momentum bonus
                stoch_momentum_bonus = 0
                if not pd.isna(row['stoch_momentum']) and row['stoch_momentum'] < 0:
                    stoch_momentum_bonus = min(abs(row['stoch_momentum']) * 0.2, 8)
                
                # Volume confirmation
                volume_bonus = 0
                if 'volume' in row and not pd.isna(row['volume']):
                    avg_volume = df['volume'].rolling(window=20).mean().iloc[i]
                    if not pd.isna(avg_volume) and avg_volume > 0:
                        volume_ratio = row['volume'] / avg_volume
                        volume_bonus = min((volume_ratio - 1) * 8, 10)
                
                confidence = min(int(base_confidence + momentum_bonus + stoch_momentum_bonus + volume_bonus), 90)
                reason = f"Bearish stochastic crossover in overbought zone - %K: {row['stoch_k']:.1f}, %D: {row['stoch_d']:.1f}"
            
            # Priority 3: Exit from extreme zones
            elif row['stoch_k'] > self.parameters['overbought_level'] and row['stoch_k_prev'] <= self.parameters['overbought_level']:
                action = 'SELL'
                confidence = self.parameters['min_confidence'] - 10
                reason = f"Stochastic entering overbought zone - %K: {row['stoch_k']:.1f}"
            
            elif row['stoch_k'] < self.parameters['oversold_level'] and row['stoch_k_prev'] >= self.parameters['oversold_level']:
                action = 'BUY'
                confidence = self.parameters['min_confidence'] - 10
                reason = f"Stochastic entering oversold zone - %K: {row['stoch_k']:.1f}"
            
            # Only add signals with meaningful actions or at key points
            if action != 'HOLD' or i == len(df) - 1:
                signals.append({
                    'timestamp': timestamp,
                    'action': action,
                    'price': float(row['close']),
                    'confidence': confidence,
                    'reason': reason,
                    'stoch_k': float(row['stoch_k']) if not pd.isna(row['stoch_k']) else 50,
                    'stoch_d': float(row['stoch_d']) if not pd.isna(row['stoch_d']) else 50,
                    'is_oversold': bool(row['is_oversold']),
                    'is_overbought': bool(row['is_overbought'])
                })
        
        return signals