#!/usr/bin/env python3
"""
Simple Web Runner for News Feed Application
===========================================

Quick way to run the web interface version of the news feed application.
"""

import sys
import subprocess
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.absolute()))

if __name__ == "__main__":
    print("News Feed Application - Web Interface")
    print("=" * 40)
    print("Starting web server...")
    print("Open your browser to: http://127.0.0.1:8081") # Using port 8081
    print("Press Ctrl+C to stop")
    print()
    
    try:
        command = ["python", "-m", "gunicorn", "-w", "1", "src.web_news_app:app", "-b", "127.0.0.1:8081"]
        subprocess.run(command)
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)