#!/usr/bin/env python3
"""
Test Reasoning Model Issue
==========================

Test to reproduce and verify the fix for reasoning models that show their thinking process
before providing the final answer.
"""

import requests
import json
import sys
from pathlib import Path

# Add src to Python path
src_path = str(Path(__file__).parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

def test_reasoning_model_output():
    """Test how reasoning models handle summarization."""
    print("🧠 Testing Reasoning Model Output")
    print("=" * 40)
    
    try:
        from core.llm_providers.ollama_provider import OllamaProvider
        from core.llm_providers.base_provider import LLMConfig
        
        # Test article about xAI funding
        test_article = """
        xAI, Elon Musk's artificial intelligence startup, has raised $10 billion in a new funding round, 
        bringing the company's valuation to $50 billion. The funding will be used to expand xAI's 
        computing infrastructure and accelerate the development of its Grok AI assistant. Major investors 
        include venture capital firms and sovereign wealth funds. The company plans to compete directly 
        with OpenAI and other major AI companies in the rapidly growing artificial intelligence market.
        """
        
        # Get available models
        response = requests.get("http://127.0.0.1:5000/api/ollama-status", timeout=10)
        data = response.json()
        
        if not data.get('available'):
            print("❌ Ollama not available")
            return False
        
        models = data.get('models', [])
        print(f"📊 Available models: {models}")
        
        # Test with reasoning models (qwen3, deepseek, etc.)
        reasoning_models = [m for m in models if any(keyword in m.lower() for keyword in ['qwen', 'deepseek', 'reasoning'])]
        
        if not reasoning_models:
            print("⚠️ No reasoning models found, testing with available models")
            reasoning_models = models[:2]  # Test first 2 models
        
        print(f"🧠 Testing reasoning models: {reasoning_models}")
        
        for model in reasoning_models:
            print(f"\n🔍 Testing model: {model}")
            
            # Create provider
            config = LLMConfig(
                provider_name="ollama",
                enabled=True,
                api_key=None,
                priority=1,
                models={model: {"max_tokens": 200}},
                rate_limits={},
                timeout=30
            )
            
            provider = OllamaProvider(config)
            
            # Test summarization
            try:
                response = provider._summarize_sync(test_article, model=model)
                
                if response.success:
                    content = response.content
                    print(f"✅ Model: {model}")
                    print(f"📝 Raw output length: {len(content)} characters")
                    print(f"📄 Content preview:")
                    print(f"   {content[:200]}...")
                    
                    # Check for reasoning patterns
                    reasoning_indicators = [
                        "let me", "i need to", "first", "the user wants",
                        "they specified", "i should", "let me read",
                        "okay,", "alright,", "so,", "well,", "hmm,",
                        "thinking", "consider", "analyze"
                    ]
                    
                    has_reasoning = any(indicator in content.lower() for indicator in reasoning_indicators)
                    
                    if has_reasoning:
                        print(f"⚠️ ISSUE DETECTED: Contains reasoning text")
                        print(f"   Reasoning indicators found in output")
                        return False
                    else:
                        print(f"✅ Clean output: No reasoning text detected")
                        
                    # Check if output is complete
                    if content.endswith((".", "!", "?")):
                        print(f"✅ Complete sentence ending")
                    else:
                        print(f"⚠️ ISSUE DETECTED: Incomplete output")
                        print(f"   Output ends with: '{content[-20:]}'")
                        return False
                        
                else:
                    print(f"❌ Summarization failed: {response.error_message}")
                    return False
                    
            except Exception as e:
                print(f"❌ Error with model {model}: {e}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing reasoning models: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_current_system_with_reasoning_model():
    """Test the current system with a reasoning model."""
    print("\n🌐 Testing Current System with Reasoning Model")
    print("=" * 50)
    
    try:
        # Set a reasoning model
        models_response = requests.get("http://127.0.0.1:5000/api/ollama-status", timeout=10)
        models_data = models_response.json()
        
        if not models_data.get('available'):
            print("❌ Ollama not available")
            return False
        
        models = models_data.get('models', [])
        reasoning_model = None
        
        # Find a reasoning model
        for model in models:
            if any(keyword in model.lower() for keyword in ['qwen', 'deepseek']):
                reasoning_model = model
                break
        
        if not reasoning_model:
            print("⚠️ No reasoning model available for testing")
            return True
        
        print(f"🧠 Testing with reasoning model: {reasoning_model}")
        
        # Set the model
        set_response = requests.post(
            "http://127.0.0.1:5000/api/ollama-model",
            json={'model': reasoning_model},
            timeout=10
        )
        
        if not set_response.json().get('success'):
            print(f"❌ Failed to set model {reasoning_model}")
            return False
        
        print(f"✅ Model set to: {reasoning_model}")
        
        # Trigger news processing
        print("📰 Triggering news fetch to test summarization...")
        fetch_response = requests.post("http://127.0.0.1:5000/api/fetch-news", timeout=60)
        
        if fetch_response.status_code != 200:
            print(f"❌ News fetch failed: {fetch_response.status_code}")
            return False
        
        print("✅ News fetch completed")
        
        # Check the results
        news_response = requests.get("http://127.0.0.1:5000/api/news", timeout=10)
        if news_response.status_code != 200:
            print("❌ Failed to get news data")
            return False
        
        news_data = news_response.json()
        articles = news_data.get('articles', [])
        
        if not articles:
            print("⚠️ No articles found")
            return True
        
        # Check first few articles for reasoning text
        issues_found = 0
        
        for i, article in enumerate(articles[:5]):
            summary = article.get('summary', '')
            model_used = article.get('llm_model', '')
            
            if model_used == reasoning_model and summary:
                print(f"\n📄 Article {i+1}: {article.get('title', '')[:50]}...")
                print(f"🤖 Model: {model_used}")
                print(f"📝 Summary: {summary[:150]}...")
                
                # Check for reasoning patterns
                reasoning_indicators = [
                    "let me", "i need to", "first", "the user wants",
                    "they specified", "i should", "let me read",
                    "okay,", "alright,", "so,", "well,", "hmm,",
                    "thinking", "consider", "analyze"
                ]
                
                has_reasoning = any(indicator in summary.lower() for indicator in reasoning_indicators)
                
                if has_reasoning:
                    print(f"⚠️ ISSUE: Contains reasoning text")
                    issues_found += 1
                else:
                    print(f"✅ Clean summary")
                
                # Check if complete
                if not summary.strip().endswith((".", "!", "?")):
                    print(f"⚠️ ISSUE: Incomplete summary")
                    issues_found += 1
        
        if issues_found > 0:
            print(f"\n❌ Found {issues_found} issues with reasoning model output")
            return False
        else:
            print(f"\n✅ All summaries clean and complete")
            return True
        
    except Exception as e:
        print(f"❌ Error testing current system: {e}")
        return False

def main():
    """Run reasoning model tests."""
    print("🧠 Reasoning Model Issue Test Suite")
    print("=" * 50)
    print("Testing how the system handles reasoning models that show their thinking process.")
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
        ("Direct Model Testing", test_reasoning_model_output),
        ("Current System Testing", test_current_system_with_reasoning_model)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*60}")
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Reasoning Model Test Results:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n✅ No reasoning model issues detected!")
    else:
        print("\n⚠️ Reasoning model issues found - fix needed")
        print("\nIssues to address:")
        print("- Reasoning models show thinking process in output")
        print("- Summaries may be incomplete or contain meta-commentary")
        print("- Need to extract final answer from reasoning output")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
