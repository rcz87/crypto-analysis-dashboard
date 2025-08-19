# gpts_routes.py
from flask import Blueprint, jsonify, request
import os
from sqlalchemy import create_engine
import logging
from core.okx_fetcher import OKXFetcher
from core.ai_engine import get_ai_engine
from core.professional_smc_analyzer import ProfessionalSMCAnalyzer
from core.signal_generator import SignalGenerator
from core.crypto_news_analyzer import get_news_analyzer
import asyncio
from typing import Any, Dict, List

try:
    import pandas as pd
except Exception:
    pd = None

gpts_api = Blueprint('gpts_api', __name__, url_prefix='/api/gpts')
logger = logging.getLogger(__name__)

# Inisialisasi komponen
smc_analyzer = ProfessionalSMCAnalyzer()
signal_generator = SignalGenerator()

# Helper
ALLOWED_TFS = {"1m","5m","15m","30m","1H","4H","1D"}

def normalize_symbol(sym: str) -> str:
    s = (sym or "").upper()
    if "-" in s:
        return s
    if s.endswith("USDT"):
        return s.replace("USDT", "-USDT")
    return f"{s}-USDT"

def validate_tf(tf: str) -> bool:
    return tf in ALLOWED_TFS

def normalize_candles(market_data: Any) -> List[Dict[str, Any]]:
    # Jika sudah format {'candles': [...]}
    if isinstance(market_data, dict) and 'candles' in market_data:
        return market_data.get('candles') or []

    # Jika list of dict
    if isinstance(market_data, list) and (len(market_data) == 0 or isinstance(market_data[0], dict)):
        return market_data

    # Jika pandas DataFrame
    if pd is not None and isinstance(market_data, pd.DataFrame):
        df = market_data
        out = []
        # Coba map kolom umum
        for _, row in df.iterrows():
            c = {}
            def getf(name, alt=None):
                if name in df.columns: return float(row[name])
                if alt and alt in df.columns: return float(row[alt])
                return None
            c['open'] = getf('open','o')
            c['high'] = getf('high','h')
            c['low'] = getf('low','l')
            c['close'] = getf('close','c')
            c['volume'] = getf('volume','v') or 0.0
            # timestamp
            if 'timestamp' in df.columns: c['timestamp'] = row['timestamp']
            elif 'time' in df.columns: c['timestamp'] = row['time']
            else: c['timestamp'] = _
            if all(k in c and c[k] is not None for k in ['open','high','low','close']):
                out.append(c)
        return out

    return []

@gpts_api.route('/status', methods=['GET'])
def get_status():
    try:
        okx_fetcher = OKXFetcher()
        okx_status = "available"
        okx_details = {}
        try:
            md = okx_fetcher.get_historical_data("BTC-USDT", "1m", 2)
            candles = normalize_candles(md)
            okx_details["data_available"] = bool(candles)
        except Exception as e:
            okx_status = "unavailable"
            okx_details["error"] = str(e)
        
        ai_engine = get_ai_engine()
        ai_test = ai_engine.test_connection()
        openai_status = "available" if ai_test.get("available", False) else "unavailable"
        
        db_status = "unavailable"
        db_details = {}
        db_url = os.environ.get("DATABASE_URL")
        if db_url:
            try:
                engine = create_engine(db_url)
                with engine.connect() as conn:
                    conn.execute("SELECT 1")
                db_status = "available"
            except Exception as e:
                db_details["error"] = str(e)
        
        version_info = {
            "api_version": "1.0.0",
            "core_version": "1.2.3",
            "supported_symbols": ["BTC", "ETH", "SOL", "ADA", "DOT", "AVAX", "LINK", "UNI", "DOGE"],
            "supported_timeframes": sorted(list(ALLOWED_TFS))
        }
        
        features = {
            "smc_analysis": True,
            "news_sentiment": True,
            "multi_timeframe": True,
            "openai_integration": ai_engine.is_available(),
            "telegram_notifications": bool(os.environ.get("TELEGRAM_BOT_TOKEN")),
            "performance_tracking": bool(os.environ.get("DATABASE_URL"))
        }
        
        return jsonify({
            "status": "operational",
            "components": {
                "okx_api": {"status": okx_status, **okx_details},
                "openai": {"status": openai_status, "model": "gpt-4o", "client_available": ai_engine.is_available()},
                "database": {"status": db_status, **db_details}
            },
            "version": version_info,
            "features": features
        })
    except Exception as e:
        logger.error(f"Error in status endpoint: {e}")
        return jsonify({"status": "error", "message": "Failed to retrieve system status", "error": str(e)}), 500

@gpts_api.route('/sinyal/tajam', methods=['POST'])
def get_tajam_signal():
    try:
        data = request.get_json(silent=True) or {}
        symbol = (data.get('symbol') or 'BTC').upper()
        timeframe = data.get('timeframe', '1H')
        if not validate_tf(timeframe):
            return jsonify({"status": "error", "message": f"Invalid timeframe: {timeframe}"}), 400
        
        okx_symbol = normalize_symbol(symbol)
        okx_fetcher = OKXFetcher()
        raw_md = okx_fetcher.get_historical_data(okx_symbol, timeframe, 200)
        candles = normalize_candles(raw_md)
        if not candles:
            return jsonify({"status": "error", "message": f"Failed to get market data for {symbol} {timeframe}"}), 400
        
        smc_result = smc_analyzer.analyze_market_structure(candles)
        signal_result = signal_generator.generate_signal({'candles': candles}, smc_result, is_concise=True)
        
        current_price = candles[-1].get('close', 0) if candles else 0
        
        return jsonify({
            "status": "success",
            "symbol": symbol,
            "timeframe": timeframe,
            "current_price": float(current_price),
            "signal": {
                "bias": signal_result.get('bias', 'NEUTRAL'),
                "strength": signal_result.get('strength', 0),
                "action": signal_result.get('action', 'WAIT'),
                "confidence": signal_result.get('confidence', 0),
                "entry_zone": {"low": signal_result.get('entry_low', 0), "high": signal_result.get('entry_high', 0)},
                "stop_loss": signal_result.get('stop_loss', 0),
                "take_profit": signal_result.get('take_profit', 0)
            },
            "key_drivers": signal_result.get('key_drivers', []),
            "generated_at": signal_result.get('timestamp', None)
        })
        
    except Exception as e:
        logger.error(f"Error generating tajam signal: {e}")
        return jsonify({"status": "error", "message": "Failed to generate signal", "error": str(e)}), 500

@gpts_api.route('/sinyal/enhanced', methods=['POST'])
def get_enhanced_signal():
    try:
        data = request.get_json(silent=True) or {}
        symbol = (data.get('symbol') or 'BTC').upper()
        timeframe = data.get('timeframe', '1H')
        include_news = bool(data.get('include_news', True))
        include_narrative = bool(data.get('include_narrative', True))
        
        if not validate_tf(timeframe):
            return jsonify({"status": "error", "message": f"Invalid timeframe: {timeframe}"}), 400
        
        okx_symbol = normalize_symbol(symbol)
        okx_fetcher = OKXFetcher()
        raw_md = okx_fetcher.get_historical_data(okx_symbol, timeframe, 200)
        candles = normalize_candles(raw_md)
        if not candles:
            return jsonify({"status": "error", "message": f"Failed to get market data for {symbol} {timeframe}"}), 400
        
        smc_result = smc_analyzer.analyze_market_structure(candles)
        signal_result = signal_generator.generate_signal({'candles': candles}, smc_result, is_concise=False)
        
        news_context = {}
        if include_news:
            try:
                news_analyzer = get_news_analyzer()
                result = asyncio.run(asyncio.wait_for(news_analyzer.get_news_sentiment(limit=5), timeout=25))
                if result['status'] == 'success':
                    agg = result['aggregate']
                    news_context = {
                        "overall_sentiment": agg['overall_sentiment'],
                        "sentiment_strength": agg['average_confidence'],
                        "high_impact_count": agg['high_impact_news'],
                        "bullish_ratio": agg['bullish_ratio'],
                        "bearish_ratio": agg['bearish_ratio'],
                        "top_news": result['data'][:3]
                    }
            except asyncio.TimeoutError:
                logger.warning("News sentiment timeout")
                news_context = {"error": "News analysis timeout"}
            except Exception as news_error:
                logger.warning(f"Failed to include news data: {news_error}")
                news_context = {"error": "News data unavailable"}
        
        narrative = ""
        if include_narrative:
            try:
                ai_engine = get_ai_engine()
                analysis_data = {
                    "candlestick": candles,
                    "smc_analysis": smc_result,
                    "signal_result": signal_result,
                    "news_context": news_context if news_context else {},
                    "confluence_summary": signal_result.get('confluence', {})
                }
                narrative = ai_engine.generate_ai_snapshot(okx_symbol, timeframe, analysis_data)
            except Exception as ai_error:
                logger.warning(f"Failed to generate narrative: {ai_error}")
                narrative = f"AI narrative unavailable: {str(ai_error)}"
        
        current_price = candles[-1].get('close', 0) if candles else 0
        
        return jsonify({
            "status": "success",
            "symbol": symbol,
            "timeframe": timeframe,
            "current_price": float(current_price),
            "signal": {
                "bias": signal_result.get('bias', 'NEUTRAL'),
                "strength": signal_result.get('strength', 0),
                "action": signal_result.get('action', 'WAIT'),
                "confidence": signal_result.get('confidence', 0),
                "entry_zone": {"low": signal_result.get('entry_low', 0), "high": signal_result.get('entry_high', 0)},
                "stop_loss": signal_result.get('stop_loss', 0),
                "take_profit": signal_result.get('take_profit', 0),
                "risk_reward": signal_result.get('risk_reward', 0)
            },
            "analysis": {
                "market_structure": signal_result.get('market_structure', 'NEUTRAL'),
                "trend_strength": signal_result.get('trend_strength', 0),
                "volatility": signal_result.get('volatility', "NORMAL"),
                "key_levels": signal_result.get('key_levels', []),
                "indicators": signal_result.get('indicators', {}),
                "smc": {
                    "ob_count": len(smc_result.get('order_blocks', {}).get('bullish', [])) + len(smc_result.get('order_blocks', {}).get('bearish', [])),
                    "fvg_count": len(smc_result.get('fair_value_gaps', [])),
                    "liquidity_sweep": smc_result.get('liquidity_sweep', {}).get('detected', False)
                }
            },
            "news_context": news_context if include_news else {},
            "confluence": signal_result.get('confluence', {}),
            "narrative": narrative if include_narrative else "",
            "generated_at": signal_result.get('timestamp', None)
        })
        
    except Exception as e:
        logger.error(f"Error generating enhanced signal: {e}")
        return jsonify({"status": "error", "message": "Failed to generate enhanced signal", "error": str(e)}), 500
