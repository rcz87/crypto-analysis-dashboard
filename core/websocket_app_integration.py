"""
WebSocket Application Integration
Connects WebSocket server with existing signal engines
"""

import logging
from typing import Dict, Any
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

def integrate_websocket_with_app(app, ws_server):
    """
    Integrate WebSocket server with Flask app and signal engines
    """
    try:
        # Import necessary components
        from core.websocket_data_manager import ws_data_manager
        from core.realtime_signal_enhancer import realtime_enhancer, RealtimeSignalEnhancer
        from core.okx_websocket_simple import ws_manager_simple
        
        # Initialize realtime enhancer
        global realtime_enhancer
        if realtime_enhancer is None:
            realtime_enhancer = RealtimeSignalEnhancer(ws_data_manager)
        
        # Connect WebSocket data to Data Manager
        def on_ticker_update(data: Dict[str, Any]):
            """Handle ticker updates from OKX WebSocket"""
            ws_data_manager.process_ticker_update(data)
            # Queue for batching to WebSocket clients
            ws_server.queue_price_update(data)
        
        def on_orderbook_update(data: Dict[str, Any]):
            """Handle orderbook updates"""
            ws_data_manager.process_orderbook_update(data)
        
        def on_liquidation_update(data: Dict[str, Any]):
            """Handle liquidation data"""
            ws_data_manager.process_liquidation_update(data)
        
        # Register data handlers
        ws_data_manager.subscribe('price_update', on_ticker_update)
        ws_data_manager.subscribe('orderbook_imbalance', on_orderbook_update)
        ws_data_manager.subscribe('liquidation_event', on_liquidation_update)
        
        # Try to register existing signal engines
        try:
            from core.high_prob_signal_engine import holly_signal_engine
            ws_data_manager.register_signal_engine('holly', holly_signal_engine)
            logger.info("✅ Holly Signal Engine integrated with WebSocket")
        except ImportError:
            logger.warning("Holly Signal Engine not found")
        
        try:
            from core.smc_analyzer import SMCAnalyzer
            smc_analyzer = SMCAnalyzer()
            ws_data_manager.register_analysis_engine('smc', smc_analyzer)
            logger.info("✅ SMC Analyzer integrated with WebSocket")
        except ImportError:
            logger.warning("SMC Analyzer not found")
        
        try:
            from core.ai_reasoning_engine import AIReasoningEngine
            ai_engine = AIReasoningEngine()
            ws_data_manager.register_analysis_engine('ai_reasoning', ai_engine)
            logger.info("✅ AI Reasoning Engine integrated with WebSocket")
        except ImportError:
            logger.warning("AI Reasoning Engine not found")
        
        # Signal broadcast handler
        def broadcast_high_priority_signal(signal: Dict[str, Any]):
            """Broadcast high-priority signals"""
            try:
                # Enhance signal with real-time data
                enhanced_signal = realtime_enhancer.enhance_signal(signal)
                
                # Broadcast to WebSocket clients
                ws_server.broadcast_signal(enhanced_signal)
                
                # Send to Telegram if configured
                try:
                    from api.telegram_integration import send_telegram_signal
                    send_telegram_signal(enhanced_signal)
                except Exception as e:
                    logger.error(f"Telegram broadcast failed: {e}")
                    
            except Exception as e:
                logger.error(f"Signal broadcast error: {e}")
        
        # Register broadcast handler
        ws_data_manager.alert_handlers.append(broadcast_high_priority_signal)
        
        # Enhanced WebSocket API endpoints
        @app.route('/api/websocket/enhanced/status', methods=['GET'])
        def websocket_enhanced_status():
            """Get enhanced WebSocket status with integration info"""
            from flask import jsonify
            
            try:
                # Get comprehensive status
                status = {
                    'websocket_server': {
                        'active_connections': len(ws_server.active_connections),
                        'metrics': ws_server.metrics
                    },
                    'data_manager': ws_data_manager.get_metrics(),
                    'okx_websocket': ws_manager_simple.get_status(),
                    'integration_status': {
                        'signal_engines': list(ws_data_manager.signal_engines.keys()),
                        'analysis_engines': list(ws_data_manager.analysis_engines.keys()),
                        'alert_handlers': len(ws_data_manager.alert_handlers)
                    },
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
                
                return jsonify({
                    'success': True,
                    'status': status
                })
                
            except Exception as e:
                logger.error(f"Enhanced status error: {e}")
                return jsonify({'error': str(e)}), 500
        
        @app.route('/api/websocket/enhanced/trigger-analysis', methods=['POST'])
        def trigger_realtime_analysis():
            """Manually trigger real-time analysis for a symbol"""
            from flask import request, jsonify
            
            try:
                data = request.get_json() or {}
                symbol = data.get('symbol', 'BTC-USDT')
                
                # Get market snapshot
                snapshot = ws_data_manager.get_market_snapshot(symbol)
                
                # Trigger signal generation
                ws_data_manager._trigger_signal_generation(
                    symbol, 
                    'manual_trigger',
                    {'triggered_by': 'api', 'snapshot': snapshot}
                )
                
                return jsonify({
                    'success': True,
                    'message': f'Analysis triggered for {symbol}',
                    'market_snapshot': snapshot
                })
                
            except Exception as e:
                logger.error(f"Trigger analysis error: {e}")
                return jsonify({'error': str(e)}), 500
        
        @app.route('/api/websocket/enhanced/configure', methods=['POST'])
        def configure_websocket():
            """Configure WebSocket thresholds and batching"""
            from flask import request, jsonify
            
            try:
                data = request.get_json() or {}
                
                # Update trigger thresholds
                if 'trigger_thresholds' in data:
                    ws_data_manager.update_trigger_thresholds(data['trigger_thresholds'])
                
                # Update batch configuration
                if 'batch_config' in data:
                    for key, config in data['batch_config'].items():
                        if key in ws_server.batch_config:
                            ws_server.batch_config[key].update(config)
                
                return jsonify({
                    'success': True,
                    'message': 'Configuration updated',
                    'current_config': {
                        'trigger_thresholds': ws_data_manager.trigger_thresholds,
                        'batch_config': ws_server.batch_config
                    }
                })
                
            except Exception as e:
                logger.error(f"Configure error: {e}")
                return jsonify({'error': str(e)}), 500
        
        # Start WebSocket data manager
        ws_data_manager.start()
        
        logger.info("🚀 WebSocket fully integrated with trading systems")
        
        return True
        
    except Exception as e:
        logger.error(f"WebSocket integration error: {e}")
        return False

def initialize_websocket_connections():
    """
    Initialize WebSocket connections on startup
    """
    try:
        from core.okx_websocket_simple import ws_manager_simple
        from core.websocket_data_manager import ws_data_manager
        
        # Default symbols to track
        default_symbols = [
            'BTC-USDT', 'ETH-USDT', 'SOL-USDT', 
            'ADA-USDT', 'DOT-USDT', 'AVAX-USDT',
            'MATIC-USDT', 'LINK-USDT', 'UNI-USDT'
        ]
        
        # Start OKX WebSocket
        if not ws_manager_simple.is_started:
            success = ws_manager_simple.start(default_symbols)
            if success:
                logger.info(f"✅ OKX WebSocket started with {len(default_symbols)} symbols")
                
                # Connect OKX data to WebSocket Data Manager
                # This would need to be implemented in okx_websocket_simple.py
                # to call ws_data_manager.process_ticker_update() on new data
                
                return True
            else:
                logger.error("❌ Failed to start OKX WebSocket")
                return False
        
        return True
        
    except Exception as e:
        logger.error(f"WebSocket initialization error: {e}")
        return False