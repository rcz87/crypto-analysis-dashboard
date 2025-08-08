#!/usr/bin/env python3
"""
Global Error Handlers untuk Flask GPTs API
Comprehensive error handling dengan logging dan structured responses
"""

import logging
import traceback
from datetime import datetime
from flask import jsonify, request
from werkzeug.exceptions import HTTPException

logger = logging.getLogger(__name__)

# Custom API Error class for compatibility
class APIError(Exception):
    """Custom API Error class"""
    def __init__(self, message, status_code=500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class APIErrorHandler:
    """Centralized error handling untuk GPTs API"""
    
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize error handlers dengan Flask app"""
        
        @app.errorhandler(Exception)
        def handle_general_exception(error):
            """Handle semua uncaught exceptions"""
            # Log full error details
            logger.error(f"🚨 Uncaught Exception: {str(error)}")
            logger.error(f"🔍 Request: {request.method} {request.url}")
            logger.error(f"📊 Traceback: {traceback.format_exc()}")
            
            # Jangan expose internal errors ke client
            return jsonify({
                "error": "INTERNAL_SERVER_ERROR",
                "error_code": 500,
                "message": "An internal server error occurred",
                "timestamp": datetime.now().isoformat(),
                "api_version": "1.0.0",
                "request_id": self._generate_request_id()
            }), 500
        
        @app.errorhandler(422)
        def handle_validation_error(error):
            """Handle validation errors (422 Unprocessable Entity)"""
            logger.warning(f"⚠️ Validation Error: {str(error)}")
            
            return jsonify({
                "error": "VALIDATION_ERROR", 
                "error_code": 422,
                "message": "Input validation failed",
                "details": getattr(error, 'description', None) or str(error),
                "timestamp": datetime.now().isoformat(),
                "api_version": "1.0.0"
            }), 422
        
        @app.errorhandler(400)
        def handle_bad_request(error):
            """Handle bad request errors"""
            logger.warning(f"⚠️ Bad Request: {str(error)}")
            
            return jsonify({
                "error": "BAD_REQUEST",
                "error_code": 400,
                "message": "Invalid request format or parameters",
                "details": getattr(error, 'description', None) or str(error),
                "timestamp": datetime.now().isoformat(),
                "api_version": "1.0.0"
            }), 400
        
        @app.errorhandler(404)
        def handle_not_found(error):
            """Handle 404 errors"""
            logger.info(f"📍 Not Found: {request.url}")
            
            return jsonify({
                "error": "NOT_FOUND",
                "error_code": 404,
                "message": "Endpoint not found",
                "available_endpoints": [
                    "/api/gpts/signal",
                    "/api/gpts/sinyal/tajam",
                    "/api/gpts/narrative", 
                    "/api/gpts/chart",
                    "/api/gpts/status"
                ],
                "timestamp": datetime.now().isoformat(),
                "api_version": "1.0.0"
            }), 404
        
        @app.errorhandler(503)
        def handle_service_unavailable(error):
            """Handle service unavailable errors"""
            logger.error(f"🔴 Service Unavailable: {str(error)}")
            
            return jsonify({
                "error": "SERVICE_UNAVAILABLE",
                "error_code": 503,
                "message": "External service temporarily unavailable",
                "details": "Please try again in a few moments",
                "timestamp": datetime.now().isoformat(),
                "api_version": "1.0.0"
            }), 503
        
        @app.errorhandler(HTTPException)
        def handle_http_exception(error):
            """Handle all other HTTP exceptions"""
            logger.warning(f"⚠️ HTTP Exception {error.code}: {str(error)}")
            
            return jsonify({
                "error": f"HTTP_{error.code}",
                "error_code": error.code,
                "message": error.description or f"HTTP {error.code} Error",
                "timestamp": datetime.now().isoformat(),
                "api_version": "1.0.0"
            }), error.code
    
    def _generate_request_id(self) -> str:
        """Generate unique request ID untuk tracking"""
        import uuid
        return str(uuid.uuid4())[:8]

    @staticmethod
    def create_error_response(error_type: str, message: str, status_code: int = 500, details=None):
        """Create standardized error response"""
        response = {
            "error": error_type,
            "error_code": status_code,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "api_version": "1.0.0"
        }
        
        if details:
            response["details"] = details
            
        return jsonify(response), status_code

# Utility functions untuk error handling
def log_endpoint_access(endpoint_name: str, success: bool = True, error_msg: str = None):
    """Log endpoint access untuk monitoring"""
    if success:
        logger.info(f"✅ {endpoint_name}: Success")
    else:
        logger.error(f"❌ {endpoint_name}: Failed - {error_msg}")

def handle_okx_api_error(error, symbol: str = "Unknown"):
    """Handle OKX API specific errors"""
    logger.error(f"🔌 OKX API Error for {symbol}: {str(error)}")
    
    return APIErrorHandler.create_error_response(
        error_type="OKX_API_ERROR",
        message="Failed to fetch market data from OKX",
        status_code=503,
        details=f"Symbol: {symbol}, Error: {str(error)}"
    )

def handle_telegram_error(error, chat_id: str = "Unknown"):
    """Handle Telegram API specific errors"""
    logger.error(f"📱 Telegram Error for chat {chat_id}: {str(error)}")
    
    return APIErrorHandler.create_error_response(
        error_type="TELEGRAM_ERROR", 
        message="Failed to send Telegram notification",
        status_code=500,
        details=f"Chat ID: {chat_id}, Error: {str(error)}"
    )

def handle_validation_error(field: str, message: str, value=None):
    """Handle input validation errors"""
    logger.warning(f"⚠️ Validation Error - {field}: {message}")
    
    details = {
        "field": field,
        "message": message,
        "received_value": value
    }
    
    return APIErrorHandler.create_error_response(
        error_type="VALIDATION_ERROR",
        message="Input validation failed", 
        status_code=422,
        details=details
    )