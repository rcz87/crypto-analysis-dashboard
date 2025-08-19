#!/bin/bash
# Update VPS production dengan kode terbaru dari GitHub

echo "🔄 UPDATING VPS PRODUCTION"
echo "========================="

# Stop containers
echo "🛑 Stopping containers..."
docker-compose -f docker-compose-vps.yml down

# Pull latest code
echo "📥 Pulling latest code from GitHub..."
git pull origin main

# Clean build untuk force update
echo "🗑️ Cleaning build cache..."
docker system prune -f
docker rmi crypto-analysis-dashboard-crypto-app 2>/dev/null || true

# Rebuild dengan kode terbaru
echo "🚀 Building with latest code..."
docker-compose -f docker-compose-vps.yml up -d --build --force-recreate

# Wait untuk containers
echo "⏳ Waiting for containers to start..."
sleep 30

# Check status
echo "📊 Container status:"
docker ps

# Test endpoint yang sudah diperbaiki
echo "🧪 Testing fixed endpoint..."
echo "GET method test:"
curl -s "http://localhost:5050/api/gpts/sinyal/tajam?symbol=BTCUSDT&timeframe=1H" | head -200

echo -e "\nPOST method test:"
curl -X POST http://localhost:5050/api/gpts/sinyal/tajam \
  -H "Content-Type: application/json" \
  -d '{"symbol": "BTCUSDT", "timeframe": "1H"}' \
  -s | head -200

# Check Flask routes
echo -e "\n📋 Checking Flask routes..."
docker exec crypto_trading_app python3 -c "
import sys; sys.path.append('/app')
from main import create_app
app = create_app()
with app.app_context():
    print('GPTs routes:')
    for rule in app.url_map.iter_rules():
        if 'sinyal' in rule.rule:
            print(f'  {rule.rule} -> {rule.endpoint} {list(rule.methods)}')
" 2>/dev/null || echo "Could not check routes"

echo ""
echo "========================="
echo "🎯 UPDATE COMPLETED"
echo "========================="
echo "External URLs ready:"
echo "  GET: http://212.26.36.253:5050/api/gpts/sinyal/tajam?symbol=BTCUSDT"
echo "  POST: http://212.26.36.253:5050/api/gpts/sinyal/tajam"
echo "========================="