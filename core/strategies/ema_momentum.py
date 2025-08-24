"""
EMA Momentum Strategy
Uses multiple EMAs with momentum confirmation for trend-following signals
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List
from .base_strategy import BaseStrategy

class Strategy(BaseStrategy):
    """EMA Momentum Strategy"""
    
    def __init__(self):
        super().__init__("EMA Momentum")
        self.parameters = {
            'fast_ema': 8,
            'medium_ema': 21,
            'slow_ema': 55,
            'momentum_period': 10,
            'volume_period': 20,
            'min_confidence': 73
        }
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate EMA and momentum indicators"""
        df = data.copy()
        
        # Calculate EMAs
        df['ema_fast'] = df['close'].ewm(span=self.parameters['fast_ema']).mean()
        df['ema_medium'] = df['close'].ewm(span=self.parameters['medium_ema']).mean()
        df['ema_slow'] = df['close'].ewm(span=self.parameters['slow_ema']).mean()
        
        # EMA alignment (all EMAs in order)
        df['bullish_alignment'] = (df['ema_fast'] > df['ema_medium']) & (df['ema_medium'] > df['ema_slow'])
        df['bearish_alignment'] = (df['ema_fast'] < df['ema_medium']) & (df['ema_medium'] < df['ema_slow'])
        
        # Previous values for crossover detection
        df['ema_fast_prev'] = df['ema_fast'].shift(1)
        df['ema_medium_prev'] = df['ema_medium'].shift(1)
        
        # EMA crossovers
        df['fast_medium_bull_cross'] = (
            (df['ema_fast'] > df['ema_medium']) & 
            (df['ema_fast_prev'] <= df['ema_medium_prev'])
        )
        
        df['fast_medium_bear_cross'] = (
            (df['ema_fast'] < df['ema_medium']) & 
            (df['ema_fast_prev'] >= df['ema_medium_prev'])
        )
        
        # Price vs EMA signals
        df['price_above_fast'] = df['close'] > df['ema_fast']
        df['price_above_medium'] = df['close'] > df['ema_medium']
        df['price_above_slow'] = df['close'] > df['ema_slow']
        
        # Momentum calculations
        df['price_momentum'] = df['close'].pct_change(self.parameters['momentum_period'])
        df['ema_fast_momentum'] = df['ema_fast'].pct_change(self.parameters['momentum_period'])
        df['ema_slope'] = (df['ema_medium'] - df['ema_medium'].shift(5)) / df['ema_medium'].shift(5)
        
        # Distance between EMAs (trend strength)
        df['ema_spread'] = (df['ema_fast'] - df['ema_slow']) / df['ema_slow']
        df['ema_spread_normalized'] = abs(df['ema_spread'])
        
        # Volume analysis
        if 'volume' in df.columns:
            df['volume_sma'] = df['volume'].rolling(window=self.parameters['volume_period']).mean()
            df['volume_ratio'] = df['volume'] / df['volume_sma']
        else:
            df['volume_ratio'] = 1.0
        
        # Pullback opportunities
        df['pullback_to_fast'] = (
            df['bullish_alignment'] & 
            (df['close'] <= df['ema_fast']) & 
            (df['close'].shift(1) > df['ema_fast'].shift(1))
        )
        
        df['pullback_from_fast'] = (
            df['bearish_alignment'] & 
            (df['close'] >= df['ema_fast']) & 
            (df['close'].shift(1) < df['ema_fast'].shift(1))
        )
        
        return df
    
    def generate_signals(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Generate EMA momentum signals"""
        if not self.validate_data(data):
            return []
        
        df = self.calculate_indicators(data)
        signals = []
        
        for i, row in df.iterrows():
            timestamp = row.get('timestamp', i)
            
            # Skip if we don't have enough data
            if pd.isna(row['ema_fast']) or pd.isna(row['ema_medium']) or pd.isna(row['ema_slow']):
                continue
            
            action = 'HOLD'
            confidence = 50
            reason = "No clear EMA signal"
            
            # Priority 1: EMA crossover with alignment
            if row['fast_medium_bull_cross'] and row['bullish_alignment']:
                action = 'BUY'
                base_confidence = self.parameters['min_confidence']
                
                # Momentum confirmation
                momentum_bonus = 0
                if not pd.isna(row['price_momentum']) and row['price_momentum'] > 0:
                    momentum_bonus = min(row['price_momentum'] * 300, 12)
                
                # EMA slope bonus
                slope_bonus = 0
                if not pd.isna(row['ema_slope']) and row['ema_slope'] > 0:
                    slope_bonus = min(row['ema_slope'] * 1000, 8)
                
                # Volume confirmation
                volume_bonus = 0
                if not pd.isna(row['volume_ratio']) and row['volume_ratio'] > 1.2:
                    volume_bonus = min((row['volume_ratio'] - 1) * 10, 10)
                
                confidence = min(int(base_confidence + momentum_bonus + slope_bonus + volume_bonus), 95)
                reason = f"Bullish EMA crossover with alignment - Fast: {row['ema_fast']:.2f}, Medium: {row['ema_medium']:.2f}"
            
            elif row['fast_medium_bear_cross'] and row['bearish_alignment']:
                action = 'SELL'
                base_confidence = self.parameters['min_confidence']
                
                # Momentum confirmation
                momentum_bonus = 0
                if not pd.isna(row['price_momentum']) and row['price_momentum'] < 0:
                    momentum_bonus = min(abs(row['price_momentum']) * 300, 12)
                
                # EMA slope bonus
                slope_bonus = 0
                if not pd.isna(row['ema_slope']) and row['ema_slope'] < 0:
                    slope_bonus = min(abs(row['ema_slope']) * 1000, 8)
                
                # Volume confirmation
                volume_bonus = 0
                if not pd.isna(row['volume_ratio']) and row['volume_ratio'] > 1.2:
                    volume_bonus = min((row['volume_ratio'] - 1) * 10, 10)
                
                confidence = min(int(base_confidence + momentum_bonus + slope_bonus + volume_bonus), 95)
                reason = f"Bearish EMA crossover with alignment - Fast: {row['ema_fast']:.2f}, Medium: {row['ema_medium']:.2f}"
            
            # Priority 2: Pullback opportunities in trending market
            elif row['pullback_to_fast']:
                action = 'BUY'
                base_confidence = self.parameters['min_confidence'] - 10
                
                # Trend strength bonus
                trend_bonus = 0
                if not pd.isna(row['ema_spread_normalized']):
                    trend_bonus = min(row['ema_spread_normalized'] * 100, 10)
                
                # Volume on pullback (lower volume is better for pullback)
                volume_bonus = 0
                if not pd.isna(row['volume_ratio']) and row['volume_ratio'] < 0.8:
                    volume_bonus = 5
                
                confidence = min(int(base_confidence + trend_bonus + volume_bonus), 85)
                reason = f"Bullish pullback to EMA in uptrend - Price: {row['close']:.2f}, Fast EMA: {row['ema_fast']:.2f}"
            
            elif row['pullback_from_fast']:
                action = 'SELL'
                base_confidence = self.parameters['min_confidence'] - 10
                
                # Trend strength bonus
                trend_bonus = 0
                if not pd.isna(row['ema_spread_normalized']):
                    trend_bonus = min(row['ema_spread_normalized'] * 100, 10)
                
                # Volume on pullback
                volume_bonus = 0
                if not pd.isna(row['volume_ratio']) and row['volume_ratio'] < 0.8:
                    volume_bonus = 5
                
                confidence = min(int(base_confidence + trend_bonus + volume_bonus), 85)
                reason = f"Bearish pullback from EMA in downtrend - Price: {row['close']:.2f}, Fast EMA: {row['ema_fast']:.2f}"
            
            # Priority 3: Strong momentum with EMA support
            elif (row['price_above_fast'] and row['price_above_medium'] and 
                  not pd.isna(row['price_momentum']) and row['price_momentum'] > 0.02):
                action = 'BUY'
                confidence = self.parameters['min_confidence'] - 15
                reason = f"Strong bullish momentum above EMAs - Momentum: {row['price_momentum']*100:.1f}%"
            
            elif (not row['price_above_fast'] and not row['price_above_medium'] and 
                  not pd.isna(row['price_momentum']) and row['price_momentum'] < -0.02):
                action = 'SELL'
                confidence = self.parameters['min_confidence'] - 15
                reason = f"Strong bearish momentum below EMAs - Momentum: {row['price_momentum']*100:.1f}%"
            
            # Only add signals with meaningful actions or at key points
            if action != 'HOLD' or i == len(df) - 1:
                signals.append({
                    'timestamp': timestamp,
                    'action': action,
                    'price': float(row['close']),
                    'confidence': confidence,
                    'reason': reason,
                    'ema_fast': float(row['ema_fast']) if not pd.isna(row['ema_fast']) else 0,
                    'ema_medium': float(row['ema_medium']) if not pd.isna(row['ema_medium']) else 0,
                    'ema_slow': float(row['ema_slow']) if not pd.isna(row['ema_slow']) else 0,
                    'bullish_alignment': bool(row['bullish_alignment']),
                    'bearish_alignment': bool(row['bearish_alignment'])
                })
        
        return signals