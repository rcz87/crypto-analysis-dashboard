#!/usr/bin/env python3
"""
TradingLite Integration API Endpoints
Provides endpoints untuk integrasi dengan TradingLite Gold subscription
"""

from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
import logging
from datetime import datetime
import os

from core.tradinglite_integration import (
    get_tradinglite_integration, 
    TradingLiteConfig,
    LitScriptGenerator
)
from core.shared_service_layer import get_shared_trading_services

logger = logging.getLogger(__name__)

# Create blueprint
tradinglite_bp = Blueprint('tradinglite', __name__, url_prefix='/api/tradinglite')

# Global TradingLite instance
tradinglite = None

@tradinglite_bp.route('/connect', methods=['POST'])
@cross_origin()
def connect_tradinglite():
    """
    Connect to TradingLite dengan Gold subscription
    
    Request Body:
    {
        "account_token": "your_tradinglite_token",
        "workspace_id": "your_workspace_id"
    }
    """
    try:
        data = request.get_json() or {}
        
        # Get credentials from request or environment
        account_token = data.get('account_token') or os.getenv('TRADINGLITE_TOKEN')
        workspace_id = data.get('workspace_id') or os.getenv('TRADINGLITE_WORKSPACE')
        
        if not account_token or not workspace_id:
            return jsonify({
                'status': 'error',
                'message': 'Missing TradingLite credentials. Please provide account_token and workspace_id'
            }), 400
        
        # Create config
        config = TradingLiteConfig(
            account_token=account_token,
            workspace_id=workspace_id,
            subscription_level='gold'
        )
        
        # Initialize integration
        global tradinglite
        tradinglite = get_tradinglite_integration(config)
        
        # Connect
        if tradinglite.connect():
            logger.info("✅ Connected to TradingLite Gold")
            return jsonify({
                'status': 'success',
                'message': 'Connected to TradingLite Gold successfully',
                'subscription': 'gold',
                'features': [
                    'Liquidity Heatmaps',
                    'Order Flow Analysis',
                    'Real-time Bid/Ask Spreads',
                    'Custom LitScript Indicators'
                ],
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to connect to TradingLite'
            }), 500
            
    except Exception as e:
        logger.error(f"TradingLite connection error: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Connection failed: {str(e)}'
        }), 500

@tradinglite_bp.route('/liquidity-analysis', methods=['GET'])
@cross_origin()
def get_liquidity_analysis():
    """
    Get liquidity heatmap analysis dari TradingLite
    """
    try:
        if not tradinglite or not tradinglite.connected:
            return jsonify({
                'status': 'error',
                'message': 'Not connected to TradingLite. Please connect first.'
            }), 400
        
        # Get liquidity analysis
        analysis = tradinglite.get_liquidity_analysis()
        
        if analysis.get('status') == 'success':
            return jsonify({
                'status': 'success',
                'liquidity_analysis': {
                    'liquidity_score': analysis['liquidity_score'],
                    'bid_dominance': analysis['bid_dominance'],
                    'significant_levels': analysis['significant_levels'],
                    'liquidity_walls': analysis['liquidity_walls'],
                    'interpretation': _interpret_liquidity(analysis)
                },
                'timestamp': analysis['timestamp']
            })
        else:
            return jsonify({
                'status': 'warning',
                'message': 'No liquidity data available yet',
                'hint': 'Data will be available after a few seconds of connection'
            })
            
    except Exception as e:
        logger.error(f"Liquidity analysis error: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to get liquidity analysis: {str(e)}'
        }), 500

@tradinglite_bp.route('/order-flow-analysis', methods=['GET'])
@cross_origin()
def get_order_flow_analysis():
    """
    Get order flow analysis dari TradingLite
    """
    try:
        if not tradinglite or not tradinglite.connected:
            return jsonify({
                'status': 'error',
                'message': 'Not connected to TradingLite. Please connect first.'
            }), 400
        
        # Get order flow analysis
        analysis = tradinglite.get_order_flow_analysis()
        
        if analysis.get('status') == 'success':
            return jsonify({
                'status': 'success',
                'order_flow_analysis': {
                    'buy_volume': analysis['total_buy_volume'],
                    'sell_volume': analysis['total_sell_volume'],
                    'cumulative_delta': analysis['cumulative_delta'],
                    'buy_pressure_percent': analysis['buy_pressure_percent'],
                    'flow_direction': analysis['flow_direction'],
                    'trend_strength': analysis['trend_strength'],
                    'interpretation': _interpret_order_flow(analysis)
                },
                'timestamp': analysis['timestamp']
            })
        else:
            return jsonify({
                'status': 'warning',
                'message': 'No order flow data available yet',
                'hint': 'Data will be available after a few seconds of connection'
            })
            
    except Exception as e:
        logger.error(f"Order flow analysis error: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to get order flow analysis: {str(e)}'
        }), 500

@tradinglite_bp.route('/combined-signal', methods=['POST'])
@cross_origin()
def get_combined_signal():
    """
    Get combined trading signal dari TradingLite + sistem existing
    
    Request Body:
    {
        "symbol": "BTC-USDT",
        "timeframe": "1H"
    }
    """
    try:
        data = request.get_json() or {}
        symbol = data.get('symbol', 'BTC-USDT')
        timeframe = data.get('timeframe', '1H')
        
        # Get TradingLite signals
        tradinglite_signals = {}
        if tradinglite and tradinglite.connected:
            tradinglite_signals = tradinglite.get_trading_signals()
        
        # Get existing system signals
        shared_services = get_shared_trading_services()
        system_analysis = shared_services.get_unified_analysis(symbol, timeframe)
        
        # Combine signals
        combined_signals = _combine_signals(tradinglite_signals, system_analysis)
        
        return jsonify({
            'status': 'success',
            'symbol': symbol,
            'timeframe': timeframe,
            'signals': {
                'tradinglite': tradinglite_signals.get('signals', []),
                'system': system_analysis.get('signals', {}).get('primary_signal', {}),
                'combined': combined_signals
            },
            'confidence': combined_signals.get('confidence', 0),
            'recommendation': combined_signals.get('action', 'HOLD'),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Combined signal error: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to generate combined signal: {str(e)}'
        }), 500

@tradinglite_bp.route('/litscript/generate', methods=['POST'])
@cross_origin()
def generate_litscript():
    """
    Generate LitScript code untuk custom indicators
    
    Request Body:
    {
        "indicator_type": "smc" | "liquidity" | "orderflow"
    }
    """
    try:
        data = request.get_json() or {}
        indicator_type = data.get('indicator_type', 'smc')
        
        generator = LitScriptGenerator()
        
        if indicator_type == 'smc':
            script = generator.generate_smc_indicator()
            description = "SMC Analysis with Order Blocks & Fair Value Gaps"
        elif indicator_type == 'liquidity':
            script = generator.generate_liquidity_heatmap()
            description = "Liquidity Heatmap Analysis"
        elif indicator_type == 'orderflow':
            script = generator.generate_order_flow_indicator()
            description = "Order Flow Analysis with Delta"
        else:
            return jsonify({
                'status': 'error',
                'message': f'Unknown indicator type: {indicator_type}'
            }), 400
        
        return jsonify({
            'status': 'success',
            'indicator_type': indicator_type,
            'description': description,
            'litscript_code': script,
            'instructions': [
                "1. Copy the LitScript code",
                "2. Open TradingLite chart",
                "3. Click 'Indicators' -> 'Create Custom'",
                "4. Paste the code and save",
                "5. The indicator will appear on your chart"
            ],
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"LitScript generation error: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to generate LitScript: {str(e)}'
        }), 500

@tradinglite_bp.route('/status', methods=['GET'])
@cross_origin()
def get_tradinglite_status():
    """
    Get TradingLite integration status
    """
    try:
        if not tradinglite:
            return jsonify({
                'status': 'not_initialized',
                'connected': False,
                'message': 'TradingLite integration not initialized'
            })
        
        metrics = tradinglite.get_metrics()
        
        return jsonify({
            'status': 'success',
            'connected': metrics['connected'],
            'subscription': 'gold',
            'metrics': {
                'messages_received': metrics['messages_received'],
                'liquidity_updates': metrics['liquidity_updates'],
                'order_flow_updates': metrics['order_flow_updates'],
                'errors': metrics['errors'],
                'last_update': metrics['last_update'].isoformat() if metrics['last_update'] else None
            },
            'data_points': {
                'liquidity': metrics['liquidity_data_points'],
                'order_flow': metrics['order_flow_data_points'],
                'spreads': metrics['spread_data_points']
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Status check error: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to get status: {str(e)}'
        }), 500

@tradinglite_bp.route('/disconnect', methods=['POST'])
@cross_origin()
def disconnect_tradinglite():
    """
    Disconnect dari TradingLite
    """
    try:
        if tradinglite:
            tradinglite.disconnect()
            logger.info("Disconnected from TradingLite")
            
        return jsonify({
            'status': 'success',
            'message': 'Disconnected from TradingLite',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Disconnect error: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to disconnect: {str(e)}'
        }), 500

# Helper functions
def _interpret_liquidity(analysis: dict) -> str:
    """Interpret liquidity analysis"""
    score = analysis.get('liquidity_score', 0)
    bid_dom = analysis.get('bid_dominance', False)
    
    if score > 70:
        if bid_dom:
            return "High liquidity with strong bid support - Bullish sentiment"
        else:
            return "High liquidity with strong ask resistance - Bearish sentiment"
    elif score > 40:
        return "Moderate liquidity - Normal market conditions"
    else:
        return "Low liquidity - Potential for high volatility"

def _interpret_order_flow(analysis: dict) -> str:
    """Interpret order flow analysis"""
    direction = analysis.get('flow_direction', 'neutral')
    buy_pressure = analysis.get('buy_pressure_percent', 50)
    
    if direction == 'bullish' and buy_pressure > 65:
        return f"Strong bullish order flow ({buy_pressure:.1f}% buy pressure) - Buyers in control"
    elif direction == 'bearish' and buy_pressure < 35:
        return f"Strong bearish order flow ({100-buy_pressure:.1f}% sell pressure) - Sellers in control"
    else:
        return "Balanced order flow - No clear directional bias"

def _combine_signals(tradinglite_signals: dict, system_analysis: dict) -> dict:
    """Combine TradingLite and system signals"""
    combined = {
        'action': 'HOLD',
        'confidence': 50,
        'reasons': []
    }
    
    # Count bullish/bearish signals
    bullish_count = 0
    bearish_count = 0
    total_confidence = 0
    
    # Process TradingLite signals
    for signal in tradinglite_signals.get('signals', []):
        if signal['signal'] == 'BUY':
            bullish_count += 1
            combined['reasons'].append(f"TradingLite: {signal['reason']}")
        elif signal['signal'] == 'SELL':
            bearish_count += 1
            combined['reasons'].append(f"TradingLite: {signal['reason']}")
    
    # Process system signals
    system_signal = system_analysis.get('signals', {}).get('primary_signal', {})
    if system_signal.get('action') in ['BUY', 'STRONG_BUY']:
        bullish_count += 1
        combined['reasons'].append(f"System: {system_signal.get('reasoning', 'Bullish signal')}")
        total_confidence += system_signal.get('confidence', 50)
    elif system_signal.get('action') in ['SELL', 'STRONG_SELL']:
        bearish_count += 1
        combined['reasons'].append(f"System: {system_signal.get('reasoning', 'Bearish signal')}")
        total_confidence += system_signal.get('confidence', 50)
    
    # Determine combined action
    if bullish_count > bearish_count + 1:
        combined['action'] = 'STRONG_BUY' if bullish_count >= 3 else 'BUY'
        combined['confidence'] = min(80 + (bullish_count * 5), 95)
    elif bearish_count > bullish_count + 1:
        combined['action'] = 'STRONG_SELL' if bearish_count >= 3 else 'SELL'
        combined['confidence'] = min(80 + (bearish_count * 5), 95)
    else:
        combined['action'] = 'HOLD'
        combined['confidence'] = 50
    
    return combined