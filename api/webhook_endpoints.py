#!/usr/bin/env python3
"""
Webhook Endpoints for External Trading Platforms
Secure webhook handlers for TradingView, LuxAlgo, and other platforms
"""

from flask import Blueprint, request, jsonify
import logging
from datetime import datetime
import traceback

from core.tradingview_webhook_handler import get_tradingview_webhook_handler

# Create blueprint
webhook_bp = Blueprint('webhooks', __name__, url_prefix='/api/webhooks')

logger = logging.getLogger(__name__)

@webhook_bp.route('/tradingview', methods=['POST'])
def handle_tradingview_webhook():
    """
    TradingView webhook endpoint
    
    Accepts signals from TradingView alerts including LuxAlgo Premium
    Secure with HMAC signature verification and IP whitelisting
    """
    try:
        # Extract request data
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        payload = request.get_data()
        signature = request.headers.get('X-TradingView-Signature', '')
        
        # Get message from request
        if request.is_json:
            message_data = request.get_json()
            message = str(message_data) if message_data else ''
        else:
            message = payload.decode('utf-8') if payload else ''
        
        # Prepare request data for handler
        request_data = {
            'remote_addr': client_ip,
            'data': payload,
            'signature': signature,
            'message': message
        }
        
        # Process through webhook handler
        handler = get_tradingview_webhook_handler()
        result = handler.process_webhook(request_data)
        
        # Return appropriate response
        status_code = result.get('code', 200)
        
        if result.get('success'):
            logger.info(f"TradingView webhook processed successfully from {client_ip}")
            return jsonify(result), status_code
        else:
            logger.warning(f"TradingView webhook rejected: {result.get('error')} from {client_ip}")
            return jsonify(result), status_code
            
    except Exception as e:
        logger.error(f"TradingView webhook error: {e}\n{traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'timestamp': datetime.now().isoformat()
        }), 500

@webhook_bp.route('/tradingview/test', methods=['POST', 'GET'])
def test_tradingview_webhook():
    """
    Test endpoint for TradingView webhook setup
    Helps verify webhook configuration without affecting live trading
    """
    try:
        if request.method == 'GET':
            return jsonify({
                'success': True,
                'message': 'TradingView webhook test endpoint is active',
                'instructions': {
                    'method': 'POST',
                    'content_type': 'application/json',
                    'sample_payload': {
                        'symbol': 'BTCUSDT',
                        'action': 'BUY',
                        'price': 50000,
                        'strategy': 'LuxAlgo Test'
                    }
                },
                'timestamp': datetime.now().isoformat()
            })
        
        # Handle test POST request
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        
        if request.is_json:
            test_data = request.get_json()
            message = test_data
        else:
            message = request.get_data().decode('utf-8')
        
        # Parse message using handler
        handler = get_tradingview_webhook_handler()
        signal = handler.parse_tradingview_message(str(message))
        
        if signal:
            is_valid, validation_msg = handler.validate_signal(signal)
            
            return jsonify({
                'success': True,
                'message': 'Test webhook processed successfully',
                'parsed_signal': {
                    'symbol': signal.symbol,
                    'action': signal.action,
                    'price': signal.price,
                    'strategy': signal.strategy,
                    'timeframe': signal.timeframe,
                    'luxalgo_indicator': signal.luxalgo_indicator
                },
                'validation': {
                    'is_valid': is_valid,
                    'message': validation_msg
                },
                'client_ip': client_ip,
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Unable to parse signal from test data',
                'received_data': str(message)[:200],  # Limit output
                'timestamp': datetime.now().isoformat()
            }), 400
            
    except Exception as e:
        logger.error(f"TradingView test webhook error: {e}")
        return jsonify({
            'success': False,
            'error': f'Test webhook error: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@webhook_bp.route('/setup-guide', methods=['GET'])
def get_webhook_setup_guide():
    """
    Complete setup guide for TradingView webhook configuration
    """
    try:
        handler = get_tradingview_webhook_handler()
        setup_guide = handler.get_webhook_setup_guide()
        
        return jsonify({
            'success': True,
            'webhook_setup_guide': setup_guide,
            'quick_start': {
                'step_1': 'Create TradingView alert with LuxAlgo indicator',
                'step_2': 'In alert settings, go to Notifications tab',
                'step_3': 'Select "Webhook URL" option',
                'step_4': f'Enter URL: {setup_guide["webhook_url"]}',
                'step_5': 'Use JSON message format for best results',
                'step_6': 'Test with /api/webhooks/tradingview/test first'
            },
            'security_notes': [
                'Webhook validates TradingView IP addresses',
                'HMAC signature verification (optional but recommended)',
                'Rate limiting: 10 requests per minute',
                'All signals logged and validated before processing'
            ],
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Setup guide error: {e}")
        return jsonify({
            'success': False,
            'error': 'Unable to generate setup guide',
            'timestamp': datetime.now().isoformat()
        }), 500

@webhook_bp.route('/status', methods=['GET'])
def get_webhook_status():
    """Get webhook system status and statistics"""
    try:
        handler = get_tradingview_webhook_handler()
        
        return jsonify({
            'success': True,
            'webhook_system': {
                'status': 'operational',
                'tradingview_handler': 'active',
                'security_features': {
                    'ip_whitelisting': len(handler.allowed_ips) > 0,
                    'signature_verification': handler.webhook_secret is not None,
                    'rate_limiting': True
                },
                'supported_formats': [
                    'JSON (recommended)',
                    'LuxAlgo format',
                    'Generic TradingView'
                ],
                'recent_requests': len(handler.request_history),
                'rate_limit_window': f"{handler.rate_limit_max} per {handler.rate_limit_window}s"
            },
            'endpoints': [
                '/api/webhooks/tradingview (production)',
                '/api/webhooks/tradingview/test (testing)', 
                '/api/webhooks/setup-guide (documentation)',
                '/api/webhooks/status (monitoring)'
            ],
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Webhook status error: {e}")
        return jsonify({
            'success': False,
            'error': 'Status check failed',
            'timestamp': datetime.now().isoformat()
        }), 500

# Additional webhook handlers can be added here
# Example: @webhook_bp.route('/mt4', methods=['POST'])
# Example: @webhook_bp.route('/3commas', methods=['POST'])