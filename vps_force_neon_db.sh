#!/bin/bash

echo "🔧 FORCE NEON DATABASE CONNECTION"
echo "================================="
echo ""

# 1. Stop the service first
echo "1. Stopping service..."
systemctl stop cryptoapi

# 2. Remove ALL localhost references from .env
echo "2. Cleaning .env file..."
if [ -f /root/crypto-analysis-dashboard/.env ]; then
    cp /root/crypto-analysis-dashboard/.env /root/crypto-analysis-dashboard/.env.old
    # Create new .env with ONLY Neon database
    cat > /root/crypto-analysis-dashboard/.env << 'ENVFILE'
# Database Configuration - NEON ONLY
DATABASE_URL=postgresql://crypto_new_owner:WgOOUP9V5X9p@ep-gentle-boat-a10aawfh.ap-southeast-1.aws.neon.tech/crypto_dashboard_new?sslmode=require
SQLALCHEMY_DATABASE_URI=postgresql://crypto_new_owner:WgOOUP9V5X9p@ep-gentle-boat-a10aawfh.ap-southeast-1.aws.neon.tech/crypto_dashboard_new?sslmode=require

# API Configuration
API_KEY_REQUIRED=true
API_KEY=sk-2024-crypto-analysis-secret-key
RATE_LIMIT_DEFAULT=120
LIMITER_STORAGE_URI=memory://

# Flask Configuration
FLASK_APP=main:app
FLASK_ENV=production
API_VERSION=2.0.0
ENVFILE
    echo "✅ .env file cleaned - using Neon database only"
fi

# 3. Force update app.py to use Neon
echo "3. Updating app.py to force Neon connection..."
cat > /tmp/fix_app.py << 'PYTHON'
import re

with open('/root/crypto-analysis-dashboard/app.py', 'r') as f:
    content = f.read()

# Find the database configuration section
if 'SQLALCHEMY_DATABASE_URI' in content:
    # Replace any localhost references
    content = re.sub(
        r'app\.config\["SQLALCHEMY_DATABASE_URI"\]\s*=.*',
        'app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "postgresql://crypto_new_owner:WgOOUP9V5X9p@ep-gentle-boat-a10aawfh.ap-southeast-1.aws.neon.tech/crypto_dashboard_new?sslmode=require")',
        content
    )
    
    # Also check for any fallback to localhost
    content = content.replace('localhost:5432', 'ep-gentle-boat-a10aawfh.ap-southeast-1.aws.neon.tech')
    content = content.replace('localhost', 'ep-gentle-boat-a10aawfh.ap-southeast-1.aws.neon.tech')
    
    with open('/root/crypto-analysis-dashboard/app.py', 'w') as f:
        f.write(content)
    print("✅ app.py updated to use Neon database")
else:
    print("⚠️  Could not find SQLALCHEMY_DATABASE_URI in app.py")
PYTHON

python3 /tmp/fix_app.py

# 4. Update systemd service with explicit environment
echo "4. Updating systemd service..."
cat > /etc/systemd/system/cryptoapi.service << 'SERVICE'
[Unit]
Description=Crypto Analysis Dashboard API
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/crypto-analysis-dashboard
# Force environment variables
Environment="PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
Environment="DATABASE_URL=postgresql://crypto_new_owner:WgOOUP9V5X9p@ep-gentle-boat-a10aawfh.ap-southeast-1.aws.neon.tech/crypto_dashboard_new?sslmode=require"
Environment="SQLALCHEMY_DATABASE_URI=postgresql://crypto_new_owner:WgOOUP9V5X9p@ep-gentle-boat-a10aawfh.ap-southeast-1.aws.neon.tech/crypto_dashboard_new?sslmode=require"
Environment="API_KEY_REQUIRED=true"
Environment="API_KEY=sk-2024-crypto-analysis-secret-key"
Environment="FLASK_APP=main:app"
Environment="FLASK_ENV=production"
# Don't load .env file
EnvironmentFile=-/dev/null
ExecStart=/usr/bin/python3 -m gunicorn --bind 0.0.0.0:5050 --workers 4 --timeout 120 --reload main:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SERVICE

# 5. Clear Python cache
echo "5. Clearing Python cache..."
find /root/crypto-analysis-dashboard -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find /root/crypto-analysis-dashboard -name "*.pyc" -delete 2>/dev/null || true

# 6. Reload and start service
echo "6. Reloading and starting service..."
systemctl daemon-reload
systemctl start cryptoapi

# 7. Wait for startup
echo "7. Waiting for service to start..."
sleep 7

# 8. Test endpoints
echo ""
echo "8. Testing endpoints..."
echo ""
echo "=== Health Check ==="
curl -s http://127.0.0.1:5050/health | jq

echo ""
echo "=== Service Status ==="
systemctl status cryptoapi --no-pager | head -15

echo ""
echo "=== Checking logs for database connection ==="
journalctl -u cryptoapi -n 20 | grep -i "database\|neon\|localhost" | tail -5

echo ""
echo "✅ COMPLETE - Database should now connect to Neon!"