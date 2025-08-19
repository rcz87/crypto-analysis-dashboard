#!/bin/bash
# VPS Auto Deployment Script untuk Cryptocurrency Trading Platform
# Usage: ./vps-auto-deploy.sh

set -e

# Configuration
APP_NAME="crypto-trading-api"
APP_DIR="/var/www/$APP_NAME"
BACKUP_DIR="/var/backups/$APP_NAME"
SERVICE_NAME="crypto-trading"
NGINX_CONFIG="/etc/nginx/sites-available/$APP_NAME"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

# Function: Create backup before deployment
create_backup() {
    log "Creating backup..."
    
    # Create backup directory if not exists
    mkdir -p $BACKUP_DIR
    
    # Backup current application
    if [ -d "$APP_DIR" ]; then
        tar -czf "$BACKUP_DIR/backup-$(date +%Y%m%d-%H%M%S).tar.gz" -C "$APP_DIR" .
        log "Backup created successfully"
    else
        warn "Application directory not found, skipping backup"
    fi
}

# Function: Deploy application
deploy_application() {
    log "Starting deployment..."
    
    # Create app directory if not exists
    mkdir -p $APP_DIR
    cd $APP_DIR
    
    # Pull latest code (assumes git repo is already cloned)
    if [ -d ".git" ]; then
        log "Pulling latest code from repository..."
        git pull origin main
    else
        error "Git repository not found. Please clone your repository first."
    fi
    
    # Install/update Python dependencies
    log "Installing Python dependencies..."
    if [ -f "requirements-prod.txt" ]; then
        pip3 install -r requirements-prod.txt
    elif [ -f "requirements.txt" ]; then
        pip3 install -r requirements.txt
    else
        warn "No requirements file found"
    fi
    
    # Set proper permissions
    chown -R www-data:www-data $APP_DIR
    chmod -R 755 $APP_DIR
    
    log "Application deployed successfully"
}

# Function: Setup systemd service
setup_systemd_service() {
    log "Setting up systemd service..."
    
    cat > /etc/systemd/system/$SERVICE_NAME.service << EOF
[Unit]
Description=Cryptocurrency Trading API
After=network.target

[Service]
Type=forking
User=www-data
Group=www-data
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/venv/bin
ExecStart=$APP_DIR/venv/bin/gunicorn --config gunicorn.conf.py wsgi_production:application
ExecReload=/bin/kill -s HUP \$MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    systemctl enable $SERVICE_NAME
    log "Systemd service configured"
}

# Function: Setup Nginx configuration
setup_nginx() {
    log "Setting up Nginx configuration..."
    
    cat > $NGINX_CONFIG << EOF
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    # Security headers
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";
    
    # Rate limiting
    limit_req_zone \$binary_remote_addr zone=api:10m rate=10r/s;
    limit_req zone=api burst=20 nodelay;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Timeout settings
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Health check endpoint
    location /health {
        proxy_pass http://127.0.0.1:5000/health;
        access_log off;
    }
    
    # Static files (if any)
    location /static {
        root $APP_DIR;
        expires 1y;
        add_header Cache-Control public;
    }
}
EOF

    # Enable site
    ln -sf $NGINX_CONFIG /etc/nginx/sites-enabled/
    nginx -t && systemctl reload nginx
    log "Nginx configured successfully"
}

# Function: Restart services
restart_services() {
    log "Restarting services..."
    
    # Restart application service
    systemctl restart $SERVICE_NAME
    
    # Check service status
    if systemctl is-active --quiet $SERVICE_NAME; then
        log "Service $SERVICE_NAME restarted successfully"
    else
        error "Failed to start $SERVICE_NAME service"
    fi
    
    # Reload Nginx
    systemctl reload nginx
    log "Nginx reloaded"
}

# Function: Health check
health_check() {
    log "Performing health check..."
    
    # Wait for service to start
    sleep 5
    
    # Check if service is running
    if curl -f -s http://localhost:5000/health > /dev/null; then
        log "Health check passed - Application is running"
    else
        error "Health check failed - Application is not responding"
    fi
}

# Function: Rollback if deployment fails
rollback() {
    warn "Deployment failed, initiating rollback..."
    
    # Find latest backup
    LATEST_BACKUP=$(ls -t $BACKUP_DIR/backup-*.tar.gz 2>/dev/null | head -n 1)
    
    if [ -n "$LATEST_BACKUP" ]; then
        log "Restoring from backup: $LATEST_BACKUP"
        
        # Extract backup
        cd $APP_DIR
        tar -xzf "$LATEST_BACKUP"
        
        # Restart services
        systemctl restart $SERVICE_NAME
        
        log "Rollback completed"
    else
        error "No backup found for rollback"
    fi
}

# Main deployment process
main() {
    log "Starting VPS deployment for Cryptocurrency Trading Platform"
    
    # Check if running as root
    if [ "$EUID" -ne 0 ]; then
        error "Please run as root (use sudo)"
    fi
    
    # Trap errors for rollback
    trap rollback ERR
    
    # Deployment steps
    create_backup
    deploy_application
    
    # Setup services (only on first run)
    if [ "$1" = "--initial-setup" ]; then
        log "Performing initial setup..."
        setup_systemd_service
        setup_nginx
    fi
    
    restart_services
    health_check
    
    log "Deployment completed successfully!"
    log "Application is running at: http://your-domain.com"
    
    # Show service status
    systemctl status $SERVICE_NAME --no-pager -l
}

# Script usage
if [ "$1" = "--help" ]; then
    echo "VPS Auto Deployment Script"
    echo "Usage:"
    echo "  $0                 # Regular deployment"
    echo "  $0 --initial-setup # First time setup with services"
    echo "  $0 --help         # Show this help"
    exit 0
fi

# Run main function
main "$@"