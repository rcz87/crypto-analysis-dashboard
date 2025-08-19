"""
Modular Endpoints - Pecah endpoint logic untuk maintainability
Mengatasi masalah: Single route logic, sulit modularisasi
"""

from flask import Blueprint, request, jsonify
from typing import Dict, Any, Optional
import time
from datetime import datetime

# Import systems
from core.enhanced_logging_system import endpoint_logger, log_info, log_error, log_success
from core.auth_system import require_auth, optional_auth, get_auth_info
from core.professional_smc_analyzer import ProfessionalSMCAnalyzer
from core.enhanced_signal_logic import enhanced_signal_logic
from core.okx_fetcher import OKXFetcher
from core.enhanced_ai_engine import EnhancedAIEngine

# Create blueprint
modular_bp = Blueprint('modular_endpoints', __name__, url_prefix='/api/v2')

# Initialize components
smc_analyzer = ProfessionalSMCAnalyzer()
ai_engine = EnhancedAIEngine()

@modular_bp.route('/health', methods=['GET'])
@endpoint_logger('health_check')
def health_check():
    """System health check endpoint"""
    try:
        health_status = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '2.0.0',
            'services': {
                'smc_analyzer': 'active',
                'ai_engine': 'active',
                'auth_system': 'active',
                'logging_system': 'active'
            },
            'uptime': time.time(),
            'endpoints_available': [
                '/api/v2/smc/analysis',
                '/api/v2/trend/analysis', 
                '/api/v2/risk/assessment',
                '/api/v2/signal/enhanced',
                '/api/v2/auth/token'
            ]
        }
        
        log_success("Health check completed", {'services_count': len(health_status['services'])})
        return jsonify(health_status)
        
    except Exception as e:
        log_error("Health check failed", {'error': str(e)})
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@modular_bp.route('/smc/analysis', methods=['GET'])
@endpoint_logger('smc_analysis')
@optional_auth()
def smc_analysis():
    """Dedicated SMC Analysis endpoint"""
    try:
        # Extract parameters
        symbol = request.args.get('symbol', 'BTCUSDT')
        timeframe = request.args.get('timeframe', '1H')
        detailed = request.args.get('detailed', 'false').lower() == 'true'
        
        log_info(f"SMC Analysis request", {
            'symbol': symbol,
            'timeframe': timeframe,
            'detailed': detailed,
            'authenticated': get_auth_info()['authenticated']
        })
        
        # Get market data
        okx_fetcher = OKXFetcher()
        df = okx_fetcher.get_kline_data(symbol, timeframe, limit=200)
        
        if df is None or df.empty:
            return jsonify({
                'status': 'error',
                'message': 'Failed to fetch market data',
                'symbol': symbol,
                'timeframe': timeframe
            }), 400
        
        # Perform SMC analysis
        smc_result = smc_analyzer.analyze_comprehensive(df, symbol, timeframe)
        
        # Format response based on detail level
        if detailed:
            response_data = {
                'status': 'success',
                'data': {
                    'symbol': symbol,
                    'timeframe': timeframe,
                    'analysis_timestamp': datetime.now().isoformat(),
                    'market_structure': smc_result.get('market_structure', {}),
                    'choch_bos_signals': smc_result.get('choch_bos_signals', []),
                    'order_blocks': smc_result.get('order_blocks', {}),
                    'fair_value_gaps': smc_result.get('fvg_signals', []),
                    'liquidity_sweeps': smc_result.get('liquidity_sweep', {}),
                    'premium_discount_zones': smc_result.get('premium_discount_zones', {}),
                    'confidence_score': smc_result.get('confidence_score', 0),
                    'trend_analysis': {
                        'current_trend': smc_result.get('market_structure', {}).get('trend', 'NEUTRAL'),
                        'break_of_structure': smc_result.get('break_of_structure', False),
                        'change_of_character': smc_result.get('change_of_character', False)
                    }
                },
                'metadata': {
                    'candles_analyzed': len(df),
                    'analysis_type': 'comprehensive_smc',
                    'authenticated': get_auth_info()['authenticated']
                }
            }
        else:
            # Simplified response
            response_data = {
                'status': 'success',
                'data': {
                    'symbol': symbol,
                    'timeframe': timeframe,
                    'trend': smc_result.get('market_structure', {}).get('trend', 'NEUTRAL'),
                    'bos_detected': smc_result.get('break_of_structure', False),
                    'choch_detected': smc_result.get('change_of_character', False),
                    'order_blocks_count': len(smc_result.get('order_blocks', {}).get('bullish', [])) + len(smc_result.get('order_blocks', {}).get('bearish', [])),
                    'fvg_count': len(smc_result.get('fvg_signals', [])),
                    'confidence': smc_result.get('confidence_score', 0),
                    'timestamp': datetime.now().isoformat()
                }
            }
        
        log_success("SMC Analysis completed", {
            'symbol': symbol,
            'trend': response_data['data'].get('trend'),
            'confidence': response_data['data'].get('confidence')
        })
        
        return jsonify(response_data)
        
    except Exception as e:
        log_error("SMC Analysis failed", {
            'symbol': symbol,
            'timeframe': timeframe,
            'error': str(e)
        })
        return jsonify({
            'status': 'error',
            'message': f'SMC analysis failed: {str(e)}',
            'error_code': 'SMC_ANALYSIS_ERROR'
        }), 500

@modular_bp.route('/trend/analysis', methods=['GET'])
@endpoint_logger('trend_analysis')
@optional_auth()
def trend_analysis():
    """Dedicated Trend Analysis endpoint"""
    try:
        symbol = request.args.get('symbol', 'BTCUSDT')
        timeframe = request.args.get('timeframe', '1H')
        method = request.args.get('method', 'comprehensive')  # comprehensive, simple, ai_enhanced
        
        log_info(f"Trend Analysis request", {
            'symbol': symbol,
            'timeframe': timeframe,
            'method': method
        })
        
        # Get market data
        okx_fetcher = OKXFetcher()
        df = okx_fetcher.get_kline_data(symbol, timeframe, limit=100)
        
        if df is None or df.empty:
            return jsonify({
                'status': 'error',
                'message': 'Failed to fetch market data'
            }), 400
        
        # Analyze trend based on method
        if method == 'comprehensive':
            # SMC + Technical analysis
            smc_result = smc_analyzer.analyze_comprehensive(df, symbol, timeframe)
            
            trend_data = {
                'primary_trend': smc_result.get('market_structure', {}).get('trend', 'NEUTRAL'),
                'trend_strength': calculate_trend_strength(df),
                'trend_confirmation': {
                    'smc_bos': smc_result.get('break_of_structure', False),
                    'smc_choch': smc_result.get('change_of_character', False),
                    'price_action': analyze_price_action_trend(df),
                    'volume_confirmation': analyze_volume_trend(df)
                },
                'trend_targets': calculate_trend_targets(df, smc_result),
                'reversal_signals': detect_reversal_signals(df, smc_result)
            }
            
        elif method == 'ai_enhanced':
            # AI-powered trend analysis
            market_context = {
                'symbol': symbol,
                'timeframe': timeframe,
                'current_price': float(df['close'].iloc[-1]),
                'price_change_24h': ((float(df['close'].iloc[-1]) - float(df['close'].iloc[-24])) / float(df['close'].iloc[-24])) * 100 if len(df) >= 24 else 0
            }
            
            ai_analysis = ai_engine.analyze_market_sentiment(f"Analyze trend for {symbol} on {timeframe}")
            
            trend_data = {
                'primary_trend': extract_trend_from_ai(ai_analysis),
                'ai_confidence': extract_confidence_from_ai(ai_analysis),
                'ai_reasoning': ai_analysis.get('reasoning', ''),
                'ai_recommendations': ai_analysis.get('recommendations', [])
            }
            
        else:  # simple
            # Simple technical analysis
            trend_data = {
                'primary_trend': calculate_simple_trend(df),
                'moving_average_trend': calculate_ma_trend(df),
                'price_momentum': calculate_momentum(df)
            }
        
        response_data = {
            'status': 'success',
            'data': {
                'symbol': symbol,
                'timeframe': timeframe,
                'method': method,
                'trend_analysis': trend_data,
                'current_price': float(df['close'].iloc[-1]),
                'analysis_timestamp': datetime.now().isoformat()
            }
        }
        
        log_success("Trend Analysis completed", {
            'symbol': symbol,
            'method': method,
            'trend': trend_data.get('primary_trend')
        })
        
        return jsonify(response_data)
        
    except Exception as e:
        log_error("Trend Analysis failed", {
            'symbol': symbol,
            'method': method,
            'error': str(e)
        })
        return jsonify({
            'status': 'error',
            'message': f'Trend analysis failed: {str(e)}',
            'error_code': 'TREND_ANALYSIS_ERROR'
        }), 500

@modular_bp.route('/risk/assessment', methods=['GET'])
@endpoint_logger('risk_assessment')
@require_auth(['read'])
def risk_assessment():
    """Dedicated Risk Assessment endpoint"""
    try:
        symbol = request.args.get('symbol', 'BTCUSDT')
        timeframe = request.args.get('timeframe', '1H')
        position_size = float(request.args.get('position_size', '1000'))  # USD
        
        log_info(f"Risk Assessment request", {
            'symbol': symbol,
            'timeframe': timeframe,
            'position_size': position_size
        })
        
        # Get market data
        okx_fetcher = OKXFetcher()
        df = okx_fetcher.get_kline_data(symbol, timeframe, limit=100)
        
        if df is None or df.empty:
            return jsonify({
                'status': 'error',
                'message': 'Failed to fetch market data'
            }), 400
        
        current_price = float(df['close'].iloc[-1])
        
        # Calculate various risk metrics
        risk_metrics = {
            'volatility': calculate_volatility(df),
            'support_resistance': calculate_support_resistance_risk(df),
            'trend_risk': calculate_trend_risk(df),
            'volume_risk': calculate_volume_risk(df),
            'smc_risk': calculate_smc_risk(df, symbol, timeframe)
        }
        
        # Overall risk score (0-100, higher = more risky)
        overall_risk_score = calculate_overall_risk_score(risk_metrics)
        
        # Position sizing recommendations
        recommended_position_sizes = calculate_position_sizing(
            position_size, overall_risk_score, risk_metrics
        )
        
        # Stop loss and take profit recommendations
        stop_take_recommendations = calculate_stop_take_levels(
            current_price, risk_metrics, df
        )
        
        response_data = {
            'status': 'success',
            'data': {
                'symbol': symbol,
                'timeframe': timeframe,
                'current_price': current_price,
                'risk_assessment': {
                    'overall_risk_score': overall_risk_score,
                    'risk_level': get_risk_level(overall_risk_score),
                    'risk_metrics': risk_metrics,
                    'risk_factors': identify_risk_factors(risk_metrics)
                },
                'position_recommendations': {
                    'conservative': recommended_position_sizes['conservative'],
                    'moderate': recommended_position_sizes['moderate'],
                    'aggressive': recommended_position_sizes['aggressive']
                },
                'stop_take_levels': stop_take_recommendations,
                'risk_warnings': generate_risk_warnings(risk_metrics, overall_risk_score),
                'analysis_timestamp': datetime.now().isoformat()
            }
        }
        
        log_success("Risk Assessment completed", {
            'symbol': symbol,
            'risk_score': overall_risk_score,
            'risk_level': get_risk_level(overall_risk_score)
        })
        
        return jsonify(response_data)
        
    except Exception as e:
        log_error("Risk Assessment failed", {
            'symbol': symbol,
            'error': str(e)
        })
        return jsonify({
            'status': 'error',
            'message': f'Risk assessment failed: {str(e)}',
            'error_code': 'RISK_ASSESSMENT_ERROR'
        }), 500

@modular_bp.route('/signal/enhanced', methods=['GET'])
@endpoint_logger('enhanced_signal')
@require_auth(['read'])
def enhanced_signal():
    """Enhanced Signal Generation dengan full transparency"""
    try:
        symbol = request.args.get('symbol', 'BTCUSDT')
        timeframe = request.args.get('timeframe', '1H')
        include_reasoning = request.args.get('reasoning', 'true').lower() == 'true'
        
        log_info(f"Enhanced Signal request", {
            'symbol': symbol,
            'timeframe': timeframe,
            'reasoning': include_reasoning
        })
        
        # Get market data
        okx_fetcher = OKXFetcher()
        df = okx_fetcher.get_kline_data(symbol, timeframe, limit=200)
        
        if df is None or df.empty:
            return jsonify({
                'status': 'error',
                'message': 'Failed to fetch market data'
            }), 400
        
        # Technical analysis
        from gpts_api_minimal import analyze_technical_indicators_enhanced
        technical_data = analyze_technical_indicators_enhanced(df)
        
        # SMC analysis
        smc_data = smc_analyzer.analyze_comprehensive(df, symbol, timeframe)
        
        # Enhanced signal logic
        enhanced_result = enhanced_signal_logic.analyze_signal_with_reasoning(
            df, symbol, technical_data, smc_data
        )
        
        # Build response
        response_data = {
            'status': 'success',
            'data': {
                'symbol': symbol,
                'timeframe': timeframe,
                'signal': enhanced_result.get('signal', 'NEUTRAL'),
                'confidence': enhanced_result.get('confidence', 0),
                'confidence_level': enhanced_result.get('confidence_level', 'WEAK'),
                'current_price': float(df['close'].iloc[-1]),
                'timestamp': datetime.now().isoformat()
            }
        }
        
        # Add reasoning if requested
        if include_reasoning:
            response_data['data']['reasoning'] = enhanced_result.get('reasoning', {})
            response_data['data']['component_scores'] = enhanced_result.get('component_scores', {})
            response_data['data']['confidence_breakdown'] = enhanced_result.get('confidence_breakdown', {})
            response_data['data']['transparency_score'] = enhanced_result.get('transparency_score', 0)
        
        # Add technical and SMC data
        response_data['data']['technical_indicators'] = technical_data
        response_data['data']['smc_analysis'] = {
            'trend': smc_data.get('market_structure', {}).get('trend', 'NEUTRAL'),
            'bos_detected': smc_data.get('break_of_structure', False),
            'choch_detected': smc_data.get('change_of_character', False)
        }
        
        log_success("Enhanced Signal completed", {
            'symbol': symbol,
            'signal': enhanced_result.get('signal'),
            'confidence': enhanced_result.get('confidence')
        })
        
        return jsonify(response_data)
        
    except Exception as e:
        log_error("Enhanced Signal failed", {
            'symbol': symbol,
            'error': str(e)
        })
        return jsonify({
            'status': 'error',
            'message': f'Enhanced signal generation failed: {str(e)}',
            'error_code': 'ENHANCED_SIGNAL_ERROR'
        }), 500

@modular_bp.route('/auth/token', methods=['POST'])
@endpoint_logger('generate_token')
def generate_token():
    """Generate JWT token for authentication"""
    try:
        from core.auth_system import enhanced_auth_system
        
        # Get credentials dari request
        data = request.get_json() or {}
        api_key = data.get('api_key') or request.headers.get('X-API-Key')
        
        if not api_key:
            return jsonify({
                'status': 'error',
                'message': 'API key required',
                'error_code': 'API_KEY_REQUIRED'
            }), 400
        
        # Verify API key
        key_data = enhanced_auth_system.verify_api_key(api_key)
        if not key_data:
            return jsonify({
                'status': 'error',
                'message': 'Invalid API key',
                'error_code': 'INVALID_API_KEY'
            }), 401
        
        # Generate JWT token
        payload = {
            'sub': key_data.get('name', 'unknown'),
            'permissions': key_data.get('permissions', ['read']),
            'rate_limit': key_data.get('rate_limit', 1000)
        }
        
        token = enhanced_auth_system.generate_jwt_token(payload)
        
        response_data = {
            'status': 'success',
            'data': {
                'access_token': token,
                'token_type': 'Bearer',
                'expires_in': 24 * 3600,  # 24 hours
                'permissions': payload['permissions'],
                'issued_at': datetime.now().isoformat()
            }
        }
        
        log_success("JWT Token generated", {
            'user': payload['sub'],
            'permissions': payload['permissions']
        })
        
        return jsonify(response_data)
        
    except Exception as e:
        log_error("Token generation failed", {'error': str(e)})
        return jsonify({
            'status': 'error',
            'message': f'Token generation failed: {str(e)}',
            'error_code': 'TOKEN_GENERATION_ERROR'
        }), 500

# Helper functions untuk risk assessment
def calculate_volatility(df):
    """Calculate price volatility"""
    returns = df['close'].pct_change().dropna()
    return float(returns.std() * 100)  # Percentage volatility

def calculate_support_resistance_risk(df):
    """Calculate support/resistance risk"""
    current_price = float(df['close'].iloc[-1])
    high_20 = float(df['high'].tail(20).max())
    low_20 = float(df['low'].tail(20).min())
    
    # Distance to key levels as risk factor
    distance_to_resistance = (high_20 - current_price) / current_price * 100
    distance_to_support = (current_price - low_20) / current_price * 100
    
    return {
        'distance_to_resistance_pct': distance_to_resistance,
        'distance_to_support_pct': distance_to_support,
        'risk_score': min(distance_to_resistance, distance_to_support) * 10  # Lower distance = higher risk
    }

def calculate_trend_risk(df):
    """Calculate trend-based risk"""
    # Simple trend calculation
    sma_20 = df['close'].rolling(20).mean().iloc[-1]
    current_price = df['close'].iloc[-1]
    
    trend_strength = abs(current_price - sma_20) / sma_20 * 100
    
    return {
        'trend_strength_pct': float(trend_strength),
        'risk_score': max(0, 50 - trend_strength)  # Weak trend = higher risk
    }

def calculate_volume_risk(df):
    """Calculate volume-based risk"""
    current_volume = df['volume'].iloc[-1]
    avg_volume = df['volume'].tail(20).mean()
    volume_ratio = current_volume / avg_volume
    
    # Low volume = higher risk
    volume_risk = max(0, 100 - (volume_ratio * 50))
    
    return {
        'volume_ratio': float(volume_ratio),
        'risk_score': float(volume_risk)
    }

def calculate_smc_risk(df, symbol, timeframe):
    """Calculate SMC-based risk"""
    try:
        smc_result = smc_analyzer.analyze_comprehensive(df, symbol, timeframe)
        
        # SMC confidence as risk inverse
        smc_confidence = smc_result.get('confidence_score', 50)
        smc_risk = 100 - smc_confidence
        
        return {
            'smc_confidence': smc_confidence,
            'risk_score': smc_risk,
            'has_bos': smc_result.get('break_of_structure', False),
            'has_choch': smc_result.get('change_of_character', False)
        }
    except:
        return {'risk_score': 50, 'error': 'SMC analysis failed'}

def calculate_overall_risk_score(risk_metrics):
    """Calculate overall risk score"""
    weights = {
        'volatility': 0.25,
        'support_resistance': 0.25,
        'trend_risk': 0.20,
        'volume_risk': 0.15,
        'smc_risk': 0.15
    }
    
    total_score = 0
    for metric, weight in weights.items():
        if metric in risk_metrics:
            score = risk_metrics[metric].get('risk_score', 50)
            total_score += score * weight
    
    return min(100, max(0, total_score))

def get_risk_level(risk_score):
    """Get risk level from score"""
    if risk_score >= 80:
        return 'VERY_HIGH'
    elif risk_score >= 60:
        return 'HIGH'
    elif risk_score >= 40:
        return 'MEDIUM'
    elif risk_score >= 20:
        return 'LOW'
    else:
        return 'VERY_LOW'

def calculate_position_sizing(base_position, risk_score, risk_metrics):
    """Calculate position sizing recommendations"""
    risk_multiplier = max(0.1, (100 - risk_score) / 100)
    
    return {
        'conservative': round(base_position * risk_multiplier * 0.5, 2),
        'moderate': round(base_position * risk_multiplier * 0.75, 2),
        'aggressive': round(base_position * risk_multiplier * 1.0, 2)
    }

def calculate_stop_take_levels(current_price, risk_metrics, df):
    """Calculate stop loss and take profit levels"""
    volatility = risk_metrics.get('volatility', {}).get('risk_score', 50) / 100
    
    # Adaptive stop distance based on volatility
    stop_distance = max(0.01, volatility * 0.03)  # 1-3% based on volatility
    
    return {
        'buy_stop_loss': round(current_price * (1 - stop_distance), 6),
        'buy_take_profit_1': round(current_price * (1 + stop_distance * 2), 6),
        'buy_take_profit_2': round(current_price * (1 + stop_distance * 3), 6),
        'sell_stop_loss': round(current_price * (1 + stop_distance), 6),
        'sell_take_profit_1': round(current_price * (1 - stop_distance * 2), 6),
        'sell_take_profit_2': round(current_price * (1 - stop_distance * 3), 6)
    }

def identify_risk_factors(risk_metrics):
    """Identify specific risk factors"""
    factors = []
    
    if risk_metrics.get('volatility', {}).get('risk_score', 0) > 70:
        factors.append("High price volatility detected")
    
    if risk_metrics.get('volume_risk', {}).get('risk_score', 0) > 60:
        factors.append("Low volume - reduced liquidity")
    
    if risk_metrics.get('trend_risk', {}).get('risk_score', 0) > 60:
        factors.append("Weak trend - uncertain direction")
    
    return factors

def generate_risk_warnings(risk_metrics, overall_risk_score):
    """Generate risk warnings"""
    warnings = []
    
    if overall_risk_score > 80:
        warnings.append("VERY HIGH RISK: Consider avoiding this trade")
    elif overall_risk_score > 60:
        warnings.append("HIGH RISK: Use smaller position sizes")
    
    if risk_metrics.get('volatility', {}).get('risk_score', 0) > 70:
        warnings.append("High volatility: Use wider stop losses")
    
    return warnings

# Trend analysis helper functions
def calculate_trend_strength(df):
    """Calculate trend strength"""
    sma_20 = df['close'].rolling(20).mean()
    current_price = df['close'].iloc[-1]
    
    if len(sma_20) < 20:
        return 50
    
    trend_strength = abs(current_price - sma_20.iloc[-1]) / sma_20.iloc[-1] * 100
    return min(100, trend_strength * 5)  # Scale to 0-100

def analyze_price_action_trend(df):
    """Analyze price action for trend"""
    if len(df) < 10:
        return 'NEUTRAL'
    
    recent_closes = df['close'].tail(10)
    if recent_closes.iloc[-1] > recent_closes.iloc[0]:
        return 'BULLISH'
    elif recent_closes.iloc[-1] < recent_closes.iloc[0]:
        return 'BEARISH'
    else:
        return 'NEUTRAL'

def analyze_volume_trend(df):
    """Analyze volume trend"""
    if len(df) < 20:
        return False
    
    recent_volume = df['volume'].tail(5).mean()
    avg_volume = df['volume'].tail(20).mean()
    
    return recent_volume > avg_volume * 1.2

def calculate_trend_targets(df, smc_result):
    """Calculate trend targets"""
    current_price = float(df['close'].iloc[-1])
    
    # Basic targets based on recent range
    high_20 = float(df['high'].tail(20).max())
    low_20 = float(df['low'].tail(20).min())
    
    return {
        'bullish_target_1': round(high_20 * 1.02, 6),
        'bullish_target_2': round(high_20 * 1.05, 6),
        'bearish_target_1': round(low_20 * 0.98, 6),
        'bearish_target_2': round(low_20 * 0.95, 6)
    }

def detect_reversal_signals(df, smc_result):
    """Detect potential reversal signals"""
    signals = []
    
    # SMC reversal signals
    if smc_result.get('change_of_character'):
        signals.append('SMC Change of Character detected')
    
    # Price action reversal
    if len(df) >= 3:
        last_3_closes = df['close'].tail(3)
        if (last_3_closes.iloc[0] > last_3_closes.iloc[1] < last_3_closes.iloc[2] and 
            last_3_closes.iloc[2] > last_3_closes.iloc[0]):
            signals.append('Bullish reversal pattern')
    
    return signals

def extract_trend_from_ai(ai_analysis):
    """Extract trend from AI analysis"""
    # Simple extraction logic - in production, use more sophisticated NLP
    analysis_text = str(ai_analysis).lower()
    
    if 'bullish' in analysis_text or 'uptrend' in analysis_text:
        return 'BULLISH'
    elif 'bearish' in analysis_text or 'downtrend' in analysis_text:
        return 'BEARISH'
    else:
        return 'NEUTRAL'

def extract_confidence_from_ai(ai_analysis):
    """Extract confidence from AI analysis"""
    # Default confidence extraction
    return ai_analysis.get('confidence', 50)

def calculate_simple_trend(df):
    """Simple trend calculation"""
    if len(df) < 10:
        return 'NEUTRAL'
    
    sma_short = df['close'].rolling(5).mean().iloc[-1]
    sma_long = df['close'].rolling(10).mean().iloc[-1]
    
    if sma_short > sma_long:
        return 'BULLISH'
    elif sma_short < sma_long:
        return 'BEARISH'
    else:
        return 'NEUTRAL'

def calculate_ma_trend(df):
    """Moving average trend"""
    if len(df) < 20:
        return 'NEUTRAL'
    
    sma_10 = df['close'].rolling(10).mean().iloc[-1]
    sma_20 = df['close'].rolling(20).mean().iloc[-1]
    current_price = df['close'].iloc[-1]
    
    if current_price > sma_10 > sma_20:
        return 'STRONG_BULLISH'
    elif current_price > sma_10:
        return 'BULLISH'
    elif current_price < sma_10 < sma_20:
        return 'STRONG_BEARISH'
    elif current_price < sma_10:
        return 'BEARISH'
    else:
        return 'NEUTRAL'

def calculate_momentum(df):
    """Calculate price momentum"""
    if len(df) < 14:
        return 0
    
    # Simple momentum calculation
    current_price = df['close'].iloc[-1]
    price_14_ago = df['close'].iloc[-14]
    
    momentum = (current_price - price_14_ago) / price_14_ago * 100
    return round(momentum, 2)