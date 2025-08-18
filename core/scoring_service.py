#!/usr/bin/env python3
"""
ScoringService - Confluence scoring engine for signal quality
Menggunakan multiple faktor untuk menilai kualitas sinyal (0-100)
"""
import logging
import time
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass
import numpy as np

logger = logging.getLogger(__name__)

@dataclass
class ScoreBreakdown:
    smc_score: float = 0.0      # 40 points max
    orderbook_score: float = 0.0 # 20 points max
    volatility_score: float = 0.0 # 10 points max
    momentum_score: float = 0.0   # 15 points max
    funding_score: float = 0.0    # 10 points max
    news_score: float = 0.0       # 5 points max
    total: float = 0.0

@dataclass
class ScoredSignal:
    signal: str  # BUY/SELL
    score: float # 0-100
    reasons: List[str]
    levels: Dict[str, float]
    breakdown: ScoreBreakdown
    confidence: str  # LOW/MEDIUM/HIGH

class ScoringService:
    def __init__(self):
        self.thresholds = {
            'sharp_signal': 70.0,  # Sinyal tajam minimal 70
            'good_signal': 60.0,   # Sinyal bagus minimal 60
            'weak_signal': 40.0    # Di bawah ini skip
        }
        
    def score_signal(self, 
                    smc_analysis: Dict[str, Any],
                    orderbook_data: Dict[str, Any] = None,
                    market_data: Dict[str, Any] = None,
                    funding_data: Dict[str, Any] = None,
                    news_data: Dict[str, Any] = None) -> ScoredSignal:
        """
        Score confluence dari berbagai faktor
        """
        try:
            breakdown = ScoreBreakdown()
            reasons = []
            
            # 1. SMC Score (40 points max)
            smc_score, smc_reasons = self._score_smc(smc_analysis)
            breakdown.smc_score = smc_score
            reasons.extend(smc_reasons)
            
            # 2. Orderbook Score (20 points max)
            if orderbook_data:
                ob_score, ob_reasons = self._score_orderbook(orderbook_data)
                breakdown.orderbook_score = ob_score
                reasons.extend(ob_reasons)
            
            # 3. Volatility & ATR Score (10 points max)
            if market_data:
                vol_score, vol_reasons = self._score_volatility(market_data)
                breakdown.volatility_score = vol_score
                reasons.extend(vol_reasons)
            
            # 4. Momentum Score (15 points max)
            if market_data:
                momentum_score, mom_reasons = self._score_momentum(market_data)
                breakdown.momentum_score = momentum_score
                reasons.extend(mom_reasons)
            
            # 5. Funding/OI Score (10 points max)
            if funding_data:
                funding_score, fund_reasons = self._score_funding(funding_data)
                breakdown.funding_score = funding_score
                reasons.extend(fund_reasons)
            
            # 6. News Score (5 points max)
            if news_data:
                news_score, news_reasons = self._score_news(news_data)
                breakdown.news_score = news_score
                reasons.extend(news_reasons)
            
            # Calculate total
            total_score = (breakdown.smc_score + breakdown.orderbook_score + 
                          breakdown.volatility_score + breakdown.momentum_score +
                          breakdown.funding_score + breakdown.news_score)
            
            breakdown.total = min(total_score, 100.0)
            
            # Determine signal direction and confidence
            signal_direction = smc_analysis.get('market_bias', 'NEUTRAL')
            if signal_direction == 'bullish':
                signal = 'BUY'
            elif signal_direction == 'bearish':
                signal = 'SELL'
            else:
                signal = 'HOLD'
            
            # Confidence levels
            if breakdown.total >= self.thresholds['sharp_signal']:
                confidence = 'HIGH'
            elif breakdown.total >= self.thresholds['good_signal']:
                confidence = 'MEDIUM'
            else:
                confidence = 'LOW'
            
            # Extract key levels
            levels = self._extract_levels(smc_analysis, market_data)
            
            return ScoredSignal(
                signal=signal,
                score=breakdown.total,
                reasons=reasons[:8],  # Top 8 reasons
                levels=levels,
                breakdown=breakdown,
                confidence=confidence
            )
            
        except Exception as e:
            logger.error(f"Scoring error: {e}")
            return self._fallback_signal()
    
    def _score_smc(self, smc_analysis: Dict[str, Any]) -> Tuple[float, List[str]]:
        """Score SMC factors (40 points max)"""
        score = 0.0
        reasons = []
        
        try:
            # Structure break (15 points)
            if smc_analysis.get('structure_analysis', {}).get('structure_break'):
                score += 15.0
                reasons.append("Strong structure break detected")
            
            # Order blocks (10 points)
            ob_quality = smc_analysis.get('order_blocks', {}).get('quality', 0)
            if ob_quality > 0.7:
                score += 10.0
                reasons.append("High-quality order blocks")
            elif ob_quality > 0.5:
                score += 5.0
                reasons.append("Decent order blocks")
            
            # Fair Value Gaps (8 points)
            fvg_count = len(smc_analysis.get('fvg_analysis', {}).get('gaps', []))
            if fvg_count >= 2:
                score += 8.0
                reasons.append("Multiple FVGs supporting direction")
            elif fvg_count == 1:
                score += 4.0
                reasons.append("FVG supporting direction")
            
            # Market bias confidence (7 points)
            confidence = smc_analysis.get('confidence', 0)
            if confidence > 0.8:
                score += 7.0
                reasons.append("Very high SMC confidence")
            elif confidence > 0.6:
                score += 4.0
                reasons.append("Good SMC confidence")
            
        except Exception as e:
            logger.warning(f"SMC scoring error: {e}")
        
        return score, reasons
    
    def _score_orderbook(self, orderbook_data: Dict[str, Any]) -> Tuple[float, List[str]]:
        """Score orderbook imbalance (20 points max)"""
        score = 0.0
        reasons = []
        
        try:
            bids = orderbook_data.get('bids', [])
            asks = orderbook_data.get('asks', [])
            
            if not bids or not asks:
                return score, reasons
            
            # Calculate imbalance
            total_bid_vol = sum(float(bid[1]) for bid in bids[:10])
            total_ask_vol = sum(float(ask[1]) for ask in asks[:10])
            
            if total_bid_vol + total_ask_vol > 0:
                imbalance = (total_bid_vol - total_ask_vol) / (total_bid_vol + total_ask_vol)
                
                # Strong imbalance (20 points)
                if abs(imbalance) > 0.3:
                    score += 20.0
                    direction = "Bullish" if imbalance > 0 else "Bearish"
                    reasons.append(f"Strong {direction.lower()} orderbook imbalance")
                elif abs(imbalance) > 0.15:
                    score += 10.0
                    direction = "Bullish" if imbalance > 0 else "Bearish"
                    reasons.append(f"Moderate {direction.lower()} orderbook imbalance")
                
                # Check spread
                spread = float(asks[0][0]) - float(bids[0][0])
                spread_pct = spread / float(bids[0][0]) * 100
                
                if spread_pct < 0.02:  # Tight spread
                    score += 5.0
                    reasons.append("Tight bid-ask spread")
            
        except Exception as e:
            logger.warning(f"Orderbook scoring error: {e}")
        
        return score, reasons
    
    def _score_volatility(self, market_data: Dict[str, Any]) -> Tuple[float, List[str]]:
        """Score volatility conditions (10 points max)"""
        score = 0.0
        reasons = []
        
        try:
            # Mock volatility analysis - in production would use ATR
            vol_regime = market_data.get('volatility_regime', 'normal')
            
            if vol_regime == 'normal':
                score += 10.0
                reasons.append("Optimal volatility conditions")
            elif vol_regime == 'low':
                score += 6.0
                reasons.append("Low volatility - limited profit potential")
            else:  # high volatility
                score += 3.0
                reasons.append("High volatility - increased risk")
                
        except Exception as e:
            logger.warning(f"Volatility scoring error: {e}")
        
        return score, reasons
    
    def _score_momentum(self, market_data: Dict[str, Any]) -> Tuple[float, List[str]]:
        """Score momentum indicators (15 points max)"""
        score = 0.0
        reasons = []
        
        try:
            # Mock momentum scoring - would use real indicators
            momentum_strength = market_data.get('momentum', {}).get('strength', 0.5)
            
            if momentum_strength > 0.7:
                score += 15.0
                reasons.append("Strong momentum alignment")
            elif momentum_strength > 0.5:
                score += 8.0
                reasons.append("Moderate momentum")
            else:
                score += 2.0
                reasons.append("Weak momentum")
                
        except Exception as e:
            logger.warning(f"Momentum scoring error: {e}")
        
        return score, reasons
    
    def _score_funding(self, funding_data: Dict[str, Any]) -> Tuple[float, List[str]]:
        """Score funding rate conditions (10 points max)"""
        score = 0.0
        reasons = []
        
        try:
            funding_rate = funding_data.get('funding_rate', 0)
            
            # Extreme funding rates can be contrarian signals
            if abs(funding_rate) > 0.0005:  # 0.05%
                score += 10.0
                direction = "bearish" if funding_rate > 0 else "bullish"
                reasons.append(f"Extreme funding suggests {direction} sentiment")
            elif abs(funding_rate) > 0.0002:  # 0.02%
                score += 5.0
                reasons.append("Notable funding rate bias")
                
        except Exception as e:
            logger.warning(f"Funding scoring error: {e}")
        
        return score, reasons
    
    def _score_news(self, news_data: Dict[str, Any]) -> Tuple[float, List[str]]:
        """Score news sentiment (5 points max)"""
        score = 0.0
        reasons = []
        
        try:
            sentiment = news_data.get('sentiment', {}).get('overall', 0)
            
            if abs(sentiment) > 0.3:
                score += 5.0
                direction = "bullish" if sentiment > 0 else "bearish"
                reasons.append(f"Strong {direction} news sentiment")
            elif abs(sentiment) > 0.1:
                score += 2.0
                reasons.append("Notable news sentiment")
                
        except Exception as e:
            logger.warning(f"News scoring error: {e}")
        
        return score, reasons
    
    def _extract_levels(self, smc_analysis: Dict[str, Any], market_data: Dict[str, Any] = None) -> Dict[str, float]:
        """Extract key price levels"""
        levels = {}
        
        try:
            # From SMC analysis
            if 'order_blocks' in smc_analysis:
                ob_data = smc_analysis['order_blocks']
                if 'bullish' in ob_data and ob_data['bullish']:
                    levels['support'] = float(ob_data['bullish'][0].get('price', 0))
                if 'bearish' in ob_data and ob_data['bearish']:
                    levels['resistance'] = float(ob_data['bearish'][0].get('price', 0))
            
            # Current price estimate
            if market_data and 'current_price' in market_data:
                levels['current'] = float(market_data['current_price'])
                
        except Exception as e:
            logger.warning(f"Level extraction error: {e}")
        
        return levels
    
    def _fallback_signal(self) -> ScoredSignal:
        """Fallback signal when scoring fails"""
        return ScoredSignal(
            signal='HOLD',
            score=0.0,
            reasons=['Scoring system error - no signal generated'],
            levels={},
            breakdown=ScoreBreakdown(),
            confidence='LOW'
        )
    
    def is_sharp_signal(self, scored_signal: ScoredSignal) -> bool:
        """Check if signal qualifies as 'sharp' (tajam)"""
        return scored_signal.score >= self.thresholds['sharp_signal']
    
    def should_trade(self, scored_signal: ScoredSignal) -> bool:
        """Determine if signal is worth trading"""
        return (scored_signal.score >= self.thresholds['weak_signal'] and 
                scored_signal.signal != 'HOLD')