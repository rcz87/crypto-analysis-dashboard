# 🚀 Manual VPS Deployment Guide

## Issue dengan GitHub Push
**Problem**: Personal Access Token tidak memiliki `workflow` scope untuk push file `.github/workflows/deploy.yml`

**Solution**: Deploy manual ke VPS (lebih aman dan terkontrol)

## ✅ Files Ready for VPS Deployment

### Core Files:
- `main.py` - Entry point (main:app)
- `app.py` - Application factory
- `routes/health.py` - Health endpoints  
- `scripts/deploy-vps.sh` - Deployment script

### Endpoints Ready:
- `/` - Platform info
- `/health` - Database + API health check
- `/api/gpts/status` - Lightweight status

## 🔧 Manual VPS Deployment Steps

### 1. SSH ke VPS
```bash
ssh root@your-vps-ip
```

### 2. Navigate ke Project Directory
```bash
cd /root/crypto-analysis-dashboard
```

### 3. Manual Git Pull (Bypass GitHub Actions)
```bash
# Pull latest code manually
git fetch origin
git reset --hard origin/main

# Verify new files
ls -la scripts/deploy-vps.sh
ls -la routes/health.py
ls -la main.py app.py
```

### 4. Run Deployment Script
```bash
# Make script executable
chmod +x scripts/deploy-vps.sh

# Run deployment
bash scripts/deploy-vps.sh
```

### 5. Verify Deployment
```bash
# Check service status
systemctl status cryptoapi.service

# Test endpoints
curl -s http://127.0.0.1:5050/health
curl -s http://127.0.0.1:5050/api/gpts/status
curl -s http://127.0.0.1:5050/

# Check logs
journalctl -u cryptoapi.service -f
```

## 🎯 Expected Results

### Service Status:
```bash
● cryptoapi.service - Crypto Trading API
   Active: active (running)
```

### Health Endpoint:
```json
{
  "status": "healthy",
  "components": {
    "database": {"status": "healthy"},
    "okx_api": {"status": "healthy"}
  }
}
```

### Status Endpoint:
```json
{
  "status": "active",
  "version": {"api_version": "2.0.0"}
}
```

## 🔍 Troubleshooting

### If Service Fails:
```bash
# Check logs
journalctl -u cryptoapi.service -n 50

# Restart service
systemctl restart cryptoapi.service

# Check database connection
curl -s http://127.0.0.1:5050/health | grep database
```

### If Endpoints Return 404:
```bash
# Check if gunicorn is using correct entry point
ps aux | grep gunicorn
# Should show: main:app

# Verify file structure
ls -la main.py app.py routes/
```

## ✅ Deployment Checklist

- [ ] SSH ke VPS berhasil
- [ ] Git pull latest code
- [ ] Script deployment executable
- [ ] Service restart berhasil  
- [ ] Health endpoint returns "healthy"
- [ ] Status endpoint returns "active"
- [ ] No error logs in journalctl

## 🚨 Important Notes

1. **GitHub Actions Disabled** - Deploy manual untuk menghindari permission issues
2. **Entry Point**: `main:app` (sudah dikonfirmasi working)
3. **Database**: Neon PostgreSQL connection tested
4. **Port**: Service berjalan di port 5050
5. **Environment**: Variables sudah di systemd service

**Flask + Gunicorn structure sudah SIAP untuk production deployment!**