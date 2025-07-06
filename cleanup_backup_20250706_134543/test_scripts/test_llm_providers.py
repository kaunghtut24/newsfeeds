#!/usr/bin/env python3
"""
Test LLM Providers API
======================

Test the LLM providers API endpoint and functionality.
"""

import requests
import json

def test_llm_providers_api():
    """Test the LLM providers API endpoint."""
    print("🤖 Testing LLM Providers API")
    print("=" * 40)
    
    try:
        response = requests.get("http://127.0.0.1:5000/api/llm-providers", timeout=10)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"Success: {data.get('success', False)}")
            
            if data.get('success'):
                providers = data.get('providers', {})
                available_providers = data.get('available_providers', [])
                available_models = data.get('available_models', {})
                budget = data.get('budget', {})
                
                print(f"Total Providers: {len(providers)}")
                print(f"Available Providers: {len(available_providers)}")
                
                print("\n📋 Provider Details:")
                for name, provider in providers.items():
                    status = "✅ Enabled" if provider.get('enabled') else "❌ Disabled"
                    model_count = len(provider.get('available_models', []))
                    print(f"   {name.upper()}: {status} ({model_count} models)")
                    
                    if provider.get('enabled') and model_count > 0:
                        models = provider.get('available_models', [])[:3]  # Show first 3
                        print(f"      Models: {', '.join(models)}")
                
                print(f"\n💰 Budget Info:")
                print(f"   Daily Limit: ${budget.get('daily_limit', 0)}")
                print(f"   Monthly Limit: ${budget.get('monthly_limit', 0)}")
                print(f"   Daily Usage: ${budget.get('current_daily_usage', 0)}")
                print(f"   Monthly Usage: ${budget.get('current_monthly_usage', 0)}")
                
                return True
            else:
                print(f"❌ API returned success=False")
                print(f"Error: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

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
            models = data.get('models', [])
            
            print(f"Available: {'✅ Yes' if available else '❌ No'}")
            print(f"Message: {message}")
            
            if available and models:
                print(f"Models: {len(models)} available")
                for model in models[:5]:  # Show first 5
                    print(f"   - {model}")
            
            return available
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_llm_config_file():
    """Test the LLM config file directly."""
    print("\n📄 Testing LLM Config File")
    print("=" * 30)
    
    try:
        with open('llm_config.json', 'r') as f:
            config = json.load(f)
        
        print("✅ Config file loaded successfully")
        
        providers = []
        for key, value in config.items():
            if key not in ['budget', 'fallback_strategy', 'default_model_preferences']:
                providers.append(key)
        
        print(f"Providers in config: {len(providers)}")
        for provider in providers:
            enabled = config[provider].get('enabled', False)
            models = list(config[provider].get('models', {}).keys())
            print(f"   {provider}: {'Enabled' if enabled else 'Disabled'} ({len(models)} models)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading config: {e}")
        return False

def main():
    """Run all LLM provider tests."""
    print("🧪 LLM Providers Test Suite")
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
    config_test = test_llm_config_file()
    api_test = test_llm_providers_api()
    ollama_test = test_ollama_status()
    
    print("\n" + "=" * 50)
    print("🎯 Final Results:")
    print(f"   Config File: {'✅ Working' if config_test else '❌ Failed'}")
    print(f"   LLM Providers API: {'✅ Working' if api_test else '❌ Failed'}")
    print(f"   Ollama Status: {'✅ Working' if ollama_test else '❌ Failed'}")
    
    if api_test:
        print("\n🎉 LLM Providers functionality is working correctly!")
        print("You can now:")
        print("   1. View LLM providers in the web interface")
        print("   2. See provider status and model availability")
        print("   3. Monitor usage and costs")
        print("   4. Enable/disable providers as needed")
    else:
        print("\n❌ LLM Providers functionality needs debugging.")
    
    return api_test and config_test

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
