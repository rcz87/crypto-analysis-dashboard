#!/bin/bash
# Setup CI/CD Pipeline untuk Auto Deployment
# Membuat webhook handler untuk auto deploy saat git push

set -e

APP_DIR="/var/www/crypto-trading-api"
WEBHOOK_PORT="9000"
SECRET_TOKEN="your-webhook-secret-here"

# Install webhook handler
install_webhook() {
    echo "Installing webhook handler..."
    
    # Install webhook binary
    if ! command -v webhook &> /dev/null; then
        apt update
        apt install -y webhook
    fi
    
    # Create webhook configuration
    cat > /etc/webhook.conf << EOF
[
  {
    "id": "crypto-trading-deploy",
    "execute-command": "$APP_DIR/vps-auto-deploy.sh",
    "command-working-directory": "$APP_DIR",
    "pass-arguments-to-command": [
      {
        "source": "payload",
        "name": "head_commit.message"
      }
    ],
    "trigger-rule": {
      "and": [
        {
          "match": {
            "type": "payload-hash-sha1",
            "secret": "$SECRET_TOKEN",
            "parameter": {
              "source": "header",
              "name": "X-Hub-Signature"
            }
          }
        },
        {
          "match": {
            "type": "value",
            "value": "refs/heads/main",
            "parameter": {
              "source": "payload",
              "name": "ref"
            }
          }
        }
      ]
    }
  }
]
EOF

    echo "Webhook configuration created"
}

# Setup systemd service for webhook
setup_webhook_service() {
    echo "Setting up webhook service..."
    
    cat > /etc/systemd/system/webhook.service << EOF
[Unit]
Description=GitHub Webhook Handler
After=network.target

[Service]
Type=simple
User=root
ExecStart=/usr/bin/webhook -hooks /etc/webhook.conf -port $WEBHOOK_PORT -verbose
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    systemctl enable webhook
    systemctl start webhook
    
    echo "Webhook service started on port $WEBHOOK_PORT"
}

# Setup nginx proxy for webhook
setup_webhook_nginx() {
    echo "Setting up Nginx proxy for webhook..."
    
    cat > /etc/nginx/sites-available/webhook << EOF
server {
    listen 80;
    server_name webhook.your-domain.com;
    
    location /hooks/ {
        proxy_pass http://127.0.0.1:$WEBHOOK_PORT/hooks/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

    ln -sf /etc/nginx/sites-available/webhook /etc/nginx/sites-enabled/
    nginx -t && systemctl reload nginx
    
    echo "Webhook nginx proxy configured"
}

# Create monitoring script
create_monitoring() {
    echo "Creating monitoring script..."
    
    cat > /usr/local/bin/monitor-crypto-app.sh << 'EOF'
#!/bin/bash
# Monitor cryptocurrency trading application

SERVICE_NAME="crypto-trading"
WEBHOOK_URL="YOUR_DISCORD_OR_SLACK_WEBHOOK_URL"

# Check if service is running
if ! systemctl is-active --quiet $SERVICE_NAME; then
    echo "Service $SERVICE_NAME is down, attempting restart..."
    systemctl restart $SERVICE_NAME
    
    # Send alert
    curl -X POST "$WEBHOOK_URL" \
        -H "Content-Type: application/json" \
        -d "{\"content\": \"🚨 Crypto Trading API was down and has been restarted at $(date)\"}"
fi

# Check application health
if ! curl -f -s http://localhost:5000/health > /dev/null; then
    echo "Health check failed for Crypto Trading API"
    
    # Send alert
    curl -X POST "$WEBHOOK_URL" \
        -H "Content-Type: application/json" \
        -d "{\"content\": \"❌ Crypto Trading API health check failed at $(date)\"}"
fi
EOF

    chmod +x /usr/local/bin/monitor-crypto-app.sh
    
    # Add to crontab (check every 5 minutes)
    (crontab -l 2>/dev/null; echo "*/5 * * * * /usr/local/bin/monitor-crypto-app.sh") | crontab -
    
    echo "Monitoring script installed"
}

echo "=== Setting up CI/CD Pipeline ==="
echo "1. Installing webhook handler..."
install_webhook

echo "2. Setting up webhook service..."
setup_webhook_service

echo "3. Configuring nginx proxy..."
setup_webhook_nginx

echo "4. Setting up monitoring..."
create_monitoring

echo ""
echo "=== CI/CD Setup Complete ==="
echo ""
echo "Next steps:"
echo "1. Update SECRET_TOKEN in /etc/webhook.conf with your actual webhook secret"
echo "2. Add webhook URL to your GitHub repository:"
echo "   URL: http://webhook.your-domain.com/hooks/crypto-trading-deploy"
echo "   Secret: $SECRET_TOKEN"
echo "   Events: Just push events"
echo ""
echo "3. Update monitoring webhook URL in /usr/local/bin/monitor-crypto-app.sh"
echo ""
echo "Now your application will auto-deploy when you push to main branch!"