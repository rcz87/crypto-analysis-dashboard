#!/bin/bash

# ===============================================
# 🚀 CRYPTO TRADING AI - VPS DEPLOYMENT SCRIPT
# ===============================================
# Deploy to Hostinger VPS or any Linux VPS
# Usage: ./deploy-vps.sh

set -e  # Exit on any error

echo "🚀 ========================================"
echo "   CRYPTO TRADING AI - VPS DEPLOYMENT"
echo "========================================"
echo ""

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo "❌ This script should not be run as root for security reasons"
   echo "   Run as regular user with sudo privileges"
   exit 1
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to install Docker
install_docker() {
    echo "📦 Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    echo "✅ Docker installed successfully"
}

# Function to install Docker Compose
install_docker_compose() {
    echo "📦 Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo "✅ Docker Compose installed successfully"
}

# Check and install prerequisites
echo "🔍 Checking prerequisites..."

if ! command_exists docker; then
    install_docker
    echo "⚠️  Docker installed. Please log out and log back in to apply group changes."
    echo "   Then run this script again."
    exit 0
else
    echo "✅ Docker is installed"
fi

if ! command_exists docker-compose; then
    install_docker_compose
else
    echo "✅ Docker Compose is installed"
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Creating .env file from template..."
    cp .env.vps.example .env
    echo ""
    echo "🔧 IMPORTANT: Edit .env file with your configuration:"
    echo "   - OKX API credentials"
    echo "   - OpenAI API key"
    echo "   - PostgreSQL password"
    echo "   - Telegram bot token (optional)"
    echo ""
    echo "📝 Edit .env file: nano .env"
    echo ""
    read -p "Press Enter after you've configured .env file..."
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs/nginx nginx/ssl
sudo chown -R $USER:$USER logs

# Set up firewall
echo "🔥 Configuring firewall..."
if command_exists ufw; then
    sudo ufw --force enable
    sudo ufw allow 22/tcp     # SSH
    sudo ufw allow 80/tcp     # HTTP
    sudo ufw allow 443/tcp    # HTTPS
    echo "✅ Firewall configured"
else
    echo "⚠️  UFW not installed, skipping firewall setup"
fi

# Build and start services
echo "🏗️  Building and starting services..."
docker-compose -f docker-compose-vps.yml down --remove-orphans 2>/dev/null || true
docker-compose -f docker-compose-vps.yml build --no-cache
docker-compose -f docker-compose-vps.yml up -d

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 30

# Check service status
echo "🩺 Checking service health..."
if curl -f http://localhost/health >/dev/null 2>&1; then
    echo "✅ Application is healthy and running!"
else
    echo "❌ Application health check failed"
    echo "📋 Checking logs..."
    docker-compose -f docker-compose-vps.yml logs --tail=20 crypto-app
    exit 1
fi

# Get server IP
SERVER_IP=$(curl -s http://checkip.amazonaws.com/ || echo "Unable to detect IP")

echo ""
echo "🎉 ========================================"
echo "   DEPLOYMENT SUCCESSFUL!"
echo "========================================"
echo ""
echo "🌐 Your application is now running at:"
echo "   HTTP:  http://$SERVER_IP"
echo "   Local: http://localhost"
echo ""
echo "📊 API Endpoints:"
echo "   Health: http://$SERVER_IP/health"
echo "   GPTs API: http://$SERVER_IP/api/gpts/"
echo ""
echo "🛠️  Management Commands:"
echo "   View logs: docker-compose -f docker-compose-vps.yml logs -f"
echo "   Restart:   docker-compose -f docker-compose-vps.yml restart"
echo "   Stop:      docker-compose -f docker-compose-vps.yml down"
echo "   Update:    git pull && docker-compose -f docker-compose-vps.yml up -d --build"
echo ""
echo "🔒 Next Steps (Optional):"
echo "   1. Set up SSL certificate with Let's Encrypt"
echo "   2. Configure domain name in nginx config"
echo "   3. Set up monitoring and backups"
echo ""
echo "✅ Deployment completed successfully!"
echo "========================================"