#!/usr/bin/env python3
"""
Test GPTs OpenAPI Schema - Verify all endpoints work with the schema
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_openapi_schema():
    """Test OpenAPI schema endpoints"""
    print("🔍 Testing GPTs OpenAPI Schema")
    print("=" * 50)
    
    # Test schema endpoint
    schema_response = requests.get(f"{BASE_URL}/openapi.json")
    if schema_response.status_code == 200:
        schema = schema_response.json()
        print(f"✅ OpenAPI Schema: {schema['openapi']} - {schema['info']['title']}")
        
        # Count operations
        operations = []
        for path, methods in schema['paths'].items():
            for method, details in methods.items():
                operations.append(f"{method.upper()} {path} ({details['operationId']})")
        
        print(f"📊 Total Operations: {len(operations)}")
        for i, op in enumerate(operations, 1):
            print(f"   {i:2d}. {op}")
    else:
        print(f"❌ Schema Error: HTTP {schema_response.status_code}")
    
    # Test well-known endpoint
    well_known = requests.get(f"{BASE_URL}/.well-known/openapi.json")
    if well_known.status_code == 200:
        print("✅ Well-known endpoint working")
    else:
        print(f"❌ Well-known error: HTTP {well_known.status_code}")
    
    # Test API docs
    docs = requests.get(f"{BASE_URL}/api/docs")
    if docs.status_code == 200:
        docs_data = docs.json()
        print(f"✅ API Docs: {docs_data['title']}")
        print(f"📋 ChatGPT Setup URL: {docs_data['chatgpt_setup']['import_url']}")
    else:
        print(f"❌ Docs error: HTTP {docs.status_code}")
    
    print("\n🎯 ChatGPT Custom GPT Setup Instructions:")
    print(f"1. Go to ChatGPT Custom GPTs")
    print(f"2. Create new GPT and go to Actions")
    print(f"3. Import schema from: {BASE_URL}/openapi.json")
    print(f"4. Test with commands like 'Analisis BTC' or 'Cek status sistem'")

if __name__ == "__main__":
    test_openapi_schema()