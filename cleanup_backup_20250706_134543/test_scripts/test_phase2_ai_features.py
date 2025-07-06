#!/usr/bin/env python3
"""
Phase 2 AI Features Test Script
==============================

Comprehensive test script for Phase 2 AI features:
1. Content Relationship Mapping
2. Trend Analysis & Prediction
3. AI News Assistant
4. Smart Briefing Generation
"""

import sys
import os
import json
import requests
from pathlib import Path

# Add src to Python path
src_path = str(Path(__file__).parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

def test_ai_features_status():
    """Test AI features status endpoint including Phase 2."""
    print("🧪 Testing AI Features Status (Phase 1 & 2)...")
    try:
        response = requests.get('http://127.0.0.1:5000/api/ai-features/status')
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                print("✅ AI Features Status:")
                
                # Phase 1 features
                phase1_features = data.get('phase1_features', [])
                print(f"   Phase 1 Features ({len(phase1_features)}):")
                for feature in phase1_features:
                    print(f"     ✅ {feature}")
                
                # Phase 2 features
                phase2_features = data.get('phase2_features', [])
                print(f"   Phase 2 Features ({len(phase2_features)}):")
                for feature in phase2_features:
                    print(f"     ✅ {feature}")
                
                total_features = len(phase1_features) + len(phase2_features)
                print(f"   Total Available Features: {total_features}")
                return True
            else:
                print(f"❌ Status check failed: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Connection error: {e}")
    return False

def test_content_relationship_analysis():
    """Test content relationship mapping feature."""
    print("\n🧪 Testing Content Relationship Analysis...")
    
    try:
        response = requests.post('http://127.0.0.1:5000/api/ai-features/relationship-analysis')
        
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                relationships = data['relationships']
                print("✅ Content Relationship Analysis Results:")
                print(f"   Articles Analyzed: {data.get('articles_analyzed', 0)}")
                
                # Story clusters
                clusters = relationships.get('story_clusters', [])
                print(f"   Story Clusters: {len(clusters)}")
                for i, cluster in enumerate(clusters[:2]):  # Show first 2 clusters
                    print(f"     Cluster {i+1}: {len(cluster['articles'])} articles")
                    print(f"       Score: {cluster['cluster_score']:.2f}")
                
                # Follow-ups
                follow_ups = relationships.get('follow_ups', [])
                print(f"   Follow-up Articles: {len(follow_ups)}")
                
                # Contradictions
                contradictions = relationships.get('contradictions', [])
                print(f"   Contradictory Articles: {len(contradictions)}")
                
                # Timelines
                timelines = relationships.get('timelines', [])
                print(f"   Story Timelines: {len(timelines)}")
                
                return True
            else:
                print(f"❌ Relationship analysis failed: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Test error: {e}")
    return False

def test_trend_analysis():
    """Test trend analysis feature."""
    print("\n🧪 Testing Trend Analysis...")
    
    try:
        response = requests.post(
            'http://127.0.0.1:5000/api/ai-features/trend-analysis',
            json={'include_historical': False}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                trends = data['trends']
                print("✅ Trend Analysis Results:")
                print(f"   Articles Analyzed: {data.get('articles_analyzed', 0)}")
                
                # Emerging topics
                emerging_topics = trends.get('emerging_topics', [])
                print(f"   Emerging Topics: {len(emerging_topics)}")
                for topic in emerging_topics[:3]:  # Show top 3
                    print(f"     • {topic['topic']}: {topic['emergence_score']:.2f}")
                
                # Sentiment trends
                sentiment_trends = trends.get('sentiment_trends', {})
                overall_trend = sentiment_trends.get('overall_trend', 'unknown')
                print(f"   Overall Sentiment Trend: {overall_trend}")
                
                # Market impact predictions
                market_impact = trends.get('market_impact_predictions', [])
                print(f"   Market Impact Predictions: {len(market_impact)}")
                for prediction in market_impact[:2]:  # Show top 2
                    article = prediction['article']
                    print(f"     • {article['title'][:50]}...")
                    print(f"       Impact Level: {prediction['impact_level']}")
                
                # Trending keywords
                trending_keywords = trends.get('trending_keywords', [])
                print(f"   Trending Keywords: {len(trending_keywords)}")
                for keyword in trending_keywords[:3]:  # Show top 3
                    print(f"     • {keyword['keyword']}: {keyword['frequency']} mentions")
                
                return True
            else:
                print(f"❌ Trend analysis failed: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Test error: {e}")
    return False

def test_ai_chat():
    """Test AI assistant chat feature."""
    print("\n🧪 Testing AI News Assistant Chat...")
    
    test_messages = [
        "What's happening with artificial intelligence today?",
        "Explain the latest market trends",
        "What are the key technology developments?"
    ]
    
    for message in test_messages:
        print(f"\n   Testing message: '{message}'")
        try:
            response = requests.post(
                'http://127.0.0.1:5000/api/ai-features/ai-chat',
                json={'message': message, 'context': {}}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data['success']:
                    ai_response = data['response']
                    print(f"   ✅ AI Response: {ai_response['message'][:100]}...")
                    print(f"   Response Type: {ai_response.get('response_type', 'unknown')}")
                    print(f"   Confidence: {ai_response.get('confidence', 0):.2f}")
                    
                    # Follow-up suggestions
                    follow_ups = ai_response.get('follow_up_suggestions', [])
                    if follow_ups:
                        print(f"   Follow-up Suggestions: {len(follow_ups)}")
                else:
                    print(f"   ❌ Chat failed: {data.get('error', 'Unknown error')}")
                    return False
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ Test error: {e}")
            return False
    
    return True

def test_article_explanation():
    """Test article explanation feature."""
    print("\n🧪 Testing Article Explanation...")
    
    test_article = {
        "title": "Revolutionary AI Breakthrough Transforms Healthcare Industry",
        "description": "Scientists have developed an advanced AI system that can diagnose diseases with unprecedented accuracy, potentially revolutionizing medical care worldwide.",
        "content": "The new artificial intelligence system, developed by researchers at leading universities, uses deep learning algorithms to analyze medical images and patient data. Early trials show 95% accuracy in disease detection.",
        "source": "TechHealth News",
        "category": "Healthcare"
    }
    
    try:
        response = requests.post(
            'http://127.0.0.1:5000/api/ai-features/explain-article',
            json={'article': test_article, 'detail_level': 'medium'}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                explanation = data['explanation']
                print("✅ Article Explanation Results:")
                print(f"   Article Category: {explanation.get('article_category', 'unknown')}")
                print(f"   Detail Level: {explanation.get('detail_level', 'unknown')}")
                
                key_info = explanation.get('key_information', {})
                print(f"   Main Topics: {key_info.get('main_topics', [])}")
                print(f"   Sentiment: {key_info.get('sentiment', 'unknown')}")
                
                follow_ups = explanation.get('follow_up_questions', [])
                print(f"   Follow-up Questions: {len(follow_ups)}")
                for question in follow_ups[:3]:  # Show first 3
                    print(f"     • {question}")
                
                return True
            else:
                print(f"❌ Article explanation failed: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Test error: {e}")
    return False

def test_daily_briefing():
    """Test daily briefing generation."""
    print("\n🧪 Testing Daily Briefing Generation...")
    
    try:
        response = requests.get('http://127.0.0.1:5000/api/ai-features/daily-briefing')
        
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                briefing = data['briefing']
                print("✅ Daily Briefing Results:")
                print(f"   Briefing Type: {briefing.get('briefing_type', 'unknown')}")
                print(f"   Date: {briefing.get('date', 'unknown')}")
                
                metadata = briefing.get('metadata', {})
                print(f"   Articles Analyzed: {metadata.get('articles_analyzed', 0)}")
                print(f"   Topics Covered: {metadata.get('topics_covered', 0)}")
                
                content = briefing.get('content', '')
                print(f"   Content Length: {len(content)} characters")
                print(f"   Content Preview: {content[:200]}...")
                
                return True
            else:
                print(f"❌ Daily briefing failed: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Test error: {e}")
    return False

def test_topic_deep_dive():
    """Test topic deep dive analysis."""
    print("\n🧪 Testing Topic Deep Dive...")
    
    test_topics = ["artificial_intelligence", "technology", "finance"]
    
    for topic in test_topics:
        print(f"\n   Testing topic: '{topic}'")
        try:
            response = requests.get(
                f'http://127.0.0.1:5000/api/ai-features/topic-deep-dive?topic={topic}'
            )
            
            if response.status_code == 200:
                data = response.json()
                if data['success']:
                    deep_dive = data['deep_dive']
                    print(f"   ✅ Deep Dive for {topic}:")
                    print(f"   Analysis Type: {deep_dive.get('analysis_type', 'unknown')}")
                    
                    metadata = deep_dive.get('metadata', {})
                    articles_analyzed = metadata.get('articles_analyzed', 0)
                    print(f"   Articles Analyzed: {articles_analyzed}")
                    
                    if articles_analyzed > 0:
                        content = deep_dive.get('content', '')
                        print(f"   Content Length: {len(content)} characters")
                    else:
                        print(f"   No articles found for topic: {topic}")
                else:
                    print(f"   ❌ Deep dive failed: {data.get('error', 'Unknown error')}")
                    return False
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ Test error: {e}")
            return False
    
    return True

def main():
    """Run all Phase 2 AI features tests."""
    print("🚀 Phase 2 AI Features Test Suite")
    print("=" * 50)
    
    # Check if server is running
    try:
        response = requests.get('http://127.0.0.1:5000/api/health')
        if response.status_code != 200:
            print("❌ Server not running. Please start the server first:")
            print("   conda activate newsfeeds && python full_server.py")
            return
    except:
        print("❌ Cannot connect to server. Please start the server first:")
        print("   conda activate newsfeeds && python full_server.py")
        return
    
    # Run tests
    tests = [
        ("AI Features Status", test_ai_features_status),
        ("Content Relationship Analysis", test_content_relationship_analysis),
        ("Trend Analysis", test_trend_analysis),
        ("AI Chat", test_ai_chat),
        ("Article Explanation", test_article_explanation),
        ("Daily Briefing", test_daily_briefing),
        ("Topic Deep Dive", test_topic_deep_dive)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"🎯 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All Phase 2 AI features are working correctly!")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()
