#!/usr/bin/env python3
"""
Sharp Scoring System Endpoints
API endpoints untuk sistem scoring tajam
"""

import os
import logging
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin

logger = logging.getLogger(__name__)

# Create sharp scoring blueprint
sharp_scoring_bp = Blueprint('sharp_scoring', __name__, url_prefix='/api/gpts/sharp-scoring')

@sharp_scoring_bp.route('/test', methods=['GET', 'POST'])
@cross_origin()
def sharp_scoring_test():
    """Test sharp scoring system"""
    try:
        if request.method == 'GET':
            # GET request - return test scenarios
            return jsonify({
                "status": "ready",
                "message": "Sharp Scoring System Test Endpoint",
                "test_scenarios": {
                    "excellent": {
                        "smc_confidence": 0.9,
                        "ob_imbalance": 0.85,
                        "momentum_signal": 0.8,
                        "vol_regime": 0.75,
                        "lux_signal": "BUY",
                        "bias": "long",
                        "funding_rate_abs": 0.01,
                        "oi_delta_pos": True,
                        "long_short_extreme": False,
                        "expected_score": "85-95 points"
                    },
                    "poor": {
                        "smc_confidence": 0.3,
                        "ob_imbalance": 0.2,
                        "momentum_signal": 0.1,
                        "vol_regime": 0.3,
                        "lux_signal": "SELL",
                        "bias": "long",
                        "funding_rate_abs": 0.08,
                        "oi_delta_pos": False,
                        "long_short_extreme": True,
                        "expected_score": "15-25 points"
                    },
                    "marginal": {
                        "smc_confidence": 0.6,
                        "ob_imbalance": 0.5,
                        "momentum_signal": 0.4,
                        "vol_regime": 0.5,
                        "lux_signal": "BUY",
                        "bias": "long",
                        "funding_rate_abs": 0.03,
                        "oi_delta_pos": True,
                        "long_short_extreme": False,
                        "expected_score": "65-75 points"
                    }
                },
                "formula": "SMC (40) + Orderbook (20) + Momentum (15) + Volume (10) + LuxAlgo alignment (±10) + CoinGlass factors (±15)",
                "threshold": "≥70 points for quality signals",
                "timestamp": datetime.now().isoformat()
            })
        else:
            # POST request - calculate score
            data = request.get_json()
            if not data:
                return jsonify({"status": "error", "message": "JSON payload required"}), 400
            
            score_result = calculate_sharp_score(data)
            
            return jsonify({
                "status": "success",
                "input": data,
                "scoring_result": score_result,
                "timestamp": datetime.now().isoformat()
            })
            
    except Exception as e:
        logger.error(f"Sharp scoring test error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

def calculate_sharp_score(inputs):
    """Calculate sharp scoring based on inputs"""
    try:
        # Core technical analysis components
        smc_score = inputs.get('smc_confidence', 0) * 40  # SMC (40 points max)
        ob_score = inputs.get('ob_imbalance', 0) * 20     # Orderbook (20 points max)
        momentum_score = inputs.get('momentum_signal', 0) * 15  # Momentum (15 points max)
        volume_score = inputs.get('vol_regime', 0) * 10   # Volume (10 points max)
        
        # Enhancement factors
        lux_signal = inputs.get('lux_signal', 'NEUTRAL')
        bias = inputs.get('bias', 'neutral')
        
        # LuxAlgo alignment (±10 points)
        lux_alignment = 0
        if lux_signal in ['BUY', 'SELL']:
            if (lux_signal == 'BUY' and bias == 'long') or (lux_signal == 'SELL' and bias == 'short'):
                lux_alignment = 10  # Aligned
            elif (lux_signal == 'BUY' and bias == 'short') or (lux_signal == 'SELL' and bias == 'long'):
                lux_alignment = -10  # Conflicting
        
        # CoinGlass risk factors (±15 points)
        coinglass_factor = 0
        funding_rate_abs = inputs.get('funding_rate_abs', 0)
        oi_delta_pos = inputs.get('oi_delta_pos', False)
        long_short_extreme = inputs.get('long_short_extreme', False)
        
        # Funding rate impact
        if funding_rate_abs < 0.02:  # Normal funding
            coinglass_factor += 5
        elif funding_rate_abs > 0.06:  # Extreme funding
            coinglass_factor -= 5
        
        # Open interest impact
        if oi_delta_pos:
            coinglass_factor += 5
        else:
            coinglass_factor -= 2
        
        # Long/short ratio impact
        if long_short_extreme:
            coinglass_factor -= 5
        else:
            coinglass_factor += 3
        
        # Calculate total score
        total_score = smc_score + ob_score + momentum_score + volume_score + lux_alignment + coinglass_factor
        
        # Determine quality rating
        if total_score >= 85:
            quality = "EXCELLENT"
            recommendation = "EXECUTE"
        elif total_score >= 70:
            quality = "SHARP"
            recommendation = "EXECUTE"
        elif total_score >= 55:
            quality = "GOOD"
            recommendation = "CONSIDER"
        elif total_score >= 40:
            quality = "FAIR"
            recommendation = "WATCH"
        else:
            quality = "POOR"
            recommendation = "AVOID"
        
        return {
            "total_score": round(total_score, 1),
            "quality_rating": quality,
            "recommendation": recommendation,
            "threshold_status": "PASS" if total_score >= 70 else "FAIL",
            "breakdown": {
                "smc_component": round(smc_score, 1),
                "orderbook_component": round(ob_score, 1),
                "momentum_component": round(momentum_score, 1),
                "volume_component": round(volume_score, 1),
                "luxalgo_alignment": lux_alignment,
                "coinglass_factors": coinglass_factor
            },
            "analysis": {
                "strengths": get_scoring_strengths(inputs, total_score),
                "weaknesses": get_scoring_weaknesses(inputs, total_score),
                "key_factors": get_key_factors(inputs)
            }
        }
        
    except Exception as e:
        logger.error(f"Score calculation error: {e}")
        return {
            "error": str(e),
            "total_score": 0,
            "quality_rating": "ERROR",
            "recommendation": "AVOID"
        }

def get_scoring_strengths(inputs, total_score):
    """Identify scoring strengths"""
    strengths = []
    
    if inputs.get('smc_confidence', 0) > 0.7:
        strengths.append("Strong SMC structure confirmation")
    if inputs.get('ob_imbalance', 0) > 0.6:
        strengths.append("Good orderbook imbalance")
    if inputs.get('momentum_signal', 0) > 0.6:
        strengths.append("Positive momentum signals")
    if inputs.get('vol_regime', 0) > 0.5:
        strengths.append("Favorable volume conditions")
    
    lux_signal = inputs.get('lux_signal', 'NEUTRAL')
    bias = inputs.get('bias', 'neutral')
    if (lux_signal == 'BUY' and bias == 'long') or (lux_signal == 'SELL' and bias == 'short'):
        strengths.append("LuxAlgo signal alignment")
    
    if inputs.get('funding_rate_abs', 1) < 0.02:
        strengths.append("Normal funding rate conditions")
    
    return strengths if strengths else ["No significant strengths identified"]

def get_scoring_weaknesses(inputs, total_score):
    """Identify scoring weaknesses"""
    weaknesses = []
    
    if inputs.get('smc_confidence', 0) < 0.5:
        weaknesses.append("Weak SMC structure signals")
    if inputs.get('ob_imbalance', 0) < 0.4:
        weaknesses.append("Poor orderbook conditions")
    if inputs.get('momentum_signal', 0) < 0.4:
        weaknesses.append("Lacking momentum confirmation")
    if inputs.get('vol_regime', 0) < 0.4:
        weaknesses.append("Unfavorable volume profile")
    
    lux_signal = inputs.get('lux_signal', 'NEUTRAL')
    bias = inputs.get('bias', 'neutral')
    if (lux_signal == 'BUY' and bias == 'short') or (lux_signal == 'SELL' and bias == 'long'):
        weaknesses.append("LuxAlgo signal conflict")
    
    if inputs.get('funding_rate_abs', 0) > 0.06:
        weaknesses.append("Extreme funding rate conditions")
    
    if inputs.get('long_short_extreme', False):
        weaknesses.append("Extreme long/short ratio")
    
    return weaknesses if weaknesses else ["No major weaknesses identified"]

def get_key_factors(inputs):
    """Get key factors affecting the score"""
    factors = []
    
    # Top contributing factors
    smc_contrib = inputs.get('smc_confidence', 0) * 40
    if smc_contrib > 25:
        factors.append(f"SMC analysis contributing {smc_contrib:.1f} points")
    
    ob_contrib = inputs.get('ob_imbalance', 0) * 20
    if ob_contrib > 12:
        factors.append(f"Orderbook imbalance adding {ob_contrib:.1f} points")
    
    # Alignment factors
    lux_signal = inputs.get('lux_signal', 'NEUTRAL')
    bias = inputs.get('bias', 'neutral')
    if lux_signal != 'NEUTRAL':
        factors.append(f"LuxAlgo {lux_signal} signal vs {bias} bias")
    
    # Risk factors
    if inputs.get('funding_rate_abs', 0) > 0.04:
        factors.append(f"High funding rate: {inputs.get('funding_rate_abs', 0):.3f}")
    
    return factors if factors else ["Standard market conditions"]