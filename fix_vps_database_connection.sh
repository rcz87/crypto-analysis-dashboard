#!/usr/bin/env bash
set -euo pipefail

# VPS Database Connection Fix Script
SERVICE="cryptoapi.service"

echo "🔧 FIXING VPS DATABASE CONNECTION"
echo "=================================="

echo "==> Stopping service for configuration update"
systemctl stop "$SERVICE"

echo "==> Checking current environment configuration"
systemctl show "$SERVICE" -p Environment | grep DATABASE_URL || echo "No DATABASE_URL found"

echo "==> Current Flask app configuration check"
if [ -f "app.py" ]; then
    echo "Database config in app.py:"
    grep -n "DATABASE_URI" app.py || echo "No DATABASE_URI config found"
fi

echo "==> Updating systemd service environment"
# Create a temporary service override
mkdir -p /etc/systemd/system/cryptoapi.service.d/

cat > /etc/systemd/system/cryptoapi.service.d/database.conf << 'EOF'
[Service]
Environment="DATABASE_URL=postgresql://neondb_owner:npg_pF1v5QHRUyJC@ep-billowing-sunset-a1n4dwi.us-east-2.aws.neon.tech/neondb?sslmode=require"
Environment="SQLALCHEMY_DATABASE_URI=postgresql://neondb_owner:npg_pF1v5QHRUyJC@ep-billowing-sunset-a1n4dwi.us-east-2.aws.neon.tech/neondb?sslmode=require"
EOF

echo "==> Reloading systemd configuration"
systemctl daemon-reload

echo "==> Verifying new configuration"
systemctl show "$SERVICE" -p Environment | grep DATABASE_URL

echo "==> Starting service with new database config"
systemctl start "$SERVICE"
sleep 5

echo "==> Checking service status"
if systemctl is-active --quiet "$SERVICE"; then
    echo "✅ Service is running"
    systemctl status "$SERVICE" --no-pager -l | head -8
else
    echo "❌ Service failed to start"
    journalctl -u "$SERVICE" -n 10 --no-pager
    exit 1
fi

echo "==> Testing database connection"
sleep 3
curl -s http://127.0.0.1:5050/health | grep -o '"database":{"[^}]*}' || echo "Database health check failed"

echo "==> Testing all endpoints"
echo "Health endpoint:"
curl -s http://127.0.0.1:5050/health | grep -o '"status":"[^"]*"' | head -1

echo "Status endpoint:"
curl -s http://127.0.0.1:5050/api/gpts/status | grep -o '"status":"[^"]*"' | head -1

echo "🎯 Database connection fix completed!"
echo ""
echo "If database still shows unhealthy, check:"
echo "1. Neon database is accessible"
echo "2. Password is URL-encoded correctly"
echo "3. SSL connection is working"