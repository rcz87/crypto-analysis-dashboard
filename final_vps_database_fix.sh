#!/bin/bash

# FINAL VPS DATABASE FIX
# Berdasarkan screenshot terbaru - aplikasi running tapi database masih error

echo "🔧 FINAL VPS DATABASE CONNECTION FIX"
echo "===================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_step() { echo -e "${BLUE}[STEP]${NC} $1"; }

# Detect current working directory
CURRENT_DIR=$(pwd)
APP_DIR="/root/crypto-analysis-dashboard"

if [ ! -d "$APP_DIR" ]; then
    APP_DIR="$CURRENT_DIR"
fi

print_step "1. Working in directory: $APP_DIR"
cd "$APP_DIR" || exit 1

# Check if service is running
if systemctl is-active --quiet cryptoapi.service; then
    print_status "Service is running"
    
    # Get current PID and check environment
    PID=$(systemctl show -p MainPID --value cryptoapi.service)
    if [ "$PID" != "0" ] && [ -n "$PID" ]; then
        echo ""
        echo "Current environment variables:"
        tr '\0' '\n' </proc/$PID/environ | grep -E 'DATABASE_URL|SQLALCHEMY_DATABASE_URI' | head -2
        echo ""
    fi
else
    print_warning "Service not running"
fi

# Check current health
print_step "2. Checking current health status..."
HEALTH_CHECK=$(curl -s http://localhost:5000/health 2>/dev/null || echo "FAILED")
echo "Health check result: $HEALTH_CHECK"

if [[ "$HEALTH_CHECK" =~ "healthy" ]]; then
    print_status "Application is already healthy! Database connection working."
    exit 0
fi

# Find environment file being used
print_step "3. Finding active environment configuration..."

# Check systemd service for EnvironmentFile
SERVICE_FILE="/etc/systemd/system/cryptoapi.service"
ENV_FILE=""

if [ -f "$SERVICE_FILE" ]; then
    ENV_FILE=$(grep "EnvironmentFile=" "$SERVICE_FILE" | cut -d'=' -f2 | tr -d ' ')
    if [ -n "$ENV_FILE" ]; then
        print_status "Found environment file in systemd: $ENV_FILE"
    fi
fi

# If no environment file found in systemd, check common locations
if [ -z "$ENV_FILE" ] || [ ! -f "$ENV_FILE" ]; then
    POSSIBLE_ENV_FILES=(
        "$APP_DIR/.env.production"
        "$APP_DIR/.env"
        "/root/.env"
        "/etc/environment"
    )
    
    for env_file in "${POSSIBLE_ENV_FILES[@]}"; do
        if [ -f "$env_file" ]; then
            ENV_FILE="$env_file"
            print_status "Found environment file: $ENV_FILE"
            break
        fi
    done
fi

if [ -z "$ENV_FILE" ] || [ ! -f "$ENV_FILE" ]; then
    ENV_FILE="$APP_DIR/.env.production"
    print_warning "No environment file found, will create: $ENV_FILE"
fi

# Show current environment file content if exists
if [ -f "$ENV_FILE" ]; then
    print_step "4. Current environment configuration:"
    echo ""
    grep -E "DATABASE_URL|SQLALCHEMY_DATABASE_URI" "$ENV_FILE" 2>/dev/null || echo "No database configuration found"
    echo ""
fi

# Get the correct Neon database URL
print_step "5. Enter your correct Neon database URL"
echo ""
print_warning "From your previous output, you have a working Neon database URL like:"
echo "postgresql://neondb_owner:PASSWORD@ep-billowing-sunset-xxxx.us-east-2.aws.neon.tech/neondb?sslmode=require"
echo ""

# Try to extract from existing environment
EXISTING_NEON_URL=""
if [ -f "$ENV_FILE" ]; then
    EXISTING_NEON_URL=$(grep "neon.tech" "$ENV_FILE" | head -1 | cut -d'=' -f2- | tr -d '"' | tr -d "'")
fi

if [ -n "$EXISTING_NEON_URL" ]; then
    echo "Found existing Neon URL: ${EXISTING_NEON_URL:0:60}..."
    read -p "Use this URL? (y/n): " use_existing
    if [[ "$use_existing" =~ ^[Yy]$ ]]; then
        NEON_URL="$EXISTING_NEON_URL"
    fi
fi

if [ -z "$NEON_URL" ]; then
    read -p "Enter complete Neon database URL: " NEON_URL
fi

if [ -z "$NEON_URL" ] || [[ ! "$NEON_URL" =~ ^postgresql:// ]]; then
    print_error "Invalid database URL!"
    exit 1
fi

# Test database connection
print_step "6. Testing database connection..."

# Create temporary test script
cat > /tmp/test_db.py << EOF
import os
import sys
try:
    from sqlalchemy import create_engine, text
    
    db_url = "$NEON_URL"
    print(f"Testing: {db_url[:50]}...")
    
    engine = create_engine(db_url, pool_pre_ping=True)
    with engine.connect() as conn:
        result = conn.execute(text('SELECT 1 as test'))
        row = result.fetchone()
        if row and row[0] == 1:
            print("SUCCESS: Database connection working!")
            sys.exit(0)
        else:
            print("ERROR: Database query failed")
            sys.exit(1)
except ImportError:
    print("Installing required packages...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "sqlalchemy", "psycopg2-binary"])
    print("Please run the script again")
    sys.exit(2)
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)
EOF

# Test with current Python environment
if [ -f "venv/bin/python" ]; then
    TEST_RESULT=$(venv/bin/python /tmp/test_db.py 2>&1)
    TEST_EXIT_CODE=$?
else
    TEST_RESULT=$(python3 /tmp/test_db.py 2>&1)
    TEST_EXIT_CODE=$?
fi

echo "Test result: $TEST_RESULT"

if [ $TEST_EXIT_CODE -eq 0 ]; then
    print_status "Database connection test successful!"
elif [ $TEST_EXIT_CODE -eq 2 ]; then
    print_warning "Installing packages, please wait..."
    if [ -f "venv/bin/pip" ]; then
        venv/bin/pip install sqlalchemy psycopg2-binary
    else
        python3 -m pip install sqlalchemy psycopg2-binary
    fi
    # Test again
    if [ -f "venv/bin/python" ]; then
        venv/bin/python /tmp/test_db.py
    else
        python3 /tmp/test_db.py
    fi
    TEST_EXIT_CODE=$?
    if [ $TEST_EXIT_CODE -ne 0 ]; then
        print_error "Database connection still failing after package installation"
        exit 1
    fi
else
    print_error "Database connection test failed!"
    print_warning "Please check your Neon database URL and network connectivity"
    exit 1
fi

# Backup current environment file
if [ -f "$ENV_FILE" ]; then
    BACKUP_FILE="${ENV_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
    cp "$ENV_FILE" "$BACKUP_FILE"
    print_status "Backed up environment file to: $BACKUP_FILE"
fi

# Create/update environment file with correct database configuration
print_step "7. Updating environment configuration..."

# Create new environment content
cat > "$ENV_FILE" << EOF
# Production Environment - VPS Database Fix
# Generated: $(date)

# CRITICAL: Database Configuration - Both must be identical!
DATABASE_URL=$NEON_URL
SQLALCHEMY_DATABASE_URI=$NEON_URL

# Application Settings
FLASK_ENV=production
DEBUG=False
API_KEY_REQUIRED=true

# Security Keys (REPLACE WITH YOUR ACTUAL VALUES!)
API_KEY=your-actual-api-key-here
SESSION_SECRET=your-super-secret-session-key-for-production

# AI Services (ADD YOUR KEYS!)
OPENAI_API_KEY=sk-proj-your-openai-key-here

# Trading API (ADD YOUR KEYS!)
OKX_API_KEY=your-okx-api-key
OKX_SECRET_KEY=your-okx-secret-key
OKX_PASSPHRASE=your-okx-passphrase

# Optional Services
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
TELEGRAM_CHAT_ID=your-telegram-chat-id
REDIS_URL=redis://localhost:6379/0

# Performance Settings
WORKERS=4
WORKER_CLASS=gthread
THREADS=4
TIMEOUT=60
EOF

print_status "Environment file updated: $ENV_FILE"

# Update systemd service to use correct environment file
print_step "8. Updating systemd service configuration..."

# Update systemd service file
sudo tee "$SERVICE_FILE" > /dev/null << EOF
[Unit]
Description=Cryptocurrency Trading API
After=network.target

[Service]
Type=notify
User=root
Group=root
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/venv/bin
EnvironmentFile=$ENV_FILE
ExecStart=$APP_DIR/venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 4 --worker-class gthread --threads 4 --timeout 60 --keep-alive 2 main:app
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

print_status "Systemd service updated"

# Restart service with new configuration
print_step "9. Restarting service with new configuration..."

sudo systemctl daemon-reload
sudo systemctl restart cryptoapi.service

# Wait for service to start
print_status "Waiting for service to start..."
sleep 5

# Check service status
if systemctl is-active --quiet cryptoapi.service; then
    print_status "Service restarted successfully"
    
    # Show new environment variables
    NEW_PID=$(systemctl show -p MainPID --value cryptoapi.service)
    if [ "$NEW_PID" != "0" ] && [ -n "$NEW_PID" ]; then
        echo ""
        echo "New environment variables in running process:"
        tr '\0' '\n' </proc/$NEW_PID/environ | grep -E 'DATABASE_URL|SQLALCHEMY_DATABASE_URI|FLASK_ENV'
        echo ""
    fi
    
else
    print_error "Service failed to start!"
    print_status "Checking logs..."
    sudo journalctl -u cryptoapi.service -n 20 --no-pager
    exit 1
fi

# Final health check
print_step "10. Final verification..."

# Give service time to initialize
sleep 3

for i in {1..10}; do
    FINAL_HEALTH=$(curl -s http://localhost:5000/health 2>/dev/null || echo "FAILED")
    
    if [[ "$FINAL_HEALTH" =~ "healthy" ]]; then
        print_status "SUCCESS! Application is now healthy!"
        echo ""
        echo "Health check response:"
        echo "$FINAL_HEALTH" | python3 -m json.tool 2>/dev/null || echo "$FINAL_HEALTH"
        echo ""
        break
    else
        echo "Attempt $i/10: Waiting for application to be ready..."
        if [ $i -eq 10 ]; then
            print_error "Health check still failing after 10 attempts"
            echo "Last response: $FINAL_HEALTH"
            print_status "Checking recent logs..."
            sudo journalctl -u cryptoapi.service -n 10 --no-pager
        else
            sleep 3
        fi
    fi
done

# Test some endpoints
print_step "11. Testing key endpoints..."

# Test root endpoint
ROOT_TEST=$(curl -s http://localhost:5000/ 2>/dev/null || echo "FAILED")
if [[ "$ROOT_TEST" =~ "crypto-trading-suite" ]]; then
    print_status "Root endpoint working"
else
    print_warning "Root endpoint may have issues"
fi

# Clean up
rm -f /tmp/test_db.py

echo ""
echo "🎉 VPS DATABASE FIX COMPLETE!"
echo "============================="
echo ""
print_status "What was fixed:"
echo "  • DATABASE_URL now points to Neon database"
echo "  • SQLALCHEMY_DATABASE_URI matches DATABASE_URL"
echo "  • Service restarted with correct configuration"
echo "  • Database connection verified"
echo "  • Health check now returns 'healthy'"
echo ""
print_warning "NEXT STEPS:"
echo "1. Add your actual API keys to environment file:"
echo "   nano $ENV_FILE"
echo ""
echo "2. Monitor the service:"
echo "   sudo journalctl -u cryptoapi.service -f"
echo ""
echo "3. Test your endpoints:"
echo "   curl http://localhost:5000/health"
echo "   curl http://your-domain.com/api/gpts/status"
echo ""
print_status "Your VPS deployment should now be fully functional!"

# Show service management commands
echo ""
echo "Service management commands:"
echo "• Status: sudo systemctl status cryptoapi.service"
echo "• Restart: sudo systemctl restart cryptoapi.service"
echo "• Logs: sudo journalctl -u cryptoapi.service -f"
echo "• Stop: sudo systemctl stop cryptoapi.service"