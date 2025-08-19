#!/usr/bin/env python3
"""
Cross Check Schema vs Available Endpoints
Memastikan SEMUA endpoint available sudah masuk schema
"""

import requests
import json
from typing import List, Set

BASE_URL = "http://localhost:5000"

def get_available_endpoints() -> Set[str]:
    """Get all available endpoints by testing them"""
    test_endpoints = [
        # Core GPTs endpoints
        "GET /api/gpts/status",
        "GET /api/gpts/signal", 
        "GET /api/gpts/market-data",
        "GET /health",
        
        # Backtest endpoints
        "GET /api/backtest",
        "POST /api/backtest", 
        "GET /api/backtest/strategies",
        "GET /api/backtest/quick",
        
        # Chart endpoints
        "GET /widget",
        "GET /dashboard", 
        "GET /data",
        
        # Enhanced GPTs
        "POST /api/gpts/sinyal/enhanced",
        "GET /api/gpts/context/live",
        "GET /api/gpts/alerts/status",
        
        # Signal endpoints
        "GET /api/signal/top",
        "GET /api/signals/history",
        "GET /api/gpts/analysis/deep",
        
        # SMC endpoints
        "POST /api/smc/patterns/recognize",
        "GET /api/smc/orderblocks",
        
        # Additional services
        "GET /api/promptbook/",
        "GET /api/performance/stats",
        "GET /api/news/status",
        
        # Original GPTs endpoints
        "POST /api/gpts/sinyal/tajam",
        "GET /api/gpts/ticker/BTC-USDT",
        "GET /api/gpts/orderbook/BTC-USDT",
        "GET /api/gpts/smc-analysis",
        "GET /api/gpts/smc-zones/BTC-USDT",
        "GET /api/smc/zones",
    ]
    
    available = set()
    print("🔍 Testing endpoint availability...")
    
    for endpoint in test_endpoints:
        method, path = endpoint.split(" ", 1)
        try:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{path}", timeout=3)
            else:
                response = requests.post(f"{BASE_URL}{path}", 
                                       json={"symbol": "BTC-USDT"}, timeout=3)
            
            # Consider 200, 400, 422, 500 as "available" (endpoint exists)
            if response.status_code != 404:
                available.add(endpoint)
                print(f"✅ {endpoint}")
            else:
                print(f"❌ {endpoint} - Not Found")
                
        except Exception as e:
            print(f"⚠️ {endpoint} - Error: {str(e)[:30]}")
    
    return available

def get_schema_endpoints() -> Set[str]:
    """Get all endpoints from OpenAPI schema"""
    try:
        response = requests.get(f"{BASE_URL}/openapi.json", timeout=5)
        if response.status_code != 200:
            print(f"❌ Failed to get schema: {response.status_code}")
            return set()
            
        schema = response.json()
        schema_endpoints = set()
        
        print("\n📋 Schema endpoints:")
        for path, methods in schema['paths'].items():
            for method, details in methods.items():
                endpoint = f"{method.upper()} {path}"
                schema_endpoints.add(endpoint)
                print(f"✅ {endpoint} ({details.get('operationId', 'no-id')})")
        
        return schema_endpoints
        
    except Exception as e:
        print(f"❌ Schema error: {e}")
        return set()

def cross_check():
    """Cross check available vs schema endpoints"""
    print("="*80)
    print("🔍 CROSS CHECK: Available Endpoints vs Schema")
    print("="*80)
    
    available = get_available_endpoints()
    schema = get_schema_endpoints()
    
    print(f"\n📊 SUMMARY:")
    print(f"Available endpoints: {len(available)}")
    print(f"Schema endpoints: {len(schema)}")
    
    # Check missing from schema
    missing_from_schema = available - schema
    if missing_from_schema:
        print(f"\n❌ MISSING FROM SCHEMA ({len(missing_from_schema)}):")
        for endpoint in sorted(missing_from_schema):
            print(f"   • {endpoint}")
    else:
        print(f"\n✅ ALL AVAILABLE ENDPOINTS ARE IN SCHEMA!")
    
    # Check extra in schema (endpoints in schema but not available)
    extra_in_schema = schema - available
    if extra_in_schema:
        print(f"\n⚠️ EXTRA IN SCHEMA ({len(extra_in_schema)}):")
        print("(These might be parameterized endpoints)")
        for endpoint in sorted(extra_in_schema):
            print(f"   • {endpoint}")
    
    # Coverage calculation
    if available:
        coverage = (len(available & schema) / len(available)) * 100
        print(f"\n📈 COVERAGE: {coverage:.1f}% of available endpoints in schema")
    
    # Final status
    if not missing_from_schema:
        print(f"\n🎉 STATUS: PERFECT! All available endpoints are in schema")
        return True
    else:
        print(f"\n⚠️ STATUS: {len(missing_from_schema)} endpoints need to be added to schema")
        return False

if __name__ == "__main__":
    is_complete = cross_check()
    
    result = {
        "timestamp": "2025-08-19",
        "complete": is_complete,
        "missing_count": 0 if is_complete else "check output"
    }
    
    with open("schema_cross_check.json", "w") as f:
        json.dump(result, f, indent=2)
    
    print(f"\n💾 Results saved to schema_cross_check.json")