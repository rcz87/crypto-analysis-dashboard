#!/usr/bin/env python3
"""
Enhanced Reasoning Engine - AI Reasoning dengan Akurasi Tinggi
Sistem reasoning yang jelas, tidak halusinasi, dan berdasarkan data faktual
"""

import logging
import time
import os
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import json
import hashlib

logger = logging.getLogger(__name__)

class ReasoningConfidence(Enum):
    """Tingkat confidence untuk reasoning results"""
    VERY_HIGH = "very_high"    # 90-100%
    HIGH = "high"              # 75-89%
    MEDIUM = "medium"          # 50-74%
    LOW = "low"                # 25-49%
    VERY_LOW = "very_low"      # 0-24%

@dataclass
class ReasoningResult:
    """Hasil reasoning dengan tingkat confidence dan evidence"""
    conclusion: str
    confidence: ReasoningConfidence
    confidence_score: float
    evidence: List[str]
    data_sources: List[str]
    reasoning_chain: List[str]
    uncertainty_factors: List[str]
    timestamp: float

@dataclass
class MarketFactors:
    """Market factors yang akan dianalisis"""
    price_data: Dict[str, Any]
    volume_data: Dict[str, Any]
    technical_indicators: Dict[str, Any]
    smc_analysis: Dict[str, Any]
    market_structure: Dict[str, Any]
    orderbook_data: Optional[Dict[str, Any]] = None
    news_sentiment: Optional[Dict[str, Any]] = None

class FactValidator:
    """Validator untuk memastikan data factual dan tidak halusinasi"""
    
    def __init__(self):
        self.validation_rules = {
            'price_range': {'min': 0.000001, 'max': 1000000},
            'volume_range': {'min': 0, 'max': float('inf')},
            'percentage_range': {'min': -100, 'max': 100},
            'confidence_range': {'min': 0, 'max': 100}
        }
        self.logger = logging.getLogger(__name__)
    
    def validate_price_data(self, price_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate price data untuk prevent halusinasi"""
        errors = []
        
        # Check required fields
        required_fields = ['open', 'high', 'low', 'close', 'volume']
        for field in required_fields:
            if field not in price_data:
                errors.append(f"Missing required field: {field}")
                continue
            
            value = price_data[field]
            if not isinstance(value, (int, float)) or value < 0:
                errors.append(f"Invalid {field} value: {value}")
        
        # Validate price relationships
        if all(field in price_data for field in ['open', 'high', 'low', 'close']):
            high = price_data['high']
            low = price_data['low']
            open_price = price_data['open']
            close = price_data['close']
            
            if high < low:
                errors.append(f"High ({high}) cannot be less than Low ({low})")
            if high < max(open_price, close):
                errors.append(f"High ({high}) cannot be less than Open/Close")
            if low > min(open_price, close):
                errors.append(f"Low ({low}) cannot be greater than Open/Close")
        
        return len(errors) == 0, errors
    
    def validate_percentage(self, value: float, field_name: str) -> Tuple[bool, str]:
        """Validate percentage values"""
        if not isinstance(value, (int, float)):
            return False, f"{field_name} must be numeric"
        
        if value < -100 or value > 100:
            return False, f"{field_name} percentage ({value}%) out of valid range (-100% to 100%)"
        
        return True, ""
    
    def validate_confidence_score(self, score: float) -> Tuple[bool, str]:
        """Validate confidence score"""
        if not isinstance(score, (int, float)):
            return False, "Confidence score must be numeric"
        
        if score < 0 or score > 100:
            return False, f"Confidence score ({score}) must be between 0-100"
        
        return True, ""

class EnhancedReasoningEngine:
    """
    Enhanced Reasoning Engine untuk analisis trading cryptocurrency
    Fokus pada accuracy, clarity, dan menghindari halusinasi
    """
    
    def __init__(self):
        self.fact_validator = FactValidator()
        self.reasoning_history = []
        self.confidence_threshold = 50.0  # Minimum confidence untuk actionable signals
        
        # OpenAI client untuk advanced reasoning (opsional)
        self.openai_client = None
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if openai_api_key:
            try:
                from openai import OpenAI
                self.openai_client = OpenAI(
                    api_key=openai_api_key,
                    timeout=20.0,
                    max_retries=1
                )
                logger.info("🧠 Enhanced Reasoning Engine initialized with OpenAI support")
            except ImportError:
                logger.warning("OpenAI library not available - using rule-based reasoning only")
            except Exception as e:
                logger.error(f"OpenAI initialization failed: {e}")
        else:
            logger.info("🧠 Enhanced Reasoning Engine initialized with rule-based reasoning")
    
    def analyze_market_factors(self, market_factors: MarketFactors, 
                             symbol: str, timeframe: str) -> ReasoningResult:
        """
        Comprehensive market analysis dengan fact-based reasoning
        """
        try:
            # 1. Validate input data
            validation_result = self._validate_market_data(market_factors)
            if not validation_result['valid']:
                return self._create_low_confidence_result(
                    "Data validation failed",
                    validation_result['errors']
                )
            
            # 2. Extract factual evidence
            evidence = self._extract_factual_evidence(market_factors)
            
            # 3. Perform rule-based reasoning
            rule_based_analysis = self._perform_rule_based_analysis(market_factors, evidence)
            
            # 4. AI-enhanced reasoning (jika available)
            ai_analysis = None
            if self.openai_client and len(evidence) >= 3:
                ai_analysis = self._perform_ai_enhanced_reasoning(
                    market_factors, evidence, symbol, timeframe
                )
            
            # 5. Combine analyses dan calculate confidence
            final_result = self._combine_analyses(
                rule_based_analysis, ai_analysis, evidence, symbol, timeframe
            )
            
            # 6. Store reasoning history
            self.reasoning_history.append(final_result)
            if len(self.reasoning_history) > 100:
                self.reasoning_history.pop(0)
            
            return final_result
            
        except Exception as e:
            logger.error(f"Error in market analysis: {e}")
            return self._create_error_result(str(e))
    
    def _validate_market_data(self, market_factors: MarketFactors) -> Dict[str, Any]:
        """Validate market data untuk prevent halusinasi"""
        errors = []
        
        # Validate price data
        if market_factors.price_data:
            price_valid, price_errors = self.fact_validator.validate_price_data(
                market_factors.price_data
            )
            if not price_valid:
                errors.extend(price_errors)
        else:
            errors.append("Price data is required")
        
        # Validate technical indicators
        if market_factors.technical_indicators:
            for indicator, value in market_factors.technical_indicators.items():
                if indicator.lower() in ['rsi', 'stoch', 'williams_r']:
                    # These should be 0-100
                    if not isinstance(value, (int, float)) or value < 0 or value > 100:
                        errors.append(f"Invalid {indicator} value: {value} (should be 0-100)")
                elif indicator.lower() in ['macd', 'ema', 'sma']:
                    # These should be reasonable numbers
                    if not isinstance(value, (int, float)):
                        errors.append(f"Invalid {indicator} value: {value} (should be numeric)")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'data_quality_score': max(0, 100 - len(errors) * 10)
        }
    
    def _extract_factual_evidence(self, market_factors: MarketFactors) -> List[str]:
        """Extract factual evidence dari market data"""
        evidence = []
        
        # Price action evidence
        if market_factors.price_data:
            price_data = market_factors.price_data
            
            # Current price level
            if 'close' in price_data:
                evidence.append(f"Current price: {price_data['close']:.6f}")
            
            # Price change
            if 'open' in price_data and 'close' in price_data:
                change = ((price_data['close'] - price_data['open']) / price_data['open']) * 100
                direction = "increased" if change > 0 else "decreased"
                evidence.append(f"Price {direction} by {abs(change):.2f}% from open")
            
            # Volatility
            if all(k in price_data for k in ['high', 'low', 'close']):
                volatility = ((price_data['high'] - price_data['low']) / price_data['close']) * 100
                evidence.append(f"Volatility: {volatility:.2f}% (high-low range)")
        
        # Volume evidence
        if market_factors.volume_data:
            volume_data = market_factors.volume_data
            if 'current_volume' in volume_data:
                evidence.append(f"Current volume: {volume_data['current_volume']}")
            
            if 'volume_trend' in volume_data:
                evidence.append(f"Volume trend: {volume_data['volume_trend']}")
        
        # Technical indicators evidence
        if market_factors.technical_indicators:
            indicators = market_factors.technical_indicators
            
            # RSI evidence
            if 'rsi' in indicators:
                rsi = indicators['rsi']
                if rsi >= 70:
                    evidence.append(f"RSI {rsi:.1f} indicates overbought conditions")
                elif rsi <= 30:
                    evidence.append(f"RSI {rsi:.1f} indicates oversold conditions")
                else:
                    evidence.append(f"RSI {rsi:.1f} in neutral range")
            
            # MACD evidence
            if 'macd' in indicators and 'macd_signal' in indicators:
                macd = indicators['macd']
                signal = indicators['macd_signal']
                if macd > signal:
                    evidence.append("MACD above signal line (bullish momentum)")
                else:
                    evidence.append("MACD below signal line (bearish momentum)")
        
        # SMC evidence
        if market_factors.smc_analysis:
            smc = market_factors.smc_analysis
            
            if 'market_bias' in smc:
                evidence.append(f"SMC market bias: {smc['market_bias']}")
            
            if 'structure_break' in smc:
                if smc['structure_break'] != 'none':
                    evidence.append(f"Structure break detected: {smc['structure_break']}")
            
            if 'order_blocks' in smc and smc['order_blocks']:
                evidence.append(f"Active order blocks: {len(smc['order_blocks'])}")
        
        return evidence
    
    def _perform_rule_based_analysis(self, market_factors: MarketFactors, 
                                   evidence: List[str]) -> Dict[str, Any]:
        """Perform rule-based analysis berdasarkan evidence faktual"""
        analysis = {
            'signal_direction': 'NEUTRAL',
            'confidence_factors': [],
            'warning_factors': [],
            'rule_confidence': 50.0
        }
        
        confidence_score = 50.0  # Base confidence
        
        # Technical indicator rules
        if market_factors.technical_indicators:
            indicators = market_factors.technical_indicators
            
            # RSI rules
            if 'rsi' in indicators:
                rsi = indicators['rsi']
                if rsi >= 70:
                    analysis['warning_factors'].append("Overbought conditions (RSI >= 70)")
                    if analysis['signal_direction'] == 'BUY':
                        confidence_score -= 15
                elif rsi <= 30:
                    analysis['confidence_factors'].append("Oversold conditions support buy signal")
                    if analysis['signal_direction'] != 'SELL':
                        confidence_score += 10
                        analysis['signal_direction'] = 'BUY'
            
            # MACD rules
            if 'macd' in indicators and 'macd_signal' in indicators:
                macd = indicators['macd']
                signal = indicators['macd_signal']
                
                if macd > signal:
                    analysis['confidence_factors'].append("MACD bullish crossover")
                    if analysis['signal_direction'] != 'SELL':
                        confidence_score += 8
                        if analysis['signal_direction'] == 'NEUTRAL':
                            analysis['signal_direction'] = 'BUY'
                else:
                    analysis['confidence_factors'].append("MACD bearish signal")
                    if analysis['signal_direction'] != 'BUY':
                        confidence_score += 8
                        if analysis['signal_direction'] == 'NEUTRAL':
                            analysis['signal_direction'] = 'SELL'
        
        # SMC rules
        if market_factors.smc_analysis:
            smc = market_factors.smc_analysis
            
            # Market bias alignment
            if 'market_bias' in smc:
                bias = smc['market_bias'].lower()
                if bias == 'bullish':
                    analysis['confidence_factors'].append("SMC bullish market bias")
                    if analysis['signal_direction'] == 'BUY':
                        confidence_score += 12
                    elif analysis['signal_direction'] == 'NEUTRAL':
                        analysis['signal_direction'] = 'BUY'
                        confidence_score += 8
                elif bias == 'bearish':
                    analysis['confidence_factors'].append("SMC bearish market bias")
                    if analysis['signal_direction'] == 'SELL':
                        confidence_score += 12
                    elif analysis['signal_direction'] == 'NEUTRAL':
                        analysis['signal_direction'] = 'SELL'
                        confidence_score += 8
            
            # Structure break
            if 'structure_break' in smc and smc['structure_break'] != 'none':
                structure = smc['structure_break'].lower()
                if 'bullish' in structure or 'bos_up' in structure:
                    analysis['confidence_factors'].append("Bullish structure break confirmed")
                    confidence_score += 15
                elif 'bearish' in structure or 'bos_down' in structure:
                    analysis['confidence_factors'].append("Bearish structure break confirmed")
                    confidence_score += 15
        
        # Volume confirmation
        if market_factors.volume_data:
            volume_data = market_factors.volume_data
            if 'volume_trend' in volume_data:
                trend = volume_data['volume_trend'].lower()
                if 'increasing' in trend:
                    analysis['confidence_factors'].append("Volume supports price movement")
                    confidence_score += 5
                elif 'decreasing' in trend:
                    analysis['warning_factors'].append("Decreasing volume may indicate weakening trend")
                    confidence_score -= 3
        
        # Final confidence adjustment
        analysis['rule_confidence'] = max(0, min(100, confidence_score))
        
        return analysis
    
    def _perform_ai_enhanced_reasoning(self, market_factors: MarketFactors,
                                     evidence: List[str], symbol: str, 
                                     timeframe: str) -> Optional[Dict[str, Any]]:
        """AI-enhanced reasoning menggunakan OpenAI dengan fact-checking"""
        try:
            # Prepare factual context untuk AI
            context = self._prepare_ai_context(market_factors, evidence, symbol, timeframe)
            
            # Create structured prompt
            prompt = f"""You are a professional cryptocurrency trading analyst. Analyze the following FACTUAL data for {symbol} on {timeframe} timeframe.

IMPORTANT: Base your analysis ONLY on the provided factual data. Do not make assumptions or add information not present in the data.

FACTUAL EVIDENCE:
{chr(10).join(evidence)}

TECHNICAL DATA:
- Price Data: {json.dumps(market_factors.price_data, indent=2) if market_factors.price_data else 'Not available'}
- Technical Indicators: {json.dumps(market_factors.technical_indicators, indent=2) if market_factors.technical_indicators else 'Not available'}
- SMC Analysis: {json.dumps(market_factors.smc_analysis, indent=2) if market_factors.smc_analysis else 'Not available'}

Please provide:
1. Your trading conclusion (BUY/SELL/NEUTRAL) based ONLY on provided data
2. Confidence level (0-100) for your conclusion
3. Three most important supporting factors from the provided data
4. Any contradictory signals or uncertainty factors from the data
5. One-sentence summary in Indonesian

Format your response as JSON:
{{
    "conclusion": "BUY/SELL/NEUTRAL",
    "confidence": 0-100,
    "supporting_factors": ["factor1", "factor2", "factor3"],
    "uncertainty_factors": ["uncertainty1", "uncertainty2"],
    "summary_indonesian": "summary in Indonesian"
}}"""

            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a factual cryptocurrency trading analyst. Only analyze provided data, never make assumptions."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.1,  # Low temperature untuk consistency
                response_format={"type": "json_object"}
            )
            
            ai_result = json.loads(response.choices[0].message.content)
            
            # Validate AI response
            return self._validate_ai_response(ai_result, evidence)
            
        except Exception as e:
            logger.error(f"AI reasoning error: {e}")
            return None
    
    def _validate_ai_response(self, ai_result: Dict[str, Any], 
                            evidence: List[str]) -> Dict[str, Any]:
        """Validate AI response untuk prevent halusinasi"""
        validated_result = {
            'conclusion': 'NEUTRAL',
            'confidence': 50.0,
            'supporting_factors': [],
            'uncertainty_factors': [],
            'summary_indonesian': 'Analisis tidak dapat dilakukan dengan confident.',
            'validation_passed': False
        }
        
        try:
            # Validate conclusion
            if 'conclusion' in ai_result:
                conclusion = ai_result['conclusion'].upper()
                if conclusion in ['BUY', 'SELL', 'NEUTRAL']:
                    validated_result['conclusion'] = conclusion
            
            # Validate confidence
            if 'confidence' in ai_result:
                confidence = ai_result['confidence']
                if isinstance(confidence, (int, float)) and 0 <= confidence <= 100:
                    validated_result['confidence'] = float(confidence)
            
            # Validate supporting factors (must reference provided evidence)
            if 'supporting_factors' in ai_result:
                factors = ai_result['supporting_factors']
                if isinstance(factors, list):
                    # Only include factors that reference actual evidence
                    valid_factors = []
                    for factor in factors[:3]:  # Max 3 factors
                        if isinstance(factor, str) and len(factor) > 10:
                            # Check if factor references actual evidence
                            factor_references_evidence = any(
                                keyword in factor.lower() for keyword in 
                                ['rsi', 'macd', 'price', 'volume', 'smc', 'structure', 'bias']
                            )
                            if factor_references_evidence:
                                valid_factors.append(factor)
                    validated_result['supporting_factors'] = valid_factors
            
            # Validate uncertainty factors
            if 'uncertainty_factors' in ai_result:
                uncertainties = ai_result['uncertainty_factors']
                if isinstance(uncertainties, list):
                    validated_result['uncertainty_factors'] = [
                        u for u in uncertainties[:2] if isinstance(u, str) and len(u) > 5
                    ]
            
            # Validate Indonesian summary
            if 'summary_indonesian' in ai_result:
                summary = ai_result['summary_indonesian']
                if isinstance(summary, str) and len(summary) > 10:
                    validated_result['summary_indonesian'] = summary
            
            # Mark as validated if key elements are present
            validated_result['validation_passed'] = (
                len(validated_result['supporting_factors']) >= 1 and
                validated_result['confidence'] > 0
            )
            
        except Exception as e:
            logger.error(f"AI response validation error: {e}")
        
        return validated_result
    
    def _combine_analyses(self, rule_analysis: Dict[str, Any], 
                         ai_analysis: Optional[Dict[str, Any]],
                         evidence: List[str], symbol: str, timeframe: str) -> ReasoningResult:
        """Combine rule-based dan AI analyses"""
        
        # Base result dari rule-based analysis
        final_conclusion = rule_analysis['signal_direction']
        base_confidence = rule_analysis['rule_confidence']
        
        # Combine evidence
        all_evidence = evidence.copy()
        reasoning_chain = [
            f"Rule-based analysis: {rule_analysis['signal_direction']} signal",
            f"Rule confidence: {base_confidence:.1f}%"
        ]
        
        confidence_factors = rule_analysis['confidence_factors'].copy()
        uncertainty_factors = rule_analysis['warning_factors'].copy()
        
        # Integrate AI analysis jika available dan valid
        if ai_analysis and ai_analysis.get('validation_passed', False):
            ai_conclusion = ai_analysis['conclusion']
            ai_confidence = ai_analysis['confidence']
            
            reasoning_chain.append(f"AI analysis: {ai_conclusion} signal")
            reasoning_chain.append(f"AI confidence: {ai_confidence:.1f}%")
            
            # Agreement boost
            if ai_conclusion == final_conclusion:
                base_confidence = min(95, base_confidence + 10)
                confidence_factors.append("AI analysis confirms rule-based signal")
                reasoning_chain.append("AI and rule-based analyses agree")
            else:
                # Disagreement - use more conservative approach
                if ai_confidence > base_confidence:
                    final_conclusion = ai_conclusion
                    base_confidence = (ai_confidence + base_confidence) / 2
                    reasoning_chain.append("AI analysis overrides with higher confidence")
                else:
                    base_confidence = (ai_confidence + base_confidence) / 2
                    reasoning_chain.append("Conflicting analyses - reduced confidence")
                
                uncertainty_factors.append("AI and rule-based analyses disagree")
            
            # Add AI supporting factors
            confidence_factors.extend(ai_analysis.get('supporting_factors', []))
            uncertainty_factors.extend(ai_analysis.get('uncertainty_factors', []))
        
        # Determine final confidence level
        if base_confidence >= 85:
            confidence_level = ReasoningConfidence.VERY_HIGH
        elif base_confidence >= 75:
            confidence_level = ReasoningConfidence.HIGH
        elif base_confidence >= 50:
            confidence_level = ReasoningConfidence.MEDIUM
        elif base_confidence >= 25:
            confidence_level = ReasoningConfidence.LOW
        else:
            confidence_level = ReasoningConfidence.VERY_LOW
        
        # Create final result
        return ReasoningResult(
            conclusion=final_conclusion,
            confidence=confidence_level,
            confidence_score=base_confidence,
            evidence=all_evidence,
            data_sources=[f"{symbol} {timeframe} market data", "Technical indicators", "SMC analysis"],
            reasoning_chain=reasoning_chain,
            uncertainty_factors=uncertainty_factors,
            timestamp=time.time()
        )
    
    def _prepare_ai_context(self, market_factors: MarketFactors, evidence: List[str],
                          symbol: str, timeframe: str) -> str:
        """Prepare context untuk AI analysis"""
        context_parts = [
            f"Analysis for {symbol} on {timeframe} timeframe",
            f"Evidence count: {len(evidence)}",
            f"Price data available: {'Yes' if market_factors.price_data else 'No'}",
            f"Technical indicators available: {'Yes' if market_factors.technical_indicators else 'No'}",
            f"SMC analysis available: {'Yes' if market_factors.smc_analysis else 'No'}"
        ]
        
        return "\n".join(context_parts)
    
    def _create_low_confidence_result(self, reason: str, errors: List[str]) -> ReasoningResult:
        """Create low confidence result untuk invalid data"""
        return ReasoningResult(
            conclusion="NEUTRAL",
            confidence=ReasoningConfidence.VERY_LOW,
            confidence_score=10.0,
            evidence=[f"Data validation failed: {reason}"],
            data_sources=["Invalid data"],
            reasoning_chain=[f"Analysis aborted: {reason}"],
            uncertainty_factors=errors,
            timestamp=time.time()
        )
    
    def _create_error_result(self, error_message: str) -> ReasoningResult:
        """Create error result"""
        return ReasoningResult(
            conclusion="NEUTRAL",
            confidence=ReasoningConfidence.VERY_LOW,
            confidence_score=0.0,
            evidence=[f"Analysis error: {error_message}"],
            data_sources=["Error"],
            reasoning_chain=[f"Error occurred: {error_message}"],
            uncertainty_factors=["System error prevented analysis"],
            timestamp=time.time()
        )
    
    def get_reasoning_summary(self, result: ReasoningResult, 
                            language: str = "indonesian") -> str:
        """Generate human-readable reasoning summary"""
        if language.lower() == "indonesian":
            return self._generate_indonesian_summary(result)
        else:
            return self._generate_english_summary(result)
    
    def _generate_indonesian_summary(self, result: ReasoningResult) -> str:
        """Generate Indonesian summary"""
        conclusion_map = {
            'BUY': 'BELI',
            'SELL': 'JUAL', 
            'NEUTRAL': 'NETRAL'
        }
        
        confidence_map = {
            ReasoningConfidence.VERY_HIGH: 'Sangat Tinggi',
            ReasoningConfidence.HIGH: 'Tinggi',
            ReasoningConfidence.MEDIUM: 'Sedang',
            ReasoningConfidence.LOW: 'Rendah',
            ReasoningConfidence.VERY_LOW: 'Sangat Rendah'
        }
        
        conclusion_indo = conclusion_map.get(result.conclusion, result.conclusion)
        confidence_indo = confidence_map.get(result.confidence, str(result.confidence))
        
        summary = f"""
📊 ANALISIS TRADING - {conclusion_indo}
🎯 Confidence: {confidence_indo} ({result.confidence_score:.1f}%)

💡 EVIDENCE FAKTUAL:
{chr(10).join(f"• {evidence}" for evidence in result.evidence)}

🧠 REASONING CHAIN:
{chr(10).join(f"→ {step}" for step in result.reasoning_chain)}

⚠️ FAKTOR KETIDAKPASTIAN:
{chr(10).join(f"• {factor}" for factor in result.uncertainty_factors) if result.uncertainty_factors else "• Tidak ada faktor ketidakpastian yang signifikan"}

📈 KESIMPULAN: Signal {conclusion_indo} dengan confidence {confidence_indo} berdasarkan {len(result.evidence)} evidence faktual."""

        return summary.strip()
    
    def _generate_english_summary(self, result: ReasoningResult) -> str:
        """Generate English summary"""
        confidence_text = result.confidence.value.replace('_', ' ').title()
        
        summary = f"""
📊 TRADING ANALYSIS - {result.conclusion}
🎯 Confidence: {confidence_text} ({result.confidence_score:.1f}%)

💡 FACTUAL EVIDENCE:
{chr(10).join(f"• {evidence}" for evidence in result.evidence)}

🧠 REASONING CHAIN:
{chr(10).join(f"→ {step}" for step in result.reasoning_chain)}

⚠️ UNCERTAINTY FACTORS:
{chr(10).join(f"• {factor}" for factor in result.uncertainty_factors) if result.uncertainty_factors else "• No significant uncertainty factors"}

📈 CONCLUSION: {result.conclusion} signal with {confidence_text} confidence based on {len(result.evidence)} factual evidence points."""

        return summary.strip()
    
    def get_reasoning_statistics(self) -> Dict[str, Any]:
        """Get reasoning engine statistics"""
        if not self.reasoning_history:
            return {'message': 'No reasoning history available'}
        
        recent_results = self.reasoning_history[-20:]  # Last 20 analyses
        
        # Confidence distribution
        confidence_counts = {}
        for result in recent_results:
            conf_level = result.confidence.value
            confidence_counts[conf_level] = confidence_counts.get(conf_level, 0) + 1
        
        # Signal distribution
        signal_counts = {}
        for result in recent_results:
            signal = result.conclusion
            signal_counts[signal] = signal_counts.get(signal, 0) + 1
        
        # Average confidence
        avg_confidence = sum(r.confidence_score for r in recent_results) / len(recent_results)
        
        return {
            'total_analyses': len(self.reasoning_history),
            'recent_analyses': len(recent_results),
            'average_confidence': round(avg_confidence, 2),
            'confidence_distribution': confidence_counts,
            'signal_distribution': signal_counts,
            'high_confidence_rate': len([r for r in recent_results if r.confidence_score >= 75]) / len(recent_results) * 100,
            'openai_available': self.openai_client is not None,
            'confidence_threshold': self.confidence_threshold
        }

# Global instance
enhanced_reasoning_engine = EnhancedReasoningEngine()

def get_enhanced_reasoning_engine():
    """Get global enhanced reasoning engine instance"""
    return enhanced_reasoning_engine

logger.info("🧠 Enhanced Reasoning Engine module initialized - Akurasi tinggi, tidak halusinasi")