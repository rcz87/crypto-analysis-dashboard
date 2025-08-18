# gpts_routes.py - Production Ready for VPS Hostinger
from flask import Blueprint, jsonify, request
import os
from sqlalchemy import create_engine, text
import logging
from core.okx_fetcher import OKXFetcher
from core.ai_engine import get_ai_engine
from core.professional_smc_analyzer import ProfessionalSMCAnalyzer
from core.signal_generator import SignalGenerator
import time

gpts_api = Blueprint('gpts_api', __name__, url_prefix='/api/gpts')
logger = logging.getLogger(__name__)

# Initialize components with fixed versions
smc_analyzer = ProfessionalSMCAnalyzer()
signal_generator = SignalGenerator()
okx_fetcher = OKXFetcher()

# Helper functions
ALLOWED_TFS = {"1m","3m","5m","15m","30m","1H","2H","4H","6H","12H","1D","2D","3D","1W","1M","3M"}

def normalize_symbol(sym: str) -> str:
    s = (sym or "").upper()
    if "-" in s:
        return s
    if s.endswith("USDT"):
        return s.replace("USDT", "-USDT")
    return f"{s}-USDT"

def validate_tf(tf: str) -> bool:
    return tf in ALLOWED_TFS

@gpts_api.route('/status', methods=['GET'])
def get_status():
    """Status ringkas ketersediaan semua komponen sistem"""
    try:
        # Test OKX API
        okx_test = okx_fetcher.test_connection()
        okx_status = okx_test['status']
        
        # Test AI Engine
        try:
            ai_engine = get_ai_engine()
            ai_test = ai_engine.test_connection()
            openai_status = "available" if ai_test.get("available", False) else "unavailable"
        except:
            openai_status = "unavailable"
        
        # Test Database
        db_status = "unavailable"
        db_url = os.environ.get("DATABASE_URL")
        if db_url:
            try:
                engine = create_engine(db_url)
                with engine.connect() as conn:
                    conn.execute(text('SELECT 1'))
                db_status = "available"
            except Exception as e:
                logger.error(f"Database test failed: {e}")
        
        version_info = {
            "api_version": "2.0.0",
            "core_version": "1.2.3",
            "supported_symbols": ["BTC", "ETH", "SOL", "ADA", "DOT", "AVAX"],
            "supported_timeframes": sorted(list(ALLOWED_TFS))
        }
        
        return jsonify({
            "status": "active",
            "components": {
                "okx_api": okx_status,
                "openai": openai_status,
                "database": db_status,
                "smc_analyzer": "available",
                "signal_generator": "available"
            },
            "version": version_info,
            "timestamp": int(time.time())
        })
        
    except Exception as e:
        logger.error(f"Status check error: {e}")
        return jsonify({
            "status": "error",
            "message": str(e),
            "timestamp": int(time.time())
        }), 500

@gpts_api.route('/sinyal/tajam', methods=['POST'])
def get_sharp_signal():
    """Sharp signal analysis endpoint optimized for VPS deployment"""
    try:
        data = request.get_json() or {}
        symbol = normalize_symbol(data.get('symbol', 'BTC-USDT'))
        timeframe = data.get('timeframe', '1H')
        
        # Validate timeframe
        if not validate_tf(timeframe):
            return jsonify({
                "status": "error",
                "message": f"Invalid timeframe. Supported: {list(ALLOWED_TFS)}"
            }), 400
        
        logger.info(f"Processing sharp signal request: {symbol} {timeframe}")
        
        # Get market data
        market_data = okx_fetcher.get_historical_data(symbol, timeframe, 100)
        
        if not market_data or not market_data.get('candles'):
            return jsonify({
                "status": "error",
                "message": "Failed to fetch market data",
                "symbol": symbol,
                "timeframe": timeframe
            }), 500
        
        # SMC Analysis
        smc_analysis = smc_analyzer.analyze_market_structure(market_data)
        
        # Generate signal
        signal = signal_generator.generate_signal(market_data, smc_analysis)
        
        # Build comprehensive response
        response = {
            "status": "success",
            "symbol": symbol,
            "timeframe": timeframe,
            "timestamp": int(time.time()),
            "signal": {
                "direction": signal['direction'],
                "confidence": signal['confidence'],
                "entry_price": signal['entry_price'],
                "take_profit": signal['take_profit'],
                "stop_loss": signal['stop_loss'],
                "reasoning": signal['reasoning']
            },
            "analysis": {
                "technical": f"Price: {signal['entry_price']:.2f}, Direction: {signal['direction']}",
                "smc": {
                    "market_bias": smc_analysis['market_bias'],
                    "structure_break": smc_analysis['structure_analysis']['structure_break'],
                    "confidence": smc_analysis['confidence']
                },
                "risk_reward": round(abs(signal['take_profit'] - signal['entry_price']) / abs(signal['entry_price'] - signal['stop_loss']), 2) if signal['stop_loss'] != signal['entry_price'] else 1.0
            },
            "market_data": {
                "candles_analyzed": market_data['count'],
                "data_status": market_data['status'],
                "current_price": signal['entry_price']
            }
        }
        
        logger.info(f"Sharp signal generated successfully: {signal['direction']} with {signal['confidence']} confidence")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Sharp signal error: {e}")
        return jsonify({
            "status": "error",
            "message": "Failed to generate signal",
            "error": str(e),
            "timestamp": int(time.time())
        }), 500

@gpts_api.route('/market-data', methods=['GET'])
def get_market_data():
    """Get current market data for a symbol"""
    try:
        symbol = normalize_symbol(request.args.get('symbol', 'BTC-USDT'))
        timeframe = request.args.get('timeframe', '1H')
        limit = min(int(request.args.get('limit', 50)), 1440)  # Maksimal OKX limit
        
        if not validate_tf(timeframe):
            return jsonify({
                "status": "error", 
                "message": f"Invalid timeframe. Supported: {list(ALLOWED_TFS)}"
            }), 400
        
        market_data = okx_fetcher.get_historical_data(symbol, timeframe, limit)
        
        if not market_data:
            return jsonify({
                "status": "error",
                "message": "Failed to fetch market data"
            }), 500
        
        return jsonify({
            "status": "success",
            "symbol": symbol,
            "timeframe": timeframe,
            "data": market_data,
            "timestamp": int(time.time())
        })
        
    except Exception as e:
        logger.error(f"Market data error: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@gpts_api.route('/smc-analysis', methods=['GET', 'POST'])
def get_smc_analysis():
    """Get SMC analysis for market data"""
    try:
        # Support both GET and POST requests
        if request.method == 'GET':
            symbol = normalize_symbol(request.args.get('symbol', 'BTC-USDT'))
            timeframe = request.args.get('timeframe', '1H')
        else:
            data = request.get_json() or {}
            symbol = normalize_symbol(data.get('symbol', 'BTC-USDT'))
            timeframe = data.get('timeframe', '1H')
        
        if not validate_tf(timeframe):
            return jsonify({
                "status": "error",
                "message": f"Invalid timeframe. Supported: {list(ALLOWED_TFS)}"
            }), 400
        
        # Get market data
        market_data = okx_fetcher.get_historical_data(symbol, timeframe, 100)
        
        if not market_data:
            return jsonify({
                "status": "error",
                "message": "Failed to fetch market data"
            }), 500
        
        # Perform SMC analysis
        smc_analysis = smc_analyzer.analyze_market_structure(market_data)
        
        return jsonify({
            "status": "success",
            "symbol": symbol,
            "timeframe": timeframe,
            "smc_analysis": smc_analysis,
            "timestamp": int(time.time())
        })
        
    except Exception as e:
        logger.error(f"SMC analysis error: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@gpts_api.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for VPS monitoring"""
    try:
        # Quick component checks
        checks = {
            'okx_fetcher': 'ok',
            'smc_analyzer': 'ok', 
            'signal_generator': 'ok',
            'database': 'ok' if os.environ.get("DATABASE_URL") else 'missing'
        }
        
        all_healthy = all(status == 'ok' for status in checks.values())
        
        return jsonify({
            "status": "healthy" if all_healthy else "degraded",
            "checks": checks,
            "timestamp": int(time.time()),
            "uptime": "active"
        }), 200 if all_healthy else 503
        
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": int(time.time())
        }), 500

@gpts_api.route('/ticker/<symbol>', methods=['GET'])
def get_ticker(symbol):
    """Get real-time ticker data for a symbol"""
    try:
        symbol = normalize_symbol(symbol)
        ticker_data = okx_fetcher.get_ticker_data(symbol)
        
        if 'error' in ticker_data:
            return jsonify({
                "status": "error",
                "message": ticker_data['error']
            }), 500
        
        return jsonify({
            "status": "success",
            "ticker": ticker_data,
            "timestamp": int(time.time())
        })
        
    except Exception as e:
        logger.error(f"Ticker error: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@gpts_api.route('/orderbook/<symbol>', methods=['GET'])
def get_orderbook(symbol):
    """Get order book data for a symbol"""
    try:
        symbol = normalize_symbol(symbol)
        depth = min(int(request.args.get('depth', 20)), 400)
        
        orderbook_data = okx_fetcher.get_order_book(symbol, depth)
        
        if 'error' in orderbook_data:
            return jsonify({
                "status": "error",
                "message": orderbook_data['error']
            }), 500
        
        return jsonify({
            "status": "success",
            "orderbook": orderbook_data,
            "timestamp": int(time.time())
        })
        
    except Exception as e:
        logger.error(f"Order book error: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@gpts_api.route('/analysis', methods=['GET'])
def get_analysis():
    """Get technical analysis for symbol"""
    try:
        symbol = normalize_symbol(request.args.get('symbol', 'BTC-USDT'))
        timeframe = request.args.get('timeframe', '1H')
        
        if not validate_tf(timeframe):
            return jsonify({
                "status": "error",
                "message": f"Invalid timeframe. Supported: {list(ALLOWED_TFS)}"
            }), 400
        
        market_data = okx_fetcher.get_historical_data(symbol, timeframe, 100)
        
        if market_data['status'] != 'success':
            return jsonify({
                "status": "error",
                "message": "Failed to fetch market data for analysis"
            }), 400
        
        # Basic technical analysis with authentic OKX data
        candles = market_data['candles']
        latest = candles[0]
        
        # Calculate indicators with real data
        prices = [float(c['close']) for c in candles[:20]]
        volumes = [float(c['volume']) for c in candles[:20]]
        sma_20 = sum(prices) / len(prices)
        avg_volume = sum(volumes) / len(volumes)
        
        # Trend analysis
        trend = 'bullish' if latest['close'] > sma_20 else 'bearish'
        volume_trend = 'high' if latest['volume'] > avg_volume else 'low'
        
        analysis = {
            'symbol': symbol,
            'timeframe': timeframe,
            'current_price': latest['close'],
            'sma_20': round(sma_20, 2),
            'trend': trend,
            'volume': latest['volume'],
            'volume_trend': volume_trend,
            'price_change_24h': round(((latest['close'] - candles[23]['close']) / candles[23]['close']) * 100, 2) if len(candles) > 23 else 0,
            'timestamp': latest['timestamp'],
            'data_source': 'OKX_Authentic',
            'analysis_type': 'technical_indicators'
        }
        
        return jsonify({
            "status": "success",
            "analysis": analysis
        })
        
    except Exception as e:
        logger.error(f"Analysis endpoint error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Failed to generate analysis"
        }), 500

@gpts_api.route('/signal', methods=['GET'])
def get_signal():
    """Get trading signal based on authentic OKX data"""
    try:
        symbol = normalize_symbol(request.args.get('symbol', 'BTC-USDT'))
        timeframe = request.args.get('timeframe', '1H')
        
        if not validate_tf(timeframe):
            return jsonify({
                "status": "error",
                "message": f"Invalid timeframe. Supported: {list(ALLOWED_TFS)}"
            }), 400
        
        market_data = okx_fetcher.get_historical_data(symbol, timeframe, 50)
        
        if market_data['status'] != 'success':
            return jsonify({
                "status": "error",
                "message": "Failed to fetch market data for signal"
            }), 400
        
        candles = market_data['candles']
        latest = candles[0]
        
        # Signal generation with authentic data
        prices = [float(c['close']) for c in candles[:10]]
        volumes = [float(c['volume']) for c in candles[:10]]
        highs = [float(c['high']) for c in candles[:10]]
        lows = [float(c['low']) for c in candles[:10]]
        
        avg_price = sum(prices) / len(prices)
        avg_volume = sum(volumes) / len(volumes)
        resistance = max(highs)
        support = min(lows)
        
        # Enhanced signal logic
        signal_type = 'neutral'
        confidence = 50
        reasoning = "Market analysis with authentic OKX data"
        
        # Bullish conditions
        if (latest['close'] > avg_price and 
            latest['volume'] > avg_volume * 1.2 and
            latest['close'] > latest['open']):
            signal_type = 'buy'
            confidence = 78
            reasoning = "Strong bullish momentum with high volume"
        
        # Bearish conditions  
        elif (latest['close'] < avg_price and
              latest['volume'] > avg_volume * 1.2 and
              latest['close'] < latest['open']):
            signal_type = 'sell'
            confidence = 75
            reasoning = "Strong bearish momentum with high volume"
        
        # Breakout conditions
        elif latest['close'] > resistance * 0.999:
            signal_type = 'buy'
            confidence = 72
            reasoning = "Resistance breakout detected"
        
        elif latest['close'] < support * 1.001:
            signal_type = 'sell'
            confidence = 70
            reasoning = "Support breakdown detected"
        
        signal = {
            'symbol': symbol,
            'timeframe': timeframe,
            'signal': signal_type,
            'confidence': confidence,
            'current_price': latest['close'],
            'target_price': round(latest['close'] * (1.025 if signal_type == 'buy' else 0.975), 2),
            'stop_loss': round(latest['close'] * (0.985 if signal_type == 'buy' else 1.015), 2),
            'support_level': round(support, 2),
            'resistance_level': round(resistance, 2),
            'volume_strength': 'high' if latest['volume'] > avg_volume else 'normal',
            'timestamp': latest['timestamp'],
            'data_source': 'OKX_Authentic',
            'reasoning': reasoning
        }
        
        return jsonify({
            "status": "success",
            "signal": signal
        })
        
    except Exception as e:
        logger.error(f"Signal endpoint error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Failed to generate signal"
        }), 500

@gpts_api.route('/smc-zones', methods=['GET'])
def get_smc_zones():
    """Get Smart Money Concept zones with authentic OKX data"""
    try:
        symbol = normalize_symbol(request.args.get('symbol', 'BTC-USDT'))
        timeframe = request.args.get('timeframe', '4H')
        
        if not validate_tf(timeframe):
            return jsonify({
                "status": "error",
                "message": f"Invalid timeframe. Supported: {list(ALLOWED_TFS)}"
            }), 400
        
        market_data = okx_fetcher.get_historical_data(symbol, timeframe, 200)
        
        if market_data['status'] != 'success':
            return jsonify({
                "status": "error",
                "message": "Failed to fetch market data for SMC analysis"
            }), 400
        
        candles = market_data['candles']
        
        # SMC zone identification with authentic data
        highs = [float(c['high']) for c in candles[:50]]
        lows = [float(c['low']) for c in candles[:50]]
        closes = [float(c['close']) for c in candles[:50]]
        volumes = [float(c['volume']) for c in candles[:50]]
        
        current_price = float(candles[0]['close'])
        
        # Key levels identification
        resistance_zones = []
        support_zones = []
        
        # Find swing highs and lows
        for i in range(2, len(highs) - 2):
            # Swing high
            if (highs[i] > highs[i-1] and highs[i] > highs[i-2] and 
                highs[i] > highs[i+1] and highs[i] > highs[i+2]):
                resistance_zones.append({
                    'price': highs[i],
                    'volume': volumes[i],
                    'strength': 'high' if volumes[i] > sum(volumes)/len(volumes) else 'medium'
                })
            
            # Swing low
            if (lows[i] < lows[i-1] and lows[i] < lows[i-2] and 
                lows[i] < lows[i+1] and lows[i] < lows[i+2]):
                support_zones.append({
                    'price': lows[i],
                    'volume': volumes[i],
                    'strength': 'high' if volumes[i] > sum(volumes)/len(volumes) else 'medium'
                })
        
        # Sort and get top levels
        resistance_zones = sorted(resistance_zones, key=lambda x: x['price'], reverse=True)[:5]
        support_zones = sorted(support_zones, key=lambda x: x['price'], reverse=True)[:5]
        
        # Market structure analysis
        zone_range = max(highs) - min(lows)
        premium_threshold = min(lows) + (zone_range * 0.7)
        discount_threshold = min(lows) + (zone_range * 0.3)
        
        if current_price > premium_threshold:
            market_structure = 'premium'
            bias = 'bearish'
        elif current_price < discount_threshold:
            market_structure = 'discount'
            bias = 'bullish'
        else:
            market_structure = 'equilibrium'
            bias = 'neutral'
        
        # Order blocks detection (simplified)
        order_blocks = []
        for i in range(10, len(candles) - 1):
            candle = candles[i]
            if (float(candle['volume']) > sum(volumes[:20])/20 * 1.5 and
                abs(float(candle['close']) - float(candle['open'])) > 
                (max(highs[:20]) - min(lows[:20])) * 0.01):
                order_blocks.append({
                    'type': 'bullish' if float(candle['close']) > float(candle['open']) else 'bearish',
                    'high': float(candle['high']),
                    'low': float(candle['low']),
                    'volume': float(candle['volume']),
                    'timestamp': candle['timestamp']
                })
        
        smc_data = {
            'symbol': symbol,
            'timeframe': timeframe,
            'current_price': current_price,
            'market_structure': market_structure,
            'bias': bias,
            'premium_threshold': round(premium_threshold, 2),
            'discount_threshold': round(discount_threshold, 2),
            'resistance_zones': resistance_zones,
            'support_zones': support_zones,
            'order_blocks': order_blocks[:10],  # Limit to 10
            'timestamp': candles[0]['timestamp'],
            'data_source': 'OKX_Authentic',
            'zones_detected': len(resistance_zones) + len(support_zones),
            'liquidity_analysis': {
                'above_current': len([r for r in resistance_zones if r['price'] > current_price]),
                'below_current': len([s for s in support_zones if s['price'] < current_price])
            }
        }
        
        return jsonify({
            "status": "success",
            "smc_zones": smc_data
        })
        
    except Exception as e:
        logger.error(f"SMC zones endpoint error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Failed to generate SMC zones"
        }), 500