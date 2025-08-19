"""
SMC Context Endpoints
Provides access to SMC Memory System for GPT integration
"""

from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Create blueprint
smc_context_bp = Blueprint('smc_context', __name__, url_prefix='/api/smc')

def add_cors_headers(response):
    """Add CORS headers for GPT access"""
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, User-Agent'
    response.headers['Access-Control-Max-Age'] = '86400'
    return response

@smc_context_bp.route('/context', methods=['GET'])
@cross_origin()
def get_smc_context():
    """Get current SMC context for GPT analysis"""
    try:
        from core.structure_memory import smc_memory
        
        context = smc_memory.get_context()
        
        response = {
            "status": "success",
            "context": context,
            "api_info": {
                "version": "1.0.0",
                "server_time": datetime.now().isoformat(),
                "service": "SMC Context API"
            }
        }
        
        logger.info("🧠 SMC context accessed via API")
        return add_cors_headers(jsonify(response))
        
    except Exception as e:
        logger.error(f"SMC context access error: {e}")
        return add_cors_headers(jsonify({
            "status": "error",
            "message": f"Failed to get SMC context: {str(e)}",
            "api_info": {
                "version": "1.0.0",
                "server_time": datetime.now().isoformat()
            }
        })), 500

@smc_context_bp.route('/summary', methods=['GET'])
@cross_origin()
def get_smc_summary():
    """Get SMC structure summary"""
    try:
        from core.structure_memory import smc_memory
        
        summary = smc_memory.get_structure_summary()
        
        response = {
            "status": "success", 
            "summary": summary,
            "api_info": {
                "version": "1.0.0",
                "server_time": datetime.now().isoformat(),
                "service": "SMC Context API"
            }
        }
        
        logger.info("📊 SMC summary accessed via API")
        return add_cors_headers(jsonify(response))
        
    except Exception as e:
        logger.error(f"SMC summary access error: {e}")
        return add_cors_headers(jsonify({
            "status": "error",
            "message": f"Failed to get SMC summary: {str(e)}",
            "api_info": {
                "version": "1.0.0", 
                "server_time": datetime.now().isoformat()
            }
        })), 500

@smc_context_bp.route('/history', methods=['GET'])
@cross_origin()
def get_smc_history():
    """Get recent SMC history with optional filtering"""
    try:
        from core.structure_memory import smc_memory
        
        # Get query parameters
        hours = int(request.args.get('hours', 24))
        symbol = request.args.get('symbol')
        timeframe = request.args.get('timeframe')
        
        history = smc_memory.get_recent_history(hours=hours, symbol=symbol, timeframe=timeframe)
        
        response = {
            "status": "success",
            "history": history,
            "filters": {
                "hours": hours,
                "symbol": symbol,
                "timeframe": timeframe
            },
            "total_entries": len(history),
            "api_info": {
                "version": "1.0.0",
                "server_time": datetime.now().isoformat(),
                "service": "SMC Context API"
            }
        }
        
        logger.info(f"📚 SMC history accessed ({len(history)} entries)")
        return add_cors_headers(jsonify(response))
        
    except Exception as e:
        logger.error(f"SMC history access error: {e}")
        return add_cors_headers(jsonify({
            "status": "error",
            "message": f"Failed to get SMC history: {str(e)}",
            "api_info": {
                "version": "1.0.0",
                "server_time": datetime.now().isoformat()
            }
        })), 500

@smc_context_bp.route('/clear', methods=['POST'])
@cross_origin()
def clear_smc_data():
    """Clear old SMC data"""
    try:
        from core.structure_memory import smc_memory
        
        data = request.get_json() or {}
        hours = data.get('hours', 48)
        
        smc_memory.clear_old_data(hours=hours)
        
        response = {
            "status": "success",
            "message": f"Cleared SMC data older than {hours} hours",
            "api_info": {
                "version": "1.0.0", 
                "server_time": datetime.now().isoformat(),
                "service": "SMC Context API"
            }
        }
        
        logger.info(f"🧹 SMC data cleared (older than {hours} hours)")
        return add_cors_headers(jsonify(response))
        
    except Exception as e:
        logger.error(f"SMC data clear error: {e}")
        return add_cors_headers(jsonify({
            "status": "error",
            "message": f"Failed to clear SMC data: {str(e)}",
            "api_info": {
                "version": "1.0.0",
                "server_time": datetime.now().isoformat()
            }
        })), 500

@smc_context_bp.route('/status', methods=['GET'])
@cross_origin()
def get_smc_status():
    """Get SMC memory system status"""
    try:
        from core.structure_memory import smc_memory
        
        context = smc_memory.get_context()
        memory_stats = context.get("memory_stats", {})
        
        response = {
            "status": "success",
            "system_status": {
                "memory_initialized": True,
                "total_entries": memory_stats.get("total_entries", 0),
                "last_updated": memory_stats.get("last_updated"),
                "symbols_tracked": memory_stats.get("symbols_tracked", []),
                "timeframes_tracked": memory_stats.get("timeframes_tracked", []),
                "active_structures": {
                    "bos_active": context.get("last_bos") is not None,
                    "choch_active": context.get("last_choch") is not None,
                    "bullish_ob_count": len(context.get("last_bullish_ob", [])),
                    "bearish_ob_count": len(context.get("last_bearish_ob", [])),
                    "fvg_count": len(context.get("last_fvg", [])),
                    "liquidity_active": context.get("last_liquidity") is not None
                }
            },
            "api_info": {
                "version": "1.0.0",
                "server_time": datetime.now().isoformat(),
                "service": "SMC Context API"
            }
        }
        
        return add_cors_headers(jsonify(response))
        
    except Exception as e:
        logger.error(f"SMC status error: {e}")
        return add_cors_headers(jsonify({
            "status": "error",
            "message": f"Failed to get SMC status: {str(e)}",
            "api_info": {
                "version": "1.0.0",
                "server_time": datetime.now().isoformat()
            }
        })), 500