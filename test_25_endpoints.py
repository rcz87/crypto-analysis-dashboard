#!/usr/bin/env python3
# EXACT 25 (diselaraskan dgn skema yang kita ekstrak)
import time, json, sys, requests
from typing import Dict, Any

BASE_URL = "http://localhost:5000"
SYMBOL = "SOL-USDT"
TIMEOUT = 30

EXACT_25 = [
    # ==== CORE / STATUS ====
    ("GET", "/"),  # kalau tidak ada, ganti dengan /api/gpts/status
    ("GET", "/api/gpts/health"),
    ("GET", "/api/gpts/status"),

    # ==== REALTIME / DATA ====
    # ticker: jika skema kamu pakai query, gunakan /api/gpts/ticker?symbol=...
    ("GET", f"/api/gpts/ticker/{SYMBOL}"),
    # orderbook: banyak skema pakai query, sediakan fallback di overrides
    ("GET", f"/api/gpts/orderbook/{SYMBOL}"),

    # ==== HISTORICAL & ANALYSIS (POST yang benar) ====
    ("POST", "/api/gpts/market-data"),
    ("POST", "/api/gpts/analysis"),

    # ==== SIGNALS ====
    ("GET", "/api/gpts/signal"),          # quick rule-based
    ("GET", "/api/gpts/sinyal/tajam"),    # narrative/advanced
    # SMC: wajib POST untuk analisa & zones
    ("POST", "/api/gpts/smc-analysis"),
    ("POST", "/api/gpts/smc-zones"),

    # ==== INDICATORS / FUNDING / DEPTH (GET dgn query) ====
    ("GET", "/api/gpts/indicators"),
    ("GET", "/api/gpts/funding-rate"),
    ("GET", "/api/gpts/market-depth"),
    ("GET", "/api/gpts/state/signal-history"),

    # ==== NEWS ====
    ("GET", "/api/news/latest"),
    ("GET", "/api/news/sentiment"),

    # ==== PERFORMANCE ====
    ("GET", "/api/performance/stats"),
    ("GET", "/api/performance/equity-curve"),
    ("POST", "/api/performance/backtest"),
    ("GET", "/api/performance/detailed-report"),

    # ==== PROMPTBOOK / CONTEXT / SMC overview ====
    ("GET", "/api/promptbook/"),
    ("GET", "/api/promptbook/status"),
    ("GET", "/api/smc/summary"),

    # ==== OPENAPI SCHEMA ====
    ("GET", "/api/openapi_schema"),
]

# Override payload & query yang cocok dengan sistemmu
PAYLOAD = {
    "/api/gpts/market-data": {"symbol": SYMBOL, "tf": "1h", "limit": 300},
    "/api/gpts/analysis": {"symbol": SYMBOL, "tf": "4h"},
    "/api/gpts/smc-analysis": {"symbol": SYMBOL, "tfs": ["1m","5m","15m","1h"],
                               "features": ["BOS","CHOCH","OB","FVG","LIQ_SWEEP"]},
    "/api/gpts/smc-zones": {"symbol": SYMBOL, "tfs": ["5m","15m","1h"]},
    "/api/performance/backtest": {"symbol": SYMBOL, "tf": "1h", "lookback": 300},
}

QUERY = {
    "/api/gpts/sinyal/tajam": {"symbol": SYMBOL, "tf": "1h", "format": "json"},
    "/api/gpts/signal": {"symbol": SYMBOL, "tf": "15m"},
    # Jika server kamu bentuknya bukan path param utk ticker/orderbook:
    # "/api/gpts/ticker": {"symbol": SYMBOL},
    # "/api/gpts/orderbook": {"symbol": SYMBOL, "depth": 400},
    "/api/gpts/indicators": {"symbol": SYMBOL, "tf": "1h"},
    "/api/gpts/funding-rate": {"symbol": SYMBOL},
    "/api/gpts/market-depth": {"symbol": SYMBOL, "limit": 400},
    "/api/gpts/state/signal-history": {"symbol": SYMBOL},
    "/api/news/latest": {"symbol": SYMBOL, "limit": 3},
    "/api/news/sentiment": {"symbol": SYMBOL},
    "/api/performance/equity-curve": {"symbol": SYMBOL},
    "/api/performance/detailed-report": {"symbol": SYMBOL},
}

def build_url(base, path):
    if path in QUERY:
        q = "&".join([f"{k}={v}" for k, v in QUERY[path].items()])
        sep = "&" if "?" in path else "?"
        return f"{base}{path}{sep}{q}"
    return f"{base}{path}"

def run(base):
    assert len(EXACT_25) == 25, f"List sekarang {len(EXACT_25)}; pastikan tepat 25."
    passed = failed = 0
    for i, (method, path) in enumerate(EXACT_25, 1):
        url = build_url(base, path)
        t0 = time.time()
        try:
            if method == "GET":
                r = requests.get(url, timeout=TIMEOUT)
            else:
                payload = PAYLOAD.get(path, {"symbol": SYMBOL})
                r = requests.post(url, json=payload, timeout=TIMEOUT)
            ms = (time.time()-t0)*1000
            ok = (r.status_code == 200)
            try:
                sample = r.json()
            except:
                sample = r.text[:200]
            print(f"[{i:2d}/25] {method:4} {path:<40} {'✅' if ok else '❌'} {ms:6.1f}ms [{r.status_code}]")
            if ok: passed += 1
            else: failed += 1
        except Exception as e:
            ms = (time.time()-t0)*1000
            failed += 1
            print(f"[{i:2d}/25] {method:4} {path:<40} ❌ {ms:6.1f}ms [EXC] {e}")
    print(f"\nResult: Passed={passed} Failed={failed}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        BASE_URL = sys.argv[1]
    run(BASE_URL)