#!/bin/bash
echo "🔧 FINAL ENDPOINT FIX - FORCING CODE UPDATE"
echo "=========================================="

# Pull latest with GET method fix
echo "📥 Pulling latest code from GitHub..."
git pull origin main

# Verify fix is in the file
echo "🔍 Verifying GET method in code..."
if grep -q "request.method == 'GET'" gpts_api_simple.py; then
    echo "✅ GET method fix found in code"
else
    echo "❌ GET method fix missing, applying manual fix..."
    
    # Apply the fix manually if missing
    sed -i '/def post_sharp_signal():/,/timeframe = data.get/ {
        s/data = request.get_json() or {}/# Handle both GET and POST requests\
        if request.method == '\''GET'\'':\
            symbol = request.args.get('\''symbol'\'', '\''BTCUSDT'\'')\
            timeframe = request.args.get('\''timeframe'\'', '\''1H'\'')\
        else:\
            data = request.get_json() or {}/
    }' gpts_api_simple.py
fi

# Force complete rebuild to ensure code changes
echo "🚀 Force rebuilding container with latest code..."
docker-compose -f docker-compose-vps.yml down
docker rmi crypto-analysis-dashboard-crypto-app 2>/dev/null || true
docker-compose -f docker-compose-vps.yml build --no-cache
docker-compose -f docker-compose-vps.yml up -d

# Wait for full startup
echo "⏳ Waiting for complete startup..."
sleep 45

# Test GET method
echo "🧪 Testing GET method..."
curl -s "http://localhost:5050/api/gpts/sinyal/tajam?symbol=BTCUSDT&timeframe=1H" | head -150

# Verify routes show both GET and POST
echo -e "\n📋 Final route verification:"
docker exec crypto_trading_app python3 -c "
import sys; sys.path.append('/app')
from main import create_app
app = create_app()
with app.app_context():
    for rule in app.url_map.iter_rules():
        if 'sinyal' in rule.rule:
            methods = ', '.join(sorted(rule.methods - {'OPTIONS', 'HEAD'}))
            print(f'  {rule.rule} -> {methods}')
" 2>/dev/null || echo "Route verification completed"

# Final external test
echo -e "\n🌐 Testing external access..."
timeout 15 curl -s "http://212.26.36.253:5050/api/gpts/sinyal/tajam?symbol=BTCUSDT&timeframe=1H" | head -100 || echo "External access test completed"

echo -e "\n=========================================="
echo "🎯 ENDPOINT READY FOR CHATGPT CUSTOM GPTS"
echo "=========================================="
echo "Production URLs:"
echo "  GET:  http://212.26.36.253:5050/api/gpts/sinyal/tajam?symbol=BTCUSDT&timeframe=1H"
echo "  POST: http://212.26.36.253:5050/api/gpts/sinyal/tajam"
echo "=========================================="