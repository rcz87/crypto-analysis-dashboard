#!/bin/bash
echo "🚀 VPS COMPLETE ENDPOINT FIX"
echo "============================"

# Stop all containers
echo "1. Stopping containers..."
docker-compose -f docker-compose-vps.yml down

# Install missing dependencies in container
echo "2. Adding missing dependencies..."
echo "aiohttp==3.8.6" >> requirements-prod.txt

# Rebuild containers completely
echo "3. Full container rebuild..."
docker-compose -f docker-compose-vps.yml up -d --build --force-recreate --no-cache

# Wait for startup
echo "4. Waiting for full startup..."
sleep 30

# Test narrative endpoint
echo "5. Testing narrative format..."
curl -s "http://localhost:5050/api/gpts/sinyal/tajam?format=narrative" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    keys = sorted(data.keys())
    print('Response keys:', keys)
    
    if 'narrative' in data and len(data['narrative']) > 100:
        print(f'✅ NARRATIVE WORKING: {len(data[\"narrative\"])} chars')
        print('Preview:', data['narrative'][:100] + '...')
    else:
        print('❌ Narrative still broken')
        
    if 'human_readable' in data:
        print(f'✅ Human readable: {len(data[\"human_readable\"])} chars')
    if 'telegram_message' in data:  
        print(f'✅ Telegram message: {len(data[\"telegram_message\"])} chars')
        
except Exception as e:
    print(f'❌ JSON Error: {e}')
    print('Raw response:')
    raw = sys.stdin.read()
    print(raw[:300])
"

echo ""
echo "6. Testing all endpoints..."
endpoints=(
    "/api/gpts/status"
    "/api/gpts/sinyal/tajam"
    "/api/state/signal-history"
    "/api/crypto-news/analyze"
    "/api/performance/stats"
)

working=0
for endpoint in "${endpoints[@]}"; do
    status=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:5050$endpoint")
    if [ "$status" = "200" ]; then
        echo "✅ $endpoint: WORKING"
        ((working++))
    else
        echo "❌ $endpoint: $status"
    fi
done

echo ""
echo "============================"
echo "Working endpoints: $working/${#endpoints[@]}"
if [ $working -ge 4 ]; then
    echo "✅ VPS FIX SUCCESSFUL"
else
    echo "⚠️ Some endpoints need attention"
fi
echo "============================"
