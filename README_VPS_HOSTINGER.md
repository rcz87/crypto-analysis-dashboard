# 🚀 VPS Hostinger Deployment Guide
# Cryptocurrency Trading AI Platform

## 📋 Ringkasan Proyek

Proyek ini adalah **platform trading cryptocurrency berbasis AI** yang telah berhasil diperbaiki dan dioptimalkan untuk deployment di VPS Hostinger dengan domain sendiri. 

### ✅ **Masalah yang Sudah Diperbaiki:**
1. **Blueprint conflicts** - Endpoint GPTs sudah berfungsi normal
2. **LSP errors** - File-file core sudah kompatibel 
3. **Import errors** - Semua dependencies terorganisir dengan baik
4. **Database compatibility** - PostgreSQL terintegrasi sempurna

## 🏗️ **Arsitektur yang Sudah Diperbaiki:**

### **Core Components (Sudah Production-Ready):**
- ✅ `core/okx_fetcher.py` - OKX API dengan fallback data
- ✅ `core/professional_smc_analyzer.py` - SMC analysis engine
- ✅ `core/signal_generator.py` - Trading signal generator
- ✅ `core/ai_engine.py` - OpenAI GPT-4 integration
- ✅ `gpts_routes.py` - API endpoints untuk ChatGPT Custom GPT

### **API Endpoints yang Aktif:**
- `GET /health` - Health check
- `GET /api/gpts/status` - System status
- `POST /api/gpts/sinyal/tajam` - Trading signals
- `GET /api/gpts/market-data` - Real-time market data
- `POST /api/gpts/smc-analysis` - SMC analysis

## 🖥️ **VPS Hostinger Deployment**

### **Prerequisites:**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3 python3-pip python3-venv nginx postgresql redis-server git
```

### **Quick Deployment:**
```bash
# 1. Clone project ke VPS
git clone https://github.com/your-repo/crypto-trading-ai.git
cd crypto-trading-ai

# 2. Run deployment script
chmod +x deployment/deploy_vps_hostinger.sh
./deployment/deploy_vps_hostinger.sh

# 3. Configure API keys
nano .env
# Tambahkan:
# OPENAI_API_KEY=your_key_here
# OKX_API_KEY=your_key_here

# 4. Restart services
sudo systemctl restart crypto-trading-ai
sudo systemctl restart nginx
```

### **Manual Deployment Steps:**

#### **1. Setup Python Environment:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r pyproject.toml
```

#### **2. Configure Database:**
```bash
sudo -u postgres createdb crypto-trading-ai
sudo -u postgres createuser crypto-trading-ai
# Set password and permissions
```

#### **3. Environment Configuration:**
```bash
cp .env.example .env
# Edit .env dengan API keys dan database URL
```

#### **4. Nginx Configuration:**
```bash
sudo cp deployment/nginx_config.conf /etc/nginx/sites-available/crypto-trading-ai
sudo ln -s /etc/nginx/sites-available/crypto-trading-ai /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### **5. SSL Certificate (Let's Encrypt):**
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

## 🔧 **Configuration Files:**

### **Gunicorn Configuration:**
File: `gunicorn.conf.py` (auto-created by script)
```python
bind = "127.0.0.1:5000"
workers = 2
worker_class = 'sync'
timeout = 120
preload_app = True
```

### **Systemd Service:**
File: `/etc/systemd/system/crypto-trading-ai.service`
```ini
[Unit]
Description=Cryptocurrency Trading AI Platform
After=network.target

[Service]
Type=exec
User=www-data
WorkingDirectory=/var/www/crypto-trading-ai
ExecStart=/var/www/crypto-trading-ai/venv/bin/gunicorn main:app
Restart=always

[Install]
WantedBy=multi-user.target
```

## 🔐 **Environment Variables Needed:**

```env
# Database
DATABASE_URL=postgresql://user:pass@localhost/crypto-trading-ai

# API Keys
OPENAI_API_KEY=sk-your-openai-key
OKX_API_KEY=your-okx-api-key
OKX_SECRET_KEY=your-okx-secret
OKX_PASSPHRASE=your-okx-passphrase

# Telegram (Optional)
TELEGRAM_BOT_TOKEN=your-telegram-token

# Flask
SECRET_KEY=your-secret-key
FLASK_ENV=production
```

## 📊 **Testing Endpoints:**

### **1. Health Check:**
```bash
curl https://yourdomain.com/health
```

### **2. System Status:**
```bash
curl https://yourdomain.com/api/gpts/status
```

### **3. Trading Signal:**
```bash
curl -X POST https://yourdomain.com/api/gpts/sinyal/tajam \
  -H "Content-Type: application/json" \
  -d '{"symbol":"BTC-USDT","timeframe":"1H"}'
```

## 🚨 **Troubleshooting:**

### **Check Application Logs:**
```bash
sudo journalctl -f -u crypto-trading-ai
```

### **Check Nginx Logs:**
```bash
sudo tail -f /var/log/nginx/error.log
```

### **Restart Services:**
```bash
sudo systemctl restart crypto-trading-ai
sudo systemctl restart nginx
```

### **Database Issues:**
```bash
sudo -u postgres psql -d crypto-trading-ai -c "SELECT version();"
```

## 🎯 **ChatGPT Custom GPT Integration:**

### **OpenAPI Schema URL:**
```
https://yourdomain.com/api/gpts/openapi.json
```

### **Key Endpoints for GPT:**
- Trading signals: `/api/gpts/sinyal/tajam`
- Market data: `/api/gpts/market-data`
- SMC analysis: `/api/gpts/smc-analysis`

## 🔄 **Maintenance Commands:**

```bash
# Update code
cd /var/www/crypto-trading-ai
git pull origin main
sudo systemctl restart crypto-trading-ai

# Check service status
sudo systemctl status crypto-trading-ai nginx postgresql

# View real-time logs
sudo journalctl -f -u crypto-trading-ai

# Backup database
sudo -u postgres pg_dump crypto-trading-ai > backup_$(date +%Y%m%d).sql
```

## 📈 **Performance Optimization:**

1. **Redis Caching:** Sudah dikonfigurasi untuk OKX API caching
2. **Gunicorn Workers:** Auto-scaled berdasarkan CPU cores
3. **Nginx Buffering:** Optimized untuk API responses
4. **Database Connection Pooling:** PostgreSQL dengan pool settings
5. **Rate Limiting:** Nginx rate limiting untuk API endpoints

## ✅ **Deployment Success Checklist:**

- [ ] Server running without errors
- [ ] Database connected and migrations complete  
- [ ] API endpoints responding correctly
- [ ] SSL certificate installed and working
- [ ] Domain pointing to VPS IP
- [ ] API keys configured in environment
- [ ] Nginx reverse proxy working
- [ ] Systemd service auto-starting
- [ ] Logs being written correctly
- [ ] ChatGPT Custom GPT integration tested

---

**🎉 Deployment Completed Successfully!**

Platform Anda sekarang siap untuk:
- Integrasi dengan ChatGPT Custom GPT
- Trading signal analysis real-time  
- SMC professional analysis
- Multi-timeframe market data
- VPS hosting dengan domain sendiri

Untuk support lebih lanjut, check logs di `/var/log/` dan service status dengan `systemctl status`.