#!/usr/bin/env python3
"""
Test Error Fixes
================

Test that both the LLM initialization and search timestamp errors are fixed.
"""

import requests
import json
import time

def test_server_startup():
    """Test that server starts without LLM errors."""
    print("🚀 Testing Server Startup")
    print("=" * 30)
    
    try:
        # Test basic connectivity
        response = requests.get("http://127.0.0.1:5000/api/news", timeout=10)
        
        if response.status_code == 200:
            print("✅ Server is running and responding")
            return True
        else:
            print(f"❌ Server returned status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        return False

def test_llm_initialization():
    """Test that LLM providers are loading correctly."""
    print("\n🤖 Testing LLM Initialization")
    print("=" * 30)
    
    try:
        response = requests.get("http://127.0.0.1:5000/api/llm-providers", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success'):
                providers = data.get('providers', {})
                print(f"✅ LLM providers loaded successfully ({len(providers)} providers)")
                
                # Check if Ollama is enabled
                ollama = providers.get('ollama', {})
                if ollama.get('enabled'):
                    models = ollama.get('available_models', [])
                    print(f"✅ Ollama is enabled with {len(models)} models")
                    return True
                else:
                    print("⚠️ Ollama is not enabled")
                    return True  # Not an error, just configuration
            else:
                print(f"❌ LLM providers failed to load: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ LLM providers API returned status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing LLM providers: {e}")
        return False

def test_search_functionality():
    """Test that search works without timestamp errors."""
    print("\n🔍 Testing Search Functionality")
    print("=" * 30)
    
    test_queries = [
        {"text": "india", "limit": 3},
        {"text": "technology", "limit": 2},
        {"text": "", "limit": 5}  # Empty search (all articles)
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Test {i}: {query}")
        
        try:
            response = requests.post(
                "http://127.0.0.1:5000/api/search",
                json=query,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success'):
                    results = data.get('results', [])
                    print(f"   ✅ Search successful: {len(results)} results")
                    
                    # Check if results have required fields
                    if results:
                        first_result = results[0]
                        required_fields = ['title', 'timestamp', 'source', 'summary']
                        missing_fields = [field for field in required_fields if field not in first_result]
                        
                        if not missing_fields:
                            print(f"   ✅ All required fields present")
                            print(f"   📰 Sample: {first_result.get('title', 'No title')[:50]}...")
                        else:
                            print(f"   ⚠️ Missing fields: {missing_fields}")
                            return False
                else:
                    print(f"   ❌ Search failed: {data.get('error', 'Unknown error')}")
                    return False
            else:
                print(f"   ❌ Search API returned status {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error in search test: {e}")
            return False
    
    print("\n✅ All search tests passed!")
    return True

def test_ollama_status():
    """Test Ollama status endpoint."""
    print("\n🦙 Testing Ollama Status")
    print("=" * 30)
    
    try:
        response = requests.get("http://127.0.0.1:5000/api/ollama-status", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            available = data.get('available', False)
            message = data.get('message', 'No message')
            
            print(f"Available: {'✅ Yes' if available else '❌ No'}")
            print(f"Message: {message}")
            
            return True
        else:
            print(f"❌ Ollama status API returned status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Ollama status: {e}")
        return False

def test_news_loading():
    """Test that news articles load correctly."""
    print("\n📰 Testing News Loading")
    print("=" * 30)
    
    try:
        response = requests.get("http://127.0.0.1:5000/api/news", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success'):
                articles = data.get('news', [])
                print(f"✅ News loaded successfully: {len(articles)} articles")
                
                if articles:
                    first_article = articles[0]
                    print(f"   📰 Sample: {first_article.get('title', 'No title')[:50]}...")
                    print(f"   🏷️ Source: {first_article.get('source', 'Unknown')}")
                    print(f"   📅 Timestamp: {first_article.get('timestamp', 'No timestamp')}")
                
                return True
            else:
                print(f"❌ News loading failed: {data.get('message', 'Unknown error')}")
                return False
        else:
            print(f"❌ News API returned status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing news loading: {e}")
        return False

def main():
    """Run all error fix tests."""
    print("🧪 Error Fixes Test Suite")
    print("=" * 50)
    print("Testing fixes for:")
    print("  1. LLM not loaded error at server startup")
    print("  2. Search timestamp error")
    print()
    
    tests = [
        ("Server Startup", test_server_startup),
        ("LLM Initialization", test_llm_initialization),
        ("News Loading", test_news_loading),
        ("Search Functionality", test_search_functionality),
        ("Ollama Status", test_ollama_status)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 All error fixes are working correctly!")
        print("✅ LLM initialization error: FIXED")
        print("✅ Search timestamp error: FIXED")
        print("\nThe application is now stable and ready for use!")
    elif passed > 0:
        print("\n⚠️ Some tests passed. Partial fixes applied.")
    else:
        print("\n❌ All tests failed. Errors still need debugging.")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
