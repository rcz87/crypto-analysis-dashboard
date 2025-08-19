# gpts_api_tester.py
import time, json, sys
from typing import Dict, Any
import requests

BASE_URL = "http://localhost:5000"  # Updated for Replit local testing
SYMBOL = "SOL-USDT"

# ==== Helper ====
def ok(resp: requests.Response) -> bool:
    return (resp.status_code == 200)

def jprint(data: Any, maxlen=500) -> str:
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
        print(f"GET {path:<35} {('✅' if ok(r) else '❌')}  {dt:6.1f} ms  {desc}")
        if ok(r):
            print("  ⤷ sample:", jprint(out))
        else:
            print("  ⤷ status:", r.status_code, "body:", jprint(out))
    except Exception as e:
        print(f"GET {path:<35} ❌  error:", e)

def test_post(path: str, payload: Dict[str, Any], desc=""):
    url = f"{BASE_URL}{path}"
    t0 = time.time()
    try:
        r = requests.post(url, json=payload, timeout=30)
        dt = (time.time() - t0) * 1000
        out = r.json()
        print(f"POST {path:<34} {('✅' if ok(r) else '❌')}  {dt:6.1f} ms  {desc}")
        if ok(r):
            print("  ⤷ payload:", jprint(payload))
            print("  ⤷ sample:", jprint(out))
        else:
            print("  ⤷ status:", r.status_code, "body:", jprint(out))
    except Exception as e:
        print(f"POST {path:<34} ❌  error:", e)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        BASE_URL = sys.argv[1]  # allow override via CLI

    print("=== GPTS API Smoke Test ===")
    print("Base:", BASE_URL, "| Symbol:", SYMBOL)
    print()

    # 1) Health & Status
    test_get("/api/gpts/health", desc="liveness")
    test_get("/api/gpts/status", desc="service status")

    # 2) Realtime data
    test_get(f"/api/gpts/ticker/{SYMBOL}", desc="ticker realtime")
    test_get(f"/api/gpts/orderbook/{SYMBOL}", desc="orderbook depth 400")

    # 3) Historical market data (candles)
    test_post("/api/gpts/market-data", {
        "symbol": SYMBOL, "tf": "1h", "limit": 300
    }, desc="candles 1h x300")

    # 4) Analisa gabungan
    test_post("/api/gpts/analysis", {
        "symbol": SYMBOL, "tf": "4h"
    }, desc="ringkasan analisa")

    # 5) Sinyal
    test_get(f"/api/gpts/sinyal/tajam?symbol={SYMBOL}&tf=1h&format=json",
             desc="sinyal tajam")
    test_get(f"/api/gpts/signal?symbol={SYMBOL}&tf=15m",
             desc="signal cepat")

    # 6) SMC
    test_post("/api/gpts/smc-zones", {
        "symbol": SYMBOL, "tfs": ["5m","15m","1h"]
    }, desc="zona OB/FVG/demand-supply")

    test_post("/api/gpts/smc-analysis", {
        "symbol": SYMBOL,
        "tfs": ["1m","5m","15m","1h"],
        "features": ["BOS","CHOCH","OB","FVG","LIQ_SWEEP"]
    }, desc="analisa SMC lengkap")

    print("\n=== Selesai. Periksa baris yang ❌ untuk dibenahi. ===")