"""
Prompt Book Manager untuk ChatGPT Custom GPT Context Initialization
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class PromptBookManager:
    """Manager untuk Prompt Book dan context initialization"""
    
    def __init__(self):
        self.prompt_book = self._load_default_prompt_book()
        logger.info("📚 Prompt Book Manager initialized")
    
    def _load_default_prompt_book(self) -> Dict[str, Any]:
        """Load default Prompt Book configuration"""
        return {
            "title": "🧠 Prompt Book – CryptoSage AI (Custom GPT)",
            "version": "1.0.0",
            "last_updated": datetime.now().isoformat(),
            "main_purpose": "Menggunakan GPT untuk melakukan analisis pasar crypto berbasis Smart Money Concept (SMC) dan indikator teknikal modern secara efisien, tanpa spekulasi, dengan integrasi penuh ke sistem backend berbasis API GPTs.",
            
            "system_integration": {
                "backend": "Flask API dengan 14 endpoint, 12 aktif",
                "data_source": "Real-time dari OKX API (via Redis & PostgreSQL)",
                "platform": "GPTs + Telegram bot",
                "supported_endpoints": [
                    "/api/gpts/signal", "/api/gpts/sinyal/tajam", "/api/gpts/indicators",
                    "/api/gpts/orderbook", "/api/gpts/market-depth", "/api/gpts/funding-rate",
                    "/api/news/latest", "/api/news/sentiment", "/api/backtest",
                    "/api/performance/stats", "/api/gpts/state/signal-history"
                ]
            },
            
            "supported_timeframes": [
                "1M", "3M", "5M", "15M", "30M", "1H", "2H", "4H", 
                "6H", "8H", "12H", "1D", "3D", "1W", "1Mo"
            ],
            
            "active_timeframes": ["5M", "15M", "1H", "4H", "1D"],
            
            "analysis_structure": {
                "required_fields": [
                    "Harga saat ini",
                    "Sinyal (BUY/SELL/NEUTRAL) + Confidence (%)",
                    "Trend (BULLISH/BEARISH/NEUTRAL)",
                    "Struktur SMC: BOS, CHoCH, OB, FVG, Liquidity",
                    "Indikator: RSI, MACD, Volume Trend",
                    "Risk Management: Entry, SL, TP, RR",
                    "Waktu Analisis",
                    "Rekomendasi Operasional (opsional)"
                ]
            },
            
            "user_preferences": {
                "language": "Bahasa Indonesia",
                "style": "Profesional, efisien, data-driven",
                "priorities": [
                    "Deteksi struktur SMC secara real-time",
                    "Tidak mengulang perintah sebelumnya",
                    "Tidak memberikan prediksi harga spekulatif",
                    "Tidak mengandalkan data mock",
                    "Gunakan data authentic dari OKX"
                ]
            },
            
            "recommended_tools": {
                "primary_endpoints": [
                    "/api/gpts/sinyal/tajam",
                    "/api/gpts/indicators", 
                    "/api/gpts/signal"
                ],
                "data_source": "Real OKX candle (200 terakhir)",
                "backend_compatibility": "GPTs-aware, OpenAPI 3.1.0, ChatGPT-ready response"
            },
            
            "restrictions": [
                "Jangan memberikan spekulasi harga tanpa data",
                "Jangan memprediksi arah tanpa confidence score",
                "Jangan mengulang logika/penjelasan perintah dasar yang sudah diberikan",
                "Selalu gunakan data authentic dari OKX Exchange"
            ],
            
            "context_instructions": """
            Jika sesi baru dimulai, gunakan endpoint /api/gpts/context/init untuk memuat konteks penuh.
            GPT akan langsung memahami preferensi analisis tanpa perlu perintah berulang.
            Sistem backend akan otomatis menyesuaikan response format sesuai Prompt Book ini.
            """
        }
    
    def get_prompt_book(self) -> Dict[str, Any]:
        """Get current Prompt Book configuration"""
        return self.prompt_book
    
    def update_prompt_book(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update Prompt Book with new configuration"""
        try:
            # Deep merge updates
            self._deep_merge(self.prompt_book, updates)
            self.prompt_book["last_updated"] = datetime.now().isoformat()
            
            logger.info("📚 Prompt Book updated successfully")
            return self.prompt_book
            
        except Exception as e:
            logger.error(f"Failed to update Prompt Book: {e}")
            raise
    
    def _deep_merge(self, target: Dict, source: Dict) -> Dict:
        """Deep merge two dictionaries"""
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._deep_merge(target[key], value)
            else:
                target[key] = value
        return target
    
    def get_context_initialization_prompt(self) -> str:
        """Generate context initialization prompt for GPT"""
        pb = self.prompt_book
        
        prompt = f"""# 🧠 {pb['title']}

## 📌 Tujuan Utama
{pb['main_purpose']}

---

## ⚙️ Sistem & Integrasi
- Backend: {pb['system_integration']['backend']}
- Data: {pb['system_integration']['data_source']}
- Platform: {pb['system_integration']['platform']}

**Endpoint Tersedia:**
{chr(10).join([f"- {endpoint}" for endpoint in pb['system_integration']['supported_endpoints']])}

---

## ⏱️ Timeframe yang Didukung
**Semua Timeframes:** {', '.join(pb['supported_timeframes'])}
**Aktif Digunakan:** {', '.join(pb['active_timeframes'])}

---

## 📊 Format Analisis Wajib
{chr(10).join([f"- {field}" for field in pb['analysis_structure']['required_fields']])}

---

## 🧠 Preferensi Pengguna
- **Bahasa:** {pb['user_preferences']['language']}
- **Gaya:** {pb['user_preferences']['style']}

**Prioritas:**
{chr(10).join([f"- {priority}" for priority in pb['user_preferences']['priorities']])}

---

## 🧰 Tools Utama
**Endpoint Utama:**
{chr(10).join([f"- {endpoint}" for endpoint in pb['recommended_tools']['primary_endpoints']])}

**Data Source:** {pb['recommended_tools']['data_source']}
**Backend:** {pb['recommended_tools']['backend_compatibility']}

---

## 🛑 Pantangan
{chr(10).join([f"- {restriction}" for restriction in pb['restrictions']])}

---

## 📝 Catatan Konteks
{pb['context_instructions']}

**Last Updated:** {pb['last_updated']}
**Version:** {pb['version']}
"""
        
        return prompt
    
    def get_system_status_for_gpt(self) -> Dict[str, Any]:
        """Get system status optimized for GPT understanding"""
        return {
            "system_ready": True,
            "data_source": "OKX Exchange (authentic)",
            "available_symbols": ["BTC-USDT", "ETH-USDT", "SOL-USDT", "BNB-USDT"],
            "timeframes_ready": self.prompt_book["supported_timeframes"],
            "analysis_capabilities": [
                "Smart Money Concept (SMC)",
                "Technical Indicators (RSI, MACD, etc)",
                "Order Flow Analysis",
                "Market Sentiment",
                "Risk Management"
            ],
            "response_language": self.prompt_book["user_preferences"]["language"],
            "confidence_based_signals": True,
            "real_time_data": True
        }
    
    def get_minimal_promptbook_response(self) -> Dict[str, Any]:
        """Get minimal prompt book response as requested"""
        pb = self.prompt_book
        
        return {
            "status": "success",
            "promptbook": {
                "purpose": pb["main_purpose"],
                "language": pb["user_preferences"]["language"],
                "style": pb["user_preferences"]["style"],
                "version": pb["version"],
                "last_updated": pb["last_updated"],
                "system_integration": {
                    "backend": pb["system_integration"]["backend"],
                    "data_source": pb["system_integration"]["data_source"],
                    "platform": pb["system_integration"]["platform"]
                },
                "timeframes": {
                    "supported": pb["supported_timeframes"],
                    "active": pb["active_timeframes"],
                    "total_count": len(pb["supported_timeframes"])
                },
                "analysis_requirements": pb["analysis_structure"]["required_fields"],
                "user_priorities": pb["user_preferences"]["priorities"],
                "restrictions": pb["restrictions"],
                "endpoints": {
                    "primary": pb["recommended_tools"]["primary_endpoints"],
                    "all_available": pb["system_integration"]["supported_endpoints"],
                    "context_init": "/api/gpts/context/init",
                    "management": "/api/gpts/context/prompt-book"
                },
                "features": {
                    "smc_analysis": True,
                    "technical_indicators": True,
                    "risk_management": True,
                    "indonesian_native": True,
                    "real_time_data": True,
                    "confidence_scoring": True,
                    "multi_timeframe": True
                }
            },
            "api_info": {
                "version": "1.0.0",
                "server_time": datetime.now().isoformat(),
                "service": "Cryptocurrency Trading Signals API"
            }
        }

# Global instance
prompt_book_manager = PromptBookManager()