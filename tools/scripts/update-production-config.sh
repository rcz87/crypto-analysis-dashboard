#!/bin/bash
# Update Production Configuration untuk domain gpts.guardiansofthetoken.id

set -e

DOMAIN="gpts.guardiansofthetoken.id" 
APP_NAME="crypto-trading-api"
APP_DIR="/var/www/$APP_NAME"

echo "🔧 Updating configuration for production domain: $DOMAIN"

# Update .env file with correct domain
cat >> $APP_DIR/.env << EOF

# Production Domain Configuration  
PRODUCTION_DOMAIN=$DOMAIN
ALLOWED_HOSTS=$DOMAIN,www.$DOMAIN
CORS_ORIGINS=https://$DOMAIN,https://www.$DOMAIN,https://chat.openai.com

# API Configuration
API_BASE_URL=https://$DOMAIN/api/gpts/
WEBHOOK_URL=https://$DOMAIN/webhook/

EOF

# Update Nginx configuration for better GPTs integration
cat > /etc/nginx/sites-available/$APP_NAME << EOF
# Rate limiting zones
limit_req_zone \$binary_remote_addr zone=api:10m rate=20r/s;
limit_req_zone \$binary_remote_addr zone=gpts:10m rate=50r/s;

server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name $DOMAIN www.$DOMAIN;
    
    # SSL Configuration (Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
    ssl_session_timeout 1d;
    ssl_session_cache shared:MozTLS:10m;
    ssl_session_tickets off;
    
    # Modern SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    # Security headers optimized for GPTs
    add_header X-Content-Type-Options nosniff always;
    add_header X-Frame-Options SAMEORIGIN always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Strict-Transport-Security "max-age=63072000" always;
    
    # CORS headers for ChatGPT
    add_header Access-Control-Allow-Origin "https://chat.openai.com" always;
    add_header Access-Control-Allow-Methods "GET, POST, OPTIONS" always;
    add_header Access-Control-Allow-Headers "Content-Type, Authorization, X-Requested-With" always;
    add_header Access-Control-Allow-Credentials "true" always;
    
    # Handle preflight requests
    if (\$request_method = 'OPTIONS') {
        add_header Access-Control-Allow-Origin "https://chat.openai.com" always;
        add_header Access-Control-Allow-Methods "GET, POST, OPTIONS" always;
        add_header Access-Control-Allow-Headers "Content-Type, Authorization, X-Requested-With" always;
        add_header Access-Control-Max-Age 86400 always;
        add_header Content-Length 0 always;
        add_header Content-Type "text/plain" always;
        return 204;
    }
    
    # Compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_comp_level 6;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
    
    # Root redirect to API documentation
    location = / {
        proxy_pass http://127.0.0.1:5000/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # GPTs API endpoints - Higher rate limit for ChatGPT
    location /api/gpts/ {
        limit_req zone=gpts burst=100 nodelay;
        
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Timeout settings for AI processing
        proxy_connect_timeout 60s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
        
        # Buffer settings for large responses
        proxy_buffering on;
        proxy_buffer_size 128k;
        proxy_buffers 4 256k;
        proxy_busy_buffers_size 256k;
    }
    
    # Health check endpoint (no rate limiting)
    location /health {
        proxy_pass http://127.0.0.1:5000/health;
        access_log off;
    }
    
    # API documentation
    location /docs {
        proxy_pass http://127.0.0.1:5000/docs;
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
        access_log off;
    }
    
    # Security: Deny access to sensitive files
    location ~ /\.(env|git|svn) {
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

# Test nginx configuration
nginx -t

# Reload nginx
systemctl reload nginx

# Update systemd service for better production settings
cat > /etc/systemd/system/crypto-trading.service << EOF
[Unit]
Description=Cryptocurrency Trading GPTs API
After=network.target postgresql.service redis.service
Wants=postgresql.service redis.service

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
TimeoutStopSec=10
PrivateTmp=true
Restart=always
RestartSec=5
StartLimitInterval=60
StartLimitBurst=3

# Resource limits
LimitNOFILE=65536
LimitNPROC=4096

# Security settings
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$APP_DIR

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and restart service
systemctl daemon-reload
systemctl restart crypto-trading

echo "✅ Production configuration updated for $DOMAIN"
echo "🔍 Checking service status..."
systemctl status crypto-trading --no-pager -l

echo "🌐 Testing endpoints..."
sleep 5
curl -s https://$DOMAIN/health | python3 -m json.tool || echo "Health check failed"
curl -s https://$DOMAIN/api/gpts/status | python3 -m json.tool || echo "Status endpoint failed"

echo "✅ Configuration update complete!"