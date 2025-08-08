"""
Sharp Signal Engine API Endpoint
Comprehensive signal analysis dengan AI, SMC, Risk Management, dan Alert Logic
"""

from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
import pandas as pd
import logging
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Create blueprint
sharp_signal_bp = Blueprint('sharp_signal_bp', __name__, url_prefix='/api/signal')

def validate_sharp_signal_request(data: Dict) -> tuple[bool, str]:
    """Validate incoming sharp signal request"""
    if not data:
        return False, "Request body required"
    
    if 'candles' not in data or not data['candles']:
        return False, "Candles data required"
    
    # Validate candle structure
    required_fields = ['close', 'high', 'low', 'volume', 'timestamp']
    for i, candle in enumerate(data['candles'][:3]):
        missing_fields = [field for field in required_fields if field not in candle]
        if missing_fields:
            return False, f"Candle {i+1} missing fields: {missing_fields}"
    
    return True, "Valid"

@sharp_signal_bp.route('/sharp', methods=['POST', 'OPTIONS'])
@cross_origin()
def sharp_signal():
    """
    Generate sharp trading signal dengan comprehensive analysis
    
    Expected JSON:
    {
        "symbol": "BTCUSDT",
        "timeframe": "1H",
        "candles": [
            {"close": 43000, "high": 43100, "low": 42900, "volume": 150, "timestamp": "2025-01-01T00:00:00Z"},
            ...
        ]
    }
    """
    try:
        # Handle OPTIONS for CORS
        if request.method == 'OPTIONS':
            return jsonify({'status': 'ok'})
        
        # Get and validate request data
        data = request.get_json()
        is_valid, validation_message = validate_sharp_signal_request(data)
        
        if not is_valid:
            return jsonify({
                'status': 'error',
                'error_code': 'VALIDATION_ERROR',
                'message': validation_message
            }), 400
        
        # Extract parameters
        symbol = data.get('symbol', 'BTCUSDT')
        timeframe = data.get('timeframe', '1H')
        candles = data.get('candles', [])
        
        logger.info(f"🎯 Sharp signal request: {symbol} {timeframe} with {len(candles)} candles")
        
        # Convert to DataFrame
        df = pd.DataFrame(candles)
        
        # Add required columns if missing
        if 'time' not in df.columns and 'timestamp' in df.columns:
            df['time'] = pd.to_datetime(df['timestamp'])
        
        # Initialize Sharp Signal Engine
        try:
            from core.sharp_signal_engine import SharpSignalEngine
            engine = SharpSignalEngine()
            
            # Generate sharp signal
            signal_result = engine.generate_sharp_signal(df, symbol, timeframe)
            
            # Enhanced response format
            enhanced_result = {
                'status': 'success',
                'data': {
                    'signal': signal_result.get('signal', 'NEUTRAL'),
                    'action': signal_result.get('action', 'HOLD'),
                    'confidence': signal_result.get('confidence', 0),
                    'confidence_level': signal_result.get('confidence_level', 'LOW'),
                    'current_price': signal_result.get('current_price', 0),
                    'symbol': symbol,
                    'timeframe': timeframe,
                    
                    # Analysis components
                    'technical_analysis': signal_result.get('technical_analysis', {}),
                    'smc_analysis': signal_result.get('smc_analysis', {}),
                    'volume_profile': signal_result.get('volume_profile', {}),
                    'multi_timeframe': signal_result.get('multi_timeframe_analysis', {}),
                    
                    # AI & Reasoning
                    'ai_reasoning': signal_result.get('ai_reasoning', {}),
                    'reasoning': signal_result.get('reasoning', ''),
                    'decision_factors': signal_result.get('decision_factors', []),
                    
                    # Risk Management
                    'risk_management': signal_result.get('risk_management', {}),
                    'position_sizing': signal_result.get('position_sizing', {}),
                    'stop_loss': signal_result.get('stop_loss', 0),
                    'take_profit': signal_result.get('take_profit', 0),
                    
                    # Performance & Alerts
                    'signal_performance': signal_result.get('signal_performance', {}),
                    'alerts': signal_result.get('alerts', []),
                    'confluence_score': signal_result.get('confluence_score', 0),
                    
                    'timestamp': datetime.now().isoformat()
                },
                'metadata': {
                    'api_version': '2.0.0',
                    'endpoint': 'sharp_signal',
                    'processing_time_ms': signal_result.get('processing_time_ms', 0),
                    'candles_processed': len(candles),
                    'engine_version': 'SharpSignalEngine v2.0'
                }
            }
            
            logger.info(f"✅ Sharp signal generated: {enhanced_result['data']['signal']} ({enhanced_result['data']['confidence']}%)")
            return jsonify(enhanced_result)
            
        except ImportError:
            # Fallback if SharpSignalEngine not available
            logger.warning("SharpSignalEngine not available, using fallback")
            fallback_result = generate_fallback_sharp_signal(df, symbol, timeframe)
            return jsonify(fallback_result)
            
    except Exception as e:
        logger.error(f"❌ Sharp signal generation failed: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'error_code': 'SIGNAL_GENERATION_ERROR',
            'message': f'Sharp signal generation failed: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@sharp_signal_bp.route('/sharp/status', methods=['GET'])
@cross_origin()
def sharp_signal_status():
    """Get Sharp Signal Engine status and capabilities"""
    try:
        from core.sharp_signal_engine import SharpSignalEngine
        engine_available = True
        
        # Test initialization
        try:
            engine = SharpSignalEngine()
            components = {
                'smc_analyzer': hasattr(engine, 'smc_analyzer'),
                'technical_analyzer': hasattr(engine, 'technical_analyzer'),
                'ai_engine': hasattr(engine, 'ai_engine'),
                'risk_manager': hasattr(engine, 'risk_manager'),
                'alert_manager': hasattr(engine, 'alert_manager'),
                'volume_profile': hasattr(engine, 'volume_profile'),
                'mtf_analyzer': hasattr(engine, 'mtf_analyzer'),
                'signal_tracker': hasattr(engine, 'signal_tracker')
            }
            active_components = sum(components.values())
        except Exception as e:
            components = {}
            active_components = 0
            logger.warning(f"Engine initialization test failed: {e}")
            
    except ImportError:
        engine_available = False
        components = {}
        active_components = 0
    
    return jsonify({
        'status': 'success',
        'service': 'Sharp Signal Engine',
        'version': '2.0.0',
        'engine_available': engine_available,
        'active_components': active_components,
        'components': components,
        'capabilities': {
            'ai_reasoning': engine_available,
            'smc_analysis': engine_available,
            'multi_timeframe': engine_available,
            'risk_management': engine_available,
            'volume_profile': engine_available,
            'alert_system': engine_available,
            'performance_tracking': engine_available
        },
        'endpoints': {
            'sharp_signal': '/api/signal/sharp (POST)',
            'status': '/api/signal/sharp/status (GET)',
            'test': '/api/signal/sharp/test (POST)'
        },
        'supported_timeframes': ['1m', '5m', '15m', '1h', '4h', '1d'],
        'supported_symbols': ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'Any crypto pair']
    })

@sharp_signal_bp.route('/sharp/test', methods=['POST'])
@cross_origin()
def sharp_signal_test():
    """Test endpoint dengan sample data"""
    sample_data = {
        "symbol": "BTCUSDT",
        "timeframe": "1H",
        "candles": [
            {"close": 43000, "high": 43100, "low": 42900, "volume": 150, "timestamp": "2025-01-01T00:00:00Z"},
            {"close": 43050, "high": 43150, "low": 42950, "volume": 145, "timestamp": "2025-01-01T01:00:00Z"},
            {"close": 43100, "high": 43200, "low": 43000, "volume": 160, "timestamp": "2025-01-01T02:00:00Z"},
            {"close": 43080, "high": 43180, "low": 42980, "volume": 155, "timestamp": "2025-01-01T03:00:00Z"},
            {"close": 43120, "high": 43220, "low": 43020, "volume": 170, "timestamp": "2025-01-01T04:00:00Z"}
        ]
    }
    
    # Process with same logic as main endpoint
    try:
        # Use provided data or sample
        data = request.get_json() or sample_data
        return sharp_signal()
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Test failed: {str(e)}',
            'sample_data': sample_data
        }), 500

def generate_fallback_sharp_signal(df: pd.DataFrame, symbol: str, timeframe: str) -> Dict[str, Any]:
    """Generate fallback signal jika SharpSignalEngine tidak tersedia"""
    
    # Basic technical analysis
    closes = df['close'].astype(float)
    highs = df['high'].astype(float)
    lows = df['low'].astype(float)
    volumes = df['volume'].astype(float)
    
    # Simple RSI calculation
    def calculate_rsi(prices, period=14):
        if len(prices) < period:
            return 50
        
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1] if not rsi.empty else 50
    
    # Calculate indicators
    current_price = closes.iloc[-1]
    rsi = calculate_rsi(closes)
    volume_avg = volumes.mean()
    current_volume = volumes.iloc[-1]
    
    # Determine signal
    signal = "NEUTRAL"
    confidence = 50
    action = "HOLD"
    
    # RSI-based signals
    if rsi < 30:
        signal = "BUY"
        action = "BUY"
        confidence = min(75, 50 + (30 - rsi))
    elif rsi > 70:
        signal = "SELL"
        action = "SELL"
        confidence = min(75, 50 + (rsi - 70))
    
    # Volume confirmation
    if current_volume > volume_avg * 1.2:
        confidence += 10
    
    # Price momentum
    if len(closes) >= 3:
        recent_trend = closes.iloc[-3:].pct_change().mean()
        if recent_trend > 0.01 and signal in ["BUY", "NEUTRAL"]:
            signal = "STRONG_BUY" if signal == "BUY" else "BUY"
            action = "STRONG_BUY" if action == "BUY" else "BUY"
            confidence += 5
        elif recent_trend < -0.01 and signal in ["SELL", "NEUTRAL"]:
            signal = "STRONG_SELL" if signal == "SELL" else "SELL"
            action = "STRONG_SELL" if action == "SELL" else "SELL"
            confidence += 5
    
    confidence = min(confidence, 85)  # Cap at 85% for fallback
    
    return {
        'status': 'success',
        'data': {
            'signal': signal,
            'action': action,
            'confidence': round(confidence, 1),
            'confidence_level': 'HIGH' if confidence > 70 else 'MEDIUM' if confidence > 50 else 'LOW',
            'current_price': current_price,
            'symbol': symbol,
            'timeframe': timeframe,
            'technical_analysis': {
                'rsi': round(rsi, 2),
                'volume_ratio': round(current_volume / volume_avg, 2)
            },
            'reasoning': f'{signal} signal berdasarkan RSI {rsi:.1f} dan volume analysis',
            'risk_management': {
                'suggested_stop_loss': current_price * 0.98 if signal in ['BUY', 'STRONG_BUY'] else current_price * 1.02,
                'suggested_take_profit': current_price * 1.04 if signal in ['BUY', 'STRONG_BUY'] else current_price * 0.96
            },
            'fallback_mode': True,
            'timestamp': datetime.now().isoformat()
        },
        'metadata': {
            'api_version': '2.0.0',
            'endpoint': 'sharp_signal_fallback',
            'candles_processed': len(df),
            'engine_version': 'Fallback Engine v1.0'
        }
    }

# Error handlers
@sharp_signal_bp.errorhandler(400)
def bad_request(error):
    return jsonify({
        'status': 'error',
        'error_code': 'BAD_REQUEST',
        'message': 'Invalid request format or missing required fields'
    }), 400

@sharp_signal_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        'status': 'error',
        'error_code': 'INTERNAL_ERROR',
        'message': 'Internal server error occurred'
    }), 500