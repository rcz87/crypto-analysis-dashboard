#!/usr/bin/env python3
"""
BiasBuilder: SMC Market Bias Determination Module
Menentukan market bias dari kombinasi CHoCH, BOS, dan trend struktur
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class MarketBias(Enum):
    """Market bias enumeration"""
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"
    MIXED = "mixed"

@dataclass
class BiasSignal:
    """Structure for bias determination signals"""
    bias: MarketBias
    strength: float  # 0.0 - 1.0
    confidence: float  # 0.0 - 1.0
    timeframe: str
    timestamp: int
    contributing_factors: List[str]
    choch_count: int
    bos_count: int
    trend_alignment: str
    description: str

class BiasBuilder:
    """
    🧠 SMC Market Bias Builder
    
    Menentukan market bias melalui analisis komprehensif:
    - CHoCH (Change of Character) patterns
    - BOS (Break of Structure) patterns  
    - Trend structure alignment
    - Multi-timeframe confluence
    - Volume confirmation
    """
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.BiasBuilder")
        
        # Configuration parameters
        self.lookback_periods = 20  # periods untuk analisis
        self.min_confidence_threshold = 0.6
        self.choch_weight = 0.4
        self.bos_weight = 0.4  
        self.trend_weight = 0.2
        
        self.logger.info("🧠 BiasBuilder initialized with SMC bias determination")
    
    def determine_market_bias(self, data: List[Dict], 
                            choch_signals: List[Dict],
                            bos_signals: List[Dict],
                            swing_points: Dict[str, List[Dict]],
                            timeframe: str = "1H") -> BiasSignal:
        """
        Determine comprehensive market bias from SMC components
        
        Args:
            data: OHLCV price data
            choch_signals: Change of Character signals
            bos_signals: Break of Structure signals
            swing_points: Swing highs and lows
            timeframe: Analysis timeframe
            
        Returns:
            BiasSignal with complete bias determination
        """
        try:
            self.logger.info(f"🔍 Determining market bias for {timeframe}")
            
            # Filter recent signals
            recent_timestamp = self._get_recent_timestamp()
            recent_choch = self._filter_recent_signals(choch_signals, recent_timestamp)
            recent_bos = self._filter_recent_signals(bos_signals, recent_timestamp)
            
            # Analyze CHoCH patterns
            choch_bias, choch_strength = self._analyze_choch_bias(recent_choch)
            
            # Analyze BOS patterns
            bos_bias, bos_strength = self._analyze_bos_bias(recent_bos)
            
            # Analyze trend structure
            trend_bias, trend_strength = self._analyze_trend_structure(data, swing_points)
            
            # Calculate weighted bias
            overall_bias, overall_strength, confidence = self._calculate_weighted_bias(
                choch_bias, choch_strength,
                bos_bias, bos_strength, 
                trend_bias, trend_strength
            )
            
            # Generate contributing factors
            factors = self._identify_contributing_factors(
                recent_choch, recent_bos, choch_bias, bos_bias, trend_bias
            )
            
            # Create bias signal
            bias_signal = BiasSignal(
                bias=overall_bias,
                strength=overall_strength,
                confidence=confidence,
                timeframe=timeframe,
                timestamp=int(datetime.now().timestamp() * 1000),
                contributing_factors=factors,
                choch_count=len(recent_choch),
                bos_count=len(recent_bos),
                trend_alignment=self._get_trend_alignment(choch_bias, bos_bias, trend_bias),
                description=self._generate_bias_description(overall_bias, overall_strength, confidence, factors)
            )
            
            self.logger.info(f"✅ Market bias determined: {overall_bias.value.upper()} ({overall_strength:.1%} strength)")
            
            return bias_signal
            
        except Exception as e:
            self.logger.error(f"❌ Error determining market bias: {e}")
            return self._get_default_bias_signal(timeframe)
    
    def _get_recent_timestamp(self, hours_back: int = 24) -> int:
        """Get timestamp for filtering recent signals"""
        return int((datetime.now() - timedelta(hours=hours_back)).timestamp() * 1000)
    
    def _filter_recent_signals(self, signals: List[Dict], timestamp_threshold: int) -> List[Dict]:
        """Filter signals to recent timeframe"""
        return [signal for signal in signals if signal.get('timestamp', 0) > timestamp_threshold]
    
    def _analyze_choch_bias(self, choch_signals: List[Dict]) -> Tuple[MarketBias, float]:
        """
        Analyze CHoCH signals for bias determination
        
        Returns:
            Tuple of (bias, strength)
        """
        if not choch_signals:
            return MarketBias.NEUTRAL, 0.0
        
        bullish_choch = sum(1 for signal in choch_signals if signal.get('direction') == 'bullish')
        bearish_choch = sum(1 for signal in choch_signals if signal.get('direction') == 'bearish')
        
        total_signals = len(choch_signals)
        
        if bullish_choch > bearish_choch:
            strength = bullish_choch / total_signals
            return MarketBias.BULLISH, strength
        elif bearish_choch > bullish_choch:
            strength = bearish_choch / total_signals
            return MarketBias.BEARISH, strength
        else:
            return MarketBias.NEUTRAL, 0.5
    
    def _analyze_bos_bias(self, bos_signals: List[Dict]) -> Tuple[MarketBias, float]:
        """
        Analyze BOS signals for bias determination
        
        Returns:
            Tuple of (bias, strength)
        """
        if not bos_signals:
            return MarketBias.NEUTRAL, 0.0
        
        bullish_bos = sum(1 for signal in bos_signals if signal.get('direction') == 'bullish')
        bearish_bos = sum(1 for signal in bos_signals if signal.get('direction') == 'bearish')
        
        total_signals = len(bos_signals)
        
        if bullish_bos > bearish_bos:
            strength = bullish_bos / total_signals
            return MarketBias.BULLISH, strength
        elif bearish_bos > bullish_bos:
            strength = bearish_bos / total_signals
            return MarketBias.BEARISH, strength
        else:
            return MarketBias.NEUTRAL, 0.5
    
    def _analyze_trend_structure(self, data: List[Dict], swing_points: Dict[str, List[Dict]]) -> Tuple[MarketBias, float]:
        """
        Analyze overall trend structure
        
        Returns:
            Tuple of (bias, strength)
        """
        try:
            recent_highs = swing_points.get('swing_highs', [])[-5:]  # Last 5 highs
            recent_lows = swing_points.get('swing_lows', [])[-5:]   # Last 5 lows
            
            if len(recent_highs) < 2 or len(recent_lows) < 2:
                return MarketBias.NEUTRAL, 0.0
            
            # Check for higher highs and higher lows (bullish structure)
            higher_highs = self._count_higher_structures(recent_highs)
            higher_lows = self._count_higher_structures(recent_lows)
            
            # Check for lower highs and lower lows (bearish structure)
            lower_highs = self._count_lower_structures(recent_highs)
            lower_lows = self._count_lower_structures(recent_lows)
            
            bullish_structure = higher_highs + higher_lows
            bearish_structure = lower_highs + lower_lows
            
            total_structure = bullish_structure + bearish_structure
            
            if total_structure == 0:
                return MarketBias.NEUTRAL, 0.0
            
            if bullish_structure > bearish_structure:
                strength = bullish_structure / total_structure
                return MarketBias.BULLISH, strength
            elif bearish_structure > bullish_structure:
                strength = bearish_structure / total_structure
                return MarketBias.BEARISH, strength
            else:
                return MarketBias.NEUTRAL, 0.5
                
        except Exception as e:
            self.logger.warning(f"⚠️ Error analyzing trend structure: {e}")
            return MarketBias.NEUTRAL, 0.0
    
    def _count_higher_structures(self, structures: List[Dict]) -> int:
        """Count higher highs or higher lows"""
        if len(structures) < 2:
            return 0
        
        count = 0
        for i in range(1, len(structures)):
            current_price = self._safe_get_price(structures[i])
            previous_price = self._safe_get_price(structures[i-1])
            
            if current_price > previous_price:
                count += 1
        
        return count
    
    def _count_lower_structures(self, structures: List[Dict]) -> int:
        """Count lower highs or lower lows"""
        if len(structures) < 2:
            return 0
        
        count = 0
        for i in range(1, len(structures)):
            current_price = self._safe_get_price(structures[i])
            previous_price = self._safe_get_price(structures[i-1])
            
            if current_price < previous_price:
                count += 1
        
        return count
    
    def _safe_get_price(self, structure: Dict) -> float:
        """Safely extract price from structure"""
        price_keys = ['price', 'high', 'low', 'close', 'level']
        for key in price_keys:
            if key in structure and structure[key] is not None:
                return float(structure[key])
        return 0.0
    
    def _calculate_weighted_bias(self, choch_bias: MarketBias, choch_strength: float,
                               bos_bias: MarketBias, bos_strength: float,
                               trend_bias: MarketBias, trend_strength: float) -> Tuple[MarketBias, float, float]:
        """
        Calculate weighted overall bias
        
        Returns:
            Tuple of (bias, strength, confidence)
        """
        # Convert bias to numeric score
        bias_scores = {
            MarketBias.BULLISH: 1.0,
            MarketBias.BEARISH: -1.0,
            MarketBias.NEUTRAL: 0.0,
            MarketBias.MIXED: 0.0
        }
        
        choch_score = bias_scores[choch_bias] * choch_strength * self.choch_weight
        bos_score = bias_scores[bos_bias] * bos_strength * self.bos_weight
        trend_score = bias_scores[trend_bias] * trend_strength * self.trend_weight
        
        weighted_score = choch_score + bos_score + trend_score
        
        # Determine overall bias
        if weighted_score > 0.1:
            overall_bias = MarketBias.BULLISH
        elif weighted_score < -0.1:
            overall_bias = MarketBias.BEARISH
        else:
            overall_bias = MarketBias.NEUTRAL
        
        # Calculate strength and confidence
        overall_strength = abs(weighted_score)
        
        # Confidence based on alignment of components
        alignment_count = 0
        if choch_bias == overall_bias:
            alignment_count += 1
        if bos_bias == overall_bias:
            alignment_count += 1
        if trend_bias == overall_bias:
            alignment_count += 1
        
        confidence = alignment_count / 3.0  # 3 components
        
        return overall_bias, overall_strength, confidence
    
    def _identify_contributing_factors(self, choch_signals: List[Dict], bos_signals: List[Dict],
                                     choch_bias: MarketBias, bos_bias: MarketBias, 
                                     trend_bias: MarketBias) -> List[str]:
        """Identify factors contributing to bias determination"""
        factors = []
        
        if choch_signals:
            factors.append(f"CHoCH signals: {len(choch_signals)} ({choch_bias.value})")
        
        if bos_signals:
            factors.append(f"BOS signals: {len(bos_signals)} ({bos_bias.value})")
        
        factors.append(f"Trend structure: {trend_bias.value}")
        
        return factors
    
    def _get_trend_alignment(self, choch_bias: MarketBias, bos_bias: MarketBias, 
                           trend_bias: MarketBias) -> str:
        """Get trend alignment description"""
        biases = [choch_bias, bos_bias, trend_bias]
        
        if all(bias == MarketBias.BULLISH for bias in biases):
            return "fully_aligned_bullish"
        elif all(bias == MarketBias.BEARISH for bias in biases):
            return "fully_aligned_bearish"
        elif biases.count(MarketBias.BULLISH) > biases.count(MarketBias.BEARISH):
            return "mostly_bullish"
        elif biases.count(MarketBias.BEARISH) > biases.count(MarketBias.BULLISH):
            return "mostly_bearish"
        else:
            return "mixed_signals"
    
    def _generate_bias_description(self, bias: MarketBias, strength: float, 
                                 confidence: float, factors: List[str]) -> str:
        """Generate human-readable bias description"""
        strength_desc = "strong" if strength > 0.7 else "moderate" if strength > 0.4 else "weak"
        confidence_desc = "high" if confidence > 0.7 else "medium" if confidence > 0.5 else "low"
        
        description = f"{bias.value.title()} bias with {strength_desc} strength ({strength:.1%}) and {confidence_desc} confidence ({confidence:.1%}). "
        description += f"Contributing factors: {', '.join(factors[:3])}"  # Top 3 factors
        
        return description
    
    def _get_default_bias_signal(self, timeframe: str) -> BiasSignal:
        """Get default bias signal in case of errors"""
        return BiasSignal(
            bias=MarketBias.NEUTRAL,
            strength=0.0,
            confidence=0.0,
            timeframe=timeframe,
            timestamp=int(datetime.now().timestamp() * 1000),
            contributing_factors=["Error in bias calculation"],
            choch_count=0,
            bos_count=0,
            trend_alignment="unknown",
            description="Unable to determine market bias due to calculation error"
        )
    
    def get_bias_summary(self, bias_signal: BiasSignal) -> Dict[str, Any]:
        """
        Get summary of bias analysis for external use
        
        Returns:
            Dictionary with bias summary
        """
        return {
            "bias": bias_signal.bias.value,
            "strength": bias_signal.strength,
            "confidence": bias_signal.confidence,
            "timeframe": bias_signal.timeframe,
            "timestamp": bias_signal.timestamp,
            "choch_count": bias_signal.choch_count,
            "bos_count": bias_signal.bos_count,
            "trend_alignment": bias_signal.trend_alignment,
            "contributing_factors": bias_signal.contributing_factors,
            "description": bias_signal.description,
            "trade_direction": self._get_trade_direction(bias_signal),
            "risk_level": self._assess_risk_level(bias_signal)
        }
    
    def _get_trade_direction(self, bias_signal: BiasSignal) -> str:
        """Get recommended trade direction based on bias"""
        if bias_signal.bias == MarketBias.BULLISH and bias_signal.confidence > 0.6:
            return "LONG"
        elif bias_signal.bias == MarketBias.BEARISH and bias_signal.confidence > 0.6:
            return "SHORT"
        else:
            return "NEUTRAL"
    
    def _assess_risk_level(self, bias_signal: BiasSignal) -> str:
        """Assess risk level based on bias characteristics"""
        if bias_signal.confidence > 0.8 and bias_signal.strength > 0.7:
            return "LOW"
        elif bias_signal.confidence > 0.6 and bias_signal.strength > 0.5:
            return "MEDIUM"
        else:
            return "HIGH"