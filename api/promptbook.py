"""
Prompt Book Blueprint for Flask Integration
Provides clean JSON response for GPT context management
"""

from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Create blueprint
promptbook_bp = Blueprint('promptbook', __name__, url_prefix='/api/promptbook')

def add_cors_headers(response):
    """Add CORS headers for GPT access"""
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, User-Agent'
    response.headers['Access-Control-Max-Age'] = '86400'
    return response

@promptbook_bp.route('/', methods=['GET'])
@cross_origin()
def get_promptbook():
    """Get minimal prompt book response as requested"""
    try:
        from core.prompt_book_manager import prompt_book_manager
        
        # Get the enhanced minimal response
        response = prompt_book_manager.get_minimal_promptbook_response()
        
        logger.info("📚 Prompt Book accessed via dedicated blueprint")
        return add_cors_headers(jsonify(response))
        
    except Exception as e:
        logger.error(f"Prompt Book access error: {e}")
        return add_cors_headers(jsonify({
            "status": "error",
            "message": f"Failed to access prompt book: {str(e)}",
            "api_info": {
                "version": "1.0.0",
                "server_time": datetime.now().isoformat(),
                "service": "Cryptocurrency Trading Signals API"
            }
        })), 500

@promptbook_bp.route('/init', methods=['GET'])
@cross_origin()
def init_gpt_context():
    """Initialize GPT context with full prompt"""
    try:
        from core.prompt_book_manager import prompt_book_manager
        
        context_prompt = prompt_book_manager.get_context_initialization_prompt()
        system_status = prompt_book_manager.get_system_status_for_gpt()
        
        response = {
            "status": "success",
            "context": {
                "full_prompt": context_prompt,
                "prompt_length": len(context_prompt),
                "system_status": system_status,
                "initialization_time": datetime.now().isoformat(),
                "instructions": "Use full_prompt as initial context for new GPT session. System configured per Prompt Book preferences."
            },
            "api_info": {
                "version": "1.0.0",
                "server_time": datetime.now().isoformat(),
                "service": "Cryptocurrency Trading Signals API"
            }
        }
        
        logger.info("🚀 GPT context initialized via dedicated blueprint")
        return add_cors_headers(jsonify(response))
        
    except Exception as e:
        logger.error(f"GPT context initialization error: {e}")
        return add_cors_headers(jsonify({
            "status": "error",
            "message": f"Failed to initialize GPT context: {str(e)}",
            "api_info": {
                "version": "1.0.0",
                "server_time": datetime.now().isoformat(),
                "service": "Cryptocurrency Trading Signals API"
            }
        })), 500

@promptbook_bp.route('/context', methods=['GET'])
@cross_origin() 
def get_context():
    """Get current context data"""
    try:
        return add_cors_headers(jsonify({
            "status": "success", 
            "context": {
                "message": "Context endpoint is available",
                "timestamp": datetime.now().isoformat(),
                "version": "1.0.0"
            }
        }))
    except Exception as e:
        return add_cors_headers(jsonify({
            "status": "error",
            "message": str(e)
        })), 500

@promptbook_bp.route('/update', methods=['POST'])
@cross_origin()
def update_promptbook():
    """Update prompt book configuration"""
    try:
        from core.prompt_book_manager import prompt_book_manager
        
        updates = request.get_json() or {}
        updated_book = prompt_book_manager.update_prompt_book(updates)
        
        response = {
            "status": "success",
            "message": "Prompt Book updated successfully",
            "updated_config": {
                "version": updated_book.get("version"),
                "last_updated": updated_book.get("last_updated"),
                "language": updated_book.get("user_preferences", {}).get("language"),
                "style": updated_book.get("user_preferences", {}).get("style")
            },
            "api_info": {
                "version": "1.0.0",
                "server_time": datetime.now().isoformat(),
                "service": "Cryptocurrency Trading Signals API"
            }
        }
        
        logger.info("📝 Prompt Book updated via dedicated blueprint")
        return add_cors_headers(jsonify(response))
        
    except Exception as e:
        logger.error(f"Prompt Book update error: {e}")
        return add_cors_headers(jsonify({
            "status": "error",
            "message": f"Failed to initialize GPT context: {str(e)}",
            "api_info": {
                "version": "1.0.0",
                "server_time": datetime.now().isoformat()
            }
        })), 500
        
        updates = request.get_json() or {}
        updated_book = prompt_book_manager.update_prompt_book(updates)
        
        response = {
            "status": "success",
            "message": "Prompt Book updated successfully",
            "updated_config": {
                "version": updated_book.get("version"),
                "last_updated": updated_book.get("last_updated"),
                "language": updated_book.get("user_preferences", {}).get("language"),
                "style": updated_book.get("user_preferences", {}).get("style")
            },
            "api_info": {
                "version": "1.0.0",
                "server_time": datetime.now().isoformat(),
                "service": "Cryptocurrency Trading Signals API"
            }
        }
        
        logger.info("📝 Prompt Book updated via dedicated blueprint")
        return add_cors_headers(jsonify(response))
        
    except Exception as e:
        logger.error(f"Prompt Book update error: {e}")
        return add_cors_headers(jsonify({
            "status": "error",
            "message": f"Failed to update prompt book: {str(e)}",
            "api_info": {
                "version": "1.0.0",
                "server_time": datetime.now().isoformat()
            }
        })), 500

@promptbook_bp.route('/status', methods=['GET'])
@cross_origin()
def promptbook_status():
    """Get prompt book system status"""
    try:
        from core.prompt_book_manager import prompt_book_manager
        
        pb = prompt_book_manager.get_prompt_book()
        
        response = {
            "status": "success", 
            "system_health": {
                "promptbook_loaded": True,
                "version": pb.get("version"),
                "last_updated": pb.get("last_updated"),
                "supported_timeframes": len(pb.get("supported_timeframes", [])),
                "active_timeframes": len(pb.get("active_timeframes", [])),
                "total_endpoints": len(pb.get("system_integration", {}).get("supported_endpoints", [])),
                "language": pb.get("user_preferences", {}).get("language"),
                "features_enabled": {
                    "auto_initialization": True,
                    "context_management": True,
                    "preference_storage": True,
                    "api_integration": True
                }
            },
            "api_info": {
                "version": "1.0.0",
                "server_time": datetime.now().isoformat(),
                "service": "Cryptocurrency Trading Signals API"
            }
        }
        
        return add_cors_headers(jsonify(response))
        
    except Exception as e:
        logger.error(f"Prompt Book status error: {e}")
        return add_cors_headers(jsonify({
            "status": "error",
            "message": f"Failed to get status: {str(e)}",
            "api_info": {
                "version": "1.0.0",
                "server_time": datetime.now().isoformat()
            }
        })), 500