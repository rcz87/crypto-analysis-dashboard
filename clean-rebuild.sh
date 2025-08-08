#!/bin/bash
# Clean rebuild script untuk mengatasi ContainerConfig error

echo "🔧 Cleaning Docker system completely..."

# Stop semua container
docker-compose -f docker-compose-vps.yml down --remove-orphans --volumes 2>/dev/null || true

# Hapus semua container crypto
docker rm -f $(docker ps -aq --filter name=crypto) 2>/dev/null || true

# Hapus semua image crypto
docker rmi -f $(docker images -q crypto-analysis-dashboard_crypto-app) 2>/dev/null || true

# Clean Docker system
docker system prune -af --volumes

echo "✅ Docker system cleaned"

echo "🔧 Setting up environment..."
# Setup .env jika belum ada
if [ ! -f ".env" ]; then
    cp .env.vps.example .env
    echo "⚠️  Edit .env file dengan API keys Anda:"
    echo "   nano .env"
    echo ""
    echo "Minimal required:"
    echo "OPENAI_API_KEY=your_key_here"
    echo "OKX_API_KEY=your_key_here"
    echo "OKX_SECRET_KEY=your_key_here"
    echo "OKX_PASSPHRASE=your_key_here"
    echo ""
    echo "After editing .env, run: docker-compose -f docker-compose-vps.yml up -d"
    exit 0
fi

echo "🔧 Building application..."
# Build tanpa cache
docker-compose -f docker-compose-vps.yml build --no-cache

echo "🚀 Starting services..."
# Start services
docker-compose -f docker-compose-vps.yml up -d

sleep 10

echo "📊 Checking status..."
docker-compose -f docker-compose-vps.yml ps

echo ""
echo "✅ Deployment completed!"
echo "🌐 Access: http://$(curl -s ifconfig.me):5000"
echo "📝 Logs: docker-compose -f docker-compose-vps.yml logs -f crypto-app"
