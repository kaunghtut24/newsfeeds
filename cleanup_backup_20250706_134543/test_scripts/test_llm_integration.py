#!/usr/bin/env python3
"""
Test LLM Integration
===================

Test the LLM integration for news summarization functionality.
"""

import sys
import json
from pathlib import Path

# Add src to Python path
src_path = str(Path(__file__).parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

def test_ollama_connection():
    """Test direct connection to Ollama."""
    print("🔗 Testing Ollama connection...")
    
    try:
        import requests
        
        # Test Ollama API
        response = requests.get('http://localhost:11434/api/tags', timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            print(f"✅ Ollama is running with {len(models)} models")
            for model in models[:3]:  # Show first 3 models
                print(f"   - {model['name']}")
            return True
        else:
            print(f"❌ Ollama API returned status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error connecting to Ollama: {e}")
        return False

def test_multi_llm_summarizer():
    """Test the MultiLLMSummarizer class."""
    print("\n🤖 Testing MultiLLMSummarizer...")
    
    try:
        from core.multi_llm_summarizer import MultiLLMSummarizer
        
        # Initialize summarizer
        summarizer = MultiLLMSummarizer(config_file='llm_config.json')
        print("✅ MultiLLMSummarizer initialized")
        
        # Test with sample news item
        sample_news = [{
            'title': 'Test News Article',
            'description': 'This is a test news article about technology and innovation. It discusses various aspects of modern computing and artificial intelligence.',
            'content': 'This is a longer content for the test article. It contains more detailed information about the topic and provides comprehensive coverage of the subject matter.',
            'source': 'Test Source',
            'url': 'https://example.com/test'
        }]
        
        print("📝 Testing summarization with sample article...")
        
        # Test summarization
        summarized = summarizer.summarize_news_items(
            sample_news,
            preferred_model='llama3:8b'
        )
        
        if summarized and len(summarized) > 0:
            print("✅ Summarization successful!")
            print(f"   Original title: {sample_news[0]['title']}")
            print(f"   Summary: {summarized[0].get('summary', 'No summary')[:100]}...")
            return True
        else:
            print("❌ Summarization failed - no results")
            return False
            
    except Exception as e:
        print(f"❌ Error testing MultiLLMSummarizer: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_simple_ollama_request():
    """Test a simple direct request to Ollama."""
    print("\n🧪 Testing direct Ollama request...")
    
    try:
        import requests
        
        # Simple test prompt
        payload = {
            "model": "llama3:8b",
            "prompt": "Summarize this in one sentence: Technology is advancing rapidly.",
            "stream": False
        }
        
        response = requests.post(
            'http://localhost:11434/api/generate',
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Direct Ollama request successful!")
            print(f"   Response: {result.get('response', 'No response')[:100]}...")
            return True
        else:
            print(f"❌ Ollama request failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error with direct Ollama request: {e}")
        return False

def test_full_pipeline():
    """Test the full news processing pipeline with LLM."""
    print("\n🔄 Testing full pipeline with LLM...")
    
    try:
        # Load existing news data
        with open('data/news_data.json', 'r', encoding='utf-8') as f:
            articles = json.load(f)
        
        if not articles:
            print("❌ No news data available for testing")
            return False
        
        print(f"📰 Found {len(articles)} articles to test with")
        
        # Test with first article
        test_article = articles[0]
        print(f"   Testing with: {test_article.get('title', 'No title')}")
        
        from core.multi_llm_summarizer import MultiLLMSummarizer
        
        summarizer = MultiLLMSummarizer(config_file='llm_config.json')
        
        # Summarize single article
        result = summarizer.summarize_news_items(
            [test_article],
            preferred_model='llama3:8b'
        )
        
        if result and len(result) > 0:
            print("✅ Full pipeline test successful!")
            print(f"   Generated summary: {result[0].get('summary', 'No summary')[:150]}...")
            return True
        else:
            print("❌ Full pipeline test failed")
            return False
            
    except Exception as e:
        print(f"❌ Error in full pipeline test: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all LLM integration tests."""
    print("🧪 LLM Integration Test Suite")
    print("=" * 50)
    
    tests = [
        ("Ollama Connection", test_ollama_connection),
        ("Simple Ollama Request", test_simple_ollama_request),
        ("MultiLLMSummarizer", test_multi_llm_summarizer),
        ("Full Pipeline", test_full_pipeline)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running: {test_name}")
        print("-" * 30)
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
        print("🎉 All LLM integration tests passed! Ready for full functionality.")
    elif passed > 0:
        print("⚠️ Some tests passed. LLM integration partially working.")
    else:
        print("❌ All tests failed. LLM integration needs debugging.")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
