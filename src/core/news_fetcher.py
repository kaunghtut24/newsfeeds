import requests
import time
from datetime import datetime
from typing import List, Dict
from bs4 import BeautifulSoup
import feedparser
import asyncio

class NewsFetcher:
    def __init__(self, sources: Dict[str, str]):
        self.news_sources = sources

    def _get_article_full_text(self, url: str) -> str:
        """Fetches the full text content of an article from its URL."""
        print(f"Attempting to fetch full text from: {url}")
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'lxml')

            # Common tags for article content
            article_tags = ['article', 'main', 'div']
            content_classes = ['story-body', 'article-content', 'post-content', 'entry-content', 'article-body']

            for tag in article_tags:
                for class_name in content_classes:
                    article_element = soup.find(tag, class_=class_name)
                    if article_element:
                        print(f"Successfully extracted text using {tag} with class {class_name}")
                        return article_element.get_text(separator='\n', strip=True)

            # Fallback: try to get all paragraph text
            paragraphs = soup.find_all('p')
            if paragraphs:
                print("Falling back to extracting all paragraph text.")
                return '\n'.join([p.get_text(strip=True) for p in paragraphs])

            print("No suitable content found for full text extraction.")
            return ""
        except requests.exceptions.Timeout:
            print(f"Timeout fetching full text from {url}")
            return ""
        except requests.exceptions.RequestException as e:
            print(f"Request error fetching full text from {url}: {e}")
            return ""
        except Exception as e:
            print(f"Unexpected error fetching full text from {url}: {e}")
            return ""

    def fetch_news_from_rss(self, source_name: str, rss_url: str) -> List[Dict]:
        """Fetch news from RSS feed using feedparser"""
        print(f"Starting RSS fetch for {source_name} from {rss_url} using feedparser...")
        try:
            feed = feedparser.parse(rss_url)
            news_items = []
            for entry in feed.entries:
                title = entry.title if hasattr(entry, 'title') else 'No Title'
                link = entry.link if hasattr(entry, 'link') else ''
                published = entry.published if hasattr(entry, 'published') else datetime.now().isoformat()
                
                full_text = self._get_article_full_text(link) if link else ""

                news_items.append({
                    'title': title,
                    'link': link,
                    'source': source_name,
                    'timestamp': published,
                    'full_text': full_text
                })
                
                if len(news_items) >= 5:  # Limit to 5 items per source
                    break
            
            print(f"Found {len(news_items)} news items from {source_name}")
            return news_items
            
        except Exception as e:
            print(f"Error fetching from {source_name}: {e}")
            return []
    
    def fetch_news_from_api(self, source_name: str) -> List[Dict]:
        """Fetch news from API sources"""
        print(f"Starting API fetch for {source_name}...")
        try:
            if source_name == "hackernews":
                # Hacker News API
                response = requests.get("https://hacker-news.firebaseio.com/v0/topstories.json", timeout=10)
                story_ids = response.json()[:10]
                print(f"Successfully fetched top story IDs for {source_name}.")
                
                news_items = []
                for story_id in story_ids:
                    story_response = requests.get(f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json", timeout=10)
                    story = story_response.json()
                    
                    if story and 'title' in story:
                        link = story.get('url', f"https://news.ycombinator.com/item?id={story_id}")
                        full_text = self._get_article_full_text(link) if link else ""

                        news_items.append({
                            'title': story['title'],
                            'link': link,
                            'source': 'hackernews',
                            'timestamp': datetime.fromtimestamp(story.get('time', time.time())).isoformat(),
                            'full_text': full_text
                        })
                print(f"Found {len(news_items)} news items from {source_name}")
                return news_items
                
        except requests.exceptions.Timeout:
            print(f"Timeout fetching API for {source_name}")
            return []
        except requests.exceptions.RequestException as e:
            print(f"Request error fetching API for {source_name}: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error during API fetch for {source_name}: {e}")
            return []

    def fetch_all_news(self) -> List[Dict]:
        """Fetch news from all sources"""
        print("Starting fetch_all_news...")
        all_news = []
        
        for source_name, source_url in self.news_sources.items():
            print(f"Processing source: {source_name}")
            if "hackernews" in source_name:
                news_items = self.fetch_news_from_api(source_name)
            else:
                news_items = self.fetch_news_from_rss(source_name, source_url)
            
            all_news.extend(news_items)
            time.sleep(1)  # Be nice to servers
        
        # Remove duplicates based on title
        seen_titles = set()
        unique_news = []
        for item in all_news:
            if item['title'] not in seen_titles:
                seen_titles.add(item['title'])
                unique_news.append(item)
        
        print(f"Finished fetch_all_news. Total unique items: {len(unique_news)}")
        return unique_news