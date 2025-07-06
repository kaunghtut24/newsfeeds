#!/usr/bin/env python3
"""
Full News Feed Application Server
=================================

Complete server with working LLM integration for AI-powered news summarization.
"""

import sys
import os
import json
import time
import threading
import logging
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, jsonify, request, send_from_directory

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add src to Python path
src_path = str(Path(__file__).parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Import required modules
from core.news_fetcher import NewsFetcher
from core.data_manager import DataManager
from core.categorizer import Categorizer
from core.multi_llm_summarizer import MultiLLMSummarizer
from core.reporting import ReportGenerator

# Import new AI features
from core.ai_features.smart_categorizer import SmartCategorizer
from core.ai_features.sentiment_analyzer import AdvancedSentimentAnalyzer
from core.ai_features.content_recommender import ContentRecommender
from core.ai_features.semantic_search import SemanticSearchEngine
from core.ai_features.content_relationship_mapper import ContentRelationshipMapper
from core.ai_features.trend_analyzer import TrendAnalyzer
from core.ai_features.ai_news_assistant import AINewsAssistant
from core.ai_features.smart_briefing_generator import SmartBriefingGenerator

# Import user management system
from core.user_management import UserManager, User, UserRole, UserStatus
from core.auth import init_auth, get_current_user, login_required, admin_required, user_owns_resource
from core.rbac import AccessControl, Permission, get_permission_checker

# Import enhanced systems
from core.admin_settings import AdminSettingsManager
from core.enhanced_user_sources import EnhancedUserSourceManager
from core.performance_optimizer import performance_optimizer

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'newsfeeds_secret_key_2024'  # In production, use environment variable

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

# Initialize user management system first
user_manager = UserManager(data_dir)
auth_manager = init_auth(user_manager)

# Initialize enhanced systems
admin_settings_manager = AdminSettingsManager(data_dir)
enhanced_user_sources = EnhancedUserSourceManager(data_dir, admin_settings_manager)

# Initialize components with admin settings
admin_settings = admin_settings_manager.get_all_settings()
max_articles_per_source = admin_settings.get('user_limits', {}).get('max_articles_per_source', 5)
news_fetcher = NewsFetcher(news_sources, max_articles_per_source=max_articles_per_source)
data_manager = DataManager(base_path=data_dir)
categorizer = Categorizer()
report_generator = ReportGenerator()

# Initialize LLM summarizer first
try:
    multi_llm_summarizer = MultiLLMSummarizer(config_file='llm_config.json')
    print("✅ LLM Summarizer initialized successfully")
except Exception as e:
    print(f"⚠️ Warning: LLM Summarizer initialization failed: {e}")
    print("   AI summarization will be disabled, using fallback summaries")
    multi_llm_summarizer = None

# Initialize new AI features
try:
    # Phase 1 features - Initialize smart categorizer with LLM support and specified model
    smart_categorizer = SmartCategorizer(llm_summarizer=multi_llm_summarizer, ollama_model=ollama_model)
    sentiment_analyzer = AdvancedSentimentAnalyzer()
    content_recommender = ContentRecommender()
    semantic_search = SemanticSearchEngine()

    # Phase 2 features
    relationship_mapper = ContentRelationshipMapper()
    trend_analyzer = TrendAnalyzer()
    ai_assistant = AINewsAssistant()
    briefing_generator = SmartBriefingGenerator(llm_summarizer=multi_llm_summarizer)

    print("✅ Phase 1 & 2 AI features initialized successfully")
except Exception as e:
    print(f"⚠️ Warning: AI features initialization failed: {e}")
    smart_categorizer = None
    sentiment_analyzer = None
    content_recommender = None
    semantic_search = None
    relationship_mapper = None
    trend_analyzer = None
    ai_assistant = None
    briefing_generator = None

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
    """Main page - redirect to login if not authenticated"""
    current_user = get_current_user()

    if current_user:
        # User is logged in, redirect to appropriate dashboard
        if current_user.is_admin():
            from flask import redirect, url_for
            return redirect(url_for('admin_dashboard'))
        else:
            from flask import redirect, url_for
            return redirect(url_for('user_dashboard'))

    # User not logged in, redirect to login page
    from flask import redirect, url_for
    return redirect(url_for('login'))

@app.route('/app')
@login_required
def main_app():
    """Main news application (requires authentication)"""
    return render_template('index.html')

@app.route('/public')
def public_news():
    """Public news feed (no authentication required) - for demo purposes"""
    return render_template('index.html')

@app.route('/report')
@login_required
def report():
    """Generate and serve HTML report"""
    try:
        # Load current news data
        news_data = data_manager.load_news_data()

        # Generate HTML report
        report_generator.create_html_report(news_data, "news_report.html")

        # Serve the generated HTML file
        return send_from_directory('.', 'news_report.html')
    except Exception as e:
        return f"Error generating report: {str(e)}", 500

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
@login_required
def get_news():
    """API endpoint to get news articles - filtered by user preferences"""
    try:
        current_user = get_current_user()

        # Load all global news articles
        all_articles = data_manager.load_news_data()

        if current_user.is_admin():
            # Admin sees all global news
            articles = all_articles
            user_specific = False
        else:
            # Regular users see filtered news based on their enhanced source preferences
            user_source_prefs = enhanced_user_sources.get_user_source_preferences(current_user.user_id)

            if not user_source_prefs:
                return jsonify({
                    'success': True,
                    'message': 'No news sources selected. Visit your dashboard to select sources.',
                    'news': [],
                    'articles': [],
                    'count': 0,
                    'user_specific': True,
                    'guidance': {
                        'title': 'Get Started with Personalized News',
                        'steps': [
                            '1. Visit your Dashboard',
                            '2. Click "Select Sources" button',
                            '3. Choose up to 3 news sources',
                            '4. Return here to see your personalized feed'
                        ]
                    }
                })

            # Filter articles by user's preferred sources
            articles = []
            for article in all_articles:
                article_source = article.get('source', '').strip()
                # Check if article source matches any of user's preferred sources
                for pref_source in user_source_prefs:
                    if article_source.lower() == pref_source.lower():
                        article['user_filtered'] = True
                        articles.append(article)
                        break

            user_specific = True

        if articles:
            return jsonify({
                'success': True,
                'news': articles,  # Frontend expects 'news'
                'articles': articles,  # Keep for compatibility
                'count': len(articles),
                'user_specific': user_specific,
                'total_available': len(all_articles) if not current_user.is_admin() else len(articles)
            })
        else:
            message = 'No news articles found'
            if not current_user.is_admin():
                message = 'No news articles found from your selected sources. Try selecting different sources in your dashboard.'

            return jsonify({
                'success': True,
                'message': message,
                'news': [],
                'articles': [],
                'count': 0,
                'user_specific': user_specific
            })
    except Exception as e:
        logger.error(f"Error loading news: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to load news articles',
            'news': [],
            'articles': [],
            'count': 0
        })

@app.route('/api/sources')
@login_required
def get_sources():
    """API endpoint to get global news sources with user preferences"""
    try:
        current_user = get_current_user()

        # Get user's source preferences (empty for admin)
        user_source_prefs = []
        if not current_user.is_admin():
            user_source_prefs = enhanced_user_sources.get_user_source_preferences(current_user.user_id)

        # Get global source states (admin enabled/disabled settings)
        global_source_states = enhanced_user_sources.get_global_source_states()

        # Build sources info from global configuration
        sources_info = []
        for source_name, source_config in news_sources.items():
            # Check if this source is globally enabled by admin
            globally_enabled = global_source_states.get(source_name, True)

            # Handle both string URLs and dict configurations
            if isinstance(source_config, str):
                # Simple URL format
                source_info = {
                    'name': source_name,
                    'url': source_config,
                    'type': 'rss',
                    'description': f'RSS feed from {source_name}',
                    'category': 'General',
                    'enabled_globally': globally_enabled,  # Use actual admin setting
                    'user_selected': source_name in user_source_prefs,  # User preference
                    'can_select': not current_user.is_admin()  # Only regular users can select
                }
            else:
                # Dict format with detailed configuration
                source_info = {
                    'name': source_name,
                    'url': source_config.get('url', ''),
                    'type': source_config.get('type', 'rss'),
                    'description': source_config.get('description', f'RSS feed from {source_name}'),
                    'category': source_config.get('category', 'General'),
                    'enabled_globally': globally_enabled,  # Use actual admin setting
                    'user_selected': source_name in user_source_prefs,  # User preference
                    'can_select': not current_user.is_admin()  # Only regular users can select
                }
            sources_info.append(source_info)

        return jsonify({
            'success': True,
            'sources': sources_info,
            'total_sources': len(sources_info),
            'user_selected_count': len(user_source_prefs),
            'max_user_sources': 3,
            'is_admin': current_user.is_admin(),
            'architecture': 'global_fetch_user_filter'
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
@login_required
@admin_required
def toggle_source():
    """API endpoint to enable/disable a global news source (Admin only)"""
    try:
        current_user = get_current_user()
        data = request.get_json()
        source_name = data.get('source_name')
        enabled = data.get('enabled', True)

        if not source_name or source_name not in news_sources:
            return jsonify({
                'success': False,
                'error': 'Invalid source name'
            })

        # For admin: toggle global source availability
        # This affects which sources are available in the global pool for users to select
        result = enhanced_user_sources.toggle_global_source_availability(source_name, enabled)

        if result.get('success'):
            return jsonify({
                'success': True,
                'source_name': source_name,
                'enabled': enabled,
                'message': f'Global source {source_name} {"enabled" if enabled else "disabled"} successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Failed to toggle source')
            })

    except Exception as e:
        logger.error(f"Toggle source error: {e}")
        return jsonify({
            'success': False,
            'error': f'Failed to toggle source: {str(e)}'
        })

@app.route('/api/fetch-news', methods=['POST'])
@login_required
def fetch_news():
    """API endpoint to fetch and summarize news with LLM"""
    global is_processing, processing_status, processing_stats

    if is_processing:
        return jsonify({
            'success': False,
            'message': 'Already processing news'
        })

    # Get current user information before starting background thread
    current_user = get_current_user()

    def process_news_with_llm(user_info):
        global is_processing, processing_status, processing_stats

        try:
            is_processing = True
            processing_status = "🚀 Starting news processing with AI summarization..."

            # Use passed user information instead of get_current_user()
            # current_user = get_current_user()  # This causes the request context error!

            # Get global source states (admin enabled/disabled settings)
            global_source_states = enhanced_user_sources.get_global_source_states()
            globally_enabled_sources = {name for name, enabled in global_source_states.items() if enabled}

            # Debug logging
            logger.info(f"🔍 Debug - Global source states: {global_source_states}")
            logger.info(f"🔍 Debug - Globally enabled sources: {globally_enabled_sources}")
            logger.info(f"🔍 Debug - Available news sources: {list(news_sources.keys())}")

            if user_info.is_admin():
                # Admin fetches from globally enabled sources only
                enabled_sources = globally_enabled_sources
                disabled_count = len(news_sources) - len(enabled_sources)
                if disabled_count > 0:
                    processing_status = f"🔧 Admin fetching from {len(enabled_sources)} enabled sources ({disabled_count} disabled)..."
                else:
                    processing_status = f"🔧 Admin fetching from all {len(enabled_sources)} global sources..."
            else:
                # Regular users fetch from their selected sources (both global and custom)
                user_source_prefs = enhanced_user_sources.get_user_source_preferences(user_info.user_id)

                # Debug logging
                logger.info(f"🔍 Debug - User {user_info.user_id} source preferences: {user_source_prefs}")

                if not user_source_prefs:
                    processing_status = "❌ No sources selected. Please configure sources in dashboard."
                    return

                # Get user's actual sources (includes both global and custom)
                user_sources = enhanced_user_sources.get_user_sources(user_info.user_id)

                # Debug logging
                logger.info(f"🔍 Debug - User sources from enhanced system: {[s.name for s in user_sources]}")

                # Build enabled sources list from user's actual sources
                enabled_sources = set()
                sources_to_fetch = []

                for source_name in user_source_prefs:
                    logger.info(f"🔍 Debug - Processing preference: {source_name}")
                    # Find the source in user's sources (handles both global and custom)
                    found_in_user_sources = False
                    for user_source in user_sources:
                        if user_source.name == source_name and user_source.enabled:
                            logger.info(f"🔍 Debug - Found {source_name} in user sources: {user_source.url}")
                            enabled_sources.add(source_name)
                            sources_to_fetch.append((source_name, user_source.url))
                            found_in_user_sources = True
                            break

                    if not found_in_user_sources:
                        logger.info(f"🔍 Debug - {source_name} not found in user sources, checking global...")
                        # Fallback: check if it's in global sources and globally enabled
                        if source_name in news_sources and source_name in globally_enabled_sources:
                            enabled_sources.add(source_name)
                            source_config = news_sources[source_name]
                            source_url = source_config if isinstance(source_config, str) else source_config.get('url', '')
                            if source_url:
                                sources_to_fetch.append((source_name, source_url))
                                logger.info(f"🔍 Debug - Added {source_name} from global sources: {source_url}")

                # Debug logging
                logger.info(f"🔍 Debug - Final enabled sources for user: {enabled_sources}")
                logger.info(f"🔍 Debug - Sources to fetch: {[name for name, _ in sources_to_fetch]}")

                processing_status = f"👤 User fetching from {len(enabled_sources)} selected sources (including custom sources)..."

                # If no enabled sources, provide helpful message
                if not enabled_sources:
                    processing_status = "❌ No valid sources available for fetching."
                    return

            # For admin, build sources list from global configuration
            if user_info.is_admin():
                sources = [(name, config) for name, config in news_sources.items() if name in enabled_sources]
            else:
                # For users, use the sources_to_fetch list we built above
                sources = sources_to_fetch

            # Debug logging
            logger.info(f"🔍 Debug - Final sources to fetch from: {[name for name, _ in sources]}")

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
            for source_idx, (source_name, source_config) in enumerate(sources, 1):
                try:
                    processing_stats["current_source"] = source_name
                    processing_status = f"📡 Fetching from {source_name} ({source_idx}/{len(sources)})..."

                    # Handle both string URLs and dict configurations
                    if isinstance(source_config, str):
                        source_url = source_config
                    elif isinstance(source_config, dict):
                        source_url = source_config.get('url', '')
                    else:
                        logger.error(f"Invalid source configuration for {source_name}: {source_config}")
                        continue

                    if not source_url:
                        logger.error(f"No URL found for source {source_name}")
                        continue

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
                    
                    # Categorize articles with AI-powered system
                    for item in source_news:
                        # Use AI-powered categorization as primary method
                        if smart_categorizer:
                            try:
                                smart_result = smart_categorizer.categorize_article(item)
                                item['category'] = smart_result.get('primary_category', 'General')
                                item['smart_categorization'] = smart_result
                            except Exception as e:
                                logger.warning(f"AI categorization failed, using fallback: {e}")
                                item['category'] = categorizer.categorize_news(item)
                        else:
                            # Fallback to old categorizer if AI is not available
                            item['category'] = categorizer.categorize_news(item)

                        # Apply sentiment analysis
                        if sentiment_analyzer:
                            try:
                                item['sentiment_analysis'] = sentiment_analyzer.analyze_sentiment(item)
                            except Exception as e:
                                logger.warning(f"Sentiment analysis failed: {e}")
                    
                    # AI Summarization with dynamic performance optimization
                    start_time = time.time()

                    # Get optimized parameters based on current load
                    estimated_articles = len(source_news)
                    total_estimated_articles = sum(len(sources) for sources in [source_news])  # Could be expanded for multi-source estimation
                    perf_params = performance_optimizer.get_processing_parameters(
                        num_sources=len(sources),  # Total sources being processed
                        estimated_articles=total_estimated_articles,
                        user_preference=None  # Could be user configurable
                    )

                    batch_size = perf_params["batch_size"]
                    batch_delay = perf_params["batch_delay"]
                    max_text_length = perf_params["max_text_length"]
                    max_retries = perf_params["max_retries"]

                    logger.info(f"🚀 Using {perf_params['profile_name']} profile: batch_size={batch_size}, delay={batch_delay}s")

                    source_summarized = []

                    for batch_start in range(0, len(source_news), batch_size):
                        batch_end = min(batch_start + batch_size, len(source_news))
                        batch = source_news[batch_start:batch_end]
                        current_batch = batch_start // batch_size + 1
                        total_batches = (len(source_news) + batch_size - 1) // batch_size

                        processing_stats["current_batch"] = current_batch
                        processing_status = f"🤖 AI processing batch {current_batch}/{total_batches} from {source_name} ({perf_params['profile_name']} mode)..."

                        # Summarize batch with AI using optimized parameters
                        try:
                            if multi_llm_summarizer is not None:
                                batch_summarized = multi_llm_summarizer.summarize_news_items(
                                    batch,
                                    model=ollama_model,
                                    max_text_length=max_text_length,
                                    batch_delay=batch_delay,
                                    max_retries=max_retries
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

                    # Update performance statistics
                    source_processing_time = time.time() - start_time
                    performance_optimizer.update_performance_stats(source_processing_time, len(source_summarized))

                    processing_status = f"✅ Completed {source_name}: {len(source_summarized)} articles with AI summaries ({source_processing_time:.1f}s)"
                    
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
    
    # Start background processing with user info
    thread = threading.Thread(target=process_news_with_llm, args=(current_user,))
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

@app.route('/api/config', methods=['GET'])
def get_config():
    """API endpoint to get configuration"""
    # Always load fresh config to ensure latest values
    current_config = load_config()
    return jsonify(current_config)

@app.route('/api/config', methods=['POST'])
def save_config():
    """API endpoint to save configuration"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'No configuration data provided'
            }), 400

        # Load current config
        current_config = load_config()

        # Merge news_sources properly to avoid overwriting existing sources
        if 'news_sources' in data:
            current_sources = current_config.get('news_sources', {})
            new_sources = data['news_sources']
            current_sources.update(new_sources)
            data['news_sources'] = current_sources

        # Update with new data
        current_config.update(data)

        # Save to file
        with open('config.json', 'w', encoding='utf-8') as f:
            json.dump(current_config, f, indent=4, ensure_ascii=False)

        # Reload global config variables
        global config, news_sources, ollama_model, llm_providers_config
        config = load_config()
        news_sources = config.get('news_sources', {})
        ollama_model = config.get('ollama_model', 'qwen3:8b')
        llm_providers_config = config.get('llm_providers', {})

        return jsonify({
            'success': True,
            'message': 'Configuration saved successfully'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error saving configuration: {str(e)}'
        }), 500

@app.route('/api/saved-searches')
def get_saved_searches():
    """API endpoint for saved searches"""
    return jsonify([])

@app.route('/api/trending-analysis')
@login_required
def get_trending_analysis():
    """API endpoint for trending analysis with real data - filtered by user's sources"""
    try:
        current_user = get_current_user()

        # Load all news data
        all_articles = data_manager.load_news_data()

        if not all_articles:
            return jsonify({
                'success': False,
                'error': 'No news data available'
            })

        # Filter articles by user's selected sources
        if current_user.is_admin():
            # Admin sees trending analysis from all sources
            articles = all_articles
        else:
            # Regular users see trending analysis only from their selected sources
            user_source_prefs = enhanced_user_sources.get_user_source_preferences(current_user.user_id)

            if not user_source_prefs:
                return jsonify({
                    'success': True,
                    'trending_topics': [],
                    'trending_keywords': [],
                    'source_distribution': {},
                    'message': 'No sources selected. Visit your dashboard to select sources.',
                    'user_specific': True
                })

            # Filter articles by user's preferred sources
            articles = []
            for article in all_articles:
                article_source = article.get('source', '').strip()
                for pref_source in user_source_prefs:
                    if article_source.lower() == pref_source.lower():
                        articles.append(article)
                        break

            if not articles:
                return jsonify({
                    'success': True,
                    'trending_topics': [],
                    'trending_keywords': [],
                    'source_distribution': {},
                    'message': f'No articles found from your selected sources: {", ".join(user_source_prefs)}',
                    'user_specific': True
                })

        # Use content enhancer for trending analysis if available
        if 'content_enhancer' in globals():
            trending_analysis = content_enhancer.get_trending_analysis(articles)
        else:
            # Enhanced trending analysis with stop word filtering
            from collections import Counter
            import re

            # Comprehensive stop words list to filter out meaningless terms
            stop_words = {
                # Common articles, pronouns, conjunctions
                'that', 'this', 'with', 'from', 'they', 'their', 'there', 'where', 'when',
                'what', 'which', 'will', 'would', 'could', 'should', 'have', 'been',
                'were', 'said', 'says', 'also', 'more', 'most', 'some', 'many', 'much',

                # Prepositions and conjunctions
                'about', 'after', 'before', 'during', 'through', 'between', 'among',
                'into', 'onto', 'upon', 'over', 'under', 'above', 'below', 'across',
                'around', 'behind', 'beside', 'beyond', 'inside', 'outside', 'within',
                'including', 'without', 'against', 'towards', 'regarding', 'concerning',

                # Common verbs and adverbs
                'does', 'done', 'doing', 'make', 'made', 'making', 'take', 'taken', 'taking',
                'give', 'given', 'giving', 'come', 'came', 'coming', 'goes', 'went', 'going',
                'know', 'knew', 'known', 'knowing', 'think', 'thought', 'thinking',
                'look', 'looked', 'looking', 'find', 'found', 'finding', 'work', 'worked', 'working',
                'help', 'helped', 'helping', 'keep', 'kept', 'keeping', 'turn', 'turned', 'turning',
                'show', 'showed', 'showing', 'play', 'played', 'playing', 'move', 'moved', 'moving',
                'follow', 'followed', 'following', 'live', 'lived', 'living', 'believe', 'believed', 'believing',
                'hold', 'held', 'holding', 'bring', 'brought', 'bringing', 'happen', 'happened', 'happening',
                'write', 'wrote', 'written', 'writing', 'provide', 'provided', 'providing',
                'allow', 'allowed', 'allowing', 'include', 'included', 'including',

                # Common adjectives and determiners
                'such', 'each', 'every', 'both', 'either', 'neither', 'another', 'other', 'others',
                'same', 'different', 'various', 'several', 'certain', 'particular', 'specific',
                'general', 'special', 'important', 'large', 'small', 'great', 'good', 'better', 'best',
                'high', 'higher', 'highest', 'long', 'longer', 'longest', 'right', 'wrong',

                # Time and quantity words
                'time', 'times', 'year', 'years', 'month', 'months', 'week', 'weeks', 'day', 'days',
                'hour', 'hours', 'minute', 'minutes', 'today', 'yesterday', 'tomorrow',
                'first', 'second', 'third', 'last', 'next', 'previous', 'current', 'recent',
                'number', 'numbers', 'part', 'parts', 'place', 'places', 'way', 'ways',

                # Generic business/news terms that are too common
                'according', 'report', 'reports', 'reported', 'reporting', 'article', 'articles',
                'story', 'stories', 'information', 'details', 'sources', 'source',
                'statement', 'statements', 'announcement', 'announcements'
            }

            # Extract keywords from titles and summaries
            all_text = []
            for article in articles:
                text = f"{article.get('title', '')} {article.get('summary', '')}"
                # Extract meaningful words (4+ characters, not stop words)
                words = re.findall(r'\b[A-Za-z]{4,}\b', text.lower())
                # Filter out stop words and additional patterns
                meaningful_words = []
                important_ing_words = {'business', 'marketing', 'trading', 'banking', 'programming', 'engineering'}

                for word in words:
                    if (word not in stop_words and
                        len(word) >= 4 and
                        word.isalpha() and  # Only alphabetic characters
                        not word.startswith('http') and
                        (not word.endswith('ing') or word in important_ing_words) and  # Filter -ing except important ones
                        not word.endswith('ed')):  # Filter past tense verbs
                        meaningful_words.append(word)
                all_text.extend(meaningful_words)

            # Count word frequencies
            word_counts = Counter(all_text)

            # Create trending topics with better filtering
            trending_topics = []
            for word, count in word_counts.most_common(20):
                if count >= 3:  # Must appear at least 3 times for significance
                    trending_topics.append({
                        'keyword': word.title(),
                        'count': count,
                        'trend_score': count / len(articles),
                        'article_count': count
                    })

            # Calculate trending sources based on article counts
            source_counts = Counter()
            for article in articles:
                source = article.get('source', 'Unknown')
                source_counts[source] += 1

            trending_sources = []
            for source, count in source_counts.most_common(8):  # Top 8 sources
                if count >= 1:  # At least 1 article
                    trending_sources.append({
                        'name': source,
                        'article_count': count,
                        'percentage': (count / len(articles)) * 100,
                        'status': 'active'
                    })

            # Basic sentiment overview
            sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
            for article in articles:
                sentiment = article.get('sentiment', 'neutral')
                if sentiment in sentiment_counts:
                    sentiment_counts[sentiment] += 1

            trending_analysis = {
                'trending_topics': trending_topics,
                'trending_sources': trending_sources,
                'sentiment_trends': sentiment_counts
            }

        return jsonify({
            'success': True,
            'trending_analysis': trending_analysis
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/content-insights')
@login_required
def get_content_insights():
    """API endpoint for content insights with comprehensive analysis - filtered by user's sources"""
    try:
        current_user = get_current_user()

        # Load all news data
        all_articles = data_manager.load_news_data()

        if not all_articles:
            return jsonify({
                'success': False,
                'error': 'No news data available'
            })

        # Filter articles by user's selected sources
        if current_user.is_admin():
            # Admin sees insights from all sources
            articles = all_articles
        else:
            # Regular users see insights only from their selected sources
            user_source_prefs = enhanced_user_sources.get_user_source_preferences(current_user.user_id)

            if not user_source_prefs:
                return jsonify({
                    'success': True,
                    'total_articles': 0,
                    'sentiment_distribution': {'positive': 0, 'negative': 0, 'neutral': 0},
                    'quality_metrics': {'average_score': 0, 'high_quality_count': 0},
                    'reading_metrics': {'average_time': 0, 'total_time': 0},
                    'category_distribution': {},
                    'source_performance': {},
                    'message': 'No sources selected. Visit your dashboard to select sources.',
                    'user_specific': True
                })

            # Filter articles by user's preferred sources
            articles = []
            for article in all_articles:
                article_source = article.get('source', '').strip()
                for pref_source in user_source_prefs:
                    if article_source.lower() == pref_source.lower():
                        articles.append(article)
                        break

            if not articles:
                return jsonify({
                    'success': True,
                    'total_articles': 0,
                    'sentiment_distribution': {'positive': 0, 'negative': 0, 'neutral': 0},
                    'quality_metrics': {'average_score': 0, 'high_quality_count': 0},
                    'reading_metrics': {'average_time': 0, 'total_time': 0},
                    'category_distribution': {},
                    'source_performance': {},
                    'message': f'No articles found from your selected sources: {", ".join(user_source_prefs)}',
                    'user_specific': True
                })

        # Calculate insights
        total_articles = len(articles)

        # Sentiment distribution
        sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
        quality_scores = []
        reading_times = []
        sources = set()
        categories = set()

        for article in articles:
            # Get sentiment from advanced sentiment analysis if available
            if article.get('sentiment_analysis', {}).get('overall_sentiment'):
                sentiment = article['sentiment_analysis']['overall_sentiment']
            else:
                sentiment = article.get('sentiment', 'neutral')

            if sentiment in sentiment_counts:
                sentiment_counts[sentiment] += 1

            # Content quality score
            if 'content_quality_score' in article:
                quality_scores.append(article['content_quality_score'])
            else:
                # Calculate basic quality score
                score = 0.5
                if article.get('title') and len(article['title']) > 20:
                    score += 0.2
                if article.get('summary') and len(article['summary']) > 50:
                    score += 0.2
                if article.get('link'):
                    score += 0.1
                quality_scores.append(min(1.0, score))

            # Reading time estimation
            if 'estimated_reading_time' in article:
                reading_times.append(article['estimated_reading_time'])
            else:
                # Estimate reading time (200 words per minute)
                content_length = len(article.get('summary', '') + article.get('full_text', ''))
                reading_time = max(1, content_length // 1000)
                reading_times.append(reading_time)

            # Sources and categories
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
            'success': True,
            'insights': insights
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
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
@login_required
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

@app.route('/api/ai-features/smart-categorization', methods=['POST'])
@login_required
def smart_categorize_article():
    """API endpoint for smart categorization of a single article"""
    try:
        if not smart_categorizer:
            return jsonify({
                'success': False,
                'error': 'Smart categorizer not available'
            })

        data = request.get_json()
        if not data or 'article' not in data:
            return jsonify({
                'success': False,
                'error': 'Article data required'
            })

        article = data['article']
        categorization = smart_categorizer.categorize_article(article)

        return jsonify({
            'success': True,
            'categorization': categorization
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Smart categorization failed: {str(e)}'
        })

@app.route('/api/ai-features/sentiment-analysis', methods=['POST'])
@login_required
def analyze_article_sentiment():
    """API endpoint for sentiment analysis of a single article"""
    try:
        if not sentiment_analyzer:
            return jsonify({
                'success': False,
                'error': 'Sentiment analyzer not available'
            })

        data = request.get_json()
        if not data or 'article' not in data:
            return jsonify({
                'success': False,
                'error': 'Article data required'
            })

        article = data['article']
        sentiment = sentiment_analyzer.analyze_sentiment(article)

        return jsonify({
            'success': True,
            'sentiment': sentiment
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Sentiment analysis failed: {str(e)}'
        })

@app.route('/api/ai-features/recommendations')
@login_required
def get_content_recommendations():
    """API endpoint for content recommendations"""
    try:
        if not content_recommender:
            return jsonify({
                'success': False,
                'error': 'Content recommender not available'
            })

        current_user = get_current_user()
        user_id = request.args.get('user_id', current_user.user_id)
        limit = int(request.args.get('limit', 10))

        # Load all articles
        all_articles = data_manager.load_news_data()
        if not all_articles:
            return jsonify({
                'success': True,
                'recommendations': [],
                'message': 'No articles available for recommendations'
            })

        # Filter articles by user's selected sources
        if current_user.is_admin():
            articles = all_articles
        else:
            user_source_prefs = enhanced_user_sources.get_user_source_preferences(current_user.user_id)

            if not user_source_prefs:
                return jsonify({
                    'success': True,
                    'recommendations': [],
                    'message': 'No sources selected. Visit your dashboard to select sources.',
                    'user_specific': True
                })

            # Filter articles by user's preferred sources
            articles = []
            for article in all_articles:
                article_source = article.get('source', '').strip()
                for pref_source in user_source_prefs:
                    if article_source.lower() == pref_source.lower():
                        articles.append(article)
                        break

            if not articles:
                return jsonify({
                    'success': True,
                    'recommendations': [],
                    'message': f'No articles found from your selected sources: {", ".join(user_source_prefs)}',
                    'user_specific': True
                })

        # Add IDs to articles if not present
        for i, article in enumerate(articles):
            if 'id' not in article:
                article['id'] = f"article_{i}"

        recommendations = content_recommender.get_recommendations(user_id, articles)

        return jsonify({
            'success': True,
            'recommendations': recommendations[:limit],
            'user_id': user_id
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Content recommendations failed: {str(e)}'
        })

@app.route('/api/ai-features/semantic-search', methods=['POST'])
@login_required
def semantic_search_articles():
    """API endpoint for semantic search"""
    try:
        if not semantic_search:
            return jsonify({
                'success': False,
                'error': 'Semantic search not available'
            })

        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({
                'success': False,
                'error': 'Search query required'
            })

        query = data['query']
        filters = data.get('filters', {})

        # Load articles
        articles = data_manager.load_news_data()
        if not articles:
            return jsonify({
                'success': True,
                'results': [],
                'message': 'No articles available to search'
            })

        # Add IDs to articles if not present
        for i, article in enumerate(articles):
            if 'id' not in article:
                article['id'] = f"article_{i}"

        results = semantic_search.search(query, articles, filters)

        return jsonify({
            'success': True,
            'results': results,
            'query': query,
            'total_results': len(results)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Semantic search failed: {str(e)}'
        })

@app.route('/api/ai-features/search-suggestions')
@login_required
def get_search_suggestions():
    """API endpoint for search suggestions"""
    try:
        if not semantic_search:
            return jsonify({
                'success': False,
                'error': 'Semantic search not available'
            })

        query = request.args.get('q', '')
        limit = int(request.args.get('limit', 5))

        if not query:
            return jsonify({
                'success': True,
                'suggestions': []
            })

        suggestions = semantic_search.get_search_suggestions(query, limit)

        return jsonify({
            'success': True,
            'suggestions': suggestions,
            'query': query
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Search suggestions failed: {str(e)}'
        })

@app.route('/api/ai-features/status')
@login_required
def get_ai_features_status():
    """API endpoint for AI features status"""
    try:
        status = {
            # Phase 1 features
            'smart_categorizer': smart_categorizer is not None,
            'sentiment_analyzer': sentiment_analyzer is not None,
            'content_recommender': content_recommender is not None,
            'semantic_search': semantic_search is not None,
            # Phase 2 features
            'relationship_mapper': relationship_mapper is not None,
            'trend_analyzer': trend_analyzer is not None,
            'ai_assistant': ai_assistant is not None,
            'briefing_generator': briefing_generator is not None,
            'timestamp': datetime.now().isoformat()
        }

        phase1_features = ['smart_categorizer', 'sentiment_analyzer', 'content_recommender', 'semantic_search']
        phase2_features = ['relationship_mapper', 'trend_analyzer', 'ai_assistant', 'briefing_generator']

        return jsonify({
            'success': True,
            'ai_features_status': status,
            'available_features': [k for k, v in status.items() if v and k != 'timestamp'],
            'phase1_features': [f for f in phase1_features if status.get(f, False)],
            'phase2_features': [f for f in phase2_features if status.get(f, False)]
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'AI features status check failed: {str(e)}'
        })

# Phase 2 AI Features API Endpoints

@app.route('/api/ai-features/relationship-analysis', methods=['POST'])
@login_required
def analyze_content_relationships():
    """API endpoint for content relationship analysis"""
    try:
        if not relationship_mapper:
            return jsonify({
                'success': False,
                'error': 'Content relationship mapper not available'
            })

        # Load articles
        articles = data_manager.load_news_data()
        if not articles:
            return jsonify({
                'success': True,
                'relationships': {},
                'message': 'No articles available for analysis'
            })

        # Add IDs to articles if not present
        for i, article in enumerate(articles):
            if 'id' not in article:
                article['id'] = f"article_{i}"

        relationships = relationship_mapper.analyze_relationships(articles)

        return jsonify({
            'success': True,
            'relationships': relationships,
            'articles_analyzed': len(articles)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Relationship analysis failed: {str(e)}'
        })

@app.route('/api/ai-features/trend-analysis', methods=['POST'])
@login_required
def analyze_trends():
    """API endpoint for trend analysis"""
    try:
        if not trend_analyzer:
            return jsonify({
                'success': False,
                'error': 'Trend analyzer not available'
            })

        data = request.get_json() or {}
        include_historical = data.get('include_historical', False)

        # Load current articles
        articles = data_manager.load_news_data()
        if not articles:
            return jsonify({
                'success': True,
                'trends': {},
                'message': 'No articles available for trend analysis'
            })

        # Load historical data if requested
        historical_data = None
        if include_historical:
            # In a real implementation, load historical articles
            historical_data = []

        trends = trend_analyzer.analyze_trends(articles, historical_data)

        return jsonify({
            'success': True,
            'trends': trends,
            'articles_analyzed': len(articles)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Trend analysis failed: {str(e)}'
        })

@app.route('/api/ai-features/ai-chat', methods=['POST'])
@login_required
def ai_chat():
    """API endpoint for AI assistant chat using real LLM"""
    try:
        if not multi_llm_summarizer:
            return jsonify({
                'success': False,
                'error': 'LLM service not available'
            })

        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({
                'success': False,
                'error': 'Message required'
            })

        user_message = data['message']
        conversation_context = data.get('context', {})

        # Build context for the LLM
        context_parts = []

        # Add conversation history
        if conversation_context.get('conversation_history'):
            context_parts.append("Previous conversation:")
            for msg in conversation_context['conversation_history'][-6:]:  # Last 6 messages
                role = msg.get('role', 'user')
                content = msg.get('content', '')
                context_parts.append(f"{role.title()}: {content}")
            context_parts.append("")

        # Add recent articles context
        if conversation_context.get('recent_articles'):
            context_parts.append("Recent news articles for context:")
            for article in conversation_context['recent_articles'][:3]:  # Top 3 articles
                title = article.get('title', 'Unknown')
                summary = article.get('summary', '')[:200] + '...' if article.get('summary') else ''
                source = article.get('source', 'Unknown')
                context_parts.append(f"- {title} ({source}): {summary}")
            context_parts.append("")

        # Build the full prompt
        system_prompt = """You are an intelligent news assistant. You help users understand and discuss current events.
        Provide informative, accurate, and engaging responses about news topics.
        Keep responses conversational but informative. If you reference specific articles, mention the source."""

        context_text = "\n".join(context_parts)
        full_prompt = f"{system_prompt}\n\n{context_text}\nUser: {user_message}\n\nAssistant:"

        # Use the LLM to generate response
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            llm_response = loop.run_until_complete(
                multi_llm_summarizer.summarize_text(
                    text=full_prompt,
                    max_tokens=500,
                    temperature=0.7
                )
            )

            if llm_response.success:
                # Generate follow-up suggestions based on the response
                follow_up_suggestions = generate_chat_follow_ups(user_message, llm_response.content)

                response = {
                    'message': llm_response.content,
                    'follow_up_suggestions': follow_up_suggestions,
                    'provider': llm_response.provider,
                    'model': llm_response.model,
                    'tokens_used': llm_response.tokens_used,
                    'cost': llm_response.cost
                }
            else:
                response = {
                    'message': "I'm having trouble processing your request right now. Please try again.",
                    'follow_up_suggestions': [],
                    'error': llm_response.error
                }

        finally:
            loop.close()

        return jsonify({
            'success': True,
            'response': response
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'AI chat failed: {str(e)}'
        })

def generate_chat_follow_ups(user_message, ai_response):
    """Generate follow-up suggestions based on the conversation"""
    follow_ups = []

    # Basic follow-up patterns based on message content
    message_lower = user_message.lower()

    if any(word in message_lower for word in ['policy', 'government', 'cabinet']):
        follow_ups.extend([
            "What are the potential impacts of this policy?",
            "How does this compare to previous policies?",
            "What do experts think about this decision?"
        ])
    elif any(word in message_lower for word in ['economy', 'market', 'business']):
        follow_ups.extend([
            "How might this affect the stock market?",
            "What are the economic implications?",
            "Which sectors could be most impacted?"
        ])
    elif any(word in message_lower for word in ['technology', 'ai', 'innovation']):
        follow_ups.extend([
            "What are the latest trends in this technology?",
            "How might this change the industry?",
            "What are the potential risks and benefits?"
        ])
    else:
        follow_ups.extend([
            "Can you explain this in more detail?",
            "What are the key takeaways?",
            "How does this relate to recent events?"
        ])

    return follow_ups[:3]  # Return top 3 suggestions

@app.route('/api/ai-features/explain-article', methods=['POST'])
@login_required
def explain_article():
    """API endpoint for article explanation"""
    try:
        if not ai_assistant:
            return jsonify({
                'success': False,
                'error': 'AI assistant not available'
            })

        data = request.get_json()
        if not data or 'article' not in data:
            return jsonify({
                'success': False,
                'error': 'Article data required'
            })

        article = data['article']
        detail_level = data.get('detail_level', 'medium')

        explanation = ai_assistant.explain_article(article, detail_level)

        return jsonify({
            'success': True,
            'explanation': explanation
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Article explanation failed: {str(e)}'
        })

@app.route('/api/ai-features/daily-briefing')
@login_required
def generate_daily_briefing():
    """API endpoint for daily briefing generation"""
    try:
        if not briefing_generator:
            return jsonify({
                'success': False,
                'error': 'Briefing generator not available'
            })

        current_user = get_current_user()
        user_preferences = request.args.get('preferences', '{}')
        try:
            user_preferences = json.loads(user_preferences) if user_preferences != '{}' else None
        except:
            user_preferences = None

        # Load all articles
        all_articles = data_manager.load_news_data()
        if not all_articles:
            return jsonify({
                'success': True,
                'briefing': {'content': 'No articles available for briefing'},
                'message': 'No articles available'
            })

        # Filter articles by user's selected sources
        if current_user.is_admin():
            articles = all_articles
        else:
            user_source_prefs = enhanced_user_sources.get_user_source_preferences(current_user.user_id)

            if not user_source_prefs:
                return jsonify({
                    'success': True,
                    'briefing': {'content': 'No sources selected. Please visit your dashboard to select news sources for your personalized daily briefing.'},
                    'message': 'No sources selected',
                    'user_specific': True
                })

            # Filter articles by user's preferred sources
            articles = []
            for article in all_articles:
                article_source = article.get('source', '').strip()
                for pref_source in user_source_prefs:
                    if article_source.lower() == pref_source.lower():
                        articles.append(article)
                        break

            if not articles:
                return jsonify({
                    'success': True,
                    'briefing': {'content': f'No recent articles found from your selected sources: {", ".join(user_source_prefs)}. Please check back later or add more sources.'},
                    'message': 'No articles from selected sources',
                    'user_specific': True
                })

        briefing = briefing_generator.generate_daily_briefing(articles, user_preferences)

        return jsonify({
            'success': True,
            'briefing': briefing
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Daily briefing generation failed: {str(e)}'
        })

@app.route('/api/ai-features/topic-deep-dive')
@login_required
def generate_topic_deep_dive():
    """API endpoint for topic deep dive analysis"""
    try:
        if not briefing_generator:
            return jsonify({
                'success': False,
                'error': 'Briefing generator not available'
            })

        topic = request.args.get('topic')
        if not topic:
            return jsonify({
                'success': False,
                'error': 'Topic parameter required'
            })

        # Load articles
        articles = data_manager.load_news_data()
        if not articles:
            return jsonify({
                'success': True,
                'deep_dive': {'analysis': 'No articles available for analysis'},
                'message': 'No articles available'
            })

        deep_dive = briefing_generator.generate_topic_deep_dive(topic, articles)

        return jsonify({
            'success': True,
            'deep_dive': deep_dive
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Topic deep dive failed: {str(e)}'
        })

# ============================================================================
# AUTHENTICATION ROUTES
# ============================================================================

@app.route('/login')
def login():
    """Login page"""
    return render_template('auth/login.html')

@app.route('/register')
def register():
    """Registration page"""
    return render_template('auth/register.html')

@app.route('/api/auth/login', methods=['POST'])
def api_login():
    """User login API"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({'success': False, 'error': 'Username and password required'})

        result = auth_manager.login(username, password)

        if result['success']:
            # Store session token in Flask session
            from flask import session
            session['session_token'] = result['session_token']
            session['user_id'] = result['user']['user_id']
            session['username'] = result['user']['username']
            session['role'] = result['user']['role']

        return jsonify(result)

    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'success': False, 'error': 'Login failed'})

@app.route('/api/auth/register', methods=['POST'])
def api_register():
    """User registration API"""
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if not username or not email or not password:
            return jsonify({'success': False, 'error': 'All fields are required'})

        result = auth_manager.register(username, email, password)
        return jsonify(result)

    except Exception as e:
        logger.error(f"Registration error: {e}")
        return jsonify({'success': False, 'error': 'Registration failed'})

@app.route('/api/auth/logout', methods=['GET', 'POST'])
def api_logout():
    """User logout API"""
    try:
        from flask import session, redirect, url_for

        # Get session token
        session_token = session.get('session_token')

        if session_token:
            auth_manager.logout(session_token)

        # Clear Flask session
        session.clear()

        # Redirect to login page
        return redirect(url_for('login'))

    except Exception as e:
        logger.error(f"Logout error: {e}")
        return jsonify({'success': False, 'error': 'Logout failed'})

# ============================================================================
# ADMIN DASHBOARD ROUTES
# ============================================================================

@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    """Admin dashboard"""
    return render_template('admin/dashboard.html')

@app.route('/admin/settings')
@login_required
@admin_required
def admin_settings_page():
    """Admin settings page"""
    return render_template('admin/settings.html')

@app.route('/api/admin/stats')
@login_required
@admin_required
def admin_stats():
    """Get admin statistics"""
    try:
        stats = user_manager.get_user_stats()
        return jsonify({'success': True, 'stats': stats})
    except Exception as e:
        logger.error(f"Admin stats error: {e}")
        return jsonify({'success': False, 'error': 'Failed to load statistics'})

@app.route('/api/admin/users')
@admin_required
def admin_users():
    """Get all users for admin"""
    try:
        users = user_manager.get_all_users()
        users_data = [user.to_dict() for user in users]
        # Remove password hashes from response
        for user_data in users_data:
            user_data.pop('password_hash', None)

        return jsonify({'success': True, 'users': users_data})
    except Exception as e:
        logger.error(f"Admin users error: {e}")
        return jsonify({'success': False, 'error': 'Failed to load users'})

@app.route('/api/admin/pending-users')
@admin_required
def admin_pending_users():
    """Get pending users for admin approval"""
    try:
        users = user_manager.get_pending_users()
        users_data = [user.to_dict() for user in users]
        # Remove password hashes from response
        for user_data in users_data:
            user_data.pop('password_hash', None)

        return jsonify({'success': True, 'users': users_data})
    except Exception as e:
        logger.error(f"Admin pending users error: {e}")
        return jsonify({'success': False, 'error': 'Failed to load pending users'})

@app.route('/api/admin/users/<user_id>/approve', methods=['POST'])
@admin_required
def admin_approve_user(user_id):
    """Approve a pending user"""
    try:
        current_user = get_current_user()
        result = user_manager.approve_user(user_id, current_user.user_id)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Admin approve user error: {e}")
        return jsonify({'success': False, 'error': 'Failed to approve user'})

@app.route('/api/admin/users/<user_id>/reject', methods=['POST'])
@admin_required
def admin_reject_user(user_id):
    """Reject a pending user"""
    try:
        current_user = get_current_user()
        result = user_manager.reject_user(user_id, current_user.user_id)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Admin reject user error: {e}")
        return jsonify({'success': False, 'error': 'Failed to reject user'})

@app.route('/api/admin/users/<user_id>/activate', methods=['POST'])
@admin_required
def admin_activate_user(user_id):
    """Activate a user"""
    try:
        current_user = get_current_user()
        result = user_manager.activate_user(user_id, current_user.user_id)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Admin activate user error: {e}")
        return jsonify({'success': False, 'error': 'Failed to activate user'})

@app.route('/api/admin/users/<user_id>/deactivate', methods=['POST'])
@admin_required
def admin_deactivate_user(user_id):
    """Deactivate a user"""
    try:
        current_user = get_current_user()
        result = user_manager.deactivate_user(user_id, current_user.user_id)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Admin deactivate user error: {e}")
        return jsonify({'success': False, 'error': 'Failed to deactivate user'})

@app.route('/api/admin/users/<user_id>', methods=['DELETE'])
@admin_required
def admin_delete_user(user_id):
    """Delete a user"""
    try:
        current_user = get_current_user()
        result = user_manager.delete_user(user_id, current_user.user_id)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Admin delete user error: {e}")
        return jsonify({'success': False, 'error': 'Failed to delete user'})

@app.route('/api/admin/audit-log')
@admin_required
def admin_audit_log():
    """Get audit log"""
    try:
        logs = user_manager.get_audit_log(limit=100)
        return jsonify({'success': True, 'logs': logs})
    except Exception as e:
        logger.error(f"Admin audit log error: {e}")
        return jsonify({'success': False, 'error': 'Failed to load audit log'})

@app.route('/api/admin/recent-activity')
@login_required
@admin_required
def admin_recent_activity():
    """Get recent activity for dashboard"""
    try:
        logs = user_manager.get_audit_log(limit=10)
        return jsonify({'success': True, 'activities': logs})
    except Exception as e:
        logger.error(f"Admin recent activity error: {e}")
        return jsonify({'success': False, 'error': 'Failed to load recent activity'})

# ============================================================================
# ADMIN SETTINGS ROUTES
# ============================================================================

@app.route('/api/admin/settings')
@login_required
@admin_required
def admin_get_settings():
    """Get all admin settings"""
    try:
        settings = admin_settings_manager.get_all_settings()
        return jsonify({'success': True, 'settings': settings})
    except Exception as e:
        logger.error(f"Admin get settings error: {e}")
        return jsonify({'success': False, 'error': 'Failed to load settings'})

@app.route('/api/admin/settings/user-limits', methods=['PUT'])
@admin_required
def admin_update_user_limits():
    """Update user limits"""
    try:
        data = request.get_json()
        result = admin_settings_manager.update_user_limits(**data)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Admin update user limits error: {e}")
        return jsonify({'success': False, 'error': 'Failed to update user limits'})

@app.route('/api/admin/settings/system', methods=['PUT'])
@admin_required
def admin_update_system_settings():
    """Update system settings"""
    try:
        data = request.get_json()
        result = admin_settings_manager.update_system_settings(**data)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Admin update system settings error: {e}")
        return jsonify({'success': False, 'error': 'Failed to update system settings'})

@app.route('/api/admin/settings/reset', methods=['POST'])
@admin_required
def admin_reset_settings():
    """Reset all settings to defaults"""
    try:
        result = admin_settings_manager.reset_to_defaults()
        return jsonify(result)
    except Exception as e:
        logger.error(f"Admin reset settings error: {e}")
        return jsonify({'success': False, 'error': 'Failed to reset settings'})

@app.route('/api/admin/custom-sources/pending')
@login_required
@admin_required
def admin_pending_custom_sources():
    """Get custom sources pending approval"""
    try:
        pending_sources = enhanced_user_sources.get_pending_custom_sources()
        sources_data = [source.to_dict() for source in pending_sources]
        return jsonify({'success': True, 'pending_sources': sources_data})
    except Exception as e:
        logger.error(f"Admin pending custom sources error: {e}")
        return jsonify({'success': False, 'error': 'Failed to load pending sources'})

@app.route('/api/admin/custom-sources/<source_id>/approve', methods=['POST'])
@admin_required
def admin_approve_custom_source(source_id):
    """Approve a custom source"""
    try:
        current_user = get_current_user()
        data = request.get_json() or {}
        tags = data.get('tags', [])

        result = enhanced_user_sources.approve_custom_source(source_id, current_user.user_id, tags)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Admin approve custom source error: {e}")
        return jsonify({'success': False, 'error': 'Failed to approve custom source'})

@app.route('/api/admin/custom-sources/<source_id>/reject', methods=['POST'])
@admin_required
def admin_reject_custom_source(source_id):
    """Reject a custom source with reason"""
    try:
        current_user = get_current_user()
        data = request.get_json()

        if not data or not data.get('reason'):
            return jsonify({'success': False, 'error': 'Rejection reason is required'})

        reason = data.get('reason')
        result = enhanced_user_sources.reject_custom_source(source_id, current_user.user_id, reason)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Admin reject custom source error: {e}")
        return jsonify({'success': False, 'error': 'Failed to reject custom source'})

@app.route('/api/admin/sources/<source_name>', methods=['DELETE'])
@admin_required
def admin_delete_source(source_name):
    """Admin endpoint to delete a source from both global config and enhanced user sources"""
    try:
        current_user = get_current_user()

        # Step 1: Remove from global config.json
        config = load_config()
        news_sources = config.get("news_sources", {})

        source_existed_in_global = source_name in news_sources
        if source_existed_in_global:
            del news_sources[source_name]
            config["news_sources"] = news_sources
            with open('config.json', 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            reload_config()

        # Step 2: Remove from enhanced user sources system
        # Get all users who have this source
        removed_from_users = []

        for user_id, user_source_list in enhanced_user_sources.user_sources.items():
            for user_source in user_source_list:
                if user_source.name == source_name:
                    # Remove this source from the user
                    result = enhanced_user_sources.remove_user_source(user_id, user_source.source_id)
                    if result.get('success'):
                        removed_from_users.append(user_id)

        # Step 3: Remove from legacy user_sources.json if exists
        user_sources_file = os.path.join(data_dir, 'user_sources.json')
        if os.path.exists(user_sources_file):
            try:
                with open(user_sources_file, 'r', encoding='utf-8') as f:
                    user_prefs = json.load(f)

                enabled_sources = set(user_prefs.get('enabled_sources', []))
                enabled_sources.discard(source_name)

                user_prefs['enabled_sources'] = list(enabled_sources)
                with open(user_sources_file, 'w', encoding='utf-8') as f:
                    json.dump(user_prefs, f, indent=2, ensure_ascii=False)
            except Exception as e:
                logger.warning(f"Failed to update legacy user_sources.json: {e}")

        # Step 4: Update global source states
        try:
            enhanced_user_sources.set_global_source_state(source_name, False)
        except Exception as e:
            logger.warning(f"Failed to update global source state: {e}")

        return jsonify({
            'success': True,
            'message': f'Source "{source_name}" deleted successfully',
            'details': {
                'removed_from_global_config': source_existed_in_global,
                'removed_from_users': removed_from_users,
                'affected_users_count': len(removed_from_users)
            }
        })

    except Exception as e:
        logger.error(f"Admin delete source error: {e}")
        return jsonify({
            'success': False,
            'error': f'Failed to delete source: {str(e)}'
        })

@app.route('/api/admin/validate-source', methods=['POST'])
@admin_required
def admin_validate_source():
    """Validate a source URL for admin review"""
    try:
        data = request.get_json()

        if not data or not data.get('url'):
            return jsonify({'success': False, 'error': 'URL is required'})

        url = data.get('url')
        name = data.get('name', '')
        category = data.get('category', 'general')

        result = enhanced_user_sources.validate_source(url, name, category)
        return jsonify(result)

    except Exception as e:
        logger.error(f"Admin validate source error: {e}")
        return jsonify({'success': False, 'error': 'Failed to validate source'})

@app.route('/api/admin/pending-sources', methods=['GET'])
@admin_required
def admin_get_pending_sources():
    """Get all pending custom sources for admin review"""
    try:
        pending_sources = enhanced_user_sources.get_pending_custom_sources()

        # Convert to dict format
        sources_data = []
        for source in pending_sources:
            source_dict = source.to_dict()
            # Add user info
            user = user_manager.get_user_by_id(source.user_id)
            if user:
                source_dict['submitted_by'] = {
                    'username': user.username,
                    'email': user.email,
                    'user_id': user.user_id
                }
            sources_data.append(source_dict)

        return jsonify({
            'success': True,
            'pending_sources': sources_data,
            'count': len(sources_data)
        })

    except Exception as e:
        logger.error(f"Admin get pending sources error: {e}")
        return jsonify({'success': False, 'error': 'Failed to get pending sources'})

@app.route('/api/admin/performance-stats')
@admin_required
def admin_performance_stats():
    """Get system performance statistics"""
    try:
        performance_report = performance_optimizer.get_performance_report()
        return jsonify({
            'success': True,
            'performance': performance_report
        })
    except Exception as e:
        logger.error(f"Admin performance stats error: {e}")
        return jsonify({'success': False, 'error': 'Failed to get performance statistics'})

# ============================================================================
# USER DASHBOARD ROUTES
# ============================================================================

@app.route('/dashboard')
@login_required
def user_dashboard():
    """User dashboard"""
    return render_template('user/dashboard.html')

@app.route('/api/user/profile')
@login_required
def user_profile():
    """Get current user profile"""
    try:
        current_user = get_current_user()
        user_data = current_user.to_dict()
        user_data.pop('password_hash', None)  # Remove password hash

        return jsonify({'success': True, 'user': user_data})
    except Exception as e:
        logger.error(f"User profile error: {e}")
        return jsonify({'success': False, 'error': 'Failed to load profile'})

@app.route('/api/user/source-preferences')
@login_required
def user_source_preferences():
    """Get user's news source preferences"""
    try:
        current_user = get_current_user()

        # Use enhanced user sources instead of old user manager
        preferences = enhanced_user_sources.get_user_source_preferences(current_user.user_id)

        # Get all user sources (both global and custom) for detailed information
        user_sources = enhanced_user_sources.get_user_sources(current_user.user_id)

        # Get details for each preferred source
        source_details = []
        for source_name in preferences:
            # First try to find in user's enhanced sources
            found_in_user_sources = False
            for user_source in user_sources:
                if user_source.name == source_name:
                    detail = {
                        'name': user_source.name,
                        'url': user_source.url,
                        'category': user_source.category,
                        'source_type': user_source.source_type.value if hasattr(user_source.source_type, 'value') else str(user_source.source_type)
                    }
                    source_details.append(detail)
                    found_in_user_sources = True
                    break

            # If not found in user sources, try global config (fallback)
            if not found_in_user_sources and source_name in news_sources:
                source_config = news_sources[source_name]
                if isinstance(source_config, str):
                    detail = {
                        'name': source_name,
                        'url': source_config,
                        'category': 'General',
                        'source_type': 'global'
                    }
                else:
                    detail = {
                        'name': source_name,
                        'url': source_config.get('url', ''),
                        'category': source_config.get('category', 'General'),
                        'source_type': 'global'
                    }
                source_details.append(detail)

        # Get admin limits
        limits = admin_settings_manager.get_user_limits()

        return jsonify({
            'success': True,
            'preferences': preferences,
            'source_details': source_details,
            'count': len(preferences),
            'max_allowed': limits.max_sources_per_user,
            'debug_info': {
                'user_id': current_user.user_id,
                'enhanced_sources_working': True,
                'total_user_sources': len(user_sources)
            }
        })
    except Exception as e:
        logger.error(f"User source preferences error: {e}")
        return jsonify({'success': False, 'error': 'Failed to load source preferences'})

@app.route('/api/user/sources')
@login_required
def user_sources():
    """Get user's news sources (legacy compatibility)"""
    return user_source_preferences()

@app.route('/api/user/source-preferences', methods=['POST'])
@login_required
def add_user_source_preference():
    """Add a news source preference for user (from global sources)"""
    try:
        current_user = get_current_user()
        data = request.get_json()

        source_name = data.get('source_name')

        if not source_name:
            return jsonify({'success': False, 'error': 'Source name is required'})

        # Check if source exists in global configuration
        if source_name not in news_sources:
            return jsonify({'success': False, 'error': 'Source not found in global configuration'})

        result = enhanced_user_sources.add_user_source_preference(current_user.user_id, source_name)

        if result.get('success'):
            # Check if there are existing articles from this source
            all_articles = data_manager.load_news_data()
            articles_from_new_source = []

            for article in all_articles:
                article_source = article.get('source', '').strip()
                if article_source.lower() == source_name.lower():
                    articles_from_new_source.append(article)

            # Enhance the response with guidance
            if articles_from_new_source:
                result['articles_available'] = len(articles_from_new_source)
                result['message'] = f'✅ {source_name} added successfully! {len(articles_from_new_source)} articles are now available in your feed.'
            else:
                result['articles_available'] = 0
                result['message'] = f'✅ {source_name} added successfully! Click "Fetch News" to get the latest articles from this source.'
                result['needs_fetch'] = True

        return jsonify(result)

    except Exception as e:
        logger.error(f"Add user source preference error: {e}")
        return jsonify({'success': False, 'error': 'Failed to add source preference'})

@app.route('/api/user/sources', methods=['POST'])
@login_required
def add_user_source():
    """Add a new news source for user (legacy compatibility)"""
    return add_user_source_preference()

@app.route('/api/user/sources/<source_id>')
@login_required
def get_user_source(source_id):
    """Get a specific user source"""
    try:
        current_user = get_current_user()
        source = user_manager.get_user_source_by_id(current_user.user_id, source_id)

        if not source:
            return jsonify({'success': False, 'error': 'Source not found'})

        return jsonify({'success': True, 'source': source.to_dict()})

    except Exception as e:
        logger.error(f"Get user source error: {e}")
        return jsonify({'success': False, 'error': 'Failed to load source'})

@app.route('/api/user/sources/<source_id>', methods=['PUT'])
@login_required
def update_user_source(source_id):
    """Update a user's news source"""
    try:
        current_user = get_current_user()
        data = request.get_json()

        name = data.get('name')
        url = data.get('url')
        category = data.get('category')
        enabled = data.get('enabled')

        result = user_manager.update_user_source(
            current_user.user_id, source_id, name, url, category, enabled
        )
        return jsonify(result)

    except Exception as e:
        logger.error(f"Update user source error: {e}")
        return jsonify({'success': False, 'error': 'Failed to update source'})

@app.route('/api/user/source-preferences/<source_name>', methods=['DELETE'])
@login_required
def remove_user_source_preference(source_name):
    """Remove a user's news source preference"""
    try:
        current_user = get_current_user()
        result = enhanced_user_sources.remove_user_source_preference(current_user.user_id, source_name)
        return jsonify(result)

    except Exception as e:
        logger.error(f"Remove user source preference error: {e}")
        return jsonify({'success': False, 'error': 'Failed to remove source preference'})

@app.route('/api/user/sources/<source_id>', methods=['DELETE'])
@login_required
def delete_user_source(source_id):
    """Delete a user's news source (legacy compatibility)"""
    # For legacy compatibility, treat source_id as source_name
    return remove_user_source_preference(source_id)

# ============================================================================
# ENHANCED USER SOURCE ROUTES
# ============================================================================

@app.route('/api/user/enhanced-sources')
@login_required
def user_enhanced_sources():
    """Get user's enhanced sources"""
    try:
        current_user = get_current_user()
        sources = enhanced_user_sources.get_user_sources(current_user.user_id)
        sources_data = [source.to_dict() for source in sources]

        # Get user limits
        limits = admin_settings_manager.get_user_limits()

        return jsonify({
            'success': True,
            'sources': sources_data,
            'limits': {
                'max_sources': limits.max_sources_per_user,
                'max_custom_sources': limits.max_custom_sources_per_user,
                'max_articles_per_source': limits.max_articles_per_source,
                'fetch_interval_minutes': limits.fetch_interval_minutes
            },
            'current_count': len(sources_data)
        })
    except Exception as e:
        logger.error(f"User enhanced sources error: {e}")
        return jsonify({'success': False, 'error': 'Failed to load enhanced sources'})

@app.route('/api/user/enhanced-sources', methods=['POST'])
@login_required
def add_user_enhanced_source():
    """Add a new enhanced source for user"""
    try:
        current_user = get_current_user()
        data = request.get_json()

        name = data.get('name')
        url = data.get('url')
        category = data.get('category', 'general')
        is_custom = data.get('is_custom', False)

        if not name or not url:
            return jsonify({'success': False, 'error': 'Name and URL are required'})

        from core.enhanced_user_sources import SourceType
        source_type = SourceType.USER_CUSTOM if is_custom else SourceType.GLOBAL

        result = enhanced_user_sources.add_user_source(
            current_user.user_id, name, url, category, source_type
        )
        return jsonify(result)

    except Exception as e:
        logger.error(f"Add user enhanced source error: {e}")
        return jsonify({'success': False, 'error': 'Failed to add enhanced source'})

@app.route('/api/user/enhanced-sources/<source_id>', methods=['DELETE'])
@login_required
def remove_user_enhanced_source(source_id):
    """Remove a user's enhanced source"""
    try:
        current_user = get_current_user()
        result = enhanced_user_sources.remove_user_source(current_user.user_id, source_id)
        return jsonify(result)

    except Exception as e:
        logger.error(f"Remove user enhanced source error: {e}")
        return jsonify({'success': False, 'error': 'Failed to remove enhanced source'})

@app.route('/api/user/fetch-schedule')
@login_required
def user_fetch_schedule():
    """Get user's fetch schedule"""
    try:
        current_user = get_current_user()
        schedule = enhanced_user_sources.get_user_schedule(current_user.user_id)

        return jsonify({
            'success': True,
            'schedule': schedule.to_dict(),
            'can_fetch_now': enhanced_user_sources.can_user_fetch_now(current_user.user_id)
        })
    except Exception as e:
        logger.error(f"User fetch schedule error: {e}")
        return jsonify({'success': False, 'error': 'Failed to load fetch schedule'})

@app.route('/api/user/fetch-schedule', methods=['PUT'])
@login_required
def update_user_fetch_schedule():
    """Update user's fetch schedule"""
    try:
        current_user = get_current_user()
        data = request.get_json()

        result = enhanced_user_sources.update_user_schedule(current_user.user_id, **data)
        return jsonify(result)

    except Exception as e:
        logger.error(f"Update user fetch schedule error: {e}")
        return jsonify({'success': False, 'error': 'Failed to update fetch schedule'})

@app.route('/api/user/news-feed')
@login_required
def user_news_feed():
    """Get user's personalized news feed with enhanced filtering"""
    try:
        current_user = get_current_user()

        # Check if user can fetch now
        fetch_check = enhanced_user_sources.can_user_fetch_now(current_user.user_id)
        if not fetch_check['can_fetch']:
            return jsonify({
                'success': False,
                'error': fetch_check.get('reason', 'Cannot fetch at this time'),
                'can_fetch': False
            })

        # Get user's enhanced sources
        user_sources = enhanced_user_sources.get_user_sources(current_user.user_id)
        active_sources = [s for s in user_sources if s.enabled and s.status.value == 'active']

        if not active_sources:
            return jsonify({
                'success': True,
                'articles': [],
                'message': 'No active sources configured'
            })

        # Create news fetcher with user's sources
        user_news_sources = {}
        for source in active_sources:
            if source.can_fetch_now():
                user_news_sources[source.name] = source.url

        if not user_news_sources:
            return jsonify({
                'success': True,
                'articles': [],
                'message': 'No sources ready for fetching (check fetch intervals)'
            })

        # Fetch news from user's sources with admin-configured limits
        schedule = enhanced_user_sources.get_user_schedule(current_user.user_id)
        user_fetcher = NewsFetcher(user_news_sources, max_articles_per_source=schedule.max_articles_per_source)
        articles = user_fetcher.fetch_all_news()

        # Apply user limits (max articles per source)
        schedule = enhanced_user_sources.get_user_schedule(current_user.user_id)
        limited_articles = []
        source_counts = {}

        for article in articles:
            source_name = article.get('source', 'Unknown')
            if source_counts.get(source_name, 0) < schedule.max_articles_per_source:
                limited_articles.append(article)
                source_counts[source_name] = source_counts.get(source_name, 0) + 1

        # Update fetch statistics for sources
        for source in active_sources:
            if source.name in user_news_sources:
                source.update_fetch_stats(success=True)

        return jsonify({
            'success': True,
            'articles': limited_articles,
            'source_counts': source_counts,
            'total_sources_fetched': len(user_news_sources)
        })

    except Exception as e:
        logger.error(f"User enhanced news feed error: {e}")
        return jsonify({'success': False, 'error': 'Failed to load enhanced news feed'})

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
