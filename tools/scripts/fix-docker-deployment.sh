#!/bin/bash
# Fix Docker deployment issues - Dependencies dan Database

echo "🔧 FIXING DOCKER DEPLOYMENT ISSUES"
echo "=================================="

# Stop containers
echo "🛑 Stopping containers..."
docker-compose -f docker-compose-vps.yml down

# Remove old containers and images 
echo "🗑️ Cleaning old containers..."
docker system prune -f
docker rmi crypto-analysis-dashboard-crypto-app 2>/dev/null || true

# Fix .env file dengan password yang benar
echo "⚙️ Fixing .env file..."
cat > .env << 'EOF'
# OKX API Configuration (REQUIRED)
OKX_API_KEY=your_okx_api_key_here
OKX_SECRET_KEY=your_okx_secret_key_here
OKX_PASSPHRASE=your_okx_passphrase_here

# OpenAI API Configuration (REQUIRED)
OPENAI_API_KEY=your_openai_api_key_here

# Telegram Bot Configuration (OPTIONAL)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
ADMIN_CHAT_ID=your_admin_chat_id_here

# Database Configuration - FIXED PASSWORD
POSTGRES_PASSWORD=crypto_secure_password_2024
DATABASE_URL=postgresql://crypto_user:crypto_secure_password_2024@postgres:5432/crypto_trading

# Flask Configuration
FLASK_ENV=production
FLASK_SECRET_KEY=crypto_trading_secret_key_production_2024
PRODUCTION_ONLY=1
PYTHONDONTWRITEBYTECODE=1
PYTHONUNBUFFERED=1
EOF

# Reset PostgreSQL data untuk password baru
echo "🗃️ Resetting PostgreSQL data..."
docker volume rm crypto-analysis-dashboard_postgres_data 2>/dev/null || true

# Build dan start dengan clean containers
echo "🚀 Building and starting containers..."
docker-compose -f docker-compose-vps.yml up -d --build --force-recreate

# Wait untuk containers
echo "⏳ Waiting for containers to start..."
sleep 30

# Check status
echo "📊 Container status:"
docker ps

echo ""
echo "📋 Recent logs:"
docker-compose -f docker-compose-vps.yml logs --tail=10

echo ""
echo "=================================="
echo "🎯 NEXT STEPS:"
echo "1. Edit API keys:"
echo "   nano .env"
echo "2. Restart containers:"
echo "   docker-compose -f docker-compose-vps.yml restart"
echo "3. Test endpoint:"
echo "   curl -X POST http://localhost:5000/api/gpts/sinyal/tajam -H 'Content-Type: application/json' -d '{\"symbol\": \"BTCUSDT\"}'"
echo "=================================="