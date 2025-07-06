#!/usr/bin/env python3
"""
Debug NMDC Categorization
=========================

Deep debug why NMDC article is being categorized as Entertainment.
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
        from core.categorizer import Categorizer
        
        print("🔍 Deep Debug: NMDC Categorization")
        print("=" * 50)
        
        # Load the actual NMDC article from the data
        with open('data/news_data.json', 'r', encoding='utf-8') as f:
            articles = json.load(f)
        
        nmdc_article = None
        for article in articles:
            if 'nmdc' in article.get('title', '').lower():
                nmdc_article = article
                break
        
        if not nmdc_article:
            print("❌ NMDC article not found!")
            return
        
        print("📰 NMDC Article Details:")
        print(f"   Title: {nmdc_article.get('title', 'No title')}")
        print(f"   Source: {nmdc_article.get('source', 'Unknown')}")
        print(f"   Description: {nmdc_article.get('description', 'No description')}")
        print(f"   Summary: {nmdc_article.get('summary', 'No summary')[:100]}...")
        print(f"   Current Category: {nmdc_article.get('category', 'Unknown')}")
        
        # Initialize categorizer and debug
        categorizer = Categorizer()
        
        print(f"\n🔧 Debugging Categorization Process:")
        print("=" * 40)
        
        # Check source-based rules first
        source = nmdc_article.get('source', '').lower()
        print(f"1. Source Check: '{source}'")
        
        source_match = False
        for source_pattern, category in categorizer.source_rules.items():
            if source_pattern in source:
                print(f"   ✅ Source rule match: '{source_pattern}' → {category}")
                source_match = True
                break
        
        if not source_match:
            print(f"   ❌ No source rule matches")
        
        # Prepare text for analysis
        title = nmdc_article.get('title', '').lower()
        content = nmdc_article.get('full_text', '').lower()
        summary = nmdc_article.get('summary', '').lower()
        description = nmdc_article.get('description', '').lower()
        
        # Combine all text with title having higher weight
        text_to_categorize = f"{title} {title} {summary} {content} {description}"
        
        print(f"\n2. Text Analysis:")
        print(f"   Title: '{title}'")
        print(f"   Description: '{description}'")
        print(f"   Summary: '{summary[:100]}...'")
        print(f"   Combined text length: {len(text_to_categorize)} characters")
        
        # Score each category
        print(f"\n3. Category Scoring:")
        category_scores = {}
        
        for category, keywords_dict in categorizer.categories.items():
            if category == "General":
                continue
                
            score = 0
            matches = []
            
            # High priority keywords (weight: 10)
            for keyword in keywords_dict.get("high_priority", []):
                if categorizer._keyword_match(keyword, text_to_categorize):
                    score += 10
                    matches.append(f"{keyword} (high:10)")
            
            # Medium priority keywords (weight: 5)
            for keyword in keywords_dict.get("medium_priority", []):
                if categorizer._keyword_match(keyword, text_to_categorize):
                    score += 5
                    matches.append(f"{keyword} (med:5)")
            
            # Low priority keywords (weight: 2)
            for keyword in keywords_dict.get("low_priority", []):
                if categorizer._keyword_match(keyword, text_to_categorize):
                    score += 2
                    matches.append(f"{keyword} (low:2)")
            
            # Bonus for title matches (additional weight)
            for keyword in keywords_dict.get("high_priority", []) + keywords_dict.get("medium_priority", []):
                if categorizer._keyword_match(keyword, title):
                    score += 5
                    matches.append(f"{keyword} (title:+5)")
            
            category_scores[category] = score
            
            if score > 0:
                print(f"   {category}: {score} points")
                for match in matches[:3]:  # Show first 3 matches
                    print(f"      - {match}")
        
        # Find the category with the highest score
        if category_scores:
            best_category = max(category_scores, key=category_scores.get)
            best_score = category_scores[best_category]
            
            print(f"\n4. Final Decision:")
            print(f"   Highest scoring category: {best_category} ({best_score} points)")
            
            if best_score > 0:
                print(f"   ✅ Predicted category: {best_category}")
            else:
                print(f"   ✅ Predicted category: General (no matches)")
        
        # Test the actual categorize_news method
        actual_result = categorizer.categorize_news(nmdc_article)
        print(f"\n5. Actual categorize_news() result: {actual_result}")
        
        # If it's still Entertainment, let's check Entertainment keywords
        if actual_result == 'Entertainment':
            print(f"\n❌ PROBLEM: Still categorized as Entertainment!")
            print(f"🔍 Checking Entertainment keyword matches:")
            
            entertainment_keywords = categorizer.categories.get('Entertainment', {})
            for priority in ['high_priority', 'medium_priority', 'low_priority']:
                keywords = entertainment_keywords.get(priority, [])
                print(f"   {priority}: {len(keywords)} keywords")
                
                for keyword in keywords:
                    if categorizer._keyword_match(keyword, text_to_categorize):
                        print(f"      ✅ MATCH: '{keyword}'")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
