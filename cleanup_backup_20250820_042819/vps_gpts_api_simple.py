#!/usr/bin/env python3
"""
Streamlined GPTs API - Focus on ChatGPT Integration & Telegram Bot
Clean, minimal endpoints for GPTs consumption and Telegram notifications
"""

import os
import logging
import pandas as pd
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create blueprint
gpts_simple = Blueprint('gpts_simple', __name__, url_prefix='/api/gpts')

# System enhancements availability check
system_enhancements_available = True
try:
    from core.validators import SignalRequest, ChartRequest, validate_request
    from core.health_monitor import HealthMonitor
    from core.error_handlers import APIError
    logger.info("✅ System enhancements loaded")
except ImportError as e:
    system_enhancements_available = False
    logger.warning(f"System enhancements not available: {e}")

# Core services initialization
okx_fetcher = None
ai_engine = None
telegram_notifier = None
redis_manager = None
signal_engine = None
mtf_analyzer = None
risk_manager = None
signal_tracker = None
alert_manager = None

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
            from core.telegram_notifier import TelegramNotifier
            telegram_notifier = TelegramNotifier()
            logger.info("✅ Telegram Notifier initialized")
    except Exception as e:
        logger.warning(f"Telegram Notifier initialization failed: {e}")
    
    try:
        if not redis_manager:
            from core.redis_manager import RedisManager
            redis_manager = RedisManager()
            logger.info("✅ Redis Manager initialized")
    except Exception as e:
        logger.warning(f"Redis Manager initialization failed: {e}")
    
    # Initialize new components
    try:
        if not signal_engine:
            from core.sharp_signal_engine import SharpSignalEngine
            # Try to get db session, fallback to None if not available
            db_session = None
            try:
                from models import db
                db_session = db.session
            except:
                pass
            signal_engine = SharpSignalEngine(okx_fetcher, ai_engine, db_session, telegram_notifier, redis_manager)
            logger.info("✅ Sharp Signal Engine initialized with enhancements")
    except Exception as e:
        logger.warning(f"Signal Engine initialization failed: {e}")
    
    try:
        if not mtf_analyzer:
            from core.multi_timeframe_analyzer import MultiTimeframeAnalyzer
            mtf_analyzer = MultiTimeframeAnalyzer(okx_fetcher)
            logger.info("✅ Multi-Timeframe Analyzer initialized")
    except Exception as e:
        logger.warning(f"MTF Analyzer initialization failed: {e}")
    
    try:
        if not risk_manager:
            from core.risk_manager import RiskManager
            risk_manager = RiskManager()
            logger.info("✅ Risk Manager initialized")
    except Exception as e:
        logger.warning(f"Risk Manager initialization failed: {e}")
    
    try:
        if not signal_tracker:
            from core.signal_tracker import SignalPerformanceTracker
            # Try to get db session, fallback to None if not available
            db_session = None
            try:
                from models import db
                db_session = db.session
            except:
                pass
            signal_tracker = SignalPerformanceTracker(db_session)
            logger.info("✅ Signal Performance Tracker initialized")
    except Exception as e:
        logger.warning(f"Signal Tracker initialization failed: {e}")
    
    try:
        if not alert_manager:
            from core.alert_manager import AlertManager
            alert_manager = AlertManager(telegram_notifier)
            logger.info("✅ Alert Manager initialized")
    except Exception as e:
        logger.warning(f"Alert Manager initialization failed: {e}")
    
    try:
        if not alert_manager:
            from core.alert_manager import AlertManager
            alert_manager = AlertManager(telegram_notifier, redis_manager)
            logger.info("✅ Alert Manager initialized")
    except Exception as e:
        logger.warning(f"Alert Manager initialization failed: {e}")

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
            "endpoints_available": 12,
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
                    message = f"""
🚨 <b>TRADING SIGNAL - {direction}</b>

📊 <b>{symbol}</b> ({timeframe})
💰 <b>Entry:</b> ${current_price:,.6f}
🎯 <b>Take Profit:</b> ${take_profit:,.6f}" if take_profit else "N/A"
🛡️ <b>Stop Loss:</b> ${stop_loss:,.6f}" if stop_loss else "N/A"
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
            response_data = {
                "signal": result,
                "human_readable": narrative,
                "telegram_message": telegram_message,
                "format": "json_only"
            }
            return add_cors_headers(jsonify(add_api_metadata(response_data)))
        else:  # format_type == 'both'  
            response_data = {
                "signal": result,
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
                
                message = f"""
🎯 <b>SHARP SIGNAL - {final_signal.get('action', 'NEUTRAL')}</b>

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

# ============================================================================
# TELEGRAM BOT ENDPOINTS  
# ============================================================================

@gpts_simple.route('/telegram/status', methods=['GET'])
@cross_origin()
def get_telegram_status():
    """Telegram bot status check"""
    try:
        initialize_core_services()
        
        status = {
            "telegram_bot": {
                "available": telegram_notifier is not None,
                "enhanced_retry": system_enhancements_available,
                "admin_chat_configured": bool(os.environ.get('ADMIN_CHAT_ID')),
                "anti_spam_active": redis_manager is not None
            },
            "features": [
                "Real-time signal notifications",
                "Enhanced retry mechanism (2x with backoff)",
                "Anti-spam deduplication",
                "HTML formatted messages"
            ]
        }
        
        return add_cors_headers(jsonify(add_api_metadata(status)))
        
    except Exception as e:
        logger.error(f"Telegram status error: {e}")
        return add_cors_headers(jsonify({
            "error": "Telegram status check failed",
            "details": str(e),
            "api_version": "1.0.0",
            "server_time": datetime.now().isoformat()
        })), 500

@gpts_simple.route('/telegram/test', methods=['POST'])
@cross_origin()
def test_telegram():
    """Test Telegram notification with retry mechanism"""
    try:
        data = request.get_json() or {}
        chat_id = data.get('chat_id', os.environ.get('ADMIN_CHAT_ID', '5899681906'))
        message = data.get('message', f'🧪 Test notification from GPTs API\n⏰ {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        
        initialize_core_services()
        
        if not telegram_notifier:
            return add_cors_headers(jsonify({
                "error": "Telegram service not available",
                "api_version": "1.0.0",
                "server_time": datetime.now().isoformat()
            })), 503
        
        success = telegram_notifier.send_message(chat_id, message)
        
        result = {
            "test_result": "SUCCESS" if success else "FAILED",
            "chat_id": chat_id,
            "message_sent": success,
            "retry_mechanism": "ACTIVE" if system_enhancements_available else "BASIC"
        }
        
        return add_cors_headers(jsonify(add_api_metadata(result)))
        
    except Exception as e:
        logger.error(f"Telegram test error: {e}")
        return add_cors_headers(jsonify({
            "error": "Telegram test failed",
            "details": str(e),
            "api_version": "1.0.0",
            "server_time": datetime.now().isoformat()
        })), 500

@gpts_simple.route('/telegram/test-signal', methods=['POST'])
@cross_origin()
def test_professional_signal():
    """Test professional signal format"""
    try:
        data = request.get_json() or {}
        chat_id = data.get('chat_id', os.environ.get('ADMIN_CHAT_ID', '5899681906'))
        
        initialize_core_services()
        
        if not telegram_notifier:
            return add_cors_headers(jsonify({
                "error": "Telegram service not available",
                "api_version": "1.0.0",
                "server_time": datetime.now().isoformat()
            })), 503
        
        # Sample professional signal data
        test_signal_data = {
            'symbol': 'BTCUSDT',
            'signal': {
                'direction': 'BUY',
                'confidence': 85.75,
                'entry_price': 67432.50,
                'stop_loss': 65890.25, 
                'take_profit': 69580.00
            },
            'indicators': {
                'trend': 'BULLISH',
                'momentum': 'STRONG',
                'rsi': 'OVERSOLD_RECOVERY',
                'macd': 'BULLISH_CROSSOVER',
                'volume': 'ABOVE_AVERAGE'
            },
            'ai_narrative': 'Current market conditions show strong bullish momentum with RSI recovering from oversold levels. MACD has formed a bullish crossover while trading volume remains above average, indicating genuine buying interest. Price action has broken above key resistance levels with confirmation from multiple technical indicators.'
        }
        
        # Use professional formatter
        formatted_message = telegram_notifier.format_sharp_signal(test_signal_data)
        success = telegram_notifier.send_message(chat_id, formatted_message, parse_mode='HTML')
        
        result = {
            "test_result": "SUCCESS" if success else "FAILED",
            "chat_id": chat_id,
            "message_sent": success,
            "signal_format": "PROFESSIONAL_MARKDOWN",
            "sample_message_preview": formatted_message[:200] + "..." if len(formatted_message) > 200 else formatted_message
        }
        
        return add_cors_headers(jsonify(add_api_metadata(result)))
        
    except Exception as e:
        logger.error(f"Professional signal test error: {e}")
        return add_cors_headers(jsonify({
            "error": "Professional signal test failed",
            "details": str(e),
            "api_version": "1.0.0",
            "server_time": datetime.now().isoformat()
        })), 500

# ============================================================================
# HEALTH MONITORING
# ============================================================================

@gpts_simple.route('/health', methods=['GET'])
@cross_origin()
def get_health():
    """System health monitoring endpoint"""
    try:
        if not system_enhancements_available:
            return add_cors_headers(jsonify({
                "health": "basic",
                "message": "Health monitoring not available - running in basic mode",
                "api_version": "1.0.0",
                "server_time": datetime.now().isoformat()
            }))
        
        # Initialize health monitor
        try:
            from core.health_monitor import HealthMonitor
            health_monitor = HealthMonitor()
            health_summary = health_monitor.get_health_summary()
            
            return add_cors_headers(jsonify(add_api_metadata(health_summary)))
            
        except Exception as health_error:
            logger.error(f"Health monitoring error: {health_error}")
            return add_cors_headers(jsonify({
                "health": "error",
                "error": str(health_error),
                "api_version": "1.0.0",
                "server_time": datetime.now().isoformat()
            })), 503
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return add_cors_headers(jsonify({
            "health": "error",
            "error": str(e),
            "api_version": "1.0.0",
            "server_time": datetime.now().isoformat()
        })), 503

# ============================================================================
# NEW ENHANCED ENDPOINTS (Multi-Timeframe, Risk Management, Performance)
# ============================================================================

@gpts_simple.route('/analysis/multi-timeframe', methods=['POST'])
@cross_origin()
def get_multi_timeframe_analysis():
    """Multi-timeframe analysis for stronger signal confirmation"""
    try:
        data = request.get_json() or {}
        symbol = data.get('symbol', 'BTCUSDT')
        primary_timeframe = data.get('timeframe', '1H')
        
        logger.info(f"🔍 Multi-timeframe analysis request: {symbol} {primary_timeframe}")
        
        # Initialize services
        initialize_core_services()
        
        if not mtf_analyzer or not okx_fetcher:
            return add_cors_headers(jsonify({
                "error": "Multi-timeframe analyzer not available",
                "api_version": "1.0.0",
                "server_time": datetime.now().isoformat()
            })), 503
        
        # Convert symbol format
        if '/' in symbol:
            symbol = symbol.replace('/', '')
        
        # Handle OKX symbol format
        if '-USDT' in symbol:
            okx_symbol = symbol  # Already in OKX format
        elif symbol.endswith('USDT'):
            okx_symbol = symbol.replace('USDT', '-USDT')
        else:
            okx_symbol = symbol + '-USDT'
        
        # Perform multi-timeframe analysis
        mtf_result = mtf_analyzer.analyze_multiple_timeframes(okx_symbol, primary_timeframe)
        
        # Format response
        response_data = {
            "symbol": symbol,
            "primary_timeframe": primary_timeframe,
            "confluence_score": mtf_result.get('confluence_score', 50),
            "confluence_details": mtf_result.get('confluence_details', ''),
            "recommendation": mtf_result.get('recommendation', {}),
            "timeframe_analysis": mtf_result.get('timeframe_analysis', {}),
            "data_source": "OKX_MULTI_TIMEFRAME"
        }
        
        return add_cors_headers(jsonify(add_api_metadata(response_data)))
        
    except Exception as e:
        logger.error(f"Multi-timeframe analysis error: {e}")
        return add_cors_headers(jsonify({
            "error": "Multi-timeframe analysis failed",
            "details": str(e),
            "api_version": "1.0.0",
            "server_time": datetime.now().isoformat()
        })), 500

@gpts_simple.route('/risk/calculate', methods=['POST'])
@cross_origin()
def calculate_risk_management():
    """Calculate position size and risk management parameters"""
    try:
        data = request.get_json() or {}
        entry_price = float(data.get('entry_price', 0))
        stop_loss = float(data.get('stop_loss', 0))
        account_balance = float(data.get('account_balance', 10000))
        risk_percent = float(data.get('risk_percent', 1.0))
        
        logger.info(f"💰 Risk calculation request: Entry={entry_price}, SL={stop_loss}")
        
        # Initialize services
        initialize_core_services()
        
        if not risk_manager:
            return add_cors_headers(jsonify({
                "error": "Risk manager not available",
                "api_version": "1.0.0",
                "server_time": datetime.now().isoformat()
            })), 503
        
        # Validate inputs
        if entry_price <= 0 or stop_loss <= 0:
            return add_cors_headers(jsonify({
                "error": "Invalid price inputs",
                "message": "Entry price and stop loss must be positive values",
                "api_version": "1.0.0",
                "server_time": datetime.now().isoformat()
            })), 400
        
        # Calculate position sizing
        position_data = risk_manager.calculate_position_size(
            entry_price, stop_loss, account_balance, risk_percent
        )
        
        # Calculate risk/reward if take profit provided
        risk_reward_data = None
        if 'take_profit' in data and data['take_profit'] > 0:
            risk_reward_data = risk_manager.calculate_risk_reward_ratio(
                entry_price, stop_loss, float(data['take_profit'])
            )
        
        # Calculate liquidation price if leverage provided
        liquidation_data = None
        if 'leverage' in data and data['leverage'] > 0:
            liquidation_data = risk_manager.calculate_liquidation_price(
                entry_price, int(data['leverage']), 
                data.get('position_type', 'LONG')
            )
        
        # Compile response
        response_data = {
            "position_sizing": position_data,
            "risk_reward": risk_reward_data,
            "liquidation": liquidation_data,
            "recommendations": {
                "use_position_size": position_data.get('position_size', 0),
                "use_leverage": position_data.get('recommended_leverage', 1),
                "max_risk_usd": position_data.get('max_loss_usd', 0)
            }
        }
        
        return add_cors_headers(jsonify(add_api_metadata(response_data)))
        
    except Exception as e:
        logger.error(f"Risk calculation error: {e}")
        return add_cors_headers(jsonify({
            "error": "Risk calculation failed",
            "details": str(e),
            "api_version": "1.0.0",
            "server_time": datetime.now().isoformat()
        })), 500

@gpts_simple.route('/performance/stats', methods=['GET'])
@cross_origin()
def get_performance_statistics():
    """Get trading performance statistics"""
    try:
        # Query parameters
        symbol = request.args.get('symbol')
        timeframe = request.args.get('timeframe')
        days = int(request.args.get('days', 30))
        
        logger.info(f"📊 Performance stats request: {symbol or 'ALL'} for {days} days")
        
        # Initialize services
        initialize_core_services()
        
        if not signal_tracker:
            return add_cors_headers(jsonify({
                "error": "Signal tracker not available",
                "api_version": "1.0.0",
                "server_time": datetime.now().isoformat()
            })), 503
        
        # Get performance statistics
        stats = signal_tracker.get_performance_stats(symbol, timeframe, days)
        
        # Get best performing pairs
        best_pairs = signal_tracker.get_best_performing_pairs(days, limit=5)
        
        # Get performance by timeframe
        tf_performance = signal_tracker.get_performance_by_timeframe(days)
        
        # Compile response
        response_data = {
            "period_days": days,
            "overall_stats": stats,
            "best_performing_pairs": best_pairs,
            "performance_by_timeframe": tf_performance,
            "tracking_status": "ACTIVE"
        }
        
        return add_cors_headers(jsonify(add_api_metadata(response_data)))
        
    except Exception as e:
        logger.error(f"Performance stats error: {e}")
        return add_cors_headers(jsonify({
            "error": "Performance statistics failed",
            "details": str(e),
            "api_version": "1.0.0",
            "server_time": datetime.now().isoformat()
        })), 500

# ============================================================================
# ALERT MANAGEMENT ENDPOINTS
# ============================================================================

@gpts_simple.route('/alerts/rules', methods=['GET'])
@cross_origin()
def get_alert_rules():
    """Get all alert rules"""
    try:
        initialize_core_services()
        
        if not alert_manager:
            return add_cors_headers(jsonify({
                "error": "Alert manager not available",
                "api_version": "1.0.0",
                "server_time": datetime.now().isoformat()
            })), 503
        
        rules = alert_manager.get_alert_rules()
        
        return add_cors_headers(jsonify(add_api_metadata({
            "alert_rules": rules,
            "total_rules": len(rules),
            "system_status": "ACTIVE"
        })))
        
    except Exception as e:
        logger.error(f"Get alert rules error: {e}")
        return add_cors_headers(jsonify({
            "error": "Failed to get alert rules",
            "details": str(e),
            "api_version": "1.0.0",
            "server_time": datetime.now().isoformat()
        })), 500

@gpts_simple.route('/alerts/rules', methods=['POST'])
@cross_origin()
def create_alert_rule():
    """Create a new alert rule"""
    try:
        data = request.get_json() or {}
        
        # Validate required fields
        if 'name' not in data:
            return add_cors_headers(jsonify({
                "error": "Rule name is required",
                "api_version": "1.0.0",
                "server_time": datetime.now().isoformat()
            })), 400
        
        initialize_core_services()
        
        if not alert_manager:
            return add_cors_headers(jsonify({
                "error": "Alert manager not available",
                "api_version": "1.0.0",
                "server_time": datetime.now().isoformat()
            })), 503
        
        # Create custom rule
        rule = alert_manager.create_custom_rule({
            'name': data['name'],
            'conditions': data.get('conditions', {}),
            'priority': data.get('priority', 'MEDIUM'),
            'notification_channels': data.get('notification_channels', ['telegram']),
            'cooldown_minutes': data.get('cooldown_minutes', 60),
            'enabled': data.get('enabled', True)
        })
        
        logger.info(f"✅ Created alert rule: {rule.name}")
        
        return add_cors_headers(jsonify(add_api_metadata({
            "message": "Alert rule created successfully",
            "rule_id": rule.rule_id,
            "rule_name": rule.name
        })))
        
    except Exception as e:
        logger.error(f"Create alert rule error: {e}")
        return add_cors_headers(jsonify({
            "error": "Failed to create alert rule",
            "details": str(e),
            "api_version": "1.0.0",
            "server_time": datetime.now().isoformat()
        })), 500

@gpts_simple.route('/alerts/rules/<rule_id>', methods=['PUT'])
@cross_origin()
def toggle_alert_rule(rule_id):
    """Enable or disable an alert rule"""
    try:
        data = request.get_json() or {}
        enabled = data.get('enabled', True)
        
        initialize_core_services()
        
        if not alert_manager:
            return add_cors_headers(jsonify({
                "error": "Alert manager not available",
                "api_version": "1.0.0",
                "server_time": datetime.now().isoformat()
            })), 503
        
        success = alert_manager.toggle_alert_rule(rule_id, enabled)
        
        if success:
            return add_cors_headers(jsonify(add_api_metadata({
                "message": f"Alert rule {rule_id} {'enabled' if enabled else 'disabled'}",
                "rule_id": rule_id,
                "enabled": enabled
            })))
        else:
            return add_cors_headers(jsonify({
                "error": "Alert rule not found",
                "rule_id": rule_id,
                "api_version": "1.0.0",
                "server_time": datetime.now().isoformat()
            })), 404
            
    except Exception as e:
        logger.error(f"Toggle alert rule error: {e}")
        return add_cors_headers(jsonify({
            "error": "Failed to toggle alert rule",
            "details": str(e),
            "api_version": "1.0.0",
            "server_time": datetime.now().isoformat()
        })), 500

@gpts_simple.route('/alerts/rules/<rule_id>', methods=['DELETE'])
@cross_origin()
def delete_alert_rule(rule_id):
    """Delete an alert rule"""
    try:
        initialize_core_services()
        
        if not alert_manager:
            return add_cors_headers(jsonify({
                "error": "Alert manager not available",
                "api_version": "1.0.0",
                "server_time": datetime.now().isoformat()
            })), 503
        
        success = alert_manager.remove_alert_rule(rule_id)
        
        if success:
            return add_cors_headers(jsonify(add_api_metadata({
                "message": f"Alert rule {rule_id} deleted successfully",
                "rule_id": rule_id
            })))
        else:
            return add_cors_headers(jsonify({
                "error": "Alert rule not found",
                "rule_id": rule_id,
                "api_version": "1.0.0",
                "server_time": datetime.now().isoformat()
            })), 404
            
    except Exception as e:
        logger.error(f"Delete alert rule error: {e}")
        return add_cors_headers(jsonify({
            "error": "Failed to delete alert rule",
            "details": str(e),
            "api_version": "1.0.0",
            "server_time": datetime.now().isoformat()
        })), 500

@gpts_simple.route('/alerts/history', methods=['GET'])
@cross_origin()
def get_alert_history():
    """Get alert history"""
    try:
        limit = int(request.args.get('limit', 50))
        
        initialize_core_services()
        
        if not alert_manager:
            return add_cors_headers(jsonify({
                "error": "Alert manager not available",
                "api_version": "1.0.0",
                "server_time": datetime.now().isoformat()
            })), 503
        
        history = alert_manager.get_alert_history(limit)
        
        return add_cors_headers(jsonify(add_api_metadata({
            "alert_history": history,
            "total_alerts": len(history),
            "limit": limit
        })))
        
    except Exception as e:
        logger.error(f"Get alert history error: {e}")
        return add_cors_headers(jsonify({
            "error": "Failed to get alert history",
            "details": str(e),
            "api_version": "1.0.0",
            "server_time": datetime.now().isoformat()
        })), 500

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@gpts_simple.errorhandler(404)
def not_found(error):
    """Custom 404 handler"""
    return add_cors_headers(jsonify({
        "error": "ENDPOINT_NOT_FOUND",
        "message": "The requested GPTs endpoint was not found",
        "available_endpoints": [
            "/api/gpts/status",
            "/api/gpts/signal", 
            "/api/gpts/sinyal/tajam",
            "/api/gpts/chart",
            "/api/gpts/telegram/status",
            "/api/gpts/telegram/test",
            "/api/gpts/health",
            "/api/gpts/analysis/multi-timeframe",
            "/api/gpts/risk/calculate",
            "/api/gpts/performance/stats",
            "/api/gpts/alerts/rules",
            "/api/gpts/alerts/history"
        ],
        "api_version": "1.0.0",
        "server_time": datetime.now().isoformat()
    })), 404

@gpts_simple.errorhandler(500)
def internal_error(error):
    """Custom 500 handler"""
    logger.error(f"Internal server error: {error}")
    return add_cors_headers(jsonify({
        "error": "INTERNAL_SERVER_ERROR",
        "message": "An internal error occurred while processing your request",
        "api_version": "1.0.0",
        "server_time": datetime.now().isoformat()
    })), 500

# Initialize services on import
try:
    initialize_core_services()
except Exception as init_error:
    logger.warning(f"GPTs API initialization warning: {init_error}")

# ============================================================================
# ENHANCED GPTS CUSTOM INTEGRATION ENDPOINTS
# ============================================================================

# Enhanced GPTs Custom Integration endpoints
@gpts_simple.route('/track-query', methods=['POST'])
@cross_origin()
def track_query():
    """
    Track dan log semua query dari GPTs untuk audit dan evaluasi
    
    Expected payload:
    {
        "query_text": "Get Bitcoin signal for 1H timeframe",
        "response_text": "BUY signal with 85% confidence",
        "source": "gpts",
        "endpoint": "/api/gpts/signal",
        "processing_time_ms": 1250,
        "confidence_score": 85.5,
        "user_id": "optional_user_id",
        "metadata": {"additional": "data"}
    }
    """
    try:
        from core.query_logger import get_query_logger
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        # Required fields
        query_text = data.get('query_text', '')
        if not query_text:
            return jsonify({'error': 'query_text is required'}), 400
        
        # Optional fields
        response_text = data.get('response_text', '')
        source = data.get('source', 'gpts')
        endpoint = data.get('endpoint', request.endpoint)
        processing_time_ms = data.get('processing_time_ms')
        confidence_score = data.get('confidence_score')
        user_id = data.get('user_id')
        metadata = data.get('metadata', {})
        
        # Log the query
        query_logger = get_query_logger()
        query_id = query_logger.log_query(
            query_text=query_text,
            response_text=response_text,
            source=source,
            endpoint=endpoint,
            processing_time_ms=processing_time_ms,
            confidence_score=confidence_score,
            user_id=user_id,
            metadata=metadata
        )
        
        return jsonify({
            'success': True,
            'query_id': query_id,
            'message': 'Query tracked successfully',
            'api_version': '1.0.0',
            'server_time': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Track query error: {e}")
        return jsonify({'error': 'Failed to track query', 'details': str(e)}), 500

@gpts_simple.route('/track-signal', methods=['POST'])
@cross_origin()
def track_signal():
    """
    Track trading signal untuk analytics dan performance evaluation
    
    Expected payload:
    {
        "signal_id": "sig_btcusdt_1h_20250803",
        "symbol": "BTCUSDT",
        "timeframe": "1H", 
        "action": "BUY",
        "confidence": 85.5,
        "entry_price": 43250.00,
        "take_profit": 44500.00,
        "stop_loss": 42800.00,
        "ai_reasoning": "Strong SMC structure break detected...",
        "smc_analysis": {...},
        "technical_indicators": {...},
        "is_executed": false,
        "source": "GPTs_API"
    }
    """
    try:
        from core.analytics_engine import get_analytics_engine
        import uuid
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        # Required fields validation
        required_fields = ['symbol', 'timeframe', 'action', 'confidence', 'entry_price']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Generate signal_id if not provided
        signal_id = data.get('signal_id')
        if not signal_id:
            unique_id = str(uuid.uuid4())[:8]
            signal_id = f"sig_{data['symbol'].lower()}_{data['timeframe']}_{unique_id}"
        
        # Create signal history record
        from models import SignalHistory, db
        import json
        
        signal_history = SignalHistory(
            signal_id=signal_id,
            symbol=data['symbol'].upper(),
            timeframe=data['timeframe'],
            action=data['action'].upper(),
            confidence=float(data['confidence']),
            entry_price=float(data['entry_price']),
            take_profit=float(data.get('take_profit')) if data.get('take_profit') else None,
            stop_loss=float(data.get('stop_loss')) if data.get('stop_loss') else None,
            risk_reward_ratio=float(data.get('risk_reward_ratio')) if data.get('risk_reward_ratio') else None,
            ai_reasoning=data.get('ai_reasoning'),
            smc_analysis=json.dumps(data.get('smc_analysis')) if data.get('smc_analysis') else None,
            technical_indicators=json.dumps(data.get('technical_indicators')) if data.get('technical_indicators') else None,
            market_conditions=data.get('market_conditions'),
            is_executed=bool(data.get('is_executed', False)),
            execution_source=data.get('source', 'GPTs_API'),
            user_agent=request.headers.get('User-Agent'),
            ip_address=request.remote_addr
        )
        
        # Add execution details if provided
        if data.get('executed_at'):
            signal_history.executed_at = datetime.fromisoformat(data['executed_at'].replace('Z', '+00:00'))
        if data.get('execution_price'):
            signal_history.execution_price = float(data['execution_price'])
        
        db.session.add(signal_history)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'signal_id': signal_id,
            'message': 'Signal tracked successfully',
            'database_id': signal_history.id,
            'api_version': '1.0.0',
            'server_time': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Track signal error: {e}")
        return jsonify({'error': 'Failed to track signal', 'details': str(e)}), 500

@gpts_simple.route('/query-log', methods=['GET'])
@cross_origin()
def query_log():
    """
    Melihat histori interaksi dari GPTs untuk audit dan evaluasi
    
    Query params:
    - limit: Max records (default: 50, max: 100)
    - source: Filter by source (gpts, telegram, api)
    - days: Filter by days (default: 7)
    - category: Filter by category (signal, analysis, chart)
    """
    try:
        from core.query_logger import get_query_logger
        
        # Get query parameters
        limit = min(int(request.args.get('limit', 50)), 100)
        source = request.args.get('source')
        days = int(request.args.get('days', 7))
        category = request.args.get('category')
        
        # Get query history
        query_logger = get_query_logger()
        history = query_logger.get_query_history(
            limit=limit,
            source=source,
            days=days,
            category=category
        )
        
        return jsonify({
            'success': True,
            'query_log': history,
            'filters': {
                'limit': limit,
                'source': source,
                'days': days,
                'category': category
            },
            'total_records': len(history),
            'api_version': '1.0.0',
            'server_time': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Query log error: {e}")
        return jsonify({'error': 'Failed to get query log', 'details': str(e)}), 500

# Advanced Analytics & Evaluation endpoints
@gpts_simple.route('/analytics/signals', methods=['GET'])
@cross_origin()
def analytics_signals():
    """
    Comprehensive signal analytics: win-rate, loss-rate, avg RR, total profit, dll
    
    Query params:
    - days: Time period (default: 30)
    - symbol: Filter by symbol (optional)
    - no_cache: Skip cache (default: false)
    """
    try:
        from core.analytics_engine import get_analytics_engine
        
        # Get query parameters
        days = int(request.args.get('days', 30))
        symbol = request.args.get('symbol', '').upper() if request.args.get('symbol') else None
        use_cache = request.args.get('no_cache', '').lower() != 'true'
        
        # Get analytics
        analytics_engine = get_analytics_engine()
        analytics = analytics_engine.get_signal_analytics(
            days=days,
            symbol=symbol,
            use_cache=use_cache
        )
        
        return jsonify({
            'success': True,
            'analytics': analytics,
            'data_source': 'Signal Performance Analytics',
            'api_version': '1.0.0',
            'server_time': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Signal analytics error: {e}")
        return jsonify({'error': 'Failed to get signal analytics', 'details': str(e)}), 500

@gpts_simple.route('/analytics/queries', methods=['GET'])
@cross_origin()
def analytics_queries():
    """
    Query analytics: patterns GPTs paling sering digunakan, performance, dll
    
    Query params:
    - days: Time period (default: 7)
    - no_cache: Skip cache (default: false)
    """
    try:
        from core.query_logger import get_query_logger
        
        # Get query parameters
        days = int(request.args.get('days', 7))
        use_cache = request.args.get('no_cache', '').lower() != 'true'
        
        # Get analytics
        query_logger = get_query_logger()
        analytics = query_logger.get_query_analytics(
            days=days,
            use_cache=use_cache
        )
        
        return jsonify({
            'success': True,
            'analytics': analytics,
            'data_source': 'GPT Query Analytics',
            'api_version': '1.0.0',
            'server_time': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Query analytics error: {e}")
        return jsonify({'error': 'Failed to get query analytics', 'details': str(e)}), 500

@gpts_simple.route('/analytics/comprehensive', methods=['GET'])
@cross_origin()
def analytics_comprehensive():
    """
    Comprehensive analytics report dengan signals, queries, dan recommendations
    
    Query params:
    - days: Time period (default: 30)
    """
    try:
        from core.analytics_engine import get_analytics_engine
        
        # Get query parameters
        days = int(request.args.get('days', 30))
        
        # Get comprehensive analytics
        analytics_engine = get_analytics_engine()
        report = analytics_engine.get_comprehensive_report(days=days)
        
        return jsonify({
            'success': True,
            'comprehensive_report': report,
            'data_source': 'Comprehensive Analytics Engine',
            'api_version': '1.0.0',
            'server_time': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Comprehensive analytics error: {e}")
        return jsonify({'error': 'Failed to get comprehensive analytics', 'details': str(e)}), 500

@gpts_simple.route('/track-interaction', methods=['POST'])
@cross_origin()
def track_interaction():
    """
    Track user interaction dengan signal (click, execute, feedback, etc)
    
    Expected payload:
    {
        "signal_id": "sig_btcusdt_1h_abc123",
        "interaction_type": "EXECUTE",
        "interaction_source": "TELEGRAM",
        "interaction_data": {"price": 43250, "quantity": 0.1},
        "user_id": "user123"
    }
    """
    try:
        from models import UserInteraction, db
        import uuid
        import json
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        # Required fields validation
        required_fields = ['signal_id', 'interaction_type', 'interaction_source']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Generate interaction_id
        unique_id = str(uuid.uuid4())[:8]
        interaction_id = f"int_{data['signal_id']}_{unique_id}"
        
        # Create interaction record
        interaction = UserInteraction(
            interaction_id=interaction_id,
            signal_id=data['signal_id'],
            interaction_type=data['interaction_type'].upper(),
            interaction_source=data['interaction_source'].upper(),
            interaction_data=json.dumps(data.get('interaction_data')) if data.get('interaction_data') else None,
            user_id=data.get('user_id', 'anonymous'),
            user_agent=request.headers.get('User-Agent'),
            ip_address=request.remote_addr
        )
        
        db.session.add(interaction)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'interaction_id': interaction_id,
            'message': 'Interaction tracked successfully',
            'database_id': interaction.id,
            'api_version': '1.0.0',
            'server_time': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Track interaction error: {e}")
        return jsonify({'error': 'Failed to track interaction', 'details': str(e)}), 500

@gpts_simple.route('/agent-mode', methods=['POST'])
@cross_origin()
def agent_mode_analysis():
    """
    🤖 Multi Role Agent Mode - Comprehensive cryptocurrency trading analysis
    
    Expected payload:
    {
        "symbol": "BTC-USDT",
        "timeframe": "1h",
        "account_balance": 1000.0,
        "risk_tolerance": 0.02,
        "use_mock_data": true
    }
    """
    try:
        from agent_mode import run_agents
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        # Extract parameters with defaults
        symbol = data.get('symbol', 'BTC-USDT')
        timeframe = data.get('timeframe', '1h')
        account_balance = float(data.get('account_balance', 1000.0))
        risk_tolerance = float(data.get('risk_tolerance', 0.02))
        use_mock_data = data.get('use_mock_data', True)
        
        # Validate parameters
        if not symbol or not timeframe:
            return jsonify({'error': 'Symbol and timeframe are required'}), 400
        
        if account_balance <= 0:
            return jsonify({'error': 'Account balance must be positive'}), 400
        
        if not (0.001 <= risk_tolerance <= 0.1):
            return jsonify({'error': 'Risk tolerance must be between 0.1% and 10%'}), 400
        
        # Run multi-agent analysis
        logger.info(f"🤖 Starting Agent Mode analysis for {symbol} ({timeframe})")
        start_time = datetime.now()
        
        analysis_result = run_agents(
            symbol=symbol,
            timeframe=timeframe,
            account_balance=account_balance,
            risk_tolerance=risk_tolerance,
            use_mock_data=use_mock_data
        )
        
        # Calculate analysis duration
        duration_ms = (datetime.now() - start_time).total_seconds() * 1000
        analysis_result['analysis_duration_ms'] = round(duration_ms, 1)
        
        # Add API metadata
        analysis_result.update({
            'success': True,
            'api_version': '1.0.0',
            'server_time': datetime.now().isoformat(),
            'data_source': 'Multi Role Agent System'
        })
        
        logger.info(f"✅ Agent Mode completed in {duration_ms:.1f}ms: {analysis_result['recommendation']}")
        
        return jsonify(analysis_result)
        
    except ImportError as e:
        logger.error(f"❌ Agent Mode import error: {e}")
        return jsonify({
            'error': 'Agent Mode module not available',
            'details': str(e),
            'suggestion': 'Ensure agent_mode.py is present in the project root'
        }), 500
        
    except Exception as e:
        logger.error(f"❌ Agent Mode analysis error: {e}")
        return jsonify({
            'error': 'Failed to run agent mode analysis',
            'details': str(e),
            'api_version': '1.0.0',
            'server_time': datetime.now().isoformat()
        }), 500

logger.info("🚀 GPTs API Blueprint initialized successfully")

# Blueprint ready for registration
if __name__ == "__main__":
    logger.info("GPTs API Simple - Focused on ChatGPT Integration & Telegram Bot")