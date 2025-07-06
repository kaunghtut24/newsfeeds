#!/usr/bin/env python3
"""
Test News Fetching Functionality
================================

This script tests the news fetching functionality to diagnose why no articles are being processed.
"""

import sys
import json
from pathlib import Path

# Add src to Python path
src_path = str(Path(__file__).parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

def test_config_loading():
    """Test if configuration is loading correctly."""
    print("🔧 Testing configuration loading...")
    
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        print(f"✅ Config loaded successfully")
        print(f"📰 Found {len(config.get('news_sources', {}))} news sources:")
        
        for name, url in config.get('news_sources', {}).items():
            print(f"   - {name}: {url}")
        
        return config
        
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        return None

def test_single_rss_feed(url, name="Test Feed"):
    """Test fetching from a single RSS feed."""
    print(f"\n📡 Testing RSS feed: {name}")
    print(f"🔗 URL: {url}")
    
    try:
        import feedparser
        import requests
        
        # Test basic connectivity
        print("🌐 Testing connectivity...")
        response = requests.get(url, timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('content-type', 'Unknown')}")
        
        # Test feedparser
        print("📰 Parsing RSS feed...")
        feed = feedparser.parse(url)
        
        print(f"   Feed title: {feed.feed.get('title', 'Unknown')}")
        print(f"   Feed description: {feed.feed.get('description', 'Unknown')[:100]}...")
        print(f"   Number of entries: {len(feed.entries)}")
        
        if feed.entries:
            entry = feed.entries[0]
            print(f"   First article title: {entry.get('title', 'No title')}")
            print(f"   First article link: {entry.get('link', 'No link')}")
            print(f"   First article published: {entry.get('published', 'No date')}")
        
        return len(feed.entries) > 0
        
    except Exception as e:
        print(f"❌ Error testing RSS feed: {e}")
        return False

def test_news_fetcher(config):
    """Test the NewsFetcher class directly."""
    print("\n🔍 Testing NewsFetcher class...")

    try:
        from core.news_fetcher import NewsFetcher

        print("✅ NewsFetcher imported successfully")

        # Get news sources from config
        news_sources = config.get('news_sources', {})

        # Create fetcher instance with sources
        fetcher = NewsFetcher(news_sources)
        print("✅ NewsFetcher instance created")

        # Test fetching news
        print("📰 Fetching news...")
        articles = fetcher.fetch_all_news()

        print(f"📊 Fetched {len(articles)} articles")

        if articles:
            article = articles[0]
            print(f"   First article: {article.get('title', 'No title')}")
            print(f"   Source: {article.get('source', 'Unknown')}")
            print(f"   URL: {article.get('url', 'No URL')}")

        return articles

    except Exception as e:
        print(f"❌ Error testing NewsFetcher: {e}")
        import traceback
        traceback.print_exc()
        return []

def main():
    """Run all tests."""
    print("🧪 News Fetching Diagnostic Test")
    print("=" * 50)
    
    # Test 1: Configuration
    config = test_config_loading()
    if not config:
        print("❌ Cannot proceed without valid configuration")
        return
    
    # Test 2: Individual RSS feeds
    news_sources = config.get('news_sources', {})
    working_feeds = 0
    
    for name, url in news_sources.items():
        if test_single_rss_feed(url, name):
            working_feeds += 1
    
    print(f"\n📊 RSS Feed Test Results:")
    print(f"   Working feeds: {working_feeds}/{len(news_sources)}")
    
    # Test 3: NewsFetcher class
    articles = test_news_fetcher(config)
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Test Summary:")
    print(f"   ✅ Config loaded: {'Yes' if config else 'No'}")
    print(f"   ✅ Working RSS feeds: {working_feeds}/{len(news_sources)}")
    print(f"   ✅ Articles fetched: {len(articles)}")
    
    if len(articles) == 0:
        print("\n🔧 Troubleshooting suggestions:")
        print("   1. Check internet connectivity")
        print("   2. Verify RSS feed URLs are accessible")
        print("   3. Check for firewall/proxy issues")
        print("   4. Try running with different news sources")
    else:
        print("\n🎉 News fetching is working correctly!")

if __name__ == "__main__":
    main()
