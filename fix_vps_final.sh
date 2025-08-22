#!/bin/bash

echo "🔧 FINAL VPS FIX - USE app.db DIRECTLY"
echo "======================================"
echo ""

# Create Python script to fix the health route
cat > /tmp/fix_health_final.py << 'PYTHON'
# Read routes.py
with open('/root/crypto-analysis-dashboard/routes.py', 'r') as f:
    lines = f.readlines()

# Find and replace health function
new_lines = []
skip_lines = 0
found_health = False

for i, line in enumerate(lines):
    if skip_lines > 0:
        skip_lines -= 1
        continue
    
    if '@core_bp.route("/health"' in line:
        found_health = True
        # Keep the decorator
        new_lines.append(line)
        # Add new simplified function
        new_lines.append('def health_check():\n')
        new_lines.append('    """Health check using app.db directly"""\n')
        new_lines.append('    from sqlalchemy import text\n')
        new_lines.append('    from datetime import datetime\n')
        new_lines.append('    import requests\n')
        new_lines.append('    \n')
        new_lines.append('    components = {}\n')
        new_lines.append('    overall_status = "healthy"\n')
        new_lines.append('    \n')
        new_lines.append('    # Database check - use app.db directly\n')
        new_lines.append('    try:\n')
        new_lines.append('        from app import db\n')
        new_lines.append('        with db.engine.connect() as conn:\n')
        new_lines.append('            result = conn.execute(text("SELECT 1"))\n')
        new_lines.append('            result.fetchone()\n')
        new_lines.append('        components["database"] = {\n')
        new_lines.append('            "status": "healthy",\n')
        new_lines.append('            "message": "Database connection successful"\n')
        new_lines.append('        }\n')
        new_lines.append('    except Exception as e:\n')
        new_lines.append('        components["database"] = {\n')
        new_lines.append('            "status": "unhealthy",\n')
        new_lines.append('            "message": f"Connection failed: {str(e)[:100]}"\n')
        new_lines.append('        }\n')
        new_lines.append('        overall_status = "unhealthy"\n')
        new_lines.append('    \n')
        new_lines.append('    # OKX API check\n')
        new_lines.append('    try:\n')
        new_lines.append('        response = requests.get("https://www.okx.com/api/v5/public/time", timeout=5)\n')
        new_lines.append('        if response.status_code == 200:\n')
        new_lines.append('            components["okx_api"] = {\n')
        new_lines.append('                "status": "healthy",\n')
        new_lines.append('                "message": "OKX API connection successful"\n')
        new_lines.append('            }\n')
        new_lines.append('        else:\n')
        new_lines.append('            components["okx_api"] = {\n')
        new_lines.append('                "status": "unhealthy",\n')
        new_lines.append('                "message": f"OKX API returned status {response.status_code}"\n')
        new_lines.append('            }\n')
        new_lines.append('            overall_status = "unhealthy"\n')
        new_lines.append('    except Exception as e:\n')
        new_lines.append('        components["okx_api"] = {\n')
        new_lines.append('            "status": "unhealthy",\n')
        new_lines.append('            "message": f"OKX API failed: {str(e)[:50]}"\n')
        new_lines.append('        }\n')
        new_lines.append('        overall_status = "unhealthy"\n')
        new_lines.append('    \n')
        new_lines.append('    return jsonify({\n')
        new_lines.append('        "status": overall_status,\n')
        new_lines.append('        "components": components,\n')
        new_lines.append('        "version": current_app.config.get("API_VERSION", "2.0.0"),\n')
        new_lines.append('        "timestamp": datetime.utcnow().isoformat(),\n')
        new_lines.append('        "uptime": "N/A"\n')
        new_lines.append('    }), 200 if overall_status == "healthy" else 503\n')
        new_lines.append('\n')
        
        # Skip the old function (approximately next 40-50 lines until next @)
        j = i + 1
        while j < len(lines) and not lines[j].strip().startswith('@'):
            j += 1
        skip_lines = j - i - 1
    else:
        new_lines.append(line)

if found_health:
    # Write the modified file
    with open('/root/crypto-analysis-dashboard/routes.py', 'w') as f:
        f.writelines(new_lines)
    print("✅ Health route fixed to use app.db directly!")
else:
    print("⚠️ Health route not found")
PYTHON

echo "1. Fixing health route in routes.py..."
python3 /tmp/fix_health_final.py

echo ""
echo "2. Restarting service..."
systemctl restart cryptoapi.service

echo ""
echo "3. Waiting for service to start..."
sleep 5

echo ""
echo "4. Testing endpoints..."
echo ""
echo "=== Health Check ==="
curl -s http://127.0.0.1:5050/health | jq

echo ""
echo "=== Status Check ==="
curl -s http://127.0.0.1:5050/api/gpts/status | jq

echo ""
echo "✅ DONE! Database should now show 'healthy' status"