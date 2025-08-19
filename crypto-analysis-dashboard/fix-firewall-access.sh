#!/bin/bash
# Fix VPS external access - Firewall dan Port Configuration

echo "🔧 FIXING VPS EXTERNAL ACCESS"
echo "============================="

# Check current firewall status
echo "🔍 Current firewall status:"
ufw status || iptables -L

# Enable UFW if not enabled
echo "🛡️ Configuring firewall..."
ufw --force enable

# Allow SSH (important!)
ufw allow ssh
ufw allow 22

# Allow HTTP ports
ufw allow 80
ufw allow 443

# Allow our application ports
ufw allow 5000
ufw allow 5050

# Allow PostgreSQL (local access only)
ufw allow from 172.0.0.0/8 to any port 5432

# Reload firewall
ufw reload

echo "✅ Firewall configured"

# Check if ports are actually listening
echo -e "\n🔌 Checking port availability:"
netstat -tuln | grep -E ':(5000|5050|80|443)' || ss -tuln | grep -E ':(5000|5050|80|443)'

# Test internal connectivity
echo -e "\n🧪 Testing internal connectivity:"
curl -s -I http://localhost:5000/health && echo "✅ Port 5000 internal OK" || echo "❌ Port 5000 internal FAILED"

# Check Docker port mapping
echo -e "\n🐳 Docker port mappings:"
docker port crypto_trading_app

# Check if application is actually binding to 0.0.0.0
echo -e "\n📡 Application binding check:"
docker exec crypto_trading_app netstat -tuln | grep -E ':(5000|5050)'

# System network info
echo -e "\n🌐 Network interface info:"
ip addr show | grep -E 'inet.*scope global'

# Final firewall status
echo -e "\n🛡️ Final firewall rules:"
ufw status numbered

echo -e "\n============================="
echo "🎯 TROUBLESHOOTING COMPLETED"
echo "============================="
echo "📡 Try accessing again:"
echo "   http://212.26.36.253:5000/health"
echo "   http://212.26.36.253:5000/api/gpts/status"
echo ""
echo "🔧 If still not working, check:"
echo "1. VPS provider firewall (Hostinger/cloud provider)"
echo "2. Application logs: docker-compose -f docker-compose-vps.yml logs crypto-app"
echo "3. Container internal network: docker exec crypto_trading_app curl localhost:5000/health"
echo "============================="