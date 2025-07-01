#!/usr/bin/env python3
"""
Full News Feed Application Server
=================================

Complete server with working LLM integration for AI-powered news summarization.
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
from core.multi_llm_summarizer import MultiLLMSummarizer

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

def reload_config():
    """Reload configuration and update global variables"""
    global news_sources, ollama_model
    config = load_config()
    news_sources = config.get("news_sources", {})
    ollama_model = config.get("ollama_model", "llama3:8b")

config = load_config()
news_sources = config.get("news_sources", {})
ollama_model = config.get("ollama_model", "llama3:8b")

# Setup data directory
data_dir = os.path.join(os.getcwd(), 'data')
os.makedirs(data_dir, exist_ok=True)

# Initialize components
news_fetcher = NewsFetcher(news_sources)
data_manager = DataManager(base_path=data_dir)
categorizer = Categorizer()

# Initialize LLM summarizer with error handling
try:
    multi_llm_summarizer = MultiLLMSummarizer(config_file='llm_config.json')
    print("✅ LLM Summarizer initialized successfully")
except Exception as e:
    print(f"⚠️ Warning: LLM Summarizer initialization failed: {e}")
    print("   AI summarization will be disabled, using fallback summaries")
    multi_llm_summarizer = None

# Global processing state
is_processing = False
processing_status = "Ready"
processing_stats = {
    "total_sources": 0,
    "completed_sources": 0,
    "total_articles": 0,
    "processed_articles": 0,
    "current_source": "",
    "current_batch": 0
}

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/health')
def health_check():
    """General application health check"""
    try:
        # Check if data manager can load data
        articles = data_manager.load_news_data()
        article_count = len(articles) if articles else 0

        # Check if LLM is available
        llm_available = multi_llm_summarizer is not None

        # Check if Ollama is running
        ollama_available = False
        try:
            import requests
            response = requests.get('http://localhost:11434/api/tags', timeout=3)
            ollama_available = response.status_code == 200
        except:
            pass

        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'components': {
                'data_manager': True,
                'llm_summarizer': llm_available,
                'ollama': ollama_available,
                'news_fetcher': True,
                'categorizer': True
            },
            'stats': {
                'articles_count': article_count,
                'sources_count': len(news_sources),
                'processing': is_processing
            }
        })

    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/news')
def get_news():
    """API endpoint to get news articles"""
    try:
        articles = data_manager.load_news_data()
        if articles:
            return jsonify({
                'success': True,
                'news': articles,  # Frontend expects 'news'
                'articles': articles,  # Keep for compatibility
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

@app.route('/api/sources')
def get_sources():
    """API endpoint to get all available news sources"""
    try:
        # Load user preferences for enabled sources
        user_sources_file = os.path.join(data_dir, 'user_sources.json')
        enabled_sources = set()

        if os.path.exists(user_sources_file):
            with open(user_sources_file, 'r', encoding='utf-8') as f:
                user_prefs = json.load(f)
                enabled_sources = set(user_prefs.get('enabled_sources', []))
        else:
            # Default: all sources enabled
            enabled_sources = set(news_sources.keys())

        sources_info = []
        for source_name, source_config in news_sources.items():
            # Handle both string URLs and dict configurations
            if isinstance(source_config, str):
                # Simple URL format
                source_info = {
                    'name': source_name,
                    'url': source_config,
                    'type': 'rss',
                    'description': f'RSS feed from {source_name}',
                    'enabled': source_name in enabled_sources,
                    'category': 'General'
                }
            else:
                # Dict format with detailed configuration
                source_info = {
                    'name': source_name,
                    'url': source_config.get('url', ''),
                    'type': source_config.get('type', 'rss'),
                    'description': source_config.get('description', f'RSS feed from {source_name}'),
                    'enabled': source_name in enabled_sources,
                    'category': source_config.get('category', 'General')
                }
            sources_info.append(source_info)

        return jsonify({
            'success': True,
            'sources': sources_info,
            'total_sources': len(sources_info),
            'enabled_sources': len(enabled_sources)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get sources: {str(e)}'
        })

@app.route('/api/sources/edit', methods=['POST'])
def edit_source():
    """API endpoint to edit a news source"""
    try:
        data = request.get_json()
        old_name = data.get('old_name')
        new_name = data.get('new_name')
        new_url = data.get('new_url')

        if not old_name or not new_name or not new_url:
            return jsonify({
                'success': False,
                'error': 'Missing required fields: old_name, new_name, new_url'
            })

        # Load current config
        config = load_config()
        news_sources = config.get("news_sources", {})

        if old_name not in news_sources:
            return jsonify({
                'success': False,
                'error': 'Source not found'
            })

        # Update the source
        if old_name != new_name:
            # Remove old entry and add new one
            del news_sources[old_name]

        news_sources[new_name] = new_url

        # Save updated config
        config["news_sources"] = news_sources
        with open('config.json', 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)

        # Reload config to update global variable
        reload_config()

        return jsonify({
            'success': True,
            'message': f'Source "{old_name}" updated to "{new_name}"'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to edit source: {str(e)}'
        })

@app.route('/api/sources/delete', methods=['POST'])
def delete_source():
    """API endpoint to delete a news source"""
    try:
        data = request.get_json()
        source_name = data.get('source_name')

        if not source_name:
            return jsonify({
                'success': False,
                'error': 'Missing source_name'
            })

        # Load current config
        config = load_config()
        news_sources = config.get("news_sources", {})

        if source_name not in news_sources:
            return jsonify({
                'success': False,
                'error': 'Source not found'
            })

        # Remove the source
        del news_sources[source_name]

        # Save updated config
        config["news_sources"] = news_sources
        with open('config.json', 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)

        # Reload config to update global variable
        reload_config()

        # Also remove from user preferences if exists
        user_sources_file = os.path.join(data_dir, 'user_sources.json')
        if os.path.exists(user_sources_file):
            with open(user_sources_file, 'r', encoding='utf-8') as f:
                user_prefs = json.load(f)

            enabled_sources = set(user_prefs.get('enabled_sources', []))
            enabled_sources.discard(source_name)

            user_prefs['enabled_sources'] = list(enabled_sources)
            with open(user_sources_file, 'w', encoding='utf-8') as f:
                json.dump(user_prefs, f, indent=2, ensure_ascii=False)

        return jsonify({
            'success': True,
            'message': f'Source "{source_name}" deleted successfully'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to delete source: {str(e)}'
        })

@app.route('/api/sources/toggle', methods=['POST'])
def toggle_source():
    """API endpoint to enable/disable a news source"""
    try:
        data = request.get_json()
        source_name = data.get('source_name')
        enabled = data.get('enabled', True)

        if not source_name or source_name not in news_sources:
            return jsonify({
                'success': False,
                'error': 'Invalid source name'
            })

        # Load current user preferences
        user_sources_file = os.path.join(data_dir, 'user_sources.json')
        user_prefs = {'enabled_sources': list(news_sources.keys())}  # Default: all enabled

        if os.path.exists(user_sources_file):
            with open(user_sources_file, 'r', encoding='utf-8') as f:
                user_prefs = json.load(f)

        enabled_sources = set(user_prefs.get('enabled_sources', []))

        # Toggle the source
        if enabled:
            enabled_sources.add(source_name)
        else:
            enabled_sources.discard(source_name)

        # Save updated preferences
        user_prefs['enabled_sources'] = list(enabled_sources)
        with open(user_sources_file, 'w', encoding='utf-8') as f:
            json.dump(user_prefs, f, indent=2, ensure_ascii=False)

        return jsonify({
            'success': True,
            'source_name': source_name,
            'enabled': enabled,
            'total_enabled': len(enabled_sources)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to toggle source: {str(e)}'
        })

@app.route('/api/fetch-news', methods=['POST'])
def fetch_news():
    """API endpoint to fetch and summarize news with LLM"""
    global is_processing, processing_status, processing_stats
    
    if is_processing:
        return jsonify({
            'success': False,
            'message': 'Already processing news'
        })
    
    def process_news_with_llm():
        global is_processing, processing_status, processing_stats
        
        try:
            is_processing = True
            processing_status = "🚀 Starting news processing with AI summarization..."
            
            # Load user preferences for enabled sources
            user_sources_file = os.path.join(data_dir, 'user_sources.json')
            enabled_sources = set(news_sources.keys())  # Default: all enabled

            if os.path.exists(user_sources_file):
                with open(user_sources_file, 'r', encoding='utf-8') as f:
                    user_prefs = json.load(f)
                    enabled_sources = set(user_prefs.get('enabled_sources', list(news_sources.keys())))

            # Filter sources based on user preferences
            sources = [(name, config) for name, config in news_sources.items() if name in enabled_sources]

            # Reset stats
            processing_stats.update({
                "total_sources": len(sources),
                "completed_sources": 0,
                "total_articles": 0,
                "processed_articles": 0,
                "current_source": "",
                "current_batch": 0,
                "enabled_sources": list(enabled_sources),
                "disabled_sources": [name for name in news_sources.keys() if name not in enabled_sources]
            })
            
            all_processed_news = []
            
            # Process each source
            for source_idx, (source_name, source_url) in enumerate(sources, 1):
                try:
                    processing_stats["current_source"] = source_name
                    processing_status = f"📡 Fetching from {source_name} ({source_idx}/{len(sources)})..."
                    
                    # Fetch news from source
                    if "hackernews" in source_name.lower():
                        source_news = news_fetcher.fetch_news_from_api(source_name)
                    else:
                        source_news = news_fetcher.fetch_news_from_rss(source_name, source_url)
                    
                    if not source_news:
                        processing_status = f"⚠️ No news found from {source_name}"
                        processing_stats["completed_sources"] += 1
                        continue
                    
                    processing_stats["total_articles"] += len(source_news)
                    processing_status = f"🤖 AI summarizing {len(source_news)} articles from {source_name}..."
                    
                    # Categorize articles
                    for item in source_news:
                        item['category'] = categorizer.categorize_news(item)
                    
                    # AI Summarization with batching
                    batch_size = 3  # Smaller batches for better performance
                    source_summarized = []
                    
                    for batch_start in range(0, len(source_news), batch_size):
                        batch_end = min(batch_start + batch_size, len(source_news))
                        batch = source_news[batch_start:batch_end]
                        current_batch = batch_start // batch_size + 1
                        total_batches = (len(source_news) + batch_size - 1) // batch_size
                        
                        processing_stats["current_batch"] = current_batch
                        processing_status = f"🤖 AI processing batch {current_batch}/{total_batches} from {source_name}..."
                        
                        # Summarize batch with AI
                        try:
                            if multi_llm_summarizer is not None:
                                batch_summarized = multi_llm_summarizer.summarize_news_items(
                                    batch,
                                    model=ollama_model
                                )
                                source_summarized.extend(batch_summarized)
                                processing_stats["processed_articles"] += len(batch_summarized)
                            else:
                                # LLM not available, use fallback summaries
                                for article in batch:
                                    article['summary'] = article.get('description', 'No summary available')[:300] + '...'
                                    article['ai_summary'] = False
                                source_summarized.extend(batch)
                                processing_stats["processed_articles"] += len(batch)
                        except Exception as e:
                            print(f"Error summarizing batch: {e}")
                            # Fallback: use original articles with basic summaries
                            for article in batch:
                                article['summary'] = article.get('description', 'No summary available')[:300] + '...'
                                article['ai_summary'] = False
                            source_summarized.extend(batch)
                            processing_stats["processed_articles"] += len(batch)
                    
                    all_processed_news.extend(source_summarized)
                    processing_stats["completed_sources"] += 1
                    processing_status = f"✅ Completed {source_name}: {len(source_summarized)} articles with AI summaries"
                    
                except Exception as e:
                    processing_stats["completed_sources"] += 1
                    processing_status = f"❌ Error processing {source_name}: {str(e)}"
                    print(f"Error processing {source_name}: {e}")
                    continue
            
            # Save results
            if all_processed_news:
                processing_status = f"💾 Saving {len(all_processed_news)} AI-processed articles..."
                data_manager.save_news_data(all_processed_news)
                processing_status = f"🎉 Completed! Processed {len(all_processed_news)} articles with AI summaries from {processing_stats['completed_sources']} sources"
            else:
                processing_status = "❌ No articles were successfully processed"
                
        except Exception as e:
            processing_status = f"❌ Processing error: {str(e)}"
            print(f"Processing error: {e}")
        finally:
            is_processing = False
    
    # Start background processing
    thread = threading.Thread(target=process_news_with_llm)
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'success': True,
        'message': 'Started AI-powered news processing'
    })

@app.route('/api/status')
def get_status():
    """API endpoint to get processing status"""
    global is_processing, processing_status, processing_stats
    
    return jsonify({
        'is_processing': is_processing,
        'status': processing_status,
        'stats': processing_stats,
        'mode': 'full_ai'
    })

@app.route('/api/config')
def get_config():
    """API endpoint to get configuration"""
    # Always load fresh config to ensure latest values
    current_config = load_config()
    return jsonify(current_config)

@app.route('/api/saved-searches')
def get_saved_searches():
    """API endpoint for saved searches"""
    return jsonify([])

@app.route('/api/trending-analysis')
def get_trending_analysis():
    """API endpoint for trending analysis"""
    return jsonify({
        'trending_topics': [],
        'sentiment_overview': {'positive': 0, 'neutral': 0, 'negative': 0}
    })

@app.route('/api/content-insights')
def get_content_insights():
    """API endpoint for content insights"""
    try:
        articles = data_manager.load_news_data()
        return jsonify({
            'total_articles': len(articles) if articles else 0,
            'sources_count': len(news_sources),
            'categories': {}
        })
    except:
        return jsonify({
            'total_articles': 0,
            'sources_count': len(news_sources),
            'categories': {}
        })

@app.route('/api/ollama-model', methods=['POST'])
def save_ollama_model():
    """API endpoint to save selected Ollama model"""
    try:
        data = request.get_json()
        model = data.get('model')

        if not model:
            return jsonify({
                'success': False,
                'error': 'No model specified'
            })

        # Load current config
        config = load_config()

        # Update the Ollama model
        config['ollama_model'] = model

        # Save updated config
        with open('config.json', 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)

        # Update global variables
        global ollama_model
        ollama_model = model

        # Reload config to update global variable
        reload_config()

        # Reinitialize LLM summarizer with new model
        global multi_llm_summarizer
        try:
            from src.core.multi_llm_summarizer import MultiLLMSummarizer
            multi_llm_summarizer = MultiLLMSummarizer()
            print(f"✅ LLM Summarizer reinitialized with model: {model}")
        except Exception as e:
            print(f"⚠️ Warning: Could not reinitialize LLM summarizer: {e}")

        return jsonify({
            'success': True,
            'message': f'Ollama model updated to: {model}',
            'model': model
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to save Ollama model: {str(e)}'
        })

@app.route('/api/ollama-status')
def get_ollama_status():
    """API endpoint for Ollama status"""
    try:
        import requests
        response = requests.get('http://localhost:11434/api/tags', timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            return jsonify({
                'available': True,
                'models': [m['name'] for m in models],
                'message': f'Ollama running with {len(models)} models'
            })
        else:
            return jsonify({
                'available': False,
                'message': 'Ollama not responding'
            })
    except:
        return jsonify({
            'available': False,
            'message': 'Ollama not available'
        })

@app.route('/api/llm-providers/health-check', methods=['POST'])
def health_check_providers():
    """API endpoint for LLM provider health check"""
    try:
        health_results = {}

        # Check Ollama
        try:
            import requests
            response = requests.get('http://localhost:11434/api/tags', timeout=5)
            health_results['ollama'] = response.status_code == 200
        except:
            health_results['ollama'] = False

        # Check other providers (placeholder - would need API keys to actually test)
        health_results['openai'] = False  # Would need API key to test
        health_results['anthropic'] = False  # Would need API key to test
        health_results['google'] = False  # Would need API key to test

        return jsonify({
            'success': True,
            'health_results': health_results,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Health check failed: {str(e)}',
            'health_results': {},
            'timestamp': datetime.now().isoformat()
        })

@app.route('/api/llm-providers')
def get_llm_providers():
    """API endpoint for LLM providers"""
    try:
        with open('llm_config.json', 'r') as f:
            llm_config = json.load(f)

        providers = {}
        available_providers = []
        available_models = {}

        for provider, config in llm_config.items():
            if provider not in ['budget', 'fallback_strategy', 'default_model_preferences']:
                models = list(config.get('models', {}).keys())
                enabled = config.get('enabled', False)

                providers[provider] = {
                    'enabled': enabled,
                    'available_models': models,
                    'request_count': 0,  # Placeholder - would come from usage tracking
                    'success_rate': 1.0,  # Placeholder - would come from usage tracking
                    'total_cost': 0.0,   # Placeholder - would come from usage tracking
                    'models': config.get('models', {})
                }

                if enabled:
                    available_providers.append(provider)
                    available_models[provider] = models

        # Get budget info
        budget_info = llm_config.get('budget', {
            'daily_limit': 10.0,
            'monthly_limit': 100.0,
            'current_daily_usage': 0.0,
            'current_monthly_usage': 0.0
        })

        return jsonify({
            'success': True,
            'providers': providers,
            'available_providers': available_providers,
            'available_models': available_models,
            'budget': budget_info
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error loading LLM providers: {str(e)}',
            'providers': {},
            'available_providers': [],
            'available_models': {},
            'budget': {}
        })

@app.route('/api/search', methods=['POST'])
def search_news():
    """API endpoint for advanced news search"""
    try:
        search_query = request.get_json()
        if not search_query:
            return jsonify({
                'success': False,
                'error': 'No search query provided'
            })

        # Load news data
        articles = data_manager.load_news_data()
        if not articles:
            return jsonify({
                'success': True,
                'results': [],
                'total_results': 0,
                'message': 'No articles available to search'
            })

        # Extract search parameters
        text_query = search_query.get('text', '').lower().strip()
        sources_filter = search_query.get('sources', [])
        categories_filter = search_query.get('categories', [])
        date_from = search_query.get('date_from')
        date_to = search_query.get('date_to')
        sentiment_filter = search_query.get('sentiment')
        sort_by = search_query.get('sort_by', 'relevance')
        limit = search_query.get('limit', 50)

        # Filter articles
        filtered_articles = []

        for article in articles:
            # Text search
            if text_query:
                searchable_text = (
                    article.get('title', '') + ' ' +
                    article.get('summary', '') + ' ' +
                    article.get('description', '') + ' ' +
                    article.get('content', '')
                ).lower()

                if text_query not in searchable_text:
                    continue

            # Source filter
            if sources_filter and article.get('source') not in sources_filter:
                continue

            # Category filter
            if categories_filter and article.get('category') not in categories_filter:
                continue

            # Add relevance score for sorting
            relevance_score = 0
            if text_query:
                title_matches = article.get('title', '').lower().count(text_query)
                summary_matches = article.get('summary', '').lower().count(text_query)
                relevance_score = title_matches * 3 + summary_matches * 2

            article['relevance_score'] = relevance_score
            filtered_articles.append(article)

        # Sort results
        if sort_by == 'relevance' and text_query:
            filtered_articles.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        elif sort_by == 'date':
            filtered_articles.sort(key=lambda x: x.get('published_date', ''), reverse=True)
        elif sort_by == 'source':
            filtered_articles.sort(key=lambda x: x.get('source', ''))

        # Limit results
        if limit:
            filtered_articles = filtered_articles[:limit]

        # Remove relevance score from results
        for article in filtered_articles:
            article.pop('relevance_score', None)

        return jsonify({
            'success': True,
            'results': filtered_articles,
            'total_results': len(filtered_articles),
            'query': search_query
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Search error: {str(e)}'
        })

def main():
    print("🚀 News Feed Application - Full AI-Powered Server")
    print("=" * 60)
    print("🤖 Features: AI Summarization, Multi-LLM Support, Real-time Processing")
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
