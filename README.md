# 📰 News Feed Pro

A comprehensive, modern news aggregation and analysis application with multi-LLM support, advanced search capabilities, and beautiful UI.

![News Feed Pro](https://img.shields.io/badge/News%20Feed-Pro-blue)
![Python](https://img.shields.io/badge/Python-3.8+-green)
![Flask](https://img.shields.io/badge/Flask-2.0+-red)
![Multi-LLM](https://img.shields.io/badge/Multi--LLM-Supported-purple)

## ✨ Features

### 🚀 Core Features
- **Multi-Source News Aggregation**: RSS feeds, APIs, and web scraping
- **Multi-LLM Integration**: OpenAI, Anthropic, Google, Ollama support
- **Intelligent Summarization**: AI-powered article summaries
- **Sentiment Analysis**: Real-time sentiment tracking
- **Advanced Search**: Full-text search with filters and saved searches
- **Modern Web UI**: Responsive design with dark/light mode

### 🎯 Advanced Features
- **Real-time Processing**: Background news fetching and analysis
- **Content Insights**: Trending topics, sentiment overview, statistics
- **Source Management**: Configurable news sources and providers
- **Export Capabilities**: HTML reports and data export
- **Error Recovery**: Robust error handling and UI recovery
- **Debug Tools**: Comprehensive debugging and monitoring

### 🛡️ Reliability Features
- **Self-Recovering UI**: Automatic loading state management
- **Emergency Reset**: Multiple recovery options for stuck states
- **Comprehensive Logging**: Detailed debug and error logging
- **Timeout Protection**: Automatic processing timeout handling
- **Graceful Degradation**: Continues working even if some services fail

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+**
- **Internet connection** for fetching news
- **LLM Provider** (Ollama, OpenAI, Anthropic, or Google)

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

3. **Configure LLM providers** (optional):
   ```bash
   # Edit llm_config.json to add your API keys
   cp llm_config.json llm_config_local.json
   # Add your API keys to llm_config_local.json
   ```

4. **Start the application:**
   ```bash
   python -m src.web_news_app
   ```

5. **Open your browser:**
   ```
   http://localhost:5000
   ```

## 🎯 Usage

### Web Interface

1. **Access the application** at `http://localhost:5000`
2. **Fetch News**: Click "🚀 Fetch & Summarize News"
3. **Browse Articles**: View summarized articles with sentiment analysis
4. **Search**: Use advanced search with filters
5. **Insights**: Check trending topics and content statistics

### Command Line Interface

```bash
# Run CLI version
python run_cli.py

# Run web server
python run_web.py

# Demo features
python demo_multi_llm.py
python demo_advanced_features.py
```

## ⚙️ Configuration

### News Sources

Edit `config.json` to configure news sources:

```json
{
  "news_sources": {
    "techcrunch": "https://techcrunch.com/feed/",
    "hackernews": "https://hacker-news.firebaseio.com/v0/topstories.json",
    "custom_source": "https://example.com/rss"
  }
}
```

### LLM Providers

Configure LLM providers in `llm_config.json`:

```json
{
  "providers": {
    "openai": {
      "enabled": true,
      "api_key": "your-api-key",
      "model": "gpt-3.5-turbo"
    },
    "ollama": {
      "enabled": true,
      "base_url": "http://localhost:11434",
      "model": "llama3:8b"
    }
  }
}
```

## 🛠️ Development

### Project Structure

```
newsfeeds/
├── src/                    # Core application code
│   ├── core/              # Core modules
│   ├── news_feed_app.py   # CLI application
│   └── web_news_app.py    # Web application
├── static/                # Web assets
│   ├── css/              # Stylesheets
│   ├── js/               # JavaScript
│   └── icons/            # Icons and images
├── templates/             # HTML templates
├── config.json           # Configuration
├── llm_config.json       # LLM configuration
└── requirements.txt      # Dependencies
```

### Running Tests

```bash
# Test the application
python test_project.py

# Test UI fixes
python test_ui_fixes.py
```

### Debug Mode

Enable debug logging by setting `debugMode: true` in the JavaScript console or using the debug tools.

## 🚨 Troubleshooting

### Common Issues

1. **Loading Overlay Stuck**:
   ```javascript
   // In browser console:
   emergencyUIReset()
   ```

2. **Processing Stuck**:
   ```bash
   curl -X POST http://localhost:5000/api/reset-processing
   ```

3. **LLM Provider Issues**:
   - Check API keys in `llm_config.json`
   - Verify provider status in the web interface
   - Use health check: `/api/llm-providers/health-check`

### Debug Tools

- **Debug UI**: Open `debug_ui.html` for comprehensive debugging
- **Browser Console**: Use `emergencyUIReset()` and `forceResetProcessing()`
- **Server Logs**: Check console output for detailed logging

## 📊 API Reference

### Main Endpoints

- `GET /` - Web interface
- `POST /api/fetch-news` - Fetch and process news
- `GET /api/news` - Get processed news
- `GET /api/status` - Check processing status
- `POST /api/reset-processing` - Reset stuck processing
- `GET /api/llm-providers` - LLM provider status

### Search API

- `POST /api/search` - Advanced search
- `GET /api/search/suggestions` - Search suggestions
- `GET /api/saved-searches` - Saved searches

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Add tests if applicable
5. Commit your changes: `git commit -am 'Add feature'`
6. Push to the branch: `git push origin feature-name`
7. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Multi-LLM Support**: OpenAI, Anthropic, Google, Ollama
- **News Sources**: TechCrunch, Hacker News, Reddit, and more
- **UI Framework**: Modern CSS with responsive design
- **Icons**: Various open-source icon sets

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/kaunghtut24/newsfeeds/issues)
- **Documentation**: Check the `/docs` folder for detailed documentation
- **Debug Tools**: Use built-in debug utilities for troubleshooting

---

**Made with ❤️ for the news and AI community**