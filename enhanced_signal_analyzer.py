# signal_routes.py
from flask import Blueprint, jsonify, request
from core.okx_fetcher import OKXFetcher
from core.professional_smc_analyzer import ProfessionalSMCAnalyzer
from core.signal_generator import SignalGenerator  # Buat class ini jika belum ada
from core.crypto_news_analyzer import get_news_analyzer
from core.telegram_notifier import send_telegram_message  # Buat function ini jika belum ada
import logging
from datetime import datetime
import asyncio

signal_api = Blueprint('signal_api', __name__, url_prefix='/api/signal')
enhanced_api = Blueprint('enhanced_api', __name__, url_prefix='/api/enhanced-signal')
logger = logging.getLogger(__name__)

# Inisialisasi komponen
okx_fetcher = OKXFetcher()
smc_analyzer = ProfessionalSMCAnalyzer()
signal_generator = SignalGenerator()

@enhanced_api.route('/analyze', methods=['POST'])
def analyze_enhanced_signal():
    """
    Analyze market with enhanced signal engine
    Combines SMC, indicators, news, and multi-timeframe
    """
    try:
        data = request.get_json()
        
        # Parse parameters
        symbol = data.get('symbol', 'BTC').upper()
        timeframe = data.get('timeframe', '1H')
        include_news = data.get('include_news', True)
        include_multi_timeframe = data.get('include_multi_timeframe', True)
        
        # Konversi format simbol
        okx_symbol = f"{symbol}-USDT" if not '-' in symbol else symbol
        if symbol.endswith('USDT'):
            okx_symbol = symbol.replace('USDT', '-USDT')
        
        # Fetch data pasar
        market_data = okx_fetcher.get_historical_data(okx_symbol, timeframe, 200)
        
        if not market_data or 'candles' not in market_data:
            return jsonify({
                "status": "error",
                "message": f"Failed to get market data for {symbol} {timeframe}"
            }), 400
        
        # Analisis SMC
        smc_result = smc_analyzer.analyze_market_structure(market_data['candles'])
        
        # Variabel untuk menyimpan data tambahan
        additional_data = {}
        
        # Get multi-timeframe data jika diminta
        if include_multi_timeframe:
            mtf_data = {}
            
            # Timeframe yang akan dianalisis
            timeframes = []
            if timeframe == '5m':
                timeframes = ['15m', '1H', '4H']
            elif timeframe == '15m':
                timeframes = ['1H', '4H', '1D']
            elif timeframe == '1H':
                timeframes = ['4H', '1D']
            elif timeframe == '4H':
                timeframes = ['1D']
            
            # Fetch dan analisis untuk setiap timeframe
            for tf in timeframes:
                try:
                    tf_data = okx_fetcher.get_historical_data(okx_symbol, tf, 100)
                    if tf_data and 'candles' in tf_data:
                        tf_smc = smc_analyzer.analyze_market_structure(tf_data['candles'])
                        mtf_data[tf] = {
                            "market_structure": tf_smc.get('market_structure', 'NEUTRAL'),
                            "trend_bias": tf_smc.get('trend_bias', 'NEUTRAL'),
                            "current_phase": tf_smc.get('current_phase', 'ACCUMULATION')
                        }
                except Exception as e:
                    logger.warning(f"Error analyzing {tf} timeframe: {e}")
            
            additional_data['multi_timeframe'] = mtf_data
        
        # Get news sentiment jika diminta
        if include_news:
            try:
                news_analyzer = get_news_analyzer()
                news_result = asyncio.run(news_analyzer.get_news_sentiment(limit=5))
                
                if news_result['status'] == 'success':
                    additional_data['news'] = {
                        "sentiment": news_result['aggregate']['overall_sentiment'],
                        "confidence": news_result['aggregate']['average_confidence'],
                        "high_impact_count": news_result['aggregate']['high_impact_news']
                    }
            except Exception as e:
                logger.warning(f"Error getting news sentiment: {e}")
        
        # Generate enhanced signal
        signal_result = signal_generator.generate_enhanced_signal(
            market_data,
            smc_result,
            additional_data
        )
        
        # Current price
        current_price = float(market_data['candles'][-1]['close']) if market_data['candles'] else 0
        
        # Format response
        result = {
            "status": "success",
            "symbol": symbol,
            "timeframe": timeframe,
            "current_price": current_price,
            "signal": {
                "bias": signal_result.get('bias', 'NEUTRAL'),
                "strength": signal_result.get('strength', 0),
                "action": signal_result.get('action', 'WAIT'),
                "confidence": signal_result.get('confidence', 0),
                "entry_zone": {
                    "low": signal_result.get('entry_low', 0),
                    "high": signal_result.get('entry_high', 0)
                },
                "stop_loss": signal_result.get('stop_loss', 0),
                "take_profit": signal_result.get('take_profit', []),
                "risk_reward": signal_result.get('risk_reward', 0)
            },
            "analysis": {
                "market_structure": smc_result.get('market_structure', 'NEUTRAL'),
                "trend_strength": smc_result.get('trend_strength', 0),
                "volatility": signal_result.get('volatility', "NORMAL"),
                "key_levels": smc_result.get('key_levels', []),
                "multi_timeframe_alignment": signal_result.get('mtf_alignment', 'NEUTRAL'),
                "indicators": signal_result.get('indicators', {})
            },
            "news_impact": additional_data.get('news', {}),
            "multi_timeframe_context": additional_data.get('multi_timeframe', {}),
            "confluence_factors": signal_result.get('confluence_factors', []),
            "risk_assessment": {
                "market_conditions": signal_result.get('market_conditions', 'NORMAL'),
                "risk_level": signal_result.get('risk_level', 'MEDIUM'),
                "position_size_adjustment": signal_result.get('position_size_adjustment', 1.0),
                "comments": signal_result.get('risk_comments', "")
            },
            "generated_at": datetime.utcnow().isoformat()
        }
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error analyzing enhanced signal: {e}")
        return jsonify({
            "status": "error",
            "message": "Failed to analyze enhanced signal",
            "error": str(e)
        }), 500

@signal_api.route('/top', methods=['GET'])
def get_top_signals():
    """
    Get top trading signals across all symbols
    """
    try:
        # Parse parameters
        timeframe = request.args.get('timeframe', '1H')
        limit = min(int(request.args.get('limit', 5)), 10)
        min_strength = float(request.args.get('min_strength', 0.6))
        
        # List simbol yang akan diperiksa
        symbols = ["BTC", "ETH", "SOL", "ADA", "AVAX", "DOT", "LINK", "DOGE", "MATIC", "UNI"]
        
        # Tampung hasil sinyal
        all_signals = []
        
        # Analisis setiap simbol
        for symbol in symbols:
            try:
                # Konversi format simbol
                okx_symbol = f"{symbol}-USDT"
                
                # Fetch data pasar
                market_data = okx_fetcher.get_historical_data(okx_symbol, timeframe, 200)
                
                if not market_data or 'candles' not in market_data:
                    logger.warning(f"Failed to get market data for {symbol}")
                    continue
                
                # Analisis SMC
                smc_result = smc_analyzer.analyze_market_structure(market_data['candles'])
                
                # Generate sinyal
                signal_result = signal_generator.generate_signal(market_data, smc_result, is_concise=True)
                
                # Skip jika sinyal lemah
                if signal_result.get('strength', 0) < min_strength:
                    continue
                
                # Current price
                current_price = float(market_data['candles'][-1]['close']) if market_data['candles'] else 0
                
                # Tambahkan ke list sinyal
                all_signals.append({
                    "symbol": symbol,
                    "bias": signal_result.get('bias', 'NEUTRAL'),
                    "action": signal_result.get('action', 'WAIT'),
                    "strength": signal_result.get('strength', 0),
                    "confidence": signal_result.get('confidence', 0),
                    "current_price": current_price,
                    "entry_zone": {
                        "low": signal_result.get('entry_low', 0),
                        "high": signal_result.get('entry_high', 0)
                    },
                    "key_drivers": signal_result.get('key_drivers', [])[:2]  # Limit to 2 key drivers
                })
                
            except Exception as e:
                logger.warning(f"Error analyzing {symbol}: {e}")
                continue
        
        # Sort by strength dan confidence
        all_signals.sort(key=lambda x: (x['strength'], x['confidence']), reverse=True)
        
        # Limit jumlah sinyal
        top_signals = all_signals[:limit]
        
        return jsonify({
            "status": "success",
            "timeframe": timeframe,
            "signals": top_signals,
            "count": len(top_signals),
            "min_strength_filter": min_strength,
            "generated_at": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting top signals: {e}")
        return jsonify({
            "status": "error",
            "message": "Failed to get top signals",
            "error": str(e)
        }), 500

@signal_api.route('/top/telegram', methods=['POST'])
def send_top_signals_telegram():
    """
    Send top signals to Telegram
    """
    try:
        data = request.get_json()
        
        # Parse parameters
        timeframe = data.get('timeframe', '1H')
        limit = min(int(data.get('limit', 3)), 5)
        min_strength = float(data.get('min_strength', 0.7))
        chat_id = data.get('chat_id')  # Optional override
        
        # List simbol yang akan diperiksa
        symbols = ["BTC", "ETH", "SOL", "ADA", "AVAX"]
        
        # Tampung hasil sinyal
        all_signals = []
        
        # Analisis setiap simbol
        for symbol in symbols:
            try:
                # Konversi format simbol
                okx_symbol = f"{symbol}-USDT"
                
                # Fetch data pasar
                market_data = okx_fetcher.get_historical_data(okx_symbol, timeframe, 200)
                
                if not market_data or 'candles' not in market_data:
                    continue
                
                # Analisis SMC
                smc_result = smc_analyzer.analyze_market_structure(market_data['candles'])
                
                # Generate sinyal
                signal_result = signal_generator.generate_signal(market_data, smc_result, is_concise=True)
                
                # Skip jika sinyal lemah
                if signal_result.get('strength', 0) < min_strength:
                    continue
                
                # Current price
                current_price = float(market_data['candles'][-1]['close']) if market_data['candles'] else 0
                
                # Tambahkan ke list sinyal
                all_signals.append({
                    "symbol": symbol,
                    "bias": signal_result.get('bias', 'NEUTRAL'),
                    "action": signal_result.get('action', 'WAIT'),
                    "strength": signal_result.get('strength', 0),
                    "confidence": signal_result.get('confidence', 0),
                    "current_price": current_price,
                    "entry_zone": {
                        "low": signal_result.get('entry_low', 0),
                        "high": signal_result.get('entry_high', 0)
                    }
                })
                
            except Exception as e:
                logger.warning(f"Error analyzing {symbol}: {e}")
                continue
        
        # Sort by strength dan confidence
        all_signals.sort(key=lambda x: (x['strength'], x['confidence']), reverse=True)
        
        # Limit jumlah sinyal
        top_signals = all_signals[:limit]
        
        if not top_signals:
            return jsonify({
                "status": "warning",
                "message": "No strong signals found to send",
                "sent": False
            })
        
        # Format pesan Telegram
        message = f"🚨 *TOP SIGNALS ({timeframe})* 🚨\n\n"
        
        for idx, signal in enumerate(top_signals, 1):
            action_emoji = "🟢" if signal['bias'] == 'BULLISH' else "🔴" if signal['bias'] == 'BEARISH' else "⚪"
            
            message += f"{idx}. {action_emoji} *{signal['symbol']}*: {signal['action']}\n"
            message += f"   💲 Price: ${signal['current_price']:.4f}\n"
            message += f"   🎯 Entry: ${signal['entry_zone']['low']:.4f} - ${signal['entry_zone']['high']:.4f}\n"
            message += f"   💪 Strength: {signal['strength']:.2f} | Confidence: {signal['confidence']:.2f}\n\n"
        
        message += f"⏱ Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}\n"
        message += f"🤖 *Crypto Trading AI Platform*"
        
        # Kirim ke Telegram
        send_result = send_telegram_message(message, chat_id)
        
        if send_result.get('success'):
            return jsonify({
                "status": "success",
                "message": "Signals sent to Telegram successfully",
                "sent": True,
                "signals": top_signals,
                "count": len(top_signals)
            })
        else:
            return jsonify({
                "status": "error",
                "message": f"Failed to send signals to Telegram: {send_result.get('error')}",
                "sent": False,
                "signals": top_signals,
                "count": len(top_signals)
            }), 500
        
    except Exception as e:
        logger.error(f"Error sending signals to Telegram: {e}")
        return jsonify({
            "status": "error",
            "message": "Failed to send signals to Telegram",
            "error": str(e),
            "sent": False
        }), 500
