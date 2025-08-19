#!/bin/bash
echo "🚀 DEPLOYING ENDPOINT FIXES TO VPS"
echo "=================================="

echo "1. Stopping VPS containers..."
docker-compose -f docker-compose-vps.yml down

echo "2. Rebuilding with fixes..."
docker-compose -f docker-compose-vps.yml up -d --build --force-recreate

echo "3. Waiting for startup..."
sleep 20

echo "4. Testing narrative format fix..."
curl -s "http://localhost:5050/api/gpts/sinyal/tajam?symbol=BTCUSDT&timeframe=1H&format=narrative" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    print('🔧 NARRATIVE FORMAT TEST:')
    print('Response keys:', sorted(data.keys()))
    if 'narrative' in data:
        print(f'✅ NARRATIVE FIXED: {len(data[\"narrative\"])} characters')
        print('Preview:', data['narrative'][:100] + '...')
    else:
        print('❌ Narrative field still missing')
    if 'human_readable' in data:
        print(f'✅ HUMAN_READABLE: {len(data[\"human_readable\"])} characters')
    if 'telegram_message' in data:
        print(f'✅ TELEGRAM_MESSAGE: {len(data[\"telegram_message\"])} characters')
except Exception as e:
    print(f'❌ Error: {e}')
"

echo ""
echo "5. Testing available endpoints..."
curl -s "http://localhost:5050/api/gpts/status" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    endpoints = data.get('endpoints', [])
    print(f'Available endpoints: {len(endpoints)}')
    for ep in endpoints:
        print(f'  ✅ {ep}')
except Exception as e:
    print(f'Error: {e}')
"

echo ""
echo "6. Testing state endpoints..."
status_code=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:5050/api/state/signal-history")
if [ "$status_code" = "200" ]; then
    echo "✅ State endpoints: WORKING"
else
    echo "❌ State endpoints: $status_code"
fi

echo ""
echo "7. Testing news endpoints..."
status_code=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:5050/api/crypto-news/analyze")
if [ "$status_code" = "200" ]; then
    echo "✅ News endpoints: WORKING"
else
    echo "❌ News endpoints: $status_code"
fi

echo ""
echo "=================================="
echo "✅ VPS ENDPOINT FIX DEPLOYMENT COMPLETE"
echo "Test results shown above"
echo "=================================="