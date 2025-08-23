#!/usr/bin/env python3
"""
Enhanced Reasoning Engine (Hybrid) - Production-hardened
Combines clean architecture with enterprise-grade robustness:
- Safe JSON serialization with proper Enum handling
- Comprehensive indicator validation & bounds checking  
- Thread-safe operations with RLock & deque ring buffer
- Compact AI context preparation for optimal token usage
- Multi-layer error handling with detailed tracking
- Enhanced retry logic with exponential backoff
"""

import logging
import time
import os
import threading
from typing import Dict, List, Optional, Any, Tuple, TypedDict
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import json
import hashlib
from collections import deque
import math

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
    
    def to_dict(self) -> Dict[str, Any]:
        """JSON-serializable dictionary with safe Enum & timestamp conversion"""
        return {
            "conclusion": self.conclusion,
            "confidence": self.confidence.value if isinstance(self.confidence, ReasoningConfidence) else str(self.confidence),
            "confidence_score": float(self.confidence_score),
            "evidence": list(self.evidence or []),
            "data_sources": list(self.data_sources or []),
            "reasoning_chain": list(self.reasoning_chain or []),
            "uncertainty_factors": list(self.uncertainty_factors or []),
            "timestamp": datetime.utcfromtimestamp(self.timestamp).isoformat() + "Z",
        }

# TypedDict for better type safety
class PriceDataType(TypedDict):
    open: float
    high: float
    low: float
    close: float
    volume: float

class TechnicalIndicatorsType(TypedDict, total=False):
    rsi: float
    macd: float
    macd_signal: float
    ema_20: float
    sma_50: float
    bb_upper: float
    bb_lower: float

@dataclass
class MarketFactors:
    """Market factors yang akan dianalisis dengan type safety"""
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
    
    def __init__(self, history_size: int = 100):
        # Fact validator for data integrity
        self.fact_validator = FactValidator()
        
        # Thread-safe reasoning history using deque ring buffer
        self._history_lock = threading.RLock()
        self.reasoning_history = deque(maxlen=max(10, history_size))
        self.confidence_threshold = 50.0
        
        # OpenAI client with robust initialization
        self.openai_client = None
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            try:
                from openai import OpenAI
                self.openai_client = OpenAI(
                    api_key=api_key,
                    timeout=30.0,
                    max_retries=3
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
            
            # 6. Store reasoning history (thread-safe)
            with self._history_lock:
                self.reasoning_history.append(final_result)
            
            return final_result
            
        except Exception as e:
            logger.error(f"Error in market analysis: {e}")
            return self._create_error_result(str(e))
    
    def _validate_market_data(self, mf: MarketFactors) -> Dict[str, Any]:
        """Hybrid validation: comprehensive but efficient (combines both approaches)"""
        errors: List[str] = []
        
        # Core price validation (essential fields)
        price = mf.price_data or {}
        for field in ("open", "high", "low", "close", "volume"):
            if field not in price:
                errors.append(f"Missing price field: {field}")
                continue
            value = price[field]
            if not isinstance(value, (int, float)) or (field != "volume" and value < 0) or (field == "volume" and value < 0):
                errors.append(f"Invalid {field}: {value}")

        # Price relationship validation (OHLC logic)
        if all(k in price for k in ("open", "high", "low", "close")):
            if price["high"] < max(price["open"], price["close"]):
                errors.append("High cannot be < max(Open, Close)")
            if price["low"] > min(price["open"], price["close"]):
                errors.append("Low cannot be > min(Open, Close)")
            if price["high"] < price["low"]:
                errors.append("High cannot be < Low")

        # Enhanced indicator validation with bounds checking
        indicators = mf.technical_indicators or {}
        current_price = float(price.get("close", 1.0))
        
        for k, v in indicators.items():
            if not isinstance(v, (int, float)):
                errors.append(f"Indicator {k} not numeric: {v}")
                continue
            
            # Oscillator bounds (0-100)
            if k.lower() in ("rsi", "stoch", "williams_r"):
                if not (0 <= v <= 100):
                    errors.append(f"{k} out of bounds: {v} (should be 0-100)")
            
            # Moving averages relative to price
            elif k.lower() in ("ema_50", "ema_200", "sma_20", "sma_50", "sma_200"):
                if v <= 0:
                    errors.append(f"{k} should be positive: {v}")
                elif abs(v - current_price) > current_price * 10:
                    errors.append(f"{k} too far from price: {v} vs {current_price}")
            
            # MACD magnitude check
            elif k.lower() in ("macd", "macd_signal", "macd_histogram"):
                if abs(v) > current_price * 0.5:
                    errors.append(f"{k} magnitude too large: {v} (vs price {current_price})")
            
            # NaN/Infinity check
            if math.isnan(v) or math.isinf(v):
                errors.append(f"{k} is NaN/Infinity: {v}")

        return {"valid": len(errors) == 0, "errors": errors}
    
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
    
    def _truncate_large_data(self, data: Any, max_chars: int = 500) -> str:
        """Truncate large data untuk prevent token bloat"""
        try:
            data_str = json.dumps(data, indent=None)
            if len(data_str) <= max_chars:
                return data_str
            
            # Truncate and add indicator
            truncated = data_str[:max_chars-20] + "...[truncated]"
            return truncated
        except:
            return str(data)[:max_chars]

    def _perform_ai_enhanced_reasoning(self, market_factors: MarketFactors,
                                     evidence: List[str], symbol: str, 
                                     timeframe: str) -> Optional[Dict[str, Any]]:
        """AI-enhanced reasoning dengan prompt size management dan error handling"""
        try:
            # Build concise context dengan size limits
            evidence_summary = "\n".join(evidence[:10])  # Limit to top 10 evidence items
            
            # Prepare truncated technical data
            price_data_str = self._truncate_large_data(market_factors.price_data, 300)
            indicators_str = self._truncate_large_data(market_factors.technical_indicators, 400)
            smc_str = self._truncate_large_data(market_factors.smc_analysis, 300)
            
            prompt = f"""Analyze {symbol} {timeframe} trading opportunity based on FACTUAL DATA ONLY.

CRITICAL: Base analysis ONLY on provided data. No assumptions or external info.

EVIDENCE:
{evidence_summary}

DATA:
Price: {price_data_str}
Indicators: {indicators_str}
SMC: {smc_str}

Provide JSON response:
{{
    "conclusion": "BUY/SELL/NEUTRAL",
    "confidence": 0-100,
    "supporting_factors": ["factor1", "factor2", "factor3"],
    "uncertainty_factors": ["uncertainty1", "uncertainty2"],
    "summary_indonesian": "summary in Indonesian"
}}"""

            if self.openai_client is None:
                return None  # Return None for consistency with function signature
                
            response = self.openai_client.chat.completions.create(
                model="gpt-5",
                messages=[
                    {"role": "system", "content": "You are a factual cryptocurrency trading analyst. Only analyze provided data, never make assumptions."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=600,  # Reduced for efficiency
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            if content is None:
                logger.error("OpenAI response content is None")
                return None  # Return None for consistency with function signature
            
            # Enhanced JSON parsing dengan comprehensive error handling
            try:
                ai_result = json.loads(content)
                logger.debug(f"✅ Successfully parsed AI JSON response")
            except json.JSONDecodeError as e:
                logger.error(f"❌ Failed to parse AI response as JSON: {e}")
                logger.debug(f"Raw response content: {content[:200]}...")
                return None
            
            # Enhanced schema validation dengan detailed checking
            validated_result = self._validate_ai_response_with_schema(ai_result, evidence)
            
            if validated_result.get('validation_passed', False):
                logger.info(f"✅ AI reasoning validation passed for {symbol}")
            else:
                logger.warning(f"⚠️ AI reasoning validation had issues for {symbol}")
                
            return validated_result
            
        except Exception as e:
            logger.error(f"AI reasoning error: {e}")
            return None
    
    def _validate_ai_response_with_schema(self, ai_result: Dict[str, Any], 
                                         evidence: List[str]) -> Dict[str, Any]:
        """Enhanced validation dengan strict schema checking"""
        validated_result = {
            'conclusion': 'NEUTRAL',
            'confidence': 50.0,
            'supporting_factors': [],
            'uncertainty_factors': [],
            'summary_indonesian': 'Analisis tidak dapat dilakukan dengan confidence yang memadai.',
            'validation_passed': False,
            'validation_errors': []
        }
        
        validation_errors = []
        
        try:
            # 1. Validate conclusion with strict checking
            if 'conclusion' not in ai_result:
                validation_errors.append("Missing required field: conclusion")
                validated_result['conclusion'] = 'NEUTRAL'
            else:
                conclusion = str(ai_result['conclusion']).upper().strip()
                if conclusion in ['BUY', 'SELL', 'NEUTRAL']:
                    validated_result['conclusion'] = conclusion
                    logger.debug(f"✅ Valid conclusion: {conclusion}")
                else:
                    validation_errors.append(f"Invalid conclusion: {ai_result['conclusion']} (must be BUY/SELL/NEUTRAL)")
                    validated_result['conclusion'] = 'NEUTRAL'
            
            # 2. Validate confidence with range checking
            if 'confidence' not in ai_result:
                validation_errors.append("Missing required field: confidence")
            else:
                try:
                    confidence = float(ai_result['confidence'])
                    if 0 <= confidence <= 100:
                        validated_result['confidence'] = confidence
                        logger.debug(f"✅ Valid confidence: {confidence}")
                    else:
                        validation_errors.append(f"Confidence out of range: {confidence} (must be 0-100)")
                        validated_result['confidence'] = max(0, min(100, confidence))  # Clamp to valid range
                except (ValueError, TypeError):
                    validation_errors.append(f"Invalid confidence type: {ai_result['confidence']} (must be numeric)")
            
            # 3. Validate supporting factors with evidence cross-checking
            if 'supporting_factors' not in ai_result:
                validation_errors.append("Missing required field: supporting_factors")
            elif not isinstance(ai_result['supporting_factors'], list):
                validation_errors.append("supporting_factors must be a list")
            else:
                valid_factors = []
                for i, factor in enumerate(ai_result['supporting_factors'][:5]):  # Max 5 factors
                    if not isinstance(factor, str):
                        validation_errors.append(f"supporting_factors[{i}] must be string")
                        continue
                    
                    factor_clean = factor.strip()
                    if len(factor_clean) < 10:
                        validation_errors.append(f"supporting_factors[{i}] too short (min 10 chars)")
                        continue
                    
                    # Check if factor references evidence or contains reasonable analysis terms
                    is_valid_factor = any(
                        keyword in factor_clean.lower() 
                        for keyword in ['rsi', 'macd', 'price', 'volume', 'trend', 'support', 'resistance', 'momentum', 'structure']
                    )
                    
                    if is_valid_factor:
                        valid_factors.append(factor_clean)
                    else:
                        validation_errors.append(f"supporting_factors[{i}] doesn't reference technical analysis")
                
                validated_result['supporting_factors'] = valid_factors
            
            # 4. Validate uncertainty factors
            if 'uncertainty_factors' in ai_result:
                if isinstance(ai_result['uncertainty_factors'], list):
                    valid_uncertainties = []
                    for i, uncertainty in enumerate(ai_result['uncertainty_factors'][:3]):  # Max 3
                        if isinstance(uncertainty, str) and len(uncertainty.strip()) > 5:
                            valid_uncertainties.append(uncertainty.strip())
                    validated_result['uncertainty_factors'] = valid_uncertainties
                else:
                    validation_errors.append("uncertainty_factors must be a list")
            
            # 5. Validate Indonesian summary
            if 'summary_indonesian' not in ai_result:
                validation_errors.append("Missing required field: summary_indonesian")
            else:
                if isinstance(ai_result['summary_indonesian'], str):
                    summary = ai_result['summary_indonesian'].strip()
                    if len(summary) >= 10:
                        validated_result['summary_indonesian'] = summary
                    else:
                        validation_errors.append("summary_indonesian too short (min 10 chars)")
                else:
                    validation_errors.append("summary_indonesian must be string")
            
            # 6. Overall validation status
            critical_errors = len([e for e in validation_errors if any(
                keyword in e for keyword in ['Missing required', 'Invalid conclusion', 'out of range']
            )])
            
            if critical_errors == 0 and len(validated_result['supporting_factors']) >= 1:
                validated_result['validation_passed'] = True
                logger.info(f"✅ AI response validation passed with {len(validation_errors)} minor warnings")
            else:
                logger.warning(f"❌ AI response validation failed: {critical_errors} critical errors, {len(validation_errors)} total issues")
            
            validated_result['validation_errors'] = validation_errors
            return validated_result
            
        except Exception as e:
            logger.error(f"Validation exception: {e}")
            validated_result['validation_errors'] = validation_errors + [f"Validation exception: {str(e)}"]
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
        
        # Thread-safe access to recent results
        with self._history_lock:
            recent_results = list(self.reasoning_history)[-20:]  # Last 20 analyses
        
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
        
        # Average confidence dengan division by zero guard
        avg_confidence = sum(r.confidence_score for r in recent_results) / max(1, len(recent_results))
        
        return {
            'total_analyses': len(self.reasoning_history),
            'recent_analyses': len(recent_results),
            'average_confidence': round(avg_confidence, 2),
            'confidence_distribution': confidence_counts,
            'signal_distribution': signal_counts,
            'high_confidence_rate': len([r for r in recent_results if r.confidence_score >= 75]) / max(1, len(recent_results)) * 100,
            'openai_available': self.openai_client is not None,
            'confidence_threshold': self.confidence_threshold
        }

    # ===============================
    # Compact Helper Methods (From User's Implementation)
    # ===============================
    
    def _prepare_ai_context_compact(self, mf: MarketFactors, evidence: List[str], 
                                   symbol: str, timeframe: str) -> Dict[str, Any]:
        """Compact context preparation for optimal token usage"""
        def subset(d: Dict[str, Any], keep: Tuple[str, ...]) -> Dict[str, Any]:
            return {k: d.get(k) for k in keep if isinstance(d, dict) and k in d}

        price = subset(mf.price_data or {}, ("open", "high", "low", "close", "volume"))
        ind = {k: (mf.technical_indicators or {}).get(k) for k in ("rsi", "macd", "ema_50", "ema_200", "sma_20", "sma_50") if k in (mf.technical_indicators or {})}

        smc = {}
        if isinstance(mf.smc_analysis, dict):
            for k in ("trend", "structure", "key_levels"):
                if k in mf.smc_analysis:
                    smc[k] = mf.smc_analysis[k]

        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "price": price,
            "indicators": ind,
            "smc": smc,
            "evidence": evidence[:12],
        }
    
    def _call_openai_safe(self, messages: List[Dict[str, str]], max_attempts: int = 3):
        """Safe OpenAI calls with exponential backoff"""
        if not self.openai_client:
            return None
        delay = 0.6
        for attempt in range(1, max_attempts + 1):
            try:
                return self.openai_client.chat.completions.create(
                    model="gpt-5",
                    messages=messages,
                    max_tokens=600,  # Compact token usage
                    temperature=0.1,
                    response_format={"type": "json_object"},
                    timeout=20.0,
                )
            except Exception as e:
                logger.warning(f"OpenAI attempt {attempt} failed: {e}")
                time.sleep(delay)
                delay *= 1.7
        return None
    
    def _validate_ai_response_hybrid(self, ai: Dict[str, Any]) -> Dict[str, Any]:
        """Hybrid validation combining comprehensive checks with user's simplicity"""
        out = {
            "conclusion": "NEUTRAL",
            "confidence": 50.0,
            "supporting_factors": [],
            "uncertainty_factors": [],
            "summary_indonesian": "Analisis terbatas karena data terbatas.",
            "validation_passed": False,
        }
        try:
            # Conclusion validation
            conc = str(ai.get("conclusion", "NEUTRAL")).upper().strip()
            if conc not in {"BUY", "SELL", "NEUTRAL"}:
                conc = "NEUTRAL"
            out["conclusion"] = conc

            # Confidence with clamping
            conf = float(ai.get("confidence", 50.0))
            out["confidence"] = max(0.0, min(100.0, conf))

            # Supporting factors validation
            s = ai.get("supporting_factors", [])
            u = ai.get("uncertainty_factors", [])
            if isinstance(s, list):
                out["supporting_factors"] = [str(x) for x in s][:10]
            if isinstance(u, list):
                out["uncertainty_factors"] = [str(x) for x in u][:10]

            # Summary validation
            summ = ai.get("summary_indonesian") or ai.get("summary") or ""
            out["summary_indonesian"] = str(summ)[:800] if summ else out["summary_indonesian"]

            out["validation_passed"] = True
        except Exception as e:
            logger.warning(f"AI response normalization failed: {e}")
        return out
    
    def _confidence_bucket(self, score: float) -> ReasoningConfidence:
        """Convert numeric score to confidence bucket"""
        s = float(score)
        if s >= 85: return ReasoningConfidence.VERY_HIGH
        if s >= 70: return ReasoningConfidence.HIGH
        if s >= 55: return ReasoningConfidence.MEDIUM
        if s >= 40: return ReasoningConfidence.LOW
        return ReasoningConfidence.VERY_LOW
    
    def _clamp(self, x: float, lo: float, hi: float) -> float:
        """Safe value clamping"""
        try:
            return max(lo, min(hi, float(x)))
        except Exception:
            return lo

# Global instance
enhanced_reasoning_engine = EnhancedReasoningEngine()

def get_enhanced_reasoning_engine():
    """Get global enhanced reasoning engine instance"""
    return enhanced_reasoning_engine

logger.info("🧠 Enhanced Reasoning Engine module initialized - Akurasi tinggi, tidak halusinasi")