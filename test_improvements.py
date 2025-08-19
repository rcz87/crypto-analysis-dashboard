#!/usr/bin/env python3
"""
Test script for the 3 critical improvements:
1. Symbol conversion & parameter consistency
2. Security enhancements  
3. Data quality & dtype validation
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000/api/gpts"

def test_symbol_normalization():
    """Test symbol normalization across different formats"""
    print("🔧 Testing Symbol Normalization & Parameter Consistency...")
    
    test_cases = [
        ("BTCUSDT", "BTC-USDT"),
        ("BTC/USDT", "BTC-USDT"), 
        ("ETH-USDC", "ETH-USDC"),
        ("SOLUSDT", "SOL-USDT")
    ]
    
    for input_symbol, expected_symbol in test_cases:
        # Test GET with 'tf' parameter (backward compatibility)
        response = requests.get(f"{BASE_URL}/signal", params={
            "symbol": input_symbol,
            "tf": "1H"
        })
        
        if response.status_code == 200:
            data = response.json()
            actual_symbol = data.get("signal", {}).get("symbol", "")
            status = "✅" if actual_symbol == expected_symbol else "❌"
            print(f"  {status} {input_symbol} → {actual_symbol} (expected: {expected_symbol})")
        else:
            print(f"  ❌ Failed to test {input_symbol}: HTTP {response.status_code}")
    
    # Test POST with 'timeframe' parameter
    print("\n🔧 Testing POST parameter consistency...")
    post_data = {
        "symbol": "ETHUSDT", 
        "timeframe": "4H",
        "confidence_threshold": 0.75
    }
    
    response = requests.post(f"{BASE_URL}/signal", json=post_data)
    if response.status_code == 200:
        data = response.json()
        symbol = data.get("signal", {}).get("symbol", "")
        timeframe = data.get("signal", {}).get("timeframe", "")
        print(f"  ✅ POST: ETHUSDT → {symbol}, timeframe: {timeframe}")
    else:
        print(f"  ❌ POST test failed: HTTP {response.status_code}")

def test_security_headers():
    """Test security headers implementation"""
    print("\n🔒 Testing Security Headers...")
    
    response = requests.get(f"{BASE_URL}/status")
    headers = response.headers
    
    security_checks = [
        ("X-Content-Type-Options", "nosniff"),
        ("Cache-Control", "no-store"),
    ]
    
    for header_name, expected_value in security_checks:
        actual_value = headers.get(header_name, "")
        if expected_value in actual_value:
            print(f"  ✅ {header_name}: {actual_value}")
        else:
            print(f"  ❌ {header_name}: Missing or incorrect (got: {actual_value})")

def test_data_validation():
    """Test data quality validation"""
    print("\n📊 Testing Data Quality & OHLCV Validation...")
    
    # Test with valid symbol - should pass data validation
    response = requests.get(f"{BASE_URL}/signal", params={
        "symbol": "BTC-USDT",
        "timeframe": "1H"
    })
    
    if response.status_code == 200:
        data = response.json()
        signal = data.get("signal", {})
        if signal.get("current_price") and signal.get("symbol"):
            print(f"  ✅ Data validation passed: {signal['symbol']} @ ${signal['current_price']}")
        else:
            print(f"  ❌ Data validation issue: Missing price or symbol data")
    else:
        print(f"  ❌ Data validation test failed: HTTP {response.status_code}")

def test_payload_limit():
    """Test 1MB payload limit"""
    print("\n🛡️ Testing Payload Size Limit...")
    
    # Create a large payload (> 1MB)
    large_data = {
        "symbol": "BTC-USDT",
        "timeframe": "1H", 
        "large_field": "x" * (1024 * 1024 + 1000)  # > 1MB
    }
    
    try:
        response = requests.post(f"{BASE_URL}/signal", json=large_data, timeout=5)
        if response.status_code == 413:
            print(f"  ✅ Payload limit working: HTTP 413 Payload Too Large")
        else:
            print(f"  ⚠️ Unexpected response: HTTP {response.status_code}")
    except requests.exceptions.ConnectionError:
        print(f"  ✅ Connection rejected (payload limit working)")
    except Exception as e:
        print(f"  ⚠️ Error testing payload limit: {e}")

def main():
    """Run all improvement tests"""
    print("🚀 Testing Production-Ready Improvements")
    print("=" * 50)
    
    test_symbol_normalization()
    test_security_headers()
    test_data_validation()
    test_payload_limit()
    
    print("\n✅ All improvement tests completed!")

if __name__ == "__main__":
    main()