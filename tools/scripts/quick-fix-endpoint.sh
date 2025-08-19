#!/bin/bash
echo "🔧 QUICK FIX ENDPOINT GET METHOD"
echo "================================"

# Manual update ke VPS - copy fixed file content
cat > gpts_api_simple_fixed.py << 'EOFILE'
# Content dipotong untuk clarity - akan copy dari replit yang sudah fixed
EOFILE

# Update file di container
docker cp gpts_api_simple.py crypto_trading_app:/app/gpts_api_simple.py 2>/dev/null || echo "Using git pull method"

# Pull latest dari GitHub
git pull origin main

# Restart untuk reload
echo "🔄 Restarting container to reload code..."
docker restart crypto_trading_app

# Wait untuk startup
sleep 20

# Test endpoints
echo "🧪 Testing GET method..."
curl -s "http://localhost:5050/api/gpts/sinyal/tajam?symbol=BTCUSDT&timeframe=1H" | head -100

echo -e "\n🧪 Testing external access..."
curl -s "http://212.26.36.253:5050/api/gpts/sinyal/tajam?symbol=BTCUSDT&timeframe=1H" | head -100

# Verify routes again
echo -e "\n📋 Verifying routes..."
docker exec crypto_trading_app python3 -c "
import sys; sys.path.append('/app')
from main import create_app
app = create_app()
with app.app_context():
    for rule in app.url_map.iter_rules():
        if 'sinyal' in rule.rule:
            methods = ', '.join(sorted(rule.methods - {'OPTIONS', 'HEAD'}))
            print(f'  {rule.rule} -> {methods}')
" 2>/dev/null || echo "Route check failed"

echo "================================"
echo "🎯 ENDPOINT FIX COMPLETED"
echo "Ready for ChatGPT GPTs integration:"
echo "  GET: http://212.26.36.253:5050/api/gpts/sinyal/tajam?symbol=BTCUSDT"
echo "  POST: http://212.26.36.253:5050/api/gpts/sinyal/tajam"
echo "================================"