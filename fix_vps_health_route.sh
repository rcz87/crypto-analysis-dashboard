#!/bin/bash

echo "🔧 FIXING VPS HEALTH ROUTE IN routes.py"
echo "========================================"
echo ""

# Backup the original file
echo "1. Creating backup..."
cp /root/crypto-analysis-dashboard/routes.py /root/crypto-analysis-dashboard/routes.py.backup_$(date +%Y%m%d_%H%M%S)

# Create Python script to fix the health route
echo "2. Fixing health route to use SQLAlchemy only..."
cat > /tmp/fix_health_route.py << 'PYTHON'
import re

# Read the routes.py file
with open('/root/crypto-analysis-dashboard/routes.py', 'r') as f:
    content = f.read()

# Define the new health function
new_health_function = '''@core_bp.route("/health", methods=["GET"])
def health_check():
    """Health check using SQLAlchemy only - NO psycopg2"""
    from sqlalchemy import text
    from flask import jsonify
    
    components = {}
    overall_status = "healthy"

    # DB check via SQLAlchemy (using DATABASE_URL / SQLALCHEMY_DATABASE_URI)
    try:
        from app import db
        with db.engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        components["database"] = {
            "status": "healthy",
            "message": "SQLAlchemy connection successful"
        }
    except Exception as e:
        components["database"] = {
            "status": "unhealthy",
            "message": f"Connection failed: {str(e)[:100]}"
        }
        overall_status = "unhealthy"

    # OKX API check
    try:
        import requests
        response = requests.get("https://www.okx.com/api/v5/public/time", timeout=5)
        if response.status_code == 200:
            components["okx_api"] = {
                "status": "healthy",
                "message": "OKX API connection successful"
            }
        else:
            components["okx_api"] = {
                "status": "unhealthy",
                "message": f"OKX API returned status {response.status_code}"
            }
            overall_status = "unhealthy"
    except Exception as e:
        components["okx_api"] = {
            "status": "unhealthy",
            "message": f"OKX API failed: {str(e)[:50]}"
        }
        overall_status = "unhealthy"

    return jsonify({
        "status": overall_status,
        "components": components,
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat()
    })'''

# Find and replace the health route function
# Look for the pattern: @core_bp.route("/health"...) and replace everything until the next route
pattern = r'@core_bp\.route\("/health"[^@]*?(?=\n@|\nif __name__|$)'
replacement_count = len(re.findall(pattern, content, re.DOTALL))

if replacement_count > 0:
    content = re.sub(pattern, new_health_function, content, count=1, flags=re.DOTALL)
    
    # Write the modified content back
    with open('/root/crypto-analysis-dashboard/routes.py', 'w') as f:
        f.write(content)
    
    print(f"✅ Successfully replaced health route function")
else:
    print("⚠️ Health route not found in expected format")

PYTHON

python3 /tmp/fix_health_route.py

# Step 3: Verify the change
echo ""
echo "3. Verifying the change..."
echo "Showing lines 95-130 of routes.py:"
sed -n '95,130p' /root/crypto-analysis-dashboard/routes.py | nl

# Step 4: Restart the service
echo ""
echo "4. Restarting cryptoapi service..."
systemctl restart cryptoapi.service

# Step 5: Wait for service to start
echo "5. Waiting for service to start..."
sleep 5

# Step 6: Test the health endpoint
echo ""
echo "6. Testing health endpoint..."
echo ""
echo "=== Health Check ==="
curl -s http://127.0.0.1:5050/health | jq

echo ""
echo "=== Status Check ==="
curl -s http://127.0.0.1:5050/api/gpts/status | jq

echo ""
echo "✅ FIX COMPLETE!"
echo ""
echo "The health route now uses SQLAlchemy-only connection."
echo "No more psycopg2.connect() fallbacks!"
echo "Database should show 'healthy' status."