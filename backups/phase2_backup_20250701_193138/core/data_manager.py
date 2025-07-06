
import json
import os
from typing import List, Dict

class DataManager:
    def __init__(self, filename: str = "news_data.json", base_path: str = '/home/yuthar/Documents/news_feed_application/'):
        self.filename = os.path.join(base_path, filename)

    def save_news_data(self, news_data: List[Dict]):
        """Save news data to JSON file"""
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(news_data, f, indent=2, ensure_ascii=False)
            print(f"✅ News data saved to {self.filename}")
        except Exception as e:
            print(f"❌ Error saving news data: {e}")

    def load_news_data(self) -> List[Dict]:
        """Load news data from JSON file"""
        try:
            if os.path.exists(self.filename):
                with open(self.filename, 'r', encoding='utf-8') as f:
                    news_data = json.load(f)
                print(f"✅ News data loaded from {self.filename}")
                return news_data
        except Exception as e:
            print(f"❌ Error loading news data: {e}")
        return []
