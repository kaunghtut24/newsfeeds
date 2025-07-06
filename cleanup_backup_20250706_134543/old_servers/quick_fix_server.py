#!/usr/bin/env python3
"""
Quick Fix Server - News Feed Application
========================================

A simplified version of the web server that bypasses LLM processing
for immediate testing of the news fetching functionality.
"""

import sys
import os
import json
import threading
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, jsonify, request

# Add src to Python path
src_path = str(Path(__file__).parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Import required modules
from core.news_fetcher import NewsFetcher
from core.data_manager import DataManager
from core.categorizer import Categorizer

# Initialize Flask app
app = Flask(__name__)

# Load configuration
def load_config():
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
        return {"news_sources": {}}

config = load_config()
news_sources = config.get("news_sources", {})

# Setup data directory
data_dir = os.path.join(os.getcwd(), 'data')
os.makedirs(data_dir, exist_ok=True)

# Initialize components
news_fetcher = NewsFetcher(news_sources)
data_manager = DataManager(base_path=data_dir)
categorizer = Categorizer()

# Global processing state
is_processing = False
processing_status = "Ready"

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/news')
def get_news():
    """API endpoint to get news articles"""
    try:
        articles = data_manager.load_news_data()
        if articles:
            return jsonify({
                'success': True,
                'news': articles,  # Frontend expects 'news' not 'articles'
                'articles': articles,  # Keep both for compatibility
                'count': len(articles)
            })
        else:
            return jsonify({
                'success': False,
                'message': 'No news data available'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error loading news: {str(e)}'
        })

@app.route('/api/fetch-news', methods=['POST'])
def fetch_news():
    """API endpoint to fetch news (simplified without LLM)"""
    global is_processing, processing_status
    
    if is_processing:
        return jsonify({
            'success': False,
            'message': 'Already processing news'
        })
    
    def process_news_simple():
        global is_processing, processing_status
        
        try:
            is_processing = True
            processing_status = "📡 Fetching news from sources..."
            
            # Fetch news
            articles = news_fetcher.fetch_all_news()
            
            if articles:
                processing_status = f"📝 Processing {len(articles)} articles..."
                
                # Add basic metadata and categorization
                for article in articles:
                    article['processed_at'] = datetime.now().isoformat()
                    article['category'] = categorizer.categorize_news(article)
                    if 'summary' not in article:
                        # Use description as summary if no LLM processing
                        article['summary'] = article.get('description', 'No summary available')[:500] + '...'
                
                processing_status = "💾 Saving articles..."
                data_manager.save_news_data(articles)
                
                processing_status = f"✅ Completed! Processed {len(articles)} articles"
            else:
                processing_status = "❌ No articles were fetched"
                
        except Exception as e:
            processing_status = f"❌ Error: {str(e)}"
        finally:
            is_processing = False
    
    # Start background processing
    thread = threading.Thread(target=process_news_simple)
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'success': True,
        'message': 'Started processing news (simplified mode)'
    })

@app.route('/api/status')
def get_status():
    """API endpoint to get processing status"""
    global is_processing, processing_status
    
    return jsonify({
        'is_processing': is_processing,
        'status': processing_status,
        'mode': 'simplified'
    })

@app.route('/api/config')
def get_config():
    """API endpoint to get configuration"""
    return jsonify(config)

@app.route('/api/saved-searches')
def get_saved_searches():
    """API endpoint for saved searches (placeholder)"""
    return jsonify([])

@app.route('/api/trending-analysis')
def get_trending_analysis():
    """API endpoint for trending analysis (placeholder)"""
    return jsonify({
        'trending_topics': [],
        'sentiment_overview': {'positive': 0, 'neutral': 0, 'negative': 0}
    })

@app.route('/api/content-insights')
def get_content_insights():
    """API endpoint for content insights (placeholder)"""
    return jsonify({
        'total_articles': 0,
        'sources_count': len(news_sources),
        'categories': {}
    })

@app.route('/api/ollama-status')
def get_ollama_status():
    """API endpoint for Ollama status (placeholder)"""
    return jsonify({
        'available': False,
        'message': 'LLM processing disabled in simplified mode'
    })

@app.route('/api/llm-providers')
def get_llm_providers():
    """API endpoint for LLM providers (placeholder)"""
    return jsonify([])

def main():
    print("🚀 News Feed Application - Quick Fix Server")
    print("=" * 50)
    print("📝 Note: This is a simplified version without LLM processing")
    print("🌐 Starting development server...")
    print("📱 Open your browser to: http://127.0.0.1:5000")
    print("🛑 Press Ctrl+C to stop the server")
    print()
    
    try:
        app.run(
            host='127.0.0.1',
            port=5000,
            debug=True,
            use_reloader=False
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")

if __name__ == "__main__":
    main()
