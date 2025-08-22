#!/bin/bash

echo "🔍 CHECKING ENVIRONMENT VARIABLES IN SERVICE"
echo "==========================================="
echo ""

echo "1. Checking systemd service environment..."
systemctl show cryptoapi.service | grep -E "Environment|DATABASE_URL|SQLALCHEMY"

echo ""
echo "2. Checking if app.py is reading the correct config..."
cat > /tmp/check_app.py << 'PYTHON'
import sys
sys.path.insert(0, '/root/crypto-analysis-dashboard')

# Check what app.py sees
try:
    from app import app
    with app.app_context():
        db_uri = app.config.get('SQLALCHEMY_DATABASE_URI')
        if db_uri:
            # Parse without exposing password
            if 'localhost' in db_uri:
                print("❌ ERROR: SQLALCHEMY_DATABASE_URI points to localhost!")
                print(f"   URI starts with: {db_uri[:50]}...")
            elif 'neon.tech' in db_uri:
                print("✅ GOOD: SQLALCHEMY_DATABASE_URI points to Neon!")
                print(f"   URI contains: ...neon.tech...")
            else:
                print(f"⚠️  UNKNOWN: URI starts with: {db_uri[:30]}...")
        else:
            print("❌ ERROR: SQLALCHEMY_DATABASE_URI is not set in app config!")
            
        # Check environment
        import os
        env_db_url = os.environ.get('DATABASE_URL')
        env_sqlalchemy = os.environ.get('SQLALCHEMY_DATABASE_URI')
        
        print("\n📋 Environment variables:")
        if env_db_url:
            if 'localhost' in env_db_url:
                print("   DATABASE_URL = localhost (WRONG!)")
            elif 'neon.tech' in env_db_url:
                print("   DATABASE_URL = neon.tech (CORRECT!)")
        else:
            print("   DATABASE_URL = NOT SET")
            
        if env_sqlalchemy:
            if 'localhost' in env_sqlalchemy:
                print("   SQLALCHEMY_DATABASE_URI = localhost (WRONG!)")
            elif 'neon.tech' in env_sqlalchemy:
                print("   SQLALCHEMY_DATABASE_URI = neon.tech (CORRECT!)")
        else:
            print("   SQLALCHEMY_DATABASE_URI = NOT SET")
            
except Exception as e:
    print(f"Error checking app config: {e}")
PYTHON

python3 /tmp/check_app.py

echo ""
echo "3. Checking .env file..."
if [ -f /root/crypto-analysis-dashboard/.env ]; then
    echo "📄 .env file exists. Checking database entries:"
    grep -E "DATABASE_URL|SQLALCHEMY" /root/crypto-analysis-dashboard/.env | sed 's/=.*@/=***@/g'
else
    echo "⚠️  No .env file found"
fi

echo ""
echo "4. Quick fix - Update systemd service with correct DATABASE_URL..."
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
ExecStart=/usr/bin/python3 -m gunicorn --bind 0.0.0.0:5050 --workers 4 --timeout 120 --reload main:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo "✅ Updated systemd service with Neon database URL"

echo ""
echo "5. Reloading and restarting service..."
systemctl daemon-reload
systemctl restart cryptoapi.service
sleep 5

echo ""
echo "6. Testing health endpoint..."
curl -s http://127.0.0.1:5050/health | jq

echo ""
echo "If database still shows 'unhealthy', there might be a .env file overriding the systemd environment."