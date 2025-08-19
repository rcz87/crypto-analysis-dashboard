#!/usr/bin/env python3
"""
AI Reasoning Integration - Integrasi Enhanced Reasoning Engine ke sistem trading
Menggabungkan sistem reasoning yang jelas dengan komponen AI yang sudah ada
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import pandas as pd

from .enhanced_reasoning_engine import (
    enhanced_reasoning_engine, 
    MarketFactors, 
    ReasoningResult,
    ReasoningConfidence
)
from .ai_engine import AIEngine
from .enhanced_ai_engine import EnhancedAIEngine
from .narrative_ai import NarrativeAI

logger = logging.getLogger(__name__)

class AIReasoningIntegrator:
    """
    AI Reasoning Integrator - Menggabungkan semua komponen AI reasoning
    untuk analisis trading yang jelas dan tidak halusinasi
    """
    
    def __init__(self):
        """Initialize AI Reasoning Integrator"""
        self.enhanced_reasoning = enhanced_reasoning_engine
        self.ai_engine = AIEngine()
        self.enhanced_ai_engine = EnhancedAIEngine()
        self.narrative_ai = NarrativeAI()
        
        # Configuration
        self.min_confidence_threshold = 60.0  # Minimum confidence untuk actionable signals
        self.use_ai_enhancement = True  # Toggle AI enhancement
        
        logger.info("🧠 AI Reasoning Integrator initialized")
    
    def analyze_trading_opportunity(self, 
                                  market_data: Dict[str, Any],
                                  smc_analysis: Dict[str, Any],
                                  technical_indicators: Dict[str, Any],
                                  symbol: str,
                                  timeframe: str,
                                  additional_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Comprehensive trading opportunity analysis dengan enhanced reasoning
        
        Args:
            market_data: Raw market data (OHLCV)
            smc_analysis: SMC analysis results
            technical_indicators: Technical indicators data
            symbol: Trading symbol
            timeframe: Analysis timeframe
            additional_context: Additional market context (optional)
            
        Returns:
            Comprehensive analysis dengan reasoning chain
        """
        try:
            logger.info(f"🔍 Starting comprehensive analysis for {symbol} {timeframe}")
            
            # 1. Prepare market factors
            market_factors = self._prepare_market_factors(
                market_data, smc_analysis, technical_indicators, additional_context
            )
            
            # 2. Enhanced reasoning analysis
            reasoning_result = self.enhanced_reasoning.analyze_market_factors(
                market_factors, symbol, timeframe
            )
            
            # 3. Generate AI narrative if confidence is sufficient
            narrative = self._generate_enhanced_narrative(
                reasoning_result, market_data, smc_analysis, symbol, timeframe
            )
            
            # 4. Create actionable recommendation
            recommendation = self._create_actionable_recommendation(
                reasoning_result, market_data, symbol, timeframe
            )
            
            # 5. Compile comprehensive result
            analysis_result = {
                'timestamp': datetime.now().isoformat(),
                'symbol': symbol,
                'timeframe': timeframe,
                'reasoning_result': {
                    'conclusion': reasoning_result.conclusion,
                    'confidence': reasoning_result.confidence.value,
                    'confidence_score': reasoning_result.confidence_score,
                    'evidence': reasoning_result.evidence,
                    'reasoning_chain': reasoning_result.reasoning_chain,
                    'uncertainty_factors': reasoning_result.uncertainty_factors
                },
                'narrative': narrative,
                'recommendation': recommendation,
                'analysis_quality': self._assess_analysis_quality(reasoning_result),
                'metadata': {
                    'data_sources': reasoning_result.data_sources,
                    'analysis_timestamp': reasoning_result.timestamp,
                    'min_confidence_threshold': self.min_confidence_threshold,
                    'ai_enhancement_used': self.use_ai_enhancement
                }
            }
            
            logger.info(f"✅ Analysis completed for {symbol} - {reasoning_result.conclusion} with {reasoning_result.confidence_score:.1f}% confidence")
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error in trading opportunity analysis: {e}")
            return self._create_error_analysis(symbol, timeframe, str(e))
    
    def _prepare_market_factors(self, 
                              market_data: Dict[str, Any],
                              smc_analysis: Dict[str, Any],
                              technical_indicators: Dict[str, Any],
                              additional_context: Optional[Dict[str, Any]]) -> MarketFactors:
        """Prepare market factors untuk reasoning engine"""
        
        # Extract price data
        price_data = {}
        if 'candles' in market_data and market_data['candles']:
            latest_candle = market_data['candles'][-1]
            price_data = {
                'open': latest_candle.get('open', 0),
                'high': latest_candle.get('high', 0),
                'low': latest_candle.get('low', 0),
                'close': latest_candle.get('close', 0),
                'volume': latest_candle.get('volume', 0)
            }
        
        # Extract volume data
        volume_data = {}
        if 'volume_analysis' in market_data:
            volume_data = market_data['volume_analysis']
        elif 'volume' in price_data:
            volume_data = {'current_volume': price_data['volume']}
        
        # Market structure from SMC
        market_structure = {}
        if smc_analysis:
            market_structure = {
                'trend': smc_analysis.get('trend', 'neutral'),
                'structure_status': smc_analysis.get('structure_analysis', {}),
                'bias': smc_analysis.get('market_bias', 'neutral')
            }
        
        # Additional context processing
        orderbook_data = None
        news_sentiment = None
        if additional_context:
            orderbook_data = additional_context.get('orderbook_data')
            news_sentiment = additional_context.get('news_sentiment')
        
        return MarketFactors(
            price_data=price_data,
            volume_data=volume_data,
            technical_indicators=technical_indicators,
            smc_analysis=smc_analysis,
            market_structure=market_structure,
            orderbook_data=orderbook_data,
            news_sentiment=news_sentiment
        )
    
    def _generate_enhanced_narrative(self, 
                                   reasoning_result: ReasoningResult,
                                   market_data: Dict[str, Any],
                                   smc_analysis: Dict[str, Any],
                                   symbol: str,
                                   timeframe: str) -> str:
        """Generate enhanced narrative berdasarkan reasoning result"""
        
        try:
            # Jika confidence tinggi, gunakan AI narrative enhancement
            if (reasoning_result.confidence_score >= self.min_confidence_threshold and 
                self.use_ai_enhancement and 
                len(reasoning_result.evidence) >= 3):
                
                # Use AI engine untuk narrative
                enhanced_narrative = self.ai_engine.generate_trading_narrative(
                    symbol=symbol,
                    timeframe=timeframe,
                    market_data=market_data,
                    smc_analysis=smc_analysis,
                    signal={'direction': reasoning_result.conclusion, 'confidence': reasoning_result.confidence_score}
                )
                
                if enhanced_narrative and len(enhanced_narrative) > 50:
                    return enhanced_narrative
            
            # Fallback ke reasoning summary
            return self.enhanced_reasoning.get_reasoning_summary(reasoning_result, "indonesian")
            
        except Exception as e:
            logger.error(f"Error generating enhanced narrative: {e}")
            return self.enhanced_reasoning.get_reasoning_summary(reasoning_result, "indonesian")
    
    def _create_actionable_recommendation(self, 
                                        reasoning_result: ReasoningResult,
                                        market_data: Dict[str, Any],
                                        symbol: str,
                                        timeframe: str) -> Dict[str, Any]:
        """Create actionable trading recommendation"""
        
        recommendation = {
            'action': 'HOLD',  # Default action
            'confidence': reasoning_result.confidence_score,
            'risk_level': 'HIGH',  # Default to high risk
            'entry_conditions': [],
            'risk_management': {},
            'notes': []
        }
        
        # Determine action based on reasoning
        if reasoning_result.confidence_score >= self.min_confidence_threshold:
            if reasoning_result.conclusion in ['BUY', 'SELL']:
                recommendation['action'] = reasoning_result.conclusion
                
                # Adjust risk level based on confidence
                if reasoning_result.confidence_score >= 85:
                    recommendation['risk_level'] = 'LOW'
                elif reasoning_result.confidence_score >= 70:
                    recommendation['risk_level'] = 'MEDIUM'
                else:
                    recommendation['risk_level'] = 'HIGH'
        
        # Add entry conditions based on evidence
        for evidence in reasoning_result.evidence:
            if 'rsi' in evidence.lower() and ('oversold' in evidence.lower() or 'overbought' in evidence.lower()):
                recommendation['entry_conditions'].append(f"RSI condition: {evidence}")
            elif 'structure' in evidence.lower() and 'break' in evidence.lower():
                recommendation['entry_conditions'].append(f"Structure condition: {evidence}")
            elif 'smc' in evidence.lower() and 'bias' in evidence.lower():
                recommendation['entry_conditions'].append(f"SMC condition: {evidence}")
        
        # Risk management based on current price
        if 'candles' in market_data and market_data['candles']:
            current_price = market_data['candles'][-1].get('close', 0)
            if current_price > 0:
                if reasoning_result.conclusion == 'BUY':
                    recommendation['risk_management'] = {
                        'entry_price': current_price,
                        'stop_loss': current_price * 0.98,  # 2% stop loss
                        'take_profit_1': current_price * 1.02,  # 2% TP
                        'take_profit_2': current_price * 1.05   # 5% TP
                    }
                elif reasoning_result.conclusion == 'SELL':
                    recommendation['risk_management'] = {
                        'entry_price': current_price,
                        'stop_loss': current_price * 1.02,  # 2% stop loss
                        'take_profit_1': current_price * 0.98,  # 2% TP
                        'take_profit_2': current_price * 0.95   # 5% TP
                    }
        
        # Add uncertainty notes
        if reasoning_result.uncertainty_factors:
            recommendation['notes'].extend([
                f"Uncertainty: {factor}" for factor in reasoning_result.uncertainty_factors[:3]
            ])
        
        return recommendation
    
    def _assess_analysis_quality(self, reasoning_result: ReasoningResult) -> Dict[str, Any]:
        """Assess quality of the analysis"""
        
        quality_score = 50  # Base score
        
        # Evidence quality
        evidence_count = len(reasoning_result.evidence)
        if evidence_count >= 5:
            quality_score += 20
        elif evidence_count >= 3:
            quality_score += 10
        elif evidence_count <= 1:
            quality_score -= 20
        
        # Confidence alignment
        if reasoning_result.confidence_score >= 80:
            quality_score += 15
        elif reasoning_result.confidence_score >= 60:
            quality_score += 5
        elif reasoning_result.confidence_score <= 30:
            quality_score -= 15
        
        # Reasoning chain completeness
        reasoning_steps = len(reasoning_result.reasoning_chain)
        if reasoning_steps >= 5:
            quality_score += 10
        elif reasoning_steps >= 3:
            quality_score += 5
        elif reasoning_steps <= 1:
            quality_score -= 10
        
        # Uncertainty handling
        if reasoning_result.uncertainty_factors:
            quality_score += 5  # Good to acknowledge uncertainty
        
        quality_score = max(0, min(100, quality_score))
        
        # Quality categories
        if quality_score >= 80:
            quality_level = "EXCELLENT"
        elif quality_score >= 70:
            quality_level = "GOOD"
        elif quality_score >= 50:
            quality_level = "FAIR"
        else:
            quality_level = "POOR"
        
        return {
            'quality_score': quality_score,
            'quality_level': quality_level,
            'evidence_count': evidence_count,
            'reasoning_steps': reasoning_steps,
            'uncertainty_acknowledged': len(reasoning_result.uncertainty_factors) > 0,
            'confidence_level': reasoning_result.confidence.value
        }
    
    def _create_error_analysis(self, symbol: str, timeframe: str, error_message: str) -> Dict[str, Any]:
        """Create error analysis result"""
        return {
            'timestamp': datetime.now().isoformat(),
            'symbol': symbol,
            'timeframe': timeframe,
            'reasoning_result': {
                'conclusion': 'NEUTRAL',
                'confidence': 'very_low',
                'confidence_score': 0.0,
                'evidence': [f"Analysis error: {error_message}"],
                'reasoning_chain': [f"Error occurred: {error_message}"],
                'uncertainty_factors': ["System error prevented proper analysis"]
            },
            'narrative': f"Maaf, terjadi error dalam analisis {symbol} pada timeframe {timeframe}. Error: {error_message}",
            'recommendation': {
                'action': 'HOLD',
                'confidence': 0.0,
                'risk_level': 'HIGH',
                'entry_conditions': [],
                'risk_management': {},
                'notes': [f"System error: {error_message}"]
            },
            'analysis_quality': {
                'quality_score': 0,
                'quality_level': 'ERROR',
                'evidence_count': 0,
                'reasoning_steps': 0,
                'uncertainty_acknowledged': True,
                'confidence_level': 'very_low'
            },
            'metadata': {
                'error': True,
                'error_message': error_message,
                'analysis_timestamp': datetime.now().timestamp()
            }
        }
    
    def get_reasoning_statistics(self) -> Dict[str, Any]:
        """Get comprehensive reasoning statistics"""
        base_stats = self.enhanced_reasoning.get_reasoning_statistics()
        
        # Add integrator-specific stats
        integrator_stats = {
            'integrator_version': '1.0.0',
            'min_confidence_threshold': self.min_confidence_threshold,
            'ai_enhancement_enabled': self.use_ai_enhancement,
            'components_available': {
                'enhanced_reasoning': True,
                'ai_engine': self.ai_engine.openai_client is not None,
                'enhanced_ai_engine': self.enhanced_ai_engine.openai_client is not None,
                'narrative_ai': self.narrative_ai.openai_api_key is not None
            }
        }
        
        return {**base_stats, **integrator_stats}
    
    def update_configuration(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Update integrator configuration"""
        updated = {}
        
        if 'min_confidence_threshold' in config:
            new_threshold = config['min_confidence_threshold']
            if 0 <= new_threshold <= 100:
                self.min_confidence_threshold = new_threshold
                updated['min_confidence_threshold'] = new_threshold
        
        if 'use_ai_enhancement' in config:
            self.use_ai_enhancement = bool(config['use_ai_enhancement'])
            updated['use_ai_enhancement'] = self.use_ai_enhancement
        
        if 'reasoning_confidence_threshold' in config:
            new_threshold = config['reasoning_confidence_threshold']
            if 0 <= new_threshold <= 100:
                self.enhanced_reasoning.confidence_threshold = new_threshold
                updated['reasoning_confidence_threshold'] = new_threshold
        
        logger.info(f"📊 AI Reasoning Integrator configuration updated: {updated}")
        return updated

# Global instance
ai_reasoning_integrator = AIReasoningIntegrator()

def get_ai_reasoning_integrator():
    """Get global AI reasoning integrator instance"""
    return ai_reasoning_integrator

logger.info("🧠 AI Reasoning Integration module initialized - Enhanced reasoning dengan AI narrative")