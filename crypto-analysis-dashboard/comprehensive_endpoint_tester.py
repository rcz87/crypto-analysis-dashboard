#!/usr/bin/env python3
"""
Comprehensive Endpoint Tester - Tests all 25+ endpoints
Automatically discovers endpoints from OpenAPI schema and tests each one
"""

import time, json, sys, requests
from typing import Dict, Any, List, Tuple
from urllib.parse import urljoin

# Configuration
BASE_URL = "http://localhost:5000"
SYMBOL = "SOL-USDT"
TIMEOUT = 30

# Schema discovery candidates
SCHEMA_CANDIDATES = [
    "/openapi.json",
    "/api/openapi.json", 
    "/docs/openapi.json",
    "/openapi_schema",
    "/swagger.json"
]

# Default payloads for POST endpoints
PAYLOAD_OVERRIDES = {
    "/api/gpts/market-data": {"symbol": SYMBOL, "timeframe": "1H", "limit": 300},
    "/api/gpts/analysis": {"symbol": SYMBOL, "timeframe": "4H"},
    "/api/gpts/smc-zones": {"symbol": SYMBOL, "tfs": ["5m","15m","1h"]},
    "/api/gpts/smc-analysis": {
        "symbol": SYMBOL, 
        "timeframe": "1H",
        "tfs": ["1m","5m","15m","1h"],
        "features": ["BOS","CHOCH","OB","FVG","LIQ_SWEEP"]
    },
    "/api/gpts/sinyal/tajam": {"symbol": SYMBOL, "timeframe": "1H"},
    "/api/gpts/signal": {"symbol": SYMBOL, "timeframe": "1H"},
}

# Query parameter overrides for GET endpoints
QUERY_OVERRIDES = {
    "/api/gpts/ticker/{symbol}": f"/api/gpts/ticker/{SYMBOL}",
    "/api/gpts/orderbook/{symbol}": f"/api/gpts/orderbook/{SYMBOL}",
    "/api/gpts/smc-zones/{symbol}": f"/api/gpts/smc-zones/{SYMBOL}?timeframe=1H",
    "/api/gpts/signal": f"/api/gpts/signal?symbol={SYMBOL}&timeframe=1H",
    "/api/gpts/analysis": f"/api/gpts/analysis?symbol={SYMBOL}&timeframe=1H",
    "/api/gpts/market-data": f"/api/gpts/market-data?symbol={SYMBOL}&timeframe=1H&limit=300",
    "/api/gpts/smc-analysis": f"/api/gpts/smc-analysis?symbol={SYMBOL}&timeframe=1H",
    "/api/smc/zones": f"/api/smc/zones?symbol={SYMBOL}&tf=1H",
}

# Comprehensive endpoint list discovered from system
FALLBACK_ROUTES = [
    # Root and health endpoints
    ("GET", "/"),
    ("GET", "/health"),
    ("GET", "/api/gpts/health"),
    ("GET", "/api/gpts/status"),
    
    # Real-time data endpoints
    ("GET", f"/api/gpts/ticker/{SYMBOL}"),
    ("GET", f"/api/gpts/orderbook/{SYMBOL}"),
    
    # Market data endpoints (GET and POST variations)
    ("GET", f"/api/gpts/market-data"),
    ("POST", "/api/gpts/market-data"),
    
    # Analysis endpoints (GET and POST variations)
    ("GET", f"/api/gpts/analysis"),
    ("POST", "/api/gpts/analysis"),
    
    # Trading signal endpoints
    ("GET", f"/api/gpts/signal"),
    ("POST", "/api/gpts/sinyal/tajam"),
    
    # SMC Analysis endpoints (GET and POST variations)
    ("GET", f"/api/gpts/smc-analysis"),
    ("POST", "/api/gpts/smc-analysis"),
    
    # SMC Zones endpoints (Multiple variations)
    ("GET", f"/api/gpts/smc-zones/{SYMBOL}"),
    ("GET", "/api/smc/zones"),
    ("GET", "/api/smc/zones/critical"),
    ("POST", "/api/gpts/smc-zones"),
    
    # Additional discovered endpoints
    ("GET", "/openapi.json"),
    ("GET", "/docs"),
    ("GET", "/api/gpts/health/detailed"),
    ("GET", f"/api/gpts/ticker/{SYMBOL}/realtime"),
    ("GET", f"/api/gpts/orderbook/{SYMBOL}/depth"),
    ("GET", f"/api/analysis/full/{SYMBOL}"),
    ("GET", f"/api/signals/enhanced/{SYMBOL}"),
]

class EndpointTester:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.results = []
        self.total_tested = 0
        self.passed = 0
        self.failed = 0
        
    def log_result(self, method: str, path: str, success: bool, response_time: float, 
                   status_code: int, sample_data: str, error: str = None):
        """Log test result"""
        self.results.append({
            'method': method,
            'path': path,
            'success': success,
            'response_time': response_time,
            'status_code': status_code,
            'sample_data': sample_data,
            'error': error
        })
        self.total_tested += 1
        if success:
            self.passed += 1
        else:
            self.failed += 1

    def format_data(self, data: Any, max_len: int = 300) -> str:
        """Format response data for display"""
        try:
            if isinstance(data, dict):
                s = json.dumps(data, ensure_ascii=False)[:max_len]
            else:
                s = str(data)[:max_len]
            return s + ("..." if len(s) >= max_len else "")
        except Exception:
            return str(data)[:max_len]

    def test_endpoint(self, method: str, path: str, payload: Dict = None, query_params: str = ""):
        """Test a single endpoint"""
        # Apply query overrides
        if path in QUERY_OVERRIDES:
            full_path = QUERY_OVERRIDES[path]
        else:
            full_path = path + query_params
            
        url = urljoin(self.base_url, full_path)
        
        start_time = time.time()
        try:
            if method.upper() == "GET":
                response = requests.get(url, timeout=TIMEOUT)
            elif method.upper() == "POST":
                # Use payload override if available
                actual_payload = PAYLOAD_OVERRIDES.get(path, payload or {"symbol": SYMBOL})
                response = requests.post(url, json=actual_payload, timeout=TIMEOUT)
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            response_time = (time.time() - start_time) * 1000
            
            try:
                data = response.json()
            except:
                data = response.text
                
            success = response.status_code == 200
            sample = self.format_data(data)
            
            self.log_result(method, path, success, response_time, 
                          response.status_code, sample)
            
            status_icon = "✅" if success else "❌"
            print(f"{method:<4} {path:<40} {status_icon} {response_time:6.1f}ms [{response.status_code}]")
            
            if success:
                print(f"     └─ {sample}")
            else:
                print(f"     └─ ERROR: {sample}")
                
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            self.log_result(method, path, False, response_time, 0, "", str(e))
            print(f"{method:<4} {path:<40} ❌ {response_time:6.1f}ms [ERROR]")
            print(f"     └─ {str(e)}")

    def discover_schema(self) -> List[Tuple[str, str]]:
        """Discover endpoints from OpenAPI schema"""
        endpoints = []
        
        for schema_path in SCHEMA_CANDIDATES:
            try:
                url = urljoin(self.base_url, schema_path)
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    schema = response.json()
                    print(f"✅ Loaded schema from {schema_path}")
                    
                    # Extract paths from OpenAPI schema
                    paths = schema.get('paths', {})
                    for path, methods in paths.items():
                        for method in methods.keys():
                            if method.upper() in ['GET', 'POST']:
                                endpoints.append((method.upper(), path))
                    
                    print(f"📋 Found {len(endpoints)} endpoints in schema")
                    return endpoints
                    
            except Exception as e:
                continue
                
        print("❌ Could not load OpenAPI schema, using fallback routes")
        return FALLBACK_ROUTES

    def run_comprehensive_test(self):
        """Run comprehensive test of all endpoints"""
        print("=== COMPREHENSIVE ENDPOINT TESTER ===")
        print(f"🎯 Testing all endpoints on {self.base_url}")
        print(f"📊 Target: 25+ endpoints with real SOL-USDT data")
        print()
        
        # Discover endpoints
        endpoints = self.discover_schema()
        
        if not endpoints:
            print("⚠️  No endpoints discovered, using fallback routes")
            endpoints = FALLBACK_ROUTES
            
        print(f"🔍 Total paths discovered: {len(endpoints)}")
        print()
        
        # Test each endpoint
        for method, path in endpoints:
            self.test_endpoint(method, path)
            time.sleep(0.1)  # Small delay to prevent overwhelming
            
        # Print summary
        print("\n" + "="*80)
        print("📊 TEST SUMMARY")
        print("="*80)
        print(f"Total tested: {self.total_tested}")
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        print(f"Success rate: {(self.passed/self.total_tested*100):.1f}%" if self.total_tested > 0 else "N/A")
        
        if self.failed > 0:
            print(f"\n❌ FAILED ENDPOINTS ({self.failed}):")
            for result in self.results:
                if not result['success']:
                    error_msg = result['error'] or f"HTTP {result['status_code']}"
                    print(f"   {result['method']} {result['path']} - {error_msg}")
        
        # Check if we hit target
        target_met = self.total_tested >= 25 and self.passed >= 20
        print(f"\n🎯 Target (25+ endpoints): {'✅ MET' if target_met else '❌ NOT MET'}")
        
        if not target_met:
            print("\n💡 TO REACH 25+ ENDPOINTS:")
            print("   • Add missing endpoints to openapi_schema.py")
            print("   • Update PAYLOAD_OVERRIDES for failing POST endpoints")
            print("   • Check QUERY_OVERRIDES for parameterized paths")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        BASE_URL = sys.argv[1]
        
    tester = EndpointTester(BASE_URL)
    tester.run_comprehensive_test()