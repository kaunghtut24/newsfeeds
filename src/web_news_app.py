#!/usr/bin/env python3
"""
Web-based News Feed Application with LLM Summarization
Flask web app that fetches news and summarizes with Ollama
"""

from flask import Flask, render_template, jsonify, request
import os
import threading
import json
import subprocess
from datetime import datetime

from core.news_fetcher import NewsFetcher
from core.multi_llm_summarizer import MultiLLMSummarizer
from core.summarizer import Summarizer
from core.data_manager import DataManager
from core.reporting import ReportGenerator
from core.categorizer import Categorizer
from core.search_engine import NewsSearchEngine, SearchQuery
from src.core.saved_searches import SavedSearchManager
from src.core.content_enhancer import ContentEnhancer

app = Flask(__name__,
            template_folder='../templates',
            static_folder='../static',
            static_url_path='/static')
app.secret_key = 'news_feed_secret_key'

CONFIG_FILE = '/home/yuthar/Documents/news_feed_application/config.json'

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {"news_sources": {}, "ollama_model": "llama3:8b"}

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

config = load_config()

# Global variables
news_sources = config["news_sources"]
ollama_model = config.get("ollama_model", "llama3:8b")

news_fetcher = NewsFetcher(news_sources)
# Initialize multi-LLM summarizer
multi_llm_summarizer = MultiLLMSummarizer(config_file='llm_config.json')
categorizer = Categorizer()
data_manager = DataManager(base_path='/home/yuthar/Documents/news_feed_application/')
report_generator = ReportGenerator(base_path='/home/yuthar/Documents/news_feed_application/')
# Initialize search engine and saved searches
search_engine = NewsSearchEngine()
saved_search_manager = SavedSearchManager()
# Initialize content enhancer
content_enhancer = ContentEnhancer()
is_processing = False
processing_status = ""
processing_start_time = None
processing_stats = {
    "total_sources": 0,
    "completed_sources": 0,
    "current_source": "",
    "total_articles": 0,
    "completed_articles": 0,
    "failed_articles": 0,
    "current_batch": 0,
    "total_batches": 0
}



@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/news')
def get_news():
    """API endpoint to get news data"""
    try:
        news_data = data_manager.load_news_data()
        if news_data:
            return jsonify({'success': True, 'news': news_data})
        else:
            return jsonify({'success': False, 'message': 'No news data available'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/fetch-news', methods=['POST'])
def fetch_news():
    """API endpoint to fetch and summarize news"""
    global is_processing, processing_status
    
    if is_processing:
        return jsonify({'success': False, 'message': 'Already processing news'})
    
    # Start processing in background
    def process_news():
        global is_processing, processing_status, processing_start_time, processing_stats

        try:
            is_processing = True
            processing_start_time = datetime.now()
            all_processed_news = []

            # Initialize processing stats
            sources = list(news_sources.items())
            processing_stats.update({
                "total_sources": len(sources),
                "completed_sources": 0,
                "current_source": "",
                "total_articles": 0,
                "completed_articles": 0,
                "failed_articles": 0,
                "current_batch": 0,
                "total_batches": 0
            })

            for source_idx, (source_name, source_url) in enumerate(sources, 1):
                try:
                    processing_stats["current_source"] = source_name
                    processing_status = f"📡 Fetching from {source_name} ({source_idx}/{processing_stats['total_sources']})..."

                    # Fetch news from single source
                    if "hackernews" in source_name:
                        source_news = news_fetcher.fetch_news_from_api(source_name)
                    else:
                        source_news = news_fetcher.fetch_news_from_rss(source_name, source_url)

                    if not source_news:
                        processing_status = f"⚠️ No news found from {source_name}"
                        processing_stats["completed_sources"] += 1
                        continue

                    # Update article counts
                    processing_stats["total_articles"] += len(source_news)

                    processing_status = f"📝 Processing {len(source_news)} articles from {source_name}..."

                    # Categorize news for this source
                    for item in source_news:
                        item['category'] = categorizer.categorize_news(item)

                    # Summarize news from this source with batching
                    processing_status = f"🤖 Summarizing {len(source_news)} articles from {source_name}..."

                    try:
                        # Process in smaller batches to avoid overwhelming the model
                        batch_size = 5  # Process 5 articles at a time
                        source_summarized = []
                        total_batches = (len(source_news) + batch_size - 1) // batch_size
                        processing_stats["total_batches"] = total_batches

                        for batch_start in range(0, len(source_news), batch_size):
                            batch_end = min(batch_start + batch_size, len(source_news))
                            batch = source_news[batch_start:batch_end]
                            current_batch = batch_start // batch_size + 1
                            processing_stats["current_batch"] = current_batch

                            processing_status = f"🤖 Summarizing batch {current_batch}/{total_batches} from {source_name} ({batch_start + 1}-{batch_end}/{len(source_news)})..."

                            # Summarize this batch with enhanced parameters
                            batch_summarized = multi_llm_summarizer.summarize_news_items(
                                batch,
                                preferred_model=ollama_model,
                                provider_preference="ollama",
                                max_text_length=2000,
                                batch_delay=0.5,
                                max_retries=2
                            )
                            source_summarized.extend(batch_summarized)
                            processing_stats["completed_articles"] += len(batch_summarized)

                    except Exception as e:
                        processing_status = f"⚠️ Summarization failed for {source_name}: {str(e)}. Using original content."
                        source_summarized = source_news

                    # Enhance content for this source
                    processing_status = f"✨ Enhancing content for {source_name}..."
                    try:
                        enhanced_source_news = content_enhancer.enhance_articles(source_summarized)
                    except Exception as e:
                        processing_status = f"⚠️ Enhancement failed for {source_name}: {str(e)}. Using basic content."
                        enhanced_source_news = source_summarized

                    all_processed_news.extend(enhanced_source_news)
                    processing_stats["completed_sources"] += 1
                    processing_status = f"✅ Completed {source_name}: {len(enhanced_source_news)} articles processed ({processing_stats['completed_sources']}/{processing_stats['total_sources']} sources done)"

                except Exception as e:
                    processing_stats["failed_articles"] += len(source_news) if 'source_news' in locals() else 0
                    processing_stats["completed_sources"] += 1
                    processing_status = f"❌ Error processing {source_name}: {str(e)}"
                    continue

            # Final save and report generation
            if all_processed_news:
                processing_status = f"💾 Saving {len(all_processed_news)} processed articles..."
                try:
                    data_manager.save_news_data(all_processed_news)
                    report_generator.create_html_report(all_processed_news)
                    processing_status = f"✅ Completed! Processed {len(all_processed_news)} articles from {total_sources} sources"
                except Exception as e:
                    processing_status = f"⚠️ Completed with save errors: {str(e)}"
            else:
                processing_status = "❌ No articles were successfully processed"

        except Exception as e:
            processing_status = f"❌ Critical error: {str(e)}"
        finally:
            is_processing = False
            processing_start_time = None
    
    # Start background thread
    thread = threading.Thread(target=process_news)
    thread.daemon = True
    thread.start()
    
    return jsonify({'success': True, 'message': 'Started processing news'})

@app.route('/api/status')
def get_status():
    """API endpoint to get processing status with detailed progress"""
    global is_processing, processing_status, processing_start_time, processing_stats

    # Check for timeout (10 minutes)
    if is_processing and processing_start_time:
        elapsed = (datetime.now() - processing_start_time).total_seconds()
        if elapsed > 600:  # 10 minutes timeout
            is_processing = False
            processing_status = "⚠️ Processing timed out after 10 minutes. Please try again."
            processing_start_time = None

    response_data = {
        'is_processing': is_processing,
        'status': processing_status
    }

    # Add processing duration if currently processing
    if is_processing and processing_start_time:
        elapsed = (datetime.now() - processing_start_time).total_seconds()
        response_data['processing_duration'] = int(elapsed)
        response_data['status'] = f"{processing_status} (Running for {int(elapsed//60)}m {int(elapsed%60)}s)"

        # Add detailed progress information
        source_progress = 0
        article_progress = 0

        if processing_stats["total_sources"] > 0:
            source_progress = (processing_stats["completed_sources"] / processing_stats["total_sources"]) * 100

        if processing_stats["total_articles"] > 0:
            article_progress = (processing_stats["completed_articles"] / processing_stats["total_articles"]) * 100

        response_data['progress'] = {
            'sources': {
                'total': processing_stats["total_sources"],
                'completed': processing_stats["completed_sources"],
                'current': processing_stats["current_source"],
                'percentage': round(source_progress, 1)
            },
            'articles': {
                'total': processing_stats["total_articles"],
                'completed': processing_stats["completed_articles"],
                'failed': processing_stats["failed_articles"],
                'percentage': round(article_progress, 1)
            },
            'batches': {
                'current': processing_stats["current_batch"],
                'total': processing_stats["total_batches"]
            }
        }

    return jsonify(response_data)

@app.route('/api/reset-processing', methods=['POST'])
def reset_processing():
    """Reset processing status (emergency reset)"""
    global is_processing, processing_status, processing_start_time, processing_stats

    is_processing = False
    processing_status = "Processing reset by user"
    processing_start_time = None

    # Reset processing stats
    processing_stats.update({
        "total_sources": 0,
        "completed_sources": 0,
        "current_source": "",
        "total_articles": 0,
        "completed_articles": 0,
        "failed_articles": 0,
        "current_batch": 0,
        "total_batches": 0
    })

    return jsonify({
        "success": True,
        "message": "Processing status has been reset"
    })

@app.route('/api/ollama-status')
def check_ollama():
    """Check if Ollama is available and list models"""
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            models = []
            # Parse ollama list output
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1: # Skip header line
                for line in lines[1:]:
                    parts = line.split()
                    if parts: # Model name is the first part
                        models.append(parts[0])
            return jsonify({'available': True, 'models': models})
        else:
            return jsonify({'available': False, 'error': result.stderr, 'models': []})
    except Exception as e:
        return jsonify({'available': False, 'error': str(e), 'models': []})

@app.route('/report')
def view_report():
    """View the HTML report"""
    if os.path.exists('news_report.html'):
        with open('news_report.html', 'r', encoding='utf-8') as f:
            return f.read()
    else:
        return "No report available. Please fetch news first."

@app.route('/api/config', methods=['GET', 'POST'])
def manage_config():
    global config, news_sources, ollama_model, news_fetcher, summarizer
    if request.method == 'GET':
        return jsonify(config)
    elif request.method == 'POST':
        new_config = request.json
        if new_config:
            config.update(new_config)
            save_config(config)
            # Re-initialize global variables with new config
            news_sources = config["news_sources"]
            ollama_model = config["ollama_model"]
            news_fetcher = NewsFetcher(news_sources)
            # Note: Summarizer will be re-initialized on next news fetch
            return jsonify({"success": True, "message": "Configuration updated successfully"})
        return jsonify({"success": False, "message": "Invalid configuration data"})

@app.route('/api/ollama-status')
def ollama_status():
    """Check Ollama status and available models"""
    try:
        # Check if Ollama is available
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            # Parse available models
            models = []
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            for line in lines:
                if line.strip():
                    model_name = line.split()[0]  # First column is model name
                    models.append(model_name)

            return jsonify({
                "available": True,
                "models": models,
                "current_model": ollama_model
            })
        else:
            return jsonify({
                "available": False,
                "models": [],
                "error": "Ollama not responding"
            })
    except Exception as e:
        return jsonify({
            "available": False,
            "models": [],
            "error": str(e)
        })

@app.route('/api/llm-providers')
def get_llm_providers():
    """Get information about all LLM providers"""
    try:
        stats = multi_llm_summarizer.get_provider_stats()
        available_providers = multi_llm_summarizer.get_available_providers()
        available_models = multi_llm_summarizer.get_available_models()

        return jsonify({
            "success": True,
            "providers": stats["providers"],
            "available_providers": available_providers,
            "available_models": available_models,
            "fallback_order": stats["fallback_order"],
            "budget": stats["budget"],
            "total_providers": stats["total_providers"],
            "enabled_providers": stats["enabled_providers"]
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })

@app.route('/api/llm-providers/health-check', methods=['POST'])
def health_check_providers():
    """Perform health check on all LLM providers"""
    try:
        import asyncio
        health_results = asyncio.run(multi_llm_summarizer.health_check_all())

        return jsonify({
            "success": True,
            "health_results": health_results
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })

@app.route('/api/llm-providers/<provider_name>/enable', methods=['POST'])
def enable_provider(provider_name):
    """Enable a specific LLM provider"""
    try:
        multi_llm_summarizer.enable_provider(provider_name)
        return jsonify({
            "success": True,
            "message": f"Provider {provider_name} enabled"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })

@app.route('/api/llm-providers/<provider_name>/disable', methods=['POST'])
def disable_provider(provider_name):
    """Disable a specific LLM provider"""
    try:
        multi_llm_summarizer.disable_provider(provider_name)
        return jsonify({
            "success": True,
            "message": f"Provider {provider_name} disabled"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })

@app.route('/api/ollama-model', methods=['GET', 'POST'])
def manage_ollama_model():
    """Get or set the preferred Ollama model"""
    global config, ollama_model

    if request.method == 'GET':
        return jsonify({
            "success": True,
            "current_model": ollama_model,
            "available_models": []  # Will be populated by frontend
        })
    elif request.method == 'POST':
        try:
            data = request.json
            new_model = data.get('model')

            if not new_model:
                return jsonify({
                    "success": False,
                    "error": "Model name is required"
                })

            # Update global config
            config['ollama_model'] = new_model
            ollama_model = new_model
            save_config(config)

            return jsonify({
                "success": True,
                "message": f"Ollama model updated to: {new_model}",
                "current_model": new_model
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            })

@app.route('/api/llm-config', methods=['GET', 'POST'])
def llm_config():
    """Get or update LLM configuration"""
    if request.method == 'GET':
        try:
            with open('llm_config.json', 'r') as f:
                config = json.load(f)
            return jsonify({
                "success": True,
                "config": config
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            })
    elif request.method == 'POST':
        try:
            new_config = request.json
            with open('llm_config.json', 'w') as f:
                json.dump(new_config, f, indent=2)

            # Reinitialize the multi-LLM summarizer with new config
            global multi_llm_summarizer
            multi_llm_summarizer = MultiLLMSummarizer(config_file='llm_config.json')

            return jsonify({
                "success": True,
                "message": "LLM configuration updated successfully"
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            })

    elif request.method == 'POST':
        try:
            new_config = request.get_json()
            multi_llm_summarizer.save_config(new_config)

            # Reinitialize providers with new config
            # Note: In production, this should be handled more gracefully
            pass  # For now, restart the application to apply new config

            return jsonify({
                "success": True,
                "message": "LLM configuration updated"
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            })

@app.route('/api/search', methods=['POST'])
def search_news():
    """Advanced search for news articles"""
    try:
        search_params = request.get_json()

        # Create SearchQuery object
        query = SearchQuery(
            text=search_params.get('text', ''),
            sources=search_params.get('sources', []),
            categories=search_params.get('categories', []),
            sentiment=search_params.get('sentiment'),
            min_relevance=search_params.get('min_relevance', 0.0),
            sort_by=search_params.get('sort_by', 'relevance'),
            sort_order=search_params.get('sort_order', 'desc'),
            limit=search_params.get('limit', 50)
        )

        # Handle date filters
        if search_params.get('date_from'):
            from datetime import datetime
            query.date_from = datetime.fromisoformat(search_params['date_from'])
        if search_params.get('date_to'):
            from datetime import datetime
            query.date_to = datetime.fromisoformat(search_params['date_to'])

        # Load news data
        news_data = data_manager.load_news_data()

        # Perform search
        search_results = search_engine.search(query, news_data)

        # Convert results to JSON-serializable format
        results = []
        for result in search_results:
            results.append({
                'article': result.article,
                'relevance_score': result.relevance_score,
                'matched_fields': result.matched_fields,
                'highlighted_text': result.highlighted_text
            })

        return jsonify({
            "success": True,
            "results": results,
            "total_results": len(results),
            "query": search_params
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })

@app.route('/api/search/suggestions')
def get_search_suggestions():
    """Get search suggestions based on partial query"""
    try:
        partial_query = request.args.get('q', '')
        limit = int(request.args.get('limit', 10))

        if len(partial_query) < 2:
            return jsonify({
                "success": True,
                "suggestions": []
            })

        # Load news data
        news_data = data_manager.load_news_data()

        # Get suggestions
        suggestions = search_engine.get_search_suggestions(partial_query, news_data, limit)

        return jsonify({
            "success": True,
            "suggestions": suggestions
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })

@app.route('/api/saved-searches', methods=['GET', 'POST'])
def handle_saved_searches():
    """Get all saved searches or create a new one"""
    if request.method == 'GET':
        try:
            searches = saved_search_manager.get_all_searches()

            # Convert to JSON-serializable format
            search_list = []
            for search in searches:
                search_data = {
                    'id': search.id,
                    'name': search.name,
                    'query': {
                        'text': search.query.text,
                        'sources': search.query.sources,
                        'categories': search.query.categories,
                        'sentiment': search.query.sentiment,
                        'sort_by': search.query.sort_by,
                        'sort_order': search.query.sort_order
                    },
                    'created_at': search.created_at.isoformat(),
                    'last_used': search.last_used.isoformat() if search.last_used else None,
                    'use_count': search.use_count,
                    'is_favorite': search.is_favorite,
                    'tags': search.tags
                }
                search_list.append(search_data)

            return jsonify({
                "success": True,
                "searches": search_list
            })

        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            })

    elif request.method == 'POST':
        try:
            data = request.get_json()
            name = data.get('name')
            query_data = data.get('query')
            tags = data.get('tags', [])

            if not name or not query_data:
                return jsonify({
                    "success": False,
                    "error": "Name and query are required"
                })

            # Create SearchQuery object
            query = SearchQuery(
                text=query_data.get('text', ''),
                sources=query_data.get('sources', []),
                categories=query_data.get('categories', []),
                sentiment=query_data.get('sentiment'),
                min_relevance=query_data.get('min_relevance', 0.0),
                sort_by=query_data.get('sort_by', 'relevance'),
                sort_order=query_data.get('sort_order', 'desc'),
                limit=query_data.get('limit', 50)
            )

            # Save the search
            search_id = saved_search_manager.save_search(name, query, tags)

            return jsonify({
                "success": True,
                "search_id": search_id,
                "message": f"Search '{name}' saved successfully"
            })

        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            })

@app.route('/api/trending-analysis')
def get_trending_analysis():
    """Get trending topics and sentiment analysis"""
    try:
        # Load news data
        news_data = data_manager.load_news_data()

        if not news_data:
            return jsonify({
                "success": False,
                "error": "No news data available"
            })

        # Get trending analysis
        trending_analysis = content_enhancer.get_trending_analysis(news_data)

        return jsonify({
            "success": True,
            "trending_analysis": trending_analysis
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })

@app.route('/api/content-insights')
def get_content_insights():
    """Get content insights and statistics"""
    try:
        # Load news data
        news_data = data_manager.load_news_data()

        if not news_data:
            return jsonify({
                "success": False,
                "error": "No news data available"
            })

        # Calculate insights
        total_articles = len(news_data)

        # Sentiment distribution
        sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
        quality_scores = []
        reading_times = []
        sources = set()
        categories = set()

        for article in news_data:
            sentiment = article.get('sentiment', 'neutral')
            sentiment_counts[sentiment] += 1

            if 'content_quality_score' in article:
                quality_scores.append(article['content_quality_score'])

            if 'estimated_reading_time' in article:
                reading_times.append(article['estimated_reading_time'])

            if article.get('source'):
                sources.add(article['source'])

            if article.get('category'):
                categories.add(article['category'])

        # Calculate averages
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
        avg_reading_time = sum(reading_times) / len(reading_times) if reading_times else 0

        insights = {
            'total_articles': total_articles,
            'sentiment_distribution': {
                'positive': sentiment_counts['positive'],
                'negative': sentiment_counts['negative'],
                'neutral': sentiment_counts['neutral'],
                'positive_percentage': (sentiment_counts['positive'] / total_articles) * 100 if total_articles > 0 else 0,
                'negative_percentage': (sentiment_counts['negative'] / total_articles) * 100 if total_articles > 0 else 0,
                'neutral_percentage': (sentiment_counts['neutral'] / total_articles) * 100 if total_articles > 0 else 0
            },
            'content_quality': {
                'average_score': avg_quality,
                'high_quality_count': len([s for s in quality_scores if s > 0.7]),
                'low_quality_count': len([s for s in quality_scores if s < 0.4])
            },
            'reading_metrics': {
                'average_reading_time': avg_reading_time,
                'total_reading_time': sum(reading_times),
                'quick_reads': len([t for t in reading_times if t <= 2]),
                'long_reads': len([t for t in reading_times if t > 5])
            },
            'diversity': {
                'unique_sources': len(sources),
                'unique_categories': len(categories),
                'sources_list': sorted(list(sources)),
                'categories_list': sorted(list(categories))
            }
        }

        return jsonify({
            "success": True,
            "insights": insights
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })

if __name__ == '__main__':
    print("🗞️ Starting News Feed Pro Web Application...")
    print("📡 Open your browser to: http://localhost:5000")
    print("🎨 New modern UI with dark mode support!")
    print("🤖 Multi-LLM integration ready")
    print("Press Ctrl+C to stop")
    app.run(debug=True, host='0.0.0.0', port=5000)