#!/usr/bin/env python3
"""
Test script untuk mencoba akses Hyblock Capital API
Berdasarkan dokumentasi resmi dari hyblockcapital.com
"""

import requests
import json
import os
from datetime import datetime

def test_hyblock_api():
    """
    Test basic access ke Hyblock Capital API
    Menggunakan endpoint publik dan test credentials
    """
    
    print("🔍 Testing Hyblock Capital API Access...")
    
    # Endpoint URLs
    auth_url = 'https://auth-api.hyblockcapital.com/oauth2/token'
    api_base_url = 'https://api1.hyblockcapital.com/v1'
    
    # Test credentials (placeholder - perlu real credentials)
    test_data = {
        "client_id": "test_client_id",
        "client_secret": "test_client_secret", 
        "api_key": "test_api_key"
    }
    
    print(f"📡 Auth URL: {auth_url}")
    print(f"📡 API Base URL: {api_base_url}")
    
    # Step 1: Test authentication endpoint
    print("\n🔐 Step 1: Testing Authentication...")
    
    auth_data = {
        "grant_type": "client_credentials",
        "client_id": test_data["client_id"],
        "client_secret": test_data["client_secret"]
    }
    
    auth_headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    try:
        print("📤 Sending auth request...")
        auth_response = requests.post(
            auth_url, 
            data=auth_data, 
            headers=auth_headers,
            timeout=10
        )
        
        print(f"🔍 Auth Response Status: {auth_response.status_code}")
        print(f"🔍 Auth Response Headers: {dict(auth_response.headers)}")
        
        if auth_response.status_code == 200:
            auth_json = auth_response.json()
            print(f"✅ Auth successful: {auth_json}")
            access_token = auth_json.get('access_token')
        else:
            print(f"❌ Auth failed: {auth_response.status_code}")
            print(f"📄 Response: {auth_response.text}")
            access_token = None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Auth request failed: {e}")
        access_token = None
    
    # Step 2: Test API endpoint (with or without token)
    print("\n📊 Step 2: Testing API Endpoint...")
    
    api_endpoint = f"{api_base_url}/bidAsk"
    query_params = {
        "coin": "BTC",
        "timeframe": "1m", 
        "exchange": "Binance",
        "limit": 5
    }
    
    api_headers = {}
    if access_token:
        api_headers = {
            "Authorization": f"Bearer {access_token}",
            "x-api-key": test_data["api_key"]
        }
    
    try:
        print("📤 Sending API request...")
        print(f"🔍 Endpoint: {api_endpoint}")
        print(f"🔍 Params: {query_params}")
        print(f"🔍 Headers: {api_headers}")
        
        api_response = requests.get(
            api_endpoint,
            params=query_params,
            headers=api_headers,
            timeout=10
        )
        
        print(f"🔍 API Response Status: {api_response.status_code}")
        print(f"🔍 API Response Headers: {dict(api_response.headers)}")
        
        if api_response.status_code == 200:
            api_json = api_response.json()
            print(f"✅ API successful: {json.dumps(api_json, indent=2)}")
        else:
            print(f"❌ API failed: {api_response.status_code}")
            print(f"📄 Response: {api_response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ API request failed: {e}")
    
    # Step 3: Test without credentials (check error response)
    print("\n🔍 Step 3: Testing Without Credentials...")
    
    try:
        no_auth_response = requests.get(
            api_endpoint,
            params=query_params,
            timeout=10
        )
        
        print(f"🔍 No-Auth Response Status: {no_auth_response.status_code}")
        print(f"📄 No-Auth Response: {no_auth_response.text}")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ No-auth request failed: {e}")
    
    print("\n📋 Summary:")
    print("- Hyblock Capital API memerlukan credentials yang valid")
    print("- API hanya tersedia untuk Professional plan ($499/bulan)")
    print("- Basic plan (gratis) tidak mendapat akses API")
    print("- Perlu mendaftar dan upgrade ke Professional untuk akses penuh")

if __name__ == "__main__":
    test_hyblock_api()