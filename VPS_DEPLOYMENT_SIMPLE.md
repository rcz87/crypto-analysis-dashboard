# 🚀 VPS DEPLOYMENT - LANGKAH MUDAH

## Yang Anda Butuhkan:
- VPS dengan Ubuntu/Debian
- IP VPS: 212.26.36.253 (atau IP VPS Anda)
- API Keys: OKX, OpenAI

## Langkah 1: SSH ke VPS
```bash
ssh root@212.26.36.253
```

## Langkah 2: Download & Run Setup Script
```bash
# Download setup script
wget https://raw.githubusercontent.com/rcz87/crypto-analysis-dashboard/main/vps-setup-complete.sh

# Beri permission
chmod +x vps-setup-complete.sh

# Jalankan setup
./vps-setup-complete.sh
```

## Langkah 3: Setup API Keys
```bash
cd crypto-analysis-dashboard
nano .env
```

**Edit file .env dengan API keys Anda:**
```
OKX_API_KEY=your_actual_okx_api_key
OKX_SECRET_KEY=your_actual_okx_secret_key
OKX_PASSPHRASE=your_actual_okx_passphrase
OPENAI_API_KEY=your_actual_openai_api_key
```

**Simpan dengan:** `Ctrl+X`, lalu `Y`, lalu `Enter`

## Langkah 4: Restart Containers
```bash
docker-compose -f docker-compose-vps.yml restart
```

## Langkah 5: Test Deployment
```bash
# Test dari dalam VPS
curl -X POST http://localhost:5000/api/gpts/sinyal/tajam \
  -H "Content-Type: application/json" \
  -d '{"symbol": "BTCUSDT", "timeframe": "1H"}'

# Test dari luar (ganti dengan IP VPS Anda)
curl -X POST http://212.26.36.253:5000/api/gpts/sinyal/tajam \
  -H "Content-Type: application/json" \
  -d '{"symbol": "BTCUSDT", "timeframe": "1H"}'
```

## URLs Setelah Deploy:
- **Main API**: `http://212.26.36.253:5000`
- **Trading Signals**: `http://212.26.36.253:5000/api/gpts/sinyal/tajam`
- **Health Check**: `http://212.26.36.253:5000/api/gpts/status`

## Troubleshooting:

### Jika containers tidak start:
```bash
docker-compose -f docker-compose-vps.yml logs
```

### Jika API keys salah:
```bash
nano .env  # Edit ulang
docker-compose -f docker-compose-vps.yml restart
```

### Jika port tidak bisa diakses:
```bash
# Buka firewall
ufw allow 5000
ufw allow 5050
```

## Ready untuk ChatGPT Custom GPTs!
Setelah berhasil, gunakan URL: `http://212.26.36.253:5000/api/gpts/sinyal/tajam` untuk ChatGPT integration.