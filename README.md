# 📰 News Feed Pro

An AI-powered news aggregation and analysis application with multi-LLM support, intelligent categorization, and modern web interface.

![News Feed Pro](https://img.shields.io/badge/News%20Feed-Pro-blue)
![Python](https://img.shields.io/badge/Python-3.8+-green)
![Flask](https://img.shields.io/badge/Flask-2.0+-red)
![Multi-LLM](https://img.shields.io/badge/Multi--LLM-Supported-purple)

## ✨ Features

### 🤖 AI-Powered Features
- **Smart Categorization**: AI-powered article categorization with keyword fallback
- **Multi-LLM Integration**: Ollama (local), OpenAI, Anthropic, Google AI support
- **Intelligent Summarization**: Real-time AI article summaries
- **Sentiment Analysis**: Automated sentiment detection and tracking
- **AI Chat Assistant**: Interactive AI chat with article context
- **Trending Analysis**: AI-powered trending topics and source analysis

### 📰 News Processing
- **Multi-Source Aggregation**: 8 diverse RSS sources (Times of India, BBC, TechCrunch, etc.)
- **Real-time Fetching**: Automatic news updates and processing
- **Content Enhancement**: AI-powered content analysis and enrichment
- **Smart Filtering**: Advanced search with category and sentiment filters
- **Report Generation**: Professional HTML reports with AI insights

### 🎨 Modern Interface
- **Responsive Design**: Mobile-friendly, collapsible sidebar
- **Real-time Updates**: Live status monitoring and progress tracking
- **Professional UI**: Clean, modern design with smooth animations
- **Interactive Dashboard**: Comprehensive AI features dashboard
- **Accessibility**: Keyboard navigation and screen reader support

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+**
- **Internet connection** for fetching news
- **Ollama** (recommended) or other LLM providers (OpenAI, Anthropic, Google AI)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/kaunghtut24/newsfeeds.git
   cd newsfeeds
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Ollama (recommended for local AI):**
   ```bash
   # Install Ollama from https://ollama.ai
   ollama pull llama3:8b
   ollama pull qwen3:8b
   ```

4. **Start the application:**
   ```bash
   python full_server.py
   ```

5. **Open your browser:**
   ```
   http://localhost:5000
   ```

## 🎯 Usage

### Web Interface

1. **Access the application** at `http://localhost:5000`
2. **Fetch News**: Click "🔄 Fetch News" to get latest articles
3. **Browse Articles**: View AI-categorized articles with summaries
4. **AI Features**: Explore the AI Features dashboard for:
   - Smart categorization and sentiment analysis
   - AI chat assistant for article discussions
   - Trending topics and active sources analysis
   - Content insights and recommendations
5. **Generate Reports**: Visit `/report` for professional HTML reports
6. **Search & Filter**: Use advanced search with category and sentiment filters

### Key Endpoints

- **Main App**: `http://localhost:5000/`
- **HTML Reports**: `http://localhost:5000/report`
- **API Status**: `http://localhost:5000/api/ai-features/status`
- **News Data**: `http://localhost:5000/api/news`

## ⚙️ Configuration

### News Sources (Pre-configured)

The application comes with 8 diverse news sources:

- **Times of India** - Indian business and general news
- **BBC News** - International business news
- **Businessline** - Indian business and economy
- **The Hindu** - Indian business news
- **Hacker News** - Technology and startup news
- **Reddit Programming** - Programming discussions
- **Reddit Technology** - Technology news and discussions
- **TechCrunch** - Technology and startup news

### LLM Configuration

Edit `config.json` to configure AI models:

```json
{
  "llm": {
    "provider": "ollama",
    "ollama_model": "llama3:8b",
    "openai_model": "gpt-3.5-turbo",
    "anthropic_model": "claude-3-haiku-20240307",
    "google_model": "gemini-pro"
  }
}
```

### Adding API Keys (Optional)

For cloud LLM providers, add API keys to `config.json`:

```json
{
  "api_keys": {
    "openai": "your-openai-api-key",
    "anthropic": "your-anthropic-api-key",
    "google": "your-google-api-key"
  }
}
```

## 🛠️ Development

### Project Structure

```
newsfeeds/
├── full_server.py              # Main application server
├── src/                        # Core application code
│   ├── core/                  # Core modules
│   │   ├── ai_features/       # AI feature implementations
│   │   ├── llm_providers/     # Multi-LLM provider support
│   │   ├── data_manager.py    # Data management
│   │   ├── multi_llm_summarizer.py  # LLM integration
│   │   └── reporting.py       # Report generation
│   ├── news_feed_app.py       # CLI application
│   └── web_news_app.py        # Alternative web app
├── static/                    # Web assets
│   ├── css/styles.css        # Main stylesheet
│   ├── js/app.js             # Frontend JavaScript
│   └── icons/                # Icons and images
├── templates/                 # HTML templates
│   └── index.html            # Main web interface
├── data/                     # Data storage
│   ├── news_data.json        # Processed news articles
│   └── user_sources.json     # User source configurations
├── config.json               # Main configuration
└── requirements.txt          # Python dependencies
```

### Architecture

- **Backend**: Flask server with multi-LLM integration
- **Frontend**: Modern JavaScript with responsive CSS
- **AI Features**: 8 comprehensive AI features for news analysis
- **Data Flow**: RSS → Processing → AI Analysis → Web Interface
- **Storage**: JSON-based with backup system

## 🚨 Troubleshooting

### Common Issues

1. **Ollama Not Running**:
   ```bash
   # Start Ollama service
   ollama serve
   # Pull required models
   ollama pull llama3:8b
   ```

2. **Port Already in Use**:
   ```bash
   # Kill process on port 5000
   lsof -ti:5000 | xargs kill -9
   # Or use different port
   export PORT=5001 && python full_server.py
   ```

3. **No News Articles Loading**:
   - Check internet connection
   - Verify RSS sources are accessible
   - Check server logs for fetch errors

4. **AI Features Not Working**:
   - Ensure Ollama is running with required models
   - Check LLM provider status in web interface
   - Verify API keys for cloud providers

## 📊 API Reference

### Core Endpoints

- `GET /` - Main web interface
- `GET /report` - HTML report generation
- `GET /api/news` - Get processed news articles
- `GET /api/sources` - Get configured news sources
- `GET /api/ai-features/status` - AI features status

### AI Features API

- `POST /api/ai-features/smart-categorization` - Categorize articles
- `POST /api/ai-features/ai-chat` - AI chat assistant
- `GET /api/trending-analysis` - Trending topics and sources
- `GET /api/content-insights` - Content analysis insights
- `GET /api/llm-providers` - LLM provider status

## 🎯 AI Features Overview

### Phase 1 Features
1. **Smart Categorizer** - AI-powered article categorization
2. **Sentiment Analyzer** - Emotion detection in articles
3. **Content Recommender** - Personalized article suggestions
4. **Semantic Search** - Advanced content search capabilities

### Phase 2 Features
5. **AI News Assistant** - Interactive chat about articles
6. **Smart Briefing Generator** - Automated news summaries
7. **Content Relationship Mapper** - Article connection analysis
8. **Trend Analyzer** - Trending topics and source analysis

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and test thoroughly
4. Commit your changes: `git commit -am 'Add feature'`
5. Push to the branch: `git push origin feature-name`
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **AI Models**: Ollama (llama3, qwen3), OpenAI, Anthropic, Google AI
- **News Sources**: Times of India, BBC, TechCrunch, Hacker News, Reddit
- **Framework**: Flask, modern JavaScript, responsive CSS
- **Community**: Open source contributors and AI enthusiasts

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/kaunghtut24/newsfeeds/issues)
- **Documentation**: See `NEWS_FEED_IMPROVEMENT_PLAN.md` for roadmap
- **Features**: Check `NEW_FEATURES_DOCUMENTATION.md` for AI features guide

---

**🚀 AI-Powered News Intelligence Platform**