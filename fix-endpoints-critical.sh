#!/bin/bash
echo "🔧 CRITICAL ENDPOINT FIX"
echo "======================="

# Stop containers
echo "1. Stopping containers..."
docker-compose -f docker-compose-vps.yml down

# Install missing dependencies
echo "2. Installing aiohttp dependency..."
pip install aiohttp

# Rebuild containers 
echo "3. Rebuilding containers with fixes..."
docker-compose -f docker-compose-vps.yml up -d --build --force-recreate

# Wait for startup
echo "4. Waiting for startup..."
sleep 15

# Test narrative format fix
echo "5. Testing narrative format fix..."
curl -s "http://localhost:5050/api/gpts/sinyal/tajam?symbol=BTCUSDT&timeframe=1H&format=narrative" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    print('✅ Response keys:', list(data.keys()))
    if 'narrative' in data:
        print(f'✅ NARRATIVE FIXED: {len(data[\"narrative\"])} chars')
    else:
        print('❌ Narrative still missing')
    if 'human_readable' in data:
        print(f'✅ HUMAN_READABLE: {len(data[\"human_readable\"])} chars')
    if 'telegram_message' in data:
        print(f'✅ TELEGRAM_MESSAGE: {len(data[\"telegram_message\"])} chars')
except Exception as e:
    print(f'❌ Error: {e}')
"

echo ""
echo "6. Testing state endpoints..."
curl -s "http://localhost:5050/api/state/signal-history" | head -3

echo ""
echo "7. Testing news endpoints..."  
curl -s "http://localhost:5050/api/crypto-news/analyze" | head -3

echo ""
echo "======================="
echo "✅ CRITICAL FIX COMPLETE"
echo "======================="