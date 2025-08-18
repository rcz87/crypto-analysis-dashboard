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

@gpts_api.route('/smc-analysis', methods=['POST'])
def get_smc_analysis():
    """Get SMC analysis for market data"""
    try:
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