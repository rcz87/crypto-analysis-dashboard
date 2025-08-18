#!/usr/bin/env python3
"""
ExecutionGuard - Pre-execution market condition checker
Menilai spread, depth, dan slippage sebelum eksekusi
"""
import logging
import time
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ExecutionStatus(Enum):
    APPROVED = "approved"
    REJECTED = "rejected" 
    WARNING = "warning"

@dataclass
class ExecutionCheck:
    status: ExecutionStatus
    reasons: list
    spread_bps: float
    depth_score: float
    slippage_estimate: float
    liquidity_score: float
    timestamp: float

class ExecutionGuard:
    def __init__(self):
        self.thresholds = {
            'max_spread_bps': 5.0,      # 5 basis points
            'min_depth_score': 0.6,     # 0-1 scale
            'max_slippage_bps': 3.0,    # 3 basis points
            'min_liquidity_score': 0.5  # 0-1 scale
        }
        
        # Major pairs get tighter thresholds
        self.pair_thresholds = {
            'BTC-USDT': {'max_spread_bps': 2.0, 'max_slippage_bps': 1.5},
            'ETH-USDT': {'max_spread_bps': 2.5, 'max_slippage_bps': 2.0},
            'SOL-USDT': {'max_spread_bps': 3.0, 'max_slippage_bps': 2.5}
        }
    
    def check_execution_conditions(self, 
                                 symbol: str,
                                 side: str,  # BUY/SELL
                                 size_usd: float,
                                 orderbook_data: Dict[str, Any],
                                 market_data: Dict[str, Any] = None) -> ExecutionCheck:
        """
        Comprehensive execution condition check
        """
        try:
            reasons = []
            
            # Get pair-specific thresholds
            thresholds = self._get_thresholds(symbol)
            
            # 1. Spread Analysis
            spread_bps, spread_ok, spread_reason = self._check_spread(orderbook_data, thresholds)
            if spread_reason:
                reasons.append(spread_reason)
            
            # 2. Depth Analysis  
            depth_score, depth_ok, depth_reason = self._check_depth(orderbook_data, side, size_usd, thresholds)
            if depth_reason:
                reasons.append(depth_reason)
            
            # 3. Slippage Estimate
            slippage_bps, slippage_ok, slippage_reason = self._estimate_slippage(orderbook_data, side, size_usd, thresholds)
            if slippage_reason:
                reasons.append(slippage_reason)
            
            # 4. Liquidity Score
            liquidity_score, liquidity_ok, liquidity_reason = self._check_liquidity(orderbook_data, thresholds)
            if liquidity_reason:
                reasons.append(liquidity_reason)
            
            # Determine overall status
            all_checks = [spread_ok, depth_ok, slippage_ok, liquidity_ok]
            
            if all(all_checks):
                status = ExecutionStatus.APPROVED
                reasons.insert(0, "All execution conditions met")
            elif any(all_checks):
                status = ExecutionStatus.WARNING
                reasons.insert(0, "Some execution concerns - proceed with caution")
            else:
                status = ExecutionStatus.REJECTED
                reasons.insert(0, "Poor execution conditions - signal blocked")
            
            return ExecutionCheck(
                status=status,
                reasons=reasons[:5],  # Top 5 reasons
                spread_bps=spread_bps,
                depth_score=depth_score,
                slippage_estimate=slippage_bps,
                liquidity_score=liquidity_score,
                timestamp=time.time()
            )
            
        except Exception as e:
            logger.error(f"Execution guard error: {e}")
            return ExecutionCheck(
                status=ExecutionStatus.REJECTED,
                reasons=[f"Execution guard error: {str(e)}"],
                spread_bps=999.9,
                depth_score=0.0,
                slippage_estimate=999.9,
                liquidity_score=0.0,
                timestamp=time.time()
            )
    
    def _get_thresholds(self, symbol: str) -> Dict[str, float]:
        """Get symbol-specific thresholds"""
        base_thresholds = self.thresholds.copy()
        pair_specific = self.pair_thresholds.get(symbol, {})
        base_thresholds.update(pair_specific)
        return base_thresholds
    
    def _check_spread(self, orderbook_data: Dict[str, Any], thresholds: Dict[str, float]) -> Tuple[float, bool, str]:
        """Check bid-ask spread"""
        try:
            bids = orderbook_data.get('bids', [])
            asks = orderbook_data.get('asks', [])
            
            if not bids or not asks:
                return 999.9, False, "Empty orderbook"
            
            best_bid = float(bids[0][0])
            best_ask = float(asks[0][0])
            
            spread = best_ask - best_bid
            spread_bps = (spread / best_bid) * 10000  # basis points
            
            max_spread = thresholds['max_spread_bps']
            
            if spread_bps <= max_spread:
                return spread_bps, True, f"Good spread: {spread_bps:.1f} bps"
            else:
                return spread_bps, False, f"Wide spread: {spread_bps:.1f} bps > {max_spread} bps"
                
        except Exception as e:
            logger.warning(f"Spread check error: {e}")
            return 999.9, False, "Spread check failed"
    
    def _check_depth(self, orderbook_data: Dict[str, Any], side: str, size_usd: float, thresholds: Dict[str, float]) -> Tuple[float, bool, str]:
        """Check market depth for order size"""
        try:
            if side == 'BUY':
                levels = orderbook_data.get('asks', [])
            else:
                levels = orderbook_data.get('bids', [])
            
            if not levels:
                return 0.0, False, "No depth on required side"
            
            # Calculate available liquidity within reasonable price range (0.5%)
            total_liquidity_usd = 0.0
            entry_price = float(levels[0][0])
            
            for price_str, size_str in levels[:20]:  # Check top 20 levels
                price = float(price_str)
                size = float(size_str)
                
                # Only count liquidity within 0.5% of best price
                price_impact = abs(price - entry_price) / entry_price
                if price_impact > 0.005:  # 0.5%
                    break
                    
                total_liquidity_usd += price * size
            
            # Depth score based on available vs needed liquidity
            if size_usd > 0:
                depth_ratio = total_liquidity_usd / size_usd
                depth_score = min(depth_ratio, 1.0)  # Cap at 1.0
            else:
                depth_score = 1.0
            
            min_depth = thresholds['min_depth_score']
            
            if depth_score >= min_depth:
                return depth_score, True, f"Adequate depth: {depth_score:.2f} ratio"
            else:
                return depth_score, False, f"Insufficient depth: {depth_score:.2f} < {min_depth}"
                
        except Exception as e:
            logger.warning(f"Depth check error: {e}")
            return 0.0, False, "Depth check failed"
    
    def _estimate_slippage(self, orderbook_data: Dict[str, Any], side: str, size_usd: float, thresholds: Dict[str, float]) -> Tuple[float, bool, str]:
        """Estimate slippage for order"""
        try:
            if side == 'BUY':
                levels = orderbook_data.get('asks', [])
            else:
                levels = orderbook_data.get('bids', [])
            
            if not levels:
                return 999.9, False, "No levels for slippage calculation"
            
            entry_price = float(levels[0][0])
            remaining_usd = size_usd
            weighted_price = 0.0
            total_filled = 0.0
            
            # Walk through orderbook to estimate fill price
            for price_str, size_str in levels[:50]:  # Check deeper
                price = float(price_str)
                size = float(size_str)
                level_usd = price * size
                
                if remaining_usd <= level_usd:
                    # Partial fill at this level
                    weighted_price += price * remaining_usd
                    total_filled += remaining_usd
                    break
                else:
                    # Full fill at this level
                    weighted_price += price * level_usd
                    total_filled += level_usd
                    remaining_usd -= level_usd
            
            if total_filled == 0:
                return 999.9, False, "Cannot estimate slippage - insufficient liquidity"
            
            avg_fill_price = weighted_price / total_filled
            slippage = abs(avg_fill_price - entry_price) / entry_price
            slippage_bps = slippage * 10000  # basis points
            
            max_slippage = thresholds['max_slippage_bps']
            
            if slippage_bps <= max_slippage:
                return slippage_bps, True, f"Low slippage: {slippage_bps:.1f} bps"
            else:
                return slippage_bps, False, f"High slippage: {slippage_bps:.1f} bps > {max_slippage} bps"
                
        except Exception as e:
            logger.warning(f"Slippage estimation error: {e}")
            return 999.9, False, "Slippage estimation failed"
    
    def _check_liquidity(self, orderbook_data: Dict[str, Any], thresholds: Dict[str, float]) -> Tuple[float, bool, str]:
        """Overall liquidity health check"""
        try:
            bids = orderbook_data.get('bids', [])
            asks = orderbook_data.get('asks', [])
            
            if len(bids) < 10 or len(asks) < 10:
                return 0.0, False, "Thin orderbook - insufficient levels"
            
            # Check bid-ask balance
            total_bid_vol = sum(float(bid[1]) for bid in bids[:10])
            total_ask_vol = sum(float(ask[1]) for ask in asks[:10])
            
            if total_bid_vol + total_ask_vol == 0:
                return 0.0, False, "No liquidity in top levels"
            
            # Balance score (closer to 0.5 is better)
            balance = total_bid_vol / (total_bid_vol + total_ask_vol)
            balance_score = 1.0 - abs(balance - 0.5) * 2  # 0-1 scale
            
            # Level consistency score
            bid_consistency = self._calculate_level_consistency([float(b[1]) for b in bids[:10]])
            ask_consistency = self._calculate_level_consistency([float(a[1]) for a in asks[:10]])
            consistency_score = (bid_consistency + ask_consistency) / 2
            
            # Combined liquidity score
            liquidity_score = (balance_score * 0.6) + (consistency_score * 0.4)
            
            min_liquidity = thresholds['min_liquidity_score']
            
            if liquidity_score >= min_liquidity:
                return liquidity_score, True, f"Good liquidity: {liquidity_score:.2f}"
            else:
                return liquidity_score, False, f"Poor liquidity: {liquidity_score:.2f} < {min_liquidity}"
                
        except Exception as e:
            logger.warning(f"Liquidity check error: {e}")
            return 0.0, False, "Liquidity check failed"
    
    def _calculate_level_consistency(self, volumes: list) -> float:
        """Calculate how consistent volume levels are (less gaps = better)"""
        if len(volumes) < 3:
            return 0.0
        
        try:
            # Coefficient of variation (lower is more consistent)
            mean_vol = sum(volumes) / len(volumes)
            if mean_vol == 0:
                return 0.0
                
            variance = sum((v - mean_vol) ** 2 for v in volumes) / len(volumes)
            std_dev = variance ** 0.5
            cv = std_dev / mean_vol
            
            # Convert to score (lower CV = higher score)
            consistency_score = max(0.0, 1.0 - cv)
            return consistency_score
            
        except:
            return 0.0
    
    def is_approved(self, check: ExecutionCheck) -> bool:
        """Check if execution is approved"""
        return check.status == ExecutionStatus.APPROVED
    
    def has_warnings(self, check: ExecutionCheck) -> bool:
        """Check if execution has warnings"""
        return check.status == ExecutionStatus.WARNING
    
    def is_blocked(self, check: ExecutionCheck) -> bool:
        """Check if execution is blocked"""
        return check.status == ExecutionStatus.REJECTED