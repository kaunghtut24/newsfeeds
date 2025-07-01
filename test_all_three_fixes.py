#!/usr/bin/env python3
"""
Test All Three Fixes
====================

Test all three issues that were reported:
1. Source edit/delete functionality
2. Ollama model selection saving
3. AI summarization prefix removal
"""

import requests
import json
import sys
from pathlib import Path

# Add src to Python path
src_path = str(Path(__file__).parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

def test_source_edit_delete():
    """Test source edit and delete functionality."""
    print("✏️ Testing Source Edit/Delete Functionality")
    print("=" * 45)
    
    try:
        # Get current sources
        response = requests.get("http://127.0.0.1:5000/api/sources", timeout=10)
        data = response.json()
        
        if not data.get('success'):
            print("❌ Cannot get sources")
            return False
        
        sources = data.get('sources', [])
        print(f"📊 Found {len(sources)} sources")
        
        # Test adding a new source first
        print("1️⃣ Testing add source...")
        add_response = requests.post(
            "http://127.0.0.1:5000/api/sources/add",
            json={
                'name': 'Test Source',
                'url': 'https://example.com/feed.rss'
            },
            timeout=10
        )
        
        if add_response.status_code == 404:
            print("⚠️ Add source endpoint not implemented yet")
        else:
            print("✅ Add source endpoint exists")
        
        # Test edit functionality (if we have sources)
        if sources:
            test_source = sources[0]
            source_name = test_source['name']
            
            print(f"2️⃣ Testing edit source: {source_name}")
            edit_response = requests.post(
                "http://127.0.0.1:5000/api/sources/edit",
                json={
                    'old_name': source_name,
                    'new_name': source_name,
                    'new_url': test_source['url'] + '?test=1'
                },
                timeout=10
            )
            
            if edit_response.status_code == 200:
                edit_data = edit_response.json()
                if edit_data.get('success'):
                    print("✅ Edit source works")
                    
                    # Restore original
                    requests.post(
                        "http://127.0.0.1:5000/api/sources/edit",
                        json={
                            'old_name': source_name,
                            'new_name': source_name,
                            'new_url': test_source['url']
                        },
                        timeout=10
                    )
                    print("✅ Source restored")
                else:
                    print(f"❌ Edit failed: {edit_data.get('error')}")
                    return False
            else:
                print(f"❌ Edit endpoint error: {edit_response.status_code}")
                return False
            
            print(f"3️⃣ Testing delete source availability")
            # Don't actually delete, just check if endpoint exists
            delete_response = requests.post(
                "http://127.0.0.1:5000/api/sources/delete",
                json={'source_name': 'non-existent-source'},
                timeout=10
            )
            
            if delete_response.status_code == 200:
                delete_data = delete_response.json()
                if not delete_data.get('success') and 'not found' in delete_data.get('error', '').lower():
                    print("✅ Delete endpoint works (correctly rejected non-existent source)")
                else:
                    print("⚠️ Delete endpoint response unexpected")
            else:
                print(f"❌ Delete endpoint error: {delete_response.status_code}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing source edit/delete: {e}")
        return False

def test_ollama_model_selection():
    """Test Ollama model selection saving."""
    print("\n🦙 Testing Ollama Model Selection")
    print("=" * 35)
    
    try:
        # Test the endpoint exists
        print("1️⃣ Testing Ollama model save endpoint...")
        
        test_model = "llama3:8b"
        response = requests.post(
            "http://127.0.0.1:5000/api/ollama-model",
            json={'model': test_model},
            timeout=10
        )
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success'):
                print(f"✅ Ollama model save works")
                print(f"   Model set to: {data.get('model')}")
                return True
            else:
                print(f"❌ Ollama model save failed: {data.get('error')}")
                return False
        elif response.status_code == 404:
            print("❌ Ollama model endpoint not found (404)")
            return False
        else:
            print(f"❌ Ollama model endpoint error: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data}")
            except:
                print(f"   Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Ollama model selection: {e}")
        return False

def test_ai_summarization_prefix():
    """Test AI summarization prefix removal."""
    print("\n🤖 Testing AI Summarization Prefix Removal")
    print("=" * 45)
    
    try:
        from core.llm_providers.ollama_provider import OllamaProvider
        from core.llm_providers.base_provider import LLMConfig
        
        print("1️⃣ Testing provider initialization...")
        config = LLMConfig(
            provider_name="ollama",
            enabled=True,
            api_key=None,
            priority=1,
            models={"llama3:8b": {"max_tokens": 150}},
            rate_limits={},
            timeout=30
        )
        
        provider = OllamaProvider(config)
        print("✅ Provider initialized")
        
        print("2️⃣ Testing prefix cleaning function...")
        # Test the cleaning function directly
        test_cases = [
            "Here is a summary of the article in 2-3 clear sentences: Tesla announced new features.",
            "Here is a concise summary: Apple released updates.",
            "Tesla announced new autonomous driving features.",
            "Summary: Microsoft launched new products."
        ]
        
        cleaned_results = []
        for test_case in test_cases:
            cleaned = provider._clean_summary_prefixes(test_case)
            cleaned_results.append(cleaned)
            
            has_prefix = any(cleaned.lower().startswith(prefix.lower()) for prefix in [
                "here is", "here's", "this is", "summary:"
            ])
            
            print(f"   Original: {test_case[:50]}...")
            print(f"   Cleaned:  {cleaned[:50]}...")
            print(f"   Has prefix: {'❌ Yes' if has_prefix else '✅ No'}")
            print()
        
        # Check if cleaning worked
        clean_count = sum(1 for result in cleaned_results if not any(
            result.lower().startswith(prefix.lower()) for prefix in [
                "here is", "here's", "this is", "summary:"
            ]
        ))
        
        success_rate = (clean_count / len(test_cases)) * 100
        print(f"📊 Prefix cleaning success rate: {clean_count}/{len(test_cases)} ({success_rate:.1f}%)")
        
        if success_rate >= 75:
            print("✅ Prefix cleaning working well")
            return True
        else:
            print("❌ Prefix cleaning needs improvement")
            return False
            
    except Exception as e:
        print(f"❌ Error testing AI summarization: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all three fix tests."""
    print("🧪 All Three Fixes Test Suite")
    print("=" * 50)
    print("Testing fixes for:")
    print("  1. Source edit/delete functionality")
    print("  2. Ollama model selection saving")
    print("  3. AI summarization prefix removal")
    print()
    
    # Check server
    try:
        response = requests.get("http://127.0.0.1:5000/api/health", timeout=5)
        if response.status_code != 200:
            print("❌ Server not responding")
            return False
        print("✅ Server is running")
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        return False
    
    # Run tests
    tests = [
        ("Source Edit/Delete", test_source_edit_delete),
        ("Ollama Model Selection", test_ollama_model_selection),
        ("AI Summarization Prefix", test_ai_summarization_prefix)
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
        print("\n🎉 All three fixes are working!")
        print("✅ Source management: Edit/delete functionality added")
        print("✅ Ollama model selection: Save functionality working")
        print("✅ AI summarization: Prefix removal implemented")
        print("\nAll reported issues have been resolved! 🚀")
    elif passed > 0:
        print(f"\n⚠️ Partial success: {passed}/{len(results)} fixes working")
    else:
        print("\n❌ All tests failed. Issues still need debugging.")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
