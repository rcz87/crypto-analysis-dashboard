#!/bin/bash

echo "🔍 FINDING SOURCE OF LOCALHOST CONNECTION"
echo "========================================="
echo ""

# 1. Check what app.py is actually reading
echo "1. Checking app.py database config..."
grep -n "DATABASE\|SQLALCHEMY\|trading_user\|localhost" /root/crypto-analysis-dashboard/app.py | head -10

echo ""
echo "2. Checking if there's a config file..."
ls -la /root/crypto-analysis-dashboard/config* 2>/dev/null || echo "No config files found"
ls -la /root/crypto-analysis-dashboard/*.cfg 2>/dev/null || echo "No .cfg files found"

echo ""
echo "3. Checking production_config.py..."
if [ -f /root/crypto-analysis-dashboard/production_config.py ]; then
    grep -n "DATABASE\|SQLALCHEMY\|localhost\|trading_user" /root/crypto-analysis-dashboard/production_config.py
fi

echo ""
echo "4. Checking if dotenv is loading different file..."
grep -r "load_dotenv\|dotenv" /root/crypto-analysis-dashboard/*.py | head -5

echo ""
echo "5. Direct check - what Python sees..."
python3 << 'PYTHON'
import sys
sys.path.insert(0, '/root/crypto-analysis-dashboard')
import os

# Load dotenv if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

# Check environment
db_url = os.environ.get('DATABASE_URL', 'NOT SET')
sqlalchemy_url = os.environ.get('SQLALCHEMY_DATABASE_URI', 'NOT SET')

print("Environment variables:")
print(f"DATABASE_URL: {'localhost' if 'localhost' in db_url else 'neon' if 'neon' in db_url else 'NOT SET'}")
print(f"SQLALCHEMY_DATABASE_URI: {'localhost' if 'localhost' in sqlalchemy_url else 'neon' if 'neon' in sqlalchemy_url else 'NOT SET'}")

# Check what app.py loads
try:
    from app import app
    with app.app_context():
        config_db = app.config.get('SQLALCHEMY_DATABASE_URI', 'NOT SET')
        print(f"\nApp config SQLALCHEMY_DATABASE_URI: {'localhost' if 'localhost' in config_db else 'neon' if 'neon' in config_db else 'NOT SET'}")
        if 'trading_user' in config_db:
            print("⚠️  FOUND: trading_user in config - this is the problem!")
except Exception as e:
    print(f"Error loading app: {e}")
PYTHON

echo ""
echo "6. Fixing app.py directly..."
# Force fix app.py
sed -i 's|postgresql://trading_user:.*@localhost:5432/trading_db|postgresql://crypto_new_owner:WgOOUP9V5X9p@ep-gentle-boat-a10aawfh.ap-southeast-1.aws.neon.tech/crypto_dashboard_new?sslmode=require|g' /root/crypto-analysis-dashboard/app.py

# Also check for any sqlite fallback
sed -i 's|sqlite:///trading.db|postgresql://crypto_new_owner:WgOOUP9V5X9p@ep-gentle-boat-a10aawfh.ap-southeast-1.aws.neon.tech/crypto_dashboard_new?sslmode=require|g' /root/crypto-analysis-dashboard/app.py

echo "✅ Fixed any hardcoded localhost in app.py"

echo ""
echo "7. Restarting service..."
systemctl restart cryptoapi
sleep 5

echo ""
echo "8. Testing health..."
curl -s http://127.0.0.1:5050/health | jq '.components.database'