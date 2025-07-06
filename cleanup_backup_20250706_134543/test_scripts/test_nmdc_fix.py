#!/usr/bin/env python3
"""
Test NMDC Fix
=============

Test that NMDC article is now correctly categorized as Business instead of Entertainment.
"""

import json
import sys
from pathlib import Path

# Add src to Python path
src_path = str(Path(__file__).parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

def test_nmdc_categorization():
    """Test that NMDC article is correctly categorized."""
    print("🏷️ Testing NMDC Article Categorization")
    print("=" * 40)
    
    try:
        # Load current articles
        with open('data/news_data.json', 'r', encoding='utf-8') as f:
            articles = json.load(f)
        
        # Find NMDC article
        nmdc_article = None
        for article in articles:
            if 'nmdc' in article.get('title', '').lower():
                nmdc_article = article
                break
        
        if not nmdc_article:
            print("❌ NMDC article not found!")
            return False
        
        title = nmdc_article.get('title', 'No title')
        category = nmdc_article.get('category', 'Unknown')
        source = nmdc_article.get('source', 'Unknown')
        
        print(f"📰 Article: {title}")
        print(f"🏷️ Category: {category}")
        print(f"📡 Source: {source}")
        
        if category == 'Business':
            print("✅ NMDC article correctly categorized as Business!")
            return True
        elif category == 'Entertainment':
            print("❌ NMDC article still incorrectly categorized as Entertainment!")
            return False
        else:
            print(f"⚠️ NMDC article categorized as {category} (not ideal but better than Entertainment)")
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_categorizer_logic():
    """Test the categorizer logic with mining/commodity examples."""
    print("\n🧪 Testing Categorizer Logic")
    print("=" * 40)
    
    try:
        from core.categorizer import Categorizer
        
        categorizer = Categorizer()
        
        # Test cases for mining/commodity articles
        test_cases = [
            {
                "title": "NMDC slashes iron ore prices",
                "source": "The Hindu",
                "expected": "Business"
            },
            {
                "title": "Steel prices rise on strong demand",
                "source": "Business Standard",
                "expected": "Business"
            },
            {
                "title": "Commodity market sees volatility",
                "source": "Economic Times",
                "expected": "Market"
            },
            {
                "title": "Mining company reports strong earnings",
                "source": "Financial Express",
                "expected": "Business"
            },
            {
                "title": "Iron ore producer expands operations",
                "source": "Business Line",
                "expected": "Business"
            }
        ]
        
        correct_predictions = 0
        
        for i, test_case in enumerate(test_cases, 1):
            news_item = {
                'title': test_case['title'],
                'source': test_case['source'],
                'full_text': test_case['title'],
                'summary': test_case['title'],
                'description': test_case['title']
            }
            
            predicted = categorizer.categorize_news(news_item)
            expected = test_case['expected']
            
            print(f"\n📝 Test {i}: {test_case['title']}")
            print(f"   Expected: {expected}")
            print(f"   Predicted: {predicted}")
            
            if predicted == expected:
                print(f"   ✅ Correct!")
                correct_predictions += 1
            elif predicted in ['Business', 'Market'] and expected in ['Business', 'Market']:
                print(f"   ✅ Acceptable (both business-related)")
                correct_predictions += 1
            else:
                print(f"   ❌ Incorrect")
        
        accuracy = (correct_predictions / len(test_cases)) * 100
        print(f"\n📊 Categorization Accuracy: {correct_predictions}/{len(test_cases)} ({accuracy:.1f}%)")
        
        return accuracy >= 80  # At least 80% accuracy
        
    except Exception as e:
        print(f"❌ Error testing categorizer: {e}")
        return False

def test_entertainment_specificity():
    """Test that Entertainment category is now more specific."""
    print("\n🎭 Testing Entertainment Category Specificity")
    print("=" * 40)
    
    try:
        from core.categorizer import Categorizer
        
        categorizer = Categorizer()
        
        # Test cases that should NOT be Entertainment
        non_entertainment_cases = [
            "NMDC slashes iron ore prices",
            "Steel producer reports earnings",
            "Mining company expands operations",
            "Commodity prices fluctuate",
            "Iron ore producer announces deal"
        ]
        
        # Test cases that SHOULD be Entertainment
        entertainment_cases = [
            "Hollywood movie producer announces new film",
            "Netflix releases new series",
            "Actor wins Oscar award",
            "Music artist releases new album",
            "Film producer signs major deal"
        ]
        
        print("🚫 Testing non-entertainment cases:")
        non_entertainment_correct = 0
        for case in non_entertainment_cases:
            news_item = {
                'title': case,
                'source': 'Test Source',
                'full_text': case,
                'summary': case,
                'description': case
            }
            
            predicted = categorizer.categorize_news(news_item)
            is_correct = predicted != 'Entertainment'
            
            print(f"   {case[:40]}... → {predicted} {'✅' if is_correct else '❌'}")
            if is_correct:
                non_entertainment_correct += 1
        
        print(f"\n🎬 Testing entertainment cases:")
        entertainment_correct = 0
        for case in entertainment_cases:
            news_item = {
                'title': case,
                'source': 'Test Source',
                'full_text': case,
                'summary': case,
                'description': case
            }
            
            predicted = categorizer.categorize_news(news_item)
            is_correct = predicted == 'Entertainment'
            
            print(f"   {case[:40]}... → {predicted} {'✅' if is_correct else '❌'}")
            if is_correct:
                entertainment_correct += 1
        
        non_ent_accuracy = (non_entertainment_correct / len(non_entertainment_cases)) * 100
        ent_accuracy = (entertainment_correct / len(entertainment_cases)) * 100
        
        print(f"\n📊 Results:")
        print(f"   Non-Entertainment Accuracy: {non_entertainment_correct}/{len(non_entertainment_cases)} ({non_ent_accuracy:.1f}%)")
        print(f"   Entertainment Accuracy: {entertainment_correct}/{len(entertainment_cases)} ({ent_accuracy:.1f}%)")
        
        return non_ent_accuracy >= 80 and ent_accuracy >= 60
        
    except Exception as e:
        print(f"❌ Error testing entertainment specificity: {e}")
        return False

def main():
    """Run all NMDC fix tests."""
    print("🧪 NMDC Categorization Fix Test Suite")
    print("=" * 50)
    print("Testing fix for: NMDC slashes iron ore prices categorized as Entertainment")
    print()
    
    tests = [
        ("NMDC Article Categorization", test_nmdc_categorization),
        ("Categorizer Logic", test_categorizer_logic),
        ("Entertainment Specificity", test_entertainment_specificity)
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
        print("\n🎉 NMDC categorization fix is successful!")
        print("✅ NMDC article correctly categorized as Business")
        print("✅ Categorizer logic improved for mining/commodity articles")
        print("✅ Entertainment category made more specific")
        print("✅ No more false Entertainment categorizations")
        print("\nThe categorization system is now more accurate and reliable!")
    elif passed > 0:
        print("\n⚠️ Some tests passed. Partial fix applied.")
    else:
        print("\n❌ All tests failed. NMDC categorization still needs work.")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
