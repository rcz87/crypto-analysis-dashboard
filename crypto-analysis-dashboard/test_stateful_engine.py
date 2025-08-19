#!/usr/bin/env python3
"""
Test script untuk Stateful AI Signal Engine
Test semua fungsi tracking dan analytics
"""

import json
import time
import requests
from datetime import datetime

# Test configuration
BASE_URL = "http://localhost:5000/api/gpts"
STATE_URL = f"{BASE_URL}/state"

def test_track_signal():
    """Test tracking signal baru"""
    print("🧪 Testing signal tracking...")
    
    signal_data = {
        "signal_data": {
            "symbol": "BTCUSDT",
            "timeframe": "1H",
            "action": "BUY",
            "confidence": 85.5,
            "entry_price": 45000.0,
            "take_profit": 46500.0,
            "stop_loss": 44200.0,
            "risk_reward_ratio": 1.8,
            "ai_reasoning": "Strong bullish momentum with SMC confirmation",
            "smc_analysis": {
                "order_blocks": ["45000-45200"],
                "fvg": "44800-45000",
                "choch": True
            },
            "market_conditions": "BULLISH"
        },
        "source": "ChatGPT"
    }
    
    try:
        response = requests.post(f"{STATE_URL}/track-signal", json=signal_data)
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        
        if response.status_code == 200:
            return result.get('signal_id')
        return None
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_signal_history():
    """Test mengambil signal history"""
    print("\n🧪 Testing signal history...")
    
    try:
        response = requests.get(f"{STATE_URL}/signal-history?limit=10&symbol=BTCUSDT")
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Signals found: {len(result.get('signals', []))}")
        
        if result.get('signals'):
            print("Latest signal:")
            print(json.dumps(result['signals'][0], indent=2))
        
    except Exception as e:
        print(f"❌ Error: {e}")

def test_execute_signal(signal_id):
    """Test marking signal sebagai executed"""
    if not signal_id:
        print("\n⏭️ Skipping signal execution test - no signal_id")
        return
        
    print(f"\n🧪 Testing signal execution for {signal_id}...")
    
    execution_data = {
        "execution_price": 45100.0,
        "source": "TELEGRAM",
        "user_id": "test_user_123"
    }
    
    try:
        response = requests.post(f"{STATE_URL}/signal/{signal_id}/execute", json=execution_data)
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def test_log_gpt_query():
    """Test logging GPT query"""
    print("\n🧪 Testing GPT query logging...")
    
    query_log_data = {
        "query_data": {
            "endpoint": "/api/gpts/signal",
            "method": "POST",
            "params": {"symbol": "BTCUSDT", "timeframe": "1H"},
            "user_query": "Give me a trading signal for Bitcoin"
        },
        "response_data": {
            "status_code": 200,
            "data": {"confidence": 85.5, "action": "BUY"},
            "processing_time_ms": 1250,
            "ai_model": "GPT-4o"
        }
    }
    
    try:
        response = requests.post(f"{STATE_URL}/log-query", json=query_log_data)
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def test_analytics():
    """Test analytics endpoints"""
    print("\n🧪 Testing analytics...")
    
    endpoints = [
        "analytics/signals?days=7",
        "analytics/queries?days=7", 
        "analytics/interactions?days=7"
    ]
    
    for endpoint in endpoints:
        try:
            print(f"\n📊 Testing {endpoint}...")
            response = requests.get(f"{STATE_URL}/{endpoint}")
            print(f"Status: {response.status_code}")
            result = response.json()
            
            if 'analytics' in result:
                analytics = result['analytics']
                print(f"Analytics keys: {list(analytics.keys())}")
                if analytics:
                    print(f"Sample data: {json.dumps(analytics, indent=2)[:200]}...")
            
        except Exception as e:
            print(f"❌ Error: {e}")

def test_integration_with_existing_api():
    """Test integration dengan existing API"""
    print("\n🧪 Testing integration dengan existing API...")
    
    try:
        # Test existing signal endpoint
        response = requests.get(f"{BASE_URL}/signal?symbol=BTCUSDT&tf=1H")
        print(f"Existing API Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("Existing API masih berfungsi ✅")
            
            # Check jika ada signal_id di response (dari integration)
            if 'signal_id' in result:
                print(f"Signal tracking terintegrasi! Signal ID: {result['signal_id']}")
            else:
                print("Signal tracking belum terintegrasi")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def test_state_api_endpoints():
    """Test semua endpoint state API"""
    print("\n🧪 Testing state API endpoints...")
    
    try:
        # Test endpoint yang tidak ada (untuk test error handling)
        response = requests.get(f"{STATE_URL}/non-existent")
        print(f"404 Test Status: {response.status_code}")
        
        if response.status_code == 404:
            result = response.json()
            print("404 handler working ✅")
            if 'available_endpoints' in result:
                print(f"Available endpoints: {len(result['available_endpoints'])}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Run semua tests"""
    print("🚀 Starting Stateful AI Signal Engine Tests")
    print("=" * 50)
    
    # Test basic tracking
    signal_id = test_track_signal()
    time.sleep(1)
    
    # Test history
    test_signal_history()
    time.sleep(1)
    
    # Test execution
    test_execute_signal(signal_id)
    time.sleep(1)
    
    # Test query logging
    test_log_gpt_query()
    time.sleep(1)
    
    # Test analytics
    test_analytics()
    time.sleep(1)
    
    # Test integration
    test_integration_with_existing_api()
    time.sleep(1)
    
    # Test error handling
    test_state_api_endpoints()
    
    print("\n" + "=" * 50)
    print("✅ Test completed! Check results above.")

if __name__ == "__main__":
    main()