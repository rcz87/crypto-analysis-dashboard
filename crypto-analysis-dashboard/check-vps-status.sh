#!/bin/bash
echo "🔍 VPS STATUS CHECK"
echo "==================="

# Check container status
echo "📊 Container Status:"
docker ps

echo -e "\n🔗 Port Bindings:"
docker port crypto_trading_app
docker port crypto_nginx

echo -e "\n🧪 Internal connectivity test:"
curl -s "http://localhost:5050/api/gpts/sinyal/tajam?symbol=BTCUSDT&timeframe=1H" | head -100 || echo "Local connection failed"

echo -e "\n📋 Container logs (last 20 lines):"
docker logs crypto_trading_app --tail 20

echo -e "\n🔥 Firewall status:"
ufw status

echo -e "\n🌐 Network interfaces:"
ip addr show | grep -E "(inet|UP)"

echo -e "\n🚪 Listening ports:"
netstat -tulpn | grep -E ":50(00|50)" || ss -tulpn | grep -E ":50(00|50)"

echo -e "\n✅ Quick external test from localhost:"
timeout 10 curl -s "http://127.0.0.1:5050/health" || echo "Health check failed"
