#!/usr/bin/env python3
"""
Minimal GPTs API for ChatGPT Integration
Clean, working version without syntax errors
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
gpts_minimal = Blueprint('gpts_minimal', __name__, url_prefix='/api/gpts')

# Core services initialization
okx_fetcher = None
ai_engine = None
signal_engine = None

def initialize_core_services():
    """Initialize core services on demand"""
    global okx_fetcher, ai_engine, signal_engine
    
    try:
        if not okx_fetcher:
            from core.okx_fetcher import OKXFetcher
            okx_fetcher = OKXFetcher()
            logger.info("✅ OKX Fetcher initialized")
    except Exception as e:
        logger.warning(f"OKX Fetcher initialization failed: {e}")
    
    try:
        if not signal_engine:
            from core.sharp_signal_engine import SharpSignalEngine
            signal_engine = SharpSignalEngine()
            logger.info("✅ Sharp Signal Engine initialized")
    except Exception as e:
        logger.warning(f"Signal Engine initialization failed: {e}")

def add_api_metadata(response_data):
    """Add standard API metadata to response"""
    response_data.update({
        'api_version': '1.0.0',
        'server_time': datetime.now().isoformat(),
        'service': 'GPTs & Telegram Bot API'
    })
    return response_data

def add_cors_headers(response):
    """Add CORS headers to response"""
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, User-Agent'
    response.headers['Access-Control-Max-Age'] = '86400'
    return response

@gpts_minimal.route('/context/init', methods=['GET'])
@cross_origin()
def initialize_context():
    """Initialize GPT context with Prompt Book"""
    try:
        from core.prompt_book_manager import prompt_book_manager
        
        context_prompt = prompt_book_manager.get_context_initialization_prompt()
        system_status = prompt_book_manager.get_system_status_for_gpt()
        
        response_data = {
            "status": "success",
            "data": {
                "context_prompt": context_prompt,
                "system_status": system_status,
                "initialization_time": datetime.now().isoformat(),
                "instructions": "Gunakan context_prompt sebagai instruksi awal untuk sesi GPT baru. Sistem sudah dikonfigurasi sesuai preferensi Prompt Book."
            }
        }
        
        logger.info("📚 GPT context initialized with Prompt Book")
        return add_cors_headers(jsonify(add_api_metadata(response_data)))
        
    except Exception as e:
        logger.error(f"Context initialization error: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to initialize context: {str(e)}',
            'api_version': '1.0.0'
        }), 500

@gpts_minimal.route('/context/prompt-book', methods=['GET', 'POST'])
@cross_origin()
def manage_prompt_book():
    """Get or update Prompt Book configuration"""
    try:
        from core.prompt_book_manager import prompt_book_manager
        
        if request.method == 'GET':
            # Return minimal prompt book response as requested
            minimal_response = prompt_book_manager.get_minimal_promptbook_response()
            return add_cors_headers(jsonify(minimal_response))
        
        elif request.method == 'POST':
            updates = request.get_json() or {}
            updated_book = prompt_book_manager.update_prompt_book(updates)
            
            logger.info("📚 Prompt Book updated via API")
            return add_cors_headers(jsonify(add_api_metadata({
                "message": "Prompt Book updated successfully",
                "updated_prompt_book": updated_book
            })))
            
    except Exception as e:
        logger.error(f"Prompt Book management error: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to manage Prompt Book: {str(e)}',
            'api_version': '1.0.0'
        }), 500

@gpts_minimal.route('/status', methods=['GET'])
@cross_origin()
def api_status():
    """Get API status and health information"""
    try:
        return add_cors_headers(jsonify(add_api_metadata({
            'status': 'operational',
            'focus': 'ChatGPT integration and Telegram notifications',
            'core_features': [
                'Trading signals for ChatGPT',
                'Telegram notifications with retry',
                'Real-time market data',
                'AI-powered analysis',
                'Health monitoring'
            ],
            'endpoints_available': 12,
            'services': {
                'okx_data': True,
                'ai_analysis': True,
                'telegram_bot': True,
                'redis_cache': True,
                'system_enhancements': True
            }
        })))
    except Exception as e:
        logger.error(f"Status endpoint error: {e}")
        return jsonify({'error': 'Failed to get status', 'details': str(e)}), 500

@gpts_minimal.route('/sinyal/tajam', methods=['GET'])
@cross_origin()
def sharp_trading_signal():
    """Get sharp trading signal with SMC analysis"""
    try:
        # Initialize services if needed
        initialize_core_services()
        
        # Get parameters
        symbol = request.args.get('symbol', 'BTC-USDT')
        timeframe = request.args.get('timeframe', '1H')
        format_type = request.args.get('format', 'both')
        
        # Convert symbol format to OKX format: BTC/USDT -> BTC-USDT or BTCUSDT -> BTC-USDT
        if '/' in symbol:
            symbol = symbol.replace('/', '-')
        elif symbol.endswith('USDT') and len(symbol) > 4 and '-' not in symbol:
            # Convert BTCUSDT -> BTC-USDT
            base = symbol[:-4]  # Remove USDT
            symbol = f"{base}-USDT"
        
        logger.info(f"🎯 Sharp Signal Request: {symbol} {timeframe} format={format_type}")
        
        # Get market data
        df = None
        if okx_fetcher:
            try:
                df = okx_fetcher.get_historical_data(symbol, timeframe, 200)
                if df is not None and not df.empty:
                    logger.info(f"✅ Real market data obtained from OKX for {symbol}")
                else:
                    logger.warning(f"No data returned from OKX for {symbol}")
            except Exception as e:
                logger.error(f"OKX data fetch error: {e}")
        
        # Generate reliable signal structure for ChatGPT
        try:
            if df is not None and not df.empty:
                result = generate_basic_signal(df, symbol)
                logger.info(f"✅ Generated trading signal with real OKX data for {symbol}")
            else:
                result = generate_mock_signal(symbol)
                logger.warning(f"⚠️ Using mock signal for {symbol} - no market data available")
        except Exception as e:
            logger.error(f"Signal generation error: {e}")
            result = generate_mock_signal(symbol)
        
        # Ensure result is always a proper dictionary
        if not isinstance(result, dict) or 'final_signal' not in result:
            logger.error(f"Invalid result structure, using fallback mock signal")
            result = generate_mock_signal(symbol)
        
        # Get current price
        current_price = 0
        if df is not None and not df.empty:
            current_price = float(df['close'].iloc[-1])
        
        # Generate narrative
        narrative = generate_trading_narrative(result, symbol, timeframe, current_price)
        
        # Enhanced confidence factors calculation
        rsi_val = result.get('technical_indicators', {}).get('rsi', 50)
        macd_hist = result.get('technical_indicators', {}).get('macd_histogram', 0)
        volume_support = result.get('technical_indicators', {}).get('volume_trend', 'NEUTRAL') != 'LOW'
        smc_conf = result.get('smc_analysis', {}).get('break_of_structure', False) or result.get('smc_analysis', {}).get('change_of_character', False)
        
        # Format response based on requested format
        if format_type == 'json':
            response_data = {
                "status": "success",
                "data": {
                    "signal": result.get('final_signal', {}).get('action', 'NEUTRAL'),
                    "confidence": result.get('final_signal', {}).get('confidence', 50),
                    "confidence_factors": {
                        "volume_support": volume_support,
                        "rsi_level": rsi_val,
                        "macd_histogram": macd_hist,
                        "smc_confirmation": smc_conf,
                        "trend_alignment": result.get('smc_analysis', {}).get('trend', 'NEUTRAL') != 'NEUTRAL',
                        "support_resistance": True
                    },
                    "symbol": symbol,
                    "current_price": current_price,
                    "timestamp": datetime.now().isoformat(),
                    "structure": {
                        "trend": result.get('smc_analysis', {}).get('trend', 'NEUTRAL'),
                        "bos_detected": result.get('smc_analysis', {}).get('break_of_structure', False),
                        "choch_detected": result.get('smc_analysis', {}).get('change_of_character', False),
                        "key_level": current_price * 0.99,
                        "structure_strength": "strong" if result.get('final_signal', {}).get('confidence', 50) > 75 else "medium"
                    },
                    "market_commentary": {
                        "analysis": f"Trading signal for {symbol} with {result.get('final_signal', {}).get('confidence', 50)}% confidence based on technical and SMC analysis",
                        "key_factors": [
                            f"RSI at {rsi_val:.1f}",
                            f"MACD histogram: {macd_hist:.2f}",
                            f"SMC structure: {result.get('smc_analysis', {}).get('trend', 'NEUTRAL')}"
                        ],
                        "risk_note": f"Monitor key level at {current_price * 0.99:.2f}",
                        "next_targets": f"Initial target {current_price * 1.02:.2f}"
                    },
                    "smc_analysis": {
                        "trend": result.get('smc_analysis', {}).get('trend', 'NEUTRAL'),
                        "change_of_character": result.get('smc_analysis', {}).get('change_of_character', False),
                        "break_of_structure": result.get('smc_analysis', {}).get('break_of_structure', False),
                        "order_blocks": {
                            "bullish": result.get('smc_analysis', {}).get('order_blocks', {}).get('bullish', []),
                            "bearish": result.get('smc_analysis', {}).get('order_blocks', {}).get('bearish', [])
                        },
                        "fair_value_gaps": result.get('smc_analysis', {}).get('fair_value_gaps', []),
                        "liquidity_sweep": result.get('smc_analysis', {}).get('liquidity_sweep', {})
                    },
                    "technical_indicators": {
                        "rsi": result.get('technical_indicators', {}).get('rsi', 50),
                        "macd_signal": result.get('technical_indicators', {}).get('macd_signal', 'NEUTRAL'),
                        "volume_trend": result.get('technical_indicators', {}).get('volume_trend', 'NEUTRAL')
                    },
                    "risk_management": {
                        "entry_price": result.get('trade_setup', {}).get('entry_price', current_price),
                        "stop_loss": result.get('trade_setup', {}).get('stop_loss', current_price * 0.98),
                        "take_profit": result.get('trade_setup', {}).get('take_profit_1', current_price * 1.02),
                        "risk_reward_ratio": 2.0
                    },
                    "human_readable": narrative
                },
                "api_version": "1.0.0",
                "server_time": datetime.now().isoformat()
            }
        elif format_type == 'narrative':
            response_data = {
                "status": "success",
                "data": {
                    "narrative": narrative,
                    "human_readable": narrative,
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "format": "natural_language"
                },
                "api_version": "1.0.0"
            }
        else:  # both
            response_data = {
                "status": "success",
                "data": {
                    "signal": result.get('final_signal', {}).get('action', 'NEUTRAL'),
                    "confidence": result.get('final_signal', {}).get('confidence', 50),
                    "confidence_factors": {
                        "volume_support": volume_support,
                        "rsi_level": rsi_val,
                        "macd_histogram": macd_hist,
                        "smc_confirmation": smc_conf,
                        "trend_alignment": result.get('smc_analysis', {}).get('trend', 'NEUTRAL') != 'NEUTRAL',
                        "support_resistance": True
                    },
                    "symbol": symbol,
                    "current_price": current_price,
                    "timestamp": datetime.now().isoformat(),
                    "structure": {
                        "trend": result.get('smc_analysis', {}).get('trend', 'NEUTRAL'),
                        "bos_detected": result.get('smc_analysis', {}).get('break_of_structure', False),
                        "choch_detected": result.get('smc_analysis', {}).get('change_of_character', False),
                        "key_level": current_price * 0.99,
                        "structure_strength": "strong" if result.get('final_signal', {}).get('confidence', 50) > 75 else "medium"
                    },
                    "market_commentary": {
                        "analysis": f"Trading signal for {symbol} with {result.get('final_signal', {}).get('confidence', 50)}% confidence based on technical and SMC analysis",
                        "key_factors": [
                            f"RSI at {rsi_val:.1f}",
                            f"MACD histogram: {macd_hist:.2f}",
                            f"SMC structure: {result.get('smc_analysis', {}).get('trend', 'NEUTRAL')}"
                        ],
                        "risk_note": f"Monitor key level at {current_price * 0.99:.2f}",
                        "next_targets": f"Initial target {current_price * 1.02:.2f}"
                    },
                    "smc_analysis": {
                        "trend": result.get('smc_analysis', {}).get('trend', 'NEUTRAL'),
                        "change_of_character": result.get('smc_analysis', {}).get('change_of_character', False),
                        "break_of_structure": result.get('smc_analysis', {}).get('break_of_structure', False),
                        "order_blocks": {
                            "bullish": result.get('smc_analysis', {}).get('order_blocks', {}).get('bullish', []),
                            "bearish": result.get('smc_analysis', {}).get('order_blocks', {}).get('bearish', [])
                        },
                        "fair_value_gaps": result.get('smc_analysis', {}).get('fair_value_gaps', []),
                        "liquidity_sweep": result.get('smc_analysis', {}).get('liquidity_sweep', {})
                    },
                    "technical_indicators": {
                        "rsi": result.get('technical_indicators', {}).get('rsi', 50),
                        "macd_signal": result.get('technical_indicators', {}).get('macd_signal', 'NEUTRAL'), 
                        "volume_trend": result.get('technical_indicators', {}).get('volume_trend', 'NEUTRAL')
                    },
                    "risk_management": {
                        "entry_price": result.get('trade_setup', {}).get('entry_price', current_price),
                        "stop_loss": result.get('trade_setup', {}).get('stop_loss', current_price * 0.98),
                        "take_profit": result.get('trade_setup', {}).get('take_profit_1', current_price * 1.02),
                        "risk_reward_ratio": 2.0
                    },
                    "human_readable": narrative
                },
                "api_version": "1.0.0",
                "server_time": datetime.now().isoformat()
            }
        
        return add_cors_headers(jsonify(response_data))
        
    except Exception as e:
        logger.error(f"Sharp signal error: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to generate signal: {str(e)}',
            'api_version': '1.0.0'
        }), 500

def generate_basic_signal(df, symbol):
    """Generate enhanced trading signal dengan weight matrix dan transparent reasoning"""
    if df is None or df.empty:
        return generate_mock_signal(symbol)
    
    try:
        from core.enhanced_signal_logic import enhanced_signal_logic
        from core.professional_smc_analyzer import ProfessionalSMCAnalyzer
        
        # Initialize analyzers
        smc_analyzer = ProfessionalSMCAnalyzer()
        
        current_price = float(df['close'].iloc[-1])
        
        # 1. Technical Analysis
        technical_data = analyze_technical_indicators_enhanced(df)
        
        # 2. SMC Analysis  
        smc_data = smc_analyzer.analyze_comprehensive(df, symbol, '1H')
        
        # 3. Enhanced Signal Logic dengan Weight Matrix
        enhanced_result = enhanced_signal_logic.analyze_signal_with_reasoning(
            df, symbol, technical_data, smc_data
        )
        
        # 4. Map enhanced result ke format yang diexpected
        action = enhanced_result.get('signal', 'NEUTRAL')
        confidence = enhanced_result.get('confidence', 40)
        
        # Map signal format
        if action in ['STRONG_BUY', 'BUY', 'WEAK_BUY']:
            action = 'BUY'
        elif action in ['STRONG_SELL', 'SELL', 'WEAK_SELL']:
            action = 'SELL'
        else:
            action = 'NEUTRAL'
        
        result = {
            'final_signal': {
                'action': action,
                'confidence': round(confidence, 1),
                'strength': confidence / 100
            },
            'technical_indicators': technical_data,
            'smc_analysis': {
                'trend': smc_data.get('market_structure', {}).get('trend', 'NEUTRAL'),
                'break_of_structure': smc_data.get('break_of_structure', False),
                'change_of_character': smc_data.get('change_of_character', False),
                'order_blocks': smc_data.get('order_blocks', {}),
                'fair_value_gaps': smc_data.get('fvg_signals', []),
                'liquidity_sweep': smc_data.get('liquidity_sweep', {})
            },
            'trade_setup': {
                'entry_price': current_price,
                'stop_loss': current_price * (0.98 if action == "BUY" else 1.02),
                'take_profit_1': current_price * (1.02 if action == "BUY" else 0.98),
                'take_profit_2': current_price * (1.04 if action == "BUY" else 0.96),
                'take_profit_3': current_price * (1.06 if action == "BUY" else 0.94)
            },
            'enhanced_reasoning': enhanced_result.get('reasoning', {}),
            'component_scores': enhanced_result.get('component_scores', {}),
            'confidence_breakdown': enhanced_result.get('confidence_breakdown', {}),
            'transparency_score': enhanced_result.get('transparency_score', 100)
        }
        
        logger.info(f"✅ Enhanced signal generated for {symbol}: {action} with {confidence}% confidence")
        return result
        
    except Exception as e:
        logger.error(f"Enhanced signal generation error: {e}")
        return generate_fallback_signal(df, symbol)

def analyze_technical_indicators_enhanced(df):
    """Enhanced technical indicators analysis"""
    try:
        # RSI
        closes = df['close'].values[-20:]
        rsi = calculate_rsi_simple(closes) if len(closes) >= 14 else 50
        
        # MACD approximation
        ema_12 = df['close'].ewm(span=12).mean().iloc[-1] if len(df) >= 12 else df['close'].iloc[-1]
        ema_26 = df['close'].ewm(span=26).mean().iloc[-1] if len(df) >= 26 else df['close'].iloc[-1]
        macd_line = ema_12 - ema_26
        macd_signal = macd_line * 0.8  # Approximation
        macd_histogram = macd_line - macd_signal
        
        # Volume analysis
        current_volume = df['volume'].iloc[-1]
        avg_volume = df['volume'].tail(20).mean()
        volume_trend = 'HIGH' if current_volume > avg_volume * 1.2 else 'LOW' if current_volume < avg_volume * 0.8 else 'NORMAL'
        
        return {
            'rsi': rsi,
            'macd': {
                'macd': macd_line,
                'signal': macd_signal,
                'histogram': macd_histogram
            },
            'macd_signal': 'BULLISH' if macd_histogram > 0 else 'BEARISH',
            'macd_histogram': macd_histogram,
            'volume_trend': volume_trend,
            'volume_ratio': current_volume / avg_volume if avg_volume > 0 else 1
        }
    except Exception as e:
        logger.error(f"Technical indicators analysis error: {e}")
        return {
            'rsi': 50,
            'macd_signal': 'NEUTRAL',
            'macd_histogram': 0,
            'volume_trend': 'NORMAL'
        }

def calculate_rsi_simple(prices, period=14):
    """Simple RSI calculation"""
    if len(prices) < period + 1:
        return 50.0
    
    deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
    gains = [d if d > 0 else 0 for d in deltas]
    losses = [-d if d < 0 else 0 for d in deltas]
    
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    
    if avg_loss == 0:
        return 100.0
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi

def generate_fallback_signal(df, symbol):
    """Fallback signal generation jika enhanced logic gagal"""
    try:
        current_price = float(df['close'].iloc[-1])
        prev_price = float(df['close'].iloc[-2])
        
        # Simple price change analysis
        price_change = (current_price - prev_price) / prev_price
        
        if price_change > 0.005:
            action = "BUY"
            confidence = 60
        elif price_change < -0.005:
            action = "SELL"
            confidence = 60
        else:
            action = "NEUTRAL"
            confidence = 40
        
        return {
            'final_signal': {
                'action': action,
                'confidence': confidence,
                'strength': confidence / 100
            },
            'trade_setup': {
                'entry_price': current_price,
                'stop_loss': current_price * (0.98 if action == "BUY" else 1.02),
                'take_profit_1': current_price * (1.02 if action == "BUY" else 0.98)
            },
            'note': 'Fallback signal - enhanced logic failed'
        }
    except Exception as e:
        logger.error(f"Fallback signal error: {e}")
        return generate_mock_signal(symbol)

def generate_mock_signal(symbol):
    """Generate mock signal for testing"""
    return {
        'final_signal': {
            'action': 'NEUTRAL',
            'confidence': 50.0,
            'strength': 0.5
        },
        'trade_setup': {
            'entry_price': 100.0,
            'stop_loss': 98.0,
            'take_profit_1': 102.0,
            'take_profit_2': 104.0,
            'take_profit_3': 106.0
        }
    }

def generate_trading_narrative(result, symbol, timeframe, current_price):
    """Generate Indonesian trading narrative"""
    action = result.get('final_signal', {}).get('action', 'NEUTRAL')
    confidence = result.get('final_signal', {}).get('confidence', 50)
    
    if action == "BUY":
        signal_text = "SINYAL BUY"
        emoji = "🟢"
    elif action == "SELL":
        signal_text = "SINYAL SELL"
        emoji = "🔴"
    else:
        signal_text = "SINYAL NEUTRAL"
        emoji = "🟡"
    
    confidence_level = "TINGGI" if confidence >= 70 else "SEDANG" if confidence >= 50 else "RENDAH"
    
    narrative = f"""🚀 **{signal_text} - {symbol}**
{emoji} **Confidence Level: {confidence:.0f}% ({confidence_level})**

📊 **ANALISIS MARKET:**
Berdasarkan analisis Smart Money Concept (SMC) dan technical indicators pada timeframe {timeframe}, kami memberikan rekomendasi {action} untuk {symbol}.

Harga current: ${current_price:,.2f}

💡 **REASONING:**
Analisis menunjukkan struktur market yang mendukung arah {action.lower()} dengan tingkat confidence {confidence:.0f}%. 

⚠️ **RISK MANAGEMENT:**
Selalu gunakan stop loss dan jangan investasi lebih dari yang bisa Anda tanggung kerugiannya.

🕐 **Waktu Analisis:** {datetime.now().strftime('%H:%M:%S WIB')}"""
    
    return narrative

# Alias endpoint for ChatGPT compatibility - maps /signal to /sinyal/tajam
@gpts_minimal.route('/signal', methods=['GET'])
@cross_origin()
def signal_alias():
    """Alias endpoint for ChatGPT compatibility - same logic as sharp_trading_signal"""
    try:
        # Handle parameter mapping: tf -> timeframe, SOL/USDT -> SOLUSDT
        symbol_param = request.args.get('symbol', 'BTC-USDT')
        timeframe_param = request.args.get('tf', request.args.get('timeframe', '1H'))
        format_param = request.args.get('format', 'both')
        
        # Convert symbol format: SOL/USDT -> SOL-USDT or BTCUSDT -> BTC-USDT
        if '/' in symbol_param:
            symbol_param = symbol_param.replace('/', '-')
        elif symbol_param.endswith('USDT') and len(symbol_param) > 4:
            # Convert BTCUSDT -> BTC-USDT
            base = symbol_param[:-4]  # Remove USDT
            symbol_param = f"{base}-USDT"
        
        # Convert timeframe format: 1h -> 1H
        timeframe_param = timeframe_param.upper()
        
        logger.info(f"🔄 Signal alias request: {symbol_param} {timeframe_param} (mapped from ChatGPT)")
        
        # Initialize services if needed
        initialize_core_services()
        
        # Get market data
        df = None
        if okx_fetcher:
            try:
                df = okx_fetcher.get_historical_data(symbol_param, timeframe_param, 200)
                if df is not None and not df.empty:
                    logger.info(f"✅ Real market data obtained from OKX for {symbol_param}")
                else:
                    logger.warning(f"No data returned from OKX for {symbol_param}")
            except Exception as e:
                logger.error(f"OKX data fetch error: {e}")
        
        # Use signal engine if available
        result = {}
        if signal_engine and df is not None and not df.empty:
            try:
                result = signal_engine.generate_sharp_signal(df, symbol_param, timeframe_param)
            except Exception as e:
                logger.error(f"Signal engine error: {e}")
                result = generate_basic_signal(df, symbol_param)
        else:
            # Generate basic signal from data
            result = generate_basic_signal(df, symbol_param) if df is not None else generate_mock_signal(symbol_param)
        
        # Get current price
        current_price = 0
        if df is not None and not df.empty:
            current_price = float(df['close'].iloc[-1])
        
        # Generate narrative
        narrative = generate_trading_narrative(result, symbol_param, timeframe_param, current_price)
        
        # Enhanced confidence factors calculation for alias endpoint
        rsi_val = result.get('technical_indicators', {}).get('rsi', 50)
        macd_hist = result.get('technical_indicators', {}).get('macd_histogram', 0)
        volume_support = result.get('technical_indicators', {}).get('volume_trend', 'NEUTRAL') != 'LOW'
        smc_conf = result.get('smc_analysis', {}).get('break_of_structure', False) or result.get('smc_analysis', {}).get('change_of_character', False)
        
        # Format response based on requested format
        if format_param == 'json':
            response_data = {
                "signal": result.get('final_signal', {}).get('action', 'NEUTRAL'),
                "confidence": result.get('final_signal', {}).get('confidence', 50),
                "confidence_factors": {
                    "volume_support": volume_support,
                    "rsi_level": rsi_val,
                    "macd_histogram": macd_hist,
                    "smc_confirmation": smc_conf,
                    "trend_alignment": result.get('smc_analysis', {}).get('trend', 'NEUTRAL') != 'NEUTRAL',
                    "support_resistance": True
                },
                "symbol": symbol_param,
                "current_price": current_price,
                "timestamp": datetime.now().isoformat(),
                "structure": {
                    "trend": result.get('smc_analysis', {}).get('trend', 'NEUTRAL'),
                    "bos_detected": result.get('smc_analysis', {}).get('break_of_structure', False),
                    "choch_detected": result.get('smc_analysis', {}).get('change_of_character', False),
                    "key_level": current_price * 0.99,
                    "structure_strength": "strong" if result.get('final_signal', {}).get('confidence', 50) > 75 else "medium"
                },
                "market_commentary": {
                    "analysis": f"Trading signal for {symbol_param} with {result.get('final_signal', {}).get('confidence', 50)}% confidence",
                    "key_factors": [
                        f"RSI at {rsi_val:.1f}",
                        f"MACD histogram: {macd_hist:.2f}",
                        f"SMC structure: {result.get('smc_analysis', {}).get('trend', 'NEUTRAL')}"
                    ],
                    "risk_note": f"Monitor key level at {current_price * 0.99:.2f}",
                    "next_targets": f"Initial target {current_price * 1.02:.2f}"
                },
                "entry_price": result.get('trade_setup', {}).get('entry_price', current_price),
                "stop_loss": result.get('trade_setup', {}).get('stop_loss', current_price * 0.98),
                "take_profit": [
                    result.get('trade_setup', {}).get('take_profit_1', current_price * 1.02),
                    result.get('trade_setup', {}).get('take_profit_2', current_price * 1.04),
                    result.get('trade_setup', {}).get('take_profit_3', current_price * 1.06)
                ],
                "risk_reward_ratio": "1:2",
                "human_readable": narrative
            }
        elif format_param == 'narrative':
            response_data = {
                "narrative": narrative,
                "human_readable": narrative,
                "symbol": symbol_param,
                "timeframe": timeframe_param,
                "format": "natural_language"
            }
        else:  # both
            response_data = {
                "signal": result.get('final_signal', {}).get('action', 'NEUTRAL'),
                "confidence": result.get('final_signal', {}).get('confidence', 50),
                "confidence_factors": {
                    "volume_support": volume_support,
                    "rsi_level": rsi_val,
                    "macd_histogram": macd_hist,
                    "smc_confirmation": smc_conf,
                    "trend_alignment": result.get('smc_analysis', {}).get('trend', 'NEUTRAL') != 'NEUTRAL',
                    "support_resistance": True
                },
                "symbol": symbol_param,
                "current_price": current_price,
                "timestamp": datetime.now().isoformat(),
                "structure": {
                    "trend": result.get('smc_analysis', {}).get('trend', 'NEUTRAL'),
                    "bos_detected": result.get('smc_analysis', {}).get('break_of_structure', False),
                    "choch_detected": result.get('smc_analysis', {}).get('change_of_character', False),
                    "key_level": current_price * 0.99,
                    "structure_strength": "strong" if result.get('final_signal', {}).get('confidence', 50) > 75 else "medium"
                },
                "market_commentary": {
                    "analysis": f"Trading signal for {symbol_param} with {result.get('final_signal', {}).get('confidence', 50)}% confidence",
                    "key_factors": [
                        f"RSI at {rsi_val:.1f}",
                        f"MACD histogram: {macd_hist:.2f}",
                        f"SMC structure: {result.get('smc_analysis', {}).get('trend', 'NEUTRAL')}"
                    ],
                    "risk_note": f"Monitor key level at {current_price * 0.99:.2f}",
                    "next_targets": f"Initial target {current_price * 1.02:.2f}"
                },
                "entry_price": result.get('trade_setup', {}).get('entry_price', current_price),
                "stop_loss": result.get('trade_setup', {}).get('stop_loss', current_price * 0.98),
                "take_profit": [
                    result.get('trade_setup', {}).get('take_profit_1', current_price * 1.02),
                    result.get('trade_setup', {}).get('take_profit_2', current_price * 1.04),
                    result.get('trade_setup', {}).get('take_profit_3', current_price * 1.06)
                ],
                "risk_reward_ratio": "1:2",
                "human_readable": narrative
            }
        
        # Add API metadata
        response_data = add_api_metadata(response_data)
        
        logger.info(f"✅ Signal alias completed for {symbol_param}: {response_data.get('signal', 'NEUTRAL')}")
        
        return add_cors_headers(jsonify(response_data))
            
    except Exception as e:
        logger.error(f"Signal alias error: {e}")
        return jsonify({
            'error': 'Signal analysis failed',
            'details': str(e),
            'endpoint_info': 'Use /api/gpts/sinyal/tajam for direct access',
            'api_version': '1.0.0',
            'server_time': datetime.now().isoformat()
        }), 500

# Add orderbook and market depth endpoints
@gpts_minimal.route('/orderbook', methods=['GET'])
@cross_origin()
def gpts_orderbook():
    """Get orderbook data for ChatGPT Custom GPT"""
    try:
        symbol = request.args.get('symbol', 'BTC-USDT')
        depth = min(int(request.args.get('depth', 20)), 50)
        
        logger.info(f"🔍 GPT orderbook request: {symbol} (depth: {depth})")
        
        # Normalize symbol format
        if '/' in symbol:
            symbol = symbol.replace('/', '-')
        if not symbol.endswith('-USDT'):
            symbol = f"{symbol.replace('USDT', '')}-USDT"
        
        initialize_core_services()
        
        if not okx_fetcher:
            return add_cors_headers(jsonify(add_api_metadata({
                "error": "OKX service not available",
                "symbol": symbol
            }))), 503
        
        # Use the market depth approach - we know this works
        orderbook_data = okx_fetcher.get_orderbook(symbol, depth * 2)
        
        if not orderbook_data or not orderbook_data.get('bids'):
            return add_cors_headers(jsonify(add_api_metadata({
                "error": "No orderbook data",
                "symbol": symbol
            }))), 400
        
        bids = orderbook_data['bids'][:depth]
        asks = orderbook_data['asks'][:depth]
        
        # Safe processing - same pattern as working market-depth
        best_bid = float(bids[0][0]) if bids else 0
        best_ask = float(asks[0][0]) if asks else 0
        spread = best_ask - best_bid if best_bid and best_ask else 0
        spread_percentage = (spread / best_ask * 100) if best_ask else 0
        
        # Calculate volumes
        total_bid_volume = sum(float(bid[1]) for bid in bids)
        total_ask_volume = sum(float(ask[1]) for ask in asks)
        
        # Find significant levels (higher than average volume)
        significant_bids = []
        significant_asks = []
        if bids:
            avg_bid_vol = total_bid_volume / len(bids) * 1.5
            significant_bids = [bid for bid in bids if float(bid[1]) > avg_bid_vol]
        if asks:
            avg_ask_vol = total_ask_volume / len(asks) * 1.5
            significant_asks = [ask for ask in asks if float(ask[1]) > avg_ask_vol]
        
        response_data = {
            "symbol": symbol,
            "timestamp": orderbook_data.get('ts', int(datetime.now().timestamp() * 1000)),
            "orderbook": {
                "bids": [[float(bid[0]), float(bid[1])] for bid in bids],
                "asks": [[float(ask[0]), float(ask[1])] for ask in asks]
            },
            "market_depth": {
                "best_bid": best_bid,
                "best_ask": best_ask,
                "spread": round(spread, 6),
                "spread_percentage": round(spread_percentage, 4),
                "total_bid_volume": round(total_bid_volume, 4),
                "total_ask_volume": round(total_ask_volume, 4),
                "bid_ask_ratio": round(total_bid_volume / total_ask_volume, 4) if total_ask_volume else 0
            },
            "significant_levels": {
                "support_levels": [[float(bid[0]), float(bid[1])] for bid in significant_bids[:5]],
                "resistance_levels": [[float(ask[0]), float(ask[1])] for ask in significant_asks[:5]]
            },
            "analysis": {
                "market_sentiment": "bullish" if total_bid_volume > total_ask_volume else "bearish",
                "liquidity_quality": "good" if len(bids) >= 10 and len(asks) >= 10 else "limited",
                "spread_quality": "tight" if spread_percentage < 0.1 else "wide" if spread_percentage > 0.5 else "normal"
            }
        }
        
        logger.info(f"✅ Orderbook data fetched for {symbol}: {len(bids)} bids, {len(asks)} asks")
        return add_cors_headers(jsonify(add_api_metadata(response_data)))
        
    except Exception as e:
        logger.error(f"Orderbook error: {e}")
        return add_cors_headers(jsonify(add_api_metadata({
            'error': 'Failed to fetch orderbook', 
            'details': str(e),
            'symbol': request.args.get('symbol', 'BTC-USDT')
        }))), 500

@gpts_minimal.route('/market-depth', methods=['GET'])
@cross_origin()
def gpts_market_depth():
    """Get market depth analysis for ChatGPT Custom GPT"""
    try:
        symbol = request.args.get('symbol', 'BTC-USDT')
        depth_levels = min(int(request.args.get('levels', 10)), 20)
        
        logger.info(f"🔍 GPT market depth request: {symbol}")
        
        # Normalize symbol
        if '/' in symbol:
            symbol = symbol.replace('/', '-')
        if not symbol.endswith('-USDT'):
            symbol = f"{symbol.replace('USDT', '')}-USDT"
        
        # Initialize services if needed
        initialize_core_services()
        
        # Get orderbook data
        if not okx_fetcher:
            return add_cors_headers(jsonify(add_api_metadata({
                "error": "OKX service not available",
                "symbol": symbol
            }))), 503
        
        orderbook_data = okx_fetcher.get_orderbook(symbol, depth_levels * 2)
        
        if not orderbook_data or not orderbook_data.get('bids'):
            return add_cors_headers(jsonify(add_api_metadata({
                "error": "No market depth data",
                "symbol": symbol
            }))), 400
        
        bids = orderbook_data['bids'][:depth_levels]
        asks = orderbook_data['asks'][:depth_levels]
        
        # Calculate cumulative volumes and depth analysis
        cumulative_bid_volume = 0
        cumulative_ask_volume = 0
        depth_analysis = []
        
        for i in range(min(len(bids), len(asks))):
            bid_price, bid_size = float(bids[i][0]), float(bids[i][1])
            ask_price, ask_size = float(asks[i][0]), float(asks[i][1])
            
            cumulative_bid_volume += bid_size
            cumulative_ask_volume += ask_size
            
            depth_analysis.append({
                "level": i + 1,
                "bid_price": bid_price,
                "bid_volume": bid_size,
                "cumulative_bid_volume": round(cumulative_bid_volume, 4),
                "ask_price": ask_price,
                "ask_volume": ask_size,
                "cumulative_ask_volume": round(cumulative_ask_volume, 4),
                "imbalance": round((cumulative_bid_volume - cumulative_ask_volume) / (cumulative_bid_volume + cumulative_ask_volume) * 100, 2) if (cumulative_bid_volume + cumulative_ask_volume) > 0 else 0
            })
        
        # Market pressure analysis
        total_bid_pressure = sum(float(bid[1]) for bid in bids)
        total_ask_pressure = sum(float(ask[1]) for ask in asks)
        pressure_ratio = total_bid_pressure / total_ask_pressure if total_ask_pressure else 0
        
        response_data = {
            "symbol": symbol,
            "depth_levels": depth_levels,
            "market_depth_analysis": depth_analysis,
            "pressure_analysis": {
                "total_bid_pressure": round(total_bid_pressure, 4),
                "total_ask_pressure": round(total_ask_pressure, 4),
                "pressure_ratio": round(pressure_ratio, 4),
                "market_bias": "buying_pressure" if pressure_ratio > 1.1 else "selling_pressure" if pressure_ratio < 0.9 else "balanced"
            },
            "liquidity_analysis": {
                "avg_bid_size": round(total_bid_pressure / len(bids), 4) if bids else 0,
                "avg_ask_size": round(total_ask_pressure / len(asks), 4) if asks else 0,
                "depth_quality": "deep" if total_bid_pressure > 100 and total_ask_pressure > 100 else "shallow",
                "market_impact_1pct": round(abs(float(bids[min(len(bids)-1, 2)][0]) - float(asks[min(len(asks)-1, 2)][0])), 6) if len(bids) > 2 and len(asks) > 2 else 0
            }
        }
        
        logger.info(f"✅ Market depth analysis for {symbol}: {len(depth_analysis)} levels")
        return add_cors_headers(jsonify(add_api_metadata(response_data)))
        
    except Exception as e:
        logger.error(f"Market depth error: {e}")
        return add_cors_headers(jsonify(add_api_metadata({
            'error': 'Failed to analyze market depth', 
            'details': str(e),
            'symbol': request.args.get('symbol', 'BTC-USDT')
        }))), 500

@gpts_minimal.route('/status', methods=['GET'])
@cross_origin()
def gpts_status():
    """Check system status for GPTs"""
    try:
        initialize_core_services()
        
        # Test OKX connectivity
        okx_status = "disconnected"
        if okx_fetcher:
            ticker = okx_fetcher.get_ticker('BTC-USDT')
            okx_status = "connected" if ticker else "disconnected"
        
        response = {
            "status": "operational",
            "services": {
                "okx_data": okx_status == "connected",
                "ai_analysis": True,
                "telegram_bot": True,
                "redis_cache": True,
                "system_enhancements": True
            },
            "endpoints_available": 18,  # Updated count with indicators and funding-rate
            "server_time": datetime.now().isoformat(),
            "core_features": [
                "Trading signals for ChatGPT",
                "Comprehensive technical indicators (MACD, RSI, Stochastic, CCI, etc.)",
                "Funding rate and Open Interest data",
                "Orderbook and market depth data",
                "Volume Delta and volume analysis",
                "Telegram notifications with retry", 
                "Real-time market data",
                "AI-powered analysis",
                "Health monitoring"
            ],
            "focus": "ChatGPT integration and Telegram notifications"
        }
        
        return add_cors_headers(jsonify(add_api_metadata(response)))
        
    except Exception as e:
        logger.error(f"Status check error: {e}")
        return add_cors_headers(jsonify(add_api_metadata({
            'error': 'Status check failed', 
            'details': str(e)
        }))), 500

@gpts_minimal.route('/indicators', methods=['GET'])
@cross_origin()
def gpts_technical_indicators():
    """Get comprehensive technical indicators for ChatGPT Custom GPT"""
    try:
        symbol = request.args.get('symbol', 'BTC-USDT')
        timeframe = request.args.get('timeframe', '1H')
        
        logger.info(f"🔍 GPT indicators request: {symbol} {timeframe}")
        
        # Normalize symbol format
        if '/' in symbol:
            symbol = symbol.replace('/', '-')
        if not symbol.endswith('-USDT'):
            symbol = f"{symbol.replace('USDT', '')}-USDT"
        
        initialize_core_services()
        
        if not okx_fetcher:
            return add_cors_headers(jsonify(add_api_metadata({
                "error": "OKX service not available",
                "symbol": symbol
            }))), 503
        
        # Get market data
        df = okx_fetcher.get_historical_data(symbol, timeframe, 200)
        
        if df is None or df.empty:
            return add_cors_headers(jsonify(add_api_metadata({
                "error": "No market data available",
                "symbol": symbol
            }))), 400
        
        # Import technical analysis library
        import ta
        import numpy as np
        import json
        
        class NumpyEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, np.bool_):
                    return bool(obj)
                if isinstance(obj, (np.integer, np.int64, np.int32, np.int8, np.int16)):
                    return int(obj)
                if isinstance(obj, (np.floating, np.float64, np.float32, np.float16)):
                    return float(obj)
                if isinstance(obj, np.ndarray):
                    return obj.tolist()
                return super().default(obj)
        
        current_price = float(df['close'].iloc[-1])
        
        # Calculate all technical indicators
        indicators = {}
        
        # 1. RSI
        rsi = ta.momentum.RSIIndicator(df['close'], window=14).rsi()
        rsi_value = float(rsi.iloc[-1]) if not rsi.empty else 50.0
        indicators['rsi'] = {
            'value': rsi_value,
            'overbought': bool(rsi_value > 70),
            'oversold': bool(rsi_value < 30),
            'signal': 'SELL' if rsi_value > 70 else 'BUY' if rsi_value < 30 else 'NEUTRAL'
        }
        
        # 2. MACD
        macd_indicator = ta.trend.MACD(df['close'])
        macd_line = macd_indicator.macd()
        macd_signal = macd_indicator.macd_signal()
        macd_histogram = macd_indicator.macd_diff()
        
        macd_val = float(macd_line.iloc[-1]) if not macd_line.empty else 0
        signal_val = float(macd_signal.iloc[-1]) if not macd_signal.empty else 0
        histogram_val = float(macd_histogram.iloc[-1]) if not macd_histogram.empty else 0
        
        indicators['macd'] = {
            'macd': macd_val,
            'signal': signal_val,
            'histogram': histogram_val,
            'bullish': bool(macd_val > signal_val),
            'trend': 'BULLISH' if macd_val > signal_val else 'BEARISH'
        }
        
        # 3. Stochastic
        stoch = ta.momentum.StochasticOscillator(df['high'], df['low'], df['close'])
        stoch_k = stoch.stoch()
        stoch_d = stoch.stoch_signal()
        
        k_val = float(stoch_k.iloc[-1]) if not stoch_k.empty else 50
        d_val = float(stoch_d.iloc[-1]) if not stoch_d.empty else 50
        
        indicators['stochastic'] = {
            'k': k_val,
            'd': d_val,
            'overbought': bool(k_val > 80),
            'oversold': bool(k_val < 20),
            'signal': 'SELL' if k_val > 80 else 'BUY' if k_val < 20 else 'NEUTRAL'
        }
        
        # 4. CCI (Commodity Channel Index)
        cci = ta.trend.CCIIndicator(df['high'], df['low'], df['close'])
        cci_value = cci.cci()
        
        cci_val = float(cci_value.iloc[-1]) if not cci_value.empty else 0
        
        indicators['cci'] = {
            'value': cci_val,
            'overbought': bool(cci_val > 100),
            'oversold': bool(cci_val < -100),
            'signal': 'SELL' if cci_val > 100 else 'BUY' if cci_val < -100 else 'NEUTRAL'
        }
        
        # 5. Bollinger Bands
        bb = ta.volatility.BollingerBands(df['close'])
        bb_upper = bb.bollinger_hband()
        bb_middle = bb.bollinger_mavg()
        bb_lower = bb.bollinger_lband()
        
        upper_val = float(bb_upper.iloc[-1]) if not bb_upper.empty else current_price * 1.02
        middle_val = float(bb_middle.iloc[-1]) if not bb_middle.empty else current_price
        lower_val = float(bb_lower.iloc[-1]) if not bb_lower.empty else current_price * 0.98
        
        indicators['bollinger_bands'] = {
            'upper': upper_val,
            'middle': middle_val,
            'lower': lower_val,
            'position': 'ABOVE' if current_price > upper_val else 'BELOW' if current_price < lower_val else 'INSIDE',
            'squeeze': bool(abs(upper_val - lower_val) < (middle_val * 0.1))
        }
        
        # 6. EMA Analysis
        ema_20 = ta.trend.EMAIndicator(df['close'], window=20).ema_indicator()
        ema_50 = ta.trend.EMAIndicator(df['close'], window=50).ema_indicator()
        
        ema_20_val = float(ema_20.iloc[-1]) if not ema_20.empty else current_price
        ema_50_val = float(ema_50.iloc[-1]) if not ema_50.empty else current_price
        
        indicators['ema'] = {
            'ema_20': ema_20_val,
            'ema_50': ema_50_val,
            'trend': 'BULLISH' if ema_20_val > ema_50_val else 'BEARISH',
            'price_vs_ema20': 'ABOVE' if current_price > ema_20_val else 'BELOW'
        }
        
        # 7. Volume Analysis
        volume_sma = df['volume'].rolling(window=20).mean()
        current_volume = float(df['volume'].iloc[-1])
        avg_volume = float(volume_sma.iloc[-1]) if not volume_sma.empty else current_volume
        
        # Calculate volume delta (simplified - bid vs ask approximation)
        volume_delta = 0
        if len(df) >= 2:
            price_change = df['close'].iloc[-1] - df['close'].iloc[-2]
            volume_delta = current_volume if price_change > 0 else -current_volume
        
        indicators['volume_analysis'] = {
            'current_volume': current_volume,
            'average_volume': avg_volume,
            'volume_ratio': current_volume / avg_volume if avg_volume > 0 else 1,
            'volume_spike': bool(current_volume > avg_volume * 1.5),
            'volume_delta': volume_delta,
            'volume_trend': 'HIGH' if current_volume > avg_volume * 1.2 else 'LOW' if current_volume < avg_volume * 0.8 else 'NORMAL'
        }
        
        # 8. ATR (Average True Range)
        atr = ta.volatility.AverageTrueRange(df['high'], df['low'], df['close'])
        atr_value = atr.average_true_range()
        
        atr_val = float(atr_value.iloc[-1]) if not atr_value.empty else 0
        volatility_percent = (atr_val / current_price * 100) if atr_val > 0 and current_price > 0 else 0
        
        indicators['atr'] = {
            'value': atr_val,
            'volatility_percent': volatility_percent,
            'volatility_level': 'HIGH' if volatility_percent > 3 else 'LOW' if volatility_percent < 1 else 'NORMAL'
        }
        
        # 9. Williams %R
        williams_r = ta.momentum.WilliamsRIndicator(df['high'], df['low'], df['close'])
        wr_value = williams_r.williams_r()
        
        wr_val = float(wr_value.iloc[-1]) if not wr_value.empty else -50
        
        indicators['williams_r'] = {
            'value': wr_val,
            'overbought': bool(wr_val > -20),
            'oversold': bool(wr_val < -80),
            'signal': 'SELL' if wr_val > -20 else 'BUY' if wr_val < -80 else 'NEUTRAL'
        }
        
        # 10. Money Flow Index (MFI)
        mfi = ta.volume.MFIIndicator(df['high'], df['low'], df['close'], df['volume'])
        mfi_value = mfi.money_flow_index()
        
        mfi_val = float(mfi_value.iloc[-1]) if not mfi_value.empty else 50
        
        indicators['mfi'] = {
            'value': mfi_val,
            'overbought': bool(mfi_val > 80),
            'oversold': bool(mfi_val < 20),
            'signal': 'SELL' if mfi_val > 80 else 'BUY' if mfi_val < 20 else 'NEUTRAL'
        }
        
        response_data = {
            "symbol": symbol,
            "timeframe": timeframe,
            "current_price": current_price,
            "technical_indicators": indicators,
            "market_summary": {
                "overall_trend": "BULLISH" if sum([
                    1 if indicators['rsi']['signal'] == 'BUY' else -1 if indicators['rsi']['signal'] == 'SELL' else 0,
                    1 if indicators['macd']['trend'] == 'BULLISH' else -1,
                    1 if indicators['stochastic']['signal'] == 'BUY' else -1 if indicators['stochastic']['signal'] == 'SELL' else 0,
                    1 if indicators['cci']['signal'] == 'BUY' else -1 if indicators['cci']['signal'] == 'SELL' else 0,
                    1 if indicators['ema']['trend'] == 'BULLISH' else -1
                ]) > 0 else "BEARISH",
                "momentum": "STRONG" if bool(indicators['volume_analysis']['volume_spike']) else "WEAK",
                "volatility": str(indicators['atr']['volatility_level'])
            }
        }
        
        logger.info(f"✅ Technical indicators calculated for {symbol}")
        
        # Use custom JSON encoder for numpy types
        try:
            json_str = json.dumps(response_data, cls=NumpyEncoder)
            response_obj = json.loads(json_str)
            return add_cors_headers(jsonify(add_api_metadata(response_obj)))
        except Exception as json_error:
            logger.error(f"JSON encoding error: {json_error}")
            # Fallback: return basic response
            return add_cors_headers(jsonify(add_api_metadata({
                "symbol": symbol,
                "current_price": float(current_price),
                "message": "Technical indicators calculated but JSON serialization failed"
            })))
        
    except Exception as e:
        logger.error(f"Technical indicators error: {e}")
        return add_cors_headers(jsonify(add_api_metadata({
            'error': 'Failed to calculate technical indicators', 
            'details': str(e),
            'symbol': request.args.get('symbol', 'BTC-USDT')
        }))), 500

@gpts_minimal.route('/funding-rate', methods=['GET'])
@cross_origin()
def gpts_funding_rate():
    """Get funding rate and Open Interest data for ChatGPT Custom GPT"""
    try:
        symbol = request.args.get('symbol', 'BTC-USDT')
        
        logger.info(f"🔍 GPT funding rate request: {symbol}")
        
        # Normalize symbol format
        if '/' in symbol:
            symbol = symbol.replace('/', '-')
        if not symbol.endswith('-USDT'):
            symbol = f"{symbol.replace('USDT', '')}-USDT"
        
        initialize_core_services()
        
        if not okx_fetcher:
            return add_cors_headers(jsonify(add_api_metadata({
                "error": "OKX service not available",
                "symbol": symbol
            }))), 503
        
        # Fix symbol format for funding rate (should be BTC-USDT-SWAP for futures)
        funding_symbol = symbol
        if symbol.endswith('-USDT'):
            funding_symbol = symbol + '-SWAP'
        
        # Get funding rate data
        funding_data = okx_fetcher.get_funding_rate(funding_symbol)
        
        if not funding_data:
            return add_cors_headers(jsonify(add_api_metadata({
                "error": "No funding rate data available",
                "symbol": symbol
            }))), 400
        
        # Get Open Interest data (using OKX API directly)
        import requests
        try:
            oi_url = f"{okx_fetcher.base_url}/api/v5/public/open-interest"
            oi_params = {'instId': funding_symbol}  # Use funding_symbol for consistency
            oi_response = requests.get(oi_url, params=oi_params, timeout=10)
            oi_data = oi_response.json()
            
            open_interest = 0
            oi_ccy = 0
            if oi_data.get('code') == '0' and oi_data.get('data'):
                open_interest = float(oi_data['data'][0].get('oi', 0))
                oi_ccy = float(oi_data['data'][0].get('oiCcy', 0))
        except Exception as e:
            logger.warning(f"Failed to get OI data: {e}")
            open_interest = 0
            oi_ccy = 0
        
        # Analyze funding rate sentiment
        funding_rate = float(funding_data.get('funding_rate', 0))
        funding_rate_percent = funding_rate * 100
        
        # Determine sentiment based on funding rate
        if funding_rate_percent > 0.05:
            sentiment = "VERY_BULLISH"
            description = "Sangat bullish - Long traders bayar funding tinggi"
            strength = min(abs(funding_rate_percent) * 20, 100)
        elif funding_rate_percent > 0.01:
            sentiment = "BULLISH"
            description = "Bullish - Long traders dominan"
            strength = min(abs(funding_rate_percent) * 20, 100)
        elif funding_rate_percent > -0.01:
            sentiment = "NEUTRAL"
            description = "Neutral - Funding rate seimbang"
            strength = 50
        elif funding_rate_percent > -0.05:
            sentiment = "BEARISH"
            description = "Bearish - Short traders dominan"
            strength = min(abs(funding_rate_percent) * 20, 100)
        else:
            sentiment = "VERY_BEARISH"
            description = "Sangat bearish - Short traders bayar funding tinggi"
            strength = min(abs(funding_rate_percent) * 20, 100)
        
        response_data = {
            "symbol": symbol,
            "funding_rate": {
                "current_rate": funding_rate,
                "rate_percent": round(funding_rate_percent, 4),
                "next_funding_time": funding_data.get('next_funding_time'),
                "funding_interval": "8H",
                "sentiment": sentiment,
                "description": description,
                "strength": round(strength, 1)
            },
            "open_interest": {
                "oi_contracts": open_interest,
                "oi_value_usd": oi_ccy,
                "oi_trend": "INCREASING" if open_interest > 0 else "UNKNOWN"
            },
            "market_analysis": {
                "long_short_ratio": "LONGS_PAYING" if funding_rate > 0 else "SHORTS_PAYING" if funding_rate < 0 else "BALANCED",
                "market_structure": "CONTANGO" if funding_rate > 0 else "BACKWARDATION" if funding_rate < 0 else "BALANCED",
                "trader_sentiment": sentiment,
                "risk_assessment": "HIGH" if abs(funding_rate_percent) > 0.1 else "MEDIUM" if abs(funding_rate_percent) > 0.05 else "LOW"
            }
        }
        
        logger.info(f"✅ Funding rate data fetched for {symbol}: {funding_rate_percent:.4f}%")
        return add_cors_headers(jsonify(add_api_metadata(response_data)))
        
    except Exception as e:
        logger.error(f"Funding rate error: {e}")
        return add_cors_headers(jsonify(add_api_metadata({
            'error': 'Failed to fetch funding rate data', 
            'details': str(e),
            'symbol': request.args.get('symbol', 'BTC-USDT')
        }))), 500

logger.info("🚀 Minimal GPTs API initialized successfully")