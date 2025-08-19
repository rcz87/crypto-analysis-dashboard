"""
Stateful AI Signal Engine - API Endpoints
Endpoint untuk tracking signal history, GPT queries, dan user interactions
"""

import json
import logging
import time
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin

# Import services
try:
    from services.state_manager import get_state_manager
except ImportError:
    # Fallback untuk state manager jika module tidak tersedia
    def get_state_manager():
        class FallbackStateManager:
            def get_signal_history(self, limit=50):
                return {"signals": [], "total": 0, "status": "fallback_mode"}
            def get_gpt_query_logs(self, limit=50):
                return {"queries": [], "total": 0, "status": "fallback_mode"}
            def get_user_interactions(self, limit=50):
                return {"interactions": [], "total": 0, "status": "fallback_mode"}
        return FallbackStateManager()
from core.redis_manager import redis_manager

logger = logging.getLogger(__name__)

# Blueprint untuk state management endpoints
state_api = Blueprint('state_api', __name__, url_prefix='/api/gpts/state')


def add_cors_headers(response):
    """Add CORS headers untuk ChatGPT integration"""
    if hasattr(response, 'headers'):
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response


def add_api_metadata(data):
    """Add standard API metadata"""
    return {
        **data,
        "api_version": "1.0.0",
        "server_time": datetime.now().isoformat(),
        "data_source": "Stateful AI Signal Engine"
    }


def get_request_context():
    """Extract request context untuk logging"""
    return {
        'user_agent': request.headers.get('User-Agent'),
        'ip_address': request.remote_addr,
        'referer': request.headers.get('Referer'),
        'session_id': request.headers.get('X-Session-ID', f"sess_{int(time.time())}")
    }


# ============================================================================
# SIGNAL TRACKING ENDPOINTS
# ============================================================================

@state_api.route('/track-signal', methods=['POST'])
@cross_origin()
def track_signal():
    """
    Track signal yang dihasilkan oleh AI engine
    Body: {
        "signal_data": {...},
        "source": "ChatGPT/API/Telegram"
    }
    """
    try:
        start_time = time.time()
        data = request.get_json() or {}
        
        # Validate input
        if 'signal_data' not in data:
            return add_cors_headers(jsonify({
                "error": "MISSING_SIGNAL_DATA",
                "message": "signal_data is required in request body",
                "api_version": "1.0.0",
                "server_time": datetime.now().isoformat()
            })), 400
        
        signal_data = data['signal_data']
        source = data.get('source', 'API')
        
        # Get state manager
        state_manager = get_state_manager(redis_manager.redis_client)
        
        # Save signal history
        signal_id = state_manager.save_signal_history(
            signal_data, 
            get_request_context()
        )
        
        # Track user interaction jika ada
        if source:
            interaction_data = {
                'type': 'SIGNAL_GENERATED',
                'source': source.upper(),
                'data': {'generation_source': source}
            }
            
            interaction_id = state_manager.track_user_interaction(
                signal_id,
                interaction_data,
                get_request_context()
            )
        
        processing_time = int((time.time() - start_time) * 1000)
        
        response_data = add_api_metadata({
            "success": True,
            "signal_id": signal_id,
            "message": "Signal tracked successfully",
            "processing_time_ms": processing_time
        })
        
        return add_cors_headers(jsonify(response_data))
        
    except Exception as e:
        logger.error(f"❌ Track signal error: {e}")
        return add_cors_headers(jsonify({
            "error": "TRACK_SIGNAL_FAILED",
            "message": "Failed to track signal",
            "details": str(e),
            "api_version": "1.0.0",
            "server_time": datetime.now().isoformat()
        })), 500


@state_api.route('/signal-history', methods=['GET'])
@cross_origin()
def get_signal_history():
    """
    Ambil history signal dengan filter
    Query params: limit, symbol, timeframe, days
    """
    try:
        # Parse query parameters
        limit = min(int(request.args.get('limit', 50)), 100)  # Max 100
        symbol = request.args.get('symbol', '').upper()
        timeframe = request.args.get('timeframe', '')
        days = int(request.args.get('days', 7))
        
        # Calculate date filter
        date_from = datetime.now() - timedelta(days=days) if days > 0 else None
        
        # Get state manager
        state_manager = get_state_manager(redis_manager.redis_client)
        
        # Get signal history
        signals = state_manager.get_signal_history(
            limit=limit,
            symbol=symbol if symbol else None,
            timeframe=timeframe if timeframe else None,
            date_from=date_from
        )
        
        response_data = add_api_metadata({
            "signals": signals,
            "total_returned": len(signals),
            "filters": {
                "limit": limit,
                "symbol": symbol if symbol else "all",
                "timeframe": timeframe if timeframe else "all",
                "days": days
            }
        })
        
        return add_cors_headers(jsonify(response_data))
        
    except Exception as e:
        logger.error(f"❌ Get signal history error: {e}")
        return add_cors_headers(jsonify({
            "error": "SIGNAL_HISTORY_FAILED",
            "message": "Failed to get signal history",
            "details": str(e),
            "api_version": "1.0.0",
            "server_time": datetime.now().isoformat()
        })), 500


@state_api.route('/signal/<signal_id>/execute', methods=['POST'])
@cross_origin()
def execute_signal(signal_id):
    """
    Mark signal sebagai executed
    Body: {
        "execution_price": 45000.0,
        "source": "TELEGRAM/API/MANUAL",
        "user_id": "optional"
    }
    """
    try:
        data = request.get_json() or {}
        
        # Get state manager
        state_manager = get_state_manager(redis_manager.redis_client)
        
        # Update signal execution
        execution_data = {
            'execution_price': data.get('execution_price'),
            'source': data.get('source', 'API')
        }
        
        success = state_manager.update_signal_execution(signal_id, execution_data)
        
        if not success:
            return add_cors_headers(jsonify({
                "error": "SIGNAL_NOT_FOUND",
                "message": f"Signal {signal_id} not found",
                "api_version": "1.0.0",
                "server_time": datetime.now().isoformat()
            })), 404
        
        # Track execution interaction
        interaction_data = {
            'type': 'EXECUTE',
            'source': data.get('source', 'API').upper(),
            'data': execution_data,
            'user_id': data.get('user_id')
        }
        
        interaction_id = state_manager.track_user_interaction(
            signal_id,
            interaction_data,
            get_request_context()
        )
        
        response_data = add_api_metadata({
            "success": True,
            "signal_id": signal_id,
            "interaction_id": interaction_id,
            "message": "Signal execution tracked successfully"
        })
        
        return add_cors_headers(jsonify(response_data))
        
    except Exception as e:
        logger.error(f"❌ Execute signal error: {e}")
        return add_cors_headers(jsonify({
            "error": "EXECUTE_SIGNAL_FAILED",
            "message": "Failed to track signal execution",
            "details": str(e),
            "api_version": "1.0.0",
            "server_time": datetime.now().isoformat()
        })), 500


# ============================================================================
# GPT QUERY LOGGING ENDPOINTS
# ============================================================================

@state_api.route('/log-query', methods=['POST'])
@cross_origin()
def log_gpt_query():
    """
    Log GPT query dan response untuk analytics
    Body: {
        "query_data": {...},
        "response_data": {...}
    }
    """
    try:
        data = request.get_json() or {}
        
        if 'query_data' not in data or 'response_data' not in data:
            return add_cors_headers(jsonify({
                "error": "MISSING_DATA",
                "message": "query_data and response_data are required",
                "api_version": "1.0.0",
                "server_time": datetime.now().isoformat()
            })), 400
        
        # Get state manager
        state_manager = get_state_manager(redis_manager.redis_client)
        
        # Log query
        query_id = state_manager.log_gpt_query(
            data['query_data'],
            data['response_data'],
            get_request_context()
        )
        
        response_data = add_api_metadata({
            "success": True,
            "query_id": query_id,
            "message": "GPT query logged successfully"
        })
        
        return add_cors_headers(jsonify(response_data))
        
    except Exception as e:
        logger.error(f"❌ Log GPT query error: {e}")
        return add_cors_headers(jsonify({
            "error": "LOG_QUERY_FAILED",
            "message": "Failed to log GPT query",
            "details": str(e),
            "api_version": "1.0.0",
            "server_time": datetime.now().isoformat()
        })), 500


# ============================================================================
# ANALYTICS ENDPOINTS
# ============================================================================

@state_api.route('/analytics/signals', methods=['GET'])
@cross_origin()
def get_signal_analytics():
    """
    Ambil analytics untuk signal performance
    Query params: days (default 30)
    """
    try:
        days = int(request.args.get('days', 30))
        
        # Get state manager
        state_manager = get_state_manager(redis_manager.redis_client)
        
        # Get analytics
        stats = state_manager.get_signal_performance_stats(days)
        
        response_data = add_api_metadata({
            "analytics": stats,
            "period_description": f"Last {days} days"
        })
        
        return add_cors_headers(jsonify(response_data))
        
    except Exception as e:
        logger.error(f"❌ Get signal analytics error: {e}")
        return add_cors_headers(jsonify({
            "error": "ANALYTICS_FAILED",
            "message": "Failed to get signal analytics",
            "details": str(e),
            "api_version": "1.0.0",
            "server_time": datetime.now().isoformat()
        })), 500


@state_api.route('/analytics/queries', methods=['GET'])
@cross_origin()
def get_query_analytics():
    """
    Ambil analytics untuk GPT queries
    Query params: days (default 7)
    """
    try:
        days = int(request.args.get('days', 7))
        
        # Get state manager
        state_manager = get_state_manager(redis_manager.redis_client)
        
        # Get analytics
        stats = state_manager.get_query_analytics(days)
        
        response_data = add_api_metadata({
            "analytics": stats,
            "period_description": f"Last {days} days"
        })
        
        return add_cors_headers(jsonify(response_data))
        
    except Exception as e:
        logger.error(f"❌ Get query analytics error: {e}")
        return add_cors_headers(jsonify({
            "error": "ANALYTICS_FAILED",
            "message": "Failed to get query analytics",
            "details": str(e),
            "api_version": "1.0.0",
            "server_time": datetime.now().isoformat()
        })), 500


@state_api.route('/analytics/interactions', methods=['GET'])
@cross_origin()
def get_interaction_analytics():
    """
    Ambil analytics untuk user interactions
    Query params: days (default 7)
    """
    try:
        days = int(request.args.get('days', 7))
        
        # Get state manager
        state_manager = get_state_manager(redis_manager.redis_client)
        
        # Get analytics
        stats = state_manager.get_user_interaction_stats(days)
        
        response_data = add_api_metadata({
            "analytics": stats,
            "period_description": f"Last {days} days"
        })
        
        return add_cors_headers(jsonify(response_data))
        
    except Exception as e:
        logger.error(f"❌ Get interaction analytics error: {e}")
        return add_cors_headers(jsonify({
            "error": "ANALYTICS_FAILED",
            "message": "Failed to get interaction analytics",
            "details": str(e),
            "api_version": "1.0.0",
            "server_time": datetime.now().isoformat()
        })), 500


# ============================================================================
# MAINTENANCE ENDPOINTS
# ============================================================================

@state_api.route('/maintenance/cleanup', methods=['POST'])
@cross_origin()
def cleanup_old_data():
    """
    Cleanup data lama untuk maintenance
    Body: {
        "days_to_keep": 90  // default 90 days
    }
    """
    try:
        data = request.get_json() or {}
        days_to_keep = data.get('days_to_keep', 90)
        
        # Get state manager
        state_manager = get_state_manager(redis_manager.redis_client)
        
        # Cleanup
        cleanup_result = state_manager.cleanup_old_data(days_to_keep)
        
        response_data = add_api_metadata({
            "success": True,
            "cleanup_result": cleanup_result,
            "message": f"Cleaned up data older than {days_to_keep} days"
        })
        
        return add_cors_headers(jsonify(response_data))
        
    except Exception as e:
        logger.error(f"❌ Cleanup error: {e}")
        return add_cors_headers(jsonify({
            "error": "CLEANUP_FAILED",
            "message": "Failed to cleanup old data",
            "details": str(e),
            "api_version": "1.0.0",
            "server_time": datetime.now().isoformat()
        })), 500


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@state_api.errorhandler(404)
def not_found(error):
    """Custom 404 handler"""
    return add_cors_headers(jsonify({
        "error": "ENDPOINT_NOT_FOUND",
        "message": "The requested state API endpoint was not found",
        "available_endpoints": [
            "/api/gpts/state/track-signal",
            "/api/gpts/state/signal-history",
            "/api/gpts/state/signal/<id>/execute",
            "/api/gpts/state/log-query",
            "/api/gpts/state/analytics/signals",
            "/api/gpts/state/analytics/queries",
            "/api/gpts/state/analytics/interactions",
            "/api/gpts/state/maintenance/cleanup"
        ],
        "api_version": "1.0.0",
        "server_time": datetime.now().isoformat()
    })), 404


@state_api.errorhandler(500)
def internal_error(error):
    """Custom 500 handler"""
    logger.error(f"Internal server error: {error}")
    return add_cors_headers(jsonify({
        "error": "INTERNAL_SERVER_ERROR", 
        "message": "An internal error occurred while processing your request",
        "api_version": "1.0.0",
        "server_time": datetime.now().isoformat()
    })), 500


# Initialize logging
logger.info("🗄️ Stateful AI Signal Engine API endpoints initialized")