# 🔧 Root User Deployment Guide

## Situasi Saat Ini
Anda login sebagai root di VPS dan script deployment menolak berjalan. Berikut solusinya:

## Option 1: Quick Root Deployment (Recommended)
```bash
# Run the root-specific deployment script
chmod +x deploy-vps-root.sh
./deploy-vps-root.sh
```

## Option 2: Create User & Deploy Properly
```bash
# 1. Create app user
useradd -m -s /bin/bash cryptoapp
usermod -aG sudo cryptoapp
usermod -aG docker cryptoapp

# 2. Copy project to user home
cp -r /root/crypto-analysis-dashboard /home/cryptoapp/
chown -R cryptoapp:cryptoapp /home/cryptoapp/crypto-analysis-dashboard

# 3. Switch to user and deploy
su - cryptoapp
cd crypto-analysis-dashboard
chmod +x deploy-vps.sh
./deploy-vps.sh
```

## Option 3: Override Security Check (Quick Fix)
```bash
# Edit the original script to skip root check
sed -i '17,21d' deploy-vps.sh
chmod +x deploy-vps.sh
./deploy-vps.sh
```

## Recommend: Use Option 1
Script `deploy-vps-root.sh` sudah saya buat khusus untuk handle deployment sebagai root dengan security measures yang proper.