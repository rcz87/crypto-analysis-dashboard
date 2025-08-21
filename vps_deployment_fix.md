# VPS Deployment Fix - Database Configuration

## Masalah yang Ditemukan

Dari output VPS Anda:
```bash
DATABASE_URL=postgresql://trading_user:your_password@localhost:5432/trading_db
SQLALCHEMY_DATABASE_URI=postgresql://neondb_owner:YOUR_NEON_PASS@ep-billowing-sunset-xxxx.us-east-2.aws.neon.tech/neondb?sslmode=require
```

**MASALAH**: Ada konflik antara dua database URLs - satu mengarah ke PostgreSQL lokal (yang tidak ada), satu ke Neon database yang benar.

## Solusi untuk VPS

### 1. Environment Variables yang BENAR

Gunakan konfigurasi ini di VPS Anda:

```bash
# File: /etc/systemd/system/cryptoapi.service.d/override.conf
# atau di file environment VPS

DATABASE_URL=postgresql://neondb_owner:YOUR_ACTUAL_NEON_PASSWORD@ep-billowing-sunset-xxxx.us-east-2.aws.neon.tech/neondb?sslmode=require
SQLALCHEMY_DATABASE_URI=postgresql://neondb_owner:YOUR_ACTUAL_NEON_PASSWORD@ep-billowing-sunset-xxxx.us-east-2.aws.neon.tech/neondb?sslmode=require
API_KEY=your_actual_api_key
API_KEY_REQUIRED=true
FLASK_ENV=production
OPENAI_API_KEY=your_openai_key
OKX_API_KEY=your_okx_api_key
OKX_SECRET_KEY=your_okx_secret
OKX_PASSPHRASE=your_okx_passphrase
```

### 2. Langkah Perbaikan di VPS

```bash
# 1. Stop service
sudo systemctl stop cryptoapi.service

# 2. Edit environment file atau systemd override
sudo nano /etc/systemd/system/cryptoapi.service.d/override.conf

# 3. Pastikan HANYA menggunakan Neon database URL
# HAPUS semua reference ke localhost:5432

# 4. Reload systemd dan restart
sudo systemctl daemon-reload
sudo systemctl start cryptoapi.service

# 5. Verify environment variables
PID=$(systemctl show -p MainPID --value cryptoapi.service)
tr '\0' '\n' </proc/$PID/environ | grep -E 'DATABASE_URL|SQLALCHEMY_DATABASE_URI'
```

### 3. Verifikasi Fix

Setelah restart, kedua environment variables harus menunjuk ke Neon database yang sama:

```bash
DATABASE_URL=postgresql://neondb_owner:PASSWORD@ep-billowing-sunset-xxxx.us-east-2.aws.neon.tech/neondb?sslmode=require
SQLALCHEMY_DATABASE_URI=postgresql://neondb_owner:PASSWORD@ep-billowing-sunset-xxxx.us-east-2.aws.neon.tech/neondb?sslmode=require
```

### 4. Test Koneksi

```bash
# Test database connection
curl -s http://YOUR_VPS_IP:5000/health | jq '.components.database'

# Should return:
{
  "status": "healthy",
  "message": "SQLAlchemy connection successful"
}
```

## Root Cause

Aplikasi menggunakan Flask-SQLAlchemy yang membaca `DATABASE_URL` sebagai primary, tapi jika ada `SQLALCHEMY_DATABASE_URI` juga bisa konflik. Pastikan keduanya menunjuk ke database yang sama.

## Production Best Practice

Untuk deployment VPS, gunakan:
1. **HANYA Neon PostgreSQL** (bukan local PostgreSQL)
2. **SSL enabled** (sslmode=require)  
3. **Environment variables consistency** (DATABASE_URL = SQLALCHEMY_DATABASE_URI)
4. **Proper secret management** (jangan hardcode passwords)