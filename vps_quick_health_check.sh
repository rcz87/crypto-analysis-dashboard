#!/bin/bash

# Quick VPS Health Check Script
# Diagnose and show current status

echo "🔍 VPS QUICK HEALTH CHECK"
echo "========================"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_ok() { echo -e "${GREEN}✅ $1${NC}"; }
print_fail() { echo -e "${RED}❌ $1${NC}"; }
print_warn() { echo -e "${YELLOW}⚠️  $1${NC}"; }

echo ""
echo "1. SERVICE STATUS"
echo "=================="

if systemctl is-active --quiet cryptoapi.service; then
    print_ok "cryptoapi.service is running"
    
    # Get PID and show basic info
    PID=$(systemctl show -p MainPID --value cryptoapi.service)
    if [ "$PID" != "0" ]; then
        echo "   Process ID: $PID"
        echo "   Memory usage: $(ps -p $PID -o rss= 2>/dev/null | awk '{print int($1/1024) " MB"}' || echo "N/A")"
        
        # Show environment variables
        echo ""
        echo "   Environment variables:"
        if [ -r "/proc/$PID/environ" ]; then
            tr '\0' '\n' </proc/$PID/environ | grep -E 'DATABASE_URL|SQLALCHEMY_DATABASE_URI|FLASK_ENV' | sed 's/^/     /'
        else
            echo "     Cannot read environment (permission denied)"
        fi
    fi
else
    print_fail "cryptoapi.service is not running"
    echo "   Last status:"
    sudo systemctl status cryptoapi.service --no-pager --lines=3
fi

echo ""
echo "2. NETWORK CONNECTIVITY"
echo "======================="

# Check if port 5000 is listening
if netstat -tlnp 2>/dev/null | grep -q ":5000 "; then
    print_ok "Port 5000 is listening"
    netstat -tlnp | grep ":5000 " | head -1
else
    print_fail "Port 5000 is not listening"
fi

echo ""
echo "3. APPLICATION HEALTH"
echo "===================="

# Test health endpoint
HEALTH_RESPONSE=$(curl -s --connect-timeout 5 http://localhost:5000/health 2>/dev/null)
CURL_EXIT_CODE=$?

if [ $CURL_EXIT_CODE -eq 0 ] && [ -n "$HEALTH_RESPONSE" ]; then
    if [[ "$HEALTH_RESPONSE" =~ "healthy" ]]; then
        print_ok "Health endpoint responding - HEALTHY"
        echo "$HEALTH_RESPONSE" | python3 -c "import sys, json; print(json.dumps(json.load(sys.stdin), indent=2))" 2>/dev/null || echo "$HEALTH_RESPONSE"
    else
        print_warn "Health endpoint responding but not healthy"
        echo "$HEALTH_RESPONSE"
    fi
else
    print_fail "Health endpoint not responding"
    echo "   Curl exit code: $CURL_EXIT_CODE"
fi

echo ""
echo "4. ROOT ENDPOINT TEST"
echo "===================="

ROOT_RESPONSE=$(curl -s --connect-timeout 5 http://localhost:5000/ 2>/dev/null)
if [[ "$ROOT_RESPONSE" =~ "crypto-trading-suite" ]]; then
    print_ok "Root endpoint working"
else
    print_fail "Root endpoint not working properly"
    echo "Response: ${ROOT_RESPONSE:0:100}..."
fi

echo ""
echo "5. DATABASE CONNECTION"
echo "====================="

# Check if database environment variables are set
ENV_FILE=""
SERVICE_FILE="/etc/systemd/system/cryptoapi.service"

if [ -f "$SERVICE_FILE" ]; then
    ENV_FILE=$(grep "EnvironmentFile=" "$SERVICE_FILE" 2>/dev/null | cut -d'=' -f2 | tr -d ' ')
fi

if [ -n "$ENV_FILE" ] && [ -f "$ENV_FILE" ]; then
    print_ok "Environment file found: $ENV_FILE"
    
    # Check database URLs
    DATABASE_URL=$(grep "^DATABASE_URL=" "$ENV_FILE" 2>/dev/null | cut -d'=' -f2-)
    SQLALCHEMY_URI=$(grep "^SQLALCHEMY_DATABASE_URI=" "$ENV_FILE" 2>/dev/null | cut -d'=' -f2-)
    
    if [[ "$DATABASE_URL" =~ neon\.tech ]]; then
        print_ok "DATABASE_URL points to Neon database"
    elif [[ "$DATABASE_URL" =~ localhost:5432 ]]; then
        print_fail "DATABASE_URL still points to localhost PostgreSQL!"
        echo "   This is the problem - needs to point to Neon database"
    else
        print_warn "DATABASE_URL: ${DATABASE_URL:0:50}..."
    fi
    
    if [[ "$SQLALCHEMY_URI" =~ neon\.tech ]]; then
        print_ok "SQLALCHEMY_DATABASE_URI points to Neon database"
    elif [[ "$SQLALCHEMY_URI" =~ localhost:5432 ]]; then
        print_fail "SQLALCHEMY_DATABASE_URI still points to localhost!"
    else
        print_warn "SQLALCHEMY_DATABASE_URI: ${SQLALCHEMY_URI:0:50}..."
    fi
    
    # Check if URLs match
    if [ "$DATABASE_URL" = "$SQLALCHEMY_URI" ]; then
        print_ok "DATABASE_URL and SQLALCHEMY_DATABASE_URI match"
    else
        print_fail "DATABASE_URL and SQLALCHEMY_DATABASE_URI are different!"
        echo "   This can cause connection issues"
    fi
else
    print_fail "Environment file not found or not accessible"
fi

echo ""
echo "6. RECENT LOGS"
echo "=============="

echo "Last 5 log entries:"
sudo journalctl -u cryptoapi.service -n 5 --no-pager 2>/dev/null | sed 's/^/   /' || echo "   Cannot access logs"

echo ""
echo "7. DISK SPACE"
echo "============="

df -h / | tail -1 | awk '{
    if ($5+0 > 90) 
        printf "❌ Disk usage: %s (WARNING: >90%%)\n", $5
    else if ($5+0 > 75)
        printf "⚠️  Disk usage: %s\n", $5
    else
        printf "✅ Disk usage: %s\n", $5
}'

echo ""
echo "8. SUMMARY & RECOMMENDATIONS"
echo "============================"

# Determine overall status
OVERALL_HEALTHY=true

if ! systemctl is-active --quiet cryptoapi.service; then
    OVERALL_HEALTHY=false
    echo "🔧 ACTION NEEDED: Service is not running"
    echo "   → sudo systemctl start cryptoapi.service"
fi

if ! netstat -tlnp 2>/dev/null | grep -q ":5000 "; then
    OVERALL_HEALTHY=false
    echo "🔧 ACTION NEEDED: Port 5000 not listening"
    echo "   → Check application startup logs"
fi

HEALTH_CHECK=$(curl -s --connect-timeout 3 http://localhost:5000/health 2>/dev/null)
if [[ ! "$HEALTH_CHECK" =~ "healthy" ]]; then
    OVERALL_HEALTHY=false
    echo "🔧 ACTION NEEDED: Health check failing"
    echo "   → Likely database connection issue"
fi

# Check for localhost database issue
if [ -n "$ENV_FILE" ] && [ -f "$ENV_FILE" ]; then
    if grep -q "localhost:5432" "$ENV_FILE" 2>/dev/null; then
        OVERALL_HEALTHY=false
        echo "🔧 ACTION NEEDED: Database URL pointing to localhost"
        echo "   → Run: ./final_vps_database_fix.sh"
    fi
fi

if $OVERALL_HEALTHY; then
    echo ""
    print_ok "VPS deployment appears to be healthy!"
    echo "   All systems operational"
else
    echo ""
    print_fail "VPS deployment has issues that need attention"
    echo ""
    echo "QUICK FIX:"
    echo "1. Run the database fix script:"
    echo "   ./final_vps_database_fix.sh"
    echo ""
    echo "2. Or manually restart service:"
    echo "   sudo systemctl restart cryptoapi.service"
    echo ""
    echo "3. Check logs for errors:"
    echo "   sudo journalctl -u cryptoapi.service -f"
fi

echo ""
echo "Run this script anytime to check VPS status: ./vps_quick_health_check.sh"