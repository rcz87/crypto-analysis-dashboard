#!/bin/bash
# Complete VPS Setup untuk Cryptocurrency Trading Platform
# Script lengkap untuk setup awal di VPS Hostinger

set -e

# Configuration
DOMAIN="gpts.guardiansofthetoken.id"
APP_NAME="crypto-trading-api"
APP_DIR="/var/www/$APP_NAME"
DB_NAME="crypto_trading"
DB_USER="crypto_user"
DB_PASS="$(openssl rand -base64 32)"
ADMIN_EMAIL="your-email@domain.com"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() { echo -e "${GREEN}[$(date '+%H:%M:%S')] $1${NC}"; }
warn() { echo -e "${YELLOW}[$(date '+%H:%M:%S')] $1${NC}"; }
error() { echo -e "${RED}[$(date '+%H:%M:%S')] ERROR: $1${NC}"; exit 1; }
info() { echo -e "${BLUE}[$(date '+%H:%M:%S')] $1${NC}"; }

# Check if running as root
[[ $EUID -eq 0 ]] || error "Please run as root (use sudo)"

log "🚀 Starting Complete VPS Setup for Cryptocurrency Trading Platform"

# 1. System Update & Dependencies
log "📦 Installing system dependencies..."
apt update && apt upgrade -y
apt install -y python3 python3-pip python3-venv postgresql postgresql-contrib nginx certbot python3-certbot-nginx git curl wget htop ufw fail2ban redis-server

# 2. Configure Firewall
log "🔒 Configuring firewall..."
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 'Nginx Full'
ufw --force enable

# 3. Configure Fail2ban
log "🛡️ Setting up Fail2ban..."
cat > /etc/fail2ban/jail.local << EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3

[sshd]
enabled = true
port = ssh
logpath = /var/log/auth.log

[nginx-http-auth]
enabled = true

[nginx-limit-req]
enabled = true
filter = nginx-limit-req
action = iptables-multiport[name=ReqLimit, port="http,https", protocol=tcp]
logpath = /var/log/nginx/error.log
maxretry = 10
EOF

systemctl enable fail2ban
systemctl start fail2ban

# 4. Setup PostgreSQL
log "🗄️ Setting up PostgreSQL database..."
sudo -u postgres createuser --createdb $DB_USER || true
sudo -u postgres psql -c "ALTER USER $DB_USER PASSWORD '$DB_PASS';" || true
sudo -u postgres createdb -O $DB_USER $DB_NAME || true

# Configure PostgreSQL
sed -i "s/#listen_addresses = 'localhost'/listen_addresses = 'localhost'/" /etc/postgresql/*/main/postgresql.conf
systemctl restart postgresql

# 5. Setup Redis
log "🔴 Configuring Redis..."
sed -i 's/# maxmemory <bytes>/maxmemory 256mb/' /etc/redis/redis.conf
sed -i 's/# maxmemory-policy noeviction/maxmemory-policy allkeys-lru/' /etc/redis/redis.conf
systemctl restart redis-server

# 6. Create Application User & Directory
log "👤 Setting up application environment..."
useradd -m -s /bin/bash crypto-app || true
mkdir -p $APP_DIR
cd $APP_DIR

# Clone repository (user needs to provide git URL)
if [ ! -d ".git" ]; then
    warn "Please clone your GitHub repository manually:"
    info "cd $APP_DIR && git clone https://github.com/YOUR-USERNAME/YOUR-REPO.git ."
    info "Then run this script again."
    exit 1
fi

# 7. Setup Python Virtual Environment
log "🐍 Setting up Python environment..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements-prod.txt || pip install -r requirements.txt

# 8. Create Environment File
log "⚙️ Creating environment configuration..."
cat > .env << EOF
# Production Environment Variables
FLASK_ENV=production
FLASK_DEBUG=false
SECRET_KEY=$(openssl rand -base64 32)

# Database
DATABASE_URL=postgresql://$DB_USER:$DB_PASS@localhost/$DB_NAME

# Redis
REDIS_URL=redis://localhost:6379/0

# API Keys (CONFIGURE THESE)
OKX_API_KEY=your-okx-api-key
OKX_SECRET_KEY=your-okx-secret-key
OKX_PASSPHRASE=your-okx-passphrase

OPENAI_API_KEY=your-openai-api-key

TELEGRAM_BOT_TOKEN=your-telegram-bot-token
TELEGRAM_CHAT_ID=your-telegram-chat-id

# Security
ALLOWED_HOSTS=$DOMAIN,www.$DOMAIN
CORS_ORIGINS=https://$DOMAIN,https://www.$DOMAIN
EOF

# 9. Set Permissions
chown -R crypto-app:crypto-app $APP_DIR
chmod -R 755 $APP_DIR

# 10. Create Systemd Service
log "🔧 Creating systemd service..."
cat > /etc/systemd/system/crypto-trading.service << EOF
[Unit]
Description=Cryptocurrency Trading API
After=network.target postgresql.service redis.service

[Service]
Type=exec
User=crypto-app
Group=crypto-app
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/venv/bin
EnvironmentFile=$APP_DIR/.env
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

# 11. Update Gunicorn Config for Production
log "⚡ Optimizing Gunicorn configuration..."
cat > gunicorn.conf.py << EOF
# Production Gunicorn Configuration
import multiprocessing
import os

# Server socket
bind = "127.0.0.1:5000"
backlog = 2048

# Worker processes
workers = min(4, (multiprocessing.cpu_count() * 2) + 1)
worker_class = "sync"
worker_connections = 1000
timeout = 120
keepalive = 2

# Restart workers
max_requests = 2000
max_requests_jitter = 100

# Logging
loglevel = "info"
accesslog = "$APP_DIR/logs/access.log"
errorlog = "$APP_DIR/logs/error.log"
access_log_format = '%({x-forwarded-for}i)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(O)s "%(f)s" "%(a)s"'

# Process naming
proc_name = "crypto-trading-api"

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Performance
preload_app = True
EOF

# Create logs directory
mkdir -p $APP_DIR/logs
chown -R crypto-app:crypto-app $APP_DIR/logs

# 12. Setup Nginx
log "🌐 Configuring Nginx..."
cat > /etc/nginx/sites-available/$APP_NAME << EOF
# Rate limiting
limit_req_zone \$binary_remote_addr zone=api:10m rate=10r/s;
limit_req_zone \$binary_remote_addr zone=login:10m rate=5r/m;

server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;
    
    # Security headers
    add_header X-Content-Type-Options nosniff always;
    add_header X-Frame-Options DENY always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';" always;
    
    # Hide server version
    server_tokens off;
    
    # Gzip compression
    gzip on;
    gzip_comp_level 6;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
    
    # Main application
    location / {
        limit_req zone=api burst=20 nodelay;
        
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Timeout settings
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # Buffer settings
        proxy_buffering on;
        proxy_buffer_size 128k;
        proxy_buffers 4 256k;
        proxy_busy_buffers_size 256k;
    }
    
    # Health check (no rate limiting)
    location /health {
        proxy_pass http://127.0.0.1:5000/health;
        access_log off;
    }
    
    # API endpoints with stricter rate limiting
    location /api/ {
        limit_req zone=api burst=10 nodelay;
        
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # Static files (if any)
    location /static {
        root $APP_DIR;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Deny access to sensitive files
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }
    
    location ~ \.(ini|log|conf)$ {
        deny all;
        access_log off;
        log_not_found off;
    }
}
EOF

# Enable site
ln -sf /etc/nginx/sites-available/$APP_NAME /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t

# 13. Initialize Database
log "🗃️ Initializing database..."
cd $APP_DIR
source venv/bin/activate
python -c "
from main import create_app
from models import db

app = create_app()
with app.app_context():
    db.create_all()
    print('Database initialized successfully')
"

# 14. Start Services
log "🚀 Starting services..."
systemctl daemon-reload
systemctl enable crypto-trading
systemctl start crypto-trading
systemctl reload nginx

# 15. Setup SSL Certificate
log "🔒 Setting up SSL certificate..."
certbot --nginx -d $DOMAIN -d www.$DOMAIN --non-interactive --agree-tos --email $ADMIN_EMAIL

# 16. Create Monitoring & Auto-Deploy Scripts
log "📊 Setting up monitoring..."
cat > /usr/local/bin/crypto-monitor.sh << 'EOF'
#!/bin/bash
SERVICE="crypto-trading"
APP_URL="http://localhost:5000/health"

# Check service status
if ! systemctl is-active --quiet $SERVICE; then
    echo "$(date): Service $SERVICE is down, restarting..."
    systemctl restart $SERVICE
    sleep 10
fi

# Check application health
if ! curl -sf $APP_URL > /dev/null; then
    echo "$(date): Health check failed, restarting service..."
    systemctl restart $SERVICE
fi
EOF

chmod +x /usr/local/bin/crypto-monitor.sh

# Add to crontab
(crontab -l 2>/dev/null; echo "*/5 * * * * /usr/local/bin/crypto-monitor.sh >> /var/log/crypto-monitor.log 2>&1") | crontab -

# 17. Create Auto-Deploy Script
cat > $APP_DIR/deploy.sh << 'EOF'
#!/bin/bash
cd /var/www/crypto-trading-api
git pull origin main
source venv/bin/activate
pip install -r requirements-prod.txt
sudo systemctl restart crypto-trading
sleep 5
curl -f http://localhost:5000/health && echo "Deployment successful!"
EOF

chmod +x $APP_DIR/deploy.sh
chown crypto-app:crypto-app $APP_DIR/deploy.sh

# 18. Final Status Check
log "✅ Performing final health check..."
sleep 10

if systemctl is-active --quiet crypto-trading; then
    log "✅ Service is running"
else
    error "❌ Service failed to start"
fi

if curl -sf http://localhost:5000/health > /dev/null; then
    log "✅ Application is responding"
else
    warn "⚠️ Application health check failed"
fi

# 19. Display Summary
log "🎉 VPS Setup Complete!"
echo
info "=== SETUP SUMMARY ==="
info "Domain: https://$DOMAIN"
info "Application: $APP_DIR"
info "Database: $DB_NAME (user: $DB_USER)"
info "Logs: $APP_DIR/logs/"
info "Service: crypto-trading"
echo
warn "=== NEXT STEPS ==="
warn "1. Update API keys in $APP_DIR/.env"
warn "2. Configure GitHub Actions secrets:"
warn "   - VPS_HOST: your-vps-ip"
warn "   - VPS_USER: root"
warn "   - VPS_SSH_KEY: your-private-ssh-key"
warn "   - VPS_PORT: 22"
warn "3. Test deployment: git push origin main"
echo
info "=== USEFUL COMMANDS ==="
info "Check status: systemctl status crypto-trading"
info "View logs: journalctl -u crypto-trading -f"
info "Manual deploy: $APP_DIR/deploy.sh"
info "Monitor: tail -f /var/log/crypto-monitor.log"
echo
log "🚀 Your Cryptocurrency Trading Platform is ready!"