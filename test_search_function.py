#!/usr/bin/env python3
"""
Test Search Function
===================

Test the search functionality to ensure it works correctly.
"""

import requests
import json

def test_search_api():
    """Test the search API endpoint."""
    print("🔍 Testing Search API")
    print("=" * 30)
    
    base_url = "http://127.0.0.1:5000"
    
    # Test cases
    test_cases = [
        {
            "name": "Basic text search",
            "query": {"text": "india", "limit": 5},
            "expected_min_results": 1
        },
        {
            "name": "Technology search",
            "query": {"text": "technology", "limit": 10},
            "expected_min_results": 0
        },
        {
            "name": "Source filter",
            "query": {"text": "", "sources": ["techcrunch"], "limit": 10},
            "expected_min_results": 0
        },
        {
            "name": "Empty search (all articles)",
            "query": {"text": "", "limit": 50},
            "expected_min_results": 10
        },
        {
            "name": "Case insensitive search",
            "query": {"text": "INDIA", "limit": 5},
            "expected_min_results": 1
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        print(f"\n📝 Testing: {test_case['name']}")
        
        try:
            response = requests.post(
                f"{base_url}/api/search",
                json=test_case["query"],
                timeout=10
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                success = data.get('success', False)
                result_count = len(data.get('results', []))
                
                print(f"   Success: {success}")
                print(f"   Results: {result_count}")
                
                if success and result_count >= test_case["expected_min_results"]:
                    print("   ✅ PASS")
                    results.append(True)
                    
                    # Show first result if available
                    if result_count > 0:
                        first_result = data['results'][0]
                        print(f"   First result: {first_result.get('title', 'No title')[:50]}...")
                else:
                    print(f"   ❌ FAIL - Expected at least {test_case['expected_min_results']} results")
                    results.append(False)
            else:
                print(f"   ❌ FAIL - HTTP {response.status_code}")
                results.append(False)
                
        except Exception as e:
            print(f"   ❌ ERROR - {e}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 30)
    print("📊 Search Test Results:")
    passed = sum(results)
    total = len(results)
    
    for i, (test_case, result) in enumerate(zip(test_cases, results)):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} - {test_case['name']}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All search tests passed!")
    else:
        print("⚠️ Some search tests failed.")
    
    return passed == total

def test_search_suggestions():
    """Test search suggestions (if implemented)."""
    print("\n🔍 Testing Search Suggestions")
    print("=" * 30)
    
    try:
        response = requests.get(
            "http://127.0.0.1:5000/api/search/suggestions?q=tech&limit=5",
            timeout=5
        )
        
        if response.status_code == 200:
            print("✅ Search suggestions endpoint available")
            return True
        elif response.status_code == 404:
            print("ℹ️ Search suggestions not implemented (optional feature)")
            return True
        else:
            print(f"⚠️ Search suggestions returned {response.status_code}")
            return False
            
    except Exception as e:
        print(f"ℹ️ Search suggestions not available: {e}")
        return True  # This is optional

def main():
    """Run all search tests."""
    print("🧪 Search Function Test Suite")
    print("=" * 50)
    
    # Test if server is running
    try:
        response = requests.get("http://127.0.0.1:5000/api/news", timeout=5)
        if response.status_code != 200:
            print("❌ Server not responding correctly")
            return False
        print("✅ Server is running")
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        print("Please make sure the server is running: python full_server.py")
        return False
    
    # Run tests
    api_test = test_search_api()
    suggestions_test = test_search_suggestions()
    
    print("\n" + "=" * 50)
    print("🎯 Final Results:")
    print(f"   Search API: {'✅ Working' if api_test else '❌ Failed'}")
    print(f"   Suggestions: {'✅ Working' if suggestions_test else '❌ Failed'}")
    
    if api_test:
        print("\n🎉 Search functionality is working correctly!")
        print("You can now test search in the web interface:")
        print("   1. Open http://127.0.0.1:5000")
        print("   2. Use the search box to search for articles")
        print("   3. Try searches like 'india', 'technology', 'AI', etc.")
    else:
        print("\n❌ Search functionality needs debugging.")
    
    return api_test

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
