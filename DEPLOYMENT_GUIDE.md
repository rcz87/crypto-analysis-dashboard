# 🚀 REPLIT DEPLOYMENT GUIDE - MUDAH & CEPAT

## Step 1: Siapkan Secrets (API Keys)

**Klik "Secrets" di sidebar kiri Replit, lalu tambahkan:**

```
OKX_API_KEY = your_okx_api_key
OKX_SECRET_KEY = your_okx_secret_key  
OKX_PASSPHRASE = your_okx_passphrase
OPENAI_API_KEY = your_openai_api_key
```

**Optional (untuk Telegram):**
```
TELEGRAM_BOT_TOKEN = your_bot_token
ADMIN_CHAT_ID = your_chat_id
```

## Step 2: Deploy ke Replit Deployments

### Opsi A: Pakai Button Deploy (Mudah)
1. Klik tombol **"Deploy"** di header Replit
2. Pilih **"Autoscale Deployment"**
3. Build Command: `pip install -r requirements-prod.txt`
4. Run Command: `python run.py`
5. Klik **"Deploy"**

### Opsi B: Manual Configuration
1. Masuk ke Deployments tab
2. Create New Deployment
3. Settings:
   - **Type**: Autoscale Deployment
   - **Build**: `pip install -r requirements-prod.txt`
   - **Run**: `python run.py`
   - **Port**: Otomatis (gunakan $PORT)

## Step 3: Database Setup (Otomatis)

Replit akan otomatis:
- Setup PostgreSQL database
- Provide `DATABASE_URL` environment variable
- Create tables saat first run

## Step 4: Test Deployment

Setelah deploy berhasil, test endpoint:

```bash
curl -X POST https://your-app.replit.app/api/gpts/sinyal/tajam \
  -H "Content-Type: application/json" \
  -d '{"symbol": "BTCUSDT", "timeframe": "1H"}'
```

## Endpoints Available:

- `GET /api/gpts/status` - Health check
- `POST /api/gpts/sinyal/tajam` - Trading signals
- `GET /api/gpts/chart` - Chart data
- `POST /api/gpts/telegram/test` - Test notifications

## Expected Response:

```json
{
  "signal": {
    "final_signal": {
      "action": "BUY/SELL/NEUTRAL",
      "confidence": 85.5
    },
    "xai_explanation": {
      "explanation": "Analisis lengkap dalam Bahasa Indonesia"
    }
  },
  "api_version": "1.0.0"
}
```

## Troubleshooting:

**Jika deployment gagal:**
1. Check Secrets sudah benar
2. Lihat Logs di Deployments tab
3. Pastikan OKX API keys valid

**Jika 500 error:**
- Check environment variables
- Verify database connection
- Check logs untuk error details

## Ready untuk ChatGPT Custom GPTs! 🎯

Setelah deploy, gunakan URL deployment untuk ChatGPT Custom GPTs integration.