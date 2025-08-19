#!/usr/bin/env python3
"""
Webhook Endpoints - TradingView LuxAlgo Integration
Complete webhook system untuk TradingView signals
"""

import os
import json
import logging
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin

logger = logging.getLogger(__name__)

# Create webhook blueprint
webhook_bp = Blueprint('webhooks', __name__, url_prefix='/api/webhooks')

@webhook_bp.route('/status', methods=['GET'])
@cross_origin()
def webhook_status():
    """Get webhook system status"""
    try:
        return jsonify({
            "status": "active",
            "webhook_system": "operational",
            "supported_formats": ["JSON", "text", "TradingView alerts"],
            "endpoints": {
                "main_webhook": "/api/webhooks/tradingview",
                "test_endpoint": "/api/webhooks/tradingview/test",
                "setup_guide": "/api/webhooks/setup-guide"
            },
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Webhook status error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@webhook_bp.route('/setup-guide', methods=['GET'])
@cross_origin()
def webhook_setup_guide():
    """Get TradingView webhook setup guide"""
    try:
        return jsonify({
            "title": "TradingView LuxAlgo Webhook Setup Guide",
            "webhook_url": "https://your-domain.com/api/webhooks/tradingview",
            "supported_formats": [
                {
                    "type": "JSON",
                    "example": {
                        "symbol": "BTCUSDT",
                        "action": "BUY",
                        "price": 50000,
                        "strategy": "LuxAlgo Premium",
                        "timeframe": "1h"
                    }
                },
                {
                    "type": "Text",
                    "example": "LuxAlgo BUY BTCUSDT at 50000"
                }
            ],
            "setup_steps": [
                "1. Open TradingView and go to your LuxAlgo Premium indicator",
                "2. Create alert condition",
                "3. Set webhook URL to the endpoint above",
                "4. Configure message format (JSON recommended)",
                "5. Test the webhook using /test endpoint"
            ],
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Setup guide error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@webhook_bp.route('/tradingview', methods=['POST'])
@cross_origin()
def tradingview_webhook():
    """Main TradingView webhook endpoint"""
    try:
        # Get request data
        if request.is_json:
            data = request.get_json()
            signal_type = "JSON"
        else:
            data = request.get_data(as_text=True)
            signal_type = "TEXT"
        
        logger.info(f"Received TradingView webhook: {signal_type}")
        
        # Process webhook data
        processed_signal = process_tradingview_signal(data, signal_type)
        
        # Send to Telegram if configured
        try:
            from core.telegram_notifier import send_telegram_message
            telegram_message = format_telegram_message(processed_signal)
            telegram_result = send_telegram_message(telegram_message)
            logger.info(f"Telegram notification sent: {telegram_result.get('success', False)}")
        except Exception as e:
            logger.warning(f"Telegram notification failed: {e}")
        
        return jsonify({
            "status": "success",
            "message": "Webhook received and processed",
            "signal": processed_signal,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Webhook processing error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@webhook_bp.route('/tradingview/test', methods=['GET', 'POST'])
@cross_origin()
def tradingview_webhook_test():
    """Test endpoint for TradingView webhook"""
    try:
        if request.method == 'GET':
            # GET request - return test info
            return jsonify({
                "status": "ready",
                "message": "TradingView webhook test endpoint",
                "test_payload": {
                    "symbol": "BTCUSDT",
                    "action": "BUY",
                    "price": 50000,
                    "strategy": "LuxAlgo Premium Test",
                    "timeframe": "1h",
                    "confidence": 85
                },
                "instructions": "Send POST request with JSON payload to test webhook processing",
                "timestamp": datetime.now().isoformat()
            })
        else:
            # POST request - process test webhook
            data = request.get_json() if request.is_json else request.get_data(as_text=True)
            processed = process_tradingview_signal(data, "TEST")
            
            return jsonify({
                "status": "test_success",
                "message": "Test webhook processed successfully",
                "original_data": data,
                "processed_signal": processed,
                "timestamp": datetime.now().isoformat()
            })
            
    except Exception as e:
        logger.error(f"Webhook test error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

def process_tradingview_signal(data, signal_type):
    """Process TradingView signal data"""
    try:
        if signal_type == "JSON" or signal_type == "TEST":
            # Process JSON data
            if isinstance(data, dict):
                signal = data
            else:
                signal = json.loads(data)
                
            return {
                "symbol": signal.get("symbol", "UNKNOWN"),
                "action": signal.get("action", "UNKNOWN"),
                "price": signal.get("price", 0),
                "strategy": signal.get("strategy", "LuxAlgo"),
                "timeframe": signal.get("timeframe", "unknown"),
                "confidence": signal.get("confidence", 0),
                "processed_at": datetime.now().isoformat(),
                "type": signal_type
            }
        else:
            # Process text data
            text = str(data).strip()
            
            # Simple text parsing for "LuxAlgo BUY BTCUSDT at 50000" format
            parts = text.split()
            action = "UNKNOWN"
            symbol = "UNKNOWN"
            price = 0
            
            if len(parts) >= 3:
                if "BUY" in text.upper():
                    action = "BUY"
                elif "SELL" in text.upper():
                    action = "SELL"
                
                for part in parts:
                    if "USDT" in part or "USD" in part:
                        symbol = part
                        break
                
                # Extract price
                for part in parts:
                    try:
                        if "." in part or part.isdigit():
                            price = float(part)
                            break
                    except:
                        continue
            
            return {
                "symbol": symbol,
                "action": action,
                "price": price,
                "strategy": "LuxAlgo",
                "timeframe": "unknown",
                "confidence": 0,
                "raw_text": text,
                "processed_at": datetime.now().isoformat(),
                "type": signal_type
            }
            
    except Exception as e:
        logger.error(f"Signal processing error: {e}")
        return {
            "error": str(e),
            "raw_data": str(data),
            "processed_at": datetime.now().isoformat(),
            "type": signal_type
        }

def format_telegram_message(signal):
    """Format signal for Telegram notification"""
    try:
        if "error" in signal:
            return f"🚨 *Webhook Error*\n\n❌ {signal['error']}"
        
        action_emoji = "🟢" if signal.get("action") == "BUY" else "🔴" if signal.get("action") == "SELL" else "⚪"
        
        message = f"""{action_emoji} *TradingView Signal*

📊 *Symbol:* {signal.get('symbol', 'N/A')}
🎯 *Action:* {signal.get('action', 'N/A')}
💰 *Price:* ${signal.get('price', 0):,.2f}
📈 *Strategy:* {signal.get('strategy', 'LuxAlgo')}
⏰ *Timeframe:* {signal.get('timeframe', 'N/A')}
🎯 *Confidence:* {signal.get('confidence', 0)}%

🕐 *Time:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""

        return message
        
    except Exception as e:
        logger.error(f"Telegram message formatting error: {e}")
        return f"🚨 Signal received but formatting failed: {str(e)}"