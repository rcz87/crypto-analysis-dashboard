# Quick VPS Deployment Guide

## 🚀 Deployment Process

### Langkah 1: Upload Code ke VPS

```bash
# Di VPS, buat direktori
mkdir -p ~/crypto-analysis-dashboard
cd ~/crypto-analysis-dashboard

# Upload semua file dari Replit ke VPS
# Gunakan scp, rsync, atau git clone
```

### Langkah 2: Jalankan Deployment Script

```bash
# Copy script deployment ke VPS
chmod +x deploy_to_vps.sh
./deploy_to_vps.sh
```

### Langkah 3: Konfigurasi Environment

Edit file environment dengan credentials yang benar:

```bash
nano .env.production
```

Pastikan menggunakan konfigurasi ini (sesuai yang Anda tunjukkan):

```bash
# Database - PENTING: Gunakan Neon database yang sama untuk kedua variable
DATABASE_URL=postgresql://neondb_owner:YOUR_NEON_PASSWORD@ep-billowing-sunset-xxxx.us-east-2.aws.neon.tech/neondb?sslmode=require
SQLALCHEMY_DATABASE_URI=postgresql://neondb_owner:YOUR_NEON_PASSWORD@ep-billowing-sunset-xxxx.us-east-2.aws.neon.tech/neondb?sslmode=require

# Security
FLASK_ENV=production
API_KEY_REQUIRED=true
API_KEY=your-actual-api-key

# AI Services
OPENAI_API_KEY=sk-proj-your-openai-key

# OKX Trading API
OKX_API_KEY=your-okx-key
OKX_SECRET_KEY=your-okx-secret
OKX_PASSPHRASE=your-okx-passphrase
```

### Langkah 4: Konfigurasi Domain

Edit konfigurasi Nginx:

```bash
sudo nano /etc/nginx/sites-available/cryptoapi
```

Ganti `your-domain.com` dengan domain Anda yang sesungguhnya.

### Langkah 5: Start Services

```bash
./start_services.sh
```

### Langkah 6: Verifikasi Deployment

```bash
./check_status.sh
```

### Langkah 7: Setup SSL (Opsional tapi Disarankan)

```bash
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

## 🔧 Troubleshooting

### Jika Database Connection Error

Masalah yang sering terjadi (seperti yang Anda alami):

```bash
# Check environment variables
PID=$(systemctl show -p MainPID --value cryptoapi.service)
tr '\0' '\n' </proc/$PID/environ | grep -E 'DATABASE_URL|SQLALCHEMY_DATABASE_URI'
```

**PASTIKAN** kedua variable menunjuk ke Neon database yang sama, BUKAN ke localhost:5432!

### Jika Service Tidak Start

```bash
# Check logs
sudo journalctl -u cryptoapi.service -f

# Check nginx
sudo nginx -t
sudo systemctl status nginx
```

### Jika API Key Error

```bash
# Test dengan curl
curl -H "X-API-KEY: your-api-key" http://your-domain.com/api/gpts/status
```

## 📊 Monitoring

Setelah deployment sukses, Anda bisa monitor dengan:

```bash
# Real-time logs
sudo journalctl -u cryptoapi.service -f

# Performance
htop

# Disk usage
df -h

# Network connections
netstat -tlnp | grep :5000
```

## 🔒 Security Checklist

- ✅ Firewall dikonfigurasi (hanya port 22, 80, 443)
- ✅ SSL certificate diinstall
- ✅ API key authentication enabled
- ✅ Rate limiting dikonfigurasi di Nginx
- ✅ Security headers ditambahkan
- ✅ Service berjalan sebagai non-root user

## 🎯 Expected Results

Setelah deployment sukses:

1. **Health Check**: `curl http://your-domain.com/health` → Status "healthy"
2. **API Endpoints**: Semua endpoint `/api/*` berfungsi dengan API key
3. **Database**: Koneksi ke Neon PostgreSQL stabil
4. **Performance**: Response time < 2 detik untuk trading signals
5. **Monitoring**: Logs tersedia di `/var/log/` dan systemd journal

## 📞 Support

Jika ada masalah, jalankan script diagnostik:

```bash
./check_status.sh > deployment_status.txt
./view_logs.sh > deployment_logs.txt
```

Dan kirimkan output file tersebut untuk troubleshooting.