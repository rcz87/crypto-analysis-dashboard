# ChatGPT Custom GPT Setup Guide

## OpenAPI Schema URL ✅ CONFIRMED WORKING
Untuk mengintegrasikan API ini dengan ChatGPT Custom GPT, gunakan URL OpenAPI schema berikut:

```
https://[your-replit-app-url]/openapi.json
```

**Status: ✅ Endpoint telah dikonfirmasi berfungsi dan dapat diakses oleh ChatGPT Custom GPT**

Alternative endpoints:
- `/.well-known/openapi.json` 
- `/api-docs` (human-readable documentation)

## Langkah Setup di ChatGPT Custom GPT

### 1. Buat Custom GPT Baru
- Buka ChatGPT dan pilih "Create a GPT"
- Berikan nama: "Crypto Trading Analyst" 
- Deskripsi: "AI assistant untuk analisis trading cryptocurrency dengan Smart Money Concept"

### 2. Configure Actions
- Pilih tab "Configure" 
- Scroll ke bawah ke bagian "Actions"
- Klik "Create new action"

### 3. Import OpenAPI Schema
- Pilih "Import from URL" 
- Masukkan URL: `https://[your-replit-app-url]/openapi.json`
- Klik "Import"

### 4. Endpoint yang Tersedia

#### A. GET /api/gpts/signal
**Fungsi**: Mendapatkan sinyal trading cepat
**Parameter**:
- `symbol` (required): Pasangan trading (BTC/USDT, ETH/USDT, SOL/USDT)
- `tf` (optional): Timeframe (15m, 1h, 4h, 1d) - default: 1h

**Contoh Penggunaan**:
```
Berikan sinyal trading untuk BTC/USDT pada timeframe 1 jam
```

#### B. POST /api/gpts/sinyal/tajam
**Fungsi**: Analisis mendalam dengan naratif AI
**Body JSON**:
```json
{
  "symbol": "BTCUSDT",
  "timeframe": "1H", 
  "format": "both"
}
```

**Contoh Penggunaan**:
```
Lakukan analisis trading mendalam untuk Bitcoin dengan penjelasan lengkap
```

#### C. GET /api/gpts/status
**Fungsi**: Cek status kesehatan API

### 5. Authentication (Jika Diperlukan)
Saat ini API tidak memerlukan authentication untuk development. Untuk production, tambahkan API key di header.

### 6. Test Integration
Setelah setup selesai, test dengan pertanyaan:
```
Analisis sinyal trading untuk BTC/USDT hari ini
```

## Troubleshooting

### GPT Tidak Bisa Akses API
1. **Periksa URL**: Pastikan URL Replit app benar
2. **CORS Headers**: API sudah dikonfigurasi untuk ChatGPT origins
3. **OpenAPI Schema**: Pastikan endpoint `/openapi.json` dapat diakses

### Error Response
Jika mendapat error:
1. Cek status API di `/api/gpts/status`
2. Pastikan format parameter benar
3. Periksa log error di Replit console

## Custom GPT Instructions

Tambahkan instruksi berikut di bagian "Instructions":

```
Anda adalah ahli analisis trading cryptocurrency yang menggunakan Smart Money Concept (SMC) dan technical analysis. 

Kemampuan:
- Menganalisis sinyal BUY/SELL/NEUTRAL dengan confidence level
- Memberikan penjelasan dalam bahasa Indonesia yang mudah dipahami
- Menyediakan level stop loss dan take profit
- Menggunakan data real-time dari exchange OKX

Ketika user meminta analisis trading:
1. Gunakan action "get_trading_signal" untuk sinyal cepat
2. Gunakan action "get_detailed_analysis" untuk analisis mendalam
3. Selalu berikan penjelasan risk management
4. Format response dengan emoji dan struktur yang jelas

Contoh response format:
🚀 **SINYAL [BUY/SELL/NEUTRAL] - [SYMBOL]**
📊 **Confidence: [XX]%**
💰 **Entry: $[price]**
⛔ **Stop Loss: $[price]**  
🎯 **Take Profit: $[price1], $[price2]**
📝 **Analisis: [penjelasan singkat]**
```

## Testing Commands

Test dengan perintah berikut:
- "Analisis BTC hari ini"
- "Berikan sinyal trading untuk Ethereum"  
- "Bagaimana prospek SOL untuk trading?"
- "Cek kondisi market crypto sekarang"

## URL Deployment

Pastikan menggunakan URL deployment Replit yang benar:
```
https://[repl-name].[username].replit.app
```

Ganti `[repl-name]` dan `[username]` dengan nilai yang sesuai dari deployment Anda.