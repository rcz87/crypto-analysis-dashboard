#!/bin/bash

# SIMPLE VPS FIX - Langsung ke masalah utama
# Berdasarkan screenshot: service running, tinggal fix database URL

clear
echo "🔧 SIMPLE VPS DATABASE FIX"
echo "========================="
echo ""

# Colors
G='\033[0;32m'  # Green
R='\033[0;31m'  # Red
Y='\033[1;33m'  # Yellow
NC='\033[0m'    # No Color

# Quick status check
echo "Current service status:"
if systemctl is-active --quiet cryptoapi.service; then
    echo -e "${G}✅ Service is running${NC}"
else
    echo -e "${R}❌ Service not running${NC}"
    exit 1
fi

# Quick health check
HEALTH=$(curl -s --max-time 3 http://localhost:5000/health 2>/dev/null || echo "FAILED")
if [[ "$HEALTH" =~ "healthy" ]]; then
    echo -e "${G}✅ Application already healthy!${NC}"
    echo "Your VPS is working correctly."
    exit 0
else
    echo -e "${Y}⚠️ Health check failing - need database fix${NC}"
fi

echo ""
echo "MASALAH: Database masih coba connect ke localhost:5432"
echo "SOLUSI: Update ke Neon database URL"
echo ""

# Find app directory
APP_DIR="/root/crypto-analysis-dashboard"
if [ ! -d "$APP_DIR" ]; then
    APP_DIR="$(pwd)"
fi
echo "Working directory: $APP_DIR"

# Get Neon URL
echo ""
echo "Paste your Neon database URL:"
echo "(Format: postgresql://neondb_owner:PASSWORD@ep-xxx.neon.tech/neondb?sslmode=require)"
read -p "URL: " NEON_URL

if [[ ! "$NEON_URL" =~ ^postgresql:// ]]; then
    echo -e "${R}❌ Invalid URL format${NC}"
    exit 1
fi

# Stop service
echo ""
echo "Stopping service..."
sudo systemctl stop cryptoapi.service

# Update environment
ENV_FILE="$APP_DIR/.env.production"
echo "Updating environment file: $ENV_FILE"

# Backup
[ -f "$ENV_FILE" ] && cp "$ENV_FILE" "$ENV_FILE.backup"

# Create minimal working environment
cat > "$ENV_FILE" << EOF
DATABASE_URL=$NEON_URL
SQLALCHEMY_DATABASE_URI=$NEON_URL
FLASK_ENV=production
API_KEY_REQUIRED=true
API_KEY=your-api-key-here
SESSION_SECRET=production-secret-key
EOF

echo -e "${G}✅ Environment updated${NC}"

# Update systemd service
SERVICE_FILE="/etc/systemd/system/cryptoapi.service"
sudo tee "$SERVICE_FILE" > /dev/null << EOF
[Unit]
Description=Crypto Trading API
After=network.target

[Service]
Type=notify
User=root
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/venv/bin
EnvironmentFile=$ENV_FILE
ExecStart=$APP_DIR/venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 4 main:app
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

echo -e "${G}✅ Service configuration updated${NC}"

# Start service
echo ""
echo "Starting service..."
sudo systemctl daemon-reload
sudo systemctl start cryptoapi.service

# Wait and check
sleep 5

if systemctl is-active --quiet cryptoapi.service; then
    echo -e "${G}✅ Service started${NC}"
else
    echo -e "${R}❌ Service failed to start${NC}"
    echo "Checking logs:"
    sudo journalctl -u cryptoapi.service -n 10 --no-pager
    exit 1
fi

# Test health
echo ""
echo "Testing health..."
for i in {1..8}; do
    HEALTH_CHECK=$(curl -s --max-time 5 http://localhost:5000/health 2>/dev/null || echo "FAILED")
    
    if [[ "$HEALTH_CHECK" =~ "healthy" ]]; then
        echo -e "${G}🎉 SUCCESS! Application is healthy!${NC}"
        echo ""
        echo "Health response:"
        echo "$HEALTH_CHECK"
        echo ""
        echo -e "${G}✅ VPS fix complete!${NC}"
        echo ""
        echo "Next steps:"
        echo "1. Add your API keys to: $ENV_FILE"
        echo "2. Test endpoints with: curl http://YOUR_VPS_IP:5000/health"
        echo "3. Monitor with: sudo journalctl -u cryptoapi.service -f"
        exit 0
    else
        echo "Attempt $i/8: Waiting for health check..."
        sleep 3
    fi
done

echo -e "${R}❌ Health check still failing${NC}"
echo "Last response: $HEALTH_CHECK"
echo ""
echo "Checking recent logs:"
sudo journalctl -u cryptoapi.service -n 15 --no-pager