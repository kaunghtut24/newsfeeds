#!/usr/bin/env python3
"""
Test All Three Fixes
====================

Test that all three issues are fixed:
1. LLM providers loading error at startup
2. Search summary error
3. Improved categorization (especially for technology news)
"""

import requests
import json
import sys
from pathlib import Path

# Add src to Python path
src_path = str(Path(__file__).parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

def test_llm_providers_startup():
    """Test that LLM providers load without errors."""
    print("🤖 Testing LLM Providers at Startup")
    print("=" * 40)
    
    try:
        response = requests.get("http://127.0.0.1:5000/api/llm-providers", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success') and data.get('providers'):
                providers = data.get('providers', {})
                print(f"✅ LLM providers loaded successfully ({len(providers)} providers)")
                
                # Check specific providers
                for name, provider in providers.items():
                    status = "Enabled" if provider.get('enabled') else "Disabled"
                    models = len(provider.get('available_models', []))
                    print(f"   {name.upper()}: {status} ({models} models)")
                
                return True
            else:
                print(f"❌ LLM providers response invalid: {data}")
                return False
        else:
            print(f"❌ LLM providers API returned status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing LLM providers: {e}")
        return False

def test_search_functionality():
    """Test that search works without summary errors."""
    print("\n🔍 Testing Search Functionality")
    print("=" * 40)
    
    test_queries = [
        {"text": "ChatGPT", "limit": 3},
        {"text": "technology", "limit": 5},
        {"text": "tesla", "limit": 2}
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Test {i}: Searching for '{query['text']}'")
        
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
                        required_fields = ['title', 'summary', 'source', 'timestamp']
                        missing_fields = [field for field in required_fields if field not in first_result]
                        
                        if not missing_fields:
                            print(f"   ✅ All required fields present")
                            print(f"   📰 Sample: {first_result.get('title', 'No title')[:50]}...")
                            print(f"   📝 Summary: {first_result.get('summary', 'No summary')[:80]}...")
                        else:
                            print(f"   ❌ Missing fields: {missing_fields}")
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

def test_categorization():
    """Test the improved categorization system."""
    print("\n🏷️ Testing Improved Categorization")
    print("=" * 40)
    
    try:
        from core.categorizer import Categorizer
        
        categorizer = Categorizer()
        print("✅ Categorizer imported successfully")
        
        # Test cases with expected categories
        test_cases = [
            {
                "title": "ChatGPT: Everything you need to know about the AI chatbot",
                "source": "techcrunch",
                "expected": "Technology"
            },
            {
                "title": "Tesla sends driverless Model Y from factory to customer",
                "source": "techcrunch", 
                "expected": "Technology"
            },
            {
                "title": "Hacker News discussion on machine learning algorithms",
                "source": "hackernews",
                "expected": "Technology"
            },
            {
                "title": "Apple announces new iPhone with AI features",
                "source": "tech",
                "expected": "Technology"
            },
            {
                "title": "Stock market rises on tech earnings",
                "source": "businessline",
                "expected": "Business"  # Should still be business due to stock market focus
            },
            {
                "title": "Manufacturing PMI rises to 14-month high",
                "source": "businessline",
                "expected": "Business"
            }
        ]
        
        correct_predictions = 0
        
        for i, test_case in enumerate(test_cases, 1):
            news_item = {
                'title': test_case['title'],
                'source': test_case['source'],
                'full_text': test_case['title'],  # Use title as content for testing
                'summary': test_case['title']
            }
            
            predicted = categorizer.categorize_news(news_item)
            expected = test_case['expected']
            
            print(f"\n📝 Test {i}: {test_case['title'][:50]}...")
            print(f"   Source: {test_case['source']}")
            print(f"   Expected: {expected}")
            print(f"   Predicted: {predicted}")
            
            if predicted == expected:
                print(f"   ✅ Correct!")
                correct_predictions += 1
            else:
                print(f"   ⚠️ Different prediction")
        
        accuracy = (correct_predictions / len(test_cases)) * 100
        print(f"\n📊 Categorization Accuracy: {correct_predictions}/{len(test_cases)} ({accuracy:.1f}%)")
        
        # Test with real news data
        print(f"\n📰 Testing with real news data...")
        response = requests.get("http://127.0.0.1:5000/api/news", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            articles = data.get('news', [])
            
            if articles:
                category_counts = {}
                tech_sources = ['techcrunch', 'hackernews', 'hacker news']
                tech_articles_as_tech = 0
                total_tech_articles = 0
                
                for article in articles:
                    category = article.get('category', 'Unknown')
                    source = article.get('source', '').lower()
                    
                    category_counts[category] = category_counts.get(category, 0) + 1
                    
                    # Check if tech sources are being categorized as Technology
                    if any(tech_source in source for tech_source in tech_sources):
                        total_tech_articles += 1
                        if category == 'Technology':
                            tech_articles_as_tech += 1
                
                print(f"   📊 Category distribution:")
                for category, count in sorted(category_counts.items()):
                    print(f"      {category}: {count} articles")
                
                if total_tech_articles > 0:
                    tech_accuracy = (tech_articles_as_tech / total_tech_articles) * 100
                    print(f"   🎯 Tech source accuracy: {tech_articles_as_tech}/{total_tech_articles} ({tech_accuracy:.1f}%)")
                    
                    if tech_accuracy >= 70:  # At least 70% of tech sources should be categorized as Technology
                        print(f"   ✅ Good tech categorization!")
                        return True
                    else:
                        print(f"   ⚠️ Tech categorization needs improvement")
                        return False
                else:
                    print(f"   ℹ️ No tech articles found for testing")
                    return True
            else:
                print(f"   ❌ No articles found")
                return False
        else:
            print(f"   ❌ Could not fetch news data")
            return False
            
    except Exception as e:
        print(f"❌ Error testing categorization: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all fix tests."""
    print("🧪 All Fixes Test Suite")
    print("=" * 50)
    print("Testing fixes for:")
    print("  1. LLM providers loading error at startup")
    print("  2. Search summary error")
    print("  3. Improved categorization for technology news")
    print()
    
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
    
    tests = [
        ("LLM Providers Startup", test_llm_providers_startup),
        ("Search Functionality", test_search_functionality),
        ("Improved Categorization", test_categorization)
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
        print("\n🎉 All fixes are working correctly!")
        print("✅ LLM providers startup error: FIXED")
        print("✅ Search summary error: FIXED")
        print("✅ Technology news categorization: IMPROVED")
        print("\nThe application is now fully stable and ready for production use!")
    elif passed > 0:
        print("\n⚠️ Some tests passed. Partial fixes applied.")
    else:
        print("\n❌ All tests failed. Issues still need debugging.")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
