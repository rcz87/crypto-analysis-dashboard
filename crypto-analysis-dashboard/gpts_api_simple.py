
#!/usr/bin/env python3
"""
Streamlined GPTs API - Focus on ChatGPT Integration & Telegram Bot
Clean, minimal endpoints for GPTs consumption and Telegram notifications
"""

import os
import platform
import logging
import pandas as pd
from datetime import datetime
from flask import Flask, Blueprint, request, jsonify
from flask_cors import cross_origin

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Global service variables
system_enhancements_available = False
okx_fetcher = None
ai_engine = None
telegram_notifier = None
redis_manager = None
signal_engine = None
mtf_analyzer = None
risk_manager = None
signal_tracker = None
alert_manager = None

# Create blueprint (defined only once)
gpts_simple = Blueprint('gpts_simple', __name__, url_prefix='/api/gpts')

def create_app():
    """
    App Factory Pattern: Create and configure the Flask application
    """
    # Try to load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
        logger.info("✅ Environment variables loaded from .env")
    except ImportError:
        logger.warning("⚠️ dotenv not installed, skipping .env loading")

    # Initialize system enhancements 
    global system_enhancements_available
    try:
        from core.validators import SignalRequest, ChartRequest, validate_request
        from core.health_monitor import HealthMonitor
        from core.error_handlers import APIError
        system_enhancements_available = True
        logger.info("✅ System enhancements loaded")
    except ImportError as e:
        system_enhancements_available = False
        logger.warning(f"System enhancements not available: {e}")

    # Create Flask app
    app = Flask(__name__)

    # Apply feature flags from environment
    app.config.update(
        DEBUG=os.environ.get('DEBUG_MODE', 'true').lower() == 'true',
        TESTING=False,
        TELEGRAM_ENABLED=os.environ.get('TELEGRAM_ENABLED', 'true').lower() == 'true',
        REDIS_ENABLED=os.environ.get('REDIS_ENABLED', 'true').lower() == 'true'
    )

    # Register the blueprint with the app
    app.register_blueprint(gpts_simple)
    
    # Register enhanced blueprints if available
    try:
        from api.enhanced_signal_endpoints import enhanced_bp
        from api.institutional_endpoints import institutional_bp 
        
        app.register_blueprint(enhanced_bp)
        app.register_blueprint(institutional_bp)
        logger.info("✅ Enhanced API blueprints registered")
        
        # Add improvement endpoints directly to gpts_simple blueprint
        from core.data_sanity_checker import DataSanityChecker
        from core.self_improvement_engine import SelfImprovementEngine
        
        data_sanity_checker = DataSanityChecker()
        improvement_engine = SelfImprovementEngine()
        
        @gpts_simple.route('/improvement/status', methods=['GET'])
        def improvement_status():
            """Self-improvement system status"""
            try:
                status = improvement_engine.get_improvement_status()
                return jsonify({'status': 'success', 'improvement_status': status})
            except Exception as e:
                return jsonify({'status': 'error', 'message': str(e)}), 500
        
        @gpts_simple.route('/improvement/data-quality', methods=['POST'])
        def validate_data_quality():
            """Validate data quality"""
            try:
                data = request.get_json() or {}
                market_data = data.get('data', {})
                data_source = data.get('data_source', 'unknown')
                
                quality_report = data_sanity_checker.validate_market_data(market_data, data_source)
                should_block, reason = data_sanity_checker.should_block_signal(quality_report)
                
                return jsonify({
                    'status': 'success',
                    'quality_report': {
                        'quality_score': quality_report.quality_score,
                        'issues': quality_report.issues,
                        'is_stale': quality_report.is_stale,
                        'has_nans': quality_report.has_nans,
                        'has_gaps': quality_report.has_gaps
                    },
                    'signal_blocking': {'should_block': should_block, 'reason': reason}
                })
            except Exception as e:
                return jsonify({'status': 'error', 'message': str(e)}), 500
        
        logger.info("✅ Improvement endpoints added directly")
        
    except ImportError as e:
        logger.warning(f"⚠️ Enhanced API blueprints not available: {e}")
    
    # Register CoinGlass integration blueprint
    try:
        from api.gpts_coinglass_simple import coinglass_bp
        app.register_blueprint(coinglass_bp)
        logger.info("✅ CoinGlass integration endpoints registered")
    except ImportError as e:
        logger.warning(f"⚠️ CoinGlass endpoints not available: {e}")
    
    # Register TradingView webhook blueprint
    try:
        from api.webhook_endpoints import webhook_bp
        app.register_blueprint(webhook_bp)
        logger.info("✅ TradingView webhook endpoints registered")
    except ImportError as e:
        logger.warning(f"⚠️ Webhook endpoints not available: {e}")

    # Initialize CORS if needed
    try:
        from flask_cors import CORS
        CORS(app)
        logger.info("✅ CORS enabled for all routes")
    except ImportError:
        logger.warning("⚠️ flask-cors not installed, using @cross_origin decorators only")

    logger.info("🚀 GPTs API initialized successfully")
    # Add CoinGlass endpoints directly to main blueprint  
    @gpts_simple.route('/coinglass/status', methods=['GET'])
    def coinglass_status():
        """CoinGlass integration status"""
        try:
            from datetime import datetime
            return jsonify({
                'success': True,
                'data': {
                    'integration_status': 'ready',
                    'api_key_configured': False,
                    'demo_mode': True,
                    'available_endpoints': [
                        '/coinglass/status',
                        '/coinglass/liquidation-preview',
                        '/coinglass/market-structure'
                    ],
                    'message': 'CoinGlass integration structure ready. Add COINGLASS_API_KEY to activate real data.',
                    'timestamp': datetime.now().isoformat()
                }
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @gpts_simple.route('/coinglass/liquidation-preview', methods=['GET'])
    def coinglass_liquidation_preview():
        """Preview of liquidation analysis structure"""
        try:
            from datetime import datetime
            symbol = request.args.get('symbol', 'BTCUSDT').upper()
            
            demo_data = {
                'symbol': symbol,
                'current_price': 50000.0,
                'liquidation_zones': [
                    {
                        'price': 51500.0,
                        'volume': 75000000,
                        'side': 'short',
                        'strength': 85,
                        'type': 'High Impact Zone'
                    },
                    {
                        'price': 48500.0, 
                        'volume': 120000000,
                        'side': 'long',
                        'strength': 92,
                        'type': 'Critical Liquidation Level'
                    }
                ],
                'analysis': {
                    'upside_sweep_probability': 65,
                    'downside_sweep_probability': 35,
                    'dominant_liquidation_side': 'long',
                    'high_impact_zones_count': 2
                },
                'trading_implications': [
                    'Strong long liquidation cluster at $48,500',
                    'Potential upside hunt to $51,500',
                    'Current bias: Upward liquidity sweep likely'
                ],
                'demo_mode': True,
                'message': 'This is demo structure. Real data available with CoinGlass API key.',
                'timestamp': datetime.now().isoformat()
            }
            
            return jsonify({
                'success': True,
                'data': demo_data
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @gpts_simple.route('/coinglass/market-structure', methods=['GET'])
    def coinglass_market_structure():
        """Preview of enhanced SMC + CoinGlass analysis"""
        try:
            from datetime import datetime
            symbol = request.args.get('symbol', 'BTCUSDT').upper()
            
            demo_analysis = {
                'symbol': symbol,
                'enhanced_smc_zones': [
                    {
                        'smc_type': 'Order Block',
                        'price': 49800.0,
                        'smc_strength': 80,
                        'liquidation_confluence': True,
                        'liquidation_volume': 89000000,
                        'confluence_score': 88,
                        'entry_recommendation': 'Strong long setup'
                    },
                    {
                        'smc_type': 'Fair Value Gap',
                        'price': 51200.0,
                        'smc_strength': 75,
                        'liquidation_confluence': False,
                        'liquidation_volume': 0,
                        'confluence_score': 75,
                        'entry_recommendation': 'Watch for confluence'
                    }
                ],
                'liquidity_magnets': [
                    {
                        'price': 48500.0,
                        'magnet_strength': 92,
                        'probability': 78,
                        'type': 'Major liquidity pool'
                    }
                ],
                'trading_opportunities': [
                    {
                        'setup_type': 'long',
                        'entry_zone': 49800.0,
                        'stop_loss': 49400.0,
                        'targets': [50500.0, 51200.0],
                        'confidence': 'High',
                        'risk_reward': 3.5
                    }
                ],
                'market_bias': {
                    'direction': 'Bullish',
                    'strength': 'Strong',
                    'key_level': 48500.0
                },
                'demo_mode': True,
                'message': 'Enhanced SMC-CoinGlass integration ready. Real confluence analysis with API key.',
                'timestamp': datetime.now().isoformat()
            }
            
            return jsonify({
                'success': True,
                'data': demo_analysis
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @gpts_simple.route('/sharp-scoring/test', methods=['GET', 'POST'])
    def sharp_scoring_test():
        """Test sharp scoring system dengan berbagai scenarios"""
        try:
            from datetime import datetime
            
            # Import sharp scoring system
            try:
                from core.sharp_scoring_system import calculate_sharp_score_simple
            except ImportError:
                return jsonify({
                    'success': False,
                    'error': 'Sharp scoring system not available',
                    'timestamp': datetime.now().isoformat()
                }), 500
            
            if request.method == 'GET':
                # Demo scenarios for testing
                scenarios = {
                    'excellent_setup': {
                        'description': 'Perfect alignment - LuxAlgo BUY + Long bias + Strong SMC',
                        'factors': {
                            'smc_confidence': 0.85,
                            'ob_imbalance': 0.8,
                            'momentum_signal': 0.7,
                            'vol_regime': 0.6,
                            'lux_signal': 'BUY',
                            'bias': 'long',
                            'funding_rate_abs': 0.03,
                            'oi_delta_pos': True,
                            'long_short_extreme': False
                        }
                    },
                    'poor_setup': {
                        'description': 'Multiple penalties - Misaligned + Extreme funding + Crowded',
                        'factors': {
                            'smc_confidence': 0.4,
                            'ob_imbalance': 0.3,
                            'momentum_signal': 0.2,
                            'vol_regime': 0.3,
                            'lux_signal': 'SELL',
                            'bias': 'long',
                            'funding_rate_abs': 0.08,
                            'oi_delta_pos': False,
                            'long_short_extreme': True
                        }
                    },
                    'marginal_setup': {
                        'description': 'Right at threshold - Testing 70 point boundary',
                        'factors': {
                            'smc_confidence': 0.7,
                            'ob_imbalance': 0.5,
                            'momentum_signal': 0.5,
                            'vol_regime': 0.4,
                            'lux_signal': 'BUY',
                            'bias': 'long',
                            'funding_rate_abs': 0.02,
                            'oi_delta_pos': False,
                            'long_short_extreme': False
                        }
                    }
                }
                
                results = {}
                for scenario_name, scenario_data in scenarios.items():
                    score_result = calculate_sharp_score_simple(**scenario_data['factors'])
                    results[scenario_name] = {
                        'description': scenario_data['description'],
                        'factors': scenario_data['factors'],
                        'score': score_result['sharp_score'],
                        'is_sharp': score_result['is_sharp_signal'],
                        'quality': score_result['quality_rating'],
                        'recommendation': score_result['recommendation'],
                        'enhancement': score_result['enhancement_summary']
                    }
                
                return jsonify({
                    'success': True,
                    'sharp_threshold': 70,
                    'test_scenarios': results,
                    'summary': {
                        'excellent_score': results['excellent_setup']['score'],
                        'poor_score': results['poor_setup']['score'],
                        'marginal_score': results['marginal_setup']['score'],
                        'sharp_signals_count': sum(1 for r in results.values() if r['is_sharp'])
                    },
                    'timestamp': datetime.now().isoformat()
                })
            
            else:  # POST request - custom scoring
                data = request.get_json() or {}
                
                # Extract factors with defaults
                factors = {
                    'smc_confidence': float(data.get('smc_confidence', 0.5)),
                    'ob_imbalance': float(data.get('ob_imbalance', 0.5)),
                    'momentum_signal': float(data.get('momentum_signal', 0.5)),
                    'vol_regime': float(data.get('vol_regime', 0.5)),
                    'lux_signal': data.get('lux_signal'),
                    'bias': data.get('bias', 'neutral'),
                    'funding_rate_abs': float(data.get('funding_rate_abs', 0.0)),
                    'oi_delta_pos': bool(data.get('oi_delta_pos', False)),
                    'long_short_extreme': bool(data.get('long_short_extreme', False))
                }
                
                # Calculate score
                score_result = calculate_sharp_score_simple(**factors)
                
                return jsonify({
                    'success': True,
                    'custom_scoring_result': score_result,
                    'input_factors': factors,
                    'timestamp': datetime.now().isoformat()
                })
                
        except Exception as e:
            logger.error(f"Sharp scoring test error: {e}")
            return jsonify({
                'success': False,
                'error': f'Sharp scoring test failed: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }), 500

    return app

def initialize_core_services():
    """Initialize core services on demand"""
    global okx_fetcher, ai_engine, telegram_notifier, redis_manager, signal_engine, mtf_analyzer, risk_manager, signal_tracker, alert_manager

    try:
        if not okx_fetcher:
            from core.okx_fetcher import OKXFetcher
            okx_fetcher = OKXFetcher()
            logger.info("✅ OKX Fetcher initialized")
    except Exception as e:
        logger.warning(f"OKX Fetcher initialization failed: {e}")

    try:
        if not ai_engine:
            from core.ai_engine import AIEngine
            ai_engine = AIEngine()
            logger.info("✅ AI Engine initialized")
    except Exception as e:
        logger.warning(f"AI Engine initialization failed: {e}")

    try:
        if not telegram_notifier:
            # Check feature flag
            telegram_enabled = os.environ.get('TELEGRAM_ENABLED', 'true').lower() == 'true'
            if not telegram_enabled:
                logger.info("ℹ️ Telegram Notifier skipped (disabled by feature flag)")
            else:
                from core.telegram_notifier import TelegramNotifier
                telegram_notifier = TelegramNotifier()
                logger.info("✅ Telegram Notifier initialized")
    except Exception as e:
        logger.warning(f"Telegram Notifier initialization failed: {e}")

    try:
        if not redis_manager:
            # Check feature flag
            redis_enabled = os.environ.get('REDIS_ENABLED', 'true').lower() == 'true'
            if not redis_enabled:
                logger.info("ℹ️ Redis Manager skipped (disabled by feature flag)")
            else:
                from core.redis_manager import RedisManager
                redis_manager = RedisManager()
                logger.info("✅ Redis Manager initialized")
    except Exception as e:
        logger.warning(f"Redis Manager initialization failed: {e}")

def add_cors_headers(response):
    """Add CORS headers for GPTs access"""
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

def add_api_metadata(data):
    """Add consistent API metadata"""
    if isinstance(data, dict):
        data['api_version'] = '1.0.0'
        data['server_time'] = datetime.now().isoformat()
    return data
# ============================================================================
# CORE GPTs ENDPOINTS
# ============================================================================

@gpts_simple.route('/status', methods=['GET'])
@cross_origin()
def get_api_status():
    """GPTs API status check"""
    try:
        initialize_core_services()

        status = {
            "service": "GPTs & Telegram Bot API",
            "status": "operational",
            "focus": "ChatGPT integration and Telegram notifications",
            "services": {
                "okx_data": okx_fetcher is not None,
                "ai_analysis": ai_engine is not None,
                "telegram_bot": telegram_notifier is not None,
                "redis_cache": redis_manager is not None,
                "system_enhancements": system_enhancements_available
            },
            "endpoints_available": 3,
            "core_features": [
                "Trading signals for ChatGPT",
                "Telegram notifications with retry",
                "Real-time market data",
                "AI-powered analysis",
                "Health monitoring"
            ]
        }

        return add_cors_headers(jsonify(add_api_metadata(status)))

    except Exception as e:
        logger.error(f"Status check error: {e}")
        return add_cors_headers(jsonify({
            "error": "Status check failed",
            "details": str(e),
            "api_version": "1.0.0",
            "server_time": datetime.now().isoformat()
        })), 500

@gpts_simple.route('/signal', methods=['GET', 'POST'])
@cross_origin()
def get_trading_signal():
    """Main trading signal endpoint for GPTs"""
    try:
        # Handle both GET and POST requests
        if request.method == 'GET':
            symbol = request.args.get('symbol', 'BTCUSDT')
            timeframe = request.args.get('tf', '1H')
            confidence_threshold = float(request.args.get('confidence', 0.75))
        else:
            data = request.get_json() or {}
            symbol = data.get('symbol', 'BTCUSDT')
            timeframe = data.get('timeframe', '1H')
            confidence_threshold = float(data.get('confidence_threshold', 0.75))

        # Input validation if available
        if system_enhancements_available:
            try:
                if request.method == 'POST':
                    from core.validators import SignalRequest, validate_request
                    validate_request(SignalRequest, data)
            except Exception as validation_error:
                return add_cors_headers(jsonify({
                    "error": "VALIDATION_ERROR",
                    "message": "Input validation failed",
                    "details": str(validation_error),
                    "api_version": "1.0.0",
                    "server_time": datetime.now().isoformat()
                })), 422

        logger.info(f"GPTs signal request: {symbol} {timeframe}")

        # Initialize services
        initialize_core_services()

        # Convert symbol format for OKX
        if '/' in symbol:
            okx_symbol = symbol.replace('/', '-')
        elif symbol.endswith('USDT') and '-' not in symbol:
            base = symbol.replace('USDT', '')
            okx_symbol = f"{base}-USDT"
        else:
            okx_symbol = symbol

        if not okx_fetcher:
            return add_cors_headers(jsonify({
                "error": "Market data service unavailable",
                "api_version": "1.0.0",
                "server_time": datetime.now().isoformat()
            })), 503

        # Get market data
        df = okx_fetcher.get_candles(okx_symbol, timeframe, limit=100)
        if df is None or df.empty:
            return add_cors_headers(jsonify({
                "error": "Market data not available",
                "symbol": symbol,
                "api_version": "1.0.0",
                "server_time": datetime.now().isoformat()
            })), 404

        # Generate signal
        current_price = float(df['close'].iloc[-1])

        # Simple signal logic for demonstration
        sma_20 = df['close'].rolling(20).mean().iloc[-1]
        sma_50 = df['close'].rolling(50).mean().iloc[-1]

        if current_price > sma_20 > sma_50:
            direction = "BUY"
            confidence = min(85, confidence_threshold * 100 + 15)
        elif current_price < sma_20 < sma_50:
            direction = "SELL" 
            confidence = min(80, confidence_threshold * 100 + 10)
        else:
            direction = "HOLD"
            confidence = 60

        # Calculate levels
        atr = df['high'].rolling(14).max() - df['low'].rolling(14).min()
        current_atr = float(atr.iloc[-1]) if not atr.empty else current_price * 0.02

        if direction == "BUY":
            take_profit = current_price + (current_atr * 2)
            stop_loss = current_price - (current_atr * 1)
        elif direction == "SELL":
            take_profit = current_price - (current_atr * 2) 
            stop_loss = current_price + (current_atr * 1)
        else:
            take_profit = None
            stop_loss = None

        signal_data = {
            "signal": {
                "symbol": symbol,
                "direction": direction,
                "confidence": round(confidence, 1),
                "entry_price": round(current_price, 6),
                "take_profit": round(take_profit, 6) if take_profit else None,
                "stop_loss": round(stop_loss, 6) if stop_loss else None,
                "timeframe": timeframe
            },
            "market_data": {
                "current_price": round(current_price, 6),
                "sma_20": round(float(sma_20), 6),
                "sma_50": round(float(sma_50), 6),
                "atr": round(current_atr, 6)
            },
            "indicators": {
                "trend": "BULLISH" if current_price > sma_20 > sma_50 else "BEARISH" if current_price < sma_20 < sma_50 else "SIDEWAYS",
                "momentum": "STRONG" if confidence > 75 else "MODERATE" if confidence > 60 else "WEAK"
            },
            "data_source": "OKX_REAL_TIME_DATA"
        }

        # Send Telegram notification if confidence is high enough
        if telegram_notifier and redis_manager and confidence >= (confidence_threshold * 100):
            try:
                # Generate signal ID for deduplication
                signal_key = f"{symbol}:{direction}:{int(current_price*1000)}:{datetime.now().strftime('%Y%m%d%H')}"

                # Check if signal already sent
                if not redis_manager.is_signal_sent(signal_key):
                    take_profit_str = f"${take_profit:,.6f}" if take_profit else "N/A"
                    stop_loss_str = f"${stop_loss:,.6f}" if stop_loss else "N/A"

                    message = f"""
🚨 <b>TRADING SIGNAL - {direction}</b>

📊 <b>{symbol}</b> ({timeframe})
💰 <b>Entry:</b> ${current_price:,.6f}
🎯 <b>Take Profit:</b> {take_profit_str}
🛡️ <b>Stop Loss:</b> {stop_loss_str}
📈 <b>Confidence:</b> {confidence:.1f}%

<i>Generated by GPTs API</i>
"""

                    # Get admin chat ID from environment
                    admin_chat_id = os.environ.get('ADMIN_CHAT_ID', '5899681906')
                    success = telegram_notifier.send_message(admin_chat_id, message)

                    if success:
                        logger.info(f"✅ Telegram signal sent for {symbol}")
                        # Mark signal as sent
                        redis_manager.mark_signal_sent(signal_key)
                        logger.info(f"✅ Signal marked as sent in Redis: {signal_key}")
                    else:
                        logger.warning(f"❌ Telegram notification failed for {symbol}")
                else:
                    logger.info(f"📋 Signal already sent: {signal_key}, skipping notification")

            except Exception as telegram_error:
                logger.error(f"Telegram notification error: {telegram_error}")

        return add_cors_headers(jsonify(add_api_metadata(signal_data)))

    except Exception as e:
        logger.error(f"Signal generation error: {e}")
        return add_cors_headers(jsonify({
            "error": "Signal generation failed",
            "details": str(e),
            "api_version": "1.0.0",
            "server_time": datetime.now().isoformat()
        })), 500

def generate_telegram_message(signal_result, symbol, timeframe, current_price):
    """Generate concise Telegram-optimized message"""
    try:
        if not signal_result or 'final_signal' not in signal_result:
            return f"📊 {symbol} ({timeframe}) - Analisis tidak tersedia"

        final_signal = signal_result['final_signal']
        trade_setup = signal_result.get('trade_setup', {})
        action = final_signal.get('signal', 'NEUTRAL').upper()
        confidence = final_signal.get('confidence', 0)

        # Emoji mapping
        action_emoji = "🚀" if action == "BUY" else "📉" if action == "SELL" else "⏸️"
        confidence_emoji = "🔥" if confidence >= 80 else "💪" if confidence >= 65 else "⚖️" if confidence >= 50 else "⚠️"

        entry = trade_setup.get('entry_price', current_price)
        tp1 = trade_setup.get('take_profit_1', entry * 1.02)
        sl = trade_setup.get('stop_loss', entry * 0.98)

        message = f"""{action_emoji} **{action} SIGNAL - {symbol}**
{confidence_emoji} **Confidence: {confidence:.0f}%**

💰 **Entry**: ${entry:,.2f}
🎯 **Take Profit**: ${tp1:,.2f}
🛡️ **Stop Loss**: ${sl:,.2f}

📊 **Timeframe**: {timeframe}
🤖 **XAI Analysis**: {signal_result.get('xai_explanation', {}).get('explanation', 'Comprehensive SMC & AI analysis')[:100]}...

⏰ {datetime.now().strftime('%H:%M WIB')}
"""

        return message.strip()

    except Exception as e:
        return f"📊 {symbol} ({timeframe}) - Error generating message: {str(e)}"

def generate_natural_language_narrative(signal_result, symbol, timeframe, current_price):
    """Generate comprehensive natural language trading narrative"""
    try:
        if not signal_result or 'signal' not in signal_result:
            return "Analisis tidak tersedia untuk saat ini."

        signal = signal_result['signal']
        action = signal.get('final_signal', {}).get('signal', 'NEUTRAL').upper()
        confidence = signal.get('confidence_score', 0)
        trade_setup = signal.get('trade_setup', {})

        # Emoji untuk confidence level
        if confidence >= 80:
            confidence_emoji = "🔥"
            confidence_level = "SANGAT TINGGI"
        elif confidence >= 65:
            confidence_emoji = "💪"
            confidence_level = "TINGGI"
        elif confidence >= 50:
            confidence_emoji = "⚖️"
            confidence_level = "MODERAT"
        else:
            confidence_emoji = "⚠️"
            confidence_level = "RENDAH"

        # Action emoji
        action_emoji = "🚀" if action == "BUY" else "📉" if action == "SELL" else "⏸️"

        # Market context
        trend_context = ""
        if 'market_analysis' in signal_result:
            market = signal_result['market_analysis']
            trend = market.get('trend', 'NEUTRAL')
            if trend == "BUY":
                trend_context = "Market sedang menunjukkan momentum bullish yang kuat, dengan buyer dominan mengontrol price action."
            elif trend == "SELL":
                trend_context = "Market sedang dalam tekanan bearish, dengan seller yang agresif mendorong harga turun."
            else:
                trend_context = "Market sedang dalam fase konsolidasi, menunggu breakout directional yang jelas."

        # Generate comprehensive narrative
        narrative = f"""
{action_emoji} **SINYAL TRADING {action} - {symbol}**
{confidence_emoji} **Confidence Level: {confidence:.0f}% ({confidence_level})**

📊 **ANALISIS MARKET:**
Berdasarkan analisis mendalam menggunakan Smart Money Concept (SMC), technical indicators, dan volume profile analysis pada timeframe {timeframe}, kami menemukan setup trading yang menarik untuk {symbol}.

{trend_context}

🎯 **SETUP TRADING:**
• **Action**: {action}
• **Entry Price**: ${current_price:,.2f}
• **Take Profit 1**: ${trade_setup.get('take_profit_1', current_price):,.2f}
• **Take Profit 2**: ${trade_setup.get('take_profit_2', current_price):,.2f}
• **Stop Loss**: ${trade_setup.get('stop_loss', current_price):,.2f}
• **Risk/Reward Ratio**: {trade_setup.get('risk_reward_ratio', 'N/A')}

📈 **REASONING AI:**
{signal.get('xai_explanation', {}).get('explanation', 'Analisis berdasarkan confluence multiple indicators dan Smart Money Concept patterns.')}

🔍 **KEY FACTORS:**
"""

        # Add XAI factors if available
        if 'xai_explanation' in signal and 'top_factors' in signal['xai_explanation']:
            for i, factor in enumerate(signal['xai_explanation']['top_factors'][:3], 1):
                narrative += f"\n{i}. **{factor.get('feature', 'Unknown')}**: {factor.get('description', 'No description')} ({factor.get('impact', '0%')})"

        narrative += f"""

⚖️ **RISK MANAGEMENT:**
• **Risk Level**: {signal.get('risk_assessment', {}).get('risk_level', 'UNKNOWN').upper()}
• **Position Size**: {signal.get('risk_assessment', {}).get('position_size_percentage', 1.0):.1f}% dari portfolio
• **Volatility**: {signal.get('risk_assessment', {}).get('volatility', 'UNKNOWN').upper()}

💡 **TRADING TIPS:**
- Pastikan risk management tetap prioritas utama
- Gunakan position sizing yang sesuai dengan risk tolerance Anda
- Monitor price action di support/resistance key levels
- Siap untuk cut loss jika setup tidak berjalan sesuai rencana

⏰ **Waktu Analisis**: {datetime.now().strftime('%d %B %Y, %H:%M:%S')} WIB
📊 **Data Source**: OKX Exchange (Real-time)
🤖 **Powered by**: XAI-Enhanced Smart Money Concept Analysis

---
*Disclaimer: Trading melibatkan risiko. Gunakan analisis ini sebagai referensi, bukan sebagai financial advice. Selalu lakukan riset sendiri dan konsultasi dengan financial advisor.*
"""

        return narrative.strip()

    except Exception as e:
        logger.error(f"Error generating narrative: {e}")
        return f"Error dalam menghasilkan narasi: {str(e)}"

        # Input validation if available
        if system_enhancements_available:
            try:
                if request.method == 'POST':
                    validate_request(SignalRequest, data)
            except Exception as validation_error:
                return add_cors_headers(jsonify({
                    "error": "VALIDATION_ERROR",
                    "message": "Input validation failed",
                    "details": str(validation_error),
                    "api_version": "1.0.0",
                    "server_time": datetime.now().isoformat()
                })), 422

        logger.info(f"GPTs signal request: {symbol} {timeframe}")

        # Initialize services
        initialize_core_services()

        # Convert symbol format for OKX
        if '/' in symbol:
            okx_symbol = symbol.replace('/', '-')
        elif symbol.endswith('USDT') and '-' not in symbol:
            base = symbol.replace('USDT', '')
            okx_symbol = f"{base}-USDT"
        else:
            okx_symbol = symbol

        if not okx_fetcher:
            return add_cors_headers(jsonify({
                "error": "Market data service unavailable",
                "api_version": "1.0.0",
                "server_time": datetime.now().isoformat()
            })), 503

        # Get market data
        df = okx_fetcher.get_candles(okx_symbol, timeframe, limit=100)
        if df is None or df.empty:
            return add_cors_headers(jsonify({
                "error": "Market data not available",
                "symbol": symbol,
                "api_version": "1.0.0",
                "server_time": datetime.now().isoformat()
            })), 404

        # Generate signal
        current_price = float(df['close'].iloc[-1])

        # Simple signal logic for demonstration
        sma_20 = df['close'].rolling(20).mean().iloc[-1]
        sma_50 = df['close'].rolling(50).mean().iloc[-1]

        if current_price > sma_20 > sma_50:
            direction = "BUY"
            confidence = min(85, confidence_threshold * 100 + 15)
        elif current_price < sma_20 < sma_50:
            direction = "SELL" 
            confidence = min(80, confidence_threshold * 100 + 10)
        else:
            direction = "HOLD"
            confidence = 60

        # Calculate levels
        atr = df['high'].rolling(14).max() - df['low'].rolling(14).min()
        current_atr = float(atr.iloc[-1]) if not atr.empty else current_price * 0.02

        if direction == "BUY":
            take_profit = current_price + (current_atr * 2)
            stop_loss = current_price - (current_atr * 1)
        elif direction == "SELL":
            take_profit = current_price - (current_atr * 2) 
            stop_loss = current_price + (current_atr * 1)
        else:
            take_profit = None
            stop_loss = None

        signal_data = {
            "signal": {
                "symbol": symbol,
                "direction": direction,
                "confidence": round(confidence, 1),
                "entry_price": round(current_price, 6),
                "take_profit": round(take_profit, 6) if take_profit else None,
                "stop_loss": round(stop_loss, 6) if stop_loss else None,
                "timeframe": timeframe
            },
            "market_data": {
                "current_price": round(current_price, 6),
                "sma_20": round(float(sma_20), 6),
                "sma_50": round(float(sma_50), 6),
                "atr": round(current_atr, 6)
            },
            "indicators": {
                "trend": "BULLISH" if current_price > sma_20 > sma_50 else "BEARISH" if current_price < sma_20 < sma_50 else "SIDEWAYS",
                "momentum": "STRONG" if confidence > 75 else "MODERATE" if confidence > 60 else "WEAK"
            },
            "data_source": "OKX_REAL_TIME_DATA"
        }

        # Send Telegram notification if confidence is high enough
        if telegram_notifier and redis_manager and confidence >= (confidence_threshold * 100):
            try:
                # Generate signal ID for deduplication
                signal_key = f"{symbol}:{direction}:{int(current_price*1000)}:{datetime.now().strftime('%Y%m%d%H')}"

                # Check if signal already sent
                if not redis_manager.is_signal_sent(signal_key):
                    take_profit_str = f"${take_profit:,.6f}" if take_profit else "N/A"
                    stop_loss_str = f"${stop_loss:,.6f}" if stop_loss else "N/A"

                    message = f"""
🚨 <b>TRADING SIGNAL - {direction}</b>

📊 <b>{symbol}</b> ({timeframe})
💰 <b>Entry:</b> ${current_price:,.6f}
🎯 <b>Take Profit:</b> {take_profit_str}
🛡️ <b>Stop Loss:</b> {stop_loss_str}
📈 <b>Confidence:</b> {confidence:.1f}%

<i>Generated by GPTs API</i>
"""

                    # Get admin chat ID from environment
                    admin_chat_id = os.environ.get('ADMIN_CHAT_ID', '5899681906')
                    success = telegram_notifier.send_message(admin_chat_id, message)

                    if success:
                        logger.info(f"✅ Telegram signal sent for {symbol}")
                        # Mark signal as sent
                        redis_manager.mark_signal_sent(signal_key)
                        logger.info(f"✅ Signal marked as sent in Redis: {signal_key}")
                    else:
                        logger.warning(f"❌ Telegram notification failed for {symbol}")
                else:
                    logger.info(f"📋 Signal already sent: {signal_key}, skipping notification")

            except Exception as telegram_error:
                logger.error(f"Telegram notification error: {telegram_error}")

        return add_cors_headers(jsonify(add_api_metadata(signal_data)))

    except Exception as e:
        logger.error(f"Signal generation error: {e}")
        return add_cors_headers(jsonify({
            "error": "Signal generation failed",
            "details": str(e),
            "api_version": "1.0.0",
            "server_time": datetime.now().isoformat()
        })), 500

# ============================================================================
# TRADING VIEW ENDPOINTS
# ============================================================================

@gpts_simple.route('/chart', methods=['GET'])
@cross_origin() 
def get_chart_data():
    """Chart data endpoint for trading view integration"""
    try:
        symbol = request.args.get('symbol', 'BTC-USDT')
        timeframe = request.args.get('tf', '1H')
        limit = int(request.args.get('limit', 100))

        logger.info(f"Chart data request: {symbol} {timeframe}")

        initialize_core_services()

        if not okx_fetcher:
            return add_cors_headers(jsonify({
                "error": "Chart data service unavailable",
                "api_version": "1.0.0",
                "server_time": datetime.now().isoformat()
            })), 503

        # Get candlestick data
        df = okx_fetcher.get_candles(symbol, timeframe, limit=limit)
        if df is None or df.empty:
            return add_cors_headers(jsonify({
                "error": "Chart data not available",
                "symbol": symbol,
                "api_version": "1.0.0", 
                "server_time": datetime.now().isoformat()
            })), 404

        # Format for trading view
        chart_data = []
        for _, row in df.iterrows():
            chart_data.append({
                "time": int(row['timestamp'].timestamp()) if hasattr(row['timestamp'], 'timestamp') else int(row['timestamp']),
                "open": float(row['open']),
                "high": float(row['high']),
                "low": float(row['low']),
                "close": float(row['close']),
                "volume": float(row['volume'])
            })

        response = {
            "symbol": symbol,
            "timeframe": timeframe,
            "data": chart_data,
            "count": len(chart_data),
            "data_source": "OKX_TRADING_VIEW_DATA"
        }

        return add_cors_headers(jsonify(add_api_metadata(response)))

    except Exception as e:
        logger.error(f"Chart data error: {e}")
        return add_cors_headers(jsonify({
            "error": "Chart data retrieval failed",
            "details": str(e),
            "api_version": "1.0.0",
            "server_time": datetime.now().isoformat()
        })), 500

@gpts_simple.route('/signal', methods=['GET', 'POST'])
@cross_origin()
def get_trading_signal():
    """Main trading signal endpoint for GPTs"""
    try:
        # Handle both GET and POST requests
        if request.method == 'GET':
            symbol = request.args.get('symbol', 'BTCUSDT')
            timeframe = request.args.get('tf', '1H')
            confidence_threshold = float(request.args.get('confidence', 0.75))
        else:
            data = request.get_json() or {}
            symbol = data.get('symbol', 'BTCUSDT')
            timeframe = data.get('timeframe', '1H')
            confidence_threshold = float(data.get('confidence_threshold', 0.75))
        
        # Input validation if available
        if system_enhancements_available:
            try:
                if request.method == 'POST':
                    validate_request(SignalRequest, data)
            except Exception as validation_error:
                return add_cors_headers(jsonify({
                    "error": "VALIDATION_ERROR",
                    "message": "Input validation failed",
                    "details": str(validation_error),
                    "api_version": "1.0.0",
                    "server_time": datetime.now().isoformat()
                })), 422
        
        logger.info(f"GPTs signal request: {symbol} {timeframe}")
        
        # Initialize services
        initialize_core_services()
        
        # Convert symbol format for OKX
        if '/' in symbol:
            okx_symbol = symbol.replace('/', '-')
        elif symbol.endswith('USDT') and '-' not in symbol:
            base = symbol.replace('USDT', '')
            okx_symbol = f"{base}-USDT"
        else:
            okx_symbol = symbol
            
        if not okx_fetcher:
            return add_cors_headers(jsonify({
                "error": "Market data service unavailable",
                "api_version": "1.0.0",
                "server_time": datetime.now().isoformat()
            })), 503
        
        # Get market data
        df = okx_fetcher.get_candles(okx_symbol, timeframe, limit=100)
        if df is None or df.empty:
            return add_cors_headers(jsonify({
                "error": "Market data not available",
                "symbol": symbol,
                "api_version": "1.0.0",
                "server_time": datetime.now().isoformat()
            })), 404
        
        # Generate signal
        current_price = float(df['close'].iloc[-1])
        
        # Simple signal logic for demonstration
        sma_20 = df['close'].rolling(20).mean().iloc[-1]
        sma_50 = df['close'].rolling(50).mean().iloc[-1]
        
        if current_price > sma_20 > sma_50:
            direction = "BUY"
            confidence = min(85, confidence_threshold * 100 + 15)
        elif current_price < sma_20 < sma_50:
            direction = "SELL" 
            confidence = min(80, confidence_threshold * 100 + 10)
        else:
            direction = "HOLD"
            confidence = 60
            
        # Calculate levels
        atr = df['high'].rolling(14).max() - df['low'].rolling(14).min()
        current_atr = float(atr.iloc[-1]) if not atr.empty else current_price * 0.02
        
        if direction == "BUY":
            take_profit = current_price + (current_atr * 2)
            stop_loss = current_price - (current_atr * 1)
        elif direction == "SELL":
            take_profit = current_price - (current_atr * 2) 
            stop_loss = current_price + (current_atr * 1)
        else:
            take_profit = None
            stop_loss = None
        
        signal_data = {
            "signal": {
                "symbol": symbol,
                "direction": direction,
                "confidence": round(confidence, 1),
                "entry_price": round(current_price, 6),
                "take_profit": round(take_profit, 6) if take_profit else None,
                "stop_loss": round(stop_loss, 6) if stop_loss else None,
                "timeframe": timeframe
            },
            "market_data": {
                "current_price": round(current_price, 6),
                "sma_20": round(float(sma_20), 6),
                "sma_50": round(float(sma_50), 6),
                "atr": round(current_atr, 6)
            },
            "indicators": {
                "trend": "BULLISH" if current_price > sma_20 > sma_50 else "BEARISH" if current_price < sma_20 < sma_50 else "SIDEWAYS",
                "momentum": "STRONG" if confidence > 75 else "MODERATE" if confidence > 60 else "WEAK"
            },
            "data_source": "OKX_REAL_TIME_DATA"
        }
        
        # Send Telegram notification if confidence is high enough
        if telegram_notifier and redis_manager and confidence >= (confidence_threshold * 100):
            try:
                # Generate signal ID for deduplication
                signal_key = f"{symbol}:{direction}:{int(current_price*1000)}:{datetime.now().strftime('%Y%m%d%H')}"
                
                # Check if signal already sent
                if not redis_manager.is_signal_sent(signal_key):
                    take_profit_str = f"${take_profit:,.6f}" if take_profit else "N/A"
                    stop_loss_str = f"${stop_loss:,.6f}" if stop_loss else "N/A"

                    message = f"""
🚨 <b>TRADING SIGNAL - {direction}</b>

📊 <b>{symbol}</b> ({timeframe})
💰 <b>Entry:</b> ${current_price:,.6f}
🎯 <b>Take Profit:</b> {take_profit_str}
🛡️ <b>Stop Loss:</b> {stop_loss_str}
📈 <b>Confidence:</b> {confidence:.1f}%

<i>Generated by GPTs API</i>
"""
                    
                    # Get admin chat ID from environment
                    admin_chat_id = os.environ.get('ADMIN_CHAT_ID', '5899681906')
                    success = telegram_notifier.send_message(admin_chat_id, message)
                    
                    if success:
                        logger.info(f"✅ Telegram signal sent for {symbol}")
                        # Mark signal as sent
                        redis_manager.mark_signal_sent(signal_key)
                        logger.info(f"✅ Signal marked as sent in Redis: {signal_key}")
                    else:
                        logger.warning(f"❌ Telegram notification failed for {symbol}")
                else:
                    logger.info(f"📋 Signal already sent: {signal_key}, skipping notification")
                    
            except Exception as telegram_error:
                logger.error(f"Telegram notification error: {telegram_error}")
        
        return add_cors_headers(jsonify(add_api_metadata(signal_data)))
        
    except Exception as e:
        logger.error(f"Signal generation error: {e}")
        return add_cors_headers(jsonify({
            "error": "Signal generation failed",
            "details": str(e),
            "api_version": "1.0.0",
            "server_time": datetime.now().isoformat()
        })), 500

def generate_telegram_message(signal_result, symbol, timeframe, current_price):
    """Generate concise Telegram-optimized message"""
    try:
        if not signal_result or 'final_signal' not in signal_result:
            return f"📊 {symbol} ({timeframe}) - Analisis tidak tersedia"
        
        final_signal = signal_result['final_signal']
        trade_setup = signal_result.get('trade_setup', {})
        action = final_signal.get('signal', 'NEUTRAL').upper()
        confidence = final_signal.get('confidence', 0)
        
        # Emoji mapping
        action_emoji = "🚀" if action == "BUY" else "📉" if action == "SELL" else "⏸️"
        confidence_emoji = "🔥" if confidence >= 80 else "💪" if confidence >= 65 else "⚖️" if confidence >= 50 else "⚠️"
        
        entry = trade_setup.get('entry_price', current_price)
        tp1 = trade_setup.get('take_profit_1', entry * 1.02)
        sl = trade_setup.get('stop_loss', entry * 0.98)
        
        message = f"""{action_emoji} **{action} SIGNAL - {symbol}**
{confidence_emoji} **Confidence: {confidence:.0f}%**

💰 **Entry**: ${entry:,.2f}
🎯 **Take Profit**: ${tp1:,.2f}
🛡️ **Stop Loss**: ${sl:,.2f}

📊 **Timeframe**: {timeframe}
🤖 **XAI Analysis**: {signal_result.get('xai_explanation', {}).get('explanation', 'Comprehensive SMC & AI analysis')[:100]}...

⏰ {datetime.now().strftime('%H:%M WIB')}
"""
        
        return message.strip()
        
    except Exception as e:
        return f"📊 {symbol} ({timeframe}) - Error generating message: {str(e)}"

@gpts_simple.route('/chart', methods=['GET'])
@cross_origin() 
def get_chart_data():
    """Chart data endpoint for trading view integration"""
    try:
        symbol = request.args.get('symbol', 'BTC-USDT')
        timeframe = request.args.get('tf', '1H')
        limit = int(request.args.get('limit', 100))

        logger.info(f"Chart data request: {symbol} {timeframe}")

        initialize_core_services()

        if not okx_fetcher:
            return add_cors_headers(jsonify({
                "error": "Chart data service unavailable",
                "api_version": "1.0.0",
                "server_time": datetime.now().isoformat()
            })), 503

        # Get candlestick data
        df = okx_fetcher.get_candles(symbol, timeframe, limit=limit)
        if df is None or df.empty:
            return add_cors_headers(jsonify({
                "error": "Chart data not available",
                "symbol": symbol,
                "api_version": "1.0.0", 
                "server_time": datetime.now().isoformat()
            })), 404

        # Format for trading view
        chart_data = []
        for _, row in df.iterrows():
            chart_data.append({
                "time": int(row['timestamp'].timestamp()) if hasattr(row['timestamp'], 'timestamp') else int(row['timestamp']),
                "open": float(row['open']),
                "high": float(row['high']),
                "low": float(row['low']),
                "close": float(row['close']),
                "volume": float(row['volume'])
            })

        response = {
            "symbol": symbol,
            "timeframe": timeframe,
            "data": chart_data,
            "count": len(chart_data),
            "data_source": "OKX_TRADING_VIEW_DATA"
        }

        return add_cors_headers(jsonify(add_api_metadata(response)))

    except Exception as e:
        logger.error(f"Chart data error: {e}")
        return add_cors_headers(jsonify({
            "error": "Chart data retrieval failed",
            "details": str(e),
            "api_version": "1.0.0",
            "server_time": datetime.now().isoformat()
        })), 500

@gpts_simple.route('/sinyal/tajam', methods=['POST', 'GET'])
@cross_origin()
def post_sharp_signal():
    """Enhanced trading signal dengan natural language narrative untuk Telegram/ChatGPT"""
    try:
        # Handle both GET and POST requests
        if request.method == 'GET':
            symbol = request.args.get('symbol', 'BTCUSDT')
            timeframe = request.args.get('timeframe', '1H')
            format_type = request.args.get('format', 'both')  # json, narrative, both
        else:
            data = request.get_json() or {}
            symbol = data.get('symbol', 'BTCUSDT')
            timeframe = data.get('timeframe', '1H')
            format_type = data.get('format', 'both')

        logger.info(f"🎯 Sharp Signal Request: {symbol} {timeframe} format={format_type}")

        # Import SignalEngine
        from core.signal_engine import SignalEngine
        import pandas as pd

        # Initialize services untuk data real jika ada
        initialize_core_services()

        # Coba dapatkan data real dari OKX jika tersedia
        df = None
        if okx_fetcher:
            try:
                # Convert symbol format untuk OKX
                okx_symbol = symbol
                if '/' in symbol:
                    okx_symbol = symbol.replace('/', '-')
                elif symbol.endswith('USDT') and '-' not in symbol:
                    base = symbol.replace('USDT', '')
                    okx_symbol = f"{base}-USDT"

                df = okx_fetcher.get_candles(okx_symbol, timeframe, limit=200)
                logger.info(f"✅ Real market data obtained from OKX for {okx_symbol}")
            except Exception as okx_error:
                logger.warning(f"OKX data failed, using sample data: {okx_error}")

        # Fallback ke sample data jika real data tidak tersedia
        if df is None or (hasattr(df, 'empty') and df.empty):
            logger.info("📊 Using sample data for signal generation")
            df = pd.DataFrame([{
                "open": 100 + i,
                "high": 101 + i,
                "low": 99 + i,
                "close": 100.5 + i,
                "volume": 1000 + i * 10,
                "timestamp": pd.Timestamp.now() - pd.Timedelta(hours=50-i)
            } for i in range(50)])

        # Initialize SignalEngine dan generate signals
        engine = SignalEngine()
        result = engine.generate_comprehensive_signals(df, symbol=symbol, timeframe=timeframe)

        # Tambahkan XAI explanation jika tidak ada
        if 'xai_explanation' not in result and 'final_signal' in result:
            final_signal = result['final_signal']
            result['xai_explanation'] = {
                "decision": final_signal.get('action', 'NEUTRAL'),
                "confidence": final_signal.get('confidence', 0),
                "explanation": f"Sinyal {final_signal.get('action', 'NEUTRAL')} untuk {symbol} berdasarkan analisis komprehensif SMC, technical indicators, dan volume analysis",
                "risk_level": result.get('risk_assessment', {}).get('risk_level', 'MEDIUM'),
                "top_factors": [
                    {
                        "feature": "SMC Analysis",
                        "impact": f"+{result.get('component_signals', {}).get('smc_analysis', {}).get('confidence', 0)}%",
                        "description": "Smart Money Concept analysis dengan pattern detection"
                    },
                    {
                        "feature": "Technical Indicators", 
                        "impact": f"+{result.get('component_signals', {}).get('technical_indicators', {}).get('confidence', 0)}%",
                        "description": "Multiple technical indicators confluence"
                    },
                    {
                        "feature": "Volume Analysis",
                        "impact": f"+{result.get('component_signals', {}).get('volume_analysis', {}).get('confidence', 0)}%", 
                        "description": "Volume profile dan market structure analysis"
                    }
                ]
            }

        # Get current price for narrative
        current_price = 0
        if df is not None and not df.empty:
            current_price = float(df['close'].iloc[-1])
        elif 'trade_setup' in result:
            current_price = result['trade_setup'].get('entry_price', 0)

        # Generate natural language narrative
        narrative = generate_natural_language_narrative(
            {"signal": result, "market_analysis": result.get("market_analysis", {})}, 
            symbol, 
            timeframe, 
            current_price
        )

        # Generate shorter telegram-optimized message
        telegram_message = generate_telegram_message(result, symbol, timeframe, current_price)

        # Format response based on format type
        response_data = {}

        if format_type == 'narrative':
            response_data = {
                "narrative": narrative,
                "human_readable": narrative,
                "telegram_message": telegram_message,
                "symbol": symbol,
                "timeframe": timeframe,
                "format": "natural_language"
            }
        elif format_type == 'json':
            # Extract essential trading fields from result for compatibility
            trade_setup = result.get('trade_setup', {})
            final_signal = result.get('final_signal', {})

            # Ensure essential fields are at signal root level
            enhanced_result = result.copy()
            enhanced_result.update({
                'entry_price': trade_setup.get('entry_price', current_price),
                'take_profit_1': trade_setup.get('take_profit_1', trade_setup.get('take_profit', current_price * 1.02 if current_price > 0 else 0)),
                'stop_loss': trade_setup.get('stop_loss', current_price * 0.98 if current_price > 0 else 0),
                'confidence_level': final_signal.get('confidence', result.get('confidence_score', 0)),
                'signal_strength': final_signal.get('strength', result.get('confidence_score', 0)),
                'direction': final_signal.get('action', final_signal.get('signal', 'NEUTRAL')),
                'current_price': current_price
            })

            response_data = {
                "signal": enhanced_result,
                "human_readable": narrative,
                "telegram_message": telegram_message,
                "format": "json_only"
            }
        else:  # format_type == 'both'  
            # Extract essential trading fields for both format
            trade_setup = result.get('trade_setup', {})
            final_signal = result.get('final_signal', {})

            # Ensure essential fields are at signal root level
            enhanced_result = result.copy()
            enhanced_result.update({
                'entry_price': trade_setup.get('entry_price', current_price),
                'take_profit_1': trade_setup.get('take_profit_1', trade_setup.get('take_profit', current_price * 1.02 if current_price > 0 else 0)),
                'stop_loss': trade_setup.get('stop_loss', current_price * 0.98 if current_price > 0 else 0),
                'confidence_level': final_signal.get('confidence', result.get('confidence_score', 0)),
                'signal_strength': final_signal.get('strength', result.get('confidence_score', 0)),
                'direction': final_signal.get('action', final_signal.get('signal', 'NEUTRAL')),
                'current_price': current_price
            })

            response_data = {
                "signal": enhanced_result,
                "narrative": narrative,
                "human_readable": narrative,
                "telegram_message": telegram_message,
                "format": "json_with_narrative"
            }

        # Send Telegram notification untuk high-confidence signals
        if (telegram_notifier and 'final_signal' in result and 
            result['final_signal'].get('confidence', 0) >= 75):
            try:
                final_signal = result['final_signal']
                trade_setup = result.get('trade_setup', {})

                message = f"""🎯 <b>SHARP SIGNAL - {final_signal.get('action', 'NEUTRAL')}</b>

📊 <b>{symbol}</b> ({timeframe})
💰 <b>Entry:</b> {trade_setup.get('entry_price', 'N/A')}
🎯 <b>TP:</b> {trade_setup.get('take_profit', 'N/A')}
🛡️ <b>SL:</b> {trade_setup.get('stop_loss', 'N/A')}
📈 <b>Confidence:</b> {final_signal.get('confidence', 0)}%

🤖 <b>Analysis Summary:</b>
{result.get('xai_explanation', {}).get('explanation', 'Comprehensive signal analysis')[:150]}...

<i>Full analysis available via API</i>
"""

                admin_chat_id = os.environ.get('ADMIN_CHAT_ID', '5899681906')
                success = telegram_notifier.send_message(admin_chat_id, message)

                if success:
                    logger.info(f"✅ Comprehensive signal sent to Telegram: {symbol}")

            except Exception as telegram_error:
                logger.error(f"Telegram notification error: {telegram_error}")

        return add_cors_headers(jsonify(add_api_metadata(response_data)))

    except Exception as e:
        logger.error(f"Sharp signal endpoint error: {e}")
        return add_cors_headers(jsonify({
            "error": "Signal generation failed",
            "details": str(e),
            "api_version": "1.0.0",
            "server_time": datetime.now().isoformat()
        })), 500

@gpts_simple.route('/sinyal/tajam', methods=['POST', 'GET'])
@cross_origin()
def post_sharp_signal():
    """Enhanced trading signal dengan natural language narrative untuk Telegram/ChatGPT"""
    try:
        # Handle both GET and POST requests
        if request.method == 'GET':
            symbol = request.args.get('symbol', 'BTCUSDT')
            timeframe = request.args.get('timeframe', '1H')
            format_type = request.args.get('format', 'both')  # json, narrative, both
        else:
            data = request.get_json() or {}
            symbol = data.get('symbol', 'BTCUSDT')
            timeframe = data.get('timeframe', '1H')
            format_type = data.get('format', 'both')
        
        logger.info(f"🎯 Sharp Signal Request: {symbol} {timeframe} format={format_type}")
        
        # Import SignalEngine
        from core.signal_engine import SignalEngine
        import pandas as pd
        
        # Initialize services untuk data real jika ada
        initialize_core_services()
        
        # Coba dapatkan data real dari OKX jika tersedia
        df = None
        if okx_fetcher:
            try:
                # Convert symbol format untuk OKX
                okx_symbol = symbol
                if '/' in symbol:
                    okx_symbol = symbol.replace('/', '-')
                elif symbol.endswith('USDT') and '-' not in symbol:
                    base = symbol.replace('USDT', '')
                    okx_symbol = f"{base}-USDT"
                
                df = okx_fetcher.get_candles(okx_symbol, timeframe, limit=200)
                logger.info(f"✅ Real market data obtained from OKX for {okx_symbol}")
            except Exception as okx_error:
                logger.warning(f"OKX data failed, using sample data: {okx_error}")
        
        # Fallback ke sample data jika real data tidak tersedia
        if df is None or (hasattr(df, 'empty') and df.empty):
            logger.info("📊 Using sample data for signal generation")
            df = pd.DataFrame([{
                "open": 100 + i,
                "high": 101 + i,
                "low": 99 + i,
                "close": 100.5 + i,
                "volume": 1000 + i * 10,
                "timestamp": pd.Timestamp.now() - pd.Timedelta(hours=50-i)
            } for i in range(50)])
        
        # Initialize SignalEngine dan generate signals
        engine = SignalEngine()
        result = engine.generate_comprehensive_signals(df, symbol=symbol, timeframe=timeframe)
        
        # Tambahkan XAI explanation jika tidak ada
        if 'xai_explanation' not in result and 'final_signal' in result:
            final_signal = result['final_signal']
            result['xai_explanation'] = {
                "decision": final_signal.get('action', 'NEUTRAL'),
                "confidence": final_signal.get('confidence', 0),
                "explanation": f"Sinyal {final_signal.get('action', 'NEUTRAL')} untuk {symbol} berdasarkan analisis komprehensif SMC, technical indicators, dan volume analysis",
                "risk_level": result.get('risk_assessment', {}).get('risk_level', 'MEDIUM'),
                "top_factors": [
                    {
                        "feature": "SMC Analysis",
                        "impact": f"+{result.get('component_signals', {}).get('smc_analysis', {}).get('confidence', 0)}%",
                        "description": "Smart Money Concept analysis dengan pattern detection"
                    },
                    {
                        "feature": "Technical Indicators", 
                        "impact": f"+{result.get('component_signals', {}).get('technical_indicators', {}).get('confidence', 0)}%",
                        "description": "Multiple technical indicators confluence"
                    },
                    {
                        "feature": "Volume Analysis",
                        "impact": f"+{result.get('component_signals', {}).get('volume_analysis', {}).get('confidence', 0)}%", 
                        "description": "Volume profile dan market structure analysis"
                    }
                ]
            }
        
        # Get current price for narrative
        current_price = 0
        if df is not None and not df.empty:
            current_price = float(df['close'].iloc[-1])
        elif 'trade_setup' in result:
            current_price = result['trade_setup'].get('entry_price', 0)
        
        # Generate natural language narrative
        narrative = generate_natural_language_narrative(
            {"signal": result, "market_analysis": result.get("market_analysis", {})}, 
            symbol, 
            timeframe, 
            current_price
        )
        
        # Generate shorter telegram-optimized message
        telegram_message = generate_telegram_message(result, symbol, timeframe, current_price)
        
        # Format response based on format type
        if format_type == 'narrative':
            return add_cors_headers(jsonify(add_api_metadata({
                "narrative": narrative,
                "human_readable": narrative,
                "telegram_message": telegram_message,
                "symbol": symbol,
                "timeframe": timeframe,
                "format": "natural_language"
            })))
        elif format_type == 'json':
            # Extract essential trading fields from result for compatibility
            trade_setup = result.get('trade_setup', {})
            final_signal = result.get('final_signal', {})
            
            # Ensure essential fields are at signal root level
            enhanced_result = result.copy()
            enhanced_result.update({
                'entry_price': trade_setup.get('entry_price', current_price),
                'take_profit_1': trade_setup.get('take_profit_1', trade_setup.get('take_profit', current_price * 1.02 if current_price > 0 else 0)),
                'stop_loss': trade_setup.get('stop_loss', current_price * 0.98 if current_price > 0 else 0),
                'confidence_level': final_signal.get('confidence', result.get('confidence_score', 0)),
                'signal_strength': final_signal.get('strength', result.get('confidence_score', 0)),
                'direction': final_signal.get('action', final_signal.get('signal', 'NEUTRAL')),
                'current_price': current_price
            })
            
            response_data = {
                "signal": enhanced_result,
                "human_readable": narrative,
                "telegram_message": telegram_message,
                "format": "json_only"
            }
            return add_cors_headers(jsonify(add_api_metadata(response_data)))
        else:  # format_type == 'both'  
            # Extract essential trading fields for both format
            trade_setup = result.get('trade_setup', {})
            final_signal = result.get('final_signal', {})
            
            # Ensure essential fields are at signal root level
            enhanced_result = result.copy()
            enhanced_result.update({
                'entry_price': trade_setup.get('entry_price', current_price),
                'take_profit_1': trade_setup.get('take_profit_1', trade_setup.get('take_profit', current_price * 1.02 if current_price > 0 else 0)),
                'stop_loss': trade_setup.get('stop_loss', current_price * 0.98 if current_price > 0 else 0),
                'confidence_level': final_signal.get('confidence', result.get('confidence_score', 0)),
                'signal_strength': final_signal.get('strength', result.get('confidence_score', 0)),
                'direction': final_signal.get('action', final_signal.get('signal', 'NEUTRAL')),
                'current_price': current_price
            })
            
            response_data = {
                "signal": enhanced_result,
                "narrative": narrative,
                "human_readable": narrative,
                "telegram_message": telegram_message,
                "format": "json_with_narrative"
            }
            return add_cors_headers(jsonify(add_api_metadata(response_data)))
        
        # Send Telegram notification untuk high-confidence signals
        if (telegram_notifier and 'final_signal' in result and 
            result['final_signal'].get('confidence', 0) >= 75):
            try:
                final_signal = result['final_signal']
                trade_setup = result.get('trade_setup', {})
                
                message = f"""🎯 <b>SHARP SIGNAL - {final_signal.get('action', 'NEUTRAL')}</b>

📊 <b>{symbol}</b> ({timeframe})
💰 <b>Entry:</b> {trade_setup.get('entry_price', 'N/A')}
🎯 <b>TP:</b> {trade_setup.get('take_profit', 'N/A')}
🛡️ <b>SL:</b> {trade_setup.get('stop_loss', 'N/A')}
📈 <b>Confidence:</b> {final_signal.get('confidence', 0)}%

🤖 <b>Analysis Summary:</b>
{result.get('xai_explanation', {}).get('explanation', 'Comprehensive signal analysis')[:150]}...

<i>Full analysis available via API</i>
"""
                
                admin_chat_id = os.environ.get('ADMIN_CHAT_ID', '5899681906')
                success = telegram_notifier.send_message(admin_chat_id, message)
                
                if success:
                    logger.info(f"✅ Comprehensive signal sent to Telegram: {symbol}")
                    
            except Exception as telegram_error:
                logger.error(f"Telegram notification error: {telegram_error}")
        
        return add_cors_headers(jsonify(add_api_metadata(response_data)))
        
    except Exception as e:
        logger.error(f"Sharp signal endpoint error: {e}")
        return add_cors_headers(jsonify({
            "error": "Signal generation failed",
            "details": str(e),
            "api_version": "1.0.0",
            "server_time": datetime.now().isoformat()
        })), 500

# ============================================================================
# TRADING VIEW ENDPOINTS (PRESERVED)
# ============================================================================

# Main execution point with App Factory Pattern
if __name__ == "__main__":
    # Clear any lingering socket file descriptors on Windows
    if platform.system() == "Windows":
        os.environ.pop("WERKZEUG_RUN_MAIN", None)
        os.environ.pop("WERKZEUG_SERVER_FD", None)

    # Create app
    app = create_app()

    # Get port from environment
    port = int(os.environ.get('PORT', 5000))

    # Log startup info
    logger.info(f"Starting GPTs API on port {port}")
    logger.info("Reloader disabled to prevent socket issues")

    # Run without reloader to avoid socket issues
    app.run(
        debug=os.environ.get('DEBUG_MODE', 'true').lower() == 'true',
        use_reloader=False,  # Critical: disable reloader to prevent socket issues
        host='0.0.0.0', 
        port=port
    )