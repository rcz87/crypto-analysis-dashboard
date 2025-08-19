#!/usr/bin/env python3
"""
Endpoint Discovery Tool
Menemu kan semua endpoint yang tersedia setelah blueprint registration
"""

import requests
import json
from typing import List, Dict

BASE_URL = "http://localhost:5000"

def test_endpoints():
    """Test berbagai endpoint untuk melihat yang available"""
    
    endpoints_to_test = [
        # Core GPTs endpoints (existing)
        ("GET", "/api/gpts/status"),
        ("GET", "/api/gpts/signal"),
        ("GET", "/api/gpts/market-data"),
        ("GET", "/health"),
        
        # Newly registered endpoints
        ("GET", "/api/backtest"),
        ("POST", "/api/backtest"),
        ("GET", "/api/backtest/strategies"),
        ("GET", "/api/backtest/quick"),
        
        ("GET", "/widget"),
        ("GET", "/dashboard"),
        ("GET", "/data"),
        
        ("POST", "/api/gpts/sinyal/enhanced"),
        ("GET", "/api/gpts/context/live"),
        ("GET", "/api/gpts/alerts/status"),
        
        ("POST", "/sharp"),
        ("GET", "/sharp/status"),
        ("POST", "/sharp/test"),
        
        ("POST", "/analyze"),
        ("GET", "/test"),
        
        ("GET", "/api/signal/top"),
        ("POST", "/api/signal/top/telegram"),
        
        ("POST", "/api/smc/patterns/recognize"),
        
        ("POST", "/track-signal"),
        ("GET", "/signal-history"),
        
        ("GET", "/liquidity-map"),
        ("GET", "/liquidation-heatmap"),
        ("GET", "/market-sentiment"),
        
        ("POST", "/auto-tune"),
        ("POST", "/retrain-model"),
        
        ("GET", "/api/signals/history"),
        ("GET", "/api/gpts/analysis/deep"),
        ("GET", "/api/smc/orderblocks"),
        
        ("GET", "/smc/analysis"),
        ("GET", "/trend/analysis"),
    ]
    
    available_endpoints = []
    unavailable_endpoints = []
    
    print("🔍 Testing All Registered Endpoints...")
    print("="*60)
    
    for method, endpoint in endpoints_to_test:
        try:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
            else:
                response = requests.post(f"{BASE_URL}{endpoint}", 
                                       json={"symbol": "BTC-USDT", "timeframe": "1H"}, 
                                       timeout=5)
            
            status = response.status_code
            if status == 404:
                unavailable_endpoints.append(f"{method} {endpoint}")
                print(f"❌ {method:4} {endpoint:40} [404 Not Found]")
            elif status in [200, 201, 400, 422, 500]:  # Available but may have errors
                available_endpoints.append(f"{method} {endpoint}")
                print(f"✅ {method:4} {endpoint:40} [{status}]")
            else:
                unavailable_endpoints.append(f"{method} {endpoint}")
                print(f"⚠️  {method:4} {endpoint:40} [{status}]")
                
        except requests.exceptions.RequestException as e:
            unavailable_endpoints.append(f"{method} {endpoint}")
            print(f"💥 {method:4} {endpoint:40} [ERROR: {str(e)[:30]}]")
    
    print("\n" + "="*60)
    print(f"📊 SUMMARY:")
    print(f"✅ Available: {len(available_endpoints)}")
    print(f"❌ Not Found: {len(unavailable_endpoints)}")
    print(f"🎯 Total Tested: {len(endpoints_to_test)}")
    
    print(f"\n🎉 AVAILABLE ENDPOINTS ({len(available_endpoints)}):")
    for endpoint in available_endpoints:
        print(f"   • {endpoint}")
    
    if unavailable_endpoints:
        print(f"\n❌ UNAVAILABLE ENDPOINTS ({len(unavailable_endpoints)}):")
        for endpoint in unavailable_endpoints:
            print(f"   • {endpoint}")
    
    return available_endpoints, unavailable_endpoints

if __name__ == "__main__":
    available, unavailable = test_endpoints()
    
    # Save results
    results = {
        "available_endpoints": available,
        "unavailable_endpoints": unavailable,
        "total_available": len(available),
        "total_unavailable": len(unavailable)
    }
    
    with open("endpoint_discovery_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results saved to endpoint_discovery_results.json")