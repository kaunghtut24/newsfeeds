#!/usr/bin/env python3
"""
Test script to demonstrate the performance optimization system
"""

import json
import time
from src.core.performance_optimizer import performance_optimizer

def test_performance_profiles():
    """Test different performance profiles"""
    print("🚀 Testing Performance Optimization System")
    print("=" * 60)
    
    # Test scenarios
    scenarios = [
        {"name": "Light Load", "sources": 2, "articles": 6},
        {"name": "Medium Load", "sources": 5, "articles": 25},
        {"name": "Heavy Load", "sources": 10, "articles": 50},
        {"name": "Very Heavy Load", "sources": 15, "articles": 100},
    ]
    
    for scenario in scenarios:
        print(f"\n📊 Scenario: {scenario['name']}")
        print(f"   Sources: {scenario['sources']}, Estimated Articles: {scenario['articles']}")
        
        # Get optimal parameters
        params = performance_optimizer.get_processing_parameters(
            num_sources=scenario['sources'],
            estimated_articles=scenario['articles']
        )
        
        print(f"   🎯 Selected Profile: {params['profile_name']}")
        print(f"   ⚙️  Articles per source: {params['max_articles_per_source']}")
        print(f"   📦 Batch size: {params['batch_size']}")
        print(f"   ⏱️  Batch delay: {params['batch_delay']}s")
        print(f"   📝 Max text length: {params['max_text_length']}")
        print(f"   🔄 Max retries: {params['max_retries']}")
        print(f"   ⏰ Estimated time: {params['estimated_processing_time']:.1f}s")

def test_user_preferences():
    """Test user preference overrides"""
    print(f"\n🎛️  Testing User Preference Overrides")
    print("-" * 40)
    
    preferences = ["minimal", "fast", "balanced", "comprehensive"]
    
    for pref in preferences:
        params = performance_optimizer.get_processing_parameters(
            num_sources=5,
            estimated_articles=25,
            user_preference=pref
        )
        
        print(f"   {pref.capitalize():12}: {params['batch_size']} batch, {params['batch_delay']}s delay, {params['max_articles_per_source']} articles/source")

def simulate_processing():
    """Simulate processing with performance tracking"""
    print(f"\n🧪 Simulating Processing with Performance Tracking")
    print("-" * 50)
    
    # Simulate different processing times
    simulations = [
        {"articles": 5, "time": 8.5},
        {"articles": 15, "time": 22.3},
        {"articles": 30, "time": 45.7},
        {"articles": 10, "time": 12.1},
    ]
    
    for sim in simulations:
        performance_optimizer.update_performance_stats(sim["time"], sim["articles"])
        print(f"   Processed {sim['articles']} articles in {sim['time']}s")
    
    # Get performance report
    report = performance_optimizer.get_performance_report()
    print(f"\n📈 Performance Report:")
    print(f"   Current Profile: {report['current_profile']}")
    print(f"   Total Requests: {report['performance_stats']['total_requests']}")
    print(f"   Avg Processing Time: {report['performance_stats']['avg_processing_time']:.1f}s")
    
    if report['recommendations']:
        print(f"   💡 Recommendations:")
        for rec in report['recommendations']:
            print(f"      • {rec}")

def test_admin_settings_integration():
    """Test integration with admin settings"""
    print(f"\n⚙️  Testing Admin Settings Integration")
    print("-" * 40)
    
    try:
        # Load current admin settings
        with open('data/admin_settings.json', 'r') as f:
            admin_settings = json.load(f)
        
        current_limit = admin_settings.get('user_limits', {}).get('max_articles_per_source', 5)
        print(f"   Current admin limit: {current_limit} articles per source")
        
        # Show how this affects performance profiles
        for profile_name in ["fast", "balanced", "comprehensive"]:
            params = performance_optimizer.get_processing_parameters(
                num_sources=3,
                estimated_articles=15,
                user_preference=profile_name
            )
            
            effective_limit = min(current_limit, params['max_articles_per_source'])
            print(f"   {profile_name.capitalize():12}: {params['max_articles_per_source']} → {effective_limit} (admin limited)")
            
    except FileNotFoundError:
        print("   ⚠️  Admin settings file not found")

def main():
    """Main test function"""
    test_performance_profiles()
    test_user_preferences()
    simulate_processing()
    test_admin_settings_integration()
    
    print(f"\n✅ Performance Optimization System Test Complete!")
    print(f"💡 The system dynamically adjusts batch sizes, delays, and limits based on:")
    print(f"   • Number of sources being processed")
    print(f"   • Total estimated articles")
    print(f"   • User preferences (if specified)")
    print(f"   • Admin-configured limits")
    print(f"   • Historical performance data")

if __name__ == "__main__":
    main()
