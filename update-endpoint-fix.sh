#!/bin/bash
echo "🔧 UPDATE ENDPOINT FIX"
echo "======================"

# Create the script on VPS and execute
ssh -o StrictHostKeyChecking=no root@212.26.36.253 << 'ENDSSH'
cd /root/crypto-analysis-dashboard

# Copy current file to container
echo "📋 Copying corrected file..."
docker cp gpts_api_simple.py crypto_trading_app:/app/gpts_api_simple.py

# Restart container
echo "🔄 Restarting container..."
docker restart crypto_trading_app

# Wait for startup
echo "⏳ Waiting for startup..."
sleep 35

# Test GET method
echo "🧪 Testing GET method:"
curl -s "http://localhost:5050/api/gpts/sinyal/tajam?symbol=BTCUSDT&timeframe=1H" | head -100

# Test POST method
echo -e "\n🧪 Testing POST method:"
curl -X POST "http://localhost:5050/api/gpts/sinyal/tajam" \
  -H "Content-Type: application/json" \
  -d '{"symbol": "BTCUSDT", "timeframe": "1H"}' \
  -s | head -100

# Verify routes
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
" 2>/dev/null

echo -e "\n======================"
echo "🎯 ENDPOINT READY"
echo "GET:  http://212.26.36.253:5050/api/gpts/sinyal/tajam?symbol=BTCUSDT&timeframe=1H"
echo "POST: http://212.26.36.253:5050/api/gpts/sinyal/tajam"
echo "======================"
ENDSSH
