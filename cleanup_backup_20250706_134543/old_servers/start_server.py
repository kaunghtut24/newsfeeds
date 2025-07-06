#!/usr/bin/env python3
"""
Simple Flask Development Server Starter
=======================================

Starts the News Feed Application web server using Flask's built-in development server.
This is perfect for testing and development.
"""

import sys
import os
from pathlib import Path

# Add src to Python path
src_path = str(Path(__file__).parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

def main():
    print("🚀 News Feed Application - Development Server")
    print("=" * 50)
    print()
    
    try:
        # Import the Flask app
        from web_news_app import app
        
        print("✅ Flask app imported successfully")
        print("🌐 Starting development server...")
        print("📱 Open your browser to: http://127.0.0.1:5000")
        print("🛑 Press Ctrl+C to stop the server")
        print()
        print("Server starting...")
        print("-" * 30)
        
        # Start the Flask development server
        app.run(
            host='127.0.0.1',
            port=5000,
            debug=True,
            use_reloader=False  # Disable reloader to avoid issues in some environments
        )
        
    except ImportError as e:
        print(f"❌ Error importing Flask app: {e}")
        print("💡 Make sure you're in the virtual environment:")
        print("   .\\venv\\Scripts\\activate")
        sys.exit(1)
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
