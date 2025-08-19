#!/usr/bin/env python3
"""
Quick Endpoint Tester - Script cepat untuk test endpoint utama
Gunakan: python quick_test.py [symbol]
"""

import sys
import requests
import time
from datetime import datetime

BASE_URL = "http://localhost:5000"
DEFAULT_SYMBOL = "SOL-USDT"

def quick_test(symbol=DEFAULT_SYMBOL):
    """Test cepat endpoint utama"""
    print(f"🚀 Quick Test Endpoint - {symbol}")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    tests = [
        ("Health Check", "GET", "/health"),
        ("System Status", "GET", "/api/gpts/status"),
        ("Ticker Real-time", "GET", f"/api/gpts/ticker/{symbol}"),
        ("Market Data", "GET", f"/api/gpts/market-data?symbol={symbol}&timeframe=1H&limit=10"),
        ("SMC Analysis", "GET", f"/api/gpts/smc-analysis?symbol={symbol}&timeframe=1H"),
        ("Signal Tajam", "POST", "/api/gpts/sinyal/tajam", {"symbol": symbol, "timeframe": "1H"}),
        ("Trading Signal", "GET", f"/api/gpts/signal?symbol={symbol}&timeframe=1H")
    ]
    
    passed = 0
    for name, method, endpoint, *payload in tests:
        try:
            url = BASE_URL + endpoint
            start_time = time.time()
            
            if method == "POST":
                response = requests.post(url, json=payload[0] if payload else {}, timeout=10)
            else:
                response = requests.get(url, timeout=10)
                
            duration = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                print(f"✅ {name:<20} {duration:>6.1f}ms")
                passed += 1
            else:
                print(f"❌ {name:<20} HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ {name:<20} ERROR: {str(e)[:30]}")
    
    print("=" * 50)
    print(f"📊 Result: {passed}/{len(tests)} endpoint berhasil ({passed/len(tests)*100:.1f}%)")
    
    if passed == len(tests):
        print("🎉 Semua endpoint berjalan sempurna!")
    elif passed >= len(tests) * 0.8:
        print("😊 Sebagian besar endpoint berjalan baik")
    else:
        print("⚠️  Ada beberapa endpoint yang perlu diperbaiki")

if __name__ == "__main__":
    symbol = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_SYMBOL
    quick_test(symbol)