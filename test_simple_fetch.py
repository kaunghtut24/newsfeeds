#!/usr/bin/env python3
"""
Simple News Fetch Test
======================

Test fetching news without LLM processing to isolate the issue.
"""

import sys
import json
import os
from pathlib import Path

# Add src to Python path
src_path = str(Path(__file__).parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

def test_simple_fetch():
    """Test simple news fetching and saving without LLM processing."""
    print("🧪 Simple News Fetch Test")
    print("=" * 40)
    
    try:
        # Load config
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        news_sources = config.get('news_sources', {})
        print(f"📰 Loaded {len(news_sources)} news sources")
        
        # Import required modules
        from core.news_fetcher import NewsFetcher
        from core.data_manager import DataManager
        
        # Create data directory
        data_dir = os.path.join(os.getcwd(), 'data')
        os.makedirs(data_dir, exist_ok=True)
        print(f"📁 Created data directory: {data_dir}")
        
        # Initialize components
        news_fetcher = NewsFetcher(news_sources)
        data_manager = DataManager(base_path=data_dir)
        
        print("✅ Components initialized")
        
        # Fetch news
        print("📡 Fetching news...")
        articles = news_fetcher.fetch_all_news()
        print(f"📊 Fetched {len(articles)} articles")
        
        if articles:
            # Add basic metadata
            for article in articles:
                article['processed_at'] = '2025-07-01T06:00:00Z'
                article['category'] = 'General'
                if 'summary' not in article:
                    article['summary'] = article.get('description', 'No summary available')
            
            # Save articles
            print("💾 Saving articles...")
            data_manager.save_news_data(articles)
            print("✅ Articles saved successfully")
            
            # Test loading
            print("📖 Testing data loading...")
            loaded_articles = data_manager.load_news_data()
            print(f"📊 Loaded {len(loaded_articles)} articles")
            
            if loaded_articles:
                print("🎉 Success! News fetching and saving is working")
                print(f"   First article: {loaded_articles[0].get('title', 'No title')}")
                return True
            else:
                print("❌ No articles loaded back")
                return False
        else:
            print("❌ No articles fetched")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_simple_fetch()
    if success:
        print("\n✅ Test passed! The issue is likely in the LLM processing.")
    else:
        print("\n❌ Test failed! The issue is in basic news fetching/saving.")
