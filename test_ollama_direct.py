#!/usr/bin/env python3
"""
Test Ollama provider directly to diagnose AI summarization issues
"""

import sys
import asyncio
sys.path.insert(0, 'src')

from core.llm_providers.ollama_provider import OllamaProvider
from core.llm_providers.base_provider import LLMConfig

def test_ollama_sync():
    """Test Ollama with synchronous method"""
    print("🧪 Testing Ollama Provider (Synchronous Method)...")
    
    config = LLMConfig(
        provider_name="ollama",
        enabled=True,
        base_url="http://localhost:11434",
        timeout=30
    )
    
    provider = OllamaProvider(config)
    
    # Test if Ollama is available
    print(f"📡 Ollama available: {provider.is_available()}")
    
    if not provider.is_available():
        print("❌ Ollama is not available. Make sure it's running.")
        return False
    
    # Test models
    models = provider.get_models()
    print(f"🤖 Available models: {models}")
    
    if not models:
        print("❌ No models available in Ollama")
        return False
    
    # Test summarization
    test_text = """
    BRICS nations' interest in national currency trade is not de-dollarisation, according to MEA official.
    The US dollar will continue to exist in global trade, said the official. BRICS nations will work on 
    increasing their understanding of the importance of having alternative payment systems.
    """
    
    print("📝 Testing summarization...")
    try:
        # Use the synchronous method directly
        response = provider._summarize_sync(test_text, model=models[0] if models else 'llama3:8b')
        
        print(f"✅ Summarization successful!")
        print(f"📄 Summary: {response.content}")
        print(f"🤖 Model: {response.model}")
        print(f"⏱️  Response time: {response.response_time:.2f}s")
        print(f"🎯 Success: {response.success}")
        
        return response.success
        
    except Exception as e:
        print(f"❌ Summarization failed: {str(e)}")
        return False

async def test_ollama_async():
    """Test Ollama with async method"""
    print("\n🧪 Testing Ollama Provider (Async Method)...")
    
    config = LLMConfig(
        provider_name="ollama",
        enabled=True,
        base_url="http://localhost:11434",
        timeout=30
    )
    
    provider = OllamaProvider(config)
    
    test_text = """
    BRICS nations' interest in national currency trade is not de-dollarisation, according to MEA official.
    The US dollar will continue to exist in global trade, said the official.
    """
    
    try:
        response = await provider.summarize(test_text)
        
        print(f"✅ Async summarization successful!")
        print(f"📄 Summary: {response.content}")
        print(f"🎯 Success: {response.success}")
        
        return response.success
        
    except Exception as e:
        print(f"❌ Async summarization failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔧 Testing Ollama AI Summarization\n")
    
    # Test synchronous method
    sync_success = test_ollama_sync()
    
    # Test async method
    try:
        async_success = asyncio.run(test_ollama_async())
    except Exception as e:
        print(f"❌ Async test failed with error: {str(e)}")
        async_success = False
    
    print(f"\n📊 Test Results:")
    print(f"   Synchronous Method: {'✅ PASS' if sync_success else '❌ FAIL'}")
    print(f"   Asynchronous Method: {'✅ PASS' if async_success else '❌ FAIL'}")
    
    if sync_success:
        print("\n🎉 Ollama AI summarization is working with synchronous method!")
    elif async_success:
        print("\n⚠️  Only async method works. Need to fix sync integration.")
    else:
        print("\n❌ Both methods failed. Ollama integration needs debugging.")
