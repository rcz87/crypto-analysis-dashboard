#!/bin/bash
echo "🔧 FINAL SIMPLE FIX"
echo "=================="

# Check current function in container
echo "📋 Current function:"
docker exec crypto_trading_app sed -n '/def post_sharp_signal/,/logger.info.*Sharp Signal Request/p' /app/gpts_api_simple.py

# Create completely new corrected file by copying from host
echo "🛠️ Copying corrected file from host..."
docker cp gpts_api_simple.py crypto_trading_app:/app/gpts_api_simple_new.py

# Replace old file with new one
docker exec crypto_trading_app mv /app/gpts_api_simple_new.py /app/gpts_api_simple.py

# Quick verification
echo "📋 Verification - looking for GET handling:"
docker exec crypto_trading_app grep -A 8 "request.method.*GET" /app/gpts_api_simple.py || echo "GET handling not found"

# Restart container
echo "🔄 Restarting..."
docker restart crypto_trading_app

# Wait and test
sleep 30
echo "🧪 Testing:"
curl -s "http://localhost:5050/api/gpts/sinyal/tajam?symbol=BTCUSDT&timeframe=1H" | head -100

# Check routes
echo -e "\n📋 Routes:"
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

echo "=================="
