#!/usr/bin/env python3
"""
🧪 Enhanced GPTs Custom Integration - Comprehensive Test Suite
Test semua endpoint untuk ChatGPT Custom GPT integration & Analytics
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:5000"

def test_endpoint(method, endpoint, data=None, expected_status=200):
    """Test helper function"""
    url = f"{BASE_URL}{endpoint}"
    
    print(f"\n🧪 Testing {method} {endpoint}")
    start_time = time.time()
    
    try:
        if method == "POST":
            response = requests.post(url, json=data, headers={'Content-Type': 'application/json'})
        else:
            response = requests.get(url)
        
        duration = (time.time() - start_time) * 1000
        
        print(f"   📊 Status: {response.status_code} | Duration: {duration:.1f}ms")
        
        if response.status_code == expected_status:
            print(f"   ✅ SUCCESS")
            result = response.json()
            if 'success' in result and result['success']:
                print(f"   📈 Response: {result.get('message', 'OK')}")
            return True, result
        else:
            print(f"   ❌ FAILED - Expected {expected_status}, got {response.status_code}")
            print(f"   📄 Response: {response.text[:200]}...")
            return False, response.json() if response.headers.get('content-type', '').startswith('application/json') else None
            
    except Exception as e:
        print(f"   💥 ERROR: {e}")
        return False, None

def main():
    """Run comprehensive test suite"""
    print("🚀 Enhanced GPTs Custom Integration - Test Suite")
    print("=" * 60)
    
    results = {
        'passed': 0,
        'failed': 0,
        'tests': []
    }
    
    # Test 1: Track Query
    print("\n📋 Test Group 1: Query Tracking")
    success, result = test_endpoint("POST", "/api/gpts/track-query", {
        "query_text": "Get Bitcoin trading signal for 1H timeframe",
        "response_text": "BUY signal with 85.5% confidence detected",
        "endpoint": "/api/gpts/signal",
        "processing_time_ms": 1250,
        "confidence_score": 85.5,
        "source": "ChatGPT"
    })
    results['tests'].append(('Track Query', success))
    results['passed' if success else 'failed'] += 1
    
    # Test 2: Track Signal
    print("\n📋 Test Group 2: Signal Tracking")
    success, result = test_endpoint("POST", "/api/gpts/track-signal", {
        "symbol": "ETHUSDT",
        "timeframe": "4H",
        "action": "SELL",
        "confidence": 78.3,
        "entry_price": 2340.50,
        "take_profit": 2280.00,
        "stop_loss": 2390.00,
        "ai_reasoning": "SMC Order Block rejection with bearish momentum",
        "market_conditions": "BEARISH",
        "source": "ChatGPT"
    })
    signal_id = result.get('signal_id') if result else None
    results['tests'].append(('Track Signal', success))
    results['passed' if success else 'failed'] += 1
    
    # Test 3: Track Interaction (if signal_id available)
    if signal_id:
        print("\n📋 Test Group 3: Interaction Tracking")
        success, result = test_endpoint("POST", "/api/gpts/track-interaction", {
            "signal_id": signal_id,
            "interaction_type": "EXECUTE",
            "interaction_source": "CHATGPT",
            "interaction_data": {"price": 2340.50, "quantity": 0.5},
            "user_id": "gpt_test_user"
        })
        results['tests'].append(('Track Interaction', success))
        results['passed' if success else 'failed'] += 1
    
    # Test 4: Query Log Retrieval
    print("\n📋 Test Group 4: Analytics - Query Log")
    success, result = test_endpoint("GET", "/api/gpts/query-log?limit=10")
    results['tests'].append(('Query Log', success))
    results['passed' if success else 'failed'] += 1
    
    # Test 5: Query Analytics
    print("\n📋 Test Group 5: Analytics - Query Patterns")
    success, result = test_endpoint("GET", "/api/gpts/analytics/queries?days=7")
    results['tests'].append(('Query Analytics', success))
    results['passed' if success else 'failed'] += 1
    
    # Test 6: Signal Analytics
    print("\n📋 Test Group 6: Analytics - Signal Performance")
    success, result = test_endpoint("GET", "/api/gpts/analytics/signals?days=30")
    results['tests'].append(('Signal Analytics', success))
    results['passed' if success else 'failed'] += 1
    
    # Test 7: Comprehensive Analytics
    print("\n📋 Test Group 7: Analytics - Comprehensive Report")
    success, result = test_endpoint("GET", "/api/gpts/analytics/comprehensive?days=7")
    results['tests'].append(('Comprehensive Analytics', success))
    results['passed' if success else 'failed'] += 1
    
    # Test Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY REPORT")
    print("=" * 60)
    
    total_tests = len(results['tests'])
    pass_rate = (results['passed'] / total_tests * 100) if total_tests > 0 else 0
    
    print(f"Total Tests: {total_tests}")
    print(f"✅ Passed: {results['passed']}")
    print(f"❌ Failed: {results['failed']}")
    print(f"📈 Pass Rate: {pass_rate:.1f}%")
    
    print("\n📋 Individual Test Results:")
    for test_name, success in results['tests']:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {status} - {test_name}")
    
    # Final Status
    if results['failed'] == 0:
        print("\n🎉 ALL TESTS PASSED - Enhanced GPTs Integration Ready!")
        print("✅ System is production ready for ChatGPT Custom GPT integration")
    else:
        print(f"\n⚠️  {results['failed']} tests failed - Review required")
        print("🔧 Check failed endpoints before deployment")
    
    # Generate test timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n📅 Test completed at: {timestamp}")
    
    return results

if __name__ == "__main__":
    main()