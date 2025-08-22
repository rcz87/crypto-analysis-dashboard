#!/usr/bin/env bash
set -euo pipefail

# VPS Deployment Script for Crypto Trading API
APP_DIR="/root/crypto-analysis-dashboard"
SERVICE="cryptoapi.service"
HEALTH_URL="http://127.0.0.1:5050/health"
STATUS_URL="http://127.0.0.1:5050/api/gpts/status"

echo "==> Starting VPS deployment..."
echo "App Directory: $APP_DIR"
echo "Service: $SERVICE"

# Navigate to application directory
echo "==> Changing to application directory"
cd "$APP_DIR" || { echo "ERROR: Cannot access $APP_DIR"; exit 1; }

# Pull latest changes from GitHub
echo "==> Pulling latest changes from GitHub"
git fetch origin
git reset --hard origin/main
echo "✅ Code updated to latest version"

# Show effective database URL from systemd environment
echo "==> Current systemd environment variables"
systemctl show "$SERVICE" -p Environment | sed 's/; /\n/g' | grep -E 'DATABASE_URL|PGHOST|PGPORT|PATH' || echo "No relevant environment variables found"

# Optional: Run database migrations if Alembic is available
echo "==> Checking for database migrations"
if [ -x ".venv/bin/alembic" ]; then 
    echo "Running database migrations..."
    source .venv/bin/activate
    alembic upgrade head || echo "⚠️ Migration failed or not needed"
else
    echo "No Alembic found, skipping migrations"
fi

# Restart the systemd service
echo "==> Restarting $SERVICE"
systemctl restart "$SERVICE"
echo "Waiting for service to start..."
sleep 5

# Check service status
echo "==> Service Status Check"
if systemctl is-active --quiet "$SERVICE"; then
    echo "✅ $SERVICE is running"
else
    echo "❌ $SERVICE failed to start"
    echo "Recent logs:"
    journalctl -u "$SERVICE" -n 10 --no-pager
    exit 1
fi

# Smoke tests
echo "==> Running smoke tests"

echo "Testing status endpoint..."
STATUS_RESPONSE=$(curl -s "$STATUS_URL" || echo "FAILED")
if echo "$STATUS_RESPONSE" | jq -e '.status' >/dev/null 2>&1; then
    echo "✅ Status endpoint: $(echo "$STATUS_RESPONSE" | jq -r '.status')"
    echo "   Version: $(echo "$STATUS_RESPONSE" | jq -r '.version.api_version // "unknown"')"
else
    echo "❌ Status endpoint failed"
    echo "Response: $STATUS_RESPONSE"
fi

echo "Testing health endpoint..."
HEALTH_RESPONSE=$(curl -s "$HEALTH_URL" || echo "FAILED")
if echo "$HEALTH_RESPONSE" | jq -e '.components.database' >/dev/null 2>&1; then
    DB_STATUS=$(echo "$HEALTH_RESPONSE" | jq -r '.components.database.status')
    OVERALL_STATUS=$(echo "$HEALTH_RESPONSE" | jq -r '.status')
    echo "✅ Health endpoint accessible"
    echo "   Overall status: $OVERALL_STATUS"
    echo "   Database: $DB_STATUS"
else
    echo "❌ Health endpoint failed"
    echo "Response: $HEALTH_RESPONSE"
fi

echo "==> Deployment completed!"
echo ""
echo "Quick verification commands:"
echo "  curl -s $STATUS_URL | jq"
echo "  curl -s $HEALTH_URL | jq"
echo "  systemctl status $SERVICE"
echo "  journalctl -u $SERVICE -f"