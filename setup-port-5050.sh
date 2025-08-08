#!/bin/bash
# Setup port 5050 untuk VPS access

echo "🔧 SETTING UP PORT 5050 ACCESS"
echo "=============================="

# Stop containers
echo "🛑 Stopping containers..."
docker-compose -f docker-compose-vps.yml down

# Open firewall untuk port 5050
echo "🛡️ Opening firewall ports..."
ufw allow 5050
ufw allow 80
ufw allow 443
ufw status

# Start containers dengan port mapping baru
echo "🚀 Starting containers dengan port 5050..."
docker-compose -f docker-compose-vps.yml up -d --build

# Wait untuk containers
echo "⏳ Waiting for containers..."
sleep 20

# Check container status
echo "📊 Container status:"
docker ps

# Check port mapping
echo "🔌 Port mappings:"
docker port crypto_trading_app

# Test internal connectivity
echo "🧪 Testing internal connectivity:"
curl -s -I http://localhost:5050/health && echo "✅ Port 5050 internal OK" || echo "❌ Port 5050 internal FAILED"

# Test dengan port 80
curl -s -I http://localhost:80/health && echo "✅ Port 80 internal OK" || echo "❌ Port 80 internal FAILED"

# Get external IP
EXTERNAL_IP=$(curl -s ifconfig.me 2>/dev/null || echo "212.26.36.253")

echo ""
echo "=============================="
echo "🎯 SETUP COMPLETED"
echo "=============================="
echo "📡 Try these URLs:"
echo "   http://$EXTERNAL_IP:5050/health"
echo "   http://$EXTERNAL_IP:5050/api/gpts/status"
echo "   http://$EXTERNAL_IP:5050/api/gpts/sinyal/tajam"
echo ""
echo "   http://$EXTERNAL_IP/health (port 80)"
echo "   http://$EXTERNAL_IP/api/gpts/sinyal/tajam (port 80)"
echo ""
echo "🔧 For ChatGPT Custom GPTs use:"
echo "   http://$EXTERNAL_IP:5050/api/gpts/sinyal/tajam"
echo "=============================="