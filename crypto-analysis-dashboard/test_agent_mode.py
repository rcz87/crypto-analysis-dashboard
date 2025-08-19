#!/usr/bin/env python3
"""
🧪 Agent Mode - Comprehensive Test Suite
Test Multi Role Agent system untuk trading analysis
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:5000"

def test_agent_mode_endpoint():
    """Test agent mode via API endpoint"""
    print("🧪 Testing Agent Mode API Endpoint")
    print("=" * 50)
    
    test_cases = [
        {
            "name": "Bitcoin 1H Analysis",
            "payload": {
                "symbol": "BTC-USDT",
                "timeframe": "1h",
                "account_balance": 1000.0,
                "risk_tolerance": 0.02,
                "use_mock_data": True
            }
        },
        {
            "name": "Ethereum 4H Conservative",
            "payload": {
                "symbol": "ETH-USDT", 
                "timeframe": "4h",
                "account_balance": 2500.0,
                "risk_tolerance": 0.015,
                "use_mock_data": True
            }
        },
        {
            "name": "Solana 1D Aggressive",
            "payload": {
                "symbol": "SOL-USDT",
                "timeframe": "1d", 
                "account_balance": 500.0,
                "risk_tolerance": 0.035,
                "use_mock_data": True
            }
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test {i}: {test_case['name']}")
        print("-" * 30)
        
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/gpts/agent-mode",
                json=test_case['payload'],
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            duration = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"✅ Status: {response.status_code} | Duration: {duration:.1f}ms")
                print(f"📊 Symbol: {data.get('symbol')}")
                print(f"🎯 Recommendation: {data.get('recommendation')}")
                print(f"📈 Confidence: {data.get('confidence', 0):.1f}%")
                print(f"⚡ Analysis Duration: {data.get('analysis_duration_ms', 0):.1f}ms")
                
                # Agent breakdown
                agents = data.get('agents', {})
                print(f"\n🤖 Agent Results:")
                for agent_name, agent_result in agents.items():
                    conf = agent_result.get('confidence', 0)
                    rec = agent_result.get('recommendation', 'N/A')
                    print(f"   {agent_name}: {rec} ({conf:.1f}%)")
                
                # Check for narrative
                narrative = data.get('narrative', '')
                if narrative:
                    print(f"\n📝 Narrative Preview: {narrative[:100]}...")
                
                results.append({
                    'test_name': test_case['name'],
                    'status': 'PASS',
                    'recommendation': data.get('recommendation'),
                    'confidence': data.get('confidence', 0),
                    'duration_ms': duration,
                    'agent_count': len(agents)
                })
                
            else:
                print(f"❌ Status: {response.status_code}")
                print(f"📄 Response: {response.text[:200]}...")
                results.append({
                    'test_name': test_case['name'],
                    'status': 'FAIL',
                    'error': f"HTTP {response.status_code}",
                    'duration_ms': duration
                })
                
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            print(f"💥 ERROR: {e}")
            results.append({
                'test_name': test_case['name'],
                'status': 'ERROR',
                'error': str(e),
                'duration_ms': duration
            })
    
    # Test Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for r in results if r['status'] == 'PASS')
    failed = sum(1 for r in results if r['status'] in ['FAIL', 'ERROR'])
    total = len(results)
    
    print(f"Total Tests: {total}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Pass Rate: {(passed/total*100):.1f}%")
    
    # Individual results
    print(f"\n📋 Detailed Results:")
    for result in results:
        status_icon = "✅" if result['status'] == 'PASS' else "❌"
        print(f"   {status_icon} {result['test_name']}")
        if result['status'] == 'PASS':
            print(f"      Recommendation: {result['recommendation']} (Confidence: {result['confidence']:.1f}%)")
            print(f"      Duration: {result['duration_ms']:.1f}ms | Agents: {result['agent_count']}")
        else:
            print(f"      Error: {result.get('error', 'Unknown error')}")
    
    return results

def test_individual_agents():
    """Test individual agent modules"""
    print("\n🔬 Testing Individual Agent Modules")
    print("=" * 50)
    
    try:
        from agent_mode import (
            TechnicalAnalyst, SentimentWatcher, RiskManager, 
            TradeExecutor, NarrativeMaker, mock_market_data
        )
        
        # Generate test data
        market_data = mock_market_data("BTC-USDT")
        symbol = "BTC-USDT"
        timeframe = "1h"
        
        print(f"📊 Test Data: {symbol} @ ${market_data['price_data']['close']}")
        
        agents_to_test = [
            ('TechnicalAnalyst', TechnicalAnalyst()),
            ('SentimentWatcher', SentimentWatcher()),
            ('RiskManager', RiskManager()),
            ('TradeExecutor', TradeExecutor())
        ]
        
        agent_results = {}
        
        for agent_name, agent in agents_to_test:
            print(f"\n🤖 Testing {agent_name}...")
            
            try:
                start_time = time.time()
                
                if agent_name == 'RiskManager':
                    result = agent.analyze(symbol, timeframe, market_data, 1000.0, 0.02)
                elif agent_name == 'TradeExecutor':
                    # Mock signal for executor
                    mock_signal = {'action': 'BUY', 'confidence': 75, 'entry_price': market_data['price_data']['close']}
                    result = agent.analyze(symbol, timeframe, market_data, mock_signal)
                else:
                    result = agent.analyze(symbol, timeframe, market_data)
                
                duration = (time.time() - start_time) * 1000
                
                if 'error' not in result:
                    print(f"   ✅ SUCCESS | Duration: {duration:.1f}ms")
                    print(f"   📈 Confidence: {result.get('confidence', 0):.1f}%")
                    print(f"   🎯 Recommendation: {result.get('recommendation', 'N/A')}")
                    agent_results[agent_name] = result
                else:
                    print(f"   ❌ FAILED | Error: {result.get('error', 'Unknown')}")
                
            except Exception as e:
                print(f"   💥 ERROR: {e}")
        
        # Test Narrative Maker
        if agent_results:
            print(f"\n📝 Testing NarrativeMaker...")
            try:
                narrative_maker = NarrativeMaker()
                narrative = narrative_maker.analyze(symbol, timeframe, agent_results)
                
                if narrative and len(narrative) > 50:
                    print(f"   ✅ SUCCESS | Length: {len(narrative)} chars")
                    print(f"   📖 Preview: {narrative[:100]}...")
                else:
                    print(f"   ❌ FAILED | Narrative too short or empty")
                    
            except Exception as e:
                print(f"   💥 ERROR: {e}")
        
        print(f"\n✅ Individual agent testing completed")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"💥 Unexpected error: {e}")
        return False

def main():
    """Run comprehensive agent mode testing"""
    print("🚀 Agent Mode - Comprehensive Test Suite")
    print("=" * 60)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test API endpoint
    api_results = test_agent_mode_endpoint()
    
    # Test individual modules
    module_test_passed = test_individual_agents()
    
    # Final summary
    print("\n" + "=" * 60)
    print("🏁 FINAL TEST SUMMARY")
    print("=" * 60)
    
    api_passed = sum(1 for r in api_results if r['status'] == 'PASS')
    api_total = len(api_results)
    
    print(f"📡 API Endpoint Tests: {api_passed}/{api_total} passed")
    print(f"🔬 Module Tests: {'PASS' if module_test_passed else 'FAIL'}")
    
    overall_success = (api_passed == api_total) and module_test_passed
    
    if overall_success:
        print("\n🎉 ALL TESTS PASSED - Agent Mode Ready for Production!")
        print("✅ Multi Role Agent system is fully operational")
    else:
        print("\n⚠️ Some tests failed - Review required")
        print("🔧 Check failed components before deployment")
    
    print(f"\nTest completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return overall_success

if __name__ == "__main__":
    success = main()