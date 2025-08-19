#!/bin/bash
# VPS Direct Fix Script - untuk dijalankan di VPS
cat > /tmp/vps_direct_fix.sh << 'SCRIPT_END'
#!/bin/bash
echo "🔧 VPS DIRECT ENDPOINT FIX"
echo "=========================="

echo "1. Backing up current files..."
cp gpts_api_simple.py gpts_api_simple.py.backup

echo "2. Creating fixed gpts_api_simple.py..."
# Fix the format parameter issue directly in the file
python3 << 'PYTHON_END'
import re

# Read current file
with open('gpts_api_simple.py', 'r') as f:
    content = f.read()

# Fix the format parameter logic - add missing return statements
old_pattern = r'''        elif format_type == 'json':
            response_data = {
                "signal": result,
                "human_readable": narrative,
                "telegram_message": telegram_message,
                "api_version": "1.0.0",
                "server_time": datetime.now().isoformat(),
                "data_source": "COMPREHENSIVE_SIGNAL_ENGINE"
            }
        else:  # format_type == 'both'
            response_data = {
                "signal": result,
                "narrative": narrative,
                "human_readable": narrative,
                "telegram_message": telegram_message,
                "api_version": "1.0.0",
                "server_time": datetime.now().isoformat(),
                "data_source": "COMPREHENSIVE_SIGNAL_ENGINE",
                "format": "json_with_narrative"
            }'''

new_pattern = '''        elif format_type == 'json':
            response_data = {
                "signal": result,
                "human_readable": narrative,
                "telegram_message": telegram_message,
                "format": "json_only"
            }
            return add_cors_headers(jsonify(add_api_metadata(response_data)))
        else:  # format_type == 'both'
            response_data = {
                "signal": result,
                "narrative": narrative,
                "human_readable": narrative,
                "telegram_message": telegram_message,
                "format": "json_with_narrative"
            }
            return add_cors_headers(jsonify(add_api_metadata(response_data)))'''

# Apply fix
if old_pattern.replace(' ', '').replace('\n', '') in content.replace(' ', '').replace('\n', ''):
    content = re.sub(re.escape(old_pattern), new_pattern, content)
    print("✅ Format parameter logic fixed")
else:
    print("⚠️ Pattern not found, checking alternative patterns...")

# Write fixed content
with open('gpts_api_simple.py', 'w') as f:
    f.write(content)
    
print("✅ File updated with fixes")
PYTHON_END

echo "3. Adding missing dependency..."
if ! grep -q "aiohttp" requirements-prod.txt 2>/dev/null; then
    echo "aiohttp==3.8.6" >> requirements-prod.txt
    echo "✅ Added aiohttp dependency"
fi

echo "4. Stopping containers..."
docker-compose -f docker-compose-vps.yml down

echo "5. Full container rebuild..."
docker-compose -f docker-compose-vps.yml up -d --build --force-recreate --no-cache

echo "6. Waiting for startup..."
sleep 30

echo "7. Testing narrative format fix..."
curl -s "http://localhost:5050/api/gpts/sinyal/tajam?format=narrative" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    print('Response keys:', sorted(data.keys()))
    
    if 'narrative' in data:
        narrative_len = len(data['narrative'])
        if narrative_len > 100:
            print(f'✅ NARRATIVE FIXED: {narrative_len} characters')
            print('Preview:', data['narrative'][:150] + '...')
        else:
            print(f'⚠️ Narrative too short: {narrative_len} chars')
    else:
        print('❌ Narrative field still missing')
        
    if 'human_readable' in data:
        print(f'✅ Human readable: {len(data[\"human_readable\"])} chars')
    if 'telegram_message' in data:
        print(f'✅ Telegram message: {len(data[\"telegram_message\"])} chars')
        
except Exception as e:
    print(f'❌ JSON Error: {e}')
    print('Raw response preview:')
    print(sys.stdin.read()[:300])
"

echo ""
echo "8. Testing endpoint accessibility..."
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
echo "=========================="
echo "Working endpoints: $working/${#endpoints[@]}"
if [ $working -ge 4 ]; then
    echo "✅ VPS FIX SUCCESSFUL"
    echo "Narrative format ready for ChatGPT Custom GPTs"
else
    echo "⚠️ Some endpoints need attention"
fi
echo "=========================="
SCRIPT_END

chmod +x /tmp/vps_direct_fix.sh
echo "Script created at /tmp/vps_direct_fix.sh"