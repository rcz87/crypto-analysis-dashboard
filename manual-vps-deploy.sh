#!/bin/bash
# Manual VPS Deployment - Run langsung di VPS

echo "🚀 CRYPTOCURRENCY TRADING PLATFORM - VPS SETUP"
echo "=============================================="

# Update system
echo "📦 Updating system..."
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
apt-get install -y docker-compose-plugin

# Install Git
echo "📋 Installing Git..."
apt-get install -y git curl nano

# Clone/Update repository
echo "📥 Setting up repository..."
if [ ! -d "crypto-analysis-dashboard" ]; then
    git clone https://github.com/rcz87/crypto-analysis-dashboard.git
    echo "✅ Repository cloned"
else
    echo "📁 Updating existing repository..."
    cd crypto-analysis-dashboard
    git pull origin main
    cd ..
fi

cd crypto-analysis-dashboard

# Create environment file
echo "⚙️ Creating environment file..."
cat > .env << 'EOF'
# Cryptocurrency Trading Platform - VPS Environment Configuration

# OKX API Configuration (REQUIRED)
OKX_API_KEY=your_okx_api_key_here
OKX_SECRET_KEY=your_okx_secret_key_here
OKX_PASSPHRASE=your_okx_passphrase_here

# OpenAI API Configuration (REQUIRED)
OPENAI_API_KEY=your_openai_api_key_here

# Telegram Bot Configuration (OPTIONAL)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
ADMIN_CHAT_ID=your_admin_chat_id_here

# Database Configuration
POSTGRES_PASSWORD=crypto_secure_password_2024
DATABASE_URL=postgresql://crypto_user:crypto_secure_password_2024@postgres:5432/crypto_trading

# Flask Configuration
FLASK_ENV=production
FLASK_SECRET_KEY=crypto_trading_secret_key_production_2024
PRODUCTION_ONLY=1
PYTHONDONTWRITEBYTECODE=1
PYTHONUNBUFFERED=1
EOF

# Create directories
echo "📁 Creating directories..."
mkdir -p logs data
chmod 755 logs data

# Start services
echo "🚀 Starting services..."
docker-compose -f docker-compose-vps.yml down || true
docker-compose -f docker-compose-vps.yml up -d --build

# Wait for services
echo "⏳ Waiting for services..."
sleep 15

# Check status
echo "📊 Container status:"
docker ps

echo ""
echo "=============================================="
echo "🎉 SETUP COMPLETED!"
echo "=============================================="
echo "🔧 NEXT STEPS:"
echo "1. Edit API keys:"
echo "   nano .env"
echo ""
echo "2. Restart after editing:"
echo "   docker-compose -f docker-compose-vps.yml restart"
echo ""
echo "3. Test endpoint:"
echo "   curl -X POST http://localhost:5000/api/gpts/sinyal/tajam \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"symbol\": \"BTCUSDT\", \"timeframe\": \"1H\"}'"
echo ""
echo "📡 External URLs:"
echo "   - Main API: http://$(curl -s ifconfig.me 2>/dev/null || echo 'YOUR_VPS_IP'):5000"
echo "   - Signals: http://$(curl -s ifconfig.me 2>/dev/null || echo 'YOUR_VPS_IP'):5000/api/gpts/sinyal/tajam"
echo "=============================================="