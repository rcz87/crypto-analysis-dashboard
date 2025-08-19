#!/bin/bash
# Test VPS deployment - Comprehensive testing

echo "🧪 TESTING VPS DEPLOYMENT"
echo "========================="

# Test 1: Check containers
echo "📊 Container Status:"
docker ps

echo -e "\n🔍 Container Health:"
docker-compose -f docker-compose-vps.yml ps

# Test 2: Check logs
echo -e "\n📋 Recent Application Logs:"
docker-compose -f docker-compose-vps.yml logs --tail=20 crypto-app

# Test 3: Test health endpoint
echo -e "\n🩺 Health Check:"
curl -s http://localhost:5000/health | python3 -m json.tool 2>/dev/null || curl -s http://localhost:5000/health

# Test 4: Test main trading signal endpoint
echo -e "\n🎯 Trading Signal Endpoint Test:"
curl -X POST http://localhost:5000/api/gpts/sinyal/tajam \
  -H "Content-Type: application/json" \
  -d '{"symbol": "BTCUSDT", "timeframe": "1H"}' \
  -w "\nStatus: %{http_code}\nTime: %{time_total}s\n" 2>/dev/null

# Test 5: Test status endpoint
echo -e "\n📈 Status Endpoint:"
curl -s http://localhost:5000/api/gpts/status | python3 -m json.tool 2>/dev/null || curl -s http://localhost:5000/api/gpts/status

# Test 6: Check external access
echo -e "\n🌐 External Access Test:"
EXTERNAL_IP=$(curl -s ifconfig.me 2>/dev/null || echo "YOUR_VPS_IP")
echo "Testing external access via: http://$EXTERNAL_IP:5000"

# Test 7: Port availability
echo -e "\n🔌 Port Check:"
netstat -tuln | grep -E ':(5000|5050|80|443)' || ss -tuln | grep -E ':(5000|5050|80|443)'

echo -e "\n========================="
echo "🎉 DEPLOYMENT TEST COMPLETED"
echo "========================="
echo "📡 Your API URLs:"
echo "   - Health: http://$EXTERNAL_IP:5000/health"
echo "   - Status: http://$EXTERNAL_IP:5000/api/gpts/status" 
echo "   - Signals: http://$EXTERNAL_IP:5000/api/gpts/sinyal/tajam"
echo "   - Alt Port: http://$EXTERNAL_IP:5050/api/gpts/sinyal/tajam"
echo ""
echo "🔧 Next Steps:"
echo "1. Edit API keys jika belum: nano .env"
echo "2. Restart jika edit keys: docker-compose -f docker-compose-vps.yml restart"
echo "3. Use URL above untuk ChatGPT Custom GPTs"
echo "========================="