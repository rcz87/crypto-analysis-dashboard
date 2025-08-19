#!/bin/bash

# VPS Hostinger Deployment Script
# Cryptocurrency Trading AI Platform

echo "🚀 Starting VPS Hostinger deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="crypto-trading-ai"
APP_DIR="/var/www/$APP_NAME"
DOMAIN="yourdomain.com"  # Replace with your domain
USER="www-data"

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   log_error "This script should not be run as root for security reasons"
   exit 1
fi

# Check if we have sudo access
if ! sudo -n true 2>/dev/null; then
    log_error "This script requires sudo access"
    exit 1
fi

log_info "Updating system packages..."
sudo apt update && sudo apt upgrade -y

log_info "Installing required packages..."
sudo apt install -y python3 python3-pip python3-venv nginx postgresql postgresql-contrib redis-server git curl

# Create application directory
log_info "Setting up application directory..."
sudo mkdir -p $APP_DIR
sudo chown $USER:$USER $APP_DIR

# Copy application files
log_info "Copying application files..."
cp -r . $APP_DIR/
cd $APP_DIR

# Create virtual environment
log_info "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
log_info "Installing Python dependencies..."
pip install -r pyproject.toml

# Set up PostgreSQL database
log_info "Setting up PostgreSQL database..."
sudo -u postgres createdb $APP_NAME 2>/dev/null || log_warn "Database may already exist"
sudo -u postgres createuser $APP_NAME 2>/dev/null || log_warn "User may already exist"

# Generate random password for database
DB_PASSWORD=$(openssl rand -base64 32)
sudo -u postgres psql -c "ALTER USER $APP_NAME WITH PASSWORD '$DB_PASSWORD';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $APP_NAME TO $APP_NAME;"

# Create environment file
log_info "Creating environment configuration..."
cat > .env << EOF
# Database Configuration
DATABASE_URL=postgresql://$APP_NAME:$DB_PASSWORD@localhost/$APP_NAME
PGDATABASE=$APP_NAME
PGUSER=$APP_NAME
PGPASSWORD=$DB_PASSWORD
PGHOST=localhost
PGPORT=5432

# Flask Configuration
FLASK_ENV=production
SECRET_KEY=$(openssl rand -base64 32)
PORT=5000

# API Keys (you need to set these manually)
OPENAI_API_KEY=your_openai_api_key_here
OKX_API_KEY=your_okx_api_key_here
OKX_SECRET_KEY=your_okx_secret_key_here
OKX_PASSPHRASE=your_okx_passphrase_here
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# Domain Configuration
DOMAIN_URL=https://$DOMAIN
EOF

log_info "Setting up file permissions..."
sudo chown -R $USER:$USER $APP_DIR
chmod 600 .env

# Initialize database
log_info "Initializing database..."
source venv/bin/activate
python -c "from app import app, db; app.app_context().push(); db.create_all()"

# Create systemd service
log_info "Creating systemd service..."
sudo tee /etc/systemd/system/$APP_NAME.service > /dev/null << EOF
[Unit]
Description=Cryptocurrency Trading AI Platform
After=network.target

[Service]
Type=exec
User=$USER
Group=$USER
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/venv/bin
EnvironmentFile=$APP_DIR/.env
ExecStart=$APP_DIR/venv/bin/gunicorn --config gunicorn.conf.py main:app
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Create Gunicorn configuration
log_info "Creating Gunicorn configuration..."
cat > gunicorn.conf.py << 'EOF'
import multiprocessing
import os

# Server socket
bind = "127.0.0.1:5000"
backlog = 2048

# Worker processes
workers = min(multiprocessing.cpu_count() * 2 + 1, 4)
worker_class = 'sync'
worker_connections = 1000
timeout = 120
keepalive = 2

# Restart workers after this many requests
max_requests = 1000
max_requests_jitter = 100

# Logging
accesslog = '/var/log/crypto-trading-ai/access.log'
errorlog = '/var/log/crypto-trading-ai/error.log'
loglevel = 'info'

# Process naming
proc_name = 'crypto-trading-ai'

# Preload app for better performance
preload_app = True
EOF

# Create log directory
sudo mkdir -p /var/log/crypto-trading-ai
sudo chown $USER:$USER /var/log/crypto-trading-ai

# Configure Nginx
log_info "Configuring Nginx..."
sudo cp deployment/nginx_config.conf /etc/nginx/sites-available/$APP_NAME
sudo sed -i "s/yourdomain.com/$DOMAIN/g" /etc/nginx/sites-available/$APP_NAME
sudo ln -sf /etc/nginx/sites-available/$APP_NAME /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
sudo nginx -t
if [ $? -ne 0 ]; then
    log_error "Nginx configuration test failed"
    exit 1
fi

# Start and enable services
log_info "Starting services..."
sudo systemctl daemon-reload
sudo systemctl enable $APP_NAME
sudo systemctl start $APP_NAME
sudo systemctl enable nginx
sudo systemctl restart nginx
sudo systemctl enable redis-server
sudo systemctl start redis-server

# Check service status
log_info "Checking service status..."
if sudo systemctl is-active --quiet $APP_NAME; then
    log_info "✅ Application service is running"
else
    log_error "❌ Application service failed to start"
    sudo systemctl status $APP_NAME
fi

if sudo systemctl is-active --quiet nginx; then
    log_info "✅ Nginx is running"
else
    log_error "❌ Nginx failed to start"
    sudo systemctl status nginx
fi

# Setup SSL certificate (Let's Encrypt)
log_info "Setting up SSL certificate..."
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d $DOMAIN -d www.$DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN

# Final status check
log_info "Performing final status check..."
sleep 5

# Test API endpoint
if curl -s http://localhost:5000/health > /dev/null; then
    log_info "✅ API is responding locally"
else
    log_error "❌ API is not responding"
fi

# Display completion message
log_info "🎉 Deployment completed!"
echo ""
echo "Next steps:"
echo "1. Update API keys in $APP_DIR/.env"
echo "2. Restart the application: sudo systemctl restart $APP_NAME"
echo "3. Check logs: sudo journalctl -f -u $APP_NAME"
echo "4. Test your domain: https://$DOMAIN/health"
echo ""
echo "Important files:"
echo "- Application: $APP_DIR"
echo "- Environment: $APP_DIR/.env"
echo "- Nginx config: /etc/nginx/sites-available/$APP_NAME"
echo "- Service logs: sudo journalctl -u $APP_NAME"
echo ""

log_info "Deployment script completed successfully!"