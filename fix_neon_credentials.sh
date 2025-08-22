#!/bin/bash

echo "🔧 FIXING NEON DATABASE CREDENTIALS"
echo "==================================="
echo ""

# The CORRECT Neon credentials (already URL-encoded)
NEON_DB_URL="postgresql://crypto_new_owner:WgOOUP9V5X9p@ep-gentle-boat-a10aawfh.ap-southeast-1.aws.neon.tech/crypto_dashboard_new?sslmode=require"

echo "1. Updating .env file with correct Neon credentials..."
cat > /root/crypto-analysis-dashboard/.env << EOF
DATABASE_URL=${NEON_DB_URL}
SQLALCHEMY_DATABASE_URI=${NEON_DB_URL}
API_KEY_REQUIRED=true
API_KEY=sk-2024-crypto-analysis-secret-key
FLASK_APP=main:app
FLASK_ENV=production
EOF

echo "✅ .env updated with correct Neon URL"

echo ""
echo "2. Updating systemd service with correct credentials..."
cat > /etc/systemd/system/cryptoapi.service << EOF
[Unit]
Description=Crypto Analysis Dashboard API
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/crypto-analysis-dashboard
Environment="PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
Environment="DATABASE_URL=${NEON_DB_URL}"
Environment="SQLALCHEMY_DATABASE_URI=${NEON_DB_URL}"
Environment="API_KEY_REQUIRED=true"
Environment="API_KEY=sk-2024-crypto-analysis-secret-key"
Environment="FLASK_APP=main:app"
Environment="FLASK_ENV=production"
ExecStart=/usr/bin/python3 -m gunicorn --bind 0.0.0.0:5050 --workers 4 --timeout 120 main:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo "✅ Systemd service updated with correct Neon URL"

echo ""
echo "3. Fixing app.py to use environment variable properly..."
python3 << 'PYTHON'
import re

with open('/root/crypto-analysis-dashboard/app.py', 'r') as f:
    content = f.read()

# Replace any hardcoded database URLs with environment variable
content = re.sub(
    r'app\.config\["SQLALCHEMY_DATABASE_URI"\]\s*=\s*["\'].*?["\']',
    'app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", os.environ.get("SQLALCHEMY_DATABASE_URI"))',
    content
)

# Make sure os is imported
if 'import os' not in content:
    content = 'import os\n' + content

with open('/root/crypto-analysis-dashboard/app.py', 'w') as f:
    f.write(content)

print("✅ app.py updated to use environment variables")
PYTHON

echo ""
echo "4. Testing connection directly..."
python3 << 'PYTHON'
import os
os.environ['DATABASE_URL'] = 'postgresql://crypto_new_owner:WgOOUP9V5X9p@ep-gentle-boat-a10aawfh.ap-southeast-1.aws.neon.tech/crypto_dashboard_new?sslmode=require'

try:
    import sqlalchemy as sa
    engine = sa.create_engine(os.environ['DATABASE_URL'])
    with engine.connect() as conn:
        result = conn.execute(sa.text("SELECT 1"))
        print("✅ Direct database connection successful!")
except Exception as e:
    print(f"❌ Connection failed: {e}")
PYTHON

echo ""
echo "5. Reloading and restarting service..."
systemctl daemon-reload
systemctl restart cryptoapi

echo ""
echo "6. Waiting for service to start..."
sleep 7

echo ""
echo "7. Testing health endpoint..."
curl -s http://127.0.0.1:5050/health | jq

echo ""
echo "8. Checking service status..."
systemctl status cryptoapi --no-pager | grep -A 2 "Active:"

echo ""
echo "✅ DONE! Database should now be healthy with correct Neon credentials"