#!/usr/bin/env python3
"""
Self-Improvement API Endpoints - Auto-tuning dan model retraining
"""
from flask import Blueprint, jsonify, request
import logging
import time
from typing import Dict, Any

from core.self_improvement_engine import SelfImprovementEngine
from core.data_sanity_checker import DataSanityChecker

logger = logging.getLogger(__name__)

# Create blueprint
improvement_bp = Blueprint('improvement', __name__, url_prefix='/api/improvement')

# Initialize engines
improvement_engine = SelfImprovementEngine()
data_sanity = DataSanityChecker()

@improvement_bp.route('/auto-tune', methods=['POST'])
def auto_tune():
    """
    Automatic system tuning - threshold optimization dan model retraining
    """
    try:
        request_data = request.get_json() or {}
        symbols = request_data.get('symbols', ['BTC-USDT', 'ETH-USDT', 'SOL-USDT'])
        
        # Perform auto-tuning
        results = improvement_engine.auto_tune_system(symbols)
        
        return jsonify({
            'status': 'success',
            'tuning_results': results,
            'timestamp': time.time(),
            'symbols_processed': results.get('symbols_processed', []),
            'summary': results.get('summary', {})
        })
        
    except Exception as e:
        logger.error(f"Auto-tune error: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': time.time()
        }), 500

@improvement_bp.route('/retrain-model', methods=['POST'])
def retrain_model():
    """
    Manual model retraining
    """
    try:
        request_data = request.get_json() or {}
        force_retrain = request_data.get('force_retrain', False)
        
        # Retrain confluence model
        performance = improvement_engine.retrain_confluence_model(force_retrain)
        
        return jsonify({
            'status': 'success',
            'model_performance': {
                'model_name': performance.model_name,
                'accuracy': performance.accuracy,
                'precision': performance.precision,
                'recall': performance.recall,
                'f1_score': performance.f1_score,
                'sample_size': performance.sample_size,
                'training_date': performance.training_date
            },
            'feature_importance': performance.feature_importance,
            'timestamp': time.time()
        })
        
    except Exception as e:
        logger.error(f"Model retraining error: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': time.time()
        }), 500

@improvement_bp.route('/optimize-threshold/<symbol>/<timeframe>', methods=['POST'])
def optimize_threshold(symbol: str, timeframe: str):
    """
    Optimize threshold untuk specific symbol/timeframe
    """
    try:
        # Optimize threshold
        optimization = improvement_engine.optimize_thresholds(symbol, timeframe)
        
        return jsonify({
            'status': 'success',
            'optimization': {
                'symbol': optimization.symbol,
                'timeframe': optimization.timeframe,
                'current_threshold': optimization.current_threshold,
                'optimal_threshold': optimization.optimal_threshold,
                'improvement_score': optimization.improvement_score,
                'win_rate_before': optimization.win_rate_before,
                'win_rate_after': optimization.win_rate_after,
                'sample_size': optimization.sample_size,
                'confidence': optimization.confidence
            },
            'timestamp': time.time()
        })
        
    except Exception as e:
        logger.error(f"Threshold optimization error for {symbol}: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e),
            'symbol': symbol,
            'timeframe': timeframe,
            'timestamp': time.time()
        }), 500

@improvement_bp.route('/status', methods=['GET'])
def improvement_status():
    """
    Get self-improvement system status
    """
    try:
        status = improvement_engine.get_improvement_status()
        
        return jsonify({
            'status': 'success',
            'improvement_status': status,
            'timestamp': time.time()
        })
        
    except Exception as e:
        logger.error(f"Improvement status error: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': time.time()
        }), 500

@improvement_bp.route('/improved-score', methods=['POST'])
def get_improved_score():
    """
    Get improved confluence score using trained model
    """
    try:
        request_data = request.get_json() or {}
        
        # Validate required features
        required_features = ['smc_score', 'orderbook_score', 'volatility_score', 'momentum_score']
        features = {}
        
        for feature in required_features:
            if feature not in request_data:
                return jsonify({
                    'status': 'error',
                    'message': f'Missing required feature: {feature}'
                }), 400
            features[feature] = float(request_data[feature])
        
        # Optional features
        features['funding_score'] = request_data.get('funding_score', 50.0)
        features['news_score'] = request_data.get('news_score', 50.0)
        
        # Get improved score
        improved_score, explanation = improvement_engine.get_improved_confluence_score(features)
        
        return jsonify({
            'status': 'success',
            'improved_score': improved_score,
            'explanation': explanation,
            'input_features': features,
            'timestamp': time.time()
        })
        
    except Exception as e:
        logger.error(f"Improved score calculation error: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': time.time()
        }), 500

@improvement_bp.route('/data-quality', methods=['POST'])
def validate_data_quality():
    """
    Validate market data quality
    """
    try:
        request_data = request.get_json() or {}
        
        if 'data' not in request_data:
            return jsonify({
                'status': 'error',
                'message': 'Missing data field'
            }), 400
        
        data_source = request_data.get('data_source', 'unknown')
        market_data = request_data['data']
        request_timestamp = request_data.get('request_timestamp', time.time())
        
        # Validate data quality
        quality_report = data_sanity.validate_market_data(
            market_data, data_source, request_timestamp
        )
        
        # Check if signal should be blocked
        should_block, reason = data_sanity.should_block_signal(quality_report)
        
        # Get fallback recommendations
        fallback_rec = data_sanity.get_fallback_recommendation(quality_report)
        
        return jsonify({
            'status': 'success',
            'quality_report': {
                'data_source': quality_report.data_source,
                'quality_score': quality_report.quality_score,
                'issues': quality_report.issues,
                'is_stale': quality_report.is_stale,
                'staleness_seconds': quality_report.staleness_seconds,
                'has_gaps': quality_report.has_gaps,
                'has_nans': quality_report.has_nans,
                'latency_ms': quality_report.latency_ms,
                'fallback_used': quality_report.fallback_used
            },
            'signal_blocking': {
                'should_block': should_block,
                'reason': reason
            },
            'fallback_recommendation': fallback_rec,
            'timestamp': time.time()
        })
        
    except Exception as e:
        logger.error(f"Data quality validation error: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': time.time()
        }), 500

@improvement_bp.route('/data-quality-summary', methods=['GET'])
def data_quality_summary():
    """
    Get data quality summary for specified period
    """
    try:
        hours = int(request.args.get('hours', 24))
        
        summary = data_sanity.get_quality_summary(hours)
        
        return jsonify({
            'status': 'success',
            'quality_summary': summary,
            'timestamp': time.time()
        })
        
    except Exception as e:
        logger.error(f"Data quality summary error: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': time.time()
        }), 500