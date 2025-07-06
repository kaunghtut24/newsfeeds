#!/usr/bin/env python3
"""
Check Categories
===============

Check the current categorization of news articles.
"""

import json

def main():
    try:
        with open('data/news_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"Total articles: {len(data)}")
        
        # Check tech sources
        tech_sources = []
        for article in data:
            source = article.get('source', '').lower()
            if 'techcrunch' in source or 'hackernews' in source or 'hacker news' in source:
                tech_sources.append(article)
        
        print(f"\nTech source articles: {len(tech_sources)}")
        
        for i, article in enumerate(tech_sources[:10], 1):
            source = article.get('source', 'Unknown')
            category = article.get('category', 'Unknown')
            title = article.get('title', 'No title')[:60]
            
            print(f"{i:2d}. {source:12} | {category:12} | {title}...")
        
        # Category distribution
        categories = {}
        for article in data:
            cat = article.get('category', 'Unknown')
            categories[cat] = categories.get(cat, 0) + 1
        
        print(f"\nCategory distribution:")
        for cat, count in sorted(categories.items()):
            print(f"  {cat:15}: {count:2d} articles")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
