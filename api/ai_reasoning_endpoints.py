#!/usr/bin/env python3
"""
AI Reasoning API Endpoints - REST API untuk Enhanced Reasoning Engine
Menyediakan endpoints untuk analisis trading dengan reasoning yang jelas dan akurat
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from flask import Blueprint, request, jsonify
import traceback

from core.ai_reasoning_integration import get_ai_reasoning_integrator
from core.enhanced_reasoning_engine import get_enhanced_reasoning_engine
from core.okx_fetcher import OKXFetcher
from core.professional_smc_analyzer import ProfessionalSMCAnalyzer
# from core.indicator_calculator import IndicatorCalculator  # Will create basic implementation

# Import enhanced systems for improved performance
from core.advanced_cache_manager import get_cache_manager
from core.response_compression import compress_large_response, compress_json_response
from core.enhanced_error_handler import get_error_handler, handle_api_error

# Setup logging
logger = logging.getLogger(__name__)

# Create Blueprint
ai_reasoning_bp = Blueprint('ai_reasoning', __name__, url_prefix='/api/ai-reasoning')

# Initialize components
ai_integrator = get_ai_reasoning_integrator()
reasoning_engine = get_enhanced_reasoning_engine()
okx_fetcher = OKXFetcher()
smc_analyzer = ProfessionalSMCAnalyzer()

# Initialize enhanced systems
cache_manager = get_cache_manager()
error_handler = get_error_handler()

@ai_reasoning_bp.route('/status', methods=['GET'])
def ai_reasoning_status():
    """AI Reasoning status - stub endpoint"""
    return jsonify({
        "status": "ok",
        "endpoint": "ai_reasoning", 
        "data": {
            "service": "AI Reasoning Engine",
            "version": "1.0.0",
            "features": ["comprehensive-analysis", "quick-analysis", "reasoning-stats"]
        }
    }), 200

def calculate_basic_technical_indicators(candles: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate basic technical indicators from candles data"""
    if not candles or len(candles) < 14:
        return {}
    
    try:
        closes = [float(candle['close']) for candle in candles]
        highs = [float(candle['high']) for candle in candles]
        lows = [float(candle['low']) for candle in candles]
        volumes = [float(candle['volume']) for candle in candles]
        
        # RSI calculation
        def calculate_rsi(prices, period=14):
            if len(prices) < period + 1:
                return 50.0
            
            gains = []
            losses = []
            
            for i in range(1, len(prices)):
                change = prices[i] - prices[i-1]
                if change > 0:
                    gains.append(change)
                    losses.append(0)
                else:
                    gains.append(0)
                    losses.append(-change)
            
            if len(gains) < period:
                return 50.0
            
            avg_gain = sum(gains[-period:]) / period
            avg_loss = sum(losses[-period:]) / period
            
            if avg_loss == 0:
                return 100.0
            
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            return rsi
        
        # Simple Moving Averages
        def calculate_sma(prices, period):
            if len(prices) < period:
                return prices[-1] if prices else 0
            return sum(prices[-period:]) / period
        
        # MACD calculation (simplified)
        def calculate_macd(prices):
            if len(prices) < 26:
                return {'macd': 0, 'signal': 0, 'histogram': 0}
            
            ema_12 = calculate_sma(prices, 12)
            ema_26 = calculate_sma(prices, 26)
            macd = ema_12 - ema_26
            signal = calculate_sma([macd], 9)
            histogram = macd - signal
            
            return {'macd': macd, 'signal': signal, 'histogram': histogram}
        
        # Calculate indicators
        current_price = closes[-1]
        rsi = calculate_rsi(closes)
        sma_20 = calculate_sma(closes, 20)
        sma_50 = calculate_sma(closes, 50)
        macd_data = calculate_macd(closes)
        
        # Volume analysis
        avg_volume = sum(volumes[-20:]) / min(20, len(volumes)) if volumes else 0
        volume_ratio = volumes[-1] / avg_volume if avg_volume > 0 else 1.0
        
        return {
            'rsi': rsi,
            'sma_20': sma_20,
            'sma_50': sma_50,
            'macd': macd_data['macd'],
            'macd_signal': macd_data['signal'],
            'macd_histogram': macd_data['histogram'],
            'current_price': current_price,
            'volume_ratio': volume_ratio,
            'price_vs_sma20': ((current_price - sma_20) / sma_20 * 100) if sma_20 > 0 else 0,
            'price_vs_sma50': ((current_price - sma_50) / sma_50 * 100) if sma_50 > 0 else 0
        }
        
    except Exception as e:
        logger.error(f"Error calculating basic indicators: {e}")
        return {}

@ai_reasoning_bp.route('/analyze', methods=['GET', 'POST'])
@compress_large_response
def analyze_trading_opportunity():
    """
    Comprehensive trading opportunity analysis dengan enhanced reasoning
    
    Request Body:
    {
        "symbol": "BTC-USDT",
        "timeframe": "1H",
        "include_smc": true,
        "include_indicators": true,
        "use_ai_enhancement": true
    }
    """
    try:
        # Support both GET and POST
        if request.method == 'POST':
            data = request.get_json() or {}
        else:
            data = {}
        
        # Extract parameters (support both methods)
        symbol = data.get('symbol', request.args.get('symbol', 'BTC-USDT'))
        timeframe = data.get('timeframe', request.args.get('timeframe', '1H'))
        include_smc = data.get('include_smc', request.args.get('include_smc', 'true').lower() == 'true')
        include_indicators = data.get('include_indicators', request.args.get('include_indicators', 'true').lower() == 'true')
        use_ai_enhancement = data.get('use_ai_enhancement', request.args.get('use_ai_enhancement', 'true').lower() == 'true')
        
        logger.info(f"🔍 Starting AI reasoning analysis for {symbol} {timeframe}")
        
        # 1. Check cache first for market data
        cache_key_params = {'symbol': symbol, 'timeframe': timeframe, 'limit': 100}
        cached_data = cache_manager.get('market_data', f"{symbol}_{timeframe}", cache_key_params)
        
        if cached_data:
            logger.info(f"🗄️ Cache hit for {symbol} {timeframe}")
            market_data = cached_data
        else:
            # Fetch market data from OKX
            market_data = okx_fetcher.get_historical_data(symbol, timeframe, limit=100)
            if not market_data or 'candles' not in market_data:
                return handle_api_error(
                    'DATA_FETCH_FAILED',
                    f'Gagal mengambil data market untuk {symbol}',
                    {'symbol': symbol, 'timeframe': timeframe},
                    status_code=400
                )
            
            # Cache the successful data
            cache_manager.set('market_data', f"{symbol}_{timeframe}", market_data, ttl=30, params=cache_key_params)
        
        # 2. Prepare analysis data
        analysis_data = {
            'market_data': market_data,
            'smc_analysis': {},
            'technical_indicators': {},
            'symbol': symbol,
            'timeframe': timeframe
        }
        
        # 3. SMC Analysis (optional)
        if include_smc:
            try:
                # Convert candles to DataFrame for SMC analysis
                import pandas as pd
                candles_df = pd.DataFrame(market_data['candles'])
                if not candles_df.empty:
                    # Use analyze_market_structure method 
                    smc_result = smc_analyzer.analyze_market_structure({'candles': market_data['candles']})
                    analysis_data['smc_analysis'] = smc_result
                    logger.info(f"✅ SMC analysis completed for {symbol}")
            except Exception as e:
                logger.error(f"SMC analysis error: {e}")
                analysis_data['smc_analysis'] = {'error': str(e)}
        
        # 4. Technical Indicators (optional)
        if include_indicators:
            try:
                # Basic technical indicators implementation
                indicators = calculate_basic_technical_indicators(market_data['candles'])
                analysis_data['technical_indicators'] = indicators
                logger.info(f"✅ Technical indicators calculated for {symbol}")
            except Exception as e:
                logger.error(f"Technical indicators error: {e}")
                analysis_data['technical_indicators'] = {'error': str(e)}
        
        # 5. Configure AI enhancement
        original_setting = ai_integrator.use_ai_enhancement
        ai_integrator.use_ai_enhancement = use_ai_enhancement
        
        # 6. Perform comprehensive analysis
        try:
            analysis_result = ai_integrator.analyze_trading_opportunity(
                market_data=analysis_data['market_data'],
                smc_analysis=analysis_data['smc_analysis'],
                technical_indicators=analysis_data['technical_indicators'],
                symbol=symbol,
                timeframe=timeframe
            )
            
            # Restore original setting
            ai_integrator.use_ai_enhancement = original_setting
            
            logger.info(f"✅ AI reasoning analysis completed for {symbol} - {analysis_result['reasoning_result']['conclusion']}")
            
            return jsonify({
                'success': True,
                'symbol': symbol,
                'timeframe': timeframe,
                'analysis': analysis_result,
                'data_sources': {
                    'market_data_available': bool(market_data),
                    'smc_analysis_included': include_smc and 'error' not in analysis_data['smc_analysis'],
                    'technical_indicators_included': include_indicators and 'error' not in analysis_data['technical_indicators'],
                    'ai_enhancement_used': use_ai_enhancement
                },
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            # Restore original setting
            ai_integrator.use_ai_enhancement = original_setting
            raise e
        
    except Exception as e:
        logger.error(f"Error in AI reasoning analysis: {e}")
        logger.error(traceback.format_exc())
        error_symbol = 'unknown'
        error_timeframe = 'unknown'
        try:
            request_data = request.get_json() if request else None
            if request_data:
                error_symbol = request_data.get('symbol', 'unknown')
                error_timeframe = request_data.get('timeframe', 'unknown')
        except:
            pass
            
        return jsonify({
            'error': 'Analysis failed',
            'message': str(e),
            'symbol': error_symbol,
            'timeframe': error_timeframe
        }), 500

@ai_reasoning_bp.route('/quick-analysis', methods=['GET', 'POST'])
@compress_large_response
def quick_analysis():
    """
    Quick trading analysis dengan basic reasoning
    
    Request Body:
    {
        "symbol": "BTC-USDT",
        "timeframe": "1H"
    }
    """
    try:
        # Support both GET and POST
        if request.method == 'POST':
            data = request.get_json() or {}
        else:
            data = {}
        
        symbol = data.get('symbol', request.args.get('symbol', 'BTC-USDT'))
        timeframe = data.get('timeframe', request.args.get('timeframe', '1H'))
        
        logger.info(f"⚡ Starting quick analysis for {symbol} {timeframe}")
        
        # Check cache first for quick analysis
        cache_key_params = {'symbol': symbol, 'timeframe': timeframe, 'limit': 50}
        cached_data = cache_manager.get('market_data', f"quick_{symbol}_{timeframe}", cache_key_params)
        
        if cached_data:
            logger.info(f"🗄️ Quick analysis cache hit for {symbol} {timeframe}")
            market_data = cached_data
        else:
            # Fetch basic market data
            market_data = okx_fetcher.get_historical_data(symbol, timeframe, limit=50)
            if not market_data or 'candles' not in market_data:
                return handle_api_error(
                    'DATA_FETCH_FAILED',
                    f'Gagal mengambil data untuk quick analysis {symbol}',
                    {'symbol': symbol, 'timeframe': timeframe},
                    status_code=400
                )
            
            # Cache with shorter TTL for quick analysis
            cache_manager.set('market_data', f"quick_{symbol}_{timeframe}", market_data, ttl=15, params=cache_key_params)
        
        # Basic technical indicators
        try:
            basic_indicators = calculate_basic_technical_indicators(market_data['candles'])
        except Exception as e:
            logger.error(f"Basic indicators error: {e}")
            basic_indicators = {}
        
        # Quick AI reasoning analysis
        analysis_result = ai_integrator.analyze_trading_opportunity(
            market_data=market_data,
            smc_analysis={},  # No SMC for quick analysis
            technical_indicators=basic_indicators,
            symbol=symbol,
            timeframe=timeframe
        )
        
        # Simplified response
        quick_result = {
            'symbol': symbol,
            'timeframe': timeframe,
            'conclusion': analysis_result['reasoning_result']['conclusion'],
            'confidence': analysis_result['reasoning_result']['confidence_score'],
            'confidence_level': analysis_result['reasoning_result']['confidence'],
            'summary': analysis_result['narrative'][:200] + '...' if len(analysis_result['narrative']) > 200 else analysis_result['narrative'],
            'recommendation': analysis_result['recommendation']['action'],
            'risk_level': analysis_result['recommendation']['risk_level'],
            'key_evidence': analysis_result['reasoning_result']['evidence'][:3],  # Top 3 evidence
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"⚡ Quick analysis completed for {symbol} - {quick_result['conclusion']}")
        
        return jsonify({
            'success': True,
            'result': quick_result
        })
        
    except Exception as e:
        logger.error(f"Error in quick analysis: {e}")
        error_symbol = 'unknown'
        error_timeframe = 'unknown'
        try:
            request_data = request.get_json() if request else None
            if request_data:
                error_symbol = request_data.get('symbol', 'unknown')
                error_timeframe = request_data.get('timeframe', 'unknown')
        except:
            pass
        return handle_api_error(
            'AI_ANALYSIS_FAILED',
            f'Quick analysis gagal untuk {error_symbol}',
            {'symbol': error_symbol, 'timeframe': error_timeframe, 'error_detail': str(e)},
            exception=e,
            status_code=500
        )

@ai_reasoning_bp.route('/reasoning-stats', methods=['GET'])
def get_reasoning_statistics():
    """Get AI reasoning engine statistics"""
    try:
        stats = ai_integrator.get_reasoning_statistics()
        
        return jsonify({
            'success': True,
            'statistics': stats,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting reasoning stats: {e}")
        return jsonify({
            'error': 'Failed to get statistics',
            'message': str(e)
        }), 500

@ai_reasoning_bp.route('/configure', methods=['POST'])
def configure_reasoning_engine():
    """
    Configure AI reasoning engine settings
    
    Request Body:
    {
        "min_confidence_threshold": 60,
        "use_ai_enhancement": true,
        "reasoning_confidence_threshold": 50
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Configuration data required'}), 400
        
        # Update configuration
        updated_config = ai_integrator.update_configuration(data)
        
        return jsonify({
            'success': True,
            'updated_configuration': updated_config,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error updating configuration: {e}")
        return jsonify({
            'error': 'Configuration update failed',
            'message': str(e)
        }), 500

@ai_reasoning_bp.route('/test-reasoning', methods=['POST'])
def test_reasoning_engine():
    """
    Test reasoning engine dengan sample data
    
    Request Body:
    {
        "test_type": "basic",  // basic, comprehensive, stress
        "symbol": "BTC-USDT"
    }
    """
    try:
        data = request.get_json() or {}
        test_type = data.get('test_type', 'basic')
        symbol = data.get('symbol', 'BTC-USDT')
        
        logger.info(f"🧪 Running {test_type} reasoning test for {symbol}")
        
        # Create test data based on type
        if test_type == 'basic':
            test_market_data = {
                'candles': [
                    {'open': 50000, 'high': 50500, 'low': 49500, 'close': 50200, 'volume': 1000},
                    {'open': 50200, 'high': 50800, 'low': 50000, 'close': 50600, 'volume': 1200},
                    {'open': 50600, 'high': 51000, 'low': 50400, 'close': 50800, 'volume': 1100}
                ]
            }
            test_indicators = {
                'rsi': 65.5,
                'macd': 150.2,
                'macd_signal': 140.8,
                'ema_20': 50400,
                'ema_50': 50200
            }
            test_smc = {
                'market_bias': 'bullish',
                'structure_break': 'bos_up',
                'order_blocks': [{'price': 50000, 'type': 'bullish'}]
            }
        
        elif test_type == 'comprehensive':
            # More complex test data
            test_market_data = {
                'candles': [
                    {'open': 50000, 'high': 50500, 'low': 49500, 'close': 50200, 'volume': 1000},
                    {'open': 50200, 'high': 50800, 'low': 50000, 'close': 50600, 'volume': 1200},
                    {'open': 50600, 'high': 51000, 'low': 50400, 'close': 50800, 'volume': 1100},
                    {'open': 50800, 'high': 51200, 'low': 50700, 'close': 51000, 'volume': 1300},
                    {'open': 51000, 'high': 51500, 'low': 50900, 'close': 51300, 'volume': 1500}
                ]
            }
            test_indicators = {
                'rsi': 72.3,
                'macd': 200.5,
                'macd_signal': 180.2,
                'ema_20': 50800,
                'ema_50': 50500,
                'bb_upper': 51500,
                'bb_lower': 50000,
                'stoch_k': 85.2,
                'stoch_d': 80.1
            }
            test_smc = {
                'market_bias': 'bullish',
                'structure_break': 'bos_up',
                'order_blocks': [
                    {'price': 50000, 'type': 'bullish', 'strength': 'strong'},
                    {'price': 50600, 'type': 'bullish', 'strength': 'medium'}
                ],
                'fvg_zones': [{'high': 50900, 'low': 50700, 'type': 'bullish'}],
                'liquidity_sweeps': True
            }
        
        else:  # stress test
            # Test dengan data yang challenging
            test_market_data = {
                'candles': [
                    {'open': 50000, 'high': 50100, 'low': 49900, 'close': 50000, 'volume': 500},  # Doji
                    {'open': 50000, 'high': 50200, 'low': 49800, 'close': 49900, 'volume': 600},  # Red
                    {'open': 49900, 'high': 50100, 'low': 49700, 'close': 50050, 'volume': 550}   # Mixed
                ]
            }
            test_indicators = {
                'rsi': 50.0,  # Neutral
                'macd': 5.2,
                'macd_signal': 5.0,  # Very close values
                'ema_20': 50000,
                'ema_50': 50000  # Flat trend
            }
            test_smc = {
                'market_bias': 'neutral',
                'structure_break': 'none',
                'order_blocks': [],
                'fvg_zones': [],
                'liquidity_sweeps': False
            }
        
        # Run reasoning test
        analysis_result = ai_integrator.analyze_trading_opportunity(
            market_data=test_market_data,
            smc_analysis=test_smc,
            technical_indicators=test_indicators,
            symbol=symbol,
            timeframe='1H'
        )
        
        # Evaluate test results
        test_evaluation = {
            'test_passed': analysis_result['reasoning_result']['confidence_score'] > 0,
            'reasoning_quality': analysis_result['analysis_quality']['quality_level'],
            'evidence_count': len(analysis_result['reasoning_result']['evidence']),
            'uncertainty_acknowledged': len(analysis_result['reasoning_result']['uncertainty_factors']) > 0,
            'actionable_recommendation': analysis_result['recommendation']['action'] != 'HOLD' if analysis_result['reasoning_result']['confidence_score'] > 60 else True
        }
        
        logger.info(f"🧪 {test_type.title()} reasoning test completed - Quality: {test_evaluation['reasoning_quality']}")
        
        return jsonify({
            'success': True,
            'test_type': test_type,
            'test_evaluation': test_evaluation,
            'analysis_result': analysis_result,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in reasoning test: {e}")
        return jsonify({
            'error': 'Reasoning test failed',
            'message': str(e)
        }), 500

@ai_reasoning_bp.route('/health', methods=['GET'])
def health_check():
    """Health check for AI reasoning endpoints"""
    try:
        # Test basic functionality
        stats = reasoning_engine.get_reasoning_statistics()
        
        health_status = {
            'status': 'healthy',
            'components': {
                'enhanced_reasoning_engine': True,
                'ai_integrator': True,
                'okx_fetcher': okx_fetcher is not None,
                'smc_analyzer': smc_analyzer is not None,
                'basic_indicators': True
            },
            'reasoning_stats': {
                'total_analyses': stats.get('total_analyses', 0),
                'openai_available': stats.get('openai_available', False),
                'confidence_threshold': stats.get('confidence_threshold', 50)
            },
            'timestamp': datetime.now().isoformat()
        }
        
        # Check if any critical component is missing
        critical_components = ['enhanced_reasoning_engine', 'ai_integrator']
        all_critical_healthy = all(health_status['components'][comp] for comp in critical_components)
        
        if not all_critical_healthy:
            health_status['status'] = 'degraded'
        
        return jsonify(health_status)
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# Error handlers
@ai_reasoning_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Endpoint not found',
        'available_endpoints': [
            '/api/v1/ai-reasoning/analyze',
            '/api/v1/ai-reasoning/quick-analysis', 
            '/api/v1/ai-reasoning/reasoning-stats',
            '/api/v1/ai-reasoning/configure',
            '/api/v1/ai-reasoning/test-reasoning',
            '/api/v1/ai-reasoning/health'
        ]
    }), 404

@ai_reasoning_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred in AI reasoning service'
    }), 500

# Performance and monitoring endpoints
@ai_reasoning_bp.route('/cache-stats', methods=['GET'])
def get_cache_statistics():
    """Get comprehensive cache statistics"""
    try:
        stats = cache_manager.get_comprehensive_stats()
        return compress_json_response({
            'success': True,
            'cache_stats': stats,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return handle_api_error(
            'SYSTEM_ERROR',
            'Gagal mengambil statistik cache',
            {'error_detail': str(e)},
            exception=e
        )

@ai_reasoning_bp.route('/compression-stats', methods=['GET']) 
def get_compression_statistics():
    """Get response compression statistics"""
    try:
        from core.response_compression import get_compression_stats
        stats = get_compression_stats()
        return compress_json_response({
            'success': True,
            'compression_stats': stats,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return handle_api_error(
            'SYSTEM_ERROR',
            'Gagal mengambil statistik kompresi',
            {'error_detail': str(e)},
            exception=e
        )

@ai_reasoning_bp.route('/error-stats', methods=['GET'])
def get_error_statistics():
    """Get error handling statistics"""
    try:
        stats = error_handler.get_error_stats()
        return compress_json_response({
            'success': True,
            'error_stats': stats,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return handle_api_error(
            'SYSTEM_ERROR',
            'Gagal mengambil statistik error',
            {'error_detail': str(e)},
            exception=e
        )

@ai_reasoning_bp.route('/system-performance', methods=['GET'])
def get_system_performance():
    """Get comprehensive system performance metrics"""
    try:
        # Get all stats
        cache_stats = cache_manager.get_comprehensive_stats()
        
        from core.response_compression import get_compression_stats
        compression_stats = get_compression_stats()
        
        error_stats = error_handler.get_error_stats()
        
        # Calculate overall performance score
        cache_hit_rate_str = cache_stats.get('overall_hit_rate', '0%')
        if isinstance(cache_hit_rate_str, str):
            cache_hit_rate = float(cache_hit_rate_str.replace('%', ''))
        else:
            cache_hit_rate = float(cache_hit_rate_str)
            
        compression_rate_str = compression_stats.get('compression_rate', '0%')
        if isinstance(compression_rate_str, str):
            compression_rate = float(compression_rate_str.replace('%', ''))
        else:
            compression_rate = float(compression_rate_str)
            
        error_rate = error_stats.get('total_errors', 0)
        
        performance_score = min(100, 
            (cache_hit_rate * 0.4) + 
            (compression_rate * 0.3) + 
            (max(0, 100 - error_rate) * 0.3)
        )
        
        return compress_json_response({
            'success': True,
            'performance_overview': {
                'performance_score': f"{performance_score:.1f}/100",
                'cache_efficiency': cache_stats.get('overall_hit_rate', '0%'),
                'compression_efficiency': compression_stats.get('compression_rate', '0%'),
                'total_errors': error_stats.get('total_errors', 0),
                'system_status': 'optimal' if performance_score > 80 else 'good' if performance_score > 60 else 'needs_attention'
            },
            'detailed_stats': {
                'cache': cache_stats,
                'compression': compression_stats,
                'errors': error_stats
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return handle_api_error(
            'SYSTEM_ERROR',
            'Gagal mengambil performa sistem',
            {'error_detail': str(e)},
            exception=e
        )

@ai_reasoning_bp.route('/cache-clear', methods=['POST'])
def clear_cache():
    """Clear cache pools with optional pool selection"""
    try:
        data = request.get_json() or {}
        pool_name = data.get('pool', 'all')
        
        if pool_name == 'all':
            cache_manager.clear_all()
            cleared_pools = 'all pools'
        else:
            cache_manager.clear_pool(pool_name)
            cleared_pools = f'pool: {pool_name}'
        
        logger.info(f"🗑️ Cache cleared - {cleared_pools}")
        
        return compress_json_response({
            'success': True,
            'message': f'Cache berhasil dihapus: {cleared_pools}',
            'cleared_pools': cleared_pools,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return handle_api_error(
            'SYSTEM_ERROR',
            'Gagal menghapus cache',
            {'error_detail': str(e)},
            exception=e
        )

logger.info("🧠 AI Reasoning API endpoints initialized - Enhanced reasoning untuk trading analysis")