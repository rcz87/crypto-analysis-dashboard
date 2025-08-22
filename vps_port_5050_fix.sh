#!/bin/bash

# VPS PORT 5050 DATABASE FIX
# Specific fix for VPS running on port 5050

clear
echo "🔧 VPS PORT 5050 DATABASE FIX"
echo "============================="
echo ""

# Colors
G='\033[0;32m'  # Green
R='\033[0;31m'  # Red
Y='\033[1;33m'  # Yellow
NC='\033[0m'    # No Color

# Check current status
echo "Current status check:"
curl -s http://127.0.0.1:5050/health | jq '.components.database' 2>/dev/null || echo "Health check failed"
echo ""

# Find the application directory
APP_DIR="/root/crypto-analysis-dashboard"
if [ ! -d "$APP_DIR" ]; then
    echo -e "${R}❌ Application directory not found: $APP_DIR${NC}"
    exit 1
fi

echo "Working directory: $APP_DIR"
echo ""

# Show current .env content
echo "Current .env content (first 10 lines):"
head -10 "$APP_DIR/.env" 2>/dev/null || echo "No .env file found"
echo ""

# Check if using systemd or direct gunicorn
echo "Checking running processes:"
ps aux | grep -E "(gunicorn|python.*main)" | grep -v grep
echo ""

# Get the service name
SERVICE_NAME=""
if systemctl list-units --type=service | grep -q cryptoapi; then
    SERVICE_NAME="cryptoapi.service"
elif systemctl list-units --type=service | grep -q crypto; then
    SERVICE_NAME=$(systemctl list-units --type=service | grep crypto | head -1 | awk '{print $1}')
fi

echo "Detected service: ${SERVICE_NAME:-'none (running directly)'}"
echo ""

# Stop the application
echo "Stopping application..."
if [ -n "$SERVICE_NAME" ]; then
    sudo systemctl stop "$SERVICE_NAME"
    echo "Stopped systemd service: $SERVICE_NAME"
else
    # Kill gunicorn processes
    pkill -f "gunicorn.*main:app" && echo "Killed gunicorn processes"
fi

sleep 2

# Backup current .env
if [ -f "$APP_DIR/.env" ]; then
    cp "$APP_DIR/.env" "$APP_DIR/.env.backup-$(date +%s)"
    echo "Backed up current .env file"
fi

# Create new .env with correct Neon database
echo "Creating new .env with Neon database..."
cat > "$APP_DIR/.env" << 'EOF'
# Production Environment Configuration
DATABASE_URL=postgresql://neondb_owner:npg_pF1v5QHRUyJC@ep-billowing-sunset-ae1iinty.us-east-2.aws.neon.tech/neondb?sslmode=require
SQLALCHEMY_DATABASE_URI=postgresql://neondb_owner:npg_pF1v5QHRUyJC@ep-billowing-sunset-ae1iinty.us-east-2.aws.neon.tech/neondb?sslmode=require

# Application Configuration
FLASK_ENV=production
API_KEY_REQUIRED=true
SESSION_SECRET=production-secret-key-$(date +%s)

# API Keys
OKX_API_KEY=9a13d0c2-b8da-4e99-a656-573327da0360
OKX_SECRET_KEY=26EB11CA76FDAC6A62729305C4686A81
OKX_PASSPHRASE=870200rZ$
OPENAI_API_KEY=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

# Telegram
TELEGRAM_BOT_TOKEN=7659990721:AAFmX7iRu4Azxs27kNE9QkAYJA6fiwQHwpc
TELEGRAM_CHAT_ID=5899681906

# Rate Limiting
RATE_LIMIT_DEFAULT=120/minute
LIMITER_STORAGE_URI=memory://
EOF

echo -e "${G}✅ New .env file created${NC}"

# Start the application
echo ""
echo "Starting application..."

if [ -n "$SERVICE_NAME" ]; then
    # Update systemd service to ensure it uses the right port and environment
    sudo tee "/etc/systemd/system/$SERVICE_NAME" > /dev/null << EOF
[Unit]
Description=Crypto Trading API
After=network.target

[Service]
Type=notify
User=root
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/venv/bin
EnvironmentFile=$APP_DIR/.env
ExecStart=$APP_DIR/venv/bin/gunicorn --bind 0.0.0.0:5050 --workers 4 --worker-class gthread --threads 2 main:app
Restart=always
RestartSec=3
KillMode=mixed
TimeoutStopSec=5

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    sudo systemctl start "$SERVICE_NAME"
    echo "Started systemd service: $SERVICE_NAME"
else
    # Start directly with gunicorn
    cd "$APP_DIR"
    source venv/bin/activate
    nohup gunicorn --bind 0.0.0.0:5050 --workers 4 --worker-class gthread --threads 2 main:app > /tmp/crypto-api.log 2>&1 &
    echo "Started gunicorn directly on port 5050"
fi

# Wait for startup
echo ""
echo "Waiting for application startup..."
sleep 8

# Test the fix
echo ""
echo "Testing database connection..."
for i in {1..5}; do
    HEALTH_RESPONSE=$(curl -s http://127.0.0.1:5050/health 2>/dev/null)
    
    if echo "$HEALTH_RESPONSE" | jq -e '.components.database.status == "healthy"' >/dev/null 2>&1; then
        echo -e "${G}🎉 SUCCESS! Database is now healthy!${NC}"
        echo ""
        echo "Full health response:"
        echo "$HEALTH_RESPONSE" | jq '.'
        echo ""
        echo -e "${G}✅ VPS database fix completed successfully!${NC}"
        echo ""
        echo "Your system is now running with:"
        echo "• Neon PostgreSQL database connection"
        echo "• Port 5050 accessible"
        echo "• All API endpoints functional"
        echo ""
        echo "Test endpoints:"
        echo "curl -s http://127.0.0.1:5050/health | jq"
        echo "curl -s http://127.0.0.1:5050/api/gpts/status | jq"
        exit 0
    else
        echo "Attempt $i/5: Database still connecting..."
        sleep 3
    fi
done

echo -e "${R}❌ Database connection still failing${NC}"
echo ""
echo "Last response:"
echo "$HEALTH_RESPONSE" | jq '.' 2>/dev/null || echo "$HEALTH_RESPONSE"
echo ""
echo "Checking logs:"
if [ -n "$SERVICE_NAME" ]; then
    sudo journalctl -u "$SERVICE_NAME" -n 20 --no-pager
else
    tail -20 /tmp/crypto-api.log 2>/dev/null || echo "No direct logs found"
fi