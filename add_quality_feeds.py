#!/usr/bin/env python3
"""
Script to add high-quality RSS feeds to the news application
"""

import requests
import json
import time

# High-quality RSS feeds organized by category
QUALITY_FEEDS = {
    "World News": [
        ("BBC World News", "http://feeds.bbci.co.uk/news/world/rss.xml"),
        ("Al Jazeera English", "https://www.aljazeera.com/xml/rss/all.xml"),
        ("Guardian World", "https://www.theguardian.com/world/rss"),
        ("CNN World", "http://rss.cnn.com/rss/edition.rss"),
        ("NPR World", "https://feeds.npr.org/1004/rss.xml"),
    ],
    "Business": [
        ("BBC Business", "http://feeds.bbci.co.uk/news/business/rss.xml"),
        ("Guardian Business", "https://www.theguardian.com/business/rss"),
        ("Financial Times", "https://www.ft.com/rss/home"),
        ("Bloomberg Markets", "https://feeds.bloomberg.com/markets/news.rss"),
        ("MarketWatch", "http://feeds.marketwatch.com/marketwatch/topstories/"),
    ],
    "Technology": [
        ("BBC Technology", "http://feeds.bbci.co.uk/news/technology/rss.xml"),
        ("Guardian Technology", "https://www.theguardian.com/technology/rss"),
        ("TechCrunch", "https://techcrunch.com/feed/"),
        ("Ars Technica", "http://feeds.arstechnica.com/arstechnica/index"),
        ("Wired", "https://www.wired.com/feed/rss"),
        ("The Verge", "https://www.theverge.com/rss/index.xml"),
        ("Engadget", "https://www.engadget.com/rss.xml"),
        ("ZDNet", "https://www.zdnet.com/news/rss.xml"),
    ],
    "Market": [
        ("CNBC Markets", "https://www.cnbc.com/id/10000664/device/rss/rss.html"),
        ("WSJ Markets", "https://feeds.a.dj.com/rss/RSSMarketsMain.xml"),
        ("Seeking Alpha", "https://seekingalpha.com/feed.xml"),
    ]
}

def add_source_to_config(name, url, category):
    """Add source directly to config.json"""
    try:
        # Read current config
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        # Add new source
        config['news_sources'][name] = {
            "url": url,
            "category": category
        }
        
        # Write back to config
        with open('config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Added {name} to config.json")
        return True
        
    except Exception as e:
        print(f"❌ Error adding {name} to config: {e}")
        return False

def main():
    print("🚀 Adding High-Quality RSS Feeds to News Application")
    print("=" * 60)
    
    added_count = 0
    total_count = sum(len(feeds) for feeds in QUALITY_FEEDS.values())
    
    for category, feeds in QUALITY_FEEDS.items():
        print(f"\n📰 Adding {category} feeds...")
        
        for name, url in feeds:
            print(f"  Adding: {name}")
            
            if add_source_to_config(name, url, category):
                added_count += 1
            
            time.sleep(0.1)  # Small delay to be nice
    
    print(f"\n🎉 Successfully added {added_count}/{total_count} high-quality RSS feeds!")
    print("\n📋 Summary of added feeds:")
    
    for category, feeds in QUALITY_FEEDS.items():
        print(f"\n{category}:")
        for name, url in feeds:
            print(f"  • {name}")
    
    print(f"\n💡 Restart the server to load the new feeds!")

if __name__ == "__main__":
    main()
