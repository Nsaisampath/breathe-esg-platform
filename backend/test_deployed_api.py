#!/usr/bin/env python
"""
Test script to verify production API is working.
Run this locally to test your deployed backend.

Usage:
    python test_deployed_api.py https://your-app.onrender.com
"""

import sys
import requests
import json

def test_api(base_url):
    """Test all major API endpoints"""
    
    api_url = f"{base_url}/api"
    
    print(f"\n{'='*60}")
    print(f"Testing Breathe ESG API")
    print(f"API Base URL: {api_url}")
    print(f"{'='*60}\n")
    
    tests = [
        ("Records List", f"{api_url}/records/?company_id=1"),
        ("Records Summary", f"{api_url}/records/summary/?company_id=1"),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, url in tests:
        try:
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ {test_name}")
                print(f"   Status: {response.status_code}")
                data = response.json()
                print(f"   Response: {json.dumps(data, indent=2)[:200]}...")
                passed += 1
            else:
                print(f"❌ {test_name}")
                print(f"   Status: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                failed += 1
                
        except requests.exceptions.ConnectionError:
            print(f"❌ {test_name}")
            print(f"   Error: Could not connect to {url}")
            failed += 1
        except Exception as e:
            print(f"❌ {test_name}")
            print(f"   Error: {str(e)}")
            failed += 1
        
        print()
    
    print(f"{'='*60}")
    print(f"Results: {passed} passed, {failed} failed")
    print(f"{'='*60}\n")
    
    return failed == 0

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_deployed_api.py https://your-app.onrender.com")
        sys.exit(1)
    
    base_url = sys.argv[1].rstrip('/')
    success = test_api(base_url)
    sys.exit(0 if success else 1)
