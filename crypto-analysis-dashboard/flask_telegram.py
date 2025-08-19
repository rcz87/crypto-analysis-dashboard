from flask import Flask, jsonify, request
import requests
import json

app = Flask(__name__)

# Telegram config
BOT_TOKEN = "7659990721:AAFmX7iRu4Azxs27kNE9QkAYJA6fiwQHwpc"
CHAT_ID = "5899681906"

def send_telegram(message):
    """Send message to Telegram"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        'chat_id': CHAT_ID,
        'text': message,
        'parse_mode': 'Markdown'
    }
    
    try:
        response = requests.post(url, data=data)
        return response.status_code == 200
    except:
        return False

@app.route('/')
def home():
    return "🚀 Flask + Telegram Bot Ready!"

@app.route('/api/signal')
def get_signal():
    """Simple trading signal endpoint"""
    signal_data = {
        'symbol': 'BTCUSDT',
        'signal': 'BUY',
        'confidence': 75,
        'price': 114500,
        'message': 'Strong bullish signal detected!'
    }
    
    # Send to Telegram
    telegram_message = f"""
🎯 *TRADING SIGNAL*

📊 Symbol: `{signal_data['symbol']}`
🚀 Signal: `{signal_data['signal']}`
💪 Confidence: `{signal_data['confidence']}%`
💰 Price: `${signal_data['price']:,}`

📝 {signal_data['message']}
    """
    
    if send_telegram(telegram_message):
        signal_data['telegram_sent'] = True
    else:
        signal_data['telegram_sent'] = False
    
    return jsonify(signal_data)

@app.route('/api/test-telegram')
def test_telegram_endpoint():
    """Test telegram sending"""
    message = "🤖 Test dari Flask API endpoint!"
    
    if send_telegram(message):
        return jsonify({'status': 'success', 'message': 'Telegram sent!'})
    else:
        return jsonify({'status': 'error', 'message': 'Failed to send'})

if __name__ == '__main__':
    print("🚀 Starting Flask + Telegram server...")
    app.run(host='0.0.0.0', port=5001, debug=True)
@app.route('/openapi.json')
def openapi_schema():
    """OpenAPI schema for ChatGPT Custom GPT"""
    schema = {
        "openapi": "3.0.0",
        "info": {
            "title": "Crypto Trading API",
            "version": "1.0.0",
            "description": "Trading signals and Telegram notifications"
        },
        "servers": [
            {
                "url": "http://localhost:5001",
                "description": "Local development server"
            }
        ],
        "paths": {
            "/api/signal": {
                "get": {
                    "summary": "Get trading signal",
                    "description": "Get trading signal with Telegram notification",
                    "responses": {
                        "200": {
                            "description": "Trading signal",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "symbol": {"type": "string"},
                                            "signal": {"type": "string"},
                                            "confidence": {"type": "number"},
                                            "price": {"type": "number"},
                                            "message": {"type": "string"},
                                            "telegram_sent": {"type": "boolean"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/api/test-telegram": {
                "get": {
                    "summary": "Test Telegram",
                    "description": "Send test message to Telegram",
                    "responses": {
                        "200": {
                            "description": "Test result"
                        }
                    }
                }
            }
        }
    }
    return jsonify(schema)