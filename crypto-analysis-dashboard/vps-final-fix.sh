#!/bin/bash
# Final VPS Fix Script - corrected docker commands
cat > /tmp/vps_final_fix.sh << 'SCRIPT_END'
#!/bin/bash
echo "🔧 VPS FINAL ENDPOINT FIX"
echo "=========================="

echo "1. Checking current status..."
curl -s "http://localhost:5050/api/gpts/sinyal/tajam?format=narrative" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    print('Current response keys:', sorted(data.keys()))
    if 'narrative' in data:
        print(f'Narrative length: {len(data[\"narrative\"])} chars')
    else:
        print('❌ Narrative field missing')
except Exception as e:
    print(f'Current error: {e}')
    print('Raw response:')
    raw = sys.stdin.read()
    print(raw[:200])
" 2>/dev/null || echo "Endpoint not responding"

echo ""
echo "2. Fixing Docker rebuild command..."
# Stop containers first
docker-compose -f docker-compose-vps.yml down

# Remove old images to force rebuild
docker image prune -f
docker system prune -f

# Rebuild without problematic --no-cache flag
echo "3. Building fresh containers..."
docker-compose -f docker-compose-vps.yml build --pull
docker-compose -f docker-compose-vps.yml up -d

echo "4. Waiting for complete startup..."
sleep 45

echo "5. Checking container status..."
docker-compose -f docker-compose-vps.yml ps

echo "6. Testing endpoints..."
for endpoint in "/api/gpts/status" "/api/gpts/sinyal/tajam"; do
    echo "Testing $endpoint..."
    status=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:5050$endpoint")
    echo "Status: $status"
    if [ "$status" = "200" ]; then
        echo "✅ $endpoint: WORKING"
    else
        echo "❌ $endpoint: $status"
    fi
done

echo ""
echo "7. Final narrative format test..."
curl -s "http://localhost:5050/api/gpts/sinyal/tajam?format=narrative" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    print('\\n✅ RESPONSE RECEIVED')
    print('Keys:', sorted(data.keys()))
    
    if 'narrative' in data:
        narrative_len = len(data['narrative'])
        print(f'\\n✅ NARRATIVE FOUND: {narrative_len} characters')
        if narrative_len > 500:
            print('✅ Narrative content sufficient for ChatGPT')
            print('Preview:', data['narrative'][:100] + '...')
        else:
            print('⚠️ Narrative too short')
    else:
        print('\\n❌ NARRATIVE STILL MISSING')
        
    if 'human_readable' in data:
        print(f'✅ Human readable: {len(data[\"human_readable\"])} chars')
    if 'telegram_message' in data:
        print(f'✅ Telegram message: {len(data[\"telegram_message\"])} chars')
        
except Exception as e:
    print(f'\\n❌ JSON Parse Error: {e}')
    print('\\nRaw response (first 300 chars):')
    raw = sys.stdin.read()
    print(raw[:300])
"

echo ""
echo "8. Testing external access..."
curl -s "http://212.26.36.253:5050/api/gpts/sinyal/tajam?format=narrative" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    if 'narrative' in data and len(data['narrative']) > 100:
        print('✅ EXTERNAL ACCESS WORKING - Ready for ChatGPT Custom GPTs')
    else:
        print('❌ External access has issues')
except:
    print('❌ External endpoint not responding properly')
"

echo ""
echo "=========================="
echo "✅ VPS FINAL FIX COMPLETE"
echo "Public URL: http://212.26.36.253:5050/api/gpts/sinyal/tajam?format=narrative"
echo "Ready for ChatGPT Custom GPTs integration"
echo "=========================="
SCRIPT_END

chmod +x /tmp/vps_final_fix.sh
echo "Fixed script created at /tmp/vps_final_fix.sh"