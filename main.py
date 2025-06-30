#!/usr/bin/env python3
"""
News Feed Application - Main Entry Point
========================================

This is the main entry point for the News Feed Application.
It can run both CLI and web interface versions.

Usage:
    python main.py                    # Run CLI version
    python main.py --web              # Run web interface
    python main.py --help             # Show help
"""

import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def main():
    parser = argparse.ArgumentParser(
        description="News Feed Application - Fetch and summarize news from multiple sources",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python main.py                    # Run CLI version
    python main.py --web              # Run web interface
    python main.py --sources techcrunch,hackernews  # Specific sources
    python main.py --limit 5          # Limit to 5 articles per source
        """
    )
    
    parser.add_argument(
        '--web', 
        action='store_true',
        help='Run web interface instead of CLI'
    )
    
    parser.add_argument(
        '--sources',
        default='techcrunch,hackernews,reddit',
        help='Comma-separated list of sources (default: techcrunch,hackernews,reddit)'
    )
    
    parser.add_argument(
        '--limit',
        type=int,
        default=10,
        help='Number of articles per source (default: 10)'
    )
    
    parser.add_argument(
        '--output',
        default='news_report.html',
        help='Output file for CLI version (default: news_report.html)'
    )
    
    parser.add_argument(
        '--host',
        default='127.0.0.1',
        help='Host for web interface (default: 127.0.0.1)'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=8080,
        help='Port for web interface (default: 8080)'
    )
    
    args = parser.parse_args()
    
    if args.web:
        # Run web interface
        from web_news_app import app
        import uvicorn
        
        print(f"🌐 Starting News Feed Pro Web Interface with Multi-LLM Support...")
        print(f"🤖 Supported providers: OpenAI, Anthropic, Google AI, Ollama")
        print(f"💡 Configure API keys in environment variables or llm_config.json")
        print(f"📡 Open your browser to: http://{args.host}:{args.port}")
        print("Press Ctrl+C to stop")
        
        uvicorn.run(
            app,
            host=args.host,
            port=args.port,
            reload=True
        )
    else:
        # Run CLI version
        from news_feed_app import NewsFeedApp
        
        print("📰 News Feed Pro - CLI Version with Multi-LLM Support")
        print("🤖 Will use the best available LLM provider for summarization")
        print("=" * 60)
        
        app = NewsFeedApp()
        
        # Parse sources
        sources = [s.strip() for s in args.sources.split(',')]
        
        print(f"Fetching news from: {', '.join(sources)}")
        print(f"Articles per source: {args.limit}")
        print(f"Output file: {args.output}")
        print()
        
        try:
            app.run_cli(
                sources=sources,
                limit=args.limit,
                output_file=args.output
            )
        except KeyboardInterrupt:
            print("\nOperation cancelled by user")
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main() 