#!/usr/bin/env python3
"""
Simple CLI Runner for News Feed Application
===========================================

Quick way to run the CLI version of the news feed application.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from news_feed_app import NewsFeedApp

if __name__ == "__main__":
    print("News Feed Application - CLI Version")
    print("=" * 40)
    
    app = NewsFeedApp()
    
    try:
        app.run_cli()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1) 