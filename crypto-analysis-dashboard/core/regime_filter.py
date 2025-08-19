#!/usr/bin/env python3
"""
Regime Filter - Volatility dan funding-based signal filtering
Hanya mengambil sinyal saat kondisi market cocok
"""
import logging
import numpy as np
from typing import Dict, Any, Optional, Tuple, List
from dataclasses import dataclass
import time

logger = logging.getLogger(__name__)

@dataclass
class RegimeState:
    volatility_regime: str  # low/normal/high
    volatility_percentile: float
    atr_normalized: float
    funding_extreme: bool
    funding_rate: float
    oi_anomaly: bool
    regime_score: float  # 0-100, higher = better conditions
    timestamp: float

class RegimeFilter:
    def __init__(self):
        # Volatility thresholds (in ATR percentiles)
        self.volatility_thresholds = {
            'low': 25,      # Below 25th percentile
            'normal': 75,   # 25th to 75th percentile  
            'high': 100     # Above 75th percentile
        }
        
        # Funding rate extreme thresholds
        self.funding_thresholds = {
            'extreme_positive': 0.0005,  # 0.05% per 8h
            'extreme_negative': -0.0005,
            'normal_range': 0.0002       # ±0.02% considered normal
        }
        
        # Signal permission rules per regime
        self.regime_rules = {
            'low_volatility': {
                'allow_signals': True,
                'position_size_multiplier': 0.8,  # Reduce size in low vol
                'min_confluence_score': 65        # Higher threshold
            },
            'normal_volatility': {
                'allow_signals': True,
                'position_size_multiplier': 1.0,
                'min_confluence_score': 60
            },
            'high_volatility': {
                'allow_signals': True,
                'position_size_multiplier': 1.5,  # Increase size but tighter stops
                'min_confluence_score': 75        # Much higher threshold
            },
            'extreme_funding': {
                'allow_contrarian': True,         # Allow contrarian trades
                'block_trend_following': True,    # Block trend trades
                'min_confluence_score': 80
            }
        }
        
        # Historical data for percentile calculation (mock)
        self.atr_history = []
        self.max_history_length = 200
        
    def analyze_regime(self, 
                      market_data: Dict[str, Any],
                      funding_data: Optional[Dict[str, Any]] = None,
                      oi_data: Optional[Dict[str, Any]] = None) -> RegimeState:
        """
        Analyze current market regime
        """
        try:
            # Calculate volatility regime
            volatility_regime, vol_percentile, atr_norm = self._analyze_volatility(market_data)
            
            # Analyze funding conditions
            funding_extreme, funding_rate = self._analyze_funding(funding_data)
            
            # Check OI anomalies
            oi_anomaly = self._check_oi_anomaly(oi_data)
            
            # Calculate overall regime score
            regime_score = self._calculate_regime_score(
                volatility_regime, vol_percentile, funding_extreme, oi_anomaly
            )
            
            return RegimeState(
                volatility_regime=volatility_regime,
                volatility_percentile=vol_percentile,
                atr_normalized=atr_norm,
                funding_extreme=funding_extreme,
                funding_rate=funding_rate,
                oi_anomaly=oi_anomaly,
                regime_score=regime_score,
                timestamp=time.time()
            )
            
        except Exception as e:
            logger.error(f"Regime analysis error: {e}")
            return self._get_fallback_regime()
    
    def should_allow_signal(self, 
                           regime_state: RegimeState,
                           signal_direction: str,  # BUY/SELL
                           confluence_score: float,
                           signal_type: str = "trend") -> Tuple[bool, str, Dict[str, Any]]:
        """
        Determine if signal should be allowed based on regime
        Returns: (allowed, reason, adjustments)
        """
        try:
            adjustments = {
                'position_size_multiplier': 1.0,
                'min_confluence_required': 60,
                'additional_filters': []
            }
            
            # Check volatility regime
            vol_rules = self.regime_rules.get(f"{regime_state.volatility_regime}_volatility", {})
            
            if not vol_rules.get('allow_signals', True):
                return False, f"Signals blocked in {regime_state.volatility_regime} volatility regime", adjustments
            
            # Apply volatility-based adjustments
            adjustments['position_size_multiplier'] = vol_rules.get('position_size_multiplier', 1.0)
            adjustments['min_confluence_required'] = vol_rules.get('min_confluence_score', 60)
            
            # Check if confluence score meets regime requirement
            min_required = adjustments['min_confluence_required']
            if confluence_score < min_required:
                return False, f"Confluence score {confluence_score:.1f} below regime requirement {min_required}", adjustments
            
            # Funding regime checks
            if regime_state.funding_extreme:
                funding_rules = self.regime_rules['extreme_funding']
                
                if signal_type == "trend" and funding_rules.get('block_trend_following', False):
                    # Block trend-following in extreme funding
                    if ((regime_state.funding_rate > 0 and signal_direction == 'BUY') or
                        (regime_state.funding_rate < 0 and signal_direction == 'SELL')):
                        return False, "Trend-following blocked during extreme funding", adjustments
                
                # Higher confluence requirement
                extreme_min = funding_rules.get('min_confluence_score', 80)
                if confluence_score < extreme_min:
                    return False, f"Extreme funding requires confluence ≥{extreme_min}, got {confluence_score:.1f}", adjustments
            
            # OI anomaly checks
            if regime_state.oi_anomaly:
                adjustments['position_size_multiplier'] *= 0.7  # Reduce size
                adjustments['additional_filters'].append("OI_anomaly_detected")
            
            # High volatility adjustments
            if regime_state.volatility_regime == 'high':
                adjustments['additional_filters'].append("tight_stops_recommended")
                adjustments['stop_loss_multiplier'] = 0.8  # Tighter stops
            
            # Low volatility adjustments  
            elif regime_state.volatility_regime == 'low':
                adjustments['additional_filters'].append("extended_targets_available")
                adjustments['take_profit_multiplier'] = 1.2  # Extended targets
            
            return True, f"Signal approved for {regime_state.volatility_regime} volatility regime", adjustments
            
        except Exception as e:
            logger.error(f"Signal filtering error: {e}")
            return False, f"Regime filter error: {str(e)}", adjustments
    
    def _analyze_volatility(self, market_data: Dict[str, Any]) -> Tuple[str, float, float]:
        """Analyze volatility regime using ATR percentiles"""
        try:
            # Mock ATR calculation - would use real market data
            current_atr = market_data.get('atr', 0.02)  # 2% mock ATR
            
            # Update ATR history
            self.atr_history.append(current_atr)
            if len(self.atr_history) > self.max_history_length:
                self.atr_history.pop(0)
            
            # Calculate percentile
            if len(self.atr_history) >= 20:
                percentile = (np.sum(np.array(self.atr_history) <= current_atr) / len(self.atr_history)) * 100
            else:
                percentile = 50  # Default to median
            
            # Normalize ATR (0-1 scale)
            atr_normalized = min(current_atr / 0.05, 1.0)  # Cap at 5%
            
            # Determine regime
            if percentile <= self.volatility_thresholds['low']:
                regime = 'low'
            elif percentile <= self.volatility_thresholds['normal']:
                regime = 'normal'
            else:
                regime = 'high'
            
            return regime, percentile, atr_normalized
            
        except Exception as e:
            logger.warning(f"Volatility analysis error: {e}")
            return 'normal', 50.0, 0.02
    
    def _analyze_funding(self, funding_data: Optional[Dict[str, Any]]) -> Tuple[bool, float]:
        """Analyze funding rate extremes"""
        try:
            if not funding_data:
                return False, 0.0
            
            funding_rate = funding_data.get('funding_rate', 0)
            
            # Check for extreme funding
            extreme = (abs(funding_rate) > self.funding_thresholds['extreme_positive'])
            
            return extreme, funding_rate
            
        except Exception as e:
            logger.warning(f"Funding analysis error: {e}")
            return False, 0.0
    
    def _check_oi_anomaly(self, oi_data: Optional[Dict[str, Any]]) -> bool:
        """Check for Open Interest anomalies"""
        try:
            if not oi_data:
                return False
            
            # Mock OI anomaly detection
            oi_change_24h = oi_data.get('change_24h_pct', 0)
            
            # Flag as anomaly if OI changed >50% in 24h
            return abs(oi_change_24h) > 50
            
        except Exception as e:
            logger.warning(f"OI anomaly check error: {e}")
            return False
    
    def _calculate_regime_score(self, 
                               volatility_regime: str,
                               vol_percentile: float,
                               funding_extreme: bool,
                               oi_anomaly: bool) -> float:
        """Calculate overall regime favorability score (0-100)"""
        try:
            score = 100.0
            
            # Volatility penalty
            if volatility_regime == 'low':
                score -= 15  # Low vol reduces opportunity
            elif volatility_regime == 'high':
                score -= 25  # High vol increases risk
            
            # Funding penalty
            if funding_extreme:
                score -= 20
            
            # OI anomaly penalty
            if oi_anomaly:
                score -= 15
            
            # Volatility percentile adjustment
            if vol_percentile < 10 or vol_percentile > 90:
                score -= 10  # Extreme percentiles
            
            return max(score, 0.0)
            
        except Exception as e:
            logger.warning(f"Regime score calculation error: {e}")
            return 50.0
    
    def _get_fallback_regime(self) -> RegimeState:
        """Fallback regime when analysis fails"""
        return RegimeState(
            volatility_regime="normal",
            volatility_percentile=50.0,
            atr_normalized=0.02,
            funding_extreme=False,
            funding_rate=0.0,
            oi_anomaly=False,
            regime_score=50.0,
            timestamp=time.time()
        )
    
    def get_regime_summary(self, regime_state: RegimeState) -> Dict[str, Any]:
        """Get human-readable regime summary"""
        return {
            "regime_assessment": {
                "volatility": f"{regime_state.volatility_regime.upper()} ({regime_state.volatility_percentile:.1f}th percentile)",
                "funding": "EXTREME" if regime_state.funding_extreme else "NORMAL",
                "open_interest": "ANOMALY" if regime_state.oi_anomaly else "NORMAL",
                "overall_score": f"{regime_state.regime_score:.1f}/100"
            },
            "recommendations": self._get_regime_recommendations(regime_state),
            "risk_adjustments": {
                "position_sizing": self._get_position_sizing_recommendation(regime_state),
                "stop_loss": self._get_stop_loss_recommendation(regime_state),
                "take_profit": self._get_take_profit_recommendation(regime_state)
            }
        }
    
    def _get_regime_recommendations(self, regime_state: RegimeState) -> List[str]:
        """Get trading recommendations for current regime"""
        recommendations = []
        
        if regime_state.volatility_regime == 'low':
            recommendations.append("Consider wider targets in low volatility")
            recommendations.append("Reduce position sizes due to limited moves")
        elif regime_state.volatility_regime == 'high':
            recommendations.append("Use tighter stops in high volatility")
            recommendations.append("Consider larger positions with proper risk management")
        
        if regime_state.funding_extreme:
            recommendations.append("Watch for funding-driven reversals")
            recommendations.append("Consider contrarian setups")
        
        if regime_state.oi_anomaly:
            recommendations.append("Reduce position sizes due to OI anomaly")
            
        return recommendations
    
    def _get_position_sizing_recommendation(self, regime_state: RegimeState) -> str:
        """Get position sizing recommendation"""
        if regime_state.volatility_regime == 'low':
            return "REDUCE (0.8x) - Limited price moves expected"
        elif regime_state.volatility_regime == 'high':
            return "INCREASE (1.5x) - Higher volatility allows bigger moves"
        else:
            return "NORMAL (1.0x) - Standard position sizing"
    
    def _get_stop_loss_recommendation(self, regime_state: RegimeState) -> str:
        """Get stop loss recommendation"""
        if regime_state.volatility_regime == 'high':
            return "TIGHTER (0.8x) - Prevent large losses in volatile conditions"
        else:
            return "STANDARD (1.0x) - Normal stop loss levels"
    
    def _get_take_profit_recommendation(self, regime_state: RegimeState) -> str:
        """Get take profit recommendation"""
        if regime_state.volatility_regime == 'low':
            return "EXTENDED (1.2x) - Capture full moves in low volatility"
        else:
            return "STANDARD (1.0x) - Normal take profit levels"