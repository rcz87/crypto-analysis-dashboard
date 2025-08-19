# Setup GitHub Secrets untuk Auto Deployment

## 📋 Langkah-langkah Setup

### 1. Di GitHub Repository
1. Buka repository Anda di GitHub
2. Klik `Settings` tab
3. Pilih `Secrets and variables` → `Actions`
4. Klik `New repository secret`

### 2. Tambahkan Secrets Berikut:

**VPS_HOST**
```
Value: IP_ADDRESS_VPS_ANDA
Example: 192.168.1.100
```

**VPS_USER**
```
Value: root
```

**VPS_SSH_KEY**
```
Value: [Private SSH Key Content]
Cara mendapatkan:
1. Di VPS jalankan: cat ~/.ssh/id_rsa
2. Copy seluruh content (dari -----BEGIN hingga -----END)
3. Paste ke secret
```

**VPS_PORT**
```
Value: 22
```

### 3. Generate SSH Key di VPS (jika belum ada)
```bash
# Di VPS Hostinger
ssh-keygen -t rsa -b 4096 -C "deploy@crypto-api"
cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

### 4. Test SSH Connection
```bash
# Dari komputer lokal
ssh -i path/to/private_key root@YOUR_VPS_IP
```

## 🚀 Cara Kerja Auto Deploy

1. **Edit kode di Replit** → Save changes
2. **Push ke GitHub**:
   ```bash
   git add .
   git commit -m "Update: fitur baru trading signal"
   git push origin main
   ```
3. **GitHub Actions otomatis**:
   - Connect ke VPS via SSH
   - Pull latest code
   - Install dependencies
   - Restart service
   - Health check

## 📊 Monitoring Deployment

### Cek Status di GitHub
- Buka tab `Actions` di GitHub repository
- Lihat status deployment (✅ atau ❌)

### Cek di VPS
```bash
# Status service
systemctl status crypto-trading

# Logs real-time
journalctl -u crypto-trading -f

# Health check
curl http://localhost:5000/health
```

## 🔧 Troubleshooting

### Error: Permission denied (publickey)
```bash
# Di VPS, pastikan SSH key sudah benar
cat ~/.ssh/authorized_keys
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

### Error: Service failed to start
```bash
# Cek logs detail
journalctl -u crypto-trading --no-pager -l

# Restart manual
systemctl restart crypto-trading
```

### Error: Health check failed
```bash
# Cek apakah port 5000 listening
netstat -tlnp | grep 5000

# Cek logs aplikasi
tail -f /var/www/crypto-trading-api/logs/error.log
```

## ⚙️ Environment Variables di VPS

File: `/var/www/crypto-trading-api/.env`
```bash
# WAJIB DIISI
OKX_API_KEY=your-actual-okx-api-key
OKX_SECRET_KEY=your-actual-okx-secret-key  
OKX_PASSPHRASE=your-actual-okx-passphrase

OPENAI_API_KEY=your-actual-openai-api-key

TELEGRAM_BOT_TOKEN=your-actual-telegram-bot-token
TELEGRAM_CHAT_ID=your-actual-telegram-chat-id
```

## 🎯 Quick Commands

**Deploy Manual (jika perlu)**
```bash
cd /var/www/crypto-trading-api
./deploy.sh
```

**Restart Service**
```bash
sudo systemctl restart crypto-trading
```

**View Logs**
```bash
tail -f /var/www/crypto-trading-api/logs/error.log
```

**Check SSL Certificate**
```bash
certbot certificates
```

Setelah setup ini, Anda tinggal edit kode di Replit, push ke GitHub, dan aplikasi di VPS otomatis terupdate!