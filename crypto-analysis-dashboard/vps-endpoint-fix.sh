#!/bin/bash
echo "🔧 VPS ENDPOINT FIX & VERIFICATION"
echo "=================================="

echo "1. Testing Current Endpoint Issues:"
echo "===================================="

echo "Testing sinyal/tajam narrative format:"
curl -s "http://localhost:5050/api/gpts/sinyal/tajam?symbol=BTCUSDT&timeframe=1H&format=narrative" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    print('📊 Current Response Structure:')
    for key in data.keys():
        if isinstance(data[key], str):
            print(f'  {key}: {len(data[key])} chars')
        else:
            print(f'  {key}: {type(data[key]).__name__}')
    
    if 'narrative' in data:
        print(f'✅ Narrative field found: {len(data[\"narrative\"])} chars')
    else:
        print('❌ Narrative field MISSING')
        
    if 'human_readable' in data:
        print(f'✅ Human readable field found: {len(data[\"human_readable\"])} chars')
    else:
        print('❌ Human readable field MISSING')
        
    if 'telegram_message' in data:
        print(f'✅ Telegram message field found: {len(data[\"telegram_message\"])} chars')
    else:
        print('❌ Telegram message field MISSING')
        
except Exception as e:
    print(f'❌ JSON Parse Error: {e}')
    print('Raw response preview:')
    raw = sys.stdin.read()
    print(raw[:300] + '...' if len(raw) > 300 else raw)
"
echo ""

echo "2. Docker Container Logs:"
echo "========================="
docker logs crypto_trading_app --tail 10 | grep -E "(ERROR|WARN|narrative|format)" || echo "No relevant logs found"
echo ""

echo "3. Available Endpoints Check:"
echo "============================="
curl -s "http://localhost:5050/api/gpts/status" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    endpoints = data.get('endpoints', [])
    print(f'Available Endpoints ({len(endpoints)}):')
    for endpoint in endpoints:
        print(f'  ✅ {endpoint}')
except Exception as e:
    print(f'Error: {e}')
"
echo ""

echo "4. Testing Narrative Generation Function:"
echo "=========================================="
curl -s "http://localhost:5050/api/gpts/sinyal/tajam?symbol=BTCUSDT&timeframe=1H&format=both" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    print('Format parameter test:')
    print(f'Format requested: both')
    print(f'Format returned: {data.get(\"format\", \"not specified\")}')
    
    # Check if response has the expected structure
    expected_fields = ['narrative', 'human_readable', 'telegram_message']
    for field in expected_fields:
        if field in data:
            print(f'✅ {field}: Present ({len(data[field])} chars)')
        else:
            print(f'❌ {field}: Missing')
            
except Exception as e:
    print(f'Error: {e}')
"

echo ""
echo "=================================="
echo "✅ VPS ENDPOINT DIAGNOSIS COMPLETED"
echo "Check results above for issues"
echo "=================================="