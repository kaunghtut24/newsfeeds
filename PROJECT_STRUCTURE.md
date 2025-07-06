# News Feed Pro - Project Structure

## Overview
This document outlines the clean, organized structure of the News Feed Pro application - an AI-powered news aggregation and analysis platform with multi-LLM support.

## Directory Structure

```
newsfeeds/
├── full_server.py                # 🚀 Main application server (primary entry point)
│
├── src/                          # Core application source code
│   ├── __init__.py              # Package initialization
│   ├── news_feed_app.py         # CLI application (alternative)
│   ├── web_news_app.py          # Web application (alternative)
│   └── core/                    # Core functionality modules
│       ├── __init__.py
│       ├── data_manager.py      # Data storage and retrieval
│       ├── news_fetcher.py      # RSS feed fetching
│       ├── categorizer.py       # Legacy categorization
│       ├── summarizer.py        # Legacy summarization
│       ├── search_engine.py     # Search functionality
│       ├── saved_searches.py    # Saved search management
│       ├── content_enhancer.py  # Content enhancement features
│       ├── reporting.py         # Professional report generation
│       ├── multi_llm_summarizer.py # Multi-LLM integration hub
│       │
│       ├── ai_features/         # 🤖 Advanced AI Features (8 features)
│       │   ├── __init__.py
│       │   ├── smart_categorizer.py      # AI-powered categorization
│       │   ├── sentiment_analyzer.py     # Sentiment analysis
│       │   ├── content_recommender.py    # Content recommendations
│       │   ├── semantic_search.py        # Advanced search
│       │   ├── ai_news_assistant.py      # AI chat assistant
│       │   ├── smart_briefing_generator.py # Automated briefings
│       │   ├── content_relationship_mapper.py # Content analysis
│       │   └── trend_analyzer.py         # Trending analysis
│       │
│       └── llm_providers/       # 🧠 Multi-LLM Provider Support
│           ├── __init__.py
│           ├── base_provider.py         # Base provider interface
│           ├── registry.py              # Provider registry
│           ├── ollama_provider.py       # Ollama (local LLM)
│           ├── openai_provider.py       # OpenAI integration
│           ├── anthropic_provider.py    # Anthropic Claude
│           └── google_provider.py       # Google AI
│
├── static/                      # 🎨 Web application assets
│   ├── css/
│   │   └── styles.css          # Modern responsive stylesheet
│   ├── js/
│   │   └── app.js              # Interactive frontend JavaScript
│   └── icons/
│       └── favicon.svg         # Application icon
│
├── templates/                   # 📄 HTML templates
│   └── index.html              # Modern web interface
│
├── data/                       # 💾 Data storage
│   ├── news_data.json         # Processed news articles
│   └── user_sources.json      # User-configured sources
│
├── backups/                    # 🔄 Automatic backups
│   └── [timestamped_backups]  # Safe code modification backups
│
├── cleanup_backup_*/           # 🧹 Cleaned unnecessary files
│   ├── test_scripts/          # Moved test files
│   ├── demo_scripts/          # Moved demo files
│   ├── old_servers/           # Moved old server versions
│   ├── duplicate_configs/     # Moved duplicate configs
│   └── old_documentation/     # Moved outdated docs
│
├── config.json                 # ⚙️ Main configuration file
├── requirements.txt            # 📦 Python dependencies
├── setup.py                   # 🔧 Package setup script
├── README.md                  # 📖 Main documentation
├── NEWS_FEED_IMPROVEMENT_PLAN.md # 🗺️ Development roadmap
├── NEW_FEATURES_DOCUMENTATION.md # 📚 AI features guide
├── PROJECT_STRUCTURE.md       # 📋 This file
└── news_report.html           # 📊 Generated HTML reports
```

## Key Components

### 🚀 Main Application (`full_server.py`)
- **Primary Entry Point**: Unified Flask server with all features
- **Multi-LLM Integration**: Supports Ollama, OpenAI, Anthropic, Google AI
- **AI Features Dashboard**: 8 comprehensive AI features
- **Professional UI**: Modern, responsive web interface
- **Report Generation**: Professional HTML reports at `/report`

### 🤖 AI Features (`src/core/ai_features/`)
**Phase 1 Features:**
1. **Smart Categorizer** - AI-powered article categorization with keyword fallback
2. **Sentiment Analyzer** - Emotion detection and sentiment tracking
3. **Content Recommender** - Personalized article suggestions
4. **Semantic Search** - Advanced content search capabilities

**Phase 2 Features:**
5. **AI News Assistant** - Interactive chat about articles with follow-up suggestions
6. **Smart Briefing Generator** - Automated news summaries and briefings
7. **Content Relationship Mapper** - Article connection and relationship analysis
8. **Trend Analyzer** - Trending topics and source analysis

### 🧠 LLM Providers (`src/core/llm_providers/`)
- **Ollama Provider** - Local LLM support (llama3:8b, qwen3:8b, etc.)
- **OpenAI Provider** - GPT models integration
- **Anthropic Provider** - Claude models integration
- **Google Provider** - Gemini models integration
- **Registry System** - Dynamic provider management and switching

### 📰 News Processing (`src/core/`)
- **Data Manager** - JSON-based data storage with backup system
- **News Fetcher** - Multi-source RSS feed processing
- **Multi-LLM Summarizer** - Unified LLM interface for all providers
- **Content Enhancer** - AI-powered content analysis and enhancement
- **Reporting** - Professional HTML report generation

### 🎨 Frontend (`static/` & `templates/`)
- **Modern UI** - Responsive design with collapsible sidebar
- **Interactive Dashboard** - Real-time AI features interface
- **Professional Styling** - Clean, modern CSS with smooth animations
- **Mobile-Friendly** - Responsive design for all screen sizes

## Data Flow

```
RSS Sources → News Fetcher → AI Processing → Web Interface
     ↓              ↓             ↓            ↓
8 Diverse     Multi-threaded   Smart Cat.   Real-time
Sources       Processing       + LLM        Updates
```

## Configuration

### News Sources (Pre-configured)
- Times of India, BBC News, Businessline, The Hindu
- Hacker News, Reddit (Programming/Technology), TechCrunch

### LLM Configuration
- **Primary**: Ollama (local, free)
- **Cloud Options**: OpenAI, Anthropic, Google AI (API keys required)
- **Model Selection**: Configurable per provider

## Cleanup Summary

### Files Moved to Backup (`cleanup_backup_*/`)
- **36 Test Scripts** - All test_*.py, check_*.py, debug_*.py files
- **Demo Scripts** - All demo_*.py and example files
- **Old Servers** - Legacy run_*.py, start_server.py, main.py files
- **Duplicate Configs** - Redundant configuration files
- **Old Documentation** - Outdated summary and guide files

### Current Clean Structure
- **1 Main Server** - `full_server.py` (primary entry point)
- **Core Modules** - Well-organized src/ directory
- **8 AI Features** - Complete AI feature implementations
- **4 LLM Providers** - Multi-provider architecture
- **Modern Frontend** - Professional web interface
- **Clean Documentation** - Updated README and guides

## Development Workflow

1. **Start Application**: `python full_server.py`
2. **Access Interface**: `http://localhost:5000`
3. **Generate Reports**: `http://localhost:5000/report`
4. **Monitor AI Features**: Check AI Features dashboard
5. **View Source Code**: Well-organized src/ directory structure

---

**🎯 Result: Clean, professional codebase ready for production deployment**
