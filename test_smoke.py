#!/usr/bin/env python3
"""
Smoke Test Suite - Automated testing for all critical endpoints
Ensures all priority endpoints return 200 OK and prevents overselling
"""
import pytest
import requests
import json
import sys
import os

# Test configuration
BASE_URL = "http://localhost:5000"
TIMEOUT = 30
CRITICAL_ENDPOINTS = [
    # Core endpoints
    ("GET", "/health"),
    ("GET", "/api/gpts/status"),
    ("POST", "/api/gpts/sinyal/tajam", {"symbol": "BTCUSDT", "timeframe": "1H"}),
    
    # Institutional endpoints  
    ("GET", "/api/institutional/status"),
    ("POST", "/api/institutional/signal", {"symbol": "BTCUSDT", "timeframe": "1H"}),
    
    # Enhanced signals
    ("GET", "/api/enhanced/status"), 
    ("POST", "/api/enhanced/sharp-signal", {"symbol": "BTCUSDT", "timeframe": "1H"}),
    
    # AI reasoning
    ("GET", "/api/v1/ai-reasoning/status"),
    
    # SMC zones  
    ("GET", "/api/smc/status"),
    ("GET", "/api/smc/zones", {"symbol": "BTCUSDT", "tf": "1H"}),
    
    # Performance monitoring
    ("GET", "/api/performance/advanced/status"),
    
    # Schema documentation
    ("GET", "/api/schema/"),
    ("GET", "/api/schema/enhanced/"),
    ("GET", "/api/schema/openapi.json"),
    ("GET", "/api/schema/enhanced/openapi-enhanced.json"),
]

class TestEndpointSmoke:
    """Smoke tests for all critical endpoints"""
    
    @pytest.mark.parametrize("method,path,data", [
        (item[0], item[1], item[2] if len(item) > 2 else None) 
        for item in CRITICAL_ENDPOINTS
    ])
    def test_endpoint_returns_200_or_expected(self, method, path, data):
        """Test that endpoint returns successful response"""
        url = f"{BASE_URL}{path}"
        
        try:
            if method == "GET":
                if data:  # Query parameters
                    response = requests.get(url, params=data, timeout=TIMEOUT)
                else:
                    response = requests.get(url, timeout=TIMEOUT)
            elif method == "POST":
                response = requests.post(
                    url, 
                    json=data or {}, 
                    headers={"Content-Type": "application/json"},
                    timeout=TIMEOUT
                )
            else:
                pytest.skip(f"Unsupported method: {method}")
                
            # Allow 200 OK or 503 for degraded health
            if path == "/health" and response.status_code == 503:
                # Health endpoint can return 503 if unhealthy - this is expected
                assert response.status_code in [200, 503], f"Health endpoint returned {response.status_code}"
            else:
                # All other endpoints should return 200
                assert response.status_code == 200, f"Endpoint {method} {path} returned {response.status_code}: {response.text}"
                
            # Verify response is valid JSON
            try:
                json_response = response.json()
                assert isinstance(json_response, dict), f"Response is not valid JSON dict: {type(json_response)}"
            except json.JSONDecodeError:
                pytest.fail(f"Endpoint {method} {path} returned invalid JSON: {response.text}")
                
        except requests.exceptions.ConnectError:
            pytest.fail(f"Could not connect to {url}. Is the server running on {BASE_URL}?")
        except requests.exceptions.Timeout:
            pytest.fail(f"Endpoint {method} {path} timed out after {TIMEOUT}s")
        except requests.exceptions.RequestException as e:
            pytest.fail(f"Request failed for {method} {path}: {e}")

    def test_core_integration_workflow(self):
        """Test full workflow: OKX data → SMC analysis → Signal generation"""
        # Test data fetch capability
        response = requests.get(f"{BASE_URL}/api/gpts/status", timeout=TIMEOUT)
        assert response.status_code == 200
        
        # Test signal generation workflow
        signal_response = requests.post(
            f"{BASE_URL}/api/gpts/sinyal/tajam",
            json={"symbol": "BTCUSDT", "timeframe": "1H"},
            headers={"Content-Type": "application/json"},
            timeout=TIMEOUT
        )
        assert signal_response.status_code == 200
        
        signal_data = signal_response.json()
        assert "signal" in signal_data or "success" in signal_data, f"Invalid signal response: {signal_data}"

    def test_no_404_responses(self):
        """Ensure no critical endpoints return 404"""
        for item in CRITICAL_ENDPOINTS:
            method, path = item[0], item[1]
            data = item[2] if len(item) > 2 else None
            
            url = f"{BASE_URL}{path}"
            
            try:
                if method == "GET":
                    response = requests.get(url, params=data or {}, timeout=TIMEOUT)
                else:
                    response = requests.post(url, json=data or {}, timeout=TIMEOUT)
                    
                # 404 is not acceptable for any critical endpoint
                assert response.status_code != 404, f"Critical endpoint {method} {path} returns 404 - endpoint not found!"
                
            except requests.exceptions.RequestException:
                # Connection errors are acceptable for this test, 404s are not
                pass

def run_smoke_tests():
    """Run smoke tests and return success status"""
    import subprocess
    
    print("🧪 RUNNING COMPREHENSIVE SMOKE TESTS")
    print("=" * 50)
    
    # Run pytest with verbose output
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        __file__, 
        "-v",
        "--tb=short",
        "--maxfail=10"
    ], capture_output=True, text=True)
    
    print("STDOUT:")
    print(result.stdout)
    if result.stderr:
        print("STDERR:")
        print(result.stderr)
        
    success = result.returncode == 0
    
    print(f"\n🎯 SMOKE TEST RESULT: {'✅ PASSED' if success else '❌ FAILED'}")
    if not success:
        print(f"Return code: {result.returncode}")
    
    return success

if __name__ == "__main__":
    success = run_smoke_tests()
    sys.exit(0 if success else 1)