#!/bin/bash

echo "🔧 COMPLETE FIX FOR VPS DATABASE CONNECTION"
echo "==========================================="
echo ""

# 1. Install psycopg2-binary
echo "1. Installing psycopg2-binary..."
pip3 install psycopg2-binary

# 2. Find and update the REAL database URL in routes.py
echo ""
echo "2. Checking current database URL in routes.py..."
grep -n "ep-billowing-sunset" /root/crypto-analysis-dashboard/routes.py && {
    echo "Found placeholder URL, fixing..."
    sed -i 's|ep-billowing-sunset-xxxx\.us-east-2\.aws\.neon\.tech|ep-gentle-boat-a10aawfh.ap-southeast-1.aws.neon.tech|g' /root/crypto-analysis-dashboard/routes.py
    sed -i 's|neondb_owner:YOUR_ACTUAL_NEON_PASSWORD|crypto_new_owner:WgOOUP9V5X9p|g' /root/crypto-analysis-dashboard/routes.py
    sed -i 's|/neondb|/crypto_dashboard_new|g' /root/crypto-analysis-dashboard/routes.py
}

# 3. Fix ALL Python files
echo ""
echo "3. Fixing all Python files with correct Neon URL..."
find /root/crypto-analysis-dashboard -name "*.py" -type f -exec sed -i \
    -e 's|ep-billowing-sunset-xxxx\.us-east-2\.aws\.neon\.tech|ep-gentle-boat-a10aawfh.ap-southeast-1.aws.neon.tech|g' \
    -e 's|neondb_owner:YOUR_ACTUAL_NEON_PASSWORD|crypto_new_owner:WgOOUP9V5X9p|g' \
    -e 's|/neondb|/crypto_dashboard_new|g' \
    -e 's|postgresql://trading_user:[^@]*@localhost:5432/trading_db|postgresql://crypto_new_owner:WgOOUP9V5X9p@ep-gentle-boat-a10aawfh.ap-southeast-1.aws.neon.tech/crypto_dashboard_new?sslmode=require|g' {} \;

# 4. Set correct .env
echo ""
echo "4. Setting correct .env file..."
cat > /root/crypto-analysis-dashboard/.env << 'ENVFILE'
DATABASE_URL=postgresql://crypto_new_owner:WgOOUP9V5X9p@ep-gentle-boat-a10aawfh.ap-southeast-1.aws.neon.tech/crypto_dashboard_new?sslmode=require
SQLALCHEMY_DATABASE_URI=postgresql://crypto_new_owner:WgOOUP9V5X9p@ep-gentle-boat-a10aawfh.ap-southeast-1.aws.neon.tech/crypto_dashboard_new?sslmode=require
API_KEY_REQUIRED=true
API_KEY=sk-2024-crypto-analysis-secret-key
FLASK_APP=main:app
FLASK_ENV=production
ENVFILE

# 5. Update systemd service
echo ""
echo "5. Updating systemd service..."
cat > /etc/systemd/system/cryptoapi.service << 'SERVICE'
[Unit]
Description=Crypto Analysis Dashboard API
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/crypto-analysis-dashboard
Environment="DATABASE_URL=postgresql://crypto_new_owner:WgOOUP9V5X9p@ep-gentle-boat-a10aawfh.ap-southeast-1.aws.neon.tech/crypto_dashboard_new?sslmode=require"
Environment="SQLALCHEMY_DATABASE_URI=postgresql://crypto_new_owner:WgOOUP9V5X9p@ep-gentle-boat-a10aawfh.ap-southeast-1.aws.neon.tech/crypto_dashboard_new?sslmode=require"
Environment="API_KEY_REQUIRED=true"
Environment="API_KEY=sk-2024-crypto-analysis-secret-key"
ExecStart=/usr/bin/python3 -m gunicorn --bind 0.0.0.0:5050 --workers 4 --timeout 120 main:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SERVICE

# 6. Clear Python cache
echo ""
echo "6. Clearing Python cache..."
find /root/crypto-analysis-dashboard -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find /root/crypto-analysis-dashboard -name "*.pyc" -delete 2>/dev/null || true

# 7. Test direct connection
echo ""
echo "7. Testing direct database connection..."
python3 << 'PYTEST'
import sqlalchemy as sa
url = "postgresql://crypto_new_owner:WgOOUP9V5X9p@ep-gentle-boat-a10aawfh.ap-southeast-1.aws.neon.tech/crypto_dashboard_new?sslmode=require"
try:
    engine = sa.create_engine(url, pool_pre_ping=True)
    with engine.connect() as conn:
        result = conn.execute(sa.text("SELECT 1"))
        print("✅ Direct connection to Neon database successful!")
except Exception as e:
    print(f"❌ Connection failed: {e}")
PYTEST

# 8. Restart service
echo ""
echo "8. Restarting service..."
systemctl daemon-reload
systemctl restart cryptoapi

# 9. Wait for service
echo "9. Waiting for service to start..."
sleep 7

# 10. Final test
echo ""
echo "10. Final health check..."
echo "==================================="
curl -s http://127.0.0.1:5050/health | jq

echo ""
echo "==================================="
echo "If database is still unhealthy, check:"
echo "1. journalctl -u cryptoapi -n 50 | grep -i error"
echo "2. Check if Neon database is accessible from VPS"
echo "3. Verify credentials are correct"