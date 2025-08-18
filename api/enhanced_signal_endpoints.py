#!/usr/bin/env python3
"""
Enhanced Signal Endpoints - Production-ready dengan quality components
Menggunakan EnhancedSharpSignalEngine untuk sinyal berkualitas tinggi
"""
import logging
from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
import time

from core.enhanced_sharp_signal_engine import EnhancedSharpSignalEngine
from core.okx_fetcher import OKXFetcher
from core.professional_smc_analyzer import ProfessionalSMCAnalyzer

logger = logging.getLogger(__name__)

# Create blueprint
enhanced_signals_bp = Blueprint('enhanced_signals', __name__, url_prefix='/api/enhanced')

# Initialize components
enhanced_engine = EnhancedSharpSignalEngine()
okx_fetcher = OKXFetcher()
smc_analyzer = ProfessionalSMCAnalyzer()

def add_cors_headers(response):
    """Add CORS headers for GPT access"""
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, User-Agent'
    return response

@enhanced_signals_bp.route('/sharp-signal', methods=['POST'])
@cross_origin()
def get_enhanced_sharp_signal():
    """Get enhanced sharp signal with full quality pipeline"""
    try:
        data = request.get_json() or {}
        
        # Extract parameters
        symbol = data.get('symbol', 'BTC-USDT').upper().replace('/', '-')
        if not symbol.endswith('-USDT'):
            symbol = f"{symbol.replace('-USDT', '').replace('USDT', '')}-USDT"
        
        timeframe = data.get('timeframe', data.get('tf', '1H'))
        position_size_usd = float(data.get('position_size_usd', 1000.0))
        
        logger.info(f"Enhanced sharp signal request: {symbol} {timeframe}")
        
        # Get market data
        market_data = okx_fetcher.get_historical_data(symbol, timeframe, 100)
        if not market_data:
            return add_cors_headers(jsonify({
                "status": "error",
                "message": "Failed to fetch market data"
            })), 500
        
        # Get orderbook data
        orderbook_data = okx_fetcher.get_order_book(symbol, depth=20)
        if 'error' in orderbook_data:
            return add_cors_headers(jsonify({
                "status": "error", 
                "message": "Failed to fetch orderbook data"
            })), 500
        
        # Get SMC analysis
        smc_analysis = smc_analyzer.analyze_market_structure(market_data)
        
        # Get funding data (optional)
        funding_data = None
        try:
            funding_response = okx_fetcher.get_funding_rate(symbol)
            if 'error' not in funding_response:
                funding_data = funding_response
        except:
            pass
        
        # Generate enhanced signal
        signal_result = enhanced_engine.generate_enhanced_signal(
            symbol=symbol,
            smc_analysis=smc_analysis,
            orderbook_data=orderbook_data,
            market_data={'current_price': 45000.0, 'volatility_regime': 'normal', 'momentum': {'strength': 0.7}},
            funding_data=funding_data,
            position_size_usd=position_size_usd
        )
        
        return add_cors_headers(jsonify(signal_result))
        
    except Exception as e:
        logger.error(f"Enhanced sharp signal error: {e}")
        return add_cors_headers(jsonify({
            "status": "error",
            "message": str(e)
        })), 500

@enhanced_signals_bp.route('/system-status', methods=['GET'])
@cross_origin()
def get_system_status():
    """Get comprehensive system status"""
    try:
        status = enhanced_engine.get_system_status()
        return add_cors_headers(jsonify({
            "status": "success",
            "system_status": status,
            "timestamp": time.time()
        }))
        
    except Exception as e:
        logger.error(f"System status error: {e}")
        return add_cors_headers(jsonify({
            "status": "error",
            "message": str(e)
        })), 500

@enhanced_signals_bp.route('/record-outcome', methods=['POST'])
@cross_origin() 
def record_trade_outcome():
    """Record trade outcome for learning"""
    try:
        data = request.get_json() or {}
        
        trade_id = data.get('trade_id')
        outcome = data.get('outcome')  # win/loss
        exit_price = float(data.get('exit_price', 0))
        pnl = float(data.get('pnl', 0))
        
        if not trade_id or not outcome:
            return add_cors_headers(jsonify({
                "status": "error",
                "message": "Missing required fields: trade_id, outcome"
            })), 400
        
        enhanced_engine.record_signal_outcome(trade_id, outcome, exit_price, pnl)
        
        return add_cors_headers(jsonify({
            "status": "success",
            "message": f"Trade outcome recorded: {trade_id} -> {outcome}"
        }))
        
    except Exception as e:
        logger.error(f"Record outcome error: {e}")
        return add_cors_headers(jsonify({
            "status": "error",
            "message": str(e)
        })), 500

@enhanced_signals_bp.route('/circuit-breaker/status', methods=['GET'])
@cross_origin()
def get_circuit_breaker_status():
    """Get detailed circuit breaker status"""
    try:
        status = enhanced_engine.circuit_breaker.get_status()
        
        return add_cors_headers(jsonify({
            "status": "success",
            "circuit_breaker": {
                "state": status.state.value,
                "reason": status.reason,
                "triggered_at": status.triggered_at,
                "recovery_at": status.recovery_at,
                "consecutive_losses": status.consecutive_losses,
                "daily_drawdown_pct": round(status.daily_drawdown, 2),
                "total_signals_today": status.total_signals_today,
                "blocked_signals_count": status.blocked_signals_count
            },
            "timestamp": time.time()
        }))
        
    except Exception as e:
        logger.error(f"Circuit breaker status error: {e}")
        return add_cors_headers(jsonify({
            "status": "error",
            "message": str(e)
        })), 500

@enhanced_signals_bp.route('/circuit-breaker/reset', methods=['POST'])
@cross_origin()
def reset_circuit_breaker():
    """Manually reset circuit breaker"""
    try:
        enhanced_engine.circuit_breaker.force_reset("Manual API reset")
        
        return add_cors_headers(jsonify({
            "status": "success",
            "message": "Circuit breaker has been reset"
        }))
        
    except Exception as e:
        logger.error(f"Circuit breaker reset error: {e}")
        return add_cors_headers(jsonify({
            "status": "error",
            "message": str(e)
        })), 500

@enhanced_signals_bp.route('/performance', methods=['GET'])
@cross_origin()
def get_performance_metrics():
    """Get recent performance metrics"""
    try:
        days = min(int(request.args.get('days', 30)), 90)
        performance = enhanced_engine.trade_logger.get_recent_performance(days)
        
        return add_cors_headers(jsonify({
            "status": "success",
            "performance": performance,
            "period_days": days,
            "timestamp": time.time()
        }))
        
    except Exception as e:
        logger.error(f"Performance metrics error: {e}")
        return add_cors_headers(jsonify({
            "status": "error", 
            "message": str(e)
        })), 500