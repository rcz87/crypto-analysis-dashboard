# 🚀 VPS Deployment Verification Commands

## System Status dari Screenshot:
✅ **VPS IP**: 212.26.36.253  
✅ **System Load**: 6.83 (normal)  
✅ **Memory**: 16.6% of 191GB (excellent)  
✅ **Disk**: 13% used (plenty of space)  
✅ **Ubuntu**: Running smoothly

## Verification Commands untuk SSH:

### 1. Connect ke VPS
```bash
ssh root@212.26.36.253
```

### 2. Check Project Directory
```bash
cd /root/crypto-analysis-dashboard
ls -la main.py app.py routes/ scripts/
```

### 3. Pull Latest Changes
```bash
git status
git fetch origin
git reset --hard origin/main
```

### 4. Verify New Structure
```bash
echo "=== Checking Flask+Gunicorn Structure ==="
echo "Entry point:"
cat main.py

echo "Application factory:"
head -20 app.py

echo "Health endpoints:"
ls -la routes/health.py

echo "Deployment script:"
ls -la scripts/deploy-vps.sh
```

### 5. Run Deployment
```bash
# Make script executable if needed
chmod +x scripts/deploy-vps.sh

# Deploy
bash scripts/deploy-vps.sh
```

### 6. Verify Service
```bash
# Check service status
systemctl status cryptoapi.service

# Check if service is running
systemctl is-active cryptoapi.service

# Check service logs
journalctl -u cryptoapi.service -n 20 --no-pager
```

### 7. Test Endpoints
```bash
echo "=== Testing New Endpoints ==="

echo "1. Health check:"
curl -s http://127.0.0.1:5050/health | head -3

echo "2. Status check:"
curl -s http://127.0.0.1:5050/api/gpts/status | head -3

echo "3. Root endpoint:"
curl -s http://127.0.0.1:5050/ | head -3
```

### 8. Full Health Verification
```bash
echo "=== Full Health Check ==="
curl -s http://127.0.0.1:5050/health | python3 -m json.tool
```

## Expected Results:

### Service Status:
```
● cryptoapi.service - Crypto Trading API
   Active: active (running)
```

### Health Response:
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
  },
  "version": "2.0.0"
}
```

### Status Response:
```json
{
  "status": "active",
  "version": {"api_version": "2.0.0"},
  "components": {
    "database": "available",
    "okx_api": "connected"
  }
}
```

## If Service Needs Restart:
```bash
systemctl restart cryptoapi.service
sleep 5
systemctl status cryptoapi.service
```

## Check Process:
```bash
ps aux | grep gunicorn
# Should show: main:app
```

---

**Flask + Gunicorn structure siap diverifikasi di VPS!**