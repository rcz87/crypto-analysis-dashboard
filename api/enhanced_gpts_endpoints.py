"""
🚀 Enhanced GPTs Endpoints dengan SMC Context Auto-Injection
Auto-inject SMC context ke semua trading signal responses
"""

from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
import logging
from datetime import datetime
from typing import Dict, Any

# Blueprint initialization
enhanced_gpts = Blueprint('enhanced_gpts', __name__)
logger = logging.getLogger(__name__)

@enhanced_gpts.route('/api/gpts/sinyal/enhanced', methods=['POST'])
@cross_origin()
def enhanced_signal_analysis():
    """
    Enhanced Signal Analysis dengan Auto-Injected SMC Context
    
    Expected payload:
    {
        "symbol": "BTCUSDT",
        "timeframe": "1H", 
        "account_balance": 1000,
        "risk_tolerance": 0.02
    }
    
    Response includes:
    - Standard signal analysis
    - Auto-injected SMC context
    - Heatmap status warnings
    - Contextual reasoning
    """
    try:
        from ..core.smc_context_injector import smc_context_injector
        from ..gpts_api_simple import gpts_simple
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        # Get original signal analysis (you'll need to adapt this based on your existing endpoint)
        # For now, creating a mock response structure
        original_signal = {
            "signal": "BUY",
            "confidence": 78,
            "entry_price": 43500.0,
            "stop_loss": 42800.0,
            "take_profit": 44200.0,
            "risk_reward_ratio": 2.5,
            "analysis": "Technical indicators show bullish momentum",
            "api_version": "1.0.0",
            "server_time": datetime.now().isoformat()
        }
        
        # Auto-inject SMC context
        enhanced_response = smc_context_injector.inject_context(
            original_signal, 
            symbol=data.get('symbol', 'BTCUSDT'),
            timeframe=data.get('timeframe', '1H')
        )
        
        logger.info(f"✅ Enhanced signal generated with SMC context for {data.get('symbol', 'UNKNOWN')}")
        
        return jsonify(enhanced_response)
        
    except Exception as e:
        logger.error(f"Enhanced signal analysis error: {e}")
        return jsonify({
            'error': 'Failed to generate enhanced signal',
            'details': str(e),
            'api_version': '1.0.0',
            'server_time': datetime.now().isoformat()
        }), 500

@enhanced_gpts.route('/api/gpts/context/live', methods=['GET'])
@cross_origin()
def live_smc_context():
    """
    Live SMC Context untuk real-time decision making
    
    Returns:
    - Current market bias
    - Active structures
    - Heatmap warnings
    - Key levels
    """
    try:
        from ..core.structure_memory import smc_memory
        from ..core.smc_context_injector import smc_context_injector
        
        # Get current context
        context = smc_memory.get_context()
        summary = smc_memory.get_structure_summary()
        
        # Generate live status
        heatmap_status = smc_context_injector._generate_heatmap_status(context, summary)
        contextual_reasoning = smc_context_injector._generate_contextual_reasoning(
            context, summary, {"signal": "ANALYSIS"}
        )
        
        live_context = {
            "status": "success",
            "live_context": {
                "market_bias": summary.get('market_bias', 'NEUTRAL'),
                "heatmap_status": heatmap_status,
                "contextual_reasoning": contextual_reasoning,
                "active_structures": {
                    "bos_active": context.get('last_bos') is not None,
                    "choch_active": context.get('last_choch') is not None,
                    "bullish_ob_count": len(context.get('last_bullish_ob', [])),
                    "bearish_ob_count": len(context.get('last_bearish_ob', [])),
                    "fvg_count": len(context.get('last_fvg', [])),
                    "liquidity_active": context.get('last_liquidity') is not None
                },
                "key_levels": summary.get('key_levels', {}),
                "context_confidence": smc_context_injector._calculate_context_confidence(context)
            },
            "api_info": {
                "version": "2.0.0",
                "server_time": datetime.now().isoformat(),
                "service": "Enhanced GPTs Context API"
            }
        }
        
        return jsonify(live_context)
        
    except Exception as e:
        logger.error(f"Live SMC context error: {e}")
        return jsonify({
            'error': 'Failed to get live SMC context',
            'details': str(e),
            'api_version': '2.0.0',
            'server_time': datetime.now().isoformat()
        }), 500

@enhanced_gpts.route('/api/gpts/alerts/status', methods=['GET'])
@cross_origin()
def alert_system_status():
    """
    Status alert system dan recent alerts
    """
    try:
        from ..core.smc_alert_system import smc_alert_system
        
        alert_status = {
            "status": "success",
            "alert_system": {
                "telegram_enabled": smc_alert_system.telegram_enabled,
                "alert_threshold": smc_alert_system.alert_threshold,
                "recent_alerts_count": len(smc_alert_system.last_alerts),
                "system_health": "operational" if smc_alert_system.telegram_enabled else "telegram_disabled"
            },
            "api_info": {
                "version": "2.0.0",
                "server_time": datetime.now().isoformat(),
                "service": "SMC Alert System API"
            }
        }
        
        return jsonify(alert_status)
        
    except Exception as e:
        logger.error(f"Alert system status error: {e}")
        return jsonify({
            'error': 'Failed to get alert system status',
            'details': str(e)
        }), 500

@enhanced_gpts.route('/api/gpts/mitigation/update', methods=['POST'])
@cross_origin()
def update_mitigation_status():
    """
    Update mitigation status untuk Order Blocks
    
    Expected payload:
    {
        "symbol": "BTCUSDT",
        "timeframe": "1H",
        "ob_price": 43200.0,
        "ob_type": "bullish",
        "new_status": "reacted"
    }
    """
    try:
        from ..core.structure_memory import smc_memory
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        symbol = data.get('symbol', 'BTCUSDT')
        timeframe = data.get('timeframe', '1H')
        ob_price = data.get('ob_price')
        ob_type = data.get('ob_type', 'bullish')
        new_status = data.get('new_status', 'reacted')
        
        if not ob_price:
            return jsonify({'error': 'ob_price is required'}), 400
        
        # Update mitigation status
        context = smc_memory.get_context()
        updated = False
        
        ob_list = context.get(f'last_{ob_type}_ob', [])
        for ob in ob_list:
            if abs(ob.get('price_level', 0) - ob_price) < 1.0:  # Small tolerance for price matching
                ob['mitigation_status'] = new_status
                updated = True
                break
        
        response = {
            "status": "success" if updated else "not_found",
            "message": f"Mitigation status updated" if updated else f"Order Block not found",
            "updated_ob": {
                "symbol": symbol,
                "timeframe": timeframe,
                "price": ob_price,
                "type": ob_type,
                "new_status": new_status
            },
            "api_info": {
                "version": "2.0.0",
                "server_time": datetime.now().isoformat(),
                "service": "SMC Mitigation Update API"
            }
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Mitigation update error: {e}")
        return jsonify({
            'error': 'Failed to update mitigation status',
            'details': str(e)
        }), 500

logger.info("🚀 Enhanced GPTs Endpoints initialized")