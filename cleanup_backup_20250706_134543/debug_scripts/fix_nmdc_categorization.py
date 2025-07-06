#!/usr/bin/env python3
"""
Fix NMDC Categorization
=======================

Fix the incorrect categorization of NMDC article from Entertainment to Business.
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
        
        print("🔧 Fixing NMDC Article Categorization")
        print("=" * 50)
        
        # Load current articles
        with open('data/news_data.json', 'r', encoding='utf-8') as f:
            articles = json.load(f)
        
        print(f"📰 Loaded {len(articles)} articles")
        
        # Initialize categorizer
        categorizer = Categorizer()
        
        # Find and fix NMDC articles
        fixed_count = 0
        
        for article in articles:
            title = article.get('title', '').lower()
            current_category = article.get('category', 'Unknown')
            
            # Check for NMDC or iron ore related articles that are miscategorized
            if ('nmdc' in title or 'iron ore' in title) and current_category == 'Entertainment':
                # Re-categorize
                new_category = categorizer.categorize_news(article)
                
                print(f"\n📝 Fixing article:")
                print(f"   Title: {article.get('title', 'No title')}")
                print(f"   Old Category: {current_category}")
                print(f"   New Category: {new_category}")
                
                # Update the category
                article['category'] = new_category
                fixed_count += 1
        
        if fixed_count > 0:
            # Save the updated articles
            with open('data/news_data.json', 'w', encoding='utf-8') as f:
                json.dump(articles, f, indent=2, ensure_ascii=False)
            
            print(f"\n✅ Fixed {fixed_count} article(s)")
            print("💾 Updated articles saved to news_data.json")
            
            # Verify the fix
            print(f"\n🔍 Verification:")
            for article in articles:
                title = article.get('title', '').lower()
                if 'nmdc' in title or 'iron ore' in title:
                    category = article.get('category', 'Unknown')
                    print(f"   {article.get('title', 'No title')}: {category}")
        else:
            print("\n✅ No NMDC articles found with incorrect categorization")
        
        # Check for any other Entertainment miscategorizations
        print(f"\n🔍 Checking for other potential Entertainment miscategorizations:")
        entertainment_articles = [a for a in articles if a.get('category') == 'Entertainment']
        
        if entertainment_articles:
            print(f"Found {len(entertainment_articles)} Entertainment articles:")
            for article in entertainment_articles:
                title = article.get('title', 'No title')
                source = article.get('source', 'Unknown')
                
                # Check if this looks like it should be business/market
                title_lower = title.lower()
                business_keywords = ['price', 'market', 'company', 'business', 'revenue', 'profit', 'stock', 'shares', 'investment', 'economy', 'financial']
                
                if any(keyword in title_lower for keyword in business_keywords):
                    print(f"   ⚠️ Potentially miscategorized: {title} ({source})")
                    
                    # Re-categorize this one too
                    new_category = categorizer.categorize_news(article)
                    if new_category != 'Entertainment':
                        print(f"      Should be: {new_category}")
                        article['category'] = new_category
                        fixed_count += 1
                else:
                    print(f"   ✅ Correctly categorized: {title[:50]}...")
        
        if fixed_count > 0:
            # Save again if we made additional fixes
            with open('data/news_data.json', 'w', encoding='utf-8') as f:
                json.dump(articles, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Final save: Fixed {fixed_count} total articles")
        
        print(f"\n🎉 NMDC categorization fix complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
