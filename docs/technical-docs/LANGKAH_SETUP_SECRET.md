# 🔐 LANGKAH SETUP GITHUB SECRET DI REPLIT

## Panduan Visual Step-by-Step

---

## 📋 LANGKAH 1: AKSES REPLIT SECRETS

1. **Di workspace Replit Anda saat ini**
2. **Lihat sidebar kiri** - ada beberapa tab/icon
3. **Cari dan klik tab "Secrets"** (biasanya icon gembok 🔒)
4. Jika tidak terlihat, coba scroll atau expand sidebar

---

## 🔑 LANGKAH 2: TAMBAH SECRET BARU

Di halaman Secrets:
1. **Klik tombol "Add Secret"** atau "Add a new secret"
2. **Isi field berikut:**
   - **Key**: `GITHUB_TOKEN`
   - **Value**: [Paste GitHub token Anda disini]
3. **Klik "Save"** atau "Add secret"

---

## ✅ LANGKAH 3: VERIFIKASI SECRET

Setelah secret tersimpan, jalankan di Shell untuk test:
```bash
# Test apakah secret tersimpan
echo "Secret status: ${GITHUB_TOKEN:+AVAILABLE}"
```

---

## 🚀 LANGKAH 4: SETUP GIT DAN PUSH

Setelah secret tersimpan:
```bash
# Setup remote dengan secret
git remote set-url origin https://$GITHUB_TOKEN@github.com/rcz87/crypto-analysis-dashboard.git

# Push semua commits ke GitHub
git push origin main
```

---

## 📊 YANG AKAN DI-PUSH

**26 commits** institutional-grade system:
- ✅ Data Sanity Checker (comprehensive validation)
- ✅ Self-Improvement Engine (ML automation)
- ✅ Enhanced Signal Processing
- ✅ Circuit Breaker Protection
- ✅ Professional Telegram Integration
- ✅ Complete Testing Suite (15/15 pass)
- ✅ Full Documentation

---

## 🔧 TROUBLESHOOTING

**Jika tidak menemukan tab Secrets:**
- Coba refresh halaman Replit
- Pastikan Anda di workspace yang benar
- Secrets biasanya di sidebar kiri bersama Files, Console, dll

**Jika secret tidak tersimpan:**
- Pastikan tidak ada spasi di awal/akhir token
- Token harus valid dan belum expired
- Coba logout/login kembali ke Replit

---

**Ready untuk mulai? Buka tab Secrets di Replit dan ikuti langkah-langkah di atas!**