#!/usr/bin/env python3
"""
News Feed Application with LLM Summarization
Fetches news from various sources and summarizes them using Ollama
"""

import os
from typing import List, Dict

from .core.news_fetcher import NewsFetcher
from .core.summarizer import Summarizer
from .core.reporting import ReportGenerator
from .core.data_manager import DataManager
from .core.categorizer import Categorizer

class NewsFeedApp:
    def __init__(self):
        self.news_sources = {
            "techcrunch": "https://techcrunch.com/feed/",
            "hackernews": "https://news.ycombinator.com/rss",
            "reddit_programming": "https://www.reddit.com/r/programming/.rss",
            "reddit_technology": "https://www.reddit.com/r/technology/.rss"
        }
        self.news_fetcher = NewsFetcher(self.news_sources)
        self.summarizer = Summarizer()
        self.categorizer = Categorizer()
        self.report_generator = ReportGenerator(base_path='/home/yuthar/Documents/news_feed_application/')
        self.data_manager = DataManager(base_path='/home/yuthar/Documents/news_feed_application/')
        self.news_data = []

    def display_news(self, news_items: List[Dict]):
        """Display news in a nice format"""
        print("\n" + "="*80)
        print("🗞️  NEWS FEED SUMMARY")
        print("="*80)
        
        for i, item in enumerate(news_items, 1):
            print(f"\n{i}. {item['title']}")
            print(f"   Source: {item['source']}")
            print(f"   Link: {item['link']}")
            print(f"   Time: {item['timestamp']}")
            print(f"   Summary: {item.get('summary', 'No summary available')}")
            print("-" * 80)

    def run(self):
        """Main application runner"""
        print("🗞️  News Feed Application with LLM Summarization")
        print("=" * 60)
        
        # Check if we should load existing data
        if os.path.exists(self.data_manager.filename):
            choice = input("Found existing news data. Load it? (y/n): ").lower()
            if choice == 'y':
                self.news_data = self.data_manager.load_news_data()
                self.display_news(self.news_data)
                return
        
        # Fetch news
        print("\n📡 Fetching news from various sources...")
        news_items = self.news_fetcher.fetch_all_news()
        
        if not news_items:
            print("❌ No news items found. Check your internet connection.")
            return

        # Categorize news
        print(f"\n🗂️ Categorizing {len(news_items)} news items...")
        for item in news_items:
            item['category'] = self.categorizer.categorize_news(item)
        
        # Summarize news
        print(f"\n🤖 Summarizing {len(news_items)} news items...")
        summarized_news = self.summarizer.summarize_news_items(news_items)
        
        # Update the news data
        self.news_data = summarized_news
        
        # Display results
        self.display_news(summarized_news)
        
        # Save data
        self.data_manager.save_news_data(self.news_data)
        
        # Create HTML report
        self.report_generator.create_html_report(self.news_data)
        
        print(f"\n✅ Processed {len(summarized_news)} news items!")
        print("📄 Check 'news_report.html' for a formatted report")

def main():
    """Main function"""
    app = NewsFeedApp()
    app.run()

if __name__ == "__main__":
    main()