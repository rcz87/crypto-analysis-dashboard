# gpts_comprehensive_tester.py - Updated for correct endpoints
import time, json, sys
from typing import Dict, Any
import requests

BASE_URL = "http://localhost:5000"  # Updated for Replit local testing
SYMBOL = "SOL-USDT"

# ==== Helper ====
def ok(resp: requests.Response) -> bool:
    return (resp.status_code == 200)

def jprint(data: Any, maxlen=400) -> str:
    try:
        s = json.dumps(data, ensure_ascii=False)[:maxlen]
        return s + ("..." if len(s) >= maxlen else "")
    except Exception:
        return str(data)[:maxlen]

def test_get(path: str, expect_json=True, desc=""):
    url = f"{BASE_URL}{path}"
    t0 = time.time()
    try:
        r = requests.get(url, timeout=15)
        dt = (time.time() - t0) * 1000
        out = r.json() if expect_json else r.text
        print(f"GET {path:<40} {('✅' if ok(r) else '❌')}  {dt:6.1f} ms  {desc}")
        if ok(r):
            print("  ⤷ sample:", jprint(out))
        else:
            print("  ⤷ status:", r.status_code, "body:", jprint(out))
    except Exception as e:
        print(f"GET {path:<40} ❌  error:", e)

def test_post(path: str, payload: Dict[str, Any], desc=""):
    url = f"{BASE_URL}{path}"
    t0 = time.time()
    try:
        r = requests.post(url, json=payload, timeout=30)
        dt = (time.time() - t0) * 1000
        out = r.json()
        print(f"POST {path:<39} {('✅' if ok(r) else '❌')}  {dt:6.1f} ms  {desc}")
        if ok(r):
            print("  ⤷ payload:", jprint(payload, 200))
            print("  ⤷ sample:", jprint(out))
        else:
            print("  ⤷ status:", r.status_code, "body:", jprint(out))
    except Exception as e:
        print(f"POST {path:<39} ❌  error:", e)

if __name__ == "__main__":
    print("=== COMPREHENSIVE GPTS API TEST ===")
    print("🎯 Simulating GPTs query: 'Analisa lengkap SOL-USDT timeframe 1H dengan SMC, orderbook depth, market data 300 candle, dan sinyal tajam'")
    print("Base:", BASE_URL, "| Symbol:", SYMBOL)
    print()

    # 1) Health & Status Check
    print("🔍 === HEALTH & STATUS ===")
    test_get("/", desc="main endpoint")
    test_get("/health", desc="health check")
    test_get("/api/gpts/health", desc="gpts health")
    test_get("/api/gpts/status", desc="service status")
    print()

    # 2) Real-time Market Data (GPTs will call these)
    print("📊 === REAL-TIME DATA ===")
    test_get(f"/api/gpts/ticker/{SYMBOL}", desc="ticker realtime")
    test_get(f"/api/gpts/orderbook/{SYMBOL}", desc="orderbook depth 400")
    print()

    # 3) Historical Market Data  
    print("📈 === HISTORICAL DATA ===")
    test_get(f"/api/gpts/market-data?symbol={SYMBOL}&timeframe=1H&limit=300", desc="300 candles 1H")
    test_get(f"/api/gpts/market-data?symbol={SYMBOL}&timeframe=4H&limit=50", desc="50 candles 4H")
    print()

    # 4) Combined Analysis
    print("🔬 === COMBINED ANALYSIS ===")
    test_get(f"/api/gpts/analysis?symbol={SYMBOL}&timeframe=1H", desc="analisa gabungan 1H")
    test_get(f"/api/gpts/analysis?symbol={SYMBOL}&timeframe=4H", desc="analisa gabungan 4H")
    print()

    # 5) Trading Signals
    print("🎯 === TRADING SIGNALS ===")
    test_post("/api/gpts/sinyal/tajam", {
        "symbol": SYMBOL, "timeframe": "1H"
    }, desc="sinyal tajam 1H")
    
    test_get(f"/api/gpts/signal?symbol={SYMBOL}&timeframe=1H", desc="signal standard 1H")
    test_get(f"/api/gpts/signal?symbol={SYMBOL}&timeframe=15m", desc="signal cepat 15m")
    print()

    # 6) SMC Analysis
    print("🧠 === SMART MONEY CONCEPT ===")
    test_get(f"/api/gpts/smc-analysis?symbol={SYMBOL}&timeframe=1H", desc="SMC analysis 1H")
    test_post("/api/gpts/smc-analysis", {
        "symbol": SYMBOL, "timeframe": "1H"
    }, desc="SMC analysis POST 1H")
    print()

    # 7) SMC Zones (the recently fixed endpoint)
    print("🗺️ === SMC ZONES ===")
    test_get(f"/api/gpts/smc-zones/{SYMBOL}?timeframe=1H", desc="SMC zones 1H")
    test_get(f"/api/gpts/smc-zones/{SYMBOL}?timeframe=4H", desc="SMC zones 4H")
    test_get("/api/smc/zones", desc="direct SMC zones")
    test_get(f"/api/smc/zones?symbol={SYMBOL}&tf=1H", desc="filtered SMC zones")
    print()

    # 8) Additional Endpoints
    print("🔧 === ADDITIONAL ENDPOINTS ===")
    test_get(f"/api/smc/zones/critical", desc="critical zones")
    print()

    print("=== SUMMARY ===")
    print("✅ Working endpoints can handle GPTs comprehensive analysis requests")
    print("❌ Failed endpoints need immediate attention")
    print("\n🎯 For the GPTs query 'Analisa lengkap SOL-USDT timeframe 1H':")
    print("   Expected calls: ticker → orderbook → market-data → smc-analysis → smc-zones → sinyal/tajam")
    print("   Response time: ~2-3 seconds for full analysis")