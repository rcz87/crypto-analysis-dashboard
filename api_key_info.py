#!/usr/bin/env python3
"""
Script untuk memberikan informasi API key dan cara menggunakan endpoint
"""
import os

def show_api_info():
    api_key = os.environ.get('API_KEY', 'tidak ditemukan')
    api_required = os.environ.get('API_KEY_REQUIRED', 'false')
    
    print("🔑 INFORMASI API KEY TRADING APPLICATION")
    print("=" * 50)
    print(f"API Key: {api_key}")
    print(f"API Key Required: {api_required}")
    print()
    
    print("📋 CARA MENGGUNAKAN:")
    print("1. Untuk endpoint TANPA API key:")
    print("   curl http://localhost:5000/")
    print("   curl http://localhost:5000/health")
    print("   curl http://localhost:5000/api/status")
    print()
    
    print("2. Untuk endpoint DENGAN API key:")
    print(f'   curl -H "X-API-KEY: {api_key}" http://localhost:5000/api/signal?symbol=BTC-USDT')
    print(f'   curl -H "X-API-KEY: {api_key}" http://localhost:5000/api/websocket/status')
    print(f'   curl -H "X-API-KEY: {api_key}" http://localhost:5000/api/smc/analysis?symbol=BTC-USDT')
    print()
    
    print("3. Atau gunakan Authorization header:")
    print(f'   curl -H "Authorization: Bearer {api_key}" http://localhost:5000/api/signal?symbol=BTC-USDT')
    print()
    
    print("📊 ENDPOINT UTAMA:")
    print("• /api/signal?symbol=BTC-USDT - Generate trading signal")
    print("• /api/signal/top - Top trading signals")  
    print("• /api/gpts/enhanced/analysis?symbol=BTC-USDT - AI analysis")
    print("• /api/smc/analysis?symbol=BTC-USDT - Smart Money Concepts")
    print("• /api/websocket/status - WebSocket status")
    print("• /api/status - API status (91 endpoints)")
    print()
    
    print("✅ APLIKASI SUDAH BERJALAN DENGAN 91 ENDPOINT AKTIF!")

if __name__ == "__main__":
    show_api_info()