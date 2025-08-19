#!/usr/bin/env python3
"""
Telegram Integration Endpoints
API endpoints untuk Telegram bot management
"""

import os
import logging
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin

logger = logging.getLogger(__name__)

# Create telegram blueprint
telegram_bp = Blueprint('telegram', __name__, url_prefix='/api/gpts/telegram')

@telegram_bp.route('/status', methods=['GET'])
@cross_origin()
def telegram_status():
    """Get Telegram integration status"""
    try:
        bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
        chat_id = os.environ.get('TELEGRAM_CHAT_ID')
        
        # Check if credentials are configured
        credentials_configured = bool(bot_token and chat_id)
        
        # Test connection if possible
        connection_status = "unknown"
        if credentials_configured:
            try:
                from core.telegram_notifier import send_telegram_message
                test_result = send_telegram_message("🔍 Connection test from API")
                connection_status = "connected" if test_result.get('success') else "failed"
            except Exception as e:
                connection_status = f"error: {str(e)}"
        
        return jsonify({
            "status": "active",
            "telegram_integration": {
                "credentials_configured": credentials_configured,
                "connection_status": connection_status,
                "bot_token_present": bool(bot_token),
                "chat_id_present": bool(chat_id)
            },
            "features": {
                "signal_notifications": True,
                "webhook_alerts": True,
                "manual_messages": True,
                "status_updates": True
            },
            "endpoints": {
                "status": "/api/gpts/telegram/status",
                "test": "/api/gpts/telegram/test",
                "send": "/api/gpts/telegram/send"
            },
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Telegram status error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@telegram_bp.route('/test', methods=['GET', 'POST'])
@cross_origin()
def telegram_test():
    """Test Telegram notification"""
    try:
        from core.telegram_notifier import send_telegram_message
        
        # Create test message
        test_message = f"""🧪 *Telegram Test Message*

✅ *Status:* Connection test successful
🕐 *Time:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🤖 *Source:* GPTs API Test Endpoint
📡 *System:* Cryptocurrency Trading Platform

This is an automated test message to verify Telegram integration is working properly."""

        # Send test message
        result = send_telegram_message(test_message)
        
        return jsonify({
            "status": "success" if result.get('success') else "failed",
            "message": "Test message sent to Telegram",
            "telegram_result": result,
            "test_message": test_message,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Telegram test error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@telegram_bp.route('/send', methods=['POST'])
@cross_origin()
def telegram_send():
    """Send custom message to Telegram"""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({"status": "error", "message": "Message content required"}), 400
        
        from core.telegram_notifier import send_telegram_message
        
        message = data['message']
        chat_id_override = data.get('chat_id')
        
        # Send message
        result = send_telegram_message(message, chat_id_override)
        
        return jsonify({
            "status": "success" if result.get('success') else "failed",
            "message": "Custom message sent to Telegram",
            "telegram_result": result,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Telegram send error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500