#!/bin/bash

# Automated VPS Deployment Script for Cryptocurrency Trading Platform
# Run this script on your VPS server

set -e  # Exit on any error

echo "🚀 VPS DEPLOYMENT SCRIPT - Cryptocurrency Trading Platform"
echo "=========================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root for security reasons"
   exit 1
fi

# 1. System Update and Dependencies
print_step "1. Updating system and installing dependencies..."
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv git nginx postgresql-client curl jq htop

# 2. Create application directory
APP_DIR="/home/$(whoami)/crypto-analysis-dashboard"
print_step "2. Setting up application directory: $APP_DIR"

if [ -d "$APP_DIR" ]; then
    print_warning "Directory exists. Backing up..."
    sudo mv "$APP_DIR" "${APP_DIR}_backup_$(date +%Y%m%d_%H%M%S)"
fi

mkdir -p "$APP_DIR"
cd "$APP_DIR"

# 3. Clone or copy application code
print_step "3. Setting up application code..."
# If you have a git repository, uncomment and modify:
# git clone https://github.com/yourusername/crypto-analysis-dashboard.git .

# For now, we'll assume code is already uploaded
if [ ! -f "main.py" ]; then
    print_error "Application code not found. Please upload your code to $APP_DIR"
    exit 1
fi

# 4. Python environment setup
print_step "4. Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# 5. Install Python dependencies
print_step "5. Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
elif [ -f "requirements.lock" ]; then
    pip install -r requirements.lock
else
    print_error "No requirements file found!"
    exit 1
fi

# Install additional production dependencies
pip install gunicorn psycopg2-binary

# 6. Environment variables setup
print_step "6. Setting up environment variables..."

# Create environment file template
cat > .env.production << 'EOF'
# Production Environment Variables
# IMPORTANT: Replace these placeholder values with your actual credentials

# Database Configuration (Neon PostgreSQL)
DATABASE_URL=postgresql://neondb_owner:YOUR_NEON_PASSWORD@ep-billowing-sunset-xxxx.us-east-2.aws.neon.tech/neondb?sslmode=require
SQLALCHEMY_DATABASE_URI=postgresql://neondb_owner:YOUR_NEON_PASSWORD@ep-billowing-sunset-xxxx.us-east-2.aws.neon.tech/neondb?sslmode=require

# Application Configuration
FLASK_ENV=production
API_KEY_REQUIRED=true
API_KEY=your-super-secret-api-key-here

# AI Services
OPENAI_API_KEY=sk-proj-your-openai-key-here

# Trading API (OKX)
OKX_API_KEY=your-okx-api-key
OKX_SECRET_KEY=your-okx-secret-key
OKX_PASSPHRASE=your-okx-passphrase

# Security
SESSION_SECRET=your-super-secret-session-key-for-production

# Optional Services
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
TELEGRAM_CHAT_ID=your-telegram-chat-id
REDIS_URL=redis://localhost:6379/0
EOF

print_warning "Environment file created at .env.production"
print_warning "IMPORTANT: Edit .env.production with your actual credentials!"

# 7. Systemd service setup
print_step "7. Creating systemd service..."

sudo tee /etc/systemd/system/cryptoapi.service > /dev/null << EOF
[Unit]
Description=Cryptocurrency Trading API
After=network.target

[Service]
Type=notify
User=$(whoami)
Group=$(whoami)
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/venv/bin
EnvironmentFile=$APP_DIR/.env.production
ExecStart=$APP_DIR/venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 4 --worker-class gthread --threads 4 --timeout 60 --keep-alive 2 --max-requests 1000 --max-requests-jitter 50 --preload --access-logfile - --error-logfile - main:app
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# 8. Nginx configuration
print_step "8. Setting up Nginx reverse proxy..."

sudo tee /etc/nginx/sites-available/cryptoapi > /dev/null << 'EOF'
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;  # Replace with your domain
    
    # Security headers
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    
    location / {
        limit_req zone=api burst=20 nodelay;
        
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # Buffer settings
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
    }
    
    # Health check endpoint (no rate limiting)
    location /health {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        access_log off;
    }
    
    # Static files (if any)
    location /static {
        alias $APP_DIR/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

# Enable site and remove default
sudo ln -sf /etc/nginx/sites-available/cryptoapi /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test nginx configuration
sudo nginx -t

# 9. Firewall setup
print_step "9. Configuring firewall..."
sudo ufw allow 22/tcp  # SSH
sudo ufw allow 80/tcp  # HTTP
sudo ufw allow 443/tcp # HTTPS
sudo ufw --force enable

# 10. Start services
print_step "10. Starting services..."
sudo systemctl daemon-reload
sudo systemctl enable cryptoapi.service
sudo systemctl enable nginx

# Don't start yet - need to configure environment first
print_warning "Services configured but not started yet."

# 11. SSL Certificate setup (Let's Encrypt)
print_step "11. Setting up SSL certificate..."
sudo apt install -y certbot python3-certbot-nginx

print_status "SSL setup prepared. After configuring your domain, run:"
print_status "sudo certbot --nginx -d your-domain.com -d www.your-domain.com"

# 12. Create deployment scripts
print_step "12. Creating management scripts..."

# Start script
cat > start_services.sh << 'EOF'
#!/bin/bash
echo "Starting Cryptocurrency Trading API services..."
sudo systemctl start cryptoapi.service
sudo systemctl start nginx
sudo systemctl status cryptoapi.service
EOF

# Stop script
cat > stop_services.sh << 'EOF'
#!/bin/bash
echo "Stopping Cryptocurrency Trading API services..."
sudo systemctl stop cryptoapi.service
sudo systemctl stop nginx
EOF

# Status script
cat > check_status.sh << 'EOF'
#!/bin/bash
echo "=== Service Status ==="
sudo systemctl status cryptoapi.service --no-pager
echo ""
echo "=== Nginx Status ==="
sudo systemctl status nginx --no-pager
echo ""
echo "=== Application Health ==="
curl -s http://localhost:5000/health | jq '.' || echo "Health check failed"
echo ""
echo "=== Environment Check ==="
PID=$(systemctl show -p MainPID --value cryptoapi.service)
if [ "$PID" != "0" ]; then
    echo "Environment variables in use:"
    tr '\0' '\n' </proc/$PID/environ | grep -E 'DATABASE_URL|API_KEY|FLASK_ENV' | head -5
else
    echo "Service not running"
fi
EOF

# Logs script
cat > view_logs.sh << 'EOF'
#!/bin/bash
echo "=== Application Logs (last 50 lines) ==="
sudo journalctl -u cryptoapi.service -n 50 --no-pager
echo ""
echo "=== Nginx Access Logs (last 20 lines) ==="
sudo tail -20 /var/log/nginx/access.log
echo ""
echo "=== Nginx Error Logs (last 20 lines) ==="
sudo tail -20 /var/log/nginx/error.log
EOF

chmod +x *.sh

print_step "13. Final setup complete!"

echo ""
echo "🎉 VPS DEPLOYMENT SETUP COMPLETE!"
echo "================================="
echo ""
print_status "Next steps to complete deployment:"
echo ""
echo "1. 📝 Edit environment variables:"
echo "   nano $APP_DIR/.env.production"
echo ""
echo "2. 🌐 Update domain in Nginx config:"
echo "   sudo nano /etc/nginx/sites-available/cryptoapi"
echo ""
echo "3. 🚀 Start services:"
echo "   cd $APP_DIR && ./start_services.sh"
echo ""
echo "4. 🔒 Setup SSL certificate:"
echo "   sudo certbot --nginx -d your-domain.com"
echo ""
echo "5. ✅ Check status:"
echo "   ./check_status.sh"
echo ""
print_status "Management scripts created:"
echo "   • start_services.sh - Start all services"
echo "   • stop_services.sh - Stop all services" 
echo "   • check_status.sh - Check service status and health"
echo "   • view_logs.sh - View application and nginx logs"
echo ""
print_warning "Remember to:"
print_warning "• Replace placeholder values in .env.production"
print_warning "• Update domain name in Nginx config"
print_warning "• Configure DNS to point to this server"
print_warning "• Setup SSL certificate after domain configuration"