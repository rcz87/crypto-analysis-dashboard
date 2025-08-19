#!/usr/bin/env python3
"""
Chart Endpoints for TradingView Widget Integration
Provides chart data and SMC overlay information
"""

from flask import Blueprint, request, jsonify
from core.professional_smc_analyzer import ProfessionalSMCAnalyzer
from core.okx_fetcher import OKXFetcher
# from core.indicator_calculator import IndicatorCalculator  # Not needed for basic chart functionality
from core.enhanced_ai_engine import EnhancedAIEngine
import logging
from typing import Dict, List, Any
from datetime import datetime

logger = logging.getLogger(__name__)

chart_bp = Blueprint('chart', __name__)

class ChartDataProvider:
    """Provides chart data and SMC analysis for TradingView integration"""
    
    def __init__(self):
        self.okx_fetcher = OKXFetcher()
        self.smc_analyzer = ProfessionalSMCAnalyzer()
        # self.indicator_calc = IndicatorCalculator()  # Will use existing endpoints
        try:
            self.ai_engine = EnhancedAIEngine()
        except Exception as e:
            logger.warning(f"AI engine unavailable: {e}")
            self.ai_engine = None
        logger.info("📊 Chart Data Provider initialized")
    
    def get_chart_data(self, symbol: str, timeframe: str = '1H', limit: int = 200) -> Dict[str, Any]:
        """Get OHLCV data formatted for TradingView"""
        try:
            # Convert symbol format for OKX
            okx_symbol = symbol.replace('/', '-') if '/' in symbol else symbol.replace('USDT', '-USDT')
            
            # Get market data using existing method
            market_data = self.okx_fetcher.get_historical_data(okx_symbol, timeframe, limit)
            
            if market_data is None or (isinstance(market_data, dict) and 'candles' not in market_data):
                return {'error': 'No market data available'}
            
            candles = market_data['candles']
            
            # Format for TradingView
            chart_data = []
            for candle in candles:
                chart_data.append({
                    'time': int(candle['timestamp']),
                    'open': float(candle['open']),
                    'high': float(candle['high']),
                    'low': float(candle['low']),
                    'close': float(candle['close']),
                    'volume': float(candle['volume'])
                })
            
            return {
                'status': 'success',
                'symbol': symbol,
                'timeframe': timeframe,
                'data': chart_data,
                'count': len(chart_data)
            }
            
        except Exception as e:
            logger.error(f"Error getting chart data for {symbol}: {e}")
            return {'error': str(e)}
    
    def get_smc_overlays(self, symbol: str, timeframe: str = '1H') -> Dict[str, Any]:
        """Get SMC analysis data for chart overlays"""
        try:
            # Convert symbol format
            okx_symbol = symbol.replace('/', '-') if '/' in symbol else symbol.replace('USDT', '-USDT')
            
            # Get market data for SMC analysis using existing method
            market_data = self.okx_fetcher.get_historical_data(okx_symbol, timeframe, 200)
            
            if market_data is None or (isinstance(market_data, dict) and 'candles' not in market_data):
                return {'error': 'No market data for SMC analysis'}
            
            # Run SMC analysis using existing method
            smc_result = self.smc_analyzer.analyze_market_structure(market_data['candles'])
            
            # Format overlays for TradingView
            overlays = {
                'order_blocks': [],
                'fair_value_gaps': [],
                'liquidity_levels': [],
                'trend_lines': [],
                'support_resistance': []
            }
            
            # Process Order Blocks
            if 'order_blocks' in smc_result:
                for ob_type, blocks in smc_result['order_blocks'].items():
                    for block in blocks:
                        overlays['order_blocks'].append({
                            'type': ob_type,
                            'high': block.get('high', 0),
                            'low': block.get('low', 0),
                            'timestamp': block.get('timestamp', 0),
                            'strength': block.get('strength', 'medium'),
                            'color': '#4caf50' if ob_type == 'bullish' else '#f44336'
                        })
            
            # Process Fair Value Gaps
            if 'fair_value_gaps' in smc_result:
                for fvg in smc_result['fair_value_gaps']:
                    overlays['fair_value_gaps'].append({
                        'high': fvg.get('high', 0),
                        'low': fvg.get('low', 0),
                        'timestamp': fvg.get('timestamp', 0),
                        'type': fvg.get('type', 'neutral'),
                        'color': '#2196f3'
                    })
            
            # Process Liquidity Levels
            if 'liquidity_sweep' in smc_result:
                sweep = smc_result['liquidity_sweep']
                if sweep.get('detected'):
                    overlays['liquidity_levels'].append({
                        'price': sweep.get('price', 0),
                        'type': sweep.get('type', 'unknown'),
                        'strength': sweep.get('strength', 'medium'),
                        'timestamp': sweep.get('timestamp', 0),
                        'color': '#ff9800'
                    })
            
            # Add current price levels
            current_price = market_data['candles'][-1]['close'] if market_data['candles'] else 0
            
            return {
                'status': 'success',
                'symbol': symbol,
                'timeframe': timeframe,
                'overlays': overlays,
                'current_price': current_price,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting SMC overlays for {symbol}: {e}")
            return {'error': str(e)}

# Initialize provider
chart_provider = ChartDataProvider()

@chart_bp.route('/widget')
def trading_widget():
    """Serve the TradingView widget HTML page"""
    try:
        with open('static/tradingview_widget.html', 'r') as f:
            html_content = f.read()
        return html_content
    except FileNotFoundError:
        return jsonify({'error': 'Widget HTML file not found'}), 404

@chart_bp.route('/dashboard')
def smc_dashboard():
    """Serve the SMC Dashboard HTML page"""
    try:
        with open('static/smc_dashboard.html', 'r') as f:
            html_content = f.read()
        return html_content
    except FileNotFoundError:
        return jsonify({'error': 'SMC Dashboard HTML file not found'}), 404

@chart_bp.route('/data')
def chart_data():
    """Get chart OHLCV data"""
    symbol = request.args.get('symbol', 'BTCUSDT')
    timeframe = request.args.get('timeframe', '1H')
    limit = int(request.args.get('limit', 200))
    
    logger.info(f"📊 Chart data request: {symbol} {timeframe}")
    
    result = chart_provider.get_chart_data(symbol, timeframe, limit)
    return jsonify(result)

@chart_bp.route('/smc-overlays')
def smc_overlays():
    """Get SMC analysis overlays for chart"""
    symbol = request.args.get('symbol', 'BTCUSDT')
    timeframe = request.args.get('timeframe', '1H')
    
    logger.info(f"🎯 SMC overlays request: {symbol} {timeframe}")
    
    result = chart_provider.get_smc_overlays(symbol, timeframe)
    return jsonify(result)

@chart_bp.route('/symbols')
def available_symbols():
    """Get list of available trading symbols"""
    symbols = [
        {'symbol': 'BTCUSDT', 'name': 'Bitcoin', 'category': 'crypto'},
        {'symbol': 'ETHUSDT', 'name': 'Ethereum', 'category': 'crypto'},
        {'symbol': 'SOLUSDT', 'name': 'Solana', 'category': 'crypto'},
        {'symbol': 'ADAUSDT', 'name': 'Cardano', 'category': 'crypto'},
        {'symbol': 'DOGEUSDT', 'name': 'Dogecoin', 'category': 'crypto'},
        {'symbol': 'AVAXUSDT', 'name': 'Avalanche', 'category': 'crypto'},
        {'symbol': 'DOTUSDT', 'name': 'Polkadot', 'category': 'crypto'},
        {'symbol': 'LINKUSDT', 'name': 'Chainlink', 'category': 'crypto'},
        {'symbol': 'UNIUSDT', 'name': 'Uniswap', 'category': 'crypto'},
        {'symbol': 'LTCUSDT', 'name': 'Litecoin', 'category': 'crypto'}
    ]
    
    return jsonify({
        'status': 'success',
        'symbols': symbols,
        'count': len(symbols)
    })

@chart_bp.route('/health')
def chart_health():
    """Chart service health check"""
    return jsonify({
        'status': 'operational',
        'service': 'Chart Data Provider',
        'features': [
            'TradingView widget integration',
            'SMC overlay analysis',
            'Real-time OKX data',
            'Multi-timeframe support'
        ],
        'timestamp': datetime.now().isoformat()
    })

logger.info("📊 Chart endpoints initialized")