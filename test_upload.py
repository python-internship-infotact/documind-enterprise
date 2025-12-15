#!/usr/bin/env python3
"""
Quick test script for DocuMind Enterprise API
"""
import requests
import json
import time

API_BASE = "http://localhost:8000"

def test_api():
    print("🧪 Testing DocuMind Enterprise API")
    print("=" * 40)
    
    # Test 1: Health check
    print("1️⃣ Testing health endpoint...")
    try:
        response = requests.get(f"{API_BASE}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Status: {response.json().get('status', 'unknown')}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Is the server running?")
        print("   Run: python start.py")
        return False
    
    # Test 2: Root endpoint
    print("\n2️⃣ Testing root endpoint...")
    try:
        response = requests.get(f"{API_BASE}/")
        if response.status_code == 200:
            data = response.json()
            print("✅ Root endpoint working")
            print(f"   Message: {data.get('message')}")
            print(f"   Version: {data.get('version')}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Search endpoint (without documents)
    print("\n3️⃣ Testing search endpoint...")
    try:
        response = requests.get(f"{API_BASE}/search", params={"query": "test query"})
        if response.status_code == 200:
            data = response.json()
            print("✅ Search endpoint working")
            print(f"   Results: {len(data.get('results', []))}")
        else:
            print(f"❌ Search failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: Stats endpoint
    print("\n4️⃣ Testing stats endpoint...")
    try:
        response = requests.get(f"{API_BASE}/stats")
        if response.status_code == 200:
            print("✅ Stats endpoint working")
        else:
            print(f"❌ Stats failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n🎉 Basic API tests completed!")
    print("\n📝 Next steps:")
    print("   1. Configure your .env file with API keys")
    print("   2. Upload a PDF document via POST /documents/upload")
    print("   3. Test search functionality with real documents")
    
    return True

if __name__ == "__main__":
    test_api()