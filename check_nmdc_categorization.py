#!/usr/bin/env python3
"""
Check NMDC Categorization
========================

Check why "NMDC slashes iron ore prices" is being categorized as Entertainment.
"""

import json
import sys
from pathlib import Path

# Add src to Python path
src_path = str(Path(__file__).parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

def main():
    try:
        # Load current articles
        with open('data/news_data.json', 'r', encoding='utf-8') as f:
            articles = json.load(f)
        
        print("🔍 Checking NMDC Article Categorization")
        print("=" * 50)
        
        # Find NMDC articles
        nmdc_articles = []
        for article in articles:
            title = article.get('title', '').lower()
            if 'nmdc' in title or 'iron ore' in title:
                nmdc_articles.append(article)
        
        print(f"Found {len(nmdc_articles)} NMDC/iron ore related articles:")
        
        for i, article in enumerate(nmdc_articles, 1):
            title = article.get('title', 'No title')
            category = article.get('category', 'Unknown')
            source = article.get('source', 'Unknown')
            description = article.get('description', 'No description')[:100]
            
            print(f"\n{i}. Title: {title}")
            print(f"   Category: {category}")
            print(f"   Source: {source}")
            print(f"   Description: {description}...")
            
            if category == 'Entertainment':
                print("   ❌ INCORRECTLY CATEGORIZED AS ENTERTAINMENT!")
        
        # Test with current categorizer
        print(f"\n🧪 Testing with Current Categorizer:")
        print("=" * 40)
        
        from core.categorizer import Categorizer
        categorizer = Categorizer()
        
        # Test NMDC article specifically
        test_article = {
            'title': 'NMDC slashes iron ore prices',
            'source': 'The Hindu',
            'description': 'NMDC has reduced iron ore prices across various grades',
            'full_text': 'NMDC slashes iron ore prices. The state-run miner has reduced prices of iron ore across various grades. This move comes amid market conditions and demand patterns.',
            'summary': 'NMDC reduces iron ore prices across various grades due to market conditions'
        }
        
        predicted_category = categorizer.categorize_news(test_article)
        print(f"Test Article: {test_article['title']}")
        print(f"Predicted Category: {predicted_category}")
        
        if predicted_category == 'Entertainment':
            print("❌ CATEGORIZER IS STILL BROKEN!")
            
            # Debug the categorization process
            print(f"\n🔧 Debugging Categorization Process:")
            
            # Check source rules
            source = test_article.get('source', '').lower()
            print(f"Source: '{source}'")
            
            for source_pattern, category in categorizer.source_rules.items():
                if source_pattern in source:
                    print(f"  Source rule match: '{source_pattern}' → {category}")
            
            # Check keyword matching
            text_to_analyze = f"{test_article['title']} {test_article['description']} {test_article['full_text']}"
            print(f"\nText to analyze: {text_to_analyze[:200]}...")
            
            # Check each category
            for category, keywords_dict in categorizer.categories.items():
                if category == "General":
                    continue
                    
                score = 0
                matches = []
                
                for priority in ['high_priority', 'medium_priority', 'low_priority']:
                    for keyword in keywords_dict.get(priority, []):
                        if categorizer._keyword_match(keyword, text_to_analyze):
                            weight = {'high_priority': 10, 'medium_priority': 5, 'low_priority': 2}[priority]
                            score += weight
                            matches.append(f"{keyword} ({priority})")
                
                if matches:
                    print(f"\n{category} (score: {score}):")
                    for match in matches[:3]:  # Show first 3 matches
                        print(f"  - {match}")
        else:
            print(f"✅ Categorizer working correctly: {predicted_category}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
