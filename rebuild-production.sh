#!/bin/bash
# Rebuild production dengan dependencies lengkap

echo "🔧 REBUILDING PRODUCTION WITH FULL DEPENDENCIES"
echo "==============================================="

# Stop semua containers
echo "🛑 Stopping all containers..."
docker-compose -f docker-compose-vps.yml down

# Clean build cache
echo "🗑️ Cleaning Docker cache..."
docker system prune -f
docker rmi crypto-analysis-dashboard-crypto-app 2>/dev/null || true

# Show current requirements
echo "📋 Current requirements-prod.txt:"
head -20 requirements-prod.txt

# Build dan start dengan force recreate
echo "🚀 Building with full dependencies..."
docker-compose -f docker-compose-vps.yml up -d --build --force-recreate

# Wait untuk build dan start
echo "⏳ Waiting for containers to build and start..."
sleep 60

# Check container status
echo "📊 Container status:"
docker ps

# Check logs untuk dependencies
echo "📋 Checking dependency load:"
docker logs crypto_trading_app | tail -30

# Test health endpoint
echo "🩺 Testing health endpoint:"
curl -s http://localhost:5050/health | python3 -m json.tool 2>/dev/null || curl -s http://localhost:5050/health

# Test trading signal endpoint
echo "🎯 Testing trading signal endpoint:"
curl -X POST http://localhost:5050/api/gpts/sinyal/tajam \
  -H "Content-Type: application/json" \
  -d '{"symbol": "BTCUSDT", "timeframe": "1H"}' \
  -s | python3 -m json.tool 2>/dev/null || echo "Endpoint test failed"

# Get external IP
EXTERNAL_IP=$(curl -s ifconfig.me 2>/dev/null || echo "212.26.36.253")

echo ""
echo "==============================================="
echo "🎉 PRODUCTION REBUILD COMPLETED"
echo "==============================================="
echo "📡 Platform URLs:"
echo "   Health: http://$EXTERNAL_IP:5050/health"
echo "   Status: http://$EXTERNAL_IP:5050/api/gpts/status"
echo "   Signals: http://$EXTERNAL_IP:5050/api/gpts/sinyal/tajam"
echo "   HTTP: http://$EXTERNAL_IP/api/gpts/sinyal/tajam"
echo ""
echo "🔧 For ChatGPT Custom GPTs use:"
echo "   http://$EXTERNAL_IP:5050/api/gpts/sinyal/tajam"
echo "==============================================="