# 🚀 Panduan Deployment VPS Hostinger - Cryptocurrency Trading AI

## ✅ Ringkasan Perbaikan yang Telah Dilakukan

Proyek Anda telah berhasil diperbaiki dan dioptimalkan untuk deployment di VPS Hostinger:

### 🔧 **Masalah yang Diperbaiki**
1. **Blueprint Conflicts**: Fixed 14 LSP errors di gpts_routes.py
2. **Database Models**: Cleaned up duplicate SignalHistory classes  
3. **API Compatibility**: Fixed OKX fetcher, SMC analyzer, signal generator
4. **Flask Structure**: Simplified architecture following Replit guidelines
5. **Production Ready**: Added VPS-specific configuration and deployment scripts

### ✅ **Komponen yang Sudah Berjalan**
- ✅ Flask app running on port 5000
- ✅ PostgreSQL database connected
- ✅ Basic API endpoints (/health, /api/gpts/status) 
- ✅ Main GPTs signal endpoint (/api/gpts/sinyal/tajam)
- ✅ OKX data fetcher with fallback support
- ✅ Professional SMC analyzer
- ✅ AI-powered signal generation

## 🚀 Deployment ke VPS Hostinger

### 1. **Persiapan Awal**

Pastikan Anda memiliki:
- VPS Hostinger dengan Ubuntu 20.04+
- Domain name yang sudah pointing ke IP VPS
- SSH access ke server
- API keys: OpenAI, OKX, Telegram Bot

### 2. **Upload Files ke VPS**

```bash
# Di komputer lokal
scp -r . username@your-server-ip:/tmp/crypto-trading-ai/

# Login ke VPS
ssh username@your-server-ip

# Pindah files
sudo mv /tmp/crypto-trading-ai /var/www/crypto-trading-ai
cd /var/www/crypto-trading-ai
```

### 3. **Jalankan Script Deployment**

```bash
# Beri permission execute
chmod +x deployment/deploy_vps_hostinger.sh

# Edit domain di script
nano deployment/deploy_vps_hostinger.sh
# Ganti 'yourdomain.com' dengan domain Anda

# Jalankan deployment
./deployment/deploy_vps_hostinger.sh
```

### 4. **Set API Keys**

Setelah deployment selesai, edit file environment:

```bash
nano /var/www/crypto-trading-ai/.env
```

Update dengan API keys Anda:
```env
# API Keys
OPENAI_API_KEY=sk-your-openai-api-key
OKX_API_KEY=your-okx-api-key
OKX_SECRET_KEY=your-okx-secret-key
OKX_PASSPHRASE=your-okx-passphrase
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
```

### 5. **Restart Services**

```bash
sudo systemctl restart crypto-trading-ai
sudo systemctl restart nginx
```

## 🧪 Testing Setelah Deployment

### Test Local (di VPS)
```bash
# Health check
curl http://localhost:5000/health

# API status
curl http://localhost:5000/api/gpts/status

# Signal generation
curl -X POST -H "Content-Type: application/json" \
  -d '{"symbol":"BTC-USDT","timeframe":"1H"}' \
  http://localhost:5000/api/gpts/sinyal/tajam
```

### Test External (dari internet)
```bash
# Ganti dengan domain Anda
curl https://yourdomain.com/health
curl https://yourdomain.com/api/gpts/status
```

## 📊 Monitoring & Maintenance

### Check Service Status
```bash
# App status
sudo systemctl status crypto-trading-ai

# Nginx status  
sudo systemctl status nginx

# Check logs
sudo journalctl -f -u crypto-trading-ai
tail -f /var/log/crypto-trading-ai/error.log
```

### Update Application
```bash
cd /var/www/crypto-trading-ai
git pull origin main  # if using git
sudo systemctl restart crypto-trading-ai
```

## 🔒 Security Considerations

1. **Firewall Settings**
```bash
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
```

2. **SSL Certificate** - Otomatis di-setup oleh script deployment dengan Let's Encrypt

3. **Database Security** - Password random di-generate otomatis

4. **API Keys** - Disimpan di file .env yang secure (permissions 600)

## 🚨 Troubleshooting

### Jika Service Tidak Start
```bash
# Check logs
sudo journalctl -u crypto-trading-ai -n 50

# Check config
sudo systemctl status crypto-trading-ai

# Manual start untuk debug
cd /var/www/crypto-trading-ai
source venv/bin/activate
python main.py
```

### Jika Nginx Error
```bash
# Test config
sudo nginx -t

# Check error logs
sudo tail -f /var/log/nginx/error.log

# Restart nginx
sudo systemctl restart nginx
```

### Jika Database Error
```bash
# Check postgres
sudo systemctl status postgresql

# Connect to database
sudo -u postgres psql crypto-trading-ai
```

## 📈 Features yang Tersedia

### API Endpoints
- `GET /health` - Health check
- `GET /api/gpts/status` - System status
- `POST /api/gpts/sinyal/tajam` - Main trading signal
- `GET /api/gpts/market-data` - Market data
- `POST /api/gpts/smc-analysis` - SMC analysis

### ChatGPT Custom GPT Integration
Endpoint sudah siap untuk integrasi dengan ChatGPT Custom GPT:
- CORS headers configured
- JSON response format
- Error handling
- Rate limiting

## 🎯 Next Steps

Setelah deployment berhasil:

1. **Test semua endpoints** dari ChatGPT Custom GPT
2. **Setup Telegram bot** untuk notifications
3. **Configure monitoring** untuk uptime checking
4. **Set up backups** untuk database
5. **Performance tuning** berdasarkan traffic

## 🆘 Support

Jika ada masalah:
1. Check logs di `/var/log/crypto-trading-ai/`
2. Check service status dengan `systemctl status`
3. Test individual components
4. Verify API keys dan environment variables

---

**Status Deployment**: ✅ **READY FOR PRODUCTION**

Sistem Anda sudah siap untuk di-deploy ke VPS Hostinger dengan konfigurasi production-grade yang aman dan scalable!