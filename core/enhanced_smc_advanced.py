"""
Enhanced SMC Analysis with CHoCH, FVG, and Liquidity Sweeps
Advanced Smart Money Concepts for professional trading
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class EnhancedSMCAdvanced:
    """
    Advanced SMC Analysis including:
    - CHoCH (Change of Character)
    - Fair Value Gaps (FVG)
    - Liquidity Sweeps
    - Equal Highs/Lows
    - Breaker Blocks
    - Mitigation Blocks
    """
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.EnhancedSMCAdvanced")
        self.min_fvg_size_pct = 0.1  # Minimum FVG size as % of price
        self.liquidity_threshold = 0.05  # 0.05% for equal highs/lows
        self.logger.info("🚀 Enhanced SMC Advanced initialized with CHoCH, FVG, Liquidity analysis")
    
    def analyze_complete_smc(self, df: pd.DataFrame, symbol: str = "BTC-USDT") -> Dict[str, Any]:
        """
        Complete SMC analysis with all advanced features
        """
        try:
            if df is None or len(df) < 50:
                return self._get_empty_analysis()
            
            # Ensure numeric types
            for col in ['open', 'high', 'low', 'close', 'volume']:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Find swing points first (crucial for all SMC analysis)
            swing_highs, swing_lows = self._identify_swing_points(df)
            
            # Core SMC analysis
            choch_analysis = self._detect_choch(df, swing_highs, swing_lows)
            fvg_zones = self._identify_fair_value_gaps(df)
            liquidity_sweeps = self._detect_liquidity_sweeps(df, swing_highs, swing_lows)
            order_blocks = self._identify_order_blocks_advanced(df)
            breaker_blocks = self._identify_breaker_blocks(df, order_blocks)
            
            # Market structure
            market_structure = self._analyze_market_structure(df, swing_highs, swing_lows, choch_analysis)
            
            # Calculate confidence based on confluence
            confidence = self._calculate_smc_confidence(
                choch_analysis, fvg_zones, liquidity_sweeps, order_blocks, market_structure
            )
            
            return {
                'symbol': symbol,
                'market_structure': market_structure,
                'choch': choch_analysis,
                'fair_value_gaps': fvg_zones,
                'liquidity_sweeps': liquidity_sweeps,
                'order_blocks': order_blocks[:5],  # Top 5 most recent
                'breaker_blocks': breaker_blocks[:3],  # Top 3 most recent
                'swing_points': {
                    'highs': swing_highs[-5:] if swing_highs else [],
                    'lows': swing_lows[-5:] if swing_lows else []
                },
                'confidence': confidence,
                'recommendation': self._generate_smc_recommendation(
                    market_structure, choch_analysis, fvg_zones, confidence
                ),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Enhanced SMC analysis error: {e}")
            return self._get_empty_analysis()
    
    def _identify_swing_points(self, df: pd.DataFrame, lookback: int = 5) -> Tuple[List[Dict], List[Dict]]:
        """
        Identify swing highs and swing lows for structure analysis
        """
        swing_highs = []
        swing_lows = []
        
        try:
            highs = df['high'].values
            lows = df['low'].values
            
            for i in range(lookback, len(df) - lookback):
                # Swing High: highest point in range
                if highs[i] == max(highs[i-lookback:i+lookback+1]):
                    swing_highs.append({
                        'index': i,
                        'price': float(highs[i]),
                        'timestamp': df.index[i] if hasattr(df.index[i], 'isoformat') else i
                    })
                
                # Swing Low: lowest point in range
                if lows[i] == min(lows[i-lookback:i+lookback+1]):
                    swing_lows.append({
                        'index': i,
                        'price': float(lows[i]),
                        'timestamp': df.index[i] if hasattr(df.index[i], 'isoformat') else i
                    })
            
            return swing_highs, swing_lows
            
        except Exception as e:
            self.logger.error(f"Swing point identification error: {e}")
            return [], []
    
    def _detect_choch(self, df: pd.DataFrame, swing_highs: List[Dict], swing_lows: List[Dict]) -> Dict[str, Any]:
        """
        Detect Change of Character (CHoCH) - when market structure changes
        CHoCH occurs when:
        - In uptrend: price breaks below previous higher low
        - In downtrend: price breaks above previous lower high
        """
        try:
            if len(swing_highs) < 3 or len(swing_lows) < 3:
                return {'detected': False, 'type': None}
            
            current_price = float(df['close'].iloc[-1])
            
            # Check last 3 swing highs and lows for trend
            recent_highs = [sh['price'] for sh in swing_highs[-3:]]
            recent_lows = [sl['price'] for sl in swing_lows[-3:]]
            
            # Detect uptrend: higher highs and higher lows
            is_uptrend = (
                len(recent_highs) >= 2 and recent_highs[-1] > recent_highs[-2] and
                len(recent_lows) >= 2 and recent_lows[-1] > recent_lows[-2]
            )
            
            # Detect downtrend: lower highs and lower lows
            is_downtrend = (
                len(recent_highs) >= 2 and recent_highs[-1] < recent_highs[-2] and
                len(recent_lows) >= 2 and recent_lows[-1] < recent_lows[-2]
            )
            
            choch_detected = False
            choch_type = None
            choch_level = None
            
            # CHoCH in uptrend (bearish reversal)
            if is_uptrend and len(recent_lows) >= 2:
                previous_higher_low = recent_lows[-2]
                if current_price < previous_higher_low:
                    choch_detected = True
                    choch_type = 'BEARISH_CHOCH'
                    choch_level = previous_higher_low
            
            # CHoCH in downtrend (bullish reversal)
            elif is_downtrend and len(recent_highs) >= 2:
                previous_lower_high = recent_highs[-2]
                if current_price > previous_lower_high:
                    choch_detected = True
                    choch_type = 'BULLISH_CHOCH'
                    choch_level = previous_lower_high
            
            return {
                'detected': choch_detected,
                'type': choch_type,
                'level': choch_level,
                'current_trend': 'UPTREND' if is_uptrend else 'DOWNTREND' if is_downtrend else 'RANGING',
                'strength': 'HIGH' if choch_detected else 'LOW',
                'description': f"{choch_type} detected at {choch_level:.2f}" if choch_detected else "No CHoCH detected"
            }
            
        except Exception as e:
            self.logger.error(f"CHoCH detection error: {e}")
            return {'detected': False, 'type': None}
    
    def _identify_fair_value_gaps(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Identify Fair Value Gaps (FVG) - price inefficiencies
        FVG occurs when there's a gap between candles that price often returns to fill
        """
        fvg_zones = []
        
        try:
            for i in range(2, len(df) - 1):
                prev_candle = df.iloc[i-1]
                curr_candle = df.iloc[i]
                next_candle = df.iloc[i+1]
                
                # Bullish FVG: gap up
                if prev_candle['high'] < next_candle['low']:
                    gap_size = next_candle['low'] - prev_candle['high']
                    gap_pct = (gap_size / prev_candle['close']) * 100
                    
                    if gap_pct >= self.min_fvg_size_pct:
                        fvg_zones.append({
                            'type': 'BULLISH_FVG',
                            'top': float(next_candle['low']),
                            'bottom': float(prev_candle['high']),
                            'size': float(gap_size),
                            'size_pct': float(gap_pct),
                            'index': i,
                            'filled': False,
                            'strength': 'HIGH' if gap_pct > 0.3 else 'MEDIUM' if gap_pct > 0.15 else 'LOW'
                        })
                
                # Bearish FVG: gap down
                elif prev_candle['low'] > next_candle['high']:
                    gap_size = prev_candle['low'] - next_candle['high']
                    gap_pct = (gap_size / prev_candle['close']) * 100
                    
                    if gap_pct >= self.min_fvg_size_pct:
                        fvg_zones.append({
                            'type': 'BEARISH_FVG',
                            'top': float(prev_candle['low']),
                            'bottom': float(next_candle['high']),
                            'size': float(gap_size),
                            'size_pct': float(gap_pct),
                            'index': i,
                            'filled': False,
                            'strength': 'HIGH' if gap_pct > 0.3 else 'MEDIUM' if gap_pct > 0.15 else 'LOW'
                        })
            
            # Check if FVGs have been filled
            current_price = float(df['close'].iloc[-1])
            for fvg in fvg_zones:
                if fvg['type'] == 'BULLISH_FVG':
                    fvg['filled'] = current_price <= fvg['top']
                else:
                    fvg['filled'] = current_price >= fvg['bottom']
            
            # Return unfilled FVGs (these are tradeable)
            unfilled_fvgs = [fvg for fvg in fvg_zones if not fvg['filled']]
            return sorted(unfilled_fvgs, key=lambda x: x['size_pct'], reverse=True)[:5]
            
        except Exception as e:
            self.logger.error(f"FVG identification error: {e}")
            return []
    
    def _detect_liquidity_sweeps(self, df: pd.DataFrame, swing_highs: List[Dict], swing_lows: List[Dict]) -> Dict[str, Any]:
        """
        Detect liquidity sweeps and equal highs/lows
        Smart money often sweeps liquidity at obvious levels before reversing
        """
        try:
            liquidity_analysis = {
                'sweep_detected': False,
                'sweep_type': None,
                'equal_highs': [],
                'equal_lows': [],
                'liquidity_zones': []
            }
            
            current_price = float(df['close'].iloc[-1])
            recent_high = float(df['high'].iloc[-5:].max())
            recent_low = float(df['low'].iloc[-5:].min())
            
            # Find equal highs (liquidity above)
            if swing_highs:
                high_prices = [sh['price'] for sh in swing_highs]
                for i, price1 in enumerate(high_prices):
                    for price2 in high_prices[i+1:]:
                        if abs(price1 - price2) / price1 < self.liquidity_threshold:
                            liquidity_analysis['equal_highs'].append({
                                'level': float((price1 + price2) / 2),
                                'strength': 'HIGH',
                                'touched_count': 2
                            })
            
            # Find equal lows (liquidity below)
            if swing_lows:
                low_prices = [sl['price'] for sl in swing_lows]
                for i, price1 in enumerate(low_prices):
                    for price2 in low_prices[i+1:]:
                        if abs(price1 - price2) / price1 < self.liquidity_threshold:
                            liquidity_analysis['equal_lows'].append({
                                'level': float((price1 + price2) / 2),
                                'strength': 'HIGH',
                                'touched_count': 2
                            })
            
            # Detect sweep: price briefly exceeds level then reverses
            if swing_highs and len(df) > 10:
                last_swing_high = swing_highs[-1]['price']
                # Check if we swept above and reversed
                if recent_high > last_swing_high * 1.001 and current_price < last_swing_high:
                    liquidity_analysis['sweep_detected'] = True
                    liquidity_analysis['sweep_type'] = 'BEARISH_SWEEP'
                    liquidity_analysis['sweep_level'] = last_swing_high
            
            if swing_lows and len(df) > 10:
                last_swing_low = swing_lows[-1]['price']
                # Check if we swept below and reversed
                if recent_low < last_swing_low * 0.999 and current_price > last_swing_low:
                    liquidity_analysis['sweep_detected'] = True
                    liquidity_analysis['sweep_type'] = 'BULLISH_SWEEP'
                    liquidity_analysis['sweep_level'] = last_swing_low
            
            return liquidity_analysis
            
        except Exception as e:
            self.logger.error(f"Liquidity sweep detection error: {e}")
            return {'sweep_detected': False, 'sweep_type': None}
    
    def _identify_order_blocks_advanced(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Identify order blocks with advanced criteria
        Order blocks are the last opposite candle before a strong move
        """
        order_blocks = []
        
        try:
            for i in range(10, len(df) - 5):
                # Look for strong moves
                move_size = abs(df.iloc[i+1:i+4]['close'].pct_change().sum())
                
                if move_size > 0.02:  # 2% move threshold
                    candle = df.iloc[i]
                    next_candles = df.iloc[i+1:i+4]
                    
                    # Bullish order block: last bearish candle before up move
                    if (candle['close'] < candle['open'] and 
                        next_candles['close'].iloc[-1] > next_candles['close'].iloc[0]):
                        
                        order_blocks.append({
                            'type': 'BULLISH_OB',
                            'top': float(candle['high']),
                            'bottom': float(candle['low']),
                            'mid': float((candle['high'] + candle['low']) / 2),
                            'index': i,
                            'strength': 'HIGH' if move_size > 0.03 else 'MEDIUM',
                            'volume_ratio': float(candle['volume'] / df['volume'].iloc[i-20:i].mean()),
                            'tested': False
                        })
                    
                    # Bearish order block: last bullish candle before down move
                    elif (candle['close'] > candle['open'] and 
                          next_candles['close'].iloc[-1] < next_candles['close'].iloc[0]):
                        
                        order_blocks.append({
                            'type': 'BEARISH_OB',
                            'top': float(candle['high']),
                            'bottom': float(candle['low']),
                            'mid': float((candle['high'] + candle['low']) / 2),
                            'index': i,
                            'strength': 'HIGH' if move_size > 0.03 else 'MEDIUM',
                            'volume_ratio': float(candle['volume'] / df['volume'].iloc[i-20:i].mean()),
                            'tested': False
                        })
            
            # Check if order blocks have been tested
            current_price = float(df['close'].iloc[-1])
            for ob in order_blocks:
                if ob['type'] == 'BULLISH_OB':
                    ob['tested'] = current_price <= ob['top'] and current_price >= ob['bottom']
                else:
                    ob['tested'] = current_price >= ob['bottom'] and current_price <= ob['top']
            
            # Sort by strength and recency
            return sorted(order_blocks, key=lambda x: (x['strength'] == 'HIGH', -x['index']))[:10]
            
        except Exception as e:
            self.logger.error(f"Order block identification error: {e}")
            return []
    
    def _identify_breaker_blocks(self, df: pd.DataFrame, order_blocks: List[Dict]) -> List[Dict[str, Any]]:
        """
        Identify breaker blocks (failed order blocks that become resistance/support)
        """
        breaker_blocks = []
        
        try:
            current_price = float(df['close'].iloc[-1])
            
            for ob in order_blocks:
                if ob['index'] < len(df) - 10:  # Need some candles after OB
                    price_after = df['close'].iloc[ob['index']+1:].values
                    
                    # Bullish OB becomes bearish breaker if broken down
                    if ob['type'] == 'BULLISH_OB':
                        if any(price_after < ob['bottom']):
                            breaker_blocks.append({
                                'type': 'BEARISH_BREAKER',
                                'level': ob['mid'],
                                'top': ob['top'],
                                'bottom': ob['bottom'],
                                'strength': ob['strength'],
                                'active': current_price < ob['top']
                            })
                    
                    # Bearish OB becomes bullish breaker if broken up
                    elif ob['type'] == 'BEARISH_OB':
                        if any(price_after > ob['top']):
                            breaker_blocks.append({
                                'type': 'BULLISH_BREAKER',
                                'level': ob['mid'],
                                'top': ob['top'],
                                'bottom': ob['bottom'],
                                'strength': ob['strength'],
                                'active': current_price > ob['bottom']
                            })
            
            return breaker_blocks
            
        except Exception as e:
            self.logger.error(f"Breaker block identification error: {e}")
            return []
    
    def _analyze_market_structure(self, df: pd.DataFrame, swing_highs: List[Dict], 
                                  swing_lows: List[Dict], choch: Dict) -> Dict[str, Any]:
        """
        Comprehensive market structure analysis
        """
        try:
            current_price = float(df['close'].iloc[-1])
            
            # Determine trend based on swing points
            trend = 'RANGING'
            if len(swing_highs) >= 2 and len(swing_lows) >= 2:
                if (swing_highs[-1]['price'] > swing_highs[-2]['price'] and 
                    swing_lows[-1]['price'] > swing_lows[-2]['price']):
                    trend = 'BULLISH'
                elif (swing_highs[-1]['price'] < swing_highs[-2]['price'] and 
                      swing_lows[-1]['price'] < swing_lows[-2]['price']):
                    trend = 'BEARISH'
            
            # Structure break analysis
            structure_break = 'NONE'
            if swing_highs and current_price > swing_highs[-1]['price']:
                structure_break = 'BOS_UP'  # Break of Structure Up
            elif swing_lows and current_price < swing_lows[-1]['price']:
                structure_break = 'BOS_DOWN'  # Break of Structure Down
            
            # If CHoCH detected, override structure
            if choch['detected']:
                structure_break = 'CHOCH'
                if choch['type'] == 'BULLISH_CHOCH':
                    trend = 'BULLISH_REVERSAL'
                elif choch['type'] == 'BEARISH_CHOCH':
                    trend = 'BEARISH_REVERSAL'
            
            return {
                'trend': trend,
                'structure_break': structure_break,
                'last_swing_high': swing_highs[-1]['price'] if swing_highs else None,
                'last_swing_low': swing_lows[-1]['price'] if swing_lows else None,
                'current_price': current_price,
                'position_in_range': self._calculate_position_in_range(
                    current_price, 
                    swing_highs[-1]['price'] if swing_highs else current_price * 1.05,
                    swing_lows[-1]['price'] if swing_lows else current_price * 0.95
                )
            }
            
        except Exception as e:
            self.logger.error(f"Market structure analysis error: {e}")
            return {'trend': 'UNKNOWN', 'structure_break': 'NONE'}
    
    def _calculate_position_in_range(self, price: float, high: float, low: float) -> float:
        """Calculate where price is within range (0-100)"""
        if high == low:
            return 50.0
        return ((price - low) / (high - low)) * 100
    
    def _calculate_smc_confidence(self, choch: Dict, fvg_zones: List, 
                                  liquidity: Dict, order_blocks: List,
                                  market_structure: Dict) -> Dict[str, Any]:
        """
        Calculate confidence score based on SMC confluence
        """
        score = 50  # Base score
        factors = []
        
        # CHoCH detected (+20 points)
        if choch['detected']:
            score += 20
            factors.append(f"{choch['type']} detected")
        
        # FVG zones available (+10 per zone, max 20)
        if fvg_zones:
            fvg_points = min(len(fvg_zones) * 10, 20)
            score += fvg_points
            factors.append(f"{len(fvg_zones)} FVG zones identified")
        
        # Liquidity sweep detected (+15 points)
        if liquidity['sweep_detected']:
            score += 15
            factors.append(f"{liquidity['sweep_type']} detected")
        
        # Strong order blocks (+10 points)
        strong_obs = [ob for ob in order_blocks if ob.get('strength') == 'HIGH']
        if strong_obs:
            score += 10
            factors.append(f"{len(strong_obs)} strong order blocks")
        
        # Structure break (+10 points)
        if market_structure['structure_break'] in ['BOS_UP', 'BOS_DOWN', 'CHOCH']:
            score += 10
            factors.append(f"Structure break: {market_structure['structure_break']}")
        
        # Cap at 95
        score = min(score, 95)
        
        return {
            'score': score,
            'level': 'HIGH' if score >= 75 else 'MEDIUM' if score >= 60 else 'LOW',
            'factors': factors
        }
    
    def _generate_smc_recommendation(self, market_structure: Dict, choch: Dict, 
                                     fvg_zones: List, confidence: Dict) -> Dict[str, Any]:
        """
        Generate trading recommendation based on SMC analysis
        """
        action = 'HOLD'
        reasoning = []
        
        # Strong bullish signals
        if (market_structure['trend'] in ['BULLISH', 'BULLISH_REVERSAL'] and 
            confidence['score'] >= 70):
            action = 'BUY'
            reasoning.append("Bullish market structure")
            if choch['type'] == 'BULLISH_CHOCH':
                reasoning.append("Bullish CHoCH confirmed")
            if any(fvg['type'] == 'BULLISH_FVG' for fvg in fvg_zones):
                reasoning.append("Bullish FVG for entry")
        
        # Strong bearish signals
        elif (market_structure['trend'] in ['BEARISH', 'BEARISH_REVERSAL'] and 
              confidence['score'] >= 70):
            action = 'SELL'
            reasoning.append("Bearish market structure")
            if choch['type'] == 'BEARISH_CHOCH':
                reasoning.append("Bearish CHoCH confirmed")
            if any(fvg['type'] == 'BEARISH_FVG' for fvg in fvg_zones):
                reasoning.append("Bearish FVG for entry")
        
        # Neutral/ranging conditions
        else:
            reasoning.append("Insufficient confluence for directional trade")
            if market_structure['trend'] == 'RANGING':
                reasoning.append("Market is ranging")
        
        return {
            'action': action,
            'confidence': confidence['score'],
            'reasoning': reasoning,
            'risk_level': 'LOW' if confidence['score'] >= 75 else 'MEDIUM' if confidence['score'] >= 60 else 'HIGH'
        }
    
    def _get_empty_analysis(self) -> Dict[str, Any]:
        """Return empty analysis structure"""
        return {
            'symbol': 'UNKNOWN',
            'market_structure': {'trend': 'UNKNOWN', 'structure_break': 'NONE'},
            'choch': {'detected': False, 'type': None},
            'fair_value_gaps': [],
            'liquidity_sweeps': {'sweep_detected': False, 'sweep_type': None},
            'order_blocks': [],
            'breaker_blocks': [],
            'swing_points': {'highs': [], 'lows': []},
            'confidence': {'score': 50, 'level': 'LOW', 'factors': []},
            'recommendation': {'action': 'HOLD', 'confidence': 50, 'reasoning': ['Insufficient data']},
            'timestamp': datetime.now().isoformat()
        }