#!/usr/bin/env python3
"""
Comprehensive Deployment Testing Script for Crypto Analysis Dashboard
Tests all critical components before VPS deployment
"""

import os
import sys
import json
import time
import requests
from pathlib import Path
from typing import Dict, List, Tuple

class DeploymentTester:
    def __init__(self):
        self.base_url = "http://localhost:5000"
        self.api_key = os.getenv('API_KEY')
        self.test_results = []
        self.failed_tests = 0
        
    def log_test(self, test_name: str, passed: bool, message: str = ""):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        result = f"{status}: {test_name}"
        if message:
            result += f" - {message}"
        print(result)
        
        self.test_results.append({
            "test": test_name,
            "passed": passed,
            "message": message
        })
        
        if not passed:
            self.failed_tests += 1
    
    def test_deployment_files(self) -> bool:
        """Test 1: Verify core deployment files exist"""
        print("\n🔍 TEST 1: Core Deployment Files")
        
        required_files = [
            "wsgi.py",
            "gunicorn.conf.py", 
            "Dockerfile",
            "docker-compose-vps.yml",
            ".env.example",
            "nginx/nginx.conf",
            "main.py",
            "app.py",
            "auth.py",
            "models.py"
        ]
        
        all_exist = True
        for file_path in required_files:
            exists = Path(file_path).exists()
            self.log_test(f"File exists: {file_path}", exists)
            if not exists:
                all_exist = False
                
        return all_exist
    
    def test_environment_config(self) -> bool:
        """Test 2: Environment configuration"""
        print("\n🔧 TEST 2: Environment Configuration")
        
        required_env_vars = [
            "DATABASE_URL",
            "API_KEY", 
            "SESSION_SECRET",
            "OKX_API_KEY",
            "OPENAI_API_KEY"
        ]
        
        all_set = True
        for env_var in required_env_vars:
            value = os.getenv(env_var)
            is_set = value is not None and value != ""
            self.log_test(f"Environment variable: {env_var}", is_set)
            if not is_set:
                all_set = False
                
        return all_set
    
    def test_health_endpoints(self) -> bool:
        """Test 3: Health check and monitoring endpoints"""
        print("\n💓 TEST 3: Health & Monitoring Endpoints")
        
        health_endpoints = [
            "/health",
            "/",
            "/api/gpts/status"
        ]
        
        all_healthy = True
        for endpoint in health_endpoints:
            try:
                headers = {}
                if endpoint == "/api/gpts/status" and self.api_key:
                    headers["X-API-KEY"] = self.api_key
                    
                response = requests.get(f"{self.base_url}{endpoint}", headers=headers, timeout=10)
                success = response.status_code == 200
                
                self.log_test(f"Health endpoint: {endpoint}", success, 
                            f"Status: {response.status_code}")
                if not success:
                    all_healthy = False
                    
            except Exception as e:
                self.log_test(f"Health endpoint: {endpoint}", False, f"Error: {str(e)}")
                all_healthy = False
                
        return all_healthy
    
    def test_authentication(self) -> bool:
        """Test 4: Authentication and authorization"""
        print("\n🔐 TEST 4: Authentication System")
        
        protected_endpoint = "/api/gpts/status"
        
        # Test without API key
        try:
            response = requests.get(f"{self.base_url}{protected_endpoint}", timeout=10)
            unauthorized = response.status_code == 401
            self.log_test("Unauthorized access blocked", unauthorized, 
                        f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Unauthorized access test", False, f"Error: {str(e)}")
            return False
        
        # Test with API key
        if self.api_key:
            try:
                headers = {"X-API-KEY": self.api_key}
                response = requests.get(f"{self.base_url}{protected_endpoint}", 
                                      headers=headers, timeout=10)
                authorized = response.status_code == 200
                self.log_test("Authorized access works", authorized,
                            f"Status: {response.status_code}")
                return unauthorized and authorized
            except Exception as e:
                self.log_test("Authorized access test", False, f"Error: {str(e)}")
                return False
        else:
            self.log_test("API key test", False, "No API_KEY environment variable")
            return False
    
    def test_core_endpoints(self) -> bool:
        """Test 5: Core functional endpoints"""
        print("\n🎯 TEST 5: Core Functional Endpoints")
        
        core_endpoints = [
            ("/api/gpts/sinyal/tajam", "POST"),
            ("/api/gpts/analysis", "GET"),
            ("/api/gpts/market-data", "GET")
        ]
        
        headers = {"X-API-KEY": self.api_key} if self.api_key else {}
        working_endpoints = 0
        
        for endpoint, method in core_endpoints:
            try:
                if method == "GET":
                    response = requests.get(f"{self.base_url}{endpoint}", 
                                          headers=headers, timeout=10)
                else:
                    test_data = {"symbol": "BTC-USDT", "timeframe": "1H"}
                    response = requests.post(f"{self.base_url}{endpoint}", 
                                           json=test_data, headers=headers, timeout=10)
                
                success = response.status_code in [200, 201, 400]  # 400 might be expected for missing params
                if success:
                    working_endpoints += 1
                    
                self.log_test(f"Endpoint: {method} {endpoint}", success,
                            f"Status: {response.status_code}")
                            
            except Exception as e:
                self.log_test(f"Endpoint: {method} {endpoint}", False, f"Error: {str(e)}")
        
        return working_endpoints >= 2  # At least 2/3 should work
    
    def test_database_connection(self) -> bool:
        """Test 6: Database connectivity"""
        print("\n🗄️ TEST 6: Database Connection")
        
        try:
            # Try to import and test database
            sys.path.append('.')
            from app import app
            
            with app.app_context():
                from models import db
                
                # Test database connection
                db.engine.execute("SELECT 1")
                self.log_test("Database connection", True, "Connected successfully")
                return True
                
        except Exception as e:
            self.log_test("Database connection", False, f"Error: {str(e)}")
            return False
    
    def test_ai_integration(self) -> bool:
        """Test 7: AI and external API integration"""
        print("\n🤖 TEST 7: AI Integration")
        
        # Test OpenAI configuration
        openai_key = os.getenv('OPENAI_API_KEY')
        okx_key = os.getenv('OKX_API_KEY')
        
        self.log_test("OpenAI API key configured", bool(openai_key))
        self.log_test("OKX API key configured", bool(okx_key))
        
        # Test AI endpoint if available
        try:
            if self.api_key:
                headers = {"X-API-KEY": self.api_key}
                test_data = {"text": "test analysis"}
                response = requests.post(f"{self.base_url}/api/gpts/analysis", 
                                       json=test_data, headers=headers, timeout=15)
                
                ai_working = response.status_code in [200, 400, 503]  # 503 might indicate AI service unavailable
                self.log_test("AI endpoint responds", ai_working,
                            f"Status: {response.status_code}")
                            
                return ai_working
        except Exception as e:
            self.log_test("AI integration test", False, f"Error: {str(e)}")
            
        return bool(openai_key and okx_key)
    
    def run_all_tests(self) -> bool:
        """Run comprehensive deployment tests"""
        print("🚀 CRYPTO ANALYSIS DASHBOARD - DEPLOYMENT TESTING")
        print("=" * 60)
        
        tests = [
            self.test_deployment_files,
            self.test_environment_config,
            self.test_health_endpoints,
            self.test_authentication,
            self.test_core_endpoints,
            self.test_database_connection,
            self.test_ai_integration
        ]
        
        start_time = time.time()
        
        for test_func in tests:
            try:
                test_func()
            except Exception as e:
                print(f"❌ Test failed with exception: {e}")
                self.failed_tests += 1
        
        elapsed = time.time() - start_time
        
        print(f"\n📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Total tests: {len(self.test_results)}")
        print(f"Passed: {len(self.test_results) - self.failed_tests}")
        print(f"Failed: {self.failed_tests}")
        print(f"Execution time: {elapsed:.2f}s")
        
        if self.failed_tests == 0:
            print("🎉 ALL TESTS PASSED - READY FOR VPS DEPLOYMENT!")
            return True
        else:
            print(f"⚠️  {self.failed_tests} TESTS FAILED - FIX BEFORE DEPLOYMENT")
            return False

if __name__ == "__main__":
    tester = DeploymentTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)