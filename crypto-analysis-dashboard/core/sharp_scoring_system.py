#!/usr/bin/env python3
"""
Sharp Scoring System - Simple & Effective
Sistem scoring tajam dengan threshold ≥70 untuk sinyal berkualitas tinggi
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class MarketFactors:
    """Market factors untuk scoring calculation"""
    # Core factors (existing)
    smc_confidence: float = 0.0      # 0..1 SMC structure confidence
    ob_imbalance: float = 0.0        # 0..1 Order book imbalance
    momentum_signal: float = 0.0     # 0..1 Momentum strength
    vol_regime: float = 0.0          # 0..1 Volume regime
    
    # New factors
    lux_signal: Optional[str] = None      # "BUY", "SELL", None
    bias: str = "neutral"                 # "long", "short", "neutral"
    funding_rate_abs: float = 0.0         # Absolute funding rate
    oi_delta_pos: bool = False            # OI increase during breakout
    long_short_extreme: bool = False      # Extreme long/short sentiment

class SharpScoringSystem:
    """
    Simple dan effective scoring system
    Fokus pada faktor-faktor yang paling predictive
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Scoring weights (total = 100 points)
        self.weights = {
            'smc_confidence': 40,        # SMC structure (most important)
            'ob_imbalance': 20,         # Order book imbalance
            'momentum_signal': 15,       # Momentum confirmation
            'vol_regime': 10,           # Volume regime
            'luxalgo_bonus': 10,        # LuxAlgo alignment bonus
            'coinglass_penalty': -5,    # CoinGlass penalty for crowded trades
            'coinglass_bonus': 5        # CoinGlass bonus for confirmation
        }
        
        # Thresholds
        self.sharp_threshold = 70       # Minimum score for "sharp" signal
        self.funding_extreme = 0.05     # 5 bps = extreme funding
        
    def calculate_sharp_score(self, factors: MarketFactors) -> Dict[str, Any]:
        """
        Calculate sharp score using simple additive model
        
        Returns score and breakdown untuk transparency
        """
        try:
            score = 0
            breakdown = {}
            
            # Core SMC scoring (existing system)
            smc_points = 40 * factors.smc_confidence
            score += smc_points
            breakdown['smc_structure'] = smc_points
            
            # Order book imbalance (existing)
            ob_points = 20 * factors.ob_imbalance
            score += ob_points
            breakdown['orderbook_imbalance'] = ob_points
            
            # Momentum/Volume (existing)
            momentum_points = 15 * factors.momentum_signal
            vol_points = 10 * factors.vol_regime
            score += momentum_points + vol_points
            breakdown['momentum'] = momentum_points
            breakdown['volume_regime'] = vol_points
            
            # NEW: LuxAlgo alignment bonus
            luxalgo_points = 0
            if factors.lux_signal == "BUY" and factors.bias == "long":
                luxalgo_points = 10
                self.logger.info("LuxAlgo BUY + Long bias alignment: +10 points")
            elif factors.lux_signal == "SELL" and factors.bias == "short":  
                luxalgo_points = 10
                self.logger.info("LuxAlgo SELL + Short bias alignment: +10 points")
            elif factors.lux_signal and factors.lux_signal != "NEUTRAL":
                luxalgo_points = -5  # Penalty for misalignment
                self.logger.warning(f"LuxAlgo {factors.lux_signal} vs {factors.bias} bias: -5 points")
                
            score += luxalgo_points
            breakdown['luxalgo_alignment'] = luxalgo_points
            
            # NEW: CoinGlass factors
            coinglass_adjustment = 0
            
            # Funding rate penalty (avoid crowded trades)
            if factors.funding_rate_abs > self.funding_extreme:
                coinglass_adjustment -= 5
                self.logger.info(f"High funding rate {factors.funding_rate_abs:.4f}: -5 points (crowded)")
                
            # OI breakout confirmation bonus
            if factors.oi_delta_pos:
                coinglass_adjustment += 5
                self.logger.info("Positive OI delta during breakout: +5 points")
                
            # Extreme sentiment penalty
            if factors.long_short_extreme:
                coinglass_adjustment -= 5
                self.logger.info("Extreme long/short sentiment: -5 points")
                
            score += coinglass_adjustment
            breakdown['coinglass_adjustment'] = coinglass_adjustment
            
            # Ensure score bounds
            score = max(0, min(100, score))
            
            # Determine signal quality
            is_sharp = score >= self.sharp_threshold
            
            quality_rating = self._get_quality_rating(score)
            
            result = {
                'sharp_score': round(score, 1),
                'is_sharp_signal': is_sharp,
                'quality_rating': quality_rating,
                'threshold_met': is_sharp,
                'score_breakdown': breakdown,
                'factors_used': {
                    'smc_confidence': factors.smc_confidence,
                    'ob_imbalance': factors.ob_imbalance, 
                    'momentum_signal': factors.momentum_signal,
                    'vol_regime': factors.vol_regime,
                    'lux_signal': factors.lux_signal,
                    'bias': factors.bias,
                    'funding_rate_abs': factors.funding_rate_abs,
                    'oi_delta_pos': factors.oi_delta_pos,
                    'long_short_extreme': factors.long_short_extreme
                },
                'enhancement_summary': {
                    'luxalgo_contribution': luxalgo_points,
                    'coinglass_contribution': coinglass_adjustment,
                    'total_enhancement': luxalgo_points + coinglass_adjustment,
                    'base_technical_score': smc_points + ob_points + momentum_points + vol_points
                }
            }
            
            # Add recommendation
            if is_sharp:
                result['recommendation'] = 'EXECUTE - High probability setup'
                result['confidence_level'] = 'HIGH'
            elif score >= 60:
                result['recommendation'] = 'CONSIDER - Good setup with minor flaws'
                result['confidence_level'] = 'MEDIUM'
            elif score >= 50:
                result['recommendation'] = 'WATCH - Marginal setup, wait for improvement'
                result['confidence_level'] = 'LOW'
            else:
                result['recommendation'] = 'AVOID - Poor setup quality'
                result['confidence_level'] = 'VERY_LOW'
                
            self.logger.info(f"Sharp score calculated: {score:.1f}/100 ({'SHARP' if is_sharp else 'NOT SHARP'})")
            return result
            
        except Exception as e:
            self.logger.error(f"Sharp scoring calculation error: {e}")
            return {
                'sharp_score': 0,
                'is_sharp_signal': False,
                'error': str(e)
            }
    
    def _get_quality_rating(self, score: float) -> str:
        """Convert numeric score to quality rating"""
        if score >= 85:
            return "EXCELLENT"
        elif score >= self.sharp_threshold:  # ≥70
            return "SHARP" 
        elif score >= 60:
            return "GOOD"
        elif score >= 50:
            return "AVERAGE"
        elif score >= 30:
            return "POOR"
        else:
            return "VERY_POOR"
    
    def analyze_signal_factors(self, 
                              smc_analysis: Dict[str, Any],
                              market_data: Dict[str, Any],
                              luxalgo_signal: Optional[str] = None) -> MarketFactors:
        """
        Convert raw analysis data ke MarketFactors structure
        """
        try:
            # Extract SMC confidence
            smc_confidence = min(1.0, smc_analysis.get('confidence_score', 0) / 100.0)
            
            # Extract order book imbalance
            ob_imbalance = market_data.get('orderbook_imbalance', 0.5)  # 0.5 = balanced
            
            # Extract momentum signal
            momentum_indicators = market_data.get('momentum_indicators', {})
            rsi = momentum_indicators.get('rsi', 50)
            macd_signal = momentum_indicators.get('macd_signal', 0)
            
            # Normalize momentum (RSI 30-70 range, MACD signal strength)
            rsi_normalized = abs(rsi - 50) / 50  # Distance from neutral
            macd_normalized = min(1.0, abs(macd_signal) / 2.0)  # MACD signal strength
            momentum_signal = (rsi_normalized + macd_normalized) / 2
            
            # Extract volume regime
            volume_data = market_data.get('volume_analysis', {})
            vol_ratio = volume_data.get('volume_ratio_20d', 1.0)  # vs 20-day average
            vol_regime = min(1.0, vol_ratio / 2.0)  # Normalize to 0-1
            
            # Determine bias from SMC analysis
            smc_bias = smc_analysis.get('bias', 'neutral').lower()
            bias = 'long' if smc_bias in ['bullish', 'long'] else ('short' if smc_bias in ['bearish', 'short'] else 'neutral')
            
            # Extract CoinGlass factors
            funding_rate = market_data.get('funding_rate', 0.0)
            funding_rate_abs = abs(funding_rate)
            
            oi_change = market_data.get('oi_24h_change', 0.0)
            oi_delta_pos = oi_change > 5.0  # >5% increase
            
            long_short_ratio = market_data.get('long_short_ratio', 1.0)
            long_short_extreme = long_short_ratio > 3.0 or long_short_ratio < 0.33
            
            factors = MarketFactors(
                smc_confidence=smc_confidence,
                ob_imbalance=ob_imbalance,
                momentum_signal=momentum_signal,
                vol_regime=vol_regime,
                lux_signal=luxalgo_signal,
                bias=bias,
                funding_rate_abs=funding_rate_abs,
                oi_delta_pos=oi_delta_pos,
                long_short_extreme=long_short_extreme
            )
            
            self.logger.info(f"Market factors analyzed: SMC={smc_confidence:.2f}, OB={ob_imbalance:.2f}, "
                           f"Mom={momentum_signal:.2f}, Vol={vol_regime:.2f}")
            
            return factors
            
        except Exception as e:
            self.logger.error(f"Factor analysis error: {e}")
            return MarketFactors()  # Return default factors
    
    def get_sharp_signals_only(self, signals_list: List[Dict]) -> List[Dict]:
        """
        Filter signals untuk hanya return yang SHARP (≥70)
        """
        try:
            sharp_signals = []
            
            for signal in signals_list:
                if signal.get('sharp_score', 0) >= self.sharp_threshold:
                    sharp_signals.append(signal)
                    
            self.logger.info(f"Filtered {len(sharp_signals)} sharp signals from {len(signals_list)} total")
            return sharp_signals
            
        except Exception as e:
            self.logger.error(f"Sharp signal filtering error: {e}")
            return []

# Global sharp scoring system
sharp_scorer = SharpScoringSystem()

def get_sharp_scoring_system():
    """Get the global sharp scoring system"""
    return sharp_scorer

def calculate_sharp_score_simple(smc_confidence: float,
                                ob_imbalance: float = 0.5,
                                momentum_signal: float = 0.5,
                                vol_regime: float = 0.5,
                                lux_signal: Optional[str] = None,
                                bias: str = "neutral",
                                funding_rate_abs: float = 0.0,
                                oi_delta_pos: bool = False,
                                long_short_extreme: bool = False) -> Dict[str, Any]:
    """
    Simple function untuk quick sharp score calculation
    
    Args:
        smc_confidence: SMC confidence 0-1
        ob_imbalance: Order book imbalance 0-1  
        momentum_signal: Momentum signal strength 0-1
        vol_regime: Volume regime 0-1
        lux_signal: LuxAlgo signal "BUY"/"SELL"/None
        bias: Current bias "long"/"short"/"neutral"
        funding_rate_abs: Absolute funding rate
        oi_delta_pos: OI increase during breakout
        long_short_extreme: Extreme sentiment
        
    Returns:
        Sharp score result dict
    """
    factors = MarketFactors(
        smc_confidence=smc_confidence,
        ob_imbalance=ob_imbalance,
        momentum_signal=momentum_signal,
        vol_regime=vol_regime,
        lux_signal=lux_signal,
        bias=bias,
        funding_rate_abs=funding_rate_abs,
        oi_delta_pos=oi_delta_pos,
        long_short_extreme=long_short_extreme
    )
    
    return sharp_scorer.calculate_sharp_score(factors)

if __name__ == "__main__":
    # Test sharp scoring system
    print("Sharp Scoring System Test")
    print("=" * 40)
    
    # Test case 1: Excellent setup
    print("\nTest 1: Excellent Setup")
    result1 = calculate_sharp_score_simple(
        smc_confidence=0.85,     # Strong SMC signal
        ob_imbalance=0.8,        # Strong order book imbalance
        momentum_signal=0.7,     # Good momentum
        vol_regime=0.6,          # Above average volume
        lux_signal="BUY",        # LuxAlgo buy signal
        bias="long",             # Aligned bias
        funding_rate_abs=0.03,   # Moderate funding
        oi_delta_pos=True,       # OI confirmation
        long_short_extreme=False # Balanced sentiment
    )
    print(f"Score: {result1['sharp_score']}/100 - {result1['quality_rating']}")
    print(f"Sharp Signal: {result1['is_sharp_signal']}")
    print(f"Recommendation: {result1['recommendation']}")
    
    # Test case 2: Poor setup with penalties
    print("\nTest 2: Poor Setup with Penalties")
    result2 = calculate_sharp_score_simple(
        smc_confidence=0.4,      # Weak SMC signal
        ob_imbalance=0.3,        # Poor order book
        momentum_signal=0.2,     # Weak momentum
        vol_regime=0.3,          # Low volume
        lux_signal="SELL",       # LuxAlgo sell but...
        bias="long",             # Misaligned bias
        funding_rate_abs=0.08,   # Extreme funding
        oi_delta_pos=False,      # No OI confirmation
        long_short_extreme=True  # Extreme sentiment
    )
    print(f"Score: {result2['sharp_score']}/100 - {result2['quality_rating']}")
    print(f"Sharp Signal: {result2['is_sharp_signal']}")
    print(f"Recommendation: {result2['recommendation']}")
    
    # Test case 3: Marginal setup (exactly at threshold)
    print("\nTest 3: Marginal Setup (At Threshold)")
    result3 = calculate_sharp_score_simple(
        smc_confidence=0.7,      # Good SMC
        ob_imbalance=0.5,        # Neutral OB
        momentum_signal=0.5,     # Neutral momentum
        vol_regime=0.4,          # Below average volume
        lux_signal="BUY",        # Aligned LuxAlgo
        bias="long",             # Aligned bias
        funding_rate_abs=0.02,   # Low funding
        oi_delta_pos=False,      # No OI boost
        long_short_extreme=False # Normal sentiment
    )
    print(f"Score: {result3['sharp_score']}/100 - {result3['quality_rating']}")
    print(f"Sharp Signal: {result3['is_sharp_signal']}")
    print(f"Recommendation: {result3['recommendation']}")
    
    print(f"\nSharp Threshold: {sharp_scorer.sharp_threshold}")
    print("Only signals ≥70 are considered 'SHARP'")