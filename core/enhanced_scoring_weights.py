#!/usr/bin/env python3
"""
Enhanced Scoring Weights with LuxAlgo, CoinGlass, and Market Sentiment Integration
Advanced signal scoring dengan multiple external data sources
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
import math

logger = logging.getLogger(__name__)

@dataclass
class MarketSentimentData:
    """Market sentiment data structure"""
    funding_rate: float              # Current funding rate (%)
    funding_rate_8h: float          # 8h average funding rate  
    open_interest: float            # Current OI ($)
    open_interest_24h_change: float # OI 24h change (%)
    long_short_ratio: float         # Long/Short ratio
    liquidation_volume_24h: float   # 24h liquidation volume ($)
    
    # LuxAlgo specific
    luxalgo_signal: Optional[str] = None    # 'BUY', 'SELL', 'NEUTRAL'
    luxalgo_strength: Optional[float] = None # Signal strength (0-100)
    luxalgo_indicator: Optional[str] = None  # Indicator name
    
@dataclass  
class ScoringFactors:
    """All scoring factors for enhanced signal calculation"""
    
    # Core SMC factors (existing)
    smc_structure_score: float = 0
    smc_zones_score: float = 0
    trend_alignment_score: float = 0
    
    # Technical factors (existing) 
    technical_indicators_score: float = 0
    volume_profile_score: float = 0
    momentum_score: float = 0
    
    # New: LuxAlgo factors
    luxalgo_confirmation_score: float = 0    # +10-20 when aligned with SMC
    luxalgo_trend_catcher_score: float = 0   # Trend confirmation bonus
    luxalgo_bias_alignment: float = 0        # Bias alignment multiplier
    
    # New: CoinGlass factors
    funding_rate_score: float = 0            # Funding rate analysis
    open_interest_delta_score: float = 0     # OI breakout confirmation
    liquidation_levels_score: float = 0     # Liquidation proximity
    
    # New: Market sentiment factors  
    long_short_ratio_score: float = 0        # Contrarian sentiment filter
    market_sentiment_filter: float = 1       # Sentiment multiplier (0.5-1.5)
    crowd_psychology_score: float = 0        # Crowd behavior analysis

class EnhancedScoringEngine:
    """
    Enhanced scoring engine dengan multiple data sources
    
    Features:
    - LuxAlgo signal integration and weighting
    - CoinGlass funding rate and OI analysis  
    - Market sentiment filtering
    - Dynamic weight adjustment based on market conditions
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Base scoring weights (existing system)
        self.base_weights = {
            'smc_structure': 25,        # SMC structure analysis
            'smc_zones': 20,           # Order blocks, FVG, etc.  
            'trend_alignment': 15,      # Multi-timeframe trend
            'technical_indicators': 15, # RSI, MACD, etc.
            'volume_profile': 10,       # Volume analysis
            'momentum': 10,            # Price momentum
            'risk_management': 5        # Basic risk factors
        }
        
        # New: Enhanced weights
        self.enhanced_weights = {
            # LuxAlgo integration
            'luxalgo_confirmation': 20,     # LuxAlgo signal confirmation
            'luxalgo_trend_alignment': 15,  # Trend catcher alignment
            'luxalgo_bias_boost': 10,       # Bias alignment multiplier
            
            # CoinGlass integration  
            'funding_rate_analysis': 12,    # Funding rate sentiment
            'open_interest_momentum': 15,   # OI breakout confirmation
            'liquidation_proximity': 8,     # Distance to liquidation levels
            
            # Market sentiment
            'long_short_sentiment': 10,     # L/S ratio contrarian filter
            'crowd_psychology': 8,          # Market psychology analysis
            'sentiment_extremes': 5         # Extreme sentiment penalty/bonus
        }
        
        # Thresholds for analysis
        self.thresholds = {
            'funding_rate_extreme': 0.1,    # 0.1% = extreme funding
            'funding_rate_moderate': 0.05,  # 0.05% = moderate funding
            'oi_breakout_threshold': 5,     # 5% OI increase for breakout
            'oi_fake_move_threshold': -2,   # 2% OI decrease = fake move
            'long_short_extreme': 3.0,      # L/S ratio > 3 = extreme
            'long_short_moderate': 2.0,     # L/S ratio > 2 = moderate
            'luxalgo_strong_threshold': 80, # LuxAlgo strength > 80 = strong
            'luxalgo_moderate_threshold': 60 # LuxAlgo strength > 60 = moderate
        }
    
    def calculate_luxalgo_score(self, 
                               luxalgo_signal: Optional[str],
                               luxalgo_strength: Optional[float], 
                               smc_bias: str,
                               luxalgo_indicator: Optional[str] = None) -> Dict[str, float]:
        """
        Calculate LuxAlgo-based scoring factors
        
        Args:
            luxalgo_signal: 'BUY', 'SELL', 'NEUTRAL' 
            luxalgo_strength: Signal strength 0-100
            smc_bias: Current SMC bias direction
            luxalgo_indicator: Specific indicator name
            
        Returns:
            Dict with LuxAlgo scoring components
        """
        try:
            scores = {
                'luxalgo_confirmation': 0,
                'luxalgo_trend_alignment': 0, 
                'luxalgo_bias_boost': 1.0  # Multiplier
            }
            
            if not luxalgo_signal or luxalgo_signal == 'NEUTRAL':
                return scores
                
            # Base confirmation score
            if luxalgo_strength and luxalgo_strength >= self.thresholds['luxalgo_strong_threshold']:
                scores['luxalgo_confirmation'] = 20  # Strong signal
            elif luxalgo_strength and luxalgo_strength >= self.thresholds['luxalgo_moderate_threshold']:
                scores['luxalgo_confirmation'] = 15  # Moderate signal
            else:
                scores['luxalgo_confirmation'] = 10  # Weak signal
                
            # Bias alignment bonus
            signal_direction = luxalgo_signal.upper()
            if ((signal_direction in ['BUY', 'LONG'] and smc_bias.lower() == 'bullish') or
                (signal_direction in ['SELL', 'SHORT'] and smc_bias.lower() == 'bearish')):
                
                scores['luxalgo_bias_boost'] = 1.2  # 20% bonus for alignment
                scores['luxalgo_trend_alignment'] = 15
                
                self.logger.info(f"LuxAlgo-SMC alignment: {signal_direction} + {smc_bias} = +20% bonus")
            else:
                scores['luxalgo_bias_boost'] = 0.8  # 20% penalty for misalignment
                scores['luxalgo_trend_alignment'] = -10
                
                self.logger.warning(f"LuxAlgo-SMC conflict: {signal_direction} vs {smc_bias} = -20% penalty")
            
            # Indicator-specific bonuses
            if luxalgo_indicator:
                indicator_bonuses = {
                    'Confirmation': 5,      # Confirmation indicator
                    'Trend Catcher': 8,     # Trend following
                    'Smart Money Concepts': 10,  # SMC-specific
                    'Order Flow': 7,        # Order flow analysis
                    'Market Structure': 6    # Structure analysis
                }
                
                bonus = indicator_bonuses.get(luxalgo_indicator, 0)
                scores['luxalgo_confirmation'] += bonus
                
            return scores
            
        except Exception as e:
            self.logger.error(f"LuxAlgo scoring error: {e}")
            return {'luxalgo_confirmation': 0, 'luxalgo_trend_alignment': 0, 'luxalgo_bias_boost': 1.0}
    
    def calculate_funding_rate_score(self, funding_rate: float, 
                                   funding_rate_8h: float,
                                   signal_direction: str) -> float:
        """
        Calculate funding rate-based score
        
        Penalizes trades against extreme funding, bonus for supportive funding
        """
        try:
            score = 0
            
            # Determine funding extremity
            abs_funding = abs(funding_rate)
            abs_funding_8h = abs(funding_rate_8h)
            
            # Extreme funding analysis
            if abs_funding >= self.thresholds['funding_rate_extreme']:
                # Very high funding rate - strong sentiment
                if funding_rate > 0:  # Longs paying shorts (bearish sentiment)
                    if signal_direction.upper() in ['SELL', 'SHORT']:
                        score += 12  # Bonus for selling into extreme long funding
                    else:
                        score -= 8   # Penalty for buying into extreme long funding
                else:  # Shorts paying longs (bullish sentiment)  
                    if signal_direction.upper() in ['BUY', 'LONG']:
                        score += 12  # Bonus for buying into extreme short funding
                    else:
                        score -= 8   # Penalty for selling into extreme short funding
                        
            elif abs_funding >= self.thresholds['funding_rate_moderate']:
                # Moderate funding - lighter weighting
                if funding_rate > 0 and signal_direction.upper() in ['SELL', 'SHORT']:
                    score += 6
                elif funding_rate < 0 and signal_direction.upper() in ['BUY', 'LONG']:
                    score += 6
                else:
                    score -= 3
                    
            # 8-hour funding trend analysis
            if abs_funding_8h >= self.thresholds['funding_rate_moderate']:
                funding_trend = 'increasing' if abs_funding > abs_funding_8h else 'decreasing'
                
                if funding_trend == 'increasing':
                    # Funding getting more extreme - fade the crowd
                    if funding_rate > 0 and signal_direction.upper() in ['SELL', 'SHORT']:
                        score += 5  # Fade the longs
                    elif funding_rate < 0 and signal_direction.upper() in ['BUY', 'LONG']:
                        score += 5  # Fade the shorts
                        
            self.logger.info(f"Funding rate analysis: {funding_rate:.4f}% -> score: {score}")
            return score
            
        except Exception as e:
            self.logger.error(f"Funding rate scoring error: {e}")
            return 0
    
    def calculate_open_interest_score(self, oi_current: float,
                                    oi_24h_change: float,
                                    price_breakout: bool,
                                    breakout_direction: str) -> float:
        """
        Calculate Open Interest delta score
        
        Bonus for breakouts with increasing OI (real moves)
        Penalty for breakouts with decreasing OI (fake moves)
        """
        try:
            score = 0
            
            if not price_breakout:
                return score
                
            # OI breakout confirmation
            if oi_24h_change >= self.thresholds['oi_breakout_threshold']:
                # Increasing OI during breakout = real move
                score += 15
                self.logger.info(f"OI breakout confirmation: +{oi_24h_change:.2f}% OI = +15 points")
                
                # Extra bonus for very strong OI increase
                if oi_24h_change >= 10:
                    score += 5
                    self.logger.info(f"Strong OI increase: +{oi_24h_change:.2f}% = +5 bonus points")
                    
            elif oi_24h_change <= self.thresholds['oi_fake_move_threshold']:
                # Decreasing OI during breakout = fake move
                score -= 12
                self.logger.warning(f"OI fake move signal: {oi_24h_change:.2f}% OI = -12 points")
                
                # Extra penalty for very weak OI
                if oi_24h_change <= -5:
                    score -= 8
                    self.logger.warning(f"Very weak OI: {oi_24h_change:.2f}% = -8 penalty points")
            
            # OI trend analysis
            if oi_24h_change > 0 and oi_current > 0:
                # Growing interest - momentum building
                momentum_bonus = min(5, oi_24h_change * 0.5)  # Cap at 5 points
                score += momentum_bonus
                
            return score
            
        except Exception as e:
            self.logger.error(f"Open Interest scoring error: {e}")
            return 0
    
    def calculate_long_short_sentiment_score(self, long_short_ratio: float,
                                           signal_direction: str) -> Tuple[float, float]:
        """
        Calculate Long/Short ratio sentiment score
        
        Returns: (score, sentiment_multiplier)
        """
        try:
            score = 0
            sentiment_multiplier = 1.0
            
            # Extreme sentiment analysis (contrarian approach)
            if long_short_ratio >= self.thresholds['long_short_extreme']:
                # Too many longs - bearish contrarian signal
                if signal_direction.upper() in ['SELL', 'SHORT']:
                    score += 10  # Bonus for contrarian trade
                    sentiment_multiplier = 1.1
                else:
                    score -= 8   # Penalty for following the crowd  
                    sentiment_multiplier = 0.9
                    
                self.logger.info(f"Extreme long sentiment: {long_short_ratio:.2f} - contrarian bonus/penalty applied")
                
            elif long_short_ratio <= (1 / self.thresholds['long_short_extreme']):
                # Too many shorts - bullish contrarian signal
                if signal_direction.upper() in ['BUY', 'LONG']:
                    score += 10  # Bonus for contrarian trade
                    sentiment_multiplier = 1.1
                else:
                    score -= 8   # Penalty for following the crowd
                    sentiment_multiplier = 0.9
                    
                self.logger.info(f"Extreme short sentiment: {long_short_ratio:.2f} - contrarian bonus/penalty applied")
                
            elif long_short_ratio >= self.thresholds['long_short_moderate']:
                # Moderate long bias
                if signal_direction.upper() in ['SELL', 'SHORT']:
                    score += 5   # Small contrarian bonus
                else:
                    score -= 3   # Small crowd penalty
                    
            elif long_short_ratio <= (1 / self.thresholds['long_short_moderate']):
                # Moderate short bias  
                if signal_direction.upper() in ['BUY', 'LONG']:
                    score += 5   # Small contrarian bonus
                else:
                    score -= 3   # Small crowd penalty
            
            return score, sentiment_multiplier
            
        except Exception as e:
            self.logger.error(f"Long/Short sentiment scoring error: {e}")
            return 0, 1.0
    
    def calculate_enhanced_signal_score(self, 
                                      base_score: float,
                                      market_data: MarketSentimentData,
                                      smc_analysis: Dict[str, Any],
                                      price_breakout: bool = False,
                                      breakout_direction: str = 'neutral') -> Dict[str, Any]:
        """
        Calculate complete enhanced signal score with all new factors
        
        Args:
            base_score: Existing signal score from SMC/technical analysis
            market_data: Market sentiment data including LuxAlgo and CoinGlass
            smc_analysis: SMC analysis results with bias direction
            price_breakout: Whether price is breaking out
            breakout_direction: Direction of breakout ('up', 'down', 'neutral')
            
        Returns:
            Complete scoring breakdown with final enhanced score
        """
        try:
            # Initialize scoring factors
            factors = ScoringFactors()
            
            # Set base scores from existing system
            factors.smc_structure_score = base_score * 0.4
            factors.technical_indicators_score = base_score * 0.3
            factors.volume_profile_score = base_score * 0.3
            
            # Determine signal direction from SMC analysis
            smc_bias = smc_analysis.get('bias', 'neutral')
            signal_direction = smc_analysis.get('recommended_action', 'HOLD')
            
            # Calculate LuxAlgo scores
            luxalgo_scores = self.calculate_luxalgo_score(
                market_data.luxalgo_signal,
                market_data.luxalgo_strength, 
                smc_bias,
                market_data.luxalgo_indicator
            )
            
            factors.luxalgo_confirmation_score = luxalgo_scores['luxalgo_confirmation']
            factors.luxalgo_trend_catcher_score = luxalgo_scores['luxalgo_trend_alignment'] 
            factors.luxalgo_bias_alignment = luxalgo_scores['luxalgo_bias_boost']
            
            # Calculate funding rate score
            factors.funding_rate_score = self.calculate_funding_rate_score(
                market_data.funding_rate,
                market_data.funding_rate_8h,
                signal_direction
            )
            
            # Calculate Open Interest score
            factors.open_interest_delta_score = self.calculate_open_interest_score(
                market_data.open_interest,
                market_data.open_interest_24h_change,
                price_breakout,
                breakout_direction
            )
            
            # Calculate Long/Short sentiment score
            sentiment_score, sentiment_multiplier = self.calculate_long_short_sentiment_score(
                market_data.long_short_ratio,
                signal_direction
            )
            
            factors.long_short_ratio_score = sentiment_score
            factors.market_sentiment_filter = sentiment_multiplier
            
            # Calculate total enhanced score
            enhanced_components = (
                factors.luxalgo_confirmation_score +
                factors.luxalgo_trend_catcher_score +
                factors.funding_rate_score +
                factors.open_interest_delta_score +
                factors.long_short_ratio_score
            )
            
            # Apply LuxAlgo bias alignment multiplier
            base_with_luxalgo = base_score * factors.luxalgo_bias_alignment
            
            # Apply market sentiment filter
            final_score = (base_with_luxalgo + enhanced_components) * factors.market_sentiment_filter
            
            # Ensure score stays within reasonable bounds (0-100)
            final_score = max(0, min(100, final_score))
            
            # Comprehensive result
            result = {
                'final_enhanced_score': final_score,
                'base_score': base_score,
                'enhancement_delta': final_score - base_score,
                'scoring_factors': factors,
                'analysis_breakdown': {
                    'luxalgo_integration': {
                        'signal': market_data.luxalgo_signal,
                        'strength': market_data.luxalgo_strength,
                        'bias_alignment': factors.luxalgo_bias_alignment,
                        'total_contribution': factors.luxalgo_confirmation_score + factors.luxalgo_trend_catcher_score
                    },
                    'coinglass_integration': {
                        'funding_rate': market_data.funding_rate,
                        'funding_contribution': factors.funding_rate_score,
                        'oi_change': market_data.open_interest_24h_change,
                        'oi_contribution': factors.open_interest_delta_score
                    },
                    'market_sentiment': {
                        'long_short_ratio': market_data.long_short_ratio,
                        'sentiment_score': factors.long_short_ratio_score,
                        'sentiment_multiplier': factors.market_sentiment_filter,
                        'sentiment_impact': 'contrarian' if sentiment_score > 0 else 'crowd_following'
                    }
                },
                'enhancement_summary': {
                    'luxalgo_boost': factors.luxalgo_confirmation_score > 0,
                    'funding_supportive': factors.funding_rate_score > 0,
                    'oi_confirmation': factors.open_interest_delta_score > 0,
                    'sentiment_contrarian': factors.long_short_ratio_score > 0,
                    'overall_enhancement': 'positive' if final_score > base_score else 'negative'
                },
                'confidence_adjustments': {
                    'high_confidence_factors': [],
                    'risk_factors': [],
                    'neutral_factors': []
                }
            }
            
            # Categorize confidence factors
            if factors.luxalgo_confirmation_score >= 15:
                result['confidence_adjustments']['high_confidence_factors'].append('Strong LuxAlgo signal')
            if factors.funding_rate_score >= 8:
                result['confidence_adjustments']['high_confidence_factors'].append('Supportive funding rate')
            if factors.open_interest_delta_score >= 10:
                result['confidence_adjustments']['high_confidence_factors'].append('OI breakout confirmation')
            if factors.long_short_ratio_score >= 8:
                result['confidence_adjustments']['high_confidence_factors'].append('Contrarian sentiment opportunity')
                
            # Risk factors
            if factors.funding_rate_score <= -5:
                result['confidence_adjustments']['risk_factors'].append('Funding rate working against position')
            if factors.open_interest_delta_score <= -8:
                result['confidence_adjustments']['risk_factors'].append('Potential fake breakout (weak OI)')
            if factors.luxalgo_bias_alignment <= 0.9:
                result['confidence_adjustments']['risk_factors'].append('LuxAlgo-SMC bias misalignment')
                
            self.logger.info(f"Enhanced scoring complete: {base_score:.1f} -> {final_score:.1f} (delta: {final_score-base_score:.1f})")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Enhanced scoring calculation error: {e}")
            return {
                'final_enhanced_score': base_score,
                'base_score': base_score,
                'enhancement_delta': 0,
                'error': str(e)
            }

# Global enhanced scoring engine
enhanced_scorer = EnhancedScoringEngine()

def get_enhanced_scoring_engine():
    """Get the global enhanced scoring engine"""
    return enhanced_scorer

if __name__ == "__main__":
    # Test enhanced scoring engine
    engine = EnhancedScoringEngine()
    
    # Test data
    test_market_data = MarketSentimentData(
        funding_rate=0.08,           # High positive funding (longs paying)
        funding_rate_8h=0.06,       # Increasing funding trend
        open_interest=1500000000,   # 1.5B OI
        open_interest_24h_change=8.5, # 8.5% increase
        long_short_ratio=3.2,       # Extremely long-biased
        liquidation_volume_24h=45000000,
        luxalgo_signal='SELL',      # LuxAlgo selling signal
        luxalgo_strength=85,        # Strong signal
        luxalgo_indicator='Confirmation'
    )
    
    test_smc_analysis = {
        'bias': 'bearish',
        'recommended_action': 'SELL',
        'confidence': 75
    }
    
    # Calculate enhanced score
    base_score = 65  # Example base score
    result = engine.calculate_enhanced_signal_score(
        base_score=base_score,
        market_data=test_market_data,
        smc_analysis=test_smc_analysis,
        price_breakout=True,
        breakout_direction='down'
    )
    
    print("Enhanced Scoring Engine Test")
    print("=" * 50)
    print(f"Base Score: {base_score}")
    print(f"Enhanced Score: {result['final_enhanced_score']:.1f}")
    print(f"Enhancement Delta: {result['enhancement_delta']:.1f}")
    print(f"\nKey Factors:")
    print(f"  LuxAlgo Contribution: {result['analysis_breakdown']['luxalgo_integration']['total_contribution']}")
    print(f"  Funding Rate Score: {result['analysis_breakdown']['coinglass_integration']['funding_contribution']}")
    print(f"  OI Delta Score: {result['analysis_breakdown']['coinglass_integration']['oi_contribution']}")
    print(f"  Sentiment Score: {result['analysis_breakdown']['market_sentiment']['sentiment_score']}")
    print(f"\nHigh Confidence Factors: {result['confidence_adjustments']['high_confidence_factors']}")
    print(f"Risk Factors: {result['confidence_adjustments']['risk_factors']}")