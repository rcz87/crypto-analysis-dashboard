#!/bin/bash

echo "🔍 ADDING DATABASE TARGET DEBUG TO HEALTH CHECK"
echo "==============================================="
echo ""

# Create Python script to add debug info
cat > /tmp/add_debug.py << 'PYTHON'
with open('/root/crypto-analysis-dashboard/routes.py', 'r') as f:
    lines = f.readlines()

new_lines = []
for i, line in enumerate(lines):
    new_lines.append(line)
    
    # Add debug after getting database_url (around line 43-45)
    if 'database_url = current_app.config.get("SQLALCHEMY_DATABASE_URI")' in line:
        # Add debug lines after this
        new_lines.append('        from sqlalchemy.engine import make_url\n')
        new_lines.append('        \n')
        new_lines.append('        # 🔎 DEBUG: identify host/db being used (without exposing password)\n')
        new_lines.append('        try:\n')
        new_lines.append('            parsed = make_url(database_url)\n')
        new_lines.append('            db_target = {\n')
        new_lines.append('                "drivername": parsed.drivername,\n')
        new_lines.append('                "host": parsed.host,\n')
        new_lines.append('                "port": parsed.port,\n')
        new_lines.append('                "database": parsed.database\n')
        new_lines.append('            }\n')
        new_lines.append('            logger.info(f"[HEALTH] Using DB target: {db_target}")\n')
        new_lines.append('            # Temporarily add to output for debugging\n')
        new_lines.append('            components["db_target"] = db_target\n')
        new_lines.append('        except Exception as _:\n')
        new_lines.append('            pass\n')
        new_lines.append('        \n')

with open('/root/crypto-analysis-dashboard/routes.py', 'w') as f:
    f.writelines(new_lines)

print("✅ Debug code added to health check")
PYTHON

echo "1. Adding debug code to routes.py..."
python3 /tmp/add_debug.py

echo ""
echo "2. Restarting service..."
systemctl restart cryptoapi.service

echo ""
echo "3. Waiting for service to start..."
sleep 5

echo ""
echo "4. Testing health endpoint with debug info..."
curl -s http://127.0.0.1:5050/health | jq

echo ""
echo "5. Checking service logs for database target..."
journalctl -u cryptoapi -n 50 | grep -i "HEALTH.*Using DB target"

echo ""
echo "✅ DEBUG INFO ADDED"
echo ""
echo "Look for 'db_target' in the health response above."
echo "It should show which database host is being used:"
echo "- If 'localhost' -> Still using wrong config"
echo "- If 'ep-gentle-boat-*.neon.tech' -> Using correct Neon database"