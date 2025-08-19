#!/bin/bash
echo "🚀 VPS ENDPOINT FIX DEPLOYMENT"
echo "=============================="

echo "1. Stopping containers..."
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
    print('Response keys:', sorted(data.keys()))
    if 'narrative' in data:
        print(f'✅ NARRATIVE FIXED: {len(data[\"narrative\"])} characters')
        print('Preview:', data['narrative'][:150] + '...')
    else:
        print('❌ Narrative field still missing')
    if 'human_readable' in data:
        print(f'✅ HUMAN_READABLE: {len(data[\"human_readable\"])} characters')
    if 'telegram_message' in data:
        print(f'✅ TELEGRAM_MESSAGE: {len(data[\"telegram_message\"])} characters')
except Exception as e:
    print(f'❌ Error: {e}')
    print('Raw response preview:')
    raw = sys.stdin.read()
    print(raw[:200] + '...' if len(raw) > 200 else raw)
"

echo ""
echo "5. Testing all endpoints status..."
status_endpoints=(
    "/api/gpts/status"
    "/api/state/signal-history" 
    "/api/crypto-news/analyze"
    "/api/performance/metrics"
    "/api/ai/prediction"
)

working=0
total=5

for endpoint in "${status_endpoints[@]}"; do
    status_code=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:5050$endpoint")
    if [ "$status_code" = "200" ]; then
        echo "✅ $endpoint: WORKING"
        ((working++))
    else
        echo "❌ $endpoint: $status_code"
    fi
done

echo ""
echo "6. ENDPOINT SUMMARY:"
echo "Working endpoints: $working/$total"

if [ $working -eq $total ]; then
    echo "✅ ALL ENDPOINTS WORKING"
else
    echo "⚠️ Some endpoints still need attention"
fi

echo ""
echo "=============================="
echo "✅ VPS DEPLOYMENT COMPLETE"
echo "=============================="