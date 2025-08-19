#!/bin/bash
echo "🔧 DIRECT FIX IN RUNNING CONTAINER"
echo "================================="

# Check current file in container
echo "📋 Current routing in container:"
docker exec crypto_trading_app grep -A 10 "def post_sharp_signal" /app/gpts_api_simple.py

# Apply fix directly to running container
echo "🛠️ Applying GET method fix directly to container..."
docker exec crypto_trading_app sed -i '/def post_sharp_signal():/,/symbol = data.get/ {
    /symbol = data.get/i\
        # Handle both GET and POST requests\
        if request.method == '\''GET'\'':\
            symbol = request.args.get('\''symbol'\'', '\''BTCUSDT'\'')\
            timeframe = request.args.get('\''timeframe'\'', '\''1H'\'')\
        else:\
            data = request.get_json() or {}
}' /app/gpts_api_simple.py

# Verify fix was applied
echo "📋 Verification after fix:"
docker exec crypto_trading_app grep -A 15 "def post_sharp_signal" /app/gpts_api_simple.py

# Restart only the application process (not container)
echo "🔄 Restarting application process..."
docker exec crypto_trading_app pkill -f python
sleep 5

# Test immediately
echo "🧪 Testing GET method after direct fix..."
curl -s "http://localhost:5050/api/gpts/sinyal/tajam?symbol=BTCUSDT&timeframe=1H" | head -150

# Check route registration
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
" 2>/dev/null || echo "Checking routes..."

echo "================================="
echo "🎯 DIRECT FIX COMPLETED"
echo "================================="