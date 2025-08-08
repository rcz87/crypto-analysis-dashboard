from flask import Flask, jsonify
import requests

app = Flask(__name__)

# Config
BOT_TOKEN = "7659990721:AAFmX7iRu4Azxs27kNE9QkAYJA6fiwQHwpc"
CHAT_ID = "5899681906"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {'chat_id': CHAT_ID, 'text': message, 'parse_mode': 'Markdown'}
    try:
        response = requests.post(url, data=data)
        return response.status_code == 200
    except:
        return False

@app.route('/')
def home():
    return "🚀 Final Trading Server Ready!"

@app.route('/api/signal')
def get_signal():
    signal_data = {
        'symbol': 'BTCUSDT',
        'signal': 'BUY',
        'confidence': 75,
        'price': 114500,
        'telegram_sent': send_telegram("🎯 TRADING SIGNAL: BUY BTCUSDT @ $114,500")
    }
    return jsonify(signal_data)

@app.route('/openapi.json')
def openapi_schema():
    return jsonify({
        "openapi": "3.0.0",
        "info": {"title": "Crypto Trading API", "version": "1.0.0"},
        "servers": [{"url": "http://localhost:5002"}],
        "paths": {
            "/api/signal": {
                "get": {"summary": "Get trading signal"}
            }
        }
    })

if __name__ == '__main__':
    print("🚀 Starting final server...")
    app.run(host='0.0.0.0', port=5002, debug=True)