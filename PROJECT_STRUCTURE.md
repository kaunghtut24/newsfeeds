# News Feed Application - Project Structure

## Overview
This is a complete news feed application that fetches and summarizes news from multiple sources using Ollama for AI-powered summarization.

## Project Structure
```
news_feed_application/
├── main.py                 # Main entry point with CLI arguments
├── run_cli.py             # Simple CLI runner
├── run_web.py             # Simple web runner
├── setup.py               # Package setup and installation
├── requirements.txt       # Python dependencies
├── README.md              # Project documentation
├── .gitignore            # Git ignore rules
├── test_project.py       # Project structure and functionality tests
├── PROJECT_STRUCTURE.md  # This file
├── src/                  # Source code package
│   ├── __init__.py       # Package initialization
│   ├── news_feed_app.py  # CLI version of the application
│   └── web_news_app.py   # Web interface using FastAPI
├── templates/            # HTML templates (for future use)
└── static/              # Static files (CSS, JS, images)
```

## Key Features

### CLI Version (`src/news_feed_app.py`)
- Fetches news from multiple sources (TechCrunch, Hacker News, Reddit)
- Uses Ollama for AI-powered summarization
- Generates HTML reports with styled output
- Real-time progress updates
- Configurable sources and article limits

### Web Interface (`src/web_news_app.py`)
- FastAPI-based web application
- Real-time status updates via Server-Sent Events
- Interactive web interface
- Same functionality as CLI but with web UI

### Main Entry Point (`main.py`)
- Unified interface for both CLI and web versions
- Command-line argument parsing
- Flexible configuration options

## Installation and Usage

### Quick Start
```bash
# Install dependencies
pip install -r requirements.txt

# Run CLI version
python main.py

# Run web interface
python main.py --web

# Or use the simple runners
python run_cli.py
python run_web.py
```

### Advanced Usage
```bash
# Custom sources and limits
python main.py --sources techcrunch,hackernews --limit 5

# Custom output file
python main.py --output my_news_report.html

# Custom web server settings
python main.py --web --host 0.0.0.0 --port 9000
```

## Dependencies
- **requests**: HTTP requests for fetching news
- **flask**: Web framework for CLI version
- **feedparser**: RSS feed parsing
- **beautifulsoup4**: HTML parsing
- **lxml**: XML/HTML parser backend
- **fastapi**: Web framework for web interface
- **uvicorn**: ASGI server for web interface

## Development

### Testing
```bash
python test_project.py
```

### Installation in Development Mode
```bash
pip install -e .
```

### Available Commands (after installation)
```bash
news-feed          # Main application
news-feed-cli      # CLI version
news-feed-web      # Web version
```

## File Descriptions

### Core Application Files
- **`src/news_feed_app.py`**: CLI version with news fetching, summarization, and HTML report generation
- **`src/web_news_app.py`**: FastAPI web application with real-time updates
- **`main.py`**: Unified entry point with argument parsing

### Runner Scripts
- **`run_cli.py`**: Simple CLI runner without arguments
- **`run_web.py`**: Simple web runner with default settings

### Project Files
- **`setup.py`**: Package configuration for pip installation
- **`requirements.txt`**: Python dependencies
- **`README.md`**: Comprehensive project documentation
- **`.gitignore`**: Git ignore patterns
- **`test_project.py`**: Project structure and functionality tests

### Directories
- **`src/`**: Source code package
- **`templates/`**: HTML templates (ready for future enhancements)
- **`static/`**: Static files (ready for future enhancements)

## Architecture

### Modular Design
The application is designed with modularity in mind:
- Core functionality in `src/` package
- Separate CLI and web interfaces
- Shared utilities and configurations
- Easy to extend with new features

### Error Handling
- Comprehensive error handling throughout
- Graceful degradation when sources are unavailable
- User-friendly error messages
- Logging for debugging

### Configuration
- Command-line arguments for flexibility
- Environment variable support (ready for future use)
- Configurable sources, limits, and output formats

## Future Enhancements
The project structure is designed to support future enhancements:
- Additional news sources
- Database storage for articles
- User authentication
- Custom themes and styling
- API endpoints for external integration
- Scheduled news fetching
- Email notifications 