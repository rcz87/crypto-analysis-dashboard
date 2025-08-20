# ENDPOINT STABILITY GUARANTEE

## User Issue Summary
User frustrated bahwa **setiap perbaikan endpoint selalu berubah nama**:
- Kemarin: 25 endpoint + 10 aktif semua  
- Sekarang: Nama beda lagi, tidak konsisten
- **Problem**: Auto-discovery system mengubah-ubah nama endpoint

## Solution Implemented (August 20, 2025)

### 🔒 Fixed Blueprint Registry
- **Replaced**: Auto-discovery system yang tidak stabil
- **Implemented**: Manual registry di `routes.py` lines 208-249
- **Guarantee**: Endpoint names tidak akan berubah lagi

### 📋 Current Stable State
- **25/27 blueprints** registered consistently  
- **19 endpoint categories** stable
- **Registry locked** untuk mencegah perubahan

### 🎯 Stable Endpoint Categories
```
/api/ai-reasoning/*          # AI reasoning & enhanced analysis
/api/analysis/improvements/* # System improvements
/api/analysis/modular/*      # Modular endpoints  
/api/backtest/*              # Backtesting tools
/api/charts/*                # Chart analysis
/api/coinglass/*             # Coinglass integration
/api/data-quality/*          # Data quality management
/api/gpts/*                  # Core GPTs integration
/api/gpts/coinglass/*        # GPTs + Coinglass
/api/gpts/enhanced/*         # Enhanced GPTs features
/api/gpts/missing/*          # Missing GPTs endpoints
/api/institutional/*         # Institutional analysis
/api/news/*                  # News analysis
/api/optimization/*          # Advanced optimization
/api/performance/*           # Performance monitoring
/api/performance/advanced/*  # Advanced performance
/api/promptbook/*            # Prompt management
/api/security/*              # Security features
/api/signals/enhanced/*      # Enhanced trading signals
/api/signals/sharp/*         # Sharp signal analysis
/api/signals/scoring/*       # Signal scoring
/api/signals/top/*           # Top signals
/api/smc-zones/*            # SMC zones analysis
/api/telegram/*             # Telegram integration
/api/webhooks/*             # Webhook management
/health                     # System health
```

## Registry Maintenance Rules

### ✅ DO (Allowed)
- Add new endpoints to the stable registry
- Fix broken blueprint imports  
- Update URL prefixes for better organization

### ❌ DON'T (Forbidden without user approval)
- Remove existing working endpoints
- Change endpoint names/prefixes arbitrarily
- Switch back to auto-discovery system
- Modify registry order unless necessary

## Verification System
- **Stability Lock**: `endpoint_stability_lock.py` monitors changes
- **Golden State**: Current 25/27 blueprints as standard
- **Consistency Check**: Automated verification available

## User Communication
- **Language**: Simple, everyday language (per replit.md)
- **Updates**: Only notify about improvements, not changes that break compatibility
- **Guarantee**: "Endpoint names akan tetap sama dan tidak berubah lagi"

---

**COMMITMENT**: Sistem endpoint sekarang LOCKED dan tidak akan berubah-ubah lagi tanpa persetujuan user.