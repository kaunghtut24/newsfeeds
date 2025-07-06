#!/usr/bin/env python3
"""
Multi-LLM Demo Script
Demonstrates the new multi-LLM integration capabilities
"""

import asyncio
import os
import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.multi_llm_summarizer import MultiLLMSummarizer

async def main():
    print("🤖 Multi-LLM Integration Demo")
    print("=" * 50)
    
    # Initialize the multi-LLM summarizer
    print("📡 Initializing Multi-LLM Summarizer...")
    summarizer = MultiLLMSummarizer(config_file='llm_config.json')
    
    # Check available providers
    print("\n🔍 Checking Available Providers...")
    available_providers = summarizer.get_available_providers()
    all_models = summarizer.get_available_models()
    
    print(f"✅ Available Providers: {', '.join(available_providers) if available_providers else 'None'}")
    
    for provider, models in all_models.items():
        print(f"   📋 {provider.upper()}: {', '.join(models[:3])}{'...' if len(models) > 3 else ''}")
    
    # Perform health check
    print("\n🏥 Performing Health Check...")
    health_results = await summarizer.health_check_all()
    
    for provider, is_healthy in health_results.items():
        status = "✅ Healthy" if is_healthy else "❌ Unhealthy"
        print(f"   {provider.upper()}: {status}")
    
    # Get provider statistics
    print("\n📊 Provider Statistics...")
    stats = summarizer.get_provider_stats()
    
    for provider_name, provider_stats in stats["providers"].items():
        print(f"   📈 {provider_name.upper()}:")
        print(f"      Enabled: {provider_stats['enabled']}")
        print(f"      Health Score: {provider_stats['health_score']:.2f}")
        print(f"      Requests: {provider_stats['request_count']}")
        print(f"      Success Rate: {provider_stats['success_rate']:.1%}")
        print(f"      Total Cost: ${provider_stats['total_cost']:.4f}")
    
    # Budget information
    budget = stats["budget"]
    print(f"\n💰 Budget Status:")
    print(f"   Daily: ${budget['current_daily']:.2f} / ${budget['daily_limit']:.2f}")
    print(f"   Monthly: ${budget['current_monthly']:.2f} / ${budget['monthly_limit']:.2f}")
    
    # Test summarization with sample text
    sample_text = """
    Breaking News: Tech Giant Announces Revolutionary AI Breakthrough
    
    In a groundbreaking announcement today, a major technology company revealed 
    its latest artificial intelligence system that promises to transform how we 
    interact with computers. The new AI model demonstrates unprecedented capabilities 
    in natural language understanding and generation, potentially revolutionizing 
    industries from healthcare to education.
    
    The company's CEO stated that this represents the most significant advancement 
    in AI technology in the past decade. Early testing shows the system can 
    perform complex reasoning tasks, write code, and even create artistic content 
    with human-like creativity and accuracy.
    
    Industry experts are calling this a watershed moment for artificial intelligence, 
    comparing its potential impact to the introduction of the internet. The technology 
    is expected to be gradually rolled out to consumers over the next year.
    """
    
    if available_providers:
        print(f"\n🧪 Testing Summarization with Available Providers...")
        print(f"📝 Sample Text: {sample_text[:100]}...")
        
        try:
            # Test with automatic provider selection
            print(f"\n🎯 Testing Automatic Provider Selection...")
            response = await summarizer.summarize_text(sample_text)
            
            if response.success:
                print(f"✅ Success!")
                print(f"   Provider: {response.provider}")
                print(f"   Model: {response.model}")
                print(f"   Tokens: {response.tokens_used}")
                print(f"   Cost: ${response.cost:.4f}")
                print(f"   Response Time: {response.response_time:.2f}s")
                print(f"   Summary: {response.content}")
            else:
                print(f"❌ Failed: {response.error_message}")
            
            # Test with specific provider if available
            if len(available_providers) > 1:
                preferred_provider = available_providers[0]
                print(f"\n🎯 Testing with Preferred Provider: {preferred_provider.upper()}...")
                
                response = await summarizer.summarize_text(
                    sample_text, 
                    preferred_provider=preferred_provider
                )
                
                if response.success:
                    print(f"✅ Success with {preferred_provider}!")
                    print(f"   Summary: {response.content}")
                else:
                    print(f"❌ Failed with {preferred_provider}: {response.error_message}")
        
        except Exception as e:
            print(f"❌ Error during testing: {str(e)}")
    
    else:
        print("\n⚠️  No LLM providers are currently available.")
        print("💡 To enable providers, set up API keys:")
        print("   • OpenAI: Set OPENAI_API_KEY environment variable")
        print("   • Anthropic: Set ANTHROPIC_API_KEY environment variable") 
        print("   • Google AI: Set GOOGLE_AI_API_KEY environment variable")
        print("   • Ollama: Ensure Ollama is running locally")
    
    # Configuration tips
    print(f"\n⚙️  Configuration Tips:")
    print(f"   📁 Config file: llm_config.json")
    print(f"   🔑 Environment variables for API keys")
    print(f"   🎛️  Adjust priorities and budgets in config")
    print(f"   🔄 Providers are automatically ordered by priority and health")
    
    # Web interface info
    print(f"\n🌐 Web Interface:")
    print(f"   🚀 Start with: python -m src.web_news_app")
    print(f"   📱 Access at: http://localhost:5000")
    print(f"   🎛️  Manage providers in the sidebar")
    print(f"   📊 View real-time statistics and costs")
    
    # Close connections
    await summarizer.close_all()
    
    print(f"\n🎉 Multi-LLM Demo Complete!")
    print(f"✨ The news feed application now supports multiple LLM providers")
    print(f"🔄 Automatic fallback ensures high reliability")
    print(f"💰 Cost tracking helps manage expenses")
    print(f"📈 Performance monitoring optimizes provider selection")

def setup_demo_environment():
    """Set up demo environment with sample configuration"""
    print("🔧 Setting up demo environment...")
    
    # Check if API keys are available
    api_keys = {
        "OpenAI": os.getenv("OPENAI_API_KEY"),
        "Anthropic": os.getenv("ANTHROPIC_API_KEY"),
        "Google AI": os.getenv("GOOGLE_AI_API_KEY")
    }
    
    print("🔑 API Key Status:")
    for provider, key in api_keys.items():
        status = "✅ Set" if key else "❌ Not Set"
        print(f"   {provider}: {status}")
    
    # Update config to enable providers with API keys
    config_file = "llm_config.json"
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        # Enable providers that have API keys
        if api_keys["OpenAI"]:
            config["openai"]["enabled"] = True
        if api_keys["Anthropic"]:
            config["anthropic"]["enabled"] = True
        if api_keys["Google AI"]:
            config["google"]["enabled"] = True
        
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"📝 Updated {config_file} with available providers")

if __name__ == "__main__":
    print("🚀 Starting Multi-LLM Demo...")
    setup_demo_environment()
    asyncio.run(main())
