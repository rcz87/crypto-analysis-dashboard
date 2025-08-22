#!/bin/bash

# VPS DIRECT DATABASE FIX
# Jalankan script ini LANGSUNG di VPS untuk fix database connection

echo "🔧 VPS DIRECT DATABASE FIX"
echo "=========================="
echo ""

# Step 1: Update routes/health.py untuk gunakan SQLAlchemy only
echo "1. Fixing routes/health.py..."
cat > /root/crypto-analysis-dashboard/routes/health.py << 'EOF'
from flask import Blueprint, jsonify, current_app
from datetime import datetime
import logging
import requests
from sqlalchemy import text
import time

logger = logging.getLogger(__name__)
health_bp = Blueprint('health', __name__)

@health_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint dengan SQLAlchemy-only connection
    """
    components = {}
    overall_status = "healthy"
    
    # Database check - USING SQLALCHEMY ONLY
    try:
        from app import db
        
        # Test database connection via SQLAlchemy
        with db.engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
            
        components["database"] = {
            "status": "healthy",
            "message": "SQLAlchemy connection successful"
        }
        logger.info("✅ Database health check passed (SQLAlchemy)")
        
    except Exception as e:
        components["database"] = {
            "status": "unhealthy", 
            "message": f"SQLAlchemy connection failed: {str(e)[:100]}"
        }
        overall_status = "unhealthy"
        logger.error(f"❌ Database health check failed: {e}")
    
    # OKX API check
    try:
        okx_api_url = "https://www.okx.com/api/v5/public/time"
        response = requests.get(okx_api_url, timeout=5)
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
    
    try:
        api_version = current_app.config.get("API_VERSION", "2.0.0")
        timestamp = datetime.utcnow().isoformat()
        status_code = 200 if overall_status == "healthy" else 503
        
        return jsonify({
            "status": overall_status,
            "components": components,
            "version": api_version,
            "timestamp": timestamp,
            "uptime": "N/A"
        }), status_code
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Health check error: {str(e)}",
            "timestamp": datetime.utcnow().isoformat()
        }), 500
EOF

# Step 2: Update systemd service environment
echo ""
echo "2. Updating systemd service environment..."
cat > /etc/systemd/system/cryptoapi.service << 'EOF'
[Unit]
Description=Crypto Analysis Dashboard API
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/crypto-analysis-dashboard
Environment="PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
Environment="PYTHONPATH=/root/crypto-analysis-dashboard"
Environment="FLASK_APP=main:app"
Environment="FLASK_ENV=production"
Environment="DATABASE_URL=postgresql://crypto_new_owner:WgOOUP9V5X9p@ep-gentle-boat-a10aawfh.ap-southeast-1.aws.neon.tech/crypto_dashboard_new?sslmode=require"
Environment="SQLALCHEMY_DATABASE_URI=postgresql://crypto_new_owner:WgOOUP9V5X9p@ep-gentle-boat-a10aawfh.ap-southeast-1.aws.neon.tech/crypto_dashboard_new?sslmode=require"
Environment="API_KEY_REQUIRED=true"
Environment="API_KEY=sk-2024-crypto-analysis-secret-key"
Environment="RATE_LIMIT_DEFAULT=120"
Environment="LIMITER_STORAGE_URI=memory://"
ExecStart=/usr/bin/python3 -m gunicorn --bind 0.0.0.0:5050 --workers 4 --timeout 120 --reload main:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Step 3: Reload systemd and restart service
echo ""
echo "3. Reloading systemd and restarting service..."
systemctl daemon-reload
systemctl restart cryptoapi.service

# Step 4: Wait for service to start
echo ""
echo "4. Waiting for service to start..."
sleep 5

# Step 5: Test endpoints
echo ""
echo "5. Testing endpoints..."
echo ""
echo "Health Check:"
curl -s http://127.0.0.1:5050/health | jq

echo ""
echo "Status Check:"
curl -s http://127.0.0.1:5050/api/gpts/status | jq

echo ""
echo "✅ VPS DIRECT FIX COMPLETE!"
echo ""
echo "If database still shows 'unhealthy', check:"
echo "1. Neon database credentials are correct"
echo "2. Neon database is accessible from VPS"
echo "3. PostgreSQL SSL connection is working"