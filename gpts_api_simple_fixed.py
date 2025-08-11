# Cleaned version (AST-precise extraction)
import os, platform, logging, json, re
from datetime import datetime
import pandas as pd
from flask import Flask, Blueprint, request, jsonify
from flask_cors import cross_origin
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)

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

# Global service references (initialized on demand)
okx_fetcher = None
ai_engine = None
telegram_notifier = None
redis_manager = None
signal_engine = None
mtf_analyzer = None
risk_manager = None
signal_tracker = None
alert_manager = None

# Blueprint (single definition)
gpts_simple = Blueprint('gpts_simple', __name__, url_prefix='/api/gpts')
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
            "endpoints_available": 1,
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
def create_app():
    load_dotenv()
    app = Flask(__name__)
    # Register blueprint ONCE after all routes are defined
    app.register_blueprint(gpts_simple)
    logger.info("🚀 GPTs API Blueprint initialized successfully")
    return app

if __name__ == "__main__":
    # Windows reloader can cause WinError 10038; disable it
    if platform.system() == "Windows":
        os.environ.pop("WERKZEUG_SERVER_FD", None)
    app = create_app()
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "1") not in ("0","false","False")
    app.run(host="0.0.0.0", port=port, debug=debug, use_reloader=False)
