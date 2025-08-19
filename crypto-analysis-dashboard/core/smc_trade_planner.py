#!/usr/bin/env python3
"""
TradePlanner: SMC Trade Planning Module
Menghitung entry, SL, TP berdasarkan OB/FVG + liquidity analysis
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import numpy as np

logger = logging.getLogger(__name__)

class TradePlanQuality(Enum):
    """Trade plan quality assessment"""
    EXCELLENT = "excellent"
    GOOD = "good"
    AVERAGE = "average"
    POOR = "poor"

@dataclass
class TradePlan:
    """Comprehensive trade plan structure"""
    symbol: str
    direction: str  # LONG/SHORT
    timeframe: str
    timestamp: int
    
    # Entry details
    entry_price: float
    entry_reason: str
    entry_confidence: float
    
    # Stop Loss details
    stop_loss: float
    stop_loss_reason: str
    stop_loss_distance: float  # in %
    
    # Take Profit levels
    take_profit_1: float
    take_profit_2: float
    take_profit_3: float
    tp1_reason: str
    tp2_reason: str
    tp3_reason: str
    
    # Risk management
    risk_reward_ratio: float
    position_size_percent: float
    max_risk_percent: float
    
    # SMC components used
    order_block_used: Optional[Dict[str, Any]]
    fvg_used: Optional[Dict[str, Any]]
    liquidity_levels: List[Dict[str, Any]]
    
    # Plan quality
    plan_quality: TradePlanQuality
    quality_score: float
    plan_notes: List[str]
    description: str

class TradePlanner:
    """
    📊 SMC Trade Planner
    
    Menghitung rencana trading lengkap berdasarkan:
    - Order Block analysis untuk entry/exit
    - Fair Value Gap positioning
    - Liquidity levels untuk target dan stop
    - Risk management calculations
    - Multi-level take profit strategy
    """
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.TradePlanner")
        
        # Risk management parameters
        self.default_risk_percent = 1.0  # 1% account risk per trade
        self.max_risk_percent = 3.0      # Maximum risk per trade
        self.min_rr_ratio = 1.5          # Minimum risk:reward ratio
        self.preferred_rr_ratio = 2.0    # Preferred risk:reward ratio
        
        # SMC calculation parameters
        self.ob_entry_offset = 0.001     # 0.1% offset from OB edge
        self.fvg_entry_offset = 0.0005   # 0.05% offset from FVG
        self.liquidity_buffer = 0.002    # 0.2% buffer from liquidity levels
        
        # Take profit distribution
        self.tp1_percent = 0.4  # 40% of position at TP1
        self.tp2_percent = 0.4  # 40% of position at TP2
        self.tp3_percent = 0.2  # 20% of position at TP3
        
        self.logger.info("📊 TradePlanner initialized with SMC-based calculations")
    
    def create_trade_plan(self, symbol: str, direction: str, current_price: float,
                         order_blocks: List[Dict], fvg_signals: List[Dict],
                         liquidity_sweeps: List[Dict], swing_points: Dict[str, List[Dict]],
                         account_balance: float = 10000, risk_percent: Optional[float] = None,
                         timeframe: str = "1H") -> TradePlan:
        """
        Create comprehensive trade plan using SMC principles
        
        Args:
            symbol: Trading symbol
            direction: LONG or SHORT
            current_price: Current market price
            order_blocks: Available order blocks
            fvg_signals: Fair Value Gap signals
            liquidity_sweeps: Liquidity sweep analysis
            swing_points: Swing highs and lows
            account_balance: Account balance for position sizing
            risk_percent: Risk percentage (default: self.default_risk_percent)
            timeframe: Analysis timeframe
            
        Returns:
            Complete TradePlan with all calculations
        """
        try:
            self.logger.info(f"📊 Creating trade plan for {direction} {symbol} at ${current_price}")
            
            # Use default risk if not provided
            if risk_percent is None:
                risk_percent = self.default_risk_percent
            
            # 1. Calculate optimal entry price
            entry_price, entry_reason, entry_confidence, ob_used, fvg_used = self._calculate_entry_price(
                direction, current_price, order_blocks, fvg_signals
            )
            
            # 2. Calculate stop loss
            stop_loss, stop_loss_reason, stop_loss_distance = self._calculate_stop_loss(
                direction, entry_price, order_blocks, swing_points, liquidity_sweeps
            )
            
            # 3. Calculate take profit levels
            tp_levels, tp_reasons = self._calculate_take_profit_levels(
                direction, entry_price, stop_loss, liquidity_sweeps, swing_points
            )
            
            # 4. Calculate risk management
            risk_reward_ratio = self._calculate_risk_reward_ratio(entry_price, stop_loss, tp_levels[0])
            position_size_percent = self._calculate_position_size(
                account_balance, entry_price, stop_loss, risk_percent
            )
            
            # 5. Assess plan quality
            plan_quality, quality_score, plan_notes = self._assess_plan_quality(
                risk_reward_ratio, entry_confidence, ob_used, fvg_used, len(liquidity_sweeps)
            )
            
            # 6. Identify relevant liquidity levels
            relevant_liquidity = self._identify_relevant_liquidity(
                liquidity_sweeps, entry_price, direction
            )
            
            # Create trade plan
            trade_plan = TradePlan(
                symbol=symbol,
                direction=direction,
                timeframe=timeframe,
                timestamp=int(datetime.now().timestamp() * 1000),
                entry_price=entry_price,
                entry_reason=entry_reason,
                entry_confidence=entry_confidence,
                stop_loss=stop_loss,
                stop_loss_reason=stop_loss_reason,
                stop_loss_distance=stop_loss_distance,
                take_profit_1=tp_levels[0],
                take_profit_2=tp_levels[1],
                take_profit_3=tp_levels[2],
                tp1_reason=tp_reasons[0],
                tp2_reason=tp_reasons[1],
                tp3_reason=tp_reasons[2],
                risk_reward_ratio=risk_reward_ratio,
                position_size_percent=position_size_percent,
                max_risk_percent=risk_percent,
                order_block_used=ob_used,
                fvg_used=fvg_used,
                liquidity_levels=relevant_liquidity,
                plan_quality=plan_quality,
                quality_score=quality_score,
                plan_notes=plan_notes,
                description=self._generate_plan_description(
                    symbol, direction, entry_price, stop_loss, tp_levels, 
                    risk_reward_ratio, plan_quality
                )
            )
            
            self.logger.info(f"✅ Trade plan created: {plan_quality.value.upper()} quality ({quality_score:.1%})")
            
            return trade_plan
            
        except Exception as e:
            self.logger.error(f"❌ Error creating trade plan: {e}")
            return self._get_default_trade_plan(symbol, direction, current_price, timeframe)
    
    def _calculate_entry_price(self, direction: str, current_price: float,
                             order_blocks: List[Dict], fvg_signals: List[Dict]) -> Tuple[float, str, float, Optional[Dict], Optional[Dict]]:
        """
        Calculate optimal entry price using OB/FVG analysis
        
        Returns:
            Tuple of (entry_price, reason, confidence, ob_used, fvg_used)
        """
        try:
            # Filter recent and relevant signals
            recent_obs = self._filter_recent_signals(order_blocks, hours=48)
            recent_fvgs = self._filter_recent_signals(fvg_signals, hours=24)
            
            # Find best Order Block for entry
            best_ob = self._find_best_order_block(direction, current_price, recent_obs)
            
            # Find best FVG for entry
            best_fvg = self._find_best_fvg(direction, current_price, recent_fvgs)
            
            # Determine optimal entry based on available signals
            if best_ob and best_fvg:
                # Use the closer one to current price
                ob_distance = abs(current_price - self._get_ob_entry_price(direction, best_ob)) / current_price
                fvg_distance = abs(current_price - self._get_fvg_entry_price(direction, best_fvg)) / current_price
                
                if ob_distance < fvg_distance:
                    entry_price = self._get_ob_entry_price(direction, best_ob)
                    return entry_price, f"Order Block entry at ${entry_price:.4f}", 0.8, best_ob, None
                else:
                    entry_price = self._get_fvg_entry_price(direction, best_fvg)
                    return entry_price, f"FVG entry at ${entry_price:.4f}", 0.75, None, best_fvg
                    
            elif best_ob:
                entry_price = self._get_ob_entry_price(direction, best_ob)
                return entry_price, f"Order Block entry at ${entry_price:.4f}", 0.8, best_ob, None
                
            elif best_fvg:
                entry_price = self._get_fvg_entry_price(direction, best_fvg)
                return entry_price, f"FVG entry at ${entry_price:.4f}", 0.75, None, best_fvg
                
            else:
                # Fallback: Use current price with small offset
                offset = self.ob_entry_offset if direction.upper() == 'LONG' else -self.ob_entry_offset
                entry_price = current_price * (1 + offset)
                return entry_price, f"Market entry at ${entry_price:.4f}", 0.5, None, None
                
        except Exception as e:
            self.logger.warning(f"⚠️ Error calculating entry price: {e}")
            return current_price, "Market entry (calculation error)", 0.3, None, None
    
    def _calculate_stop_loss(self, direction: str, entry_price: float,
                           order_blocks: List[Dict], swing_points: Dict[str, List[Dict]],
                           liquidity_sweeps: List[Dict]) -> Tuple[float, str, float]:
        """
        Calculate stop loss using SMC principles
        
        Returns:
            Tuple of (stop_loss, reason, distance_percent)
        """
        try:
            # Get recent swing points
            recent_highs = swing_points.get('swing_highs', [])[-5:]
            recent_lows = swing_points.get('swing_lows', [])[-5:]
            
            if direction.upper() == 'LONG':
                # For LONG: Stop below recent swing low or order block
                potential_stops = []
                
                # Add recent swing lows
                for low in recent_lows:
                    low_price = self._safe_get_price(low)
                    if low_price > 0 and low_price < entry_price:
                        distance = (entry_price - low_price) / entry_price
                        if distance < 0.1:  # Within 10%
                            potential_stops.append((low_price * 0.998, f"Below swing low", distance))
                
                # Add order block lows
                for ob in order_blocks[-3:]:  # Last 3 OBs
                    if ob.get('direction') == 'support':
                        ob_low = ob.get('price_low', self._safe_get_price(ob))
                        if ob_low > 0 and ob_low < entry_price:
                            distance = (entry_price - ob_low) / entry_price
                            if distance < 0.08:  # Within 8%
                                potential_stops.append((ob_low * 0.998, f"Below order block", distance))
                
                # Choose the closest reasonable stop
                if potential_stops:
                    # Sort by distance and choose closest
                    potential_stops.sort(key=lambda x: x[2])
                    stop_loss, reason, distance = potential_stops[0]
                else:
                    # Fallback: 2% below entry
                    distance = 0.02
                    stop_loss = entry_price * (1 - distance)
                    reason = "2% below entry (fallback)"
                    
            else:  # SHORT
                # For SHORT: Stop above recent swing high or order block
                potential_stops = []
                
                # Add recent swing highs
                for high in recent_highs:
                    high_price = self._safe_get_price(high)
                    if high_price > 0 and high_price > entry_price:
                        distance = (high_price - entry_price) / entry_price
                        if distance < 0.1:  # Within 10%
                            potential_stops.append((high_price * 1.002, f"Above swing high", distance))
                
                # Add order block highs
                for ob in order_blocks[-3:]:  # Last 3 OBs
                    if ob.get('direction') == 'resistance':
                        ob_high = ob.get('price_high', self._safe_get_price(ob))
                        if ob_high > 0 and ob_high > entry_price:
                            distance = (ob_high - entry_price) / entry_price
                            if distance < 0.08:  # Within 8%
                                potential_stops.append((ob_high * 1.002, f"Above order block", distance))
                
                # Choose the closest reasonable stop
                if potential_stops:
                    potential_stops.sort(key=lambda x: x[2])
                    stop_loss, reason, distance = potential_stops[0]
                else:
                    # Fallback: 2% above entry
                    distance = 0.02
                    stop_loss = entry_price * (1 + distance)
                    reason = "2% above entry (fallback)"
            
            return stop_loss, reason, distance * 100  # Convert to percentage
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error calculating stop loss: {e}")
            # Emergency fallback
            distance = 0.02
            if direction.upper() == 'LONG':
                stop_loss = entry_price * (1 - distance)
            else:
                stop_loss = entry_price * (1 + distance)
            return stop_loss, "2% stop (calculation error)", distance * 100
    
    def _calculate_take_profit_levels(self, direction: str, entry_price: float, stop_loss: float,
                                    liquidity_sweeps: List[Dict], swing_points: Dict[str, List[Dict]]) -> Tuple[List[float], List[str]]:
        """
        Calculate multiple take profit levels using liquidity analysis
        
        Returns:
            Tuple of (tp_levels, tp_reasons)
        """
        try:
            # Calculate risk distance
            if direction.upper() == 'LONG':
                risk_distance = entry_price - stop_loss
            else:
                risk_distance = stop_loss - entry_price
            
            # Get potential targets from liquidity levels
            liquidity_targets = self._get_liquidity_targets(direction, entry_price, liquidity_sweeps)
            
            # Get targets from swing points
            swing_targets = self._get_swing_targets(direction, entry_price, swing_points)
            
            # Combine and sort targets
            all_targets = liquidity_targets + swing_targets
            
            if direction.upper() == 'LONG':
                valid_targets = [(price, reason) for price, reason in all_targets if price > entry_price]
                valid_targets.sort(key=lambda x: x[0])  # Sort ascending
            else:
                valid_targets = [(price, reason) for price, reason in all_targets if price < entry_price]
                valid_targets.sort(key=lambda x: x[0], reverse=True)  # Sort descending
            
            # Select 3 take profit levels
            tp_levels = []
            tp_reasons = []
            
            if len(valid_targets) >= 3:
                # Use first 3 targets
                tp_levels = [target[0] for target in valid_targets[:3]]
                tp_reasons = [target[1] for target in valid_targets[:3]]
            elif len(valid_targets) >= 1:
                # Use available targets and fill with RR-based levels
                for target in valid_targets:
                    tp_levels.append(target[0])
                    tp_reasons.append(target[1])
                
                # Fill remaining with RR-based levels
                while len(tp_levels) < 3:
                    rr_multiplier = (len(tp_levels) + 1) * 1.5  # 1.5, 3.0, 4.5 RR
                    if direction.upper() == 'LONG':
                        rr_target = entry_price + (risk_distance * rr_multiplier)
                    else:
                        rr_target = entry_price - (risk_distance * rr_multiplier)
                    
                    tp_levels.append(rr_target)
                    tp_reasons.append(f"{rr_multiplier:.1f}:1 Risk/Reward")
            else:
                # Fallback: Use RR-based levels only
                for i, rr_multiplier in enumerate([1.5, 2.5, 3.5]):
                    if direction.upper() == 'LONG':
                        rr_target = entry_price + (risk_distance * rr_multiplier)
                    else:
                        rr_target = entry_price - (risk_distance * rr_multiplier)
                    
                    tp_levels.append(rr_target)
                    tp_reasons.append(f"{rr_multiplier:.1f}:1 Risk/Reward")
            
            return tp_levels, tp_reasons
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error calculating take profit levels: {e}")
            # Emergency fallback
            risk_distance = abs(entry_price - stop_loss)
            fallback_levels = []
            fallback_reasons = []
            
            for i, rr_multiplier in enumerate([2.0, 3.0, 4.0]):
                if direction.upper() == 'LONG':
                    target = entry_price + (risk_distance * rr_multiplier)
                else:
                    target = entry_price - (risk_distance * rr_multiplier)
                
                fallback_levels.append(target)
                fallback_reasons.append(f"{rr_multiplier:.1f}:1 R/R (fallback)")
            
            return fallback_levels, fallback_reasons
    
    def _filter_recent_signals(self, signals: List[Dict], hours: int = 24) -> List[Dict]:
        """Filter signals to recent timeframe"""
        cutoff_timestamp = int((datetime.now() - timedelta(hours=hours)).timestamp() * 1000)
        return [signal for signal in signals if signal.get('timestamp', 0) > cutoff_timestamp]
    
    def _find_best_order_block(self, direction: str, current_price: float, order_blocks: List[Dict]) -> Optional[Dict]:
        """Find best order block for entry"""
        try:
            relevant_obs = []
            
            for ob in order_blocks:
                ob_price = self._safe_get_price(ob)
                if ob_price <= 0:
                    continue
                
                distance = abs(current_price - ob_price) / current_price
                
                # For LONG: Look for support OBs below current price
                if direction.upper() == 'LONG' and ob.get('direction') == 'support' and ob_price < current_price:
                    if distance < 0.05:  # Within 5%
                        relevant_obs.append((ob, distance))
                
                # For SHORT: Look for resistance OBs above current price  
                elif direction.upper() == 'SHORT' and ob.get('direction') == 'resistance' and ob_price > current_price:
                    if distance < 0.05:  # Within 5%
                        relevant_obs.append((ob, distance))
            
            if relevant_obs:
                # Return closest OB
                relevant_obs.sort(key=lambda x: x[1])
                return relevant_obs[0][0]
            
            return None
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error finding best order block: {e}")
            return None
    
    def _find_best_fvg(self, direction: str, current_price: float, fvg_signals: List[Dict]) -> Optional[Dict]:
        """Find best FVG for entry"""
        try:
            relevant_fvgs = []
            
            for fvg in fvg_signals:
                fvg_high = fvg.get('gap_high', 0)
                fvg_low = fvg.get('gap_low', 0)
                
                if fvg_high <= 0 or fvg_low <= 0:
                    continue
                
                fvg_mid = (fvg_high + fvg_low) / 2
                distance = abs(current_price - fvg_mid) / current_price
                
                # Check if current price is near FVG
                if distance < 0.03:  # Within 3%
                    relevant_fvgs.append((fvg, distance))
            
            if relevant_fvgs:
                # Return closest FVG
                relevant_fvgs.sort(key=lambda x: x[1])
                return relevant_fvgs[0][0]
            
            return None
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error finding best FVG: {e}")
            return None
    
    def _get_ob_entry_price(self, direction: str, order_block: Dict) -> float:
        """Get entry price from order block"""
        if direction.upper() == 'LONG':
            # Enter slightly above OB low
            ob_low = order_block.get('price_low', self._safe_get_price(order_block))
            return ob_low * (1 + self.ob_entry_offset)
        else:
            # Enter slightly below OB high
            ob_high = order_block.get('price_high', self._safe_get_price(order_block))
            return ob_high * (1 - self.ob_entry_offset)
    
    def _get_fvg_entry_price(self, direction: str, fvg: Dict) -> float:
        """Get entry price from FVG"""
        fvg_high = fvg.get('gap_high', 0)
        fvg_low = fvg.get('gap_low', 0)
        
        if direction.upper() == 'LONG':
            # Enter near FVG low
            return fvg_low * (1 + self.fvg_entry_offset)
        else:
            # Enter near FVG high
            return fvg_high * (1 - self.fvg_entry_offset)
    
    def _get_liquidity_targets(self, direction: str, entry_price: float, liquidity_sweeps: List[Dict]) -> List[Tuple[float, str]]:
        """Get target levels from liquidity analysis"""
        targets = []
        
        for sweep in liquidity_sweeps:
            sweep_price = self._safe_get_price(sweep)
            if sweep_price <= 0:
                continue
            
            # For LONG: Target liquidity above entry
            if direction.upper() == 'LONG' and sweep_price > entry_price:
                distance = (sweep_price - entry_price) / entry_price
                if 0.01 < distance < 0.2:  # 1% to 20% away
                    targets.append((sweep_price * (1 - self.liquidity_buffer), f"Liquidity at ${sweep_price:.4f}"))
            
            # For SHORT: Target liquidity below entry
            elif direction.upper() == 'SHORT' and sweep_price < entry_price:
                distance = (entry_price - sweep_price) / entry_price
                if 0.01 < distance < 0.2:  # 1% to 20% away
                    targets.append((sweep_price * (1 + self.liquidity_buffer), f"Liquidity at ${sweep_price:.4f}"))
        
        return targets
    
    def _get_swing_targets(self, direction: str, entry_price: float, swing_points: Dict[str, List[Dict]]) -> List[Tuple[float, str]]:
        """Get target levels from swing analysis"""
        targets = []
        
        if direction.upper() == 'LONG':
            # Target recent swing highs
            recent_highs = swing_points.get('swing_highs', [])[-5:]
            for high in recent_highs:
                high_price = self._safe_get_price(high)
                if high_price > entry_price:
                    distance = (high_price - entry_price) / entry_price
                    if 0.01 < distance < 0.15:  # 1% to 15% away
                        targets.append((high_price, f"Swing high at ${high_price:.4f}"))
        else:
            # Target recent swing lows
            recent_lows = swing_points.get('swing_lows', [])[-5:]
            for low in recent_lows:
                low_price = self._safe_get_price(low)
                if low_price < entry_price:
                    distance = (entry_price - low_price) / entry_price
                    if 0.01 < distance < 0.15:  # 1% to 15% away
                        targets.append((low_price, f"Swing low at ${low_price:.4f}"))
        
        return targets
    
    def _safe_get_price(self, data_point: Dict) -> float:
        """Safely extract price from data structure"""
        price_keys = ['price', 'close', 'high', 'low', 'level', 'sweep_price']
        for key in price_keys:
            if key in data_point and data_point[key] is not None:
                try:
                    return float(data_point[key])
                except (ValueError, TypeError):
                    continue
        return 0.0
    
    def _calculate_risk_reward_ratio(self, entry_price: float, stop_loss: float, take_profit: float) -> float:
        """Calculate risk/reward ratio"""
        try:
            risk = abs(entry_price - stop_loss)
            reward = abs(take_profit - entry_price)
            
            if risk > 0:
                return reward / risk
            else:
                return 0.0
                
        except Exception:
            return 0.0
    
    def _calculate_position_size(self, account_balance: float, entry_price: float, 
                               stop_loss: float, risk_percent: float) -> float:
        """Calculate position size based on risk management"""
        try:
            risk_amount = account_balance * (risk_percent / 100)
            risk_per_unit = abs(entry_price - stop_loss)
            
            if risk_per_unit > 0:
                position_size = risk_amount / risk_per_unit
                position_value = position_size * entry_price
                position_percent = (position_value / account_balance) * 100
                
                return min(position_percent, 50.0)  # Cap at 50% of account
            else:
                return 0.0
                
        except Exception:
            return 0.0
    
    def _assess_plan_quality(self, risk_reward_ratio: float, entry_confidence: float,
                           ob_used: Optional[Dict], fvg_used: Optional[Dict], liquidity_count: int) -> Tuple[TradePlanQuality, float, List[str]]:
        """Assess overall trade plan quality"""
        try:
            score = 0.0
            notes = []
            
            # Risk/Reward assessment (40% weight)
            if risk_reward_ratio >= 3.0:
                score += 0.4
                notes.append("Excellent R/R ratio")
            elif risk_reward_ratio >= 2.0:
                score += 0.3
                notes.append("Good R/R ratio")
            elif risk_reward_ratio >= 1.5:
                score += 0.2
                notes.append("Acceptable R/R ratio")
            else:
                notes.append("Poor R/R ratio")
            
            # Entry confidence (30% weight)
            if entry_confidence >= 0.8:
                score += 0.3
                notes.append("High entry confidence")
            elif entry_confidence >= 0.6:
                score += 0.2
                notes.append("Medium entry confidence")
            else:
                notes.append("Low entry confidence")
            
            # SMC components (20% weight)
            smc_score = 0
            if ob_used:
                smc_score += 0.1
                notes.append("Order Block utilized")
            if fvg_used:
                smc_score += 0.1
                notes.append("FVG utilized")
            score += smc_score
            
            # Liquidity analysis (10% weight)
            if liquidity_count >= 3:
                score += 0.1
                notes.append("Strong liquidity analysis")
            elif liquidity_count >= 1:
                score += 0.05
                notes.append("Basic liquidity analysis")
            
            # Determine quality level
            if score >= 0.8:
                quality = TradePlanQuality.EXCELLENT
            elif score >= 0.6:
                quality = TradePlanQuality.GOOD
            elif score >= 0.4:
                quality = TradePlanQuality.AVERAGE
            else:
                quality = TradePlanQuality.POOR
            
            return quality, score, notes
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error assessing plan quality: {e}")
            return TradePlanQuality.AVERAGE, 0.5, ["Quality assessment error"]
    
    def _identify_relevant_liquidity(self, liquidity_sweeps: List[Dict], entry_price: float, direction: str) -> List[Dict]:
        """Identify liquidity levels relevant to the trade"""
        relevant = []
        
        for sweep in liquidity_sweeps[-10:]:  # Last 10 sweeps
            sweep_price = self._safe_get_price(sweep)
            if sweep_price <= 0:
                continue
            
            distance = abs(sweep_price - entry_price) / entry_price
            if distance < 0.1:  # Within 10% of entry
                relevant.append({
                    "price": sweep_price,
                    "type": sweep.get('type', 'unknown'),
                    "distance_percent": distance * 100,
                    "timestamp": sweep.get('timestamp', 0)
                })
        
        return relevant
    
    def _generate_plan_description(self, symbol: str, direction: str, entry_price: float,
                                 stop_loss: float, tp_levels: List[float],
                                 risk_reward_ratio: float, plan_quality: TradePlanQuality) -> str:
        """Generate human-readable plan description"""
        risk_distance = abs(entry_price - stop_loss) / entry_price * 100
        reward_distance = abs(tp_levels[0] - entry_price) / entry_price * 100
        
        description = f"{direction} {symbol} at ${entry_price:.4f} with {plan_quality.value} quality plan. "
        description += f"Risk: {risk_distance:.1f}% (${stop_loss:.4f}), "
        description += f"Reward: {reward_distance:.1f}% (${tp_levels[0]:.4f}), "
        description += f"R/R: {risk_reward_ratio:.1f}:1"
        
        return description
    
    def _get_default_trade_plan(self, symbol: str, direction: str, current_price: float, timeframe: str) -> TradePlan:
        """Get default trade plan for error cases"""
        stop_loss = current_price * 0.98 if direction.upper() == 'LONG' else current_price * 1.02
        tp1 = current_price * 1.04 if direction.upper() == 'LONG' else current_price * 0.96
        tp2 = current_price * 1.06 if direction.upper() == 'LONG' else current_price * 0.94
        tp3 = current_price * 1.08 if direction.upper() == 'LONG' else current_price * 0.92
        
        return TradePlan(
            symbol=symbol,
            direction=direction,
            timeframe=timeframe,
            timestamp=int(datetime.now().timestamp() * 1000),
            entry_price=current_price,
            entry_reason="Market entry (calculation error)",
            entry_confidence=0.3,
            stop_loss=stop_loss,
            stop_loss_reason="2% stop (default)",
            stop_loss_distance=2.0,
            take_profit_1=tp1,
            take_profit_2=tp2,
            take_profit_3=tp3,
            tp1_reason="4% target (default)",
            tp2_reason="6% target (default)",
            tp3_reason="8% target (default)",
            risk_reward_ratio=2.0,
            position_size_percent=1.0,
            max_risk_percent=1.0,
            order_block_used=None,
            fvg_used=None,
            liquidity_levels=[],
            plan_quality=TradePlanQuality.POOR,
            quality_score=0.3,
            plan_notes=["Default plan due to calculation error"],
            description=f"Default {direction} plan for {symbol} due to system error"
        )
    
    def get_trade_plan_summary(self, trade_plan: TradePlan) -> Dict[str, Any]:
        """
        Get summary of trade plan for external use
        
        Returns:
            Dictionary with trade plan summary
        """
        return {
            "symbol": trade_plan.symbol,
            "direction": trade_plan.direction,
            "timeframe": trade_plan.timeframe,
            "timestamp": trade_plan.timestamp,
            "entry_price": trade_plan.entry_price,
            "stop_loss": trade_plan.stop_loss,
            "take_profit_levels": [
                trade_plan.take_profit_1,
                trade_plan.take_profit_2,
                trade_plan.take_profit_3
            ],
            "risk_reward_ratio": trade_plan.risk_reward_ratio,
            "position_size_percent": trade_plan.position_size_percent,
            "plan_quality": trade_plan.plan_quality.value,
            "quality_score": trade_plan.quality_score,
            "smc_components": {
                "order_block_used": trade_plan.order_block_used is not None,
                "fvg_used": trade_plan.fvg_used is not None,
                "liquidity_levels_count": len(trade_plan.liquidity_levels)
            },
            "description": trade_plan.description,
            "plan_notes": trade_plan.plan_notes
        }