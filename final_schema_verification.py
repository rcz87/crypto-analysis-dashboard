#!/usr/bin/env python3
"""
Final Schema Verification
Verifikasi final bahwa semua functionality tersedia dalam schema
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def verify_schema_completeness():
    """Verifikasi kelengkapan schema dengan pemahaman parameter path"""
    
    print("🔍 FINAL SCHEMA VERIFICATION")
    print("="*60)
    
    # Get schema
    try:
        response = requests.get(f"{BASE_URL}/openapi.json", timeout=5)
        schema = response.json()
        
        print(f"✅ Schema title: {schema['info']['title']}")
        print(f"✅ Schema version: {schema['info']['version']}")
        
        # Count operations
        operations = []
        for path, methods in schema['paths'].items():
            for method, details in methods.items():
                operations.append({
                    "method": method.upper(),
                    "path": path,
                    "operationId": details.get('operationId', 'no-id'),
                    "summary": details.get('summary', 'no-summary')
                })
        
        print(f"✅ Total operations: {len(operations)}")
        
    except Exception as e:
        print(f"❌ Schema error: {e}")
        return False
    
    # Test core functionalities are covered
    required_functionalities = [
        ("System Health", "health"),
        ("Trading Signals", "signal"),
        ("Market Data", "market"),
        ("SMC Analysis", "smc"),
        ("Backtest", "backtest"),
        ("Charts", "widget|dashboard"),
        ("Enhanced Analysis", "analysis"),
        ("Performance", "performance")
    ]
    
    print(f"\n📋 FUNCTIONALITY COVERAGE:")
    covered_count = 0
    
    for func_name, keyword in required_functionalities:
        found = any(keyword.lower() in op['operationId'].lower() or 
                   keyword.lower() in op['path'].lower() or
                   any(k in op['operationId'].lower() for k in keyword.split('|'))
                   for op in operations)
        
        if found:
            print(f"✅ {func_name}")
            covered_count += 1
        else:
            print(f"❌ {func_name}")
    
    coverage_percent = (covered_count / len(required_functionalities)) * 100
    print(f"\n📊 Functionality Coverage: {coverage_percent:.1f}%")
    
    # Test parameterized endpoints work
    print(f"\n🧪 PARAMETERIZED ENDPOINT TESTS:")
    param_tests = [
        ("GET", "/api/gpts/ticker/BTC-USDT", "Ticker endpoint"),
        ("GET", "/api/gpts/orderbook/BTC-USDT", "Orderbook endpoint"),
        ("GET", "/api/gpts/smc-zones/BTC-USDT", "SMC zones endpoint")
    ]
    
    param_working = 0
    for method, endpoint, name in param_tests:
        try:
            resp = requests.get(f"{BASE_URL}{endpoint}", timeout=3)
            if resp.status_code == 200:
                print(f"✅ {name} working")
                param_working += 1
            else:
                print(f"⚠️ {name} status {resp.status_code}")
        except:
            print(f"❌ {name} failed")
    
    # Calculate final score
    operation_score = min(100, (len(operations) / 25) * 100)  # Target: 25+ operations
    functionality_score = coverage_percent
    parameter_score = (param_working / len(param_tests)) * 100
    
    final_score = (operation_score + functionality_score + parameter_score) / 3
    
    print(f"\n" + "="*60)
    print(f"📊 FINAL ASSESSMENT:")
    print(f"   Operations Score: {operation_score:.1f}% ({len(operations)}/25+ target)")
    print(f"   Functionality Score: {functionality_score:.1f}% ({covered_count}/{len(required_functionalities)} covered)")
    print(f"   Parameter Score: {parameter_score:.1f}% ({param_working}/{len(param_tests)} working)")
    print(f"   Overall Score: {final_score:.1f}%")
    
    if final_score >= 95:
        status = "🎉 EXCELLENT - Schema sempurna!"
        complete = True
    elif final_score >= 85:
        status = "✅ VERY GOOD - Schema hampir sempurna!"
        complete = True
    elif final_score >= 75:
        status = "👍 GOOD - Schema baik, minor issues"
        complete = False
    else:
        status = "⚠️ NEEDS WORK - Schema perlu diperbaiki"
        complete = False
    
    print(f"\n{status}")
    
    # Detailed operations list
    print(f"\n📋 ALL {len(operations)} OPERATIONS IN SCHEMA:")
    for i, op in enumerate(operations, 1):
        print(f"{i:2d}. {op['method']} {op['path']} ({op['operationId']})")
    
    return {
        "complete": complete,
        "score": final_score,
        "operations_count": len(operations),
        "functionality_coverage": functionality_score,
        "status": status
    }

if __name__ == "__main__":
    result = verify_schema_completeness()
    
    with open("final_schema_verification.json", "w") as f:
        json.dump(result, f, indent=2)
    
    print(f"\n💾 Verification results saved to final_schema_verification.json")