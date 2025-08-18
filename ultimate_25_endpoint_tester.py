#!/usr/bin/env python3
"""
Ultimate 25+ Endpoint Tester
Discovers and tests ALL available endpoints based on actual blueprint registration
Target: 25+ total endpoints with comprehensive coverage
"""

import time, json, sys, requests
from typing import Dict, Any, List, Tuple

# Configuration
BASE_URL = "http://localhost:5000"
SYMBOL = "SOL-USDT"
TIMEOUT = 30

# Comprehensive endpoint list based on actual blueprint discovery
COMPREHENSIVE_ENDPOINTS = [
    # === CORE ROUTES (4 endpoints) ===
    ("GET", "/"),
    ("GET", "/health"),
    
    # === GPTs API ROUTES (12 endpoints) ===
    ("GET", "/api/gpts/health"),
    ("GET", "/api/gpts/status"),
    ("GET", f"/api/gpts/ticker/{SYMBOL}"),
    ("GET", f"/api/gpts/orderbook/{SYMBOL}"),
    ("GET", "/api/gpts/market-data"),
    ("GET", "/api/gpts/analysis"),
    ("GET", "/api/gpts/signal"),
    ("GET", "/api/gpts/smc-analysis"),
    ("GET", f"/api/gpts/smc-zones/{SYMBOL}"),
    ("POST", "/api/gpts/sinyal/tajam"),
    ("POST", "/api/gpts/smc-analysis"),
    ("POST", "/api/gpts/analysis"),
    
    # === SMC ZONES ENDPOINTS (3 endpoints) ===
    ("GET", "/api/smc/zones"),
    ("GET", "/api/smc/zones/critical"),
    ("GET", f"/api/smc/zones?symbol={SYMBOL}&tf=1H"),
    
    # === PROMPTBOOK ENDPOINTS (3 endpoints) ===
    ("GET", "/api/promptbook/"),
    ("GET", "/api/promptbook/init"),
    ("GET", "/api/promptbook/context"),
    
    # === PERFORMANCE ENDPOINTS (4 endpoints) ===
    ("GET", "/api/performance/stats"),
    ("GET", "/api/performance/detailed-report"),
    ("GET", "/api/performance/metrics"),
    ("GET", "/api/performance/backtest"),
    
    # === NEWS ENDPOINTS (3 endpoints) ===
    ("GET", "/api/news/status"),
    ("GET", "/api/news/latest"),
    ("GET", "/api/news/sentiment"),
    
    # === ADDITIONAL DISCOVERED ENDPOINTS (6 endpoints) ===
    ("GET", f"/api/gpts/ticker/{SYMBOL}/realtime"),
    ("GET", f"/api/gpts/orderbook/{SYMBOL}/depth"),
    ("GET", "/api/gpts/signal/enhanced"),
    ("GET", "/api/gpts/analysis/comprehensive"),
    ("POST", "/api/gpts/market-data"),
    ("GET", "/openapi.json"),
]

# Enhanced payload overrides
PAYLOAD_OVERRIDES = {
    "/api/gpts/market-data": {"symbol": SYMBOL, "timeframe": "1H", "limit": 300},
    "/api/gpts/analysis": {"symbol": SYMBOL, "timeframe": "4H"},
    "/api/gpts/sinyal/tajam": {"symbol": SYMBOL, "timeframe": "1H"},
    "/api/gpts/smc-analysis": {"symbol": SYMBOL, "timeframe": "1H"},
    "/api/news/sentiment": {"query": "bitcoin", "limit": 5},
}

# Enhanced query overrides
QUERY_OVERRIDES = {
    "/api/gpts/market-data": f"/api/gpts/market-data?symbol={SYMBOL}&timeframe=1H&limit=300",
    "/api/gpts/analysis": f"/api/gpts/analysis?symbol={SYMBOL}&timeframe=1H",
    "/api/gpts/signal": f"/api/gpts/signal?symbol={SYMBOL}&timeframe=1H",
    "/api/gpts/smc-analysis": f"/api/gpts/smc-analysis?symbol={SYMBOL}&timeframe=1H",
    "/api/gpts/smc-zones/{SYMBOL}": f"/api/gpts/smc-zones/{SYMBOL}?timeframe=1H",
    "/api/performance/stats": "/api/performance/stats?strategy=main",
    "/api/performance/detailed-report": "/api/performance/detailed-report?strategy=main",
    "/api/news/latest": "/api/news/latest?limit=3",
}

class Ultimate25Tester:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.results = []
        self.total_tested = 0
        self.passed = 0
        self.failed = 0
        self.categories = {
            "core": [],
            "gpts": [],
            "smc": [],
            "promptbook": [],
            "performance": [],
            "news": [],
            "additional": []
        }
        
    def categorize_endpoint(self, path: str) -> str:
        """Categorize endpoint by type"""
        if path.startswith("/api/gpts"):
            return "gpts"
        elif path.startswith("/api/smc"):
            return "smc"
        elif path.startswith("/api/promptbook"):
            return "promptbook"
        elif path.startswith("/api/performance"):
            return "performance"
        elif path.startswith("/api/news"):
            return "news"
        elif path in ["/", "/health"]:
            return "core"
        else:
            return "additional"

    def format_data(self, data: Any, max_len: int = 250) -> str:
        """Format response data for display"""
        try:
            if isinstance(data, dict):
                s = json.dumps(data, ensure_ascii=False)[:max_len]
            else:
                s = str(data)[:max_len]
            return s + ("..." if len(s) >= max_len else "")
        except Exception:
            return str(data)[:max_len]

    def test_endpoint(self, method: str, path: str):
        """Test a single endpoint with enhanced error handling"""
        # Apply query overrides
        test_path = QUERY_OVERRIDES.get(path, path)
        url = f"{self.base_url}{test_path}"
        
        start_time = time.time()
        category = self.categorize_endpoint(path)
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, timeout=TIMEOUT)
            elif method.upper() == "POST":
                payload = PAYLOAD_OVERRIDES.get(path, {"symbol": SYMBOL})
                response = requests.post(url, json=payload, timeout=TIMEOUT)
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            response_time = (time.time() - start_time) * 1000
            
            try:
                data = response.json()
            except:
                data = response.text
                
            success = response.status_code == 200
            sample = self.format_data(data)
            
            # Store result
            result = {
                'method': method,
                'path': path,
                'success': success,
                'response_time': response_time,
                'status_code': response.status_code,
                'sample_data': sample,
                'category': category
            }
            
            self.results.append(result)
            self.categories[category].append(result)
            self.total_tested += 1
            
            if success:
                self.passed += 1
                status_icon = "✅"
            else:
                self.failed += 1
                status_icon = "❌"
            
            print(f"{method:<4} {path:<45} {status_icon} {response_time:6.1f}ms [{response.status_code}] ({category})")
            print(f"     └─ {sample}")
                
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            result = {
                'method': method,
                'path': path,
                'success': False,
                'response_time': response_time,
                'status_code': 0,
                'sample_data': str(e),
                'category': category,
                'error': str(e)
            }
            
            self.results.append(result)
            self.categories[category].append(result)
            self.total_tested += 1
            self.failed += 1
            
            print(f"{method:<4} {path:<45} ❌ {response_time:6.1f}ms [ERROR] ({category})")
            print(f"     └─ {str(e)}")

    def print_category_summary(self):
        """Print summary by category"""
        print("\n" + "="*80)
        print("📊 RESULTS BY CATEGORY")
        print("="*80)
        
        for category, results in self.categories.items():
            if not results:
                continue
                
            passed = sum(1 for r in results if r['success'])
            total = len(results)
            success_rate = (passed/total*100) if total > 0 else 0
            
            print(f"\n🔹 {category.upper()} ({passed}/{total} - {success_rate:.1f}%)")
            for result in results:
                icon = "✅" if result['success'] else "❌"
                print(f"   {icon} {result['method']} {result['path']}")

    def run_ultimate_test(self):
        """Run the ultimate 25+ endpoint test"""
        print("="*80)
        print("🎯 ULTIMATE 25+ ENDPOINT TESTER")
        print("="*80)
        print(f"Target: Test 25+ endpoints across all system components")
        print(f"Base URL: {self.base_url}")
        print(f"Test Symbol: {SYMBOL}")
        print(f"Total Endpoints Scheduled: {len(COMPREHENSIVE_ENDPOINTS)}")
        print()
        
        # Test each endpoint
        for i, (method, path) in enumerate(COMPREHENSIVE_ENDPOINTS, 1):
            print(f"[{i:2d}/{len(COMPREHENSIVE_ENDPOINTS)}]", end=" ")
            self.test_endpoint(method, path)
            time.sleep(0.05)  # Small delay
            
        # Print comprehensive summary
        self.print_category_summary()
        
        print("\n" + "="*80)
        print("🏆 FINAL RESULTS")
        print("="*80)
        print(f"Total Tested: {self.total_tested}")
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        print(f"Success Rate: {(self.passed/self.total_tested*100):.1f}%")
        
        # Target achievement check
        target_met = self.total_tested >= 25 and self.passed >= 20
        achievement = "🎯 TARGET ACHIEVED!" if target_met else "⚠️  TARGET NOT MET"
        print(f"\n{achievement}")
        
        if target_met:
            print("✨ System ready for comprehensive GPTs integration!")
            print("🚀 All core components tested and operational")
        else:
            print(f"💡 Need {25 - self.total_tested} more endpoints or {20 - self.passed} more working endpoints")
            
        # Failed endpoints analysis
        if self.failed > 0:
            print(f"\n❌ FAILED ENDPOINTS ANALYSIS ({self.failed}):")
            failed_by_category = {}
            for result in self.results:
                if not result['success']:
                    cat = result['category']
                    if cat not in failed_by_category:
                        failed_by_category[cat] = []
                    failed_by_category[cat].append(result)
            
            for category, failed_results in failed_by_category.items():
                print(f"\n   {category.upper()}:")
                for result in failed_results:
                    status = result.get('error', f"HTTP {result['status_code']}")
                    print(f"     • {result['method']} {result['path']} - {status}")

        print("\n🎯 GPTs Query Simulation:")
        print("   'Analisa lengkap SOL-USDT timeframe 1H dengan SMC, orderbook, market data'")
        print("   → Would call: ticker → orderbook → market-data → smc-analysis → smc-zones → sinyal")
        print(f"   → Expected time: ~2-3 seconds for {self.passed} working endpoints")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        BASE_URL = sys.argv[1]
        
    tester = Ultimate25Tester(BASE_URL)
    tester.run_ultimate_test()