# Cara Copy Script ke VPS Hostinger

## Metode 1: Copy-Paste Manual (Recommended)

### Langkah 1: Copy Script dari Replit
1. Buka file `final_vps_database_fix.sh` di Replit
2. Select All (Ctrl+A) dan Copy (Ctrl+C)

### Langkah 2: Paste ke VPS Hostinger
```bash
# Di VPS Hostinger, buka terminal dan jalankan:
cd /root/crypto-analysis-dashboard
nano final_vps_database_fix.sh

# Paste script content (Ctrl+Shift+V di terminal)
# Save file (Ctrl+X, then Y, then Enter)

# Make executable dan jalankan:
chmod +x final_vps_database_fix.sh
./final_vps_database_fix.sh
```

## Metode 2: SCP (Jika Ada Akses SSH dari Lokal)

```bash
# Dari computer lokal (bukan VPS):
scp final_vps_database_fix.sh root@YOUR_VPS_IP:/root/crypto-analysis-dashboard/
ssh root@YOUR_VPS_IP
cd /root/crypto-analysis-dashboard
chmod +x final_vps_database_fix.sh
./final_vps_database_fix.sh
```

## Metode 3: Create Script Directly di VPS

Karena Anda pakai VPS Hostinger, cara paling mudah adalah copy-paste manual.

### Script Singkat untuk VPS Hostinger:

```bash
# Jalankan di VPS Hostinger:
cd /root/crypto-analysis-dashboard

# Create quick fix script:
cat > quick_fix.sh << 'EOF'
#!/bin/bash
echo "VPS Hostinger Database Fix"
echo "=========================="

# Stop service
sudo systemctl stop cryptoapi.service

# Ask for Neon database URL
echo "Masukkan URL database Neon lengkap:"
read NEON_URL

# Update environment file
ENV_FILE="/root/crypto-analysis-dashboard/.env.production"
echo "DATABASE_URL=$NEON_URL" > $ENV_FILE
echo "SQLALCHEMY_DATABASE_URI=$NEON_URL" >> $ENV_FILE
echo "FLASK_ENV=production" >> $ENV_FILE
echo "API_KEY_REQUIRED=true" >> $ENV_FILE

# Update systemd service
sudo tee /etc/systemd/system/cryptoapi.service > /dev/null << EOL
[Unit]
Description=Cryptocurrency Trading API
After=network.target

[Service]
Type=notify
User=root
Group=root
WorkingDirectory=/root/crypto-analysis-dashboard
Environment=PATH=/root/crypto-analysis-dashboard/venv/bin
EnvironmentFile=$ENV_FILE
ExecStart=/root/crypto-analysis-dashboard/venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 4 main:app
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOL

# Restart service
sudo systemctl daemon-reload
sudo systemctl start cryptoapi.service

# Check status
sleep 3
curl -s http://localhost:5000/health
sudo systemctl status cryptoapi.service
EOF

chmod +x quick_fix.sh
./quick_fix.sh
```

## Yang Dibutuhkan:

1. **URL Database Neon** - Format seperti:
   ```
   postgresql://neondb_owner:PASSWORD@ep-billowing-sunset-xxxx.us-east-2.aws.neon.tech/neondb?sslmode=require
   ```

2. **Terminal VPS Hostinger** - Akses melalui:
   - Hostinger hPanel → VPS Management → Terminal
   - SSH client (PuTTY, Terminal, dll)

## Troubleshooting VPS Hostinger:

### Jika Environment File Tidak Ditemukan:
```bash
# Check current directory:
pwd
ls -la

# Find application directory:
find /root -name "main.py" 2>/dev/null
find /home -name "main.py" 2>/dev/null
```

### Jika Service Tidak Start:
```bash
# Check logs:
sudo journalctl -u cryptoapi.service -f

# Check permissions:
ls -la /root/crypto-analysis-dashboard/
```

### Jika Port 5000 Tidak Accessible:
```bash
# Check if port is blocked:
sudo ufw status
sudo ufw allow 5000

# Check if service is listening:
netstat -tlnp | grep 5000
```

## Setelah Fix Berhasil:

Test endpoints Anda:
```bash
# Health check:
curl http://YOUR_VPS_IP:5000/health

# API endpoints:
curl -H "X-API-KEY: your-api-key" http://YOUR_VPS_IP:5000/api/gpts/status
```

## Tips untuk VPS Hostinger:

1. **Backup otomatis** - Hostinger punya snapshot features
2. **Monitor resource** - Check memory/CPU usage
3. **DNS Setup** - Point domain ke VPS IP
4. **SSL Certificate** - Use Let's Encrypt via cPanel
5. **Firewall** - Configure di Hostinger panel