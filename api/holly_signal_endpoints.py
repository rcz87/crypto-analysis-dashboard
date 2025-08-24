"""
Holly-like High Probability Signal API Endpoints
"""

import logging
from flask import Blueprint, request, jsonify
from datetime import datetime
from typing import Dict, Any

from core.high_prob_signal_engine import HighProbSignalEngine
from auth import require_api_key

logger = logging.getLogger(__name__)

# Create blueprint
holly_signals_bp = Blueprint('holly_signals', __name__)

# Initialize the engine (will be done properly when integrated)
holly_engine = None

def init_holly_engine(okx_fetcher=None):
    """Initialize the Holly-like signal engine"""
    global holly_engine
    try:
        holly_engine = HighProbSignalEngine(okx_fetcher=okx_fetcher)
        logger.info("🎯 Holly Signal Engine initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Holly Signal Engine: {e}")

@holly_signals_bp.route('/api/holly/signal', methods=['GET'])
@require_api_key
def get_holly_signal():
    """
    Generate high probability signal using Holly-like backtesting approach
    
    Parameters:
    - symbol: Trading pair (e.g., BTC-USDT)
    - timeframe: Chart timeframe (1m, 5m, 15m, 1H, 4H, 1D) [default: 1H]
    """
    try:
        # Get parameters
        symbol = request.args.get('symbol', 'BTC-USDT').upper()
        timeframe = request.args.get('timeframe', '1H')
        
        # Validate parameters
        if not symbol:
            return jsonify({
                'error': 'MISSING_SYMBOL',
                'message': 'Symbol parameter is required'
            }), 400
        
        valid_timeframes = ['1m', '5m', '15m', '1H', '4H', '1D']
        if timeframe not in valid_timeframes:
            return jsonify({
                'error': 'INVALID_TIMEFRAME',
                'message': f'Timeframe must be one of: {valid_timeframes}'
            }), 400
        
        # Check if engine is initialized
        if not holly_engine:
            return jsonify({
                'error': 'ENGINE_NOT_INITIALIZED',
                'message': 'Holly Signal Engine is not available'
            }), 503
        
        # Generate signal
        signal_result = holly_engine.generate_high_prob_signal(symbol, timeframe)
        
        # Add metadata
        signal_result['api_version'] = '1.0'
        signal_result['generated_at'] = datetime.now().isoformat()
        signal_result['engine_type'] = 'holly_backtest'
        
        logger.info(f"Holly signal generated for {symbol}/{timeframe}: {signal_result.get('signal', {}).get('action', 'UNKNOWN')}")
        
        return jsonify(signal_result)
        
    except Exception as e:
        logger.error(f"Holly signal generation error: {e}")
        return jsonify({
            'error': 'SIGNAL_GENERATION_ERROR',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@holly_signals_bp.route('/api/holly/strategies', methods=['GET'])
@require_api_key
def get_strategy_rankings():
    """
    Get performance rankings of all available strategies
    
    Parameters:
    - symbol: Trading pair (e.g., BTC-USDT)
    - timeframe: Chart timeframe [default: 1H]
    """
    try:
        # Get parameters
        symbol = request.args.get('symbol', 'BTC-USDT').upper()
        timeframe = request.args.get('timeframe', '1H')
        
        # Check if engine is initialized
        if not holly_engine:
            return jsonify({
                'error': 'ENGINE_NOT_INITIALIZED',
                'message': 'Holly Signal Engine is not available'
            }), 503
        
        # Get strategy rankings
        rankings = holly_engine.get_strategy_rankings(symbol, timeframe)
        
        response = {
            'status': 'success',
            'symbol': symbol,
            'timeframe': timeframe,
            'total_strategies': len(rankings),
            'strategies': rankings,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Strategy rankings error: {e}")
        return jsonify({
            'error': 'RANKINGS_ERROR',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@holly_signals_bp.route('/api/holly/status', methods=['GET'])
@require_api_key
def get_holly_status():
    """Get Holly Signal Engine status and loaded strategies"""
    try:
        if not holly_engine:
            return jsonify({
                'status': 'engine_not_initialized',
                'available': False,
                'message': 'Holly Signal Engine is not available'
            })
        
        # Get engine status
        status = {
            'status': 'active',
            'available': True,
            'engine_info': {
                'lookback_days': holly_engine.lookback_days,
                'min_win_rate': holly_engine.min_win_rate,
                'min_risk_reward': holly_engine.min_risk_reward,
                'max_drawdown': holly_engine.max_drawdown
            },
            'strategies': {
                'total_loaded': len(holly_engine.strategies),
                'available_strategies': list(holly_engine.strategies.keys())
            },
            'features': {
                'multi_strategy_backtesting': True,
                'performance_based_selection': True,
                'risk_adjusted_signals': True,
                'strategy_rankings': True
            },
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(status)
        
    except Exception as e:
        logger.error(f"Holly status error: {e}")
        return jsonify({
            'status': 'error',
            'available': False,
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@holly_signals_bp.route('/api/holly/backtest', methods=['POST'])
@require_api_key
def run_strategy_backtest():
    """
    Run backtest for a specific strategy
    
    Body parameters:
    - symbol: Trading pair
    - timeframe: Chart timeframe
    - strategy: Strategy name to test
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'MISSING_DATA',
                'message': 'JSON body is required'
            }), 400
        
        symbol = data.get('symbol', 'BTC-USDT').upper()
        timeframe = data.get('timeframe', '1H')
        strategy_name = data.get('strategy')
        
        if not strategy_name:
            return jsonify({
                'error': 'MISSING_STRATEGY',
                'message': 'Strategy name is required'
            }), 400
        
        # Check if engine is initialized
        if not holly_engine:
            return jsonify({
                'error': 'ENGINE_NOT_INITIALIZED',
                'message': 'Holly Signal Engine is not available'
            }), 503
        
        # Check if strategy exists
        if strategy_name not in holly_engine.strategies:
            return jsonify({
                'error': 'STRATEGY_NOT_FOUND',
                'message': f'Strategy "{strategy_name}" not available. Available: {list(holly_engine.strategies.keys())}'
            }), 404
        
        # Get historical data
        historical_data = holly_engine._get_historical_data(symbol, timeframe)
        if historical_data.empty:
            return jsonify({
                'error': 'NO_DATA',
                'message': 'Unable to fetch historical data'
            }), 503
        
        # Run backtest for specific strategy
        strategy = holly_engine.strategies[strategy_name]
        result = holly_engine._backtest_strategy(strategy, historical_data, symbol, strategy_name)
        
        if not result:
            return jsonify({
                'status': 'failed',
                'message': f'Strategy "{strategy_name}" did not meet minimum performance criteria',
                'symbol': symbol,
                'timeframe': timeframe,
                'strategy': strategy_name
            })
        
        response = {
            'status': 'success',
            'symbol': symbol,
            'timeframe': timeframe,
            'strategy': strategy_name,
            'backtest_period': f'{holly_engine.lookback_days} days',
            'performance': result['performance'],
            'total_signals': len(result['signals']),
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Strategy backtest error: {e}")
        return jsonify({
            'error': 'BACKTEST_ERROR',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500