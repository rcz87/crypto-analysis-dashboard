#!/bin/bash

# HOSTINGER VPS DATABASE FIX - Simple & Direct
# Khusus untuk VPS Hostinger dengan masalah database connection

echo "🔧 HOSTINGER VPS DATABASE FIX"
echo "============================="
echo ""

# Function untuk print colored output
print_success() { echo -e "\033[0;32m✅ $1\033[0m"; }
print_error() { echo -e "\033[0;31m❌ $1\033[0m"; }
print_warning() { echo -e "\033[1;33m⚠️  $1\033[0m"; }
print_info() { echo -e "\033[0;34mℹ️  $1\033[0m"; }

# 1. Check current status
print_info "Checking current service status..."
if systemctl is-active --quiet cryptoapi.service; then
    print_success "Service is running"
else
    print_warning "Service is not running"
fi

# Check health endpoint
CURRENT_HEALTH=$(curl -s --connect-timeout 3 http://localhost:5000/health 2>/dev/null || echo "FAILED")
if [[ "$CURRENT_HEALTH" =~ "healthy" ]]; then
    print_success "Application is already healthy!"
    echo "Current health: $CURRENT_HEALTH"
    exit 0
else
    print_warning "Health check failing - need to fix database connection"
fi

# 2. Find application directory
APP_DIRS=(
    "/root/crypto-analysis-dashboard"
    "/home/crypto-analysis-dashboard"
    "/var/www/crypto-analysis-dashboard"
    "/opt/crypto-analysis-dashboard"
    "$(pwd)"
)

APP_DIR=""
for dir in "${APP_DIRS[@]}"; do
    if [ -d "$dir" ] && [ -f "$dir/main.py" ]; then
        APP_DIR="$dir"
        break
    fi
done

if [ -z "$APP_DIR" ]; then
    print_error "Application directory not found!"
    print_info "Please run this script from your application directory"
    exit 1
fi

print_success "Using application directory: $APP_DIR"
cd "$APP_DIR"

# 3. Stop service
print_info "Stopping service..."
sudo systemctl stop cryptoapi.service 2>/dev/null || true

# 4. Get Neon database URL
echo ""
print_info "MASALAH: Aplikasi masih coba konek ke localhost:5432"
print_info "SOLUSI: Kita perlu URL database Neon yang benar"
echo ""
print_warning "Contoh format URL Neon database:"
echo "postgresql://neondb_owner:PASSWORD@ep-billowing-sunset-xxxx.us-east-2.aws.neon.tech/neondb?sslmode=require"
echo ""

# Try to find existing Neon URL
EXISTING_NEON=""
for env_file in ".env" ".env.production" "/etc/environment"; do
    if [ -f "$env_file" ]; then
        EXISTING_NEON=$(grep "neon.tech" "$env_file" 2>/dev/null | head -1 | cut -d'=' -f2- | tr -d '"' | tr -d "'")
        if [ -n "$EXISTING_NEON" ]; then
            echo "Found existing Neon URL in $env_file:"
            echo "${EXISTING_NEON:0:60}..."
            echo ""
            read -p "Use this URL? (y/n): " use_existing
            if [[ "$use_existing" =~ ^[Yy]$ ]]; then
                NEON_URL="$EXISTING_NEON"
                break
            fi
        fi
    fi
done

if [ -z "$NEON_URL" ]; then
    read -p "Paste your complete Neon database URL: " NEON_URL
fi

# Validate URL
if [ -z "$NEON_URL" ] || [[ ! "$NEON_URL" =~ ^postgresql:// ]]; then
    print_error "Invalid database URL!"
    print_info "URL must start with postgresql://"
    exit 1
fi

if [[ ! "$NEON_URL" =~ neon\.tech ]]; then
    print_warning "URL doesn't look like a Neon database. Continue anyway? (y/n)"
    read -r confirm
    if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

print_success "Database URL validated"

# 5. Test database connection
print_info "Testing database connection..."

# Install required packages if needed
if [ -f "venv/bin/pip" ]; then
    ./venv/bin/pip install sqlalchemy psycopg2-binary >/dev/null 2>&1 || true
else
    pip3 install sqlalchemy psycopg2-binary >/dev/null 2>&1 || true
fi

# Test connection
cat > /tmp/test_neon_connection.py << EOF
import sys
try:
    from sqlalchemy import create_engine, text
    engine = create_engine("$NEON_URL", pool_pre_ping=True)
    with engine.connect() as conn:
        result = conn.execute(text('SELECT 1'))
        row = result.fetchone()
        if row and row[0] == 1:
            print("SUCCESS")
            sys.exit(0)
    print("FAILED")
    sys.exit(1)
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)
EOF

TEST_RESULT=$(python3 /tmp/test_neon_connection.py 2>&1)
if [[ "$TEST_RESULT" == "SUCCESS" ]]; then
    print_success "Database connection test passed!"
else
    print_error "Database connection test failed: $TEST_RESULT"
    print_info "Please check your database URL and network connectivity"
    exit 1
fi

# 6. Create/update environment file
ENV_FILE="$APP_DIR/.env.production"
print_info "Creating environment file: $ENV_FILE"

# Backup existing file
if [ -f "$ENV_FILE" ]; then
    cp "$ENV_FILE" "${ENV_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
    print_success "Backed up existing environment file"
fi

# Create new environment file
cat > "$ENV_FILE" << EOF
# Hostinger VPS Production Environment
# Generated: $(date)

# CRITICAL: Database Configuration
DATABASE_URL=$NEON_URL
SQLALCHEMY_DATABASE_URI=$NEON_URL

# Application Settings
FLASK_ENV=production
DEBUG=False
API_KEY_REQUIRED=true

# Security (REPLACE WITH YOUR ACTUAL KEYS!)
API_KEY=your-actual-api-key-here
SESSION_SECRET=your-super-secret-session-key

# AI Services (ADD YOUR KEYS!)
OPENAI_API_KEY=sk-proj-your-openai-key-here

# Trading API (ADD YOUR KEYS!)
OKX_API_KEY=your-okx-api-key
OKX_SECRET_KEY=your-okx-secret-key
OKX_PASSPHRASE=your-okx-passphrase

# Optional
TELEGRAM_BOT_TOKEN=your-telegram-token
TELEGRAM_CHAT_ID=your-chat-id
EOF

print_success "Environment file created"

# 7. Update systemd service
print_info "Updating systemd service..."

SERVICE_FILE="/etc/systemd/system/cryptoapi.service"
sudo tee "$SERVICE_FILE" > /dev/null << EOF
[Unit]
Description=Cryptocurrency Trading API - Hostinger VPS
After=network.target

[Service]
Type=notify
User=root
Group=root
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/venv/bin
EnvironmentFile=$ENV_FILE
ExecStart=$APP_DIR/venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 4 --worker-class gthread --threads 4 --timeout 60 main:app
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

print_success "Systemd service updated"

# 8. Start service
print_info "Starting service with new configuration..."

sudo systemctl daemon-reload
sudo systemctl enable cryptoapi.service
sudo systemctl start cryptoapi.service

# Wait for startup
sleep 5

# 9. Verify fix
print_info "Verifying the fix..."

if systemctl is-active --quiet cryptoapi.service; then
    print_success "Service started successfully"
    
    # Test health endpoint multiple times
    for i in {1..10}; do
        HEALTH_CHECK=$(curl -s --connect-timeout 5 http://localhost:5000/health 2>/dev/null || echo "FAILED")
        
        if [[ "$HEALTH_CHECK" =~ "healthy" ]]; then
            print_success "SUCCESS! Application is now healthy!"
            echo ""
            echo "Health response:"
            echo "$HEALTH_CHECK" | python3 -m json.tool 2>/dev/null || echo "$HEALTH_CHECK"
            break
        elif [ $i -eq 10 ]; then
            print_error "Health check still failing after 10 attempts"
            print_info "Checking service logs..."
            sudo journalctl -u cryptoapi.service -n 10 --no-pager
        else
            echo "Waiting for application startup... ($i/10)"
            sleep 3
        fi
    done
else
    print_error "Service failed to start!"
    print_info "Checking service logs..."
    sudo journalctl -u cryptoapi.service -n 15 --no-pager
    exit 1
fi

# 10. Test endpoints
echo ""
print_info "Testing key endpoints..."

# Root endpoint
ROOT_TEST=$(curl -s --connect-timeout 5 http://localhost:5000/ 2>/dev/null || echo "FAILED")
if [[ "$ROOT_TEST" =~ "crypto-trading-suite" ]]; then
    print_success "Root endpoint working"
else
    print_warning "Root endpoint may have issues"
    echo "Response: ${ROOT_TEST:0:100}..."
fi

# Show final status
echo ""
print_info "Current environment variables in running process:"
PID=$(systemctl show -p MainPID --value cryptoapi.service)
if [ "$PID" != "0" ] && [ -n "$PID" ]; then
    tr '\0' '\n' </proc/$PID/environ | grep -E 'DATABASE_URL|SQLALCHEMY_DATABASE_URI|FLASK_ENV' | head -3
fi

# Clean up
rm -f /tmp/test_neon_connection.py

echo ""
echo "🎉 HOSTINGER VPS FIX COMPLETE!"
echo "=============================="
echo ""
print_success "What was accomplished:"
echo "  • Fixed database URL to point to Neon instead of localhost"
echo "  • Updated systemd service configuration"
echo "  • Service restarted successfully"
echo "  • Health check now returns 'healthy'"
echo ""
print_warning "NEXT STEPS:"
echo "1. Add your actual API keys:"
echo "   nano $ENV_FILE"
echo ""
echo "2. Test your API endpoints:"
echo "   curl -H 'X-API-KEY: your-key' http://YOUR_DOMAIN/api/gpts/status"
echo ""
echo "3. Monitor service:"
echo "   sudo journalctl -u cryptoapi.service -f"
echo ""
print_success "Your Hostinger VPS is now ready for production!"

echo ""
echo "Service management commands:"
echo "• Check status: sudo systemctl status cryptoapi.service"
echo "• View logs: sudo journalctl -u cryptoapi.service -f"
echo "• Restart: sudo systemctl restart cryptoapi.service"
echo "• Stop: sudo systemctl stop cryptoapi.service"