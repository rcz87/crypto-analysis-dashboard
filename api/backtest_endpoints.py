#!/usr/bin/env python3
"""
Backtest API Endpoints
Strategy backtesting with performance analytics
"""

import logging
import asyncio
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from typing import Dict, Any

# Setup logging
logger = logging.getLogger(__name__)

backtest_api = Blueprint('backtest_api', __name__)

def get_backtest_engine():
    """Get or create backtest engine instance"""
    try:
        from core.backtesting_engine import BacktestingEngine
        return BacktestingEngine()
    except ImportError as e:
        logger.error(f"Backtesting engine not available: {e}")
        return None

@backtest_api.route('/api/backtest', methods=['GET', 'POST'])
def run_strategy_backtest():
    """
    Run strategy backtest dengan historical data
    
    Parameters:
    - strategy: trading strategy (RSI_MACD, SMA_CROSSOVER, BREAKOUT)
    - symbol: trading pair (default: BTC-USDT)
    - start_date: start date (YYYY-MM-DD)
    - end_date: end date (YYYY-MM-DD) 
    - timeframe: timeframe (1H, 4H, 1D)
    - initial_balance: starting balance (default: 10000)
    """
    try:
        # Get backtest engine
        engine = get_backtest_engine()
        if not engine:
            return jsonify({
                "status": "error",
                "error": "BACKTEST_UNAVAILABLE",
                "message": "Backtesting engine not available"
            }), 503
        
        # Get parameters
        strategy = request.args.get('strategy', 'RSI_MACD')
        symbol = request.args.get('symbol', 'BTC-USDT')
        timeframe = request.args.get('timeframe', '1H')
        initial_balance = float(request.args.get('initial_balance', 10000))
        
        # Date parameters
        end_date = request.args.get('end_date', datetime.now().strftime('%Y-%m-%d'))
        start_date = request.args.get('start_date', 
                                    (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
        
        # Validate strategy
        valid_strategies = ['RSI_MACD', 'SMA_CROSSOVER', 'BREAKOUT', 'ML_ENSEMBLE']
        if strategy not in valid_strategies:
            return jsonify({
                "status": "error",
                "error": "INVALID_STRATEGY",
                "message": f"Strategy must be one of: {', '.join(valid_strategies)}",
                "available_strategies": valid_strategies
            }), 400
        
        # Run backtest
        logger.info(f"Starting backtest: {strategy} on {symbol} from {start_date} to {end_date}")
        
        result = engine.run_backtest(
            strategy=strategy,
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            timeframe=timeframe,
            initial_balance=initial_balance
        )
        
        if 'error' in result:
            return jsonify({
                "status": "error",
                "error": "BACKTEST_FAILED", 
                "message": result['error'],
                "parameters": {
                    "strategy": strategy,
                    "symbol": symbol,
                    "start_date": start_date,
                    "end_date": end_date,
                    "timeframe": timeframe
                }
            }), 400
        
        # Add metadata
        result['metadata'] = {
            "strategy": strategy,
            "symbol": symbol,
            "timeframe": timeframe,
            "period": f"{start_date} to {end_date}",
            "initial_balance": initial_balance,
            "generated_at": datetime.now().isoformat()
        }
        
        return jsonify({
            "status": "success",
            "data": result
        })
        
    except ValueError as e:
        logger.error(f"Backtest parameter error: {e}")
        return jsonify({
            "status": "error",
            "error": "INVALID_PARAMETERS",
            "message": str(e)
        }), 400
    except Exception as e:
        logger.error(f"Backtest error: {e}")
        return jsonify({
            "status": "error", 
            "error": "INTERNAL_ERROR",
            "message": "Internal server error during backtesting"
        }), 500

@backtest_api.route('/api/backtest/strategies', methods=['GET'])
def get_available_strategies():
    """Get list of available trading strategies"""
    try:
        strategies = {
            "RSI_MACD": {
                "name": "RSI + MACD Strategy",
                "description": "Combined RSI oversold/overbought with MACD crossover signals",
                "indicators": ["RSI", "MACD"],
                "timeframes": ["1H", "4H", "1D"],
                "risk_level": "Medium"
            },
            "SMA_CROSSOVER": {
                "name": "Simple Moving Average Crossover",
                "description": "Buy on golden cross (SMA20 > SMA50), sell on death cross",
                "indicators": ["SMA20", "SMA50"],
                "timeframes": ["1H", "4H", "1D"],
                "risk_level": "Low"
            },
            "BREAKOUT": {
                "name": "Bollinger Bands Breakout",
                "description": "Trade breakouts above/below Bollinger Bands",
                "indicators": ["Bollinger Bands"],
                "timeframes": ["1H", "4H"],
                "risk_level": "High"
            },
            "ML_ENSEMBLE": {
                "name": "Machine Learning Ensemble",
                "description": "AI-powered predictions using multiple ML models",
                "indicators": ["Multiple AI Models"],
                "timeframes": ["1H", "4H"],
                "risk_level": "Medium-High"
            }
        }
        
        return jsonify({
            "status": "success",
            "data": {
                "strategies": strategies,
                "total_count": len(strategies),
                "default_parameters": {
                    "initial_balance": 10000,
                    "timeframe": "1H",
                    "period_days": 30
                }
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting strategies: {e}")
        return jsonify({
            "status": "error",
            "message": "Failed to get available strategies"
        }), 500

@backtest_api.route('/api/backtest/quick', methods=['GET'])
def quick_backtest():
    """Quick backtest dengan parameter default untuk demo"""
    try:
        # Get engine
        engine = get_backtest_engine()
        if not engine:
            return jsonify({
                "status": "error",
                "message": "Backtesting engine not available",
                "demo_data": {
                    "strategy": "RSI_MACD",
                    "performance": {
                        "total_return_pct": 15.8,
                        "win_rate_pct": 68.2,
                        "max_drawdown_pct": 8.5,
                        "total_trades": 24
                    },
                    "note": "Demo data - backtesting engine unavailable"
                }
            })
        
        # Quick backtest dengan BTC-USDT, RSI_MACD, 7 hari terakhir
        symbol = request.args.get('symbol', 'BTC-USDT')
        strategy = request.args.get('strategy', 'RSI_MACD')
        days = int(request.args.get('days', 7))
        
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        result = engine.run_backtest(
            strategy=strategy,
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            timeframe='1H',
            initial_balance=10000
        )
        
        return jsonify({
            "status": "success",
            "data": result
        })
        
    except Exception as e:
        logger.error(f"Quick backtest error: {e}")
        return jsonify({
            "status": "error",
            "message": "Quick backtest failed",
            "demo_result": {
                "performance": {
                    "total_return_pct": 12.4,
                    "win_rate_pct": 65.0,
                    "sharpe_ratio": 1.8,
                    "max_drawdown_pct": 6.2
                },
                "note": "Demo data due to error"
            }
        }), 500

# Error handlers
@backtest_api.errorhandler(404)
def not_found(error):
    return jsonify({
        "status": "error",
        "error": "NOT_FOUND",
        "message": "Backtest endpoint not found",
        "available_endpoints": [
            "GET /api/backtest - Run strategy backtest",
            "GET /api/backtest/strategies - Get available strategies", 
            "GET /api/backtest/quick - Quick demo backtest"
        ]
    }), 404

@backtest_api.errorhandler(500)
def internal_error(error):
    return jsonify({
        "status": "error",
        "error": "INTERNAL_ERROR", 
        "message": "Internal backtest error"
    }), 500