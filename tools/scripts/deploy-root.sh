#!/bin/bash
# Root deployment script for crypto-analysis-dashboard

set -e

echo "🚀 Crypto Trading AI - Root Deployment"
echo "======================================"

# Install Docker if not present
if ! command -v docker >/dev/null 2>&1; then
    echo "Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
fi

# Install Docker Compose if not present
if ! command -v docker-compose >/dev/null 2>&1; then
    echo "Installing Docker Compose..."
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

# Setup environment file
if [ ! -f ".env" ]; then
    echo "Setting up environment file..."
    cp .env.vps.example .env
    echo "⚠️  Please edit .env file with your API keys"
    echo "   nano .env"
    echo "   Then run: docker-compose -f docker-compose-vps.yml up -d"
    exit 0
fi

# Stop existing containers
echo "Stopping existing containers..."
docker-compose -f docker-compose-vps.yml down 2>/dev/null || true

# Build and start
echo "Building and starting services..."
docker-compose -f docker-compose-vps.yml up -d --build

echo "✅ Deployment completed!"
echo "🌐 Check: http://$(curl -s ifconfig.me):5000"
