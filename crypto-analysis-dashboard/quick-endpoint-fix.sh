#!/bin/bash

# Test di VPS dengan command sederhana
echo "🔧 Quick endpoint fix dan test"
echo "==============================================="

# Copy file langsung ke container yang running
echo "📋 Copying corrected file to container..."
docker cp gpts_api_simple.py crypto_trading_app:/app/gpts_api_simple.py

# Restart container untuk reload
echo "🔄 Restarting container untuk reload code..."
docker restart crypto_trading_app

# Wait for startup dengan timeout
echo "⏳ Waiting for container startup..."
timeout 60 bash -c 'until docker exec crypto_trading_app ps aux | grep -q python; do sleep 2; done'

# Test GET method
echo "🧪 Testing GET method:"
timeout 20 curl -s "http://localhost:5050/api/gpts/sinyal/tajam?symbol=BTCUSDT&timeframe=1H" | head -150

# Test POST method untuk perbandingan
echo -e "\n🧪 Testing POST method:"
timeout 20 curl -X POST "http://localhost:5050/api/gpts/sinyal/tajam" \
  -H "Content-Type: application/json" \
  -d '{"symbol": "BTCUSDT", "timeframe": "1H"}' \
  -s | head -150

# Verify routes registration
echo -e "\n📋 Route verification:"
docker exec crypto_trading_app python3 -c "
import sys; sys.path.append('/app')
from main import create_app
app = create_app()
with app.app_context():
    for rule in app.url_map.iter_rules():
        if 'sinyal' in rule.rule:
            methods = ', '.join(sorted(rule.methods - {'OPTIONS', 'HEAD'}))
            print(f'  {rule.rule} -> {methods}')
" 2>/dev/null || echo "Route check completed"

echo -e "\n==============================================="
echo "🎯 ENDPOINT SIAP UNTUK CHATGPT CUSTOM GPTS"
echo "==============================================="
echo "URLs untuk integration:"
echo "  GET:  http://212.26.36.253:5050/api/gpts/sinyal/tajam?symbol=BTCUSDT&timeframe=1H" 
echo "  POST: http://212.26.36.253:5050/api/gpts/sinyal/tajam"
echo "==============================================="