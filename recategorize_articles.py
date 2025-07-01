#!/usr/bin/env python3
"""
Re-categorize Articles
======================

Re-categorize existing articles with the improved categorizer.
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
        
        print("🏷️ Re-categorizing Articles with Improved Categorizer")
        print("=" * 60)
        
        # Load existing articles
        with open('data/news_data.json', 'r', encoding='utf-8') as f:
            articles = json.load(f)
        
        print(f"📰 Loaded {len(articles)} articles")
        
        # Initialize new categorizer
        categorizer = Categorizer()
        print("✅ Improved categorizer initialized")
        
        # Track changes
        category_changes = {}
        old_categories = {}
        new_categories = {}
        
        # Re-categorize each article
        for i, article in enumerate(articles, 1):
            old_category = article.get('category', 'Unknown')
            new_category = categorizer.categorize_news(article)
            
            # Update the article
            article['category'] = new_category
            
            # Track statistics
            old_categories[old_category] = old_categories.get(old_category, 0) + 1
            new_categories[new_category] = new_categories.get(new_category, 0) + 1
            
            if old_category != new_category:
                change_key = f"{old_category} → {new_category}"
                category_changes[change_key] = category_changes.get(change_key, 0) + 1
                
                # Show some examples
                if len(category_changes) <= 10:  # Show first 10 changes
                    source = article.get('source', 'Unknown')
                    title = article.get('title', 'No title')[:50]
                    print(f"  📝 {source:12} | {old_category:10} → {new_category:10} | {title}...")
        
        # Save updated articles
        with open('data/news_data.json', 'w', encoding='utf-8') as f:
            json.dump(articles, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Re-categorized {len(articles)} articles")
        
        # Show statistics
        print(f"\n📊 Category Changes:")
        if category_changes:
            for change, count in sorted(category_changes.items()):
                print(f"   {change}: {count} articles")
        else:
            print("   No category changes")
        
        print(f"\n📊 Old Category Distribution:")
        for cat, count in sorted(old_categories.items()):
            print(f"   {cat:15}: {count:2d} articles")
        
        print(f"\n📊 New Category Distribution:")
        for cat, count in sorted(new_categories.items()):
            print(f"   {cat:15}: {count:2d} articles")
        
        # Check tech source accuracy
        tech_sources = ['techcrunch', 'hackernews', 'hacker news']
        tech_articles_as_tech = 0
        total_tech_articles = 0
        
        print(f"\n🎯 Technology Source Analysis:")
        for article in articles:
            source = article.get('source', '').lower()
            category = article.get('category', 'Unknown')
            
            if any(tech_source in source for tech_source in tech_sources):
                total_tech_articles += 1
                if category == 'Technology':
                    tech_articles_as_tech += 1
                else:
                    title = article.get('title', 'No title')[:50]
                    print(f"   ⚠️ {source:12} | {category:12} | {title}...")
        
        if total_tech_articles > 0:
            tech_accuracy = (tech_articles_as_tech / total_tech_articles) * 100
            print(f"\n📈 Tech Source Accuracy: {tech_articles_as_tech}/{total_tech_articles} ({tech_accuracy:.1f}%)")
            
            if tech_accuracy >= 70:
                print("✅ Good tech categorization!")
            else:
                print("⚠️ Tech categorization still needs improvement")
        
        print(f"\n🎉 Re-categorization complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
