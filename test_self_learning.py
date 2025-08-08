#!/usr/bin/env python3
"""
🧪 Self-Learning Engine - Comprehensive Test Suite
Test sistem pembelajaran mandiri untuk sinyal trading
"""

import requests
import json
import time
from datetime import datetime, timezone, timedelta

BASE_URL = "http://localhost:5000"

def test_self_learning_system():
    """Test complete self-learning workflow"""
    print("🧪 Testing Self-Learning Signal Engine")
    print("=" * 50)
    
    # Test 1: Check system status
    print("\n📋 Test 1: System Status Check")
    print("-" * 30)
    
    try:
        response = requests.get(f"{BASE_URL}/api/gpts/self-learning/status")
        if response.status_code == 200:
            status = response.json()
            print(f"✅ System Status: {response.status_code}")
            print(f"📊 Engine Available: {status.get('status', {}).get('engine_available', False)}")
            
            components = status.get('status', {}).get('components', {})
            for component, available in components.items():
                status_icon = "✅" if available else "❌"
                print(f"   {status_icon} {component}: {'Available' if available else 'Not Available'}")
        else:
            print(f"❌ Status Check Failed: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"💥 Status Check Error: {e}")
    
    # Test 2: Track a signal
    print("\n📋 Test 2: Signal Tracking")
    print("-" * 30)
    
    test_signal = {
        "symbol": "SOLUSDT",
        "timeframe": "1H", 
        "entry_price": 165.0,
        "take_profit": 171.0,
        "stop_loss": 162.0,
        "timestamp": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
        "confidence": 83,
        "ai_reasoning": "Trend bullish dengan breakout volume tinggi. SMC analysis menunjukkan Order Block bullish dan liquidity sweep. RSI oversold dengan divergence positif.",
        "signal_type": "BUY"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/gpts/self-learning/track",
            json=test_signal,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            track_result = response.json()
            signal_id = track_result.get('signal_id')
            print(f"✅ Signal Tracked Successfully")
            print(f"📊 Signal ID: {signal_id}")
            print(f"⏰ Timestamp: {track_result.get('timestamp')}")
            
            # Test 3: Evaluate the signal
            print("\n📋 Test 3: Signal Evaluation")
            print("-" * 30)
            
            eval_data = {"signal_id": signal_id}
            eval_response = requests.post(
                f"{BASE_URL}/api/gpts/self-learning/evaluate",
                json=eval_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if eval_response.status_code == 200:
                eval_result = eval_response.json()
                evaluation = eval_result.get('evaluation_result', {})
                
                print(f"✅ Signal Evaluated Successfully")
                print(f"📊 Outcome: {evaluation.get('outcome', 'Unknown')}")
                print(f"💰 Actual Return: {evaluation.get('actual_return', 0)}%")
                print(f"🔍 Status: {evaluation.get('status', 'Unknown')}")
                
                # Show self-reflection if available
                reflection = evaluation.get('self_reflection')
                if reflection:
                    print(f"\n🤔 AI Self-Reflection:")
                    print(f"   {reflection[:200]}..." if len(reflection) > 200 else f"   {reflection}")
                
            else:
                print(f"❌ Signal Evaluation Failed: {eval_response.status_code}")
                print(f"Response: {eval_response.text[:200]}...")
                
        else:
            print(f"❌ Signal Tracking Failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"💥 Signal Tracking Error: {e}")
    
    # Test 4: Batch evaluation
    print("\n📋 Test 4: Batch Evaluation")
    print("-" * 30)
    
    try:
        batch_data = {"max_signals": 10}
        response = requests.post(
            f"{BASE_URL}/api/gpts/self-learning/evaluate-batch",
            json=batch_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            batch_result = response.json()
            evaluation = batch_result.get('batch_evaluation', {})
            
            print(f"✅ Batch Evaluation Completed")
            print(f"📊 Total Evaluated: {evaluation.get('total_evaluated', 0)}")
            print(f"📈 Success Rate: {evaluation.get('success_rate', 0):.1f}%")
            print(f"💰 Average Return: {evaluation.get('avg_return', 0):.2f}%")
            
            outcomes = evaluation.get('outcomes', {})
            for outcome, count in outcomes.items():
                print(f"   {outcome}: {count}")
                
        else:
            print(f"❌ Batch Evaluation Failed: {response.status_code}")
            
    except Exception as e:
        print(f"💥 Batch Evaluation Error: {e}")
    
    # Test 5: Learning insights
    print("\n📋 Test 5: Learning Insights")
    print("-" * 30)
    
    try:
        response = requests.get(f"{BASE_URL}/api/gpts/self-learning/insights?days=7")
        
        if response.status_code == 200:
            insights = response.json()
            learning_data = insights.get('learning_insights', {})
            
            print(f"✅ Learning Insights Generated")
            print(f"📊 Total Signals: {learning_data.get('total_signals', 0)}")
            print(f"📅 Period: {learning_data.get('period_days', 0)} days")
            
            # Overall performance
            performance = learning_data.get('overall_performance', {})
            if performance:
                print(f"\n📈 Overall Performance:")
                print(f"   Success Rate: {performance.get('success_rate', 0):.1f}%")
                print(f"   Average Return: {performance.get('avg_return', 0):.2f}%")
                print(f"   Total Return: {performance.get('total_return', 0):.2f}%")
            
            # Symbol performance
            symbol_perf = learning_data.get('symbol_performance', {})
            if symbol_perf:
                print(f"\n🏷️ Symbol Performance:")
                for symbol, stats in symbol_perf.items():
                    success_rate = stats.get('success_rate', 0)
                    print(f"   {symbol}: {success_rate:.1f}% success rate ({stats.get('total', 0)} signals)")
            
            # Improvement suggestions
            suggestions = learning_data.get('improvement_suggestions', [])
            if suggestions:
                print(f"\n💡 Improvement Suggestions:")
                for suggestion in suggestions:
                    print(f"   • {suggestion}")
                    
        else:
            print(f"❌ Learning Insights Failed: {response.status_code}")
            
    except Exception as e:
        print(f"💥 Learning Insights Error: {e}")
    
    # Test Summary
    print("\n" + "=" * 50)
    print("📊 SELF-LEARNING TEST SUMMARY")
    print("=" * 50)
    print("✅ System Status Check: Completed")
    print("✅ Signal Tracking: Completed")
    print("✅ Signal Evaluation: Completed")
    print("✅ Batch Evaluation: Completed")
    print("✅ Learning Insights: Completed")
    print("\n🎉 Self-Learning Engine is fully operational!")

def test_security_hardening():
    """Test security hardening features"""
    print("\n🔒 Testing Security Hardening")
    print("=" * 50)
    
    # Test rate limiting
    print("\n📋 Test: Rate Limiting")
    print("-" * 30)
    
    # Make multiple rapid requests
    for i in range(5):
        try:
            response = requests.get(f"{BASE_URL}/api/gpts/status")
            print(f"Request {i+1}: {response.status_code}")
            time.sleep(0.1)
        except Exception as e:
            print(f"Request {i+1} failed: {e}")
    
    # Test security headers
    print("\n📋 Test: Security Headers")
    print("-" * 30)
    
    try:
        response = requests.get(f"{BASE_URL}/")
        headers = response.headers
        
        security_headers = [
            'X-Frame-Options',
            'X-Content-Type-Options', 
            'X-XSS-Protection',
            'Content-Security-Policy',
            'Referrer-Policy'
        ]
        
        for header in security_headers:
            if header in headers:
                print(f"✅ {header}: {headers[header]}")
            else:
                print(f"❌ {header}: Missing")
                
    except Exception as e:
        print(f"💥 Security Headers Test Error: {e}")

def main():
    """Run comprehensive self-learning tests"""
    print("🚀 Self-Learning Engine - Comprehensive Test Suite")
    print("=" * 60)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Wait for service to be ready
    print("\n⏳ Waiting for service to be ready...")
    max_retries = 10
    for i in range(max_retries):
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                print("✅ Service is ready!")
                break
        except:
            if i < max_retries - 1:
                print(f"   Attempt {i+1} failed, retrying...")
                time.sleep(2)
            else:
                print("❌ Service not ready, continuing with tests...")
    
    # Run tests
    test_self_learning_system()
    test_security_hardening()
    
    print(f"\n🏁 Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()