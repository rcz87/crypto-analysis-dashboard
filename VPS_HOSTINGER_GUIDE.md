# 🚀 Deploy ke VPS Hostinger - Complete Guide

## 📋 Prerequisites
- VPS Hostinger dengan Ubuntu 20.04+ atau CentOS 8+
- Domain name (opsional, bisa pakai IP langsung)
- API keys: OKX, OpenAI

## 🔧 Step 1: Persiapan VPS

### 1.1 Connect ke VPS
```bash
ssh root@your-vps-ip
# atau
ssh your-username@your-vps-ip
```

### 1.2 Update sistem
```bash
sudo apt update && sudo apt upgrade -y
```

### 1.3 Install Git
```bash
sudo apt install git -y
```

## 📦 Step 2: Upload Project ke VPS

### Option A: Upload via Git (Recommended)
```bash
# Di VPS
git clone https://github.com/your-username/crypto-trading-ai.git
cd crypto-trading-ai
```

### Option B: Upload via SCP dari komputer lokal
```bash
# Di komputer lokal (bukan VPS)
scp -r crypto-trading-ai/ your-username@your-vps-ip:/home/your-username/
```

## 🚀 Step 3: Deploy Otomatis

### 3.1 Jalankan script deployment
```bash
# Di VPS, masuk ke folder project
cd crypto-trading-ai
chmod +x deploy-vps.sh
./deploy-vps.sh
```

Script akan otomatis:
- ✅ Install Docker & Docker Compose
- ✅ Setup firewall (UFW)
- ✅ Create .env file
- ✅ Build & start semua services
- ✅ Health check aplikasi

### 3.2 Configure environment variables
Saat diminta, edit file `.env`:
```bash
nano .env
```

Isi dengan data Anda:
```env
# Database
POSTGRES_PASSWORD=crypto_secure_password_2024

# OKX API (WAJIB)
OKX_API_KEY=your_okx_api_key
OKX_SECRET_KEY=your_okx_secret_key  
OKX_PASSPHRASE=your_okx_passphrase

# OpenAI (WAJIB)
OPENAI_API_KEY=sk-your_openai_key

# Telegram (OPSIONAL)
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

## 🌐 Step 4: Testing

### 4.1 Cek aplikasi running
```bash
curl http://localhost/health
```

Response sukses:
```json
{
  "status": "healthy",
  "timestamp": "2024-08-02T16:30:00Z"
}
```

### 4.2 Test API endpoints
```bash
# Get market data
curl "http://your-vps-ip/api/gpts/market-data?symbol=BTC-USDT"

# Get trading signals
curl "http://your-vps-ip/api/gpts/trading-signals?symbol=BTC-USDT&timeframe=1H"
```

## ⚙️ Step 5: Management Commands

### 5.1 View logs
```bash
# All services
docker-compose -f docker-compose-vps.yml logs -f

# Specific service
docker-compose -f docker-compose-vps.yml logs -f crypto-app
docker-compose -f docker-compose-vps.yml logs -f postgres
docker-compose -f docker-compose-vps.yml logs -f nginx
```

### 5.2 Restart services
```bash
# Restart all
docker-compose -f docker-compose-vps.yml restart

# Restart specific service
docker-compose -f docker-compose-vps.yml restart crypto-app
```

### 5.3 Update aplikasi
```bash
git pull
docker-compose -f docker-compose-vps.yml up -d --build
```

### 5.4 Stop services
```bash
docker-compose -f docker-compose-vps.yml down
```

## 🔒 Step 6: SSL Certificate (HTTPS) - Opsional

### 6.1 Install Certbot
```bash
sudo apt install certbot python3-certbot-nginx -y
```

### 6.2 Update nginx config dengan domain
```bash
nano nginx/nginx.conf
```

Ganti `server_name _;` dengan:
```nginx
server_name your-domain.com www.your-domain.com;
```

### 6.3 Generate SSL certificate
```bash
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

### 6.4 Auto-renewal
```bash
sudo crontab -e
```

Tambahkan:
```
0 12 * * * /usr/bin/certbot renew --quiet
```

## 📊 Step 7: Monitoring & Backup

### 7.1 Monitor resources
```bash
# CPU, Memory usage
htop

# Disk usage  
df -h

# Docker stats
docker stats
```

### 7.2 Backup database
```bash
# Create backup
docker exec crypto_postgres pg_dump -U crypto_user crypto_trading > backup_$(date +%Y%m%d).sql

# Restore backup
docker exec -i crypto_postgres psql -U crypto_user crypto_trading < backup_20240802.sql
```

## 🔧 Troubleshooting

### Service tidak start
```bash
# Check logs
docker-compose -f docker-compose-vps.yml logs crypto-app

# Rebuild
docker-compose -f docker-compose-vps.yml up -d --build --force-recreate
```

### Port sudah digunakan
```bash
# Check port usage
sudo netstat -tulpn | grep :80
sudo netstat -tulpn | grep :5000

# Kill process using port
sudo kill -9 PID
```

### Database connection error
```bash
# Reset database
docker-compose -f docker-compose-vps.yml down
docker volume rm crypto-trading-ai_postgres_data
docker-compose -f docker-compose-vps.yml up -d
```

## 🎯 Performance Tips

### 1. Optimize VPS resources
- Minimum: 2GB RAM, 2 CPU cores
- Recommended: 4GB RAM, 4 CPU cores
- Storage: 20GB+ SSD

### 2. Scale with Docker
```bash
# Scale app instances
docker-compose -f docker-compose-vps.yml up -d --scale crypto-app=2
```

### 3. Monitor logs
```bash
# Rotate logs
docker-compose -f docker-compose-vps.yml logs --tail=1000 crypto-app > app.log
```

## 📱 Akses Aplikasi

Setelah deployment sukses:

- **Web Interface**: `http://your-vps-ip`  
- **API Documentation**: `http://your-vps-ip/api/gpts/`
- **Health Check**: `http://your-vps-ip/health`

## ✅ Checklist Deployment

- [ ] VPS prepared and updated
- [ ] Project uploaded to VPS  
- [ ] Docker & Docker Compose installed
- [ ] .env configured with API keys
- [ ] Services built and started
- [ ] Health check passing
- [ ] API endpoints working
- [ ] Firewall configured
- [ ] SSL certificate (optional)
- [ ] Monitoring setup
- [ ] Backup strategy

---

**🎉 Selamat! Aplikasi Crypto Trading AI sudah running di VPS Hostinger Anda!**

Support: Jika ada masalah, cek logs dan troubleshooting section di atas.