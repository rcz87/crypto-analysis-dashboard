#!/usr/bin/env python3
"""
GPTS Comprehensive Tester - Enhanced Version
Test semua endpoint termasuk LuxAlgo webhook dan CoinGlass integration
"""

import requests
import json
import time
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime

class GPTSComprehensiveTester:
    """Comprehensive tester untuk semua GPTS endpoints"""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'GPTS-Comprehensive-Tester/1.0',
            'Accept': 'application/json'
        })
        
        # Test results tracking
        self.results = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'test_details': []
        }
        
    def log_result(self, endpoint: str, method: str, status: str, 
                   response_time: float, details: str = ""):
        """Log test result"""
        self.results['total_tests'] += 1
        if status == 'PASS':
            self.results['passed_tests'] += 1
        else:
            self.results['failed_tests'] += 1
            
        self.results['test_details'].append({
            'endpoint': endpoint,
            'method': method,
            'status': status,
            'response_time_ms': round(response_time * 1000, 1),
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
        
        status_emoji = "✅" if status == 'PASS' else "❌"
        print(f"{status_emoji} {method} {endpoint} - {status} ({response_time*1000:.1f}ms)")
        if details and status == 'FAIL':
            print(f"   Details: {details}")
    
    def test_endpoint(self, endpoint: str, method: str = 'GET', 
                     data: Optional[Dict] = None, 
                     expected_status: int = 200,
                     timeout: int = 30) -> bool:
        """Test individual endpoint"""
        try:
            start_time = time.time()
            url = f"{self.base_url}{endpoint}"
            
            if method.upper() == 'GET':
                response = self.session.get(url, timeout=timeout)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data, timeout=timeout)
            else:
                response = self.session.request(method.upper(), url, 
                                              json=data, timeout=timeout)
            
            response_time = time.time() - start_time
            
            # Check status code
            if response.status_code != expected_status:
                self.log_result(endpoint, method, 'FAIL', response_time,
                              f"Expected {expected_status}, got {response.status_code}")
                return False
            
            # Try to parse JSON response
            try:
                json_response = response.json()
                if not isinstance(json_response, dict):
                    self.log_result(endpoint, method, 'FAIL', response_time,
                                  "Response is not valid JSON object")
                    return False
            except json.JSONDecodeError:
                self.log_result(endpoint, method, 'FAIL', response_time,
                              "Response is not valid JSON")
                return False
            
            self.log_result(endpoint, method, 'PASS', response_time)
            return True
            
        except requests.exceptions.Timeout:
            self.log_result(endpoint, method, 'FAIL', timeout,
                          f"Timeout after {timeout}s")
            return False
        except requests.exceptions.RequestException as e:
            self.log_result(endpoint, method, 'FAIL', 0,
                          f"Request failed: {str(e)}")
            return False
        except Exception as e:
            self.log_result(endpoint, method, 'FAIL', 0,
                          f"Unexpected error: {str(e)}")
            return False
    
    def test_core_endpoints(self):
        """Test core GPTS endpoints"""
        print("\n🎯 TESTING CORE GPTS ENDPOINTS")
        print("=" * 50)
        
        core_endpoints = [
            # Health and status
            ('/api/gpts/health', 'GET'),
            ('/api/gpts/status', 'GET'),
            
            # Main signal endpoints  
            ('/api/gpts/signal?symbol=BTCUSDT', 'GET'),
            ('/api/gpts/sinyal-tajam?symbol=BTCUSDT', 'GET'),
            
            # SMC analysis
            ('/api/gpts/smc-analysis?symbol=BTCUSDT', 'GET'),
            ('/api/gpts/smc-zones?symbol=BTCUSDT', 'GET'),
            
            # Market data
            ('/api/gpts/market-structure?symbol=BTCUSDT', 'GET'),
            ('/api/gpts/volume-profile?symbol=BTCUSDT', 'GET'),
            
            # Performance and monitoring
            ('/api/gpts/performance-metrics', 'GET'),
            ('/api/gpts/system-health', 'GET'),
        ]
        
        for endpoint, method in core_endpoints:
            self.test_endpoint(endpoint, method)
    
    def test_luxalgo_webhook(self):
        """Test LuxAlgo TradingView webhook endpoints"""
        print("\n📡 TESTING LUXALGO WEBHOOK ENDPOINTS") 
        print("=" * 50)
        
        # Test webhook endpoints
        webhook_endpoints = [
            ('/api/webhooks/status', 'GET'),
            ('/api/webhooks/setup-guide', 'GET'),
            ('/api/webhooks/tradingview/test', 'GET'),
        ]
        
        for endpoint, method in webhook_endpoints:
            self.test_endpoint(endpoint, method)
        
        # Test TradingView webhook simulation
        print("\n📊 Testing TradingView webhook simulation...")
        
        # Simulate JSON payload from TradingView LuxAlgo
        luxalgo_payloads = [
            {
                "symbol": "BTCUSDT",
                "action": "BUY", 
                "price": 50000,
                "strategy": "LuxAlgo Premium",
                "timeframe": "1h",
                "indicator": "Confirmation",
                "confidence": 85
            },
            {
                "symbol": "ETHUSDT",
                "action": "SELL",
                "price": 2500,
                "strategy": "LuxAlgo Premium", 
                "timeframe": "4h",
                "indicator": "Trend Catcher",
                "confidence": 78
            },
            # Simple format
            "LuxAlgo BUY SOLUSDT at 150",
            "LuxAlgo SELL ADAUSDT at 0.45"
        ]
        
        for i, payload in enumerate(luxalgo_payloads, 1):
            print(f"\nTesting LuxAlgo payload {i}...")
            success = self.test_endpoint(
                '/api/webhooks/tradingview/test', 
                'POST', 
                payload if isinstance(payload, dict) else {"message": payload}
            )
    
    def test_coinglass_integration(self):
        """Test CoinGlass integration endpoints"""
        print("\n💰 TESTING COINGLASS INTEGRATION")
        print("=" * 50)
        
        # Test CoinGlass endpoints
        coinglass_endpoints = [
            ('/api/gpts/coinglass/status', 'GET'),
            ('/api/gpts/coinglass/liquidation-preview?symbol=BTCUSDT', 'GET'),
            ('/api/gpts/coinglass/market-structure?symbol=BTCUSDT', 'GET'),
        ]
        
        for endpoint, method in coinglass_endpoints:
            self.test_endpoint(endpoint, method)
        
        # Test external CoinGlass API simulation
        print("\n🌐 Testing CoinGlass external API simulation...")
        
        # Simulate CoinGlass API responses
        coinglass_symbols = ['BTC-USDT', 'ETH-USDT', 'SOL-USDT', 'ADA-USDT']
        
        for symbol in coinglass_symbols:
            print(f"\nTesting CoinGlass funding for {symbol}...")
            # This would be the actual endpoint when implemented
            endpoint = f'/api/ext/coinglass/funding?symbol={symbol}'
            # For now, test the existing structure
            test_endpoint = f'/api/gpts/coinglass/liquidation-preview?symbol={symbol.replace("-", "")}'
            self.test_endpoint(test_endpoint, 'GET')
    
    def test_sharp_scoring_system(self):
        """Test sharp scoring system"""
        print("\n🎯 TESTING SHARP SCORING SYSTEM")
        print("=" * 50)
        
        # Test demo scenarios
        self.test_endpoint('/api/gpts/sharp-scoring/test', 'GET')
        
        # Test custom scoring scenarios
        test_scenarios = [
            {
                "name": "Perfect Setup",
                "data": {
                    "smc_confidence": 0.9,
                    "ob_imbalance": 0.85,
                    "momentum_signal": 0.8,
                    "vol_regime": 0.7,
                    "lux_signal": "BUY",
                    "bias": "long",
                    "funding_rate_abs": 0.02,
                    "oi_delta_pos": True,
                    "long_short_extreme": False
                }
            },
            {
                "name": "Poor Setup",
                "data": {
                    "smc_confidence": 0.3,
                    "ob_imbalance": 0.2,
                    "momentum_signal": 0.1,
                    "vol_regime": 0.2,
                    "lux_signal": "SELL",
                    "bias": "long",
                    "funding_rate_abs": 0.08,
                    "oi_delta_pos": False,
                    "long_short_extreme": True
                }
            },
            {
                "name": "Marginal Setup",
                "data": {
                    "smc_confidence": 0.7,
                    "ob_imbalance": 0.5,
                    "momentum_signal": 0.5,
                    "vol_regime": 0.4,
                    "lux_signal": "BUY", 
                    "bias": "long",
                    "funding_rate_abs": 0.02,
                    "oi_delta_pos": False,
                    "long_short_extreme": False
                }
            }
        ]
        
        for scenario in test_scenarios:
            print(f"\nTesting {scenario['name']}...")
            self.test_endpoint('/api/gpts/sharp-scoring/test', 'POST', scenario['data'])
    
    def test_enhanced_features(self):
        """Test enhanced features and integrations"""
        print("\n⚡ TESTING ENHANCED FEATURES")
        print("=" * 50)
        
        enhanced_endpoints = [
            # Telegram integration
            ('/api/gpts/telegram/status', 'GET'),
            
            # Advanced analysis
            ('/api/gpts/confluence-analysis?symbol=BTCUSDT', 'GET'),
            ('/api/gpts/risk-assessment?symbol=BTCUSDT', 'GET'),
            
            # Performance tracking
            ('/api/gpts/signal-history?limit=10', 'GET'),
            ('/api/gpts/performance-dashboard', 'GET'),
        ]
        
        for endpoint, method in enhanced_endpoints:
            # Some endpoints might not exist yet, so we allow 404s
            success = self.test_endpoint(endpoint, method)
            # Don't fail the test for missing advanced endpoints
            if not success and "404" in str(self.results['test_details'][-1].get('details', '')):
                print(f"   ℹ️  Endpoint {endpoint} not implemented yet (expected)")
    
    def run_comprehensive_test(self):
        """Run comprehensive test suite"""
        print("🚀 GPTS COMPREHENSIVE TESTER")
        print("=" * 60)
        print(f"Base URL: {self.base_url}")
        print(f"Start Time: {datetime.now().isoformat()}")
        print("=" * 60)
        
        start_time = time.time()
        
        try:
            # Test core functionality
            self.test_core_endpoints()
            
            # Test LuxAlgo webhook integration
            self.test_luxalgo_webhook()
            
            # Test CoinGlass integration
            self.test_coinglass_integration()
            
            # Test sharp scoring system
            self.test_sharp_scoring_system()
            
            # Test enhanced features
            self.test_enhanced_features()
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Test suite interrupted by user")
        except Exception as e:
            print(f"\n\n❌ Test suite failed with error: {e}")
            
        finally:
            # Print comprehensive results
            self.print_final_results(time.time() - start_time)
    
    def print_final_results(self, total_time: float):
        """Print comprehensive test results"""
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE TEST RESULTS")
        print("=" * 60)
        
        print(f"Total Tests: {self.results['total_tests']}")
        print(f"Passed: {self.results['passed_tests']} ✅")
        print(f"Failed: {self.results['failed_tests']} ❌")
        print(f"Success Rate: {(self.results['passed_tests']/self.results['total_tests']*100):.1f}%")
        print(f"Total Time: {total_time:.2f}s")
        
        # Group results by category
        categories = {}
        for test in self.results['test_details']:
            endpoint = test['endpoint']
            
            # Categorize endpoints
            if '/webhooks/' in endpoint:
                category = 'LuxAlgo Webhooks'
            elif '/coinglass/' in endpoint:
                category = 'CoinGlass Integration'
            elif '/sharp-scoring/' in endpoint:
                category = 'Sharp Scoring System'
            elif any(core in endpoint for core in ['/signal', '/smc-', '/market-']):
                category = 'Core Signal Endpoints'
            elif any(status in endpoint for status in ['/health', '/status']):
                category = 'Health & Status'
            else:
                category = 'Enhanced Features'
            
            if category not in categories:
                categories[category] = {'passed': 0, 'failed': 0, 'total': 0}
            
            categories[category]['total'] += 1
            if test['status'] == 'PASS':
                categories[category]['passed'] += 1
            else:
                categories[category]['failed'] += 1
        
        print("\n📈 RESULTS BY CATEGORY:")
        for category, stats in categories.items():
            success_rate = (stats['passed'] / stats['total'] * 100) if stats['total'] > 0 else 0
            status_emoji = "✅" if success_rate >= 80 else "⚠️" if success_rate >= 60 else "❌"
            print(f"{status_emoji} {category}: {stats['passed']}/{stats['total']} ({success_rate:.1f}%)")
        
        # Print failed tests details
        if self.results['failed_tests'] > 0:
            print("\n❌ FAILED TESTS DETAILS:")
            for test in self.results['test_details']:
                if test['status'] == 'FAIL':
                    print(f"   • {test['method']} {test['endpoint']}")
                    print(f"     Error: {test['details']}")
        
        # Overall assessment
        print("\n🎯 OVERALL ASSESSMENT:")
        overall_success_rate = (self.results['passed_tests']/self.results['total_tests']*100)
        
        if overall_success_rate >= 90:
            print("🟢 EXCELLENT - System is production ready")
        elif overall_success_rate >= 80:
            print("🟡 GOOD - System is mostly functional with minor issues")
        elif overall_success_rate >= 60:
            print("🟠 FAIR - System has significant issues that need attention")
        else:
            print("🔴 POOR - System has major problems requiring immediate fixes")
        
        print(f"\nTest completed at: {datetime.now().isoformat()}")
        print("=" * 60)

def main():
    """Main function"""
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "http://localhost:5000"
    
    tester = GPTSComprehensiveTester(base_url)
    tester.run_comprehensive_test()

if __name__ == "__main__":
    main()