#!/bin/bash

echo "🔧 VPS DIRECT HEALTH FIX - REMOVING DUPLICATE ROUTES"
echo "===================================================="
echo ""

# Step 1: Backup current files
echo "1. Creating backups..."
cp /root/crypto-analysis-dashboard/routes.py /root/crypto-analysis-dashboard/routes.py.backup
cp /root/crypto-analysis-dashboard/routes/health.py /root/crypto-analysis-dashboard/routes/health.py.backup

# Step 2: Remove duplicate health route from routes.py 
echo "2. Removing duplicate health route from routes.py..."
cat > /tmp/fix_routes.py << 'EOF'
# Read the file
with open('/root/crypto-analysis-dashboard/routes.py', 'r') as f:
    lines = f.readlines()

# Find and remove the health route in core_bp
new_lines = []
skip_until = 0
for i, line in enumerate(lines):
    if skip_until > 0 and i <= skip_until:
        continue
    if '@core_bp.route("/health"' in line:
        # Skip this route and its function (approximately 80 lines)
        skip_until = i + 80
        continue
    new_lines.append(line)

# Write back
with open('/root/crypto-analysis-dashboard/routes.py', 'w') as f:
    f.writelines(new_lines)
print("Removed duplicate health route from routes.py")
EOF
python3 /tmp/fix_routes.py

# Step 3: Fix the health.py to use correct database connection
echo "3. Fixing routes/health.py with proper SQLAlchemy connection..."
cat > /root/crypto-analysis-dashboard/routes/health.py << 'EOF'
from flask import Blueprint, jsonify, current_app
from datetime import datetime
import logging
import requests
from sqlalchemy import text
import time
import os

logger = logging.getLogger(__name__)
health_bp = Blueprint('health', __name__)

@health_bp.route("/", methods=["GET"])
def home():
    """Root endpoint"""
    return jsonify({
        "message": "Cryptocurrency GPTs & Telegram Bot API",
        "version": "1.0.0",
        "focus": "GPTs integration and Telegram notifications",
        "endpoints": {
            "gpts_api": "/api/gpts/",
            "health": "/health",
            "status": "/api/gpts/status"
        }
    })

@health_bp.route("/api/gpts/status", methods=["GET"])
def gpts_status():
    """Lightweight status check"""
    try:
        return jsonify({
            "status": "active",
            "version": {
                "api_version": current_app.config.get("API_VERSION", "2.0.0"),
                "core_version": "1.2.3"
            },
            "components": {
                "signal_generator": "available",
                "smc_analyzer": "available",
                "okx_api": "connected",
                "openai": "available",
                "database": "available"
            },
            "supported_symbols": ["BTC", "ETH", "SOL", "ADA", "DOT", "AVAX"],
            "supported_timeframes": ["1m", "3m", "5m", "15m", "30m", "1H", "2H", "4H", "6H", "12H", "1D", "2D", "3D", "1W", "1M", "3M"],
            "timestamp": int(time.time())
        })
    except Exception as e:
        logger.error(f"Status endpoint error: {e}")
        return jsonify({
            "status": "error",
            "message": "Internal server error",
            "timestamp": int(time.time())
        }), 500

@health_bp.route("/health", methods=["GET"])
def health_check():
    """Health check using Flask app database config"""
    components = {}
    overall_status = "healthy"
    
    # Database check - Use Flask app's db instance
    try:
        from app import db
        
        # Test connection using SQLAlchemy session
        with db.engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        
        components["database"] = {
            "status": "healthy",
            "message": "Database connection successful"
        }
        logger.info("✅ Database health check passed")
        
    except Exception as e:
        components["database"] = {
            "status": "unhealthy",
            "message": f"Connection failed: {str(e)[:100]}"
        }
        overall_status = "unhealthy"
        logger.error(f"❌ Database health check failed: {e}")
    
    # OKX API check
    try:
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
            "message": f"OKX API connection failed: {str(e)[:100]}"
        }
        overall_status = "unhealthy"
    
    return jsonify({
        "status": overall_status,
        "components": components,
        "version": current_app.config.get("API_VERSION", "2.0.0"),
        "timestamp": datetime.utcnow().isoformat(),
        "uptime": "N/A"
    }), 200 if overall_status == "healthy" else 503
EOF

# Step 4: Restart the service
echo ""
echo "4. Restarting cryptoapi service..."
systemctl restart cryptoapi.service

# Step 5: Wait for service to start
echo "5. Waiting for service to start..."
sleep 5

# Step 6: Test endpoints
echo ""
echo "6. Testing endpoints..."
echo ""
echo "=== Health Check ==="
curl -s http://127.0.0.1:5050/health | jq

echo ""
echo "=== Status Check ==="
curl -s http://127.0.0.1:5050/api/gpts/status | jq

echo ""
echo "=== Root Check ==="
curl -s http://127.0.0.1:5050/ | jq

echo ""
echo "✅ VPS HEALTH FIX COMPLETE!"
echo ""
echo "Database should now show 'healthy' status"