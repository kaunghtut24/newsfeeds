#!/usr/bin/env python3
"""
Phase 1 AI Features Test Script
==============================

Test script for the newly implemented Phase 1 AI features:
1. Smart Content Categorization
2. Advanced Sentiment Analysis
3. Content Recommendation System
4. Semantic Search Engine
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
    """Test AI features status endpoint."""
    print("🧪 Testing AI Features Status...")
    try:
        response = requests.get('http://127.0.0.1:5000/api/ai-features/status')
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                print("✅ AI Features Status:")
                for feature, status in data['ai_features_status'].items():
                    if feature != 'timestamp':
                        status_icon = "✅" if status else "❌"
                        print(f"   {status_icon} {feature}: {status}")
                print(f"   Available features: {data['available_features']}")
                return True
            else:
                print(f"❌ Status check failed: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Connection error: {e}")
    return False

def test_smart_categorization():
    """Test smart categorization feature."""
    print("\n🧪 Testing Smart Categorization...")
    
    test_article = {
        "title": "Tesla Announces Revolutionary AI-Powered Autonomous Vehicle Technology",
        "description": "Tesla has unveiled groundbreaking artificial intelligence technology for self-driving cars, promising to revolutionize the automotive industry with advanced machine learning algorithms.",
        "content": "The electric vehicle manufacturer Tesla has announced a major breakthrough in autonomous vehicle technology, leveraging cutting-edge artificial intelligence and deep learning algorithms. The new system promises enhanced safety and efficiency for self-driving cars.",
        "source": "TechNews"
    }
    
    try:
        response = requests.post(
            'http://127.0.0.1:5000/api/ai-features/smart-categorization',
            json={'article': test_article}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                categorization = data['categorization']
                print("✅ Smart Categorization Results:")
                print(f"   Primary Category: {categorization.get('primary_category', 'N/A')}")
                
                topics = categorization.get('topics', [])
                if topics:
                    print("   Detected Topics:")
                    for topic in topics[:3]:  # Show top 3
                        print(f"     • {topic['topic']}: {topic['confidence']:.2f}")
                
                industries = categorization.get('industries', [])
                if industries:
                    print("   Industry Classification:")
                    for industry in industries:
                        print(f"     • {industry['industry']}: {industry['confidence']:.2f}")
                
                events = categorization.get('events', [])
                if events:
                    print("   Event Detection:")
                    for event in events:
                        print(f"     • {event['event_type']}: {event['confidence']:.2f}")
                
                return True
            else:
                print(f"❌ Categorization failed: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Test error: {e}")
    return False

def test_sentiment_analysis():
    """Test sentiment analysis feature."""
    print("\n🧪 Testing Advanced Sentiment Analysis...")
    
    test_article = {
        "title": "Market Crashes as Investors Panic Over Economic Uncertainty",
        "description": "Stock markets plunged dramatically today as worried investors fled to safety amid growing concerns about economic instability and rising inflation fears.",
        "content": "The financial markets experienced a terrible day as panic selling gripped investors. The dramatic decline reflects deep concerns about the economic outlook and uncertainty about future monetary policy.",
        "source": "FinanceNews"
    }
    
    try:
        response = requests.post(
            'http://127.0.0.1:5000/api/ai-features/sentiment-analysis',
            json={'article': test_article}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                sentiment = data['sentiment']
                print("✅ Sentiment Analysis Results:")
                print(f"   Overall Sentiment: {sentiment.get('overall_sentiment', 'N/A')}")
                
                scores = sentiment.get('sentiment_scores', {})
                print(f"   Sentiment Scores:")
                print(f"     • Positive: {scores.get('positive', 0):.3f}")
                print(f"     • Negative: {scores.get('negative', 0):.3f}")
                print(f"     • Neutral: {scores.get('neutral', 0):.3f}")
                print(f"     • Compound: {scores.get('compound', 0):.3f}")
                
                emotions = sentiment.get('emotions', {})
                if emotions:
                    print("   Detected Emotions:")
                    for emotion, data in emotions.items():
                        print(f"     • {emotion}: {data['intensity']:.3f}")
                
                market_sentiment = sentiment.get('market_sentiment', {})
                if market_sentiment:
                    print("   Market Sentiment:")
                    for sentiment_type, data in market_sentiment.items():
                        print(f"     • {sentiment_type}: {data.get('intensity', 0):.3f}")
                
                return True
            else:
                print(f"❌ Sentiment analysis failed: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Test error: {e}")
    return False

def test_semantic_search():
    """Test semantic search feature."""
    print("\n🧪 Testing Semantic Search...")
    
    test_queries = [
        "artificial intelligence technology",
        "market crash financial crisis",
        "electric vehicle innovation"
    ]
    
    for query in test_queries:
        print(f"\n   Testing query: '{query}'")
        try:
            response = requests.post(
                'http://127.0.0.1:5000/api/ai-features/semantic-search',
                json={'query': query}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data['success']:
                    results = data['results']
                    print(f"   ✅ Found {len(results)} results")
                    
                    # Show top 2 results
                    for i, result in enumerate(results[:2]):
                        article = result['article']
                        score = result['relevance_score']
                        print(f"     {i+1}. {article.get('title', 'No title')[:50]}...")
                        print(f"        Relevance: {score:.3f}")
                        
                        highlights = result.get('highlights', {})
                        if highlights:
                            print(f"        Highlights: {list(highlights.keys())}")
                else:
                    print(f"   ❌ Search failed: {data.get('error', 'Unknown error')}")
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Test error: {e}")
            return False
    
    return True

def test_search_suggestions():
    """Test search suggestions feature."""
    print("\n🧪 Testing Search Suggestions...")
    
    test_queries = ["ai", "market", "tech"]
    
    for query in test_queries:
        try:
            response = requests.get(
                f'http://127.0.0.1:5000/api/ai-features/search-suggestions?q={query}&limit=3'
            )
            
            if response.status_code == 200:
                data = response.json()
                if data['success']:
                    suggestions = data['suggestions']
                    print(f"   Query '{query}' → Suggestions: {suggestions}")
                else:
                    print(f"   ❌ Suggestions failed: {data.get('error', 'Unknown error')}")
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Test error: {e}")
            return False
    
    return True

def test_content_recommendations():
    """Test content recommendations feature."""
    print("\n🧪 Testing Content Recommendations...")
    
    try:
        response = requests.get(
            'http://127.0.0.1:5000/api/ai-features/recommendations?user_id=test_user&limit=5'
        )
        
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                recommendations = data['recommendations']
                print(f"✅ Generated {len(recommendations)} recommendations")
                
                for i, rec in enumerate(recommendations[:3]):
                    article = rec['article']
                    score = rec['score']
                    print(f"   {i+1}. {article.get('title', 'No title')[:50]}...")
                    print(f"      Score: {score:.3f}")
                    
                    reasons = rec.get('reasons', [])
                    if reasons:
                        print(f"      Reasons: {reasons[:2]}")
                
                return True
            else:
                print(f"❌ Recommendations failed: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Test error: {e}")
    return False

def main():
    """Run all Phase 1 AI features tests."""
    print("🚀 Phase 1 AI Features Test Suite")
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
        ("Smart Categorization", test_smart_categorization),
        ("Sentiment Analysis", test_sentiment_analysis),
        ("Semantic Search", test_semantic_search),
        ("Search Suggestions", test_search_suggestions),
        ("Content Recommendations", test_content_recommendations)
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
        print("🎉 All Phase 1 AI features are working correctly!")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()
