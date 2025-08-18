#!/usr/bin/env python3
"""
Institutional Endpoints - Kelas institusi dengan full compliance testing
"""
import logging
from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
import time

from core.institutional_signal_engine import InstitutionalSignalEngine
from core.okx_fetcher import OKXFetcher

logger = logging.getLogger(__name__)

# Create blueprint
institutional_bp = Blueprint('institutional', __name__, url_prefix='/api/institutional')

# Initialize components
institutional_engine = InstitutionalSignalEngine()
okx_fetcher = OKXFetcher()

def add_cors_headers(response):
    """Add CORS headers"""
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response

@institutional_bp.route('/signal', methods=['POST'])
@cross_origin()
def get_institutional_signal():
    """Generate institutional-grade trading signal"""
    try:
        data = request.get_json() or {}
        
        symbol = data.get('symbol', 'BTC-USDT').upper().replace('/', '-')
        if not symbol.endswith('-USDT'):
            symbol = f"{symbol.replace('-USDT', '').replace('USDT', '')}-USDT"
        
        timeframe = data.get('timeframe', data.get('tf', '1H'))
        position_size_usd = float(data.get('position_size_usd', 1000.0))
        
        # Get market data
        market_data = okx_fetcher.get_historical_data(symbol, timeframe, 100)
        orderbook_data = okx_fetcher.get_order_book(symbol, depth=20)
        
        # Get funding data
        funding_data = None
        try:
            funding_response = okx_fetcher.get_funding_rate(symbol)
            if 'error' not in funding_response:
                funding_data = funding_response
        except:
            pass
        
        # Generate institutional signal
        signal_result = institutional_engine.generate_institutional_signal(
            symbol=symbol,
            timeframe=timeframe,
            position_size_usd=position_size_usd,
            market_data={'current_price': 45000.0, 'atr': 0.025, 'volatility_regime': 'normal'},
            orderbook_data=orderbook_data if 'error' not in orderbook_data else None,
            funding_data=funding_data
        )
        
        return add_cors_headers(jsonify(signal_result))
        
    except Exception as e:
        logger.error(f"Institutional signal error: {e}")
        return add_cors_headers(jsonify({
            "status": "error",
            "message": str(e)
        })), 500

@institutional_bp.route('/status', methods=['GET'])
@cross_origin()
def get_institutional_status():
    """Get institutional system status"""
    try:
        status = institutional_engine.get_institutional_status()
        return add_cors_headers(jsonify(status))
        
    except Exception as e:
        logger.error(f"Institutional status error: {e}")
        return add_cors_headers(jsonify({
            "status": "error",
            "message": str(e)
        })), 500

@institutional_bp.route('/acceptance-test', methods=['POST'])
@cross_origin()
def run_acceptance_tests():
    """Run institutional acceptance criteria test suite"""
    try:
        test_results = institutional_engine.run_acceptance_test_suite()
        return add_cors_headers(jsonify(test_results))
        
    except Exception as e:
        logger.error(f"Acceptance test error: {e}")
        return add_cors_headers(jsonify({
            "status": "error",
            "message": str(e)
        })), 500

@institutional_bp.route('/smc-audit/<symbol>/<timeframe>', methods=['GET'])
@cross_origin()
def get_smc_audit(symbol, timeframe):
    """Get SMC state audit report"""
    try:
        audit_report = institutional_engine.smc_state_manager.get_audit_report(symbol, timeframe)
        return add_cors_headers(jsonify({
            "status": "success",
            "audit_report": audit_report,
            "timestamp": time.time()
        }))
        
    except Exception as e:
        logger.error(f"SMC audit error: {e}")
        return add_cors_headers(jsonify({
            "status": "error",
            "message": str(e)
        })), 500

@institutional_bp.route('/regime-analysis', methods=['POST'])
@cross_origin()
def analyze_regime():
    """Analyze current market regime"""
    try:
        data = request.get_json() or {}
        
        # Mock market data for regime analysis
        market_data = {
            'atr': data.get('atr', 0.025),
            'volatility': data.get('volatility', 'normal')
        }
        
        funding_data = {
            'funding_rate': data.get('funding_rate', 0.0001)
        } if 'funding_rate' in data else None
        
        regime_state = institutional_engine.regime_filter.analyze_regime(
            market_data=market_data,
            funding_data=funding_data
        )
        
        regime_summary = institutional_engine.regime_filter.get_regime_summary(regime_state)
        
        return add_cors_headers(jsonify({
            "status": "success",
            "regime_state": {
                "volatility_regime": regime_state.volatility_regime,
                "volatility_percentile": round(regime_state.volatility_percentile, 1),
                "funding_extreme": regime_state.funding_extreme,
                "regime_score": round(regime_state.regime_score, 1)
            },
            "regime_summary": regime_summary,
            "timestamp": time.time()
        }))
        
    except Exception as e:
        logger.error(f"Regime analysis error: {e}")
        return add_cors_headers(jsonify({
            "status": "error",
            "message": str(e)
        })), 500