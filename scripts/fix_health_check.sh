#!/usr/bin/env bash
set -euo pipefail

# Fix Health Check Database Connection Script
SERVICE="cryptoapi.service"

echo "🔧 FIXING HEALTH CHECK DATABASE CONNECTION"
echo "=========================================="

echo "==> Stopping service for health check fix"
systemctl stop "$SERVICE"

echo "==> Current Flask app health check has been updated to:"
echo "    - Use SQLALCHEMY_DATABASE_URI from Flask config only"
echo "    - No fallback to psycopg2.connect with environment variables"
echo "    - Single source of truth for database connection"

echo "==> Verifying systemd environment configuration"
systemctl show "$SERVICE" -p Environment | grep DATABASE_URL || echo "No DATABASE_URL found"

echo "==> Starting service with fixed health check"
systemctl start "$SERVICE"
sleep 8

echo "==> Checking service status"
if systemctl is-active --quiet "$SERVICE"; then
    echo "✅ Service is running"
    systemctl status "$SERVICE" --no-pager -l | head -8
else
    echo "❌ Service failed to start"
    journalctl -u "$SERVICE" -n 15 --no-pager
    exit 1
fi

echo "==> Testing fixed health endpoint"
sleep 3

echo "Health endpoint test:"
HEALTH_RESPONSE=$(curl -s http://127.0.0.1:5050/health 2>/dev/null || echo "FAILED")
if echo "$HEALTH_RESPONSE" | grep -q '"database".*"healthy"' 2>/dev/null; then
    echo "✅ Database health check: HEALTHY"
    echo "   Using SQLAlchemy config successfully"
else
    echo "❌ Database health check still failing"
    echo "Response: ${HEALTH_RESPONSE:0:200}..."
fi

echo "Status endpoint test:"
STATUS_RESPONSE=$(curl -s http://127.0.0.1:5050/api/gpts/status 2>/dev/null || echo "FAILED")
if echo "$STATUS_RESPONSE" | grep -q '"status".*"active"' 2>/dev/null; then
    echo "✅ Status endpoint: Active"
else
    echo "❌ Status endpoint failed"
    echo "Response: ${STATUS_RESPONSE:0:200}..."
fi

echo "==> Health check fix completed!"
echo ""
echo "The fix ensures:"
echo "1. Health check uses SQLALCHEMY_DATABASE_URI from Flask config"
echo "2. No fallback to psycopg2.connect with environment variables"
echo "3. Single source of truth for database connection"
echo "4. Proper timeout and SSL handling for Neon database"