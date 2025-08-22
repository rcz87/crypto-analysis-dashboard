#!/usr/bin/env bash
set -euo pipefail

# VPS Deployment Script for Flask + Gunicorn Crypto Trading API
APP_DIR="/root/crypto-analysis-dashboard"
SERVICE="cryptoapi.service"
HEALTH_URL="http://127.0.0.1:5050/health"
STATUS_URL="http://127.0.0.1:5050/api/gpts/status"
ROOT_URL="http://127.0.0.1:5050/"

echo "==> Starting Flask + Gunicorn VPS deployment..."
echo "App Directory: $APP_DIR"
echo "Service: $SERVICE"

# Navigate to application directory
echo "==> Confirming application directory"
cd "$APP_DIR" || { echo "ERROR: Cannot access $APP_DIR"; exit 1; }

# Verify Flask structure
echo "==> Verifying Flask + Gunicorn structure"
if [ ! -f "main.py" ]; then
    echo "❌ main.py not found"
    exit 1
fi

if [ ! -f "app.py" ]; then
    echo "❌ app.py not found"
    exit 1
fi

if [ ! -f "routes/health.py" ]; then
    echo "❌ routes/health.py not found"
    exit 1
fi

echo "✅ Flask structure verified"

# Show current systemd environment
echo "==> Current systemd environment variables"
systemctl show "$SERVICE" -p Environment 2>/dev/null | sed 's/; /\n/g' | grep -E 'DATABASE_URL|PGHOST|PGPORT|PATH' || echo "No relevant environment variables found"

# Restart the systemd service
echo "==> Restarting $SERVICE with new Flask structure"
systemctl restart "$SERVICE"
echo "Waiting for service to start..."
sleep 8

# Check service status
echo "==> Service Status Check"
if systemctl is-active --quiet "$SERVICE"; then
    echo "✅ $SERVICE is running"
    
    # Show service details
    echo "Service details:"
    systemctl status "$SERVICE" --no-pager -l | head -10
else
    echo "❌ $SERVICE failed to start"
    echo "Recent logs:"
    journalctl -u "$SERVICE" -n 15 --no-pager
    exit 1
fi

# Wait a bit more for full startup
sleep 5

# Smoke tests for all endpoints
echo "==> Running Flask endpoint smoke tests"

echo "Testing root endpoint..."
ROOT_RESPONSE=$(curl -s "$ROOT_URL" 2>/dev/null || echo "FAILED")
if echo "$ROOT_RESPONSE" | grep -q '"status".*"active"' 2>/dev/null; then
    echo "✅ Root endpoint: Platform info available"
    echo "   Service: $(echo "$ROOT_RESPONSE" | grep -o '"service":"[^"]*"' | cut -d'"' -f4 || echo 'unknown')"
else
    echo "❌ Root endpoint failed"
    echo "Response: ${ROOT_RESPONSE:0:200}..."
fi

echo "Testing status endpoint..."
STATUS_RESPONSE=$(curl -s "$STATUS_URL" 2>/dev/null || echo "FAILED")
if echo "$STATUS_RESPONSE" | grep -q '"status".*"active"' 2>/dev/null; then
    echo "✅ Status endpoint: $(echo "$STATUS_RESPONSE" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)"
    echo "   Version: $(echo "$STATUS_RESPONSE" | grep -o '"api_version":"[^"]*"' | cut -d'"' -f4 || echo 'unknown')"
else
    echo "❌ Status endpoint failed"
    echo "Response: ${STATUS_RESPONSE:0:200}..."
fi

echo "Testing health endpoint..."
HEALTH_RESPONSE=$(curl -s "$HEALTH_URL" 2>/dev/null || echo "FAILED")
if echo "$HEALTH_RESPONSE" | grep -q '"components"' 2>/dev/null; then
    OVERALL_STATUS=$(echo "$HEALTH_RESPONSE" | grep -o '"status":"[^"]*"' | head -1 | cut -d'"' -f4)
    echo "✅ Health endpoint accessible"
    echo "   Overall status: $OVERALL_STATUS"
    
    # Check database status
    if echo "$HEALTH_RESPONSE" | grep -q '"database".*"healthy"' 2>/dev/null; then
        echo "   Database: healthy"
    else
        echo "   Database: degraded/unhealthy"
    fi
    
    # Check OKX API status  
    if echo "$HEALTH_RESPONSE" | grep -q '"okx_api".*"healthy"' 2>/dev/null; then
        echo "   OKX API: healthy"
    else
        echo "   OKX API: degraded/unhealthy"
    fi
else
    echo "❌ Health endpoint failed"
    echo "Response: ${HEALTH_RESPONSE:0:200}..."
fi

# Check process
echo "==> Process verification"
GUNICORN_PROCESSES=$(ps aux | grep '[g]unicorn.*main:app' | wc -l)
if [ "$GUNICORN_PROCESSES" -gt 0 ]; then
    echo "✅ Gunicorn processes running: $GUNICORN_PROCESSES"
    echo "   Entry point: main:app (verified)"
else
    echo "❌ No gunicorn processes found with main:app"
    echo "All gunicorn processes:"
    ps aux | grep '[g]unicorn' || echo "No gunicorn processes"
fi

echo "==> Flask + Gunicorn deployment completed!"
echo ""
echo "🎯 Quick verification commands:"
echo "  curl -s $ROOT_URL"
echo "  curl -s $STATUS_URL"  
echo "  curl -s $HEALTH_URL"
echo "  systemctl status $SERVICE"
echo "  journalctl -u $SERVICE -f"
echo ""
echo "🚀 Flask application factory with main:app entry point deployed successfully!"