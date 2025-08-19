#!/bin/bash
# Deployment Script untuk VPS - Cryptocurrency Trading Platform

set -e

echo "🚀 CRYPTOCURRENCY TRADING AI - VPS DEPLOYMENT"
echo "=============================================="

# Configuration
VPS_IP="212.26.36.253"
VPS_USER="root"
PROJECT_DIR="crypto-analysis-dashboard"
GITHUB_REPO="https://github.com/rcz87/crypto-analysis-dashboard.git"

echo "📋 Deployment Configuration:"
echo "   VPS: $VPS_IP"
echo "   User: $VPS_USER" 
echo "   Project: $PROJECT_DIR"
echo "   GitHub: $GITHUB_REPO"

echo -e "\n🔧 DEPLOYMENT STEPS:"
echo "1. Connect ke VPS via SSH"
echo "2. Clone/Update repository dari GitHub"
echo "3. Install Docker & Docker Compose"
echo "4. Setup environment variables"
echo "5. Build dan start containers"
echo "6. Verify deployment"

echo -e "\n📝 Manual Commands untuk VPS:"

echo -e "\n# 1. SSH ke VPS"
echo "ssh $VPS_USER@$VPS_IP"

echo -e "\n# 2. Clone repository (jika belum ada)"
echo "git clone $GITHUB_REPO"
echo "cd $PROJECT_DIR"

echo -e "\n# 3. Atau update repository (jika sudah ada)"
echo "cd $PROJECT_DIR"
echo "git pull origin main"

echo -e "\n# 4. Install Docker (jika belum ada)"
echo "curl -fsSL https://get.docker.com -o get-docker.sh"
echo "sh get-docker.sh"
echo "apt-get install -y docker-compose-plugin"

echo -e "\n# 5. Setup environment variables"
echo "cp .env.vps.example .env"
echo "nano .env  # Edit dengan API keys Anda"

echo -e "\n# 6. Build dan start containers"
echo "docker-compose -f docker-compose-vps.yml down"
echo "docker-compose -f docker-compose-vps.yml up -d --build"

echo -e "\n# 7. Check status containers"
echo "docker ps"
echo "docker-compose -f docker-compose-vps.yml logs"

echo -e "\n# 8. Test endpoint"
echo "curl -X POST http://localhost:5000/api/gpts/sinyal/tajam \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"symbol\": \"BTCUSDT\", \"timeframe\": \"1H\"}'"

echo -e "\n=============================================="
echo "🎯 SETELAH DEPLOYMENT:"
echo "- API URL: http://$VPS_IP:5000"
echo "- Main Endpoint: http://$VPS_IP:5000/api/gpts/sinyal/tajam"
echo "- Status Check: http://$VPS_IP:5000/api/gpts/status"
echo "=============================================="