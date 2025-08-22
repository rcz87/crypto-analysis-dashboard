# 🔧 VPS Database Connection Fix

## Problem Analysis
- **Database Status**: unhealthy (connection to localhost:5432 failed)
- **User Issue**: Using 'trading_user' instead of 'neondb_owner'  
- **Root Cause**: Service using old localhost PostgreSQL config instead of Neon

## Current Status
✅ **OKX API**: healthy  
✅ **Status Endpoint**: active  
✅ **Flask App**: running (28/32 blueprints registered)  
❌ **Database**: unhealthy (wrong connection string)

## Fix Commands for VPS

### Option 1: Run Database Fix Script
```bash
cd /root/crypto-analysis-dashboard
bash fix_vps_database_connection.sh
```

### Option 2: Manual Fix Steps
```bash
# Stop service
systemctl stop cryptoapi.service

# Create systemd override directory
mkdir -p /etc/systemd/system/cryptoapi.service.d/

# Create database configuration override
cat > /etc/systemd/system/cryptoapi.service.d/database.conf << 'EOF'
[Service]
Environment="DATABASE_URL=postgresql://neondb_owner:npg_pF1v5QHRUyJC@ep-billowing-sunset-a1n4dwi.us-east-2.aws.neon.tech/neondb?sslmode=require"
Environment="SQLALCHEMY_DATABASE_URI=postgresql://neondb_owner:npg_pF1v5QHRUyJC@ep-billowing-sunset-a1n4dwi.us-east-2.aws.neon.tech/neondb?sslmode=require"
EOF

# Reload systemd and restart service
systemctl daemon-reload
systemctl start cryptoapi.service

# Test database connection
curl -s http://127.0.0.1:5050/health
```

## Expected Result After Fix

### Health Endpoint Should Show:
```json
{
  "status": "healthy",
  "components": {
    "database": {
      "status": "healthy", 
      "message": "Database connection successful"
    },
    "okx_api": {
      "status": "healthy",
      "message": "OKX API connection successful"
    }
  }
}
```

## Verification Commands
```bash
# Check service status
systemctl status cryptoapi.service

# Check database environment
systemctl show cryptoapi.service -p Environment | grep DATABASE_URL

# Test all endpoints
curl -s http://127.0.0.1:5050/health
curl -s http://127.0.0.1:5050/api/gpts/status
curl -s http://127.0.0.1:5050/

# Check service logs
journalctl -u cryptoapi.service -n 20
```

## Notes
- Neon database credentials are embedded in the fix
- SSL connection required for Neon
- Service will restart with proper Flask + Gunicorn structure
- All 28 blueprints will remain registered