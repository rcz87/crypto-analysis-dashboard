"""
🎯 SMC Pattern Recognition Endpoint
Mendeteksi pola-pola trading advanced berdasarkan SMC structures
"""

from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Blueprint initialization
smc_pattern = Blueprint('smc_pattern', __name__)
logger = logging.getLogger(__name__)

@smc_pattern.route('/api/smc/patterns/recognize', methods=['POST'])
@cross_origin()
def recognize_smc_patterns():
    """
    🎯 SMC Pattern Recognition - Deteksi pola trading advanced
    
    Expected payload:
    {
        "symbol": "BTCUSDT",
        "timeframe": "1H",
        "lookback_hours": 24,
        "pattern_types": ["wyckoff", "accumulation", "distribution", "spring", "upthrust"]
    }
    
    Response:
    {
        "status": "success",
        "patterns_detected": [
            {
                "pattern_type": "wyckoff_accumulation",
                "confidence": 0.85,
                "phase": "Phase C - Spring Test",
                "key_levels": [...],
                "trading_plan": {...},
                "risk_level": "medium"
            }
        ]
    }
    """
    try:
        from core.structure_memory import smc_memory
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        symbol = data.get('symbol', 'BTCUSDT')
        timeframe = data.get('timeframe', '1H')
        lookback_hours = data.get('lookback_hours', 24)
        pattern_types = data.get('pattern_types', ['wyckoff', 'accumulation', 'spring'])
        
        # Get current SMC context
        context = smc_memory.get_context()
        summary = smc_memory.get_structure_summary()
        
        # Pattern recognition logic
        detected_patterns = []
        
        # 1. Wyckoff Accumulation Pattern
        if 'wyckoff' in pattern_types or 'accumulation' in pattern_types:
            wyckoff_pattern = _detect_wyckoff_accumulation(context, summary)
            if wyckoff_pattern:
                detected_patterns.append(wyckoff_pattern)
        
        # 2. Spring Test Pattern
        if 'spring' in pattern_types:
            spring_pattern = _detect_spring_test(context, summary)
            if spring_pattern:
                detected_patterns.append(spring_pattern)
        
        # 3. Upthrust Pattern
        if 'upthrust' in pattern_types:
            upthrust_pattern = _detect_upthrust(context, summary)
            if upthrust_pattern:
                detected_patterns.append(upthrust_pattern)
        
        # 4. Distribution Pattern
        if 'distribution' in pattern_types:
            distribution_pattern = _detect_distribution(context, summary)
            if distribution_pattern:
                detected_patterns.append(distribution_pattern)
        
        # 5. Institutional Order Flow
        if 'institutional' in pattern_types:
            institutional_pattern = _detect_institutional_flow(context, summary)
            if institutional_pattern:
                detected_patterns.append(institutional_pattern)
        
        # Generate overall market structure analysis
        market_structure = _analyze_market_structure(context, summary, detected_patterns)
        
        response = {
            "status": "success",
            "symbol": symbol,
            "timeframe": timeframe,
            "analysis_timestamp": datetime.now().isoformat(),
            "patterns_detected": detected_patterns,
            "pattern_count": len(detected_patterns),
            "market_structure": market_structure,
            "trading_recommendations": _generate_trading_recommendations(detected_patterns, context),
            "risk_assessment": _assess_pattern_risks(detected_patterns),
            "confidence_score": _calculate_overall_confidence(detected_patterns),
            "api_info": {
                "version": "2.0.0",
                "service": "SMC Pattern Recognition",
                "server_time": datetime.now().isoformat()
            }
        }
        
        logger.info(f"✅ Pattern recognition completed for {symbol}: {len(detected_patterns)} patterns detected")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Pattern recognition error: {e}")
        return jsonify({
            'error': 'Failed to recognize SMC patterns',
            'details': str(e),
            'api_version': '2.0.0',
            'server_time': datetime.now().isoformat()
        }), 500

def _detect_wyckoff_accumulation(context: Dict, summary: Dict) -> Dict:
    """Detect Wyckoff Accumulation pattern"""
    try:
        pattern_confidence = 0.0
        phase = "Unknown"
        key_indicators = []
        
        # Check for accumulation signs
        market_bias = summary.get('market_bias', 'NEUTRAL')
        liquidity_data = context.get('last_liquidity')
        bos_data = context.get('last_bos')
        
        # Phase A: Stopping Action
        if liquidity_data and liquidity_data.get('sweep_type') == 'buy_side_liquidity':
            pattern_confidence += 0.3
            key_indicators.append("Liquidity sweep indicating selling climax")
            phase = "Phase A - Stopping Action"
        
        # Phase B: Building Cause
        bullish_obs = context.get('last_bullish_ob', [])
        if len(bullish_obs) >= 2:
            pattern_confidence += 0.25
            key_indicators.append(f"{len(bullish_obs)} bullish order blocks forming support")
            phase = "Phase B - Building Cause"
        
        # Phase C: Spring Test
        if bos_data and bos_data.get('direction') == 'bullish' and market_bias == 'BULLISH':
            pattern_confidence += 0.3
            key_indicators.append("Bullish BOS confirming spring completion")
            phase = "Phase C - Spring Test Complete"
        
        # Phase D: Signs of Strength
        if pattern_confidence > 0.5 and market_bias == 'BULLISH':
            pattern_confidence += 0.15
            key_indicators.append("Market bias turning bullish - SOS emerging")
            phase = "Phase D - Signs of Strength"
        
        if pattern_confidence >= 0.5:
            return {
                "pattern_type": "wyckoff_accumulation",
                "confidence": min(pattern_confidence, 1.0),
                "phase": phase,
                "key_indicators": key_indicators,
                "key_levels": {
                    "support_levels": summary.get('key_levels', {}).get('support_levels', []),
                    "spring_low": liquidity_data.get('sweep_price') if liquidity_data else None,
                    "accumulation_range": _calculate_accumulation_range(context)
                },
                "trading_plan": {
                    "entry_strategy": "Break above last resistance with volume",
                    "stop_loss": "Below spring low",
                    "target": "Measured move from accumulation range",
                    "position_size": "Start with smaller size, add on strength"
                },
                "risk_level": "medium",
                "timeframe_validity": "Valid for current timeframe",
                "next_expected_move": "Markup phase if spring holds"
            }
        
        return None
        
    except Exception as e:
        logger.error(f"Wyckoff accumulation detection error: {e}")
        return None

def _detect_spring_test(context: Dict, summary: Dict) -> Dict:
    """Detect Spring Test pattern"""
    try:
        pattern_confidence = 0.0
        key_indicators = []
        
        liquidity_data = context.get('last_liquidity')
        bos_data = context.get('last_bos')
        
        # Spring characteristics
        if liquidity_data:
            sweep_strength = liquidity_data.get('strength', 0)
            if sweep_strength > 0.7 and liquidity_data.get('direction') == 'bullish':
                pattern_confidence += 0.4
                key_indicators.append(f"Strong liquidity sweep (strength: {sweep_strength:.2f})")
        
        # Quick recovery (BOS)
        if bos_data and bos_data.get('direction') == 'bullish':
            bos_confidence = bos_data.get('confidence', 0)
            if bos_confidence > 0.7:
                pattern_confidence += 0.35
                key_indicators.append(f"Quick bullish recovery (BOS confidence: {bos_confidence:.2f})")
        
        # Volume confirmation
        if liquidity_data and liquidity_data.get('volume_spike'):
            pattern_confidence += 0.25
            key_indicators.append("Volume spike on spring test")
        
        if pattern_confidence >= 0.6:
            return {
                "pattern_type": "spring_test",
                "confidence": min(pattern_confidence, 1.0),
                "phase": "Spring Test Completed",
                "key_indicators": key_indicators,
                "key_levels": {
                    "spring_low": liquidity_data.get('sweep_price') if liquidity_data else None,
                    "resistance_to_break": summary.get('key_levels', {}).get('resistance_levels', [])
                },
                "trading_plan": {
                    "entry_strategy": "Long on break above previous resistance",
                    "stop_loss": f"Below spring low: {liquidity_data.get('sweep_price', 'N/A')}",
                    "target": "Previous high + extension",
                    "risk_reward": "Minimum 1:2"
                },
                "risk_level": "low-medium",
                "validity_period": "24-48 hours",
                "failure_condition": "Break below spring low with volume"
            }
        
        return None
        
    except Exception as e:
        logger.error(f"Spring test detection error: {e}")
        return None

def _detect_upthrust(context: Dict, summary: Dict) -> Dict:
    """Detect Upthrust pattern (bearish)"""
    try:
        pattern_confidence = 0.0
        key_indicators = []
        
        liquidity_data = context.get('last_liquidity')
        bos_data = context.get('last_bos')
        bearish_obs = context.get('last_bearish_ob', [])
        
        # Upthrust to supply
        if liquidity_data and liquidity_data.get('direction') == 'bearish':
            sweep_strength = liquidity_data.get('strength', 0)
            if sweep_strength > 0.7:
                pattern_confidence += 0.35
                key_indicators.append(f"Bearish liquidity sweep indicating upthrust")
        
        # Bearish order blocks forming
        if len(bearish_obs) >= 1:
            pattern_confidence += 0.25
            key_indicators.append(f"{len(bearish_obs)} bearish order blocks forming resistance")
        
        # Quick rejection (bearish BOS)
        if bos_data and bos_data.get('direction') == 'bearish':
            pattern_confidence += 0.3
            key_indicators.append("Bearish BOS confirming upthrust rejection")
        
        # Market bias turning bearish
        if summary.get('market_bias') == 'BEARISH':
            pattern_confidence += 0.1
            key_indicators.append("Market bias turning bearish")
        
        if pattern_confidence >= 0.6:
            return {
                "pattern_type": "upthrust",
                "confidence": min(pattern_confidence, 1.0),
                "phase": "Upthrust Rejection",
                "key_indicators": key_indicators,
                "key_levels": {
                    "upthrust_high": liquidity_data.get('sweep_price') if liquidity_data else None,
                    "support_to_break": summary.get('key_levels', {}).get('support_levels', []),
                    "resistance_zone": [ob.get('price_level') for ob in bearish_obs]
                },
                "trading_plan": {
                    "entry_strategy": "Short on break below key support",
                    "stop_loss": f"Above upthrust high: {liquidity_data.get('sweep_price', 'N/A')}",
                    "target": "Previous low - extension",
                    "risk_reward": "Minimum 1:2"
                },
                "risk_level": "medium",
                "validity_period": "24-48 hours",
                "confirmation_needed": "Break of support with volume"
            }
        
        return None
        
    except Exception as e:
        logger.error(f"Upthrust detection error: {e}")
        return None

def _detect_distribution(context: Dict, summary: Dict) -> Dict:
    """Detect Distribution pattern"""
    try:
        pattern_confidence = 0.0
        key_indicators = []
        
        bearish_obs = context.get('last_bearish_ob', [])
        choch_data = context.get('last_choch')
        
        # Multiple bearish order blocks
        if len(bearish_obs) >= 2:
            pattern_confidence += 0.3
            key_indicators.append(f"{len(bearish_obs)} bearish order blocks indicating distribution")
        
        # Change of character
        if choch_data and choch_data.get('new_trend') == 'downtrend':
            pattern_confidence += 0.35
            key_indicators.append("Change of character to downtrend")
        
        # Weakening buying pressure
        if summary.get('market_bias') in ['BEARISH', 'NEUTRAL']:
            pattern_confidence += 0.2
            key_indicators.append("Market bias showing weakness")
        
        # Range-bound price action
        support_levels = summary.get('key_levels', {}).get('support_levels', [])
        resistance_levels = summary.get('key_levels', {}).get('resistance_levels', [])
        
        if len(support_levels) >= 1 and len(resistance_levels) >= 1:
            pattern_confidence += 0.15
            key_indicators.append("Range-bound price action forming distribution")
        
        if pattern_confidence >= 0.6:
            return {
                "pattern_type": "distribution",
                "confidence": min(pattern_confidence, 1.0),
                "phase": "Distribution Phase",
                "key_indicators": key_indicators,
                "key_levels": {
                    "distribution_high": max(resistance_levels) if resistance_levels else None,
                    "distribution_low": min(support_levels) if support_levels else None,
                    "supply_zones": [ob.get('price_level') for ob in bearish_obs]
                },
                "trading_plan": {
                    "entry_strategy": "Short on any rally to supply zones",
                    "stop_loss": "Above distribution high",
                    "target": "Below distribution range",
                    "position_sizing": "Layer in shorts on rallies"
                },
                "risk_level": "medium-high",
                "pattern_maturity": "Developing",
                "breakdown_target": "Measured move from distribution range"
            }
        
        return None
        
    except Exception as e:
        logger.error(f"Distribution detection error: {e}")
        return None

def _detect_institutional_flow(context: Dict, summary: Dict) -> Dict:
    """Detect Institutional Order Flow pattern"""
    try:
        pattern_confidence = 0.0
        flow_direction = "neutral"
        key_indicators = []
        
        bullish_obs = context.get('last_bullish_ob', [])
        bearish_obs = context.get('last_bearish_ob', [])
        liquidity_data = context.get('last_liquidity')
        
        # Strong order block formation
        total_obs = len(bullish_obs) + len(bearish_obs)
        if total_obs >= 3:
            pattern_confidence += 0.25
            key_indicators.append(f"Strong institutional footprint: {total_obs} order blocks")
        
        # Liquidity sweep indicating institutional activity
        if liquidity_data and liquidity_data.get('strength', 0) > 0.8:
            pattern_confidence += 0.35
            sweep_direction = liquidity_data.get('direction', 'neutral')
            flow_direction = sweep_direction
            key_indicators.append(f"High-conviction liquidity sweep ({sweep_direction})")
        
        # Order block strength analysis
        strong_obs = []
        for ob in bullish_obs + bearish_obs:
            if ob.get('strength', 0) > 0.75:
                strong_obs.append(ob)
        
        if len(strong_obs) >= 2:
            pattern_confidence += 0.25
            key_indicators.append(f"{len(strong_obs)} high-strength order blocks")
        
        # Volume confirmation
        if liquidity_data and liquidity_data.get('volume_spike'):
            pattern_confidence += 0.15
            key_indicators.append("Volume spike confirming institutional activity")
        
        if pattern_confidence >= 0.7:
            return {
                "pattern_type": "institutional_order_flow",
                "confidence": min(pattern_confidence, 1.0),
                "flow_direction": flow_direction,
                "key_indicators": key_indicators,
                "institutional_levels": {
                    "high_strength_obs": [ob.get('price_level') for ob in strong_obs],
                    "liquidity_target": liquidity_data.get('sweep_price') if liquidity_data else None,
                    "flow_bias": flow_direction.upper()
                },
                "trading_plan": {
                    "entry_strategy": f"Follow institutional flow ({flow_direction})",
                    "key_levels": [ob.get('price_level') for ob in strong_obs],
                    "risk_management": "Tight stops outside institutional levels",
                    "target_method": "Institutional target projection"
                },
                "risk_level": "low",
                "reliability": "high",
                "timeframe_strength": "Multi-timeframe confirmation recommended"
            }
        
        return None
        
    except Exception as e:
        logger.error(f"Institutional flow detection error: {e}")
        return None

def _analyze_market_structure(context: Dict, summary: Dict, patterns: List[Dict]) -> Dict:
    """Analyze overall market structure"""
    try:
        structure_health = "neutral"
        trend_strength = 0.5
        key_observations = []
        
        market_bias = summary.get('market_bias', 'NEUTRAL')
        
        # Analyze based on detected patterns
        bullish_patterns = [p for p in patterns if p['pattern_type'] in ['wyckoff_accumulation', 'spring_test']]
        bearish_patterns = [p for p in patterns if p['pattern_type'] in ['upthrust', 'distribution']]
        
        if len(bullish_patterns) > len(bearish_patterns):
            structure_health = "bullish"
            trend_strength = 0.7
            key_observations.append("Bullish patterns dominating market structure")
        elif len(bearish_patterns) > len(bullish_patterns):
            structure_health = "bearish"
            trend_strength = 0.7
            key_observations.append("Bearish patterns indicating weakness")
        
        # SMC structure analysis
        bos_data = context.get('last_bos')
        if bos_data:
            bos_direction = bos_data.get('direction', '')
            if 'bull' in bos_direction.lower():
                trend_strength += 0.2
                key_observations.append("Recent bullish BOS supporting upward structure")
            elif 'bear' in bos_direction.lower():
                trend_strength -= 0.2
                key_observations.append("Recent bearish BOS indicating structure shift")
        
        return {
            "overall_bias": structure_health,
            "trend_strength": min(max(trend_strength, 0), 1),
            "market_bias_smc": market_bias,
            "structure_quality": "clean" if len(patterns) <= 2 else "complex",
            "key_observations": key_observations,
            "trading_environment": _assess_trading_environment(patterns, context),
            "structure_invalidation": _define_structure_invalidation(context, summary)
        }
        
    except Exception as e:
        logger.error(f"Market structure analysis error: {e}")
        return {"overall_bias": "neutral", "trend_strength": 0.5}

def _generate_trading_recommendations(patterns: List[Dict], context: Dict) -> Dict:
    """Generate trading recommendations based on patterns"""
    try:
        recommendations = {
            "primary_bias": "neutral",
            "entry_setups": [],
            "risk_management": [],
            "timeframe_analysis": "Current timeframe only"
        }
        
        if not patterns:
            return recommendations
        
        # Analyze patterns for bias
        bullish_count = sum(1 for p in patterns if p['pattern_type'] in ['wyckoff_accumulation', 'spring_test'])
        bearish_count = sum(1 for p in patterns if p['pattern_type'] in ['upthrust', 'distribution'])
        
        if bullish_count > bearish_count:
            recommendations["primary_bias"] = "bullish"
            recommendations["entry_setups"].append("Look for long entries on pullbacks to demand zones")
            recommendations["entry_setups"].append("Buy breakouts above key resistance with volume")
        elif bearish_count > bullish_count:
            recommendations["primary_bias"] = "bearish"
            recommendations["entry_setups"].append("Look for short entries on rallies to supply zones")
            recommendations["entry_setups"].append("Sell breakdowns below key support with volume")
        
        # Risk management based on pattern reliability
        avg_confidence = sum(p['confidence'] for p in patterns) / len(patterns)
        if avg_confidence > 0.8:
            recommendations["risk_management"].append("High confidence patterns - standard position sizing")
        elif avg_confidence > 0.6:
            recommendations["risk_management"].append("Medium confidence - reduce position size by 25%")
        else:
            recommendations["risk_management"].append("Lower confidence - reduce position size by 50%")
        
        return recommendations
        
    except Exception as e:
        logger.error(f"Trading recommendations error: {e}")
        return {"primary_bias": "neutral", "entry_setups": [], "risk_management": []}

def _assess_pattern_risks(patterns: List[Dict]) -> Dict:
    """Assess risks based on detected patterns"""
    try:
        risk_level = "medium"
        risk_factors = []
        
        if not patterns:
            return {"overall_risk": "high", "risk_factors": ["No clear patterns detected"]}
        
        # Calculate average confidence
        avg_confidence = sum(p['confidence'] for p in patterns) / len(patterns)
        
        if avg_confidence > 0.8:
            risk_level = "low"
        elif avg_confidence < 0.6:
            risk_level = "high"
            risk_factors.append("Lower pattern confidence scores")
        
        # Check for conflicting patterns
        pattern_types = [p['pattern_type'] for p in patterns]
        bullish_patterns = ['wyckoff_accumulation', 'spring_test']
        bearish_patterns = ['upthrust', 'distribution']
        
        has_bullish = any(p in pattern_types for p in bullish_patterns)
        has_bearish = any(p in pattern_types for p in bearish_patterns)
        
        if has_bullish and has_bearish:
            risk_level = "high"
            risk_factors.append("Conflicting bullish and bearish patterns detected")
        
        return {
            "overall_risk": risk_level,
            "risk_factors": risk_factors,
            "confidence_score": avg_confidence,
            "pattern_reliability": "high" if avg_confidence > 0.75 else "medium"
        }
        
    except Exception as e:
        logger.error(f"Risk assessment error: {e}")
        return {"overall_risk": "high", "risk_factors": ["Error in risk assessment"]}

def _calculate_overall_confidence(patterns: List[Dict]) -> float:
    """Calculate overall confidence score"""
    try:
        if not patterns:
            return 0.0
        
        return sum(p['confidence'] for p in patterns) / len(patterns)
        
    except Exception as e:
        logger.error(f"Confidence calculation error: {e}")
        return 0.0

def _calculate_accumulation_range(context: Dict) -> Dict:
    """Calculate accumulation range from context"""
    try:
        support_levels = []
        resistance_levels = []
        
        # Get levels from order blocks
        bullish_obs = context.get('last_bullish_ob', [])
        bearish_obs = context.get('last_bearish_ob', [])
        
        for ob in bullish_obs:
            support_levels.append(ob.get('price_level', 0))
        
        for ob in bearish_obs:
            resistance_levels.append(ob.get('price_level', 0))
        
        if support_levels and resistance_levels:
            return {
                "range_low": min(support_levels),
                "range_high": max(resistance_levels),
                "range_size": max(resistance_levels) - min(support_levels)
            }
        
        return {"range_low": None, "range_high": None, "range_size": None}
        
    except Exception as e:
        logger.error(f"Accumulation range calculation error: {e}")
        return {}

def _assess_trading_environment(patterns: List[Dict], context: Dict) -> str:
    """Assess current trading environment"""
    try:
        if len(patterns) == 0:
            return "unclear_structure"
        elif len(patterns) == 1:
            return "trending"
        elif len(patterns) <= 3:
            return "complex_structure"
        else:
            return "choppy_conditions"
    except:
        return "unknown"

def _define_structure_invalidation(context: Dict, summary: Dict) -> Dict:
    """Define structure invalidation levels"""
    try:
        invalidation = {}
        
        support_levels = summary.get('key_levels', {}).get('support_levels', [])
        resistance_levels = summary.get('key_levels', {}).get('resistance_levels', [])
        
        if support_levels:
            invalidation['bullish_invalidation'] = min(support_levels)
        
        if resistance_levels:
            invalidation['bearish_invalidation'] = max(resistance_levels)
        
        return invalidation
        
    except Exception as e:
        logger.error(f"Structure invalidation error: {e}")
        return {}

logger.info("🎯 SMC Pattern Recognition Endpoint initialized")