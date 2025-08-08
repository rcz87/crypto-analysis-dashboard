#!/usr/bin/env python3
"""
Debug deployment issues - find the real problem
"""
import os
import sys
import requests
import json

def test_local_endpoints():
    """Test local endpoints"""
    print("🔍 Testing Local Endpoints...")
    
    try:
        from main import app
        with app.test_client() as client:
            # Test status endpoint
            response = client.get('/api/gpts/status')
            print(f"Local /api/gpts/status: {response.status_code}")
            
            # Test trading signal
            response = client.get('/api/gpts/sinyal/tajam?symbol=BTCUSDT')
            print(f"Local /api/gpts/sinyal/tajam: {response.status_code}")
            
            # Test root
            response = client.get('/')
            print(f"Local /: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Local test failed: {e}")

def test_production_endpoints():
    """Test production endpoints"""
    print("\n🌐 Testing Production Endpoints...")
    
    base_urls = [
        "https://crypto-analysis-dashboard-rcz887.replit.app",
        "https://crypto-analysis-dashboard-rcz887.replit.dev"
    ]
    
    endpoints = [
        "/",
        "/api/gpts/status", 
        "/api/gpts/sinyal/tajam?symbol=BTCUSDT"
    ]
    
    for base_url in base_urls:
        print(f"\n📡 Testing {base_url}:")
        for endpoint in endpoints:
            try:
                url = f"{base_url}{endpoint}"
                response = requests.get(url, timeout=10, headers={
                    'User-Agent': 'ChatGPT/1.0'
                })
                print(f"  {endpoint}: {response.status_code}")
                if response.status_code != 404:
                    print(f"    Response: {response.text[:100]}...")
                    
            except Exception as e:
                print(f"  {endpoint}: ERROR - {e}")

def check_deployment_config():
    """Check deployment configuration"""
    print("\n⚙️  Checking Deployment Config...")
    
    # Check .replit file
    try:
        with open('.replit', 'r') as f:
            content = f.read()
            print("📄 .replit deployment section:")
            lines = content.split('\n')
            in_deployment = False
            for line in lines:
                if '[deployment]' in line:
                    in_deployment = True
                elif line.startswith('[') and in_deployment:
                    break
                elif in_deployment:
                    print(f"  {line}")
    except Exception as e:
        print(f"❌ Could not read .replit: {e}")

if __name__ == "__main__":
    test_local_endpoints()
    test_production_endpoints()
    check_deployment_config()
    
    print("\n🎯 DEBUGGING COMPLETE")
    print("📋 Check results above to identify the real issue")