#!/bin/bash
# VPS Deployment Script - Root User Version
# Special version for root deployment with security considerations

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "${GREEN}[DEPLOY] $1${NC}"; }
info() { echo -e "${BLUE}[INFO] $1${NC}"; }
warn() { echo -e "${YELLOW}[WARN] $1${NC}"; }
error() { echo -e "${RED}[ERROR] $1${NC}"; exit 1; }

log "🚀 ========================================"
log "   CRYPTO TRADING AI - VPS DEPLOYMENT"
log "========================================"
log ""

# Root user deployment with security measures
if [ "$EUID" -eq 0 ]; then
    warn "Running as root - Implementing additional security measures"
    
    # Create application user if not exists
    if ! id "cryptoapp" &>/dev/null; then
        log "Creating application user 'cryptoapp'"
        useradd -m -s /bin/bash cryptoapp
        usermod -aG docker cryptoapp
    fi
    
    # Set proper ownership
    log "Setting proper file ownership"
    chown -R cryptoapp:cryptoapp /root/crypto-analysis-dashboard
    
    # Switch to app user for deployment
    log "Switching to application user for secure deployment"
    sudo -u cryptoapp bash -c "cd /home/cryptoapp && cp -r /root/crypto-analysis-dashboard . && cd crypto-analysis-dashboard && bash deploy-vps.sh"
    exit 0
fi

# Check if running in correct directory
if [ ! -f "main.py" ]; then
    error "Please run this script from the crypto-analysis-dashboard directory"
fi

# Check for required files
log "Checking deployment files..."
required_files=(
    "main.py"
    "docker-compose-vps.yml" 
    "Dockerfile"
    "requirements-prod.txt"
    ".env.vps.example"
)

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        error "Required file missing: $file"
    fi
done

log "✅ All required files found"

# Update system packages
log "Updating system packages..."
if command -v apt-get >/dev/null 2>&1; then
    sudo apt-get update -y
    sudo apt-get upgrade -y
    sudo apt-get install -y curl wget git nano htop
elif command -v yum >/dev/null 2>&1; then
    sudo yum update -y
    sudo yum install -y curl wget git nano htop
fi

# Install Docker if not present
if ! command -v docker >/dev/null 2>&1; then
    log "Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    log "✅ Docker installed"
else
    log "✅ Docker already installed"
fi

# Install Docker Compose if not present
if ! command -v docker-compose >/dev/null 2>&1; then
    log "Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    log "✅ Docker Compose installed"
else
    log "✅ Docker Compose already installed"
fi

# Setup environment file
if [ ! -f ".env" ]; then
    log "Setting up environment file..."
    cp .env.vps.example .env
    warn "⚠️  Please edit .env file with your actual API keys and database credentials"
    warn "⚠️  Run: nano .env"
    warn "⚠️  Then run this script again to continue deployment"
    exit 0
else
    log "✅ Environment file found"
fi

# Check if .env has been configured
if grep -q "your_openai_key" .env; then
    warn "⚠️  Environment file still contains placeholder values"
    warn "⚠️  Please edit .env file with your actual API keys:"
    warn "⚠️  nano .env"
    warn "⚠️  Then run this script again"
    exit 0
fi

# Stop any existing containers
log "Stopping existing containers..."
docker-compose -f docker-compose-vps.yml down --remove-orphans 2>/dev/null || true

# Build and start services
log "Building and starting services..."
docker-compose -f docker-compose-vps.yml build --no-cache
docker-compose -f docker-compose-vps.yml up -d

# Wait for services to start
log "Waiting for services to start..."
sleep 30

# Check service status
log "Checking service status..."
if docker-compose -f docker-compose-vps.yml ps | grep -q "Up"; then
    log "✅ Services are running"
else
    error "❌ Services failed to start. Check logs: docker-compose -f docker-compose-vps.yml logs"
fi

# Health check
log "Performing health check..."
sleep 10

# Test main endpoint
if curl -s http://localhost:5000/ >/dev/null; then
    log "✅ Main application endpoint responding"
else
    warn "⚠️  Main endpoint not responding yet, checking logs..."
    docker-compose -f docker-compose-vps.yml logs crypto-app | tail -20
fi

# Show service URLs
log ""
log "🎯 ========================================"
log "   DEPLOYMENT COMPLETED SUCCESSFULLY!"
log "========================================"
log ""
log "🌐 Service URLs:"
log "   Main API: http://$(curl -s ifconfig.me):5000"
log "   Health Check: http://$(curl -s ifconfig.me):5000/"
log "   GPTs API: http://$(curl -s ifconfig.me):5000/api/gpts/sinyal/tajam"
log "   Performance: http://$(curl -s ifconfig.me):5000/api/performance/stats"
log ""
log "🔧 Management Commands:"
log "   View logs: docker-compose -f docker-compose-vps.yml logs -f"
log "   Restart: docker-compose -f docker-compose-vps.yml restart"
log "   Stop: docker-compose -f docker-compose-vps.yml down"
log "   Update: git pull && docker-compose -f docker-compose-vps.yml up -d --build"
log ""
log "📊 Monitor system:"
log "   CPU/Memory: htop"
log "   Docker stats: docker stats"
log "   Service status: docker-compose -f docker-compose-vps.yml ps"
log ""

# Setup automatic updates (optional)
read -p "Setup automatic daily updates? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    log "Setting up automatic updates..."
    
    # Create update script
    cat > /usr/local/bin/crypto-app-update.sh << 'EOF'
#!/bin/bash
cd /home/cryptoapp/crypto-analysis-dashboard
git pull origin main
docker-compose -f docker-compose-vps.yml up -d --build
EOF
    
    chmod +x /usr/local/bin/crypto-app-update.sh
    
    # Add to crontab (daily at 3 AM)
    (crontab -l 2>/dev/null; echo "0 3 * * * /usr/local/bin/crypto-app-update.sh >> /var/log/crypto-app-update.log 2>&1") | crontab -
    
    log "✅ Automatic daily updates configured"
fi

log "🚀 Crypto Trading AI Platform is now live!"
log "🔗 Share this URL with ChatGPT for GPTs integration"
log ""