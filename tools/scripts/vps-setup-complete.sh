#!/bin/bash
# Complete VPS Setup Script - Run di VPS

set -e

echo "🚀 SETTING UP CRYPTOCURRENCY TRADING PLATFORM"
echo "=============================================="

# Update system
echo "📦 Updating system packages..."
apt-get update && apt-get upgrade -y

# Install Docker
echo "🐳 Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    echo "✅ Docker installed"
else
    echo "✅ Docker already installed"
fi

# Install Docker Compose
echo "🔧 Installing Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    apt-get install -y docker-compose-plugin
    echo "✅ Docker Compose installed"
else
    echo "✅ Docker Compose already installed"
fi

# Install Git
echo "📋 Installing Git..."
if ! command -v git &> /dev/null; then
    apt-get install -y git
    echo "✅ Git installed"
else
    echo "✅ Git already installed"
fi

# Clone repository
echo "📥 Cloning repository..."
PROJECT_DIR="crypto-analysis-dashboard"
GITHUB_REPO="https://github.com/rcz87/crypto-analysis-dashboard.git"

if [ ! -d "$PROJECT_DIR" ]; then
    git clone $GITHUB_REPO
    echo "✅ Repository cloned"
else
    echo "📁 Repository exists, updating..."
    cd $PROJECT_DIR
    git pull origin main
    cd ..
fi

# Enter project directory
cd $PROJECT_DIR

# Setup environment file
echo "⚙️ Setting up environment..."
if [ ! -f ".env" ]; then
    cp .env.vps.example .env
    echo "📝 Environment file created from template"
    echo "⚠️  IMPORTANT: Edit .env file dengan API keys Anda!"
    echo "   nano .env"
else
    echo "✅ Environment file already exists"
fi

# Create required directories
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p data
chmod 755 logs data

# Start services
echo "🚀 Starting services..."
docker-compose -f docker-compose-vps.yml down
docker-compose -f docker-compose-vps.yml up -d --build

# Wait for services
echo "⏳ Waiting for services to start..."
sleep 10

# Check status
echo "📊 Checking container status..."
docker ps

echo -e "\n=============================================="
echo "🎉 DEPLOYMENT COMPLETED!"
echo "=============================================="
echo "📡 Service URLs:"
echo "   - Main API: http://$(curl -s ifconfig.me):5000"
echo "   - Health: http://$(curl -s ifconfig.me):5000/api/gpts/status"
echo "   - Signals: http://$(curl -s ifconfig.me):5000/api/gpts/sinyal/tajam"
echo ""
echo "🔧 Next Steps:"
echo "1. Edit .env file dengan API keys:"
echo "   nano .env"
echo "2. Restart containers setelah edit:"
echo "   docker-compose -f docker-compose-vps.yml restart"
echo "3. Test endpoint:"
echo "   curl -X POST http://localhost:5000/api/gpts/sinyal/tajam -H 'Content-Type: application/json' -d '{\"symbol\": \"BTCUSDT\"}'"
echo "=============================================="