#!/usr/bin/env python3
"""
Test script untuk mencoba akses CoinGlass API
Melihat endpoint publik dan response structure
"""

import requests
import json
from datetime import datetime

def test_coinglass_api():
    """
    Test basic access ke CoinGlass API
    Cek endpoint publik dan error responses
    """
    
    print("🔍 Testing CoinGlass API Access...")
    
    # Base URLs
    base_url = 'https://open-api-v4.coinglass.com'
    
    # Test endpoints yang mungkin publik
    test_endpoints = [
        '/public/v4/futures/funding-rates',
        '/public/v4/futures/open-interest', 
        '/public/v4/futures/liquidation-map',
        '/api/pro/v1/futures/liquidation_history',
        '/api/pro/v1/futures/aggregated_liquidation_chart'
    ]
    
    print(f"📡 Base URL: {base_url}")
    
    # Test tanpa API key
    print("\n🔍 Testing Public Endpoints (No API Key)...")
    
    for endpoint in test_endpoints:
        try:
            full_url = f"{base_url}{endpoint}"
            print(f"\n📤 Testing: {endpoint}")
            
            # Test dengan parameter umum
            params = {
                'symbol': 'BTCUSDT',
                'time_type': '4h'
            }
            
            response = requests.get(
                full_url,
                params=params,
                timeout=10
            )
            
            print(f"🔍 Status: {response.status_code}")
            print(f"🔍 Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"✅ Success: {json.dumps(data, indent=2)[:500]}...")
                except:
                    print(f"✅ Success: {response.text[:500]}...")
            else:
                print(f"❌ Failed: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
    
    # Test dengan fake API key
    print("\n🔑 Testing With Fake API Key...")
    
    headers = {
        'X-API-KEY': 'test_api_key_12345'
    }
    
    test_endpoint = f"{base_url}/api/pro/v1/futures/liquidation_history"
    
    try:
        response = requests.get(
            test_endpoint,
            headers=headers,
            params={'symbol': 'BTCUSDT'},
            timeout=10
        )
        
        print(f"🔍 Status with fake key: {response.status_code}")
        print(f"📄 Response: {response.text}")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Request with fake key failed: {e}")
    
    # Test dokumentasi endpoint
    print("\n📚 Testing Documentation Endpoints...")
    
    doc_endpoints = [
        'https://docs.coinglass.com',
        'https://www.coinglass.com/api-docs'
    ]
    
    for doc_url in doc_endpoints:
        try:
            response = requests.get(doc_url, timeout=10)
            print(f"📚 {doc_url}: {response.status_code}")
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Doc request failed: {e}")
    
    print("\n📋 Summary:")
    print("- CoinGlass API tidak memiliki endpoint publik gratis")
    print("- Semua data liquidation memerlukan API key berbayar")
    print("- Plan termurah: $29/bulan (HOBBYIST)")
    print("- Alternative: Gunakan exchange APIs langsung (OKX, Binance)")

if __name__ == "__main__":
    test_coinglass_api()