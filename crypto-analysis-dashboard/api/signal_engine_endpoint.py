"""
Enhanced Signal Engine Endpoint
Integrated advanced signal analysis dengan confidence & reasoning
"""

from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
import pandas as pd
import logging
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Create blueprint
signal_bp = Blueprint('signal_bp', __name__, url_prefix='/api/enhanced-signal')

def validate_signal_request(data: Dict) -> tuple[bool, str]:
    """Validate incoming signal analysis request"""
    if not data:
        return False, "Request body required"
    
    if 'candles' not in data or not data['candles']:
        return False, "Candles data required"
    
    if 'symbol' not in data:
        return False, "Symbol required"
    
    # Validate candle structure
    required_candle_fields = ['close', 'high', 'low', 'volume']
    for candle in data['candles'][:3]:  # Check first 3 candles
        if not all(field in candle for field in required_candle_fields):
            return False, f"Each candle must have: {required_candle_fields}"
    
    return True, "Valid"

@signal_bp.route('/analyze', methods=['POST', 'OPTIONS'])
@cross_origin()
def analyze_signal():
    """
    Analyze trading signal dengan enhanced logic dan reasoning
    
    Expected JSON body:
    {
        "symbol": "BTCUSDT",
        "candles": [{"close": 43000, "high": 43100, "low": 42900, "volume": 150}, ...],
        "technical": {"rsi": 43.08, "macd_histogram": -113.45},
        "smc": {"break_of_structure": true, "trend": "BULLISH", "order_blocks": {...}}
    }
    """
    try:
        # Handle OPTIONS request for CORS
        if request.method == 'OPTIONS':
            return jsonify({'status': 'ok'})
        
        # Get request data
        data = request.get_json()
        
        # Validate request
        is_valid, validation_message = validate_signal_request(data)
        if not is_valid:
            return jsonify({
                'status': 'error',
                'error_code': 'VALIDATION_ERROR',
                'message': validation_message
            }), 400
        
        # Extract data
        symbol = data.get('symbol', 'UNKNOWN')
        candles = data.get('candles', [])
        technical_data = data.get('technical', {})
        smc_data = data.get('smc', {})
        
        logger.info(f"🎯 Enhanced signal analysis request for {symbol} with {len(candles)} candles")
        
        # Convert candles to DataFrame
        df = pd.DataFrame(candles)
        
        # Ensure required columns exist
        if df.empty:
            return jsonify({
                'status': 'error',
                'error_code': 'EMPTY_DATA',
                'message': 'No valid candle data provided'
            }), 400
        
        # Initialize enhanced signal logic
        try:
            from core.enhanced_signal_logic import EnhancedSignalLogic
            enhanced_logic = EnhancedSignalLogic()
        except ImportError:
            # Fallback: create minimal enhanced logic
            logger.warning("Enhanced Signal Logic not found, using fallback")
            enhanced_logic = create_fallback_enhanced_logic()
        
        # Analyze signal with reasoning
        analysis_result = enhanced_logic.analyze_signal_with_reasoning(
            df=df,
            symbol=symbol,
            technical_data=technical_data,
            smc_data=smc_data
        )
        
        # Add API metadata
        response_data = {
            'status': 'success',
            'data': analysis_result,
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'api_version': '2.0.0',
                'endpoint': 'enhanced-signal/analyze',
                'symbol': symbol,
                'candles_processed': len(candles)
            }
        }
        
        logger.info(f"✅ Enhanced signal analysis completed for {symbol}: {analysis_result.get('signal')} ({analysis_result.get('confidence')}%)")
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"❌ Enhanced signal analysis failed: {e}", exc_info=True)
        
        return jsonify({
            'status': 'error',
            'error_code': 'ANALYSIS_ERROR',
            'message': f'Signal analysis failed: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@signal_bp.route('/test', methods=['GET'])
@cross_origin()
def test_endpoint():
    """Test endpoint untuk memastikan enhanced signal engine aktif"""
    try:
        from core.enhanced_signal_logic import EnhancedSignalLogic
        logic_available = True
        logic_info = "Enhanced Signal Logic available"
    except ImportError:
        logic_available = False
        logic_info = "Enhanced Signal Logic not available - using fallback"
    
    return jsonify({
        'status': 'success',
        'service': 'Enhanced Signal Engine',
        'version': '2.0.0',
        'enhanced_logic_available': logic_available,
        'info': logic_info,
        'endpoints': {
            'analyze': '/api/enhanced-signal/analyze (POST)',
            'test': '/api/enhanced-signal/test (GET)'
        },
        'example_request': {
            'symbol': 'BTCUSDT',
            'candles': [
                {'close': 43000, 'high': 43100, 'low': 42900, 'volume': 150},
                {'close': 43050, 'high': 43150, 'low': 42950, 'volume': 145}
            ],
            'technical': {'rsi': 43.08, 'macd_histogram': -113.45},
            'smc': {'break_of_structure': True, 'trend': 'BULLISH'}
        }
    })

def create_fallback_enhanced_logic():
    """Create fallback enhanced logic jika yang asli tidak tersedia"""
    
    class FallbackEnhancedLogic:
        def __init__(self):
            self.weight_matrix = {
                'rsi_oversold': {'weight': 0.25, 'priority': 'high'},
                'rsi_overbought': {'weight': 0.25, 'priority': 'high'},
                'bos_bullish': {'weight': 0.35, 'priority': 'critical'},
                'bos_bearish': {'weight': 0.35, 'priority': 'critical'},
                'volume_confirmation': {'weight': 0.20, 'priority': 'high'}
            }
        
        def analyze_signal_with_reasoning(self, df, symbol, technical_data, smc_data):
            """Fallback analysis dengan basic logic"""
            
            # Basic signal determination
            signal = "NEUTRAL"
            confidence = 50
            
            # RSI analysis
            rsi = technical_data.get('rsi', 50)
            if rsi < 30:
                signal = "BUY"
                confidence += 20
            elif rsi > 70:
                signal = "SELL"
                confidence += 20
            
            # SMC analysis
            if smc_data.get('break_of_structure'):
                trend = smc_data.get('trend', 'NEUTRAL')
                if trend == 'BULLISH':
                    signal = "STRONG_BUY" if signal == "BUY" else "BUY"
                    confidence += 15
                elif trend == 'BEARISH':
                    signal = "STRONG_SELL" if signal == "SELL" else "SELL"
                    confidence += 15
            
            # Volume confirmation
            if len(df) > 1:
                avg_volume = df['volume'].mean()
                last_volume = df['volume'].iloc[-1]
                if last_volume > avg_volume * 1.2:
                    confidence += 10
            
            # Cap confidence
            confidence = min(confidence, 95)
            
            return {
                'signal': signal,
                'confidence': confidence,
                'confidence_level': self._get_confidence_level(confidence),
                'reasoning': {
                    'summary': f'{signal} signal untuk {symbol} berdasarkan RSI {rsi} dan SMC analysis',
                    'factors': [
                        f'RSI: {rsi} ({"Oversold" if rsi < 30 else "Overbought" if rsi > 70 else "Neutral"})',
                        f'SMC Trend: {smc_data.get("trend", "Unknown")}',
                        f'Break of Structure: {smc_data.get("break_of_structure", False)}'
                    ],
                    'risk_assessment': 'Medium risk' if confidence > 60 else 'High risk'
                },
                'current_price': df['close'].iloc[-1] if len(df) > 0 else 0,
                'symbol': symbol,
                'timestamp': datetime.now().isoformat()
            }
        
        def _get_confidence_level(self, confidence):
            if confidence >= 80:
                return 'Very High'
            elif confidence >= 65:
                return 'High'
            elif confidence >= 50:
                return 'Medium'
            else:
                return 'Low'
    
    return FallbackEnhancedLogic()

# Add error handlers
@signal_bp.errorhandler(400)
def bad_request(error):
    return jsonify({
        'status': 'error',
        'error_code': 'BAD_REQUEST',
        'message': 'Invalid request format'
    }), 400

@signal_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        'status': 'error',
        'error_code': 'INTERNAL_ERROR',
        'message': 'Internal server error'
    }), 500