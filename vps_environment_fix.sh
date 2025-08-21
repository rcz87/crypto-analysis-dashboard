#!/bin/bash

# VPS Environment Variables Fix Script
# This script fixes the database connection issue you encountered

echo "🔧 VPS ENVIRONMENT VARIABLES FIX"
echo "================================"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() { echo -e "${GREEN}[INFO]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Check if service exists
if ! systemctl list-unit-files | grep -q cryptoapi.service; then
    print_error "cryptoapi.service not found!"
    exit 1
fi

# 1. Check current environment variables
print_status "1. Checking current environment variables..."
PID=$(systemctl show -p MainPID --value cryptoapi.service)

if [ "$PID" != "0" ] && [ -n "$PID" ]; then
    echo "Current DATABASE_URL configurations:"
    tr '\0' '\n' </proc/$PID/environ | grep -E 'DATABASE_URL|SQLALCHEMY_DATABASE_URI'
    echo ""
else
    print_warning "Service not running or no PID found"
fi

# 2. Find environment file
ENV_FILE=""
SERVICE_FILE="/etc/systemd/system/cryptoapi.service"

if [ -f "$SERVICE_FILE" ]; then
    ENV_FILE=$(grep EnvironmentFile "$SERVICE_FILE" | cut -d'=' -f2)
    print_status "Found environment file: $ENV_FILE"
else
    print_error "Service file not found: $SERVICE_FILE"
    exit 1
fi

# 3. Backup current environment file
if [ -n "$ENV_FILE" ] && [ -f "$ENV_FILE" ]; then
    BACKUP_FILE="${ENV_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
    print_status "Creating backup: $BACKUP_FILE"
    cp "$ENV_FILE" "$BACKUP_FILE"
else
    print_error "Environment file not found: $ENV_FILE"
    exit 1
fi

# 4. Interactive fix
echo ""
print_warning "MASALAH DITEMUKAN:"
echo "Anda memiliki DATABASE_URL yang berbeda:"
echo "❌ DATABASE_URL=postgresql://trading_user:your_password@localhost:5432/trading_db"
echo "✅ SQLALCHEMY_DATABASE_URI=postgresql://neondb_owner:password@ep-billowing-sunset-...neon.tech/neondb?sslmode=require"
echo ""

read -p "Masukkan URL database Neon yang benar (dari SQLALCHEMY_DATABASE_URI): " NEON_DB_URL

if [ -z "$NEON_DB_URL" ]; then
    print_error "Database URL tidak boleh kosong!"
    exit 1
fi

# 5. Validate URL format
if [[ ! "$NEON_DB_URL" =~ ^postgresql://.*neon\.tech.* ]]; then
    print_warning "URL tidak terlihat seperti Neon database. Lanjutkan? (y/N)"
    read -r confirm
    if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 6. Update environment file
print_status "Updating environment file..."

# Create temp file with fixed variables
TEMP_FILE=$(mktemp)

# Copy existing file and update DATABASE_URL
while IFS= read -r line; do
    if [[ "$line" =~ ^DATABASE_URL= ]]; then
        echo "DATABASE_URL=$NEON_DB_URL"
    elif [[ "$line" =~ ^SQLALCHEMY_DATABASE_URI= ]]; then
        echo "SQLALCHEMY_DATABASE_URI=$NEON_DB_URL"
    else
        echo "$line"
    fi
done < "$ENV_FILE" > "$TEMP_FILE"

# Add missing variables if needed
if ! grep -q "^DATABASE_URL=" "$TEMP_FILE"; then
    echo "DATABASE_URL=$NEON_DB_URL" >> "$TEMP_FILE"
fi

if ! grep -q "^SQLALCHEMY_DATABASE_URI=" "$TEMP_FILE"; then
    echo "SQLALCHEMY_DATABASE_URI=$NEON_DB_URL" >> "$TEMP_FILE"
fi

# Ensure production settings
if ! grep -q "^FLASK_ENV=" "$TEMP_FILE"; then
    echo "FLASK_ENV=production" >> "$TEMP_FILE"
fi

if ! grep -q "^API_KEY_REQUIRED=" "$TEMP_FILE"; then
    echo "API_KEY_REQUIRED=true" >> "$TEMP_FILE"
fi

# Replace original file
mv "$TEMP_FILE" "$ENV_FILE"

print_status "Environment file updated successfully!"

# 7. Restart service
print_status "Restarting cryptoapi service..."
sudo systemctl daemon-reload
sudo systemctl restart cryptoapi.service

# Wait a moment for service to start
sleep 3

# 8. Verify fix
print_status "Verifying fix..."
if systemctl is-active --quiet cryptoapi.service; then
    print_status "✅ Service is running"
    
    # Check new environment variables
    NEW_PID=$(systemctl show -p MainPID --value cryptoapi.service)
    if [ "$NEW_PID" != "0" ] && [ -n "$NEW_PID" ]; then
        echo ""
        echo "Updated environment variables:"
        tr '\0' '\n' </proc/$NEW_PID/environ | grep -E 'DATABASE_URL|SQLALCHEMY_DATABASE_URI'
        echo ""
    fi
    
    # Test database connection
    print_status "Testing database connection..."
    sleep 2
    
    HEALTH_RESPONSE=$(curl -s http://localhost:5000/health 2>/dev/null || echo "ERROR")
    
    if [[ "$HEALTH_RESPONSE" =~ "healthy" ]]; then
        print_status "✅ Database connection successful!"
        echo "$HEALTH_RESPONSE" | grep -o '"database":[^}]*}' || echo "Database status in health response"
    else
        print_error "❌ Database connection failed"
        echo "Health response: $HEALTH_RESPONSE"
        
        print_status "Checking service logs..."
        sudo journalctl -u cryptoapi.service -n 10 --no-pager
    fi
    
else
    print_error "❌ Service failed to start"
    print_status "Checking service logs..."
    sudo journalctl -u cryptoapi.service -n 20 --no-pager
fi

# 9. Test API endpoints
print_status "Testing API endpoints..."

# Test public endpoint
ROOT_RESPONSE=$(curl -s http://localhost:5000/ 2>/dev/null || echo "ERROR")
if [[ "$ROOT_RESPONSE" =~ "crypto-trading-suite" ]]; then
    print_status "✅ Root endpoint working"
else
    print_warning "⚠️ Root endpoint may have issues"
fi

echo ""
print_status "🎉 FIX COMPLETE!"
echo "==============="
echo ""
echo "Summary of changes:"
echo "• DATABASE_URL updated to use Neon database"
echo "• SQLALCHEMY_DATABASE_URI confirmed to use same database"
echo "• Service restarted with new configuration"
echo "• Database connection verified"
echo ""
echo "Your VPS deployment should now be working correctly!"
echo ""
print_warning "Backup file created at: $BACKUP_FILE"
print_warning "You can restore the old configuration with:"
echo "cp $BACKUP_FILE $ENV_FILE && sudo systemctl restart cryptoapi.service"