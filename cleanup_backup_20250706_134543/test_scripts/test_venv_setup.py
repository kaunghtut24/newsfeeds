#!/usr/bin/env python3
"""
Virtual Environment Setup Test
==============================

This script tests that the virtual environment is properly set up
and all dependencies are correctly installed.
"""

import sys
import os
import subprocess
from pathlib import Path

def test_python_version():
    """Test Python version compatibility."""
    print("Testing Python version...")
    version = sys.version_info
    print(f"  Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor >= 8:
        print("  ✓ Python version is compatible (3.8+)")
        return True
    else:
        print("  ✗ Python version is not compatible (requires 3.8+)")
        return False

def test_virtual_environment():
    """Test that we're running in a virtual environment."""
    print("\nTesting virtual environment...")
    
    # Check if we're in a virtual environment
    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )
    
    if in_venv:
        print("  ✓ Running in virtual environment")
        print(f"  Virtual env path: {sys.prefix}")
        return True
    else:
        print("  ⚠ Not running in virtual environment")
        print("  This is okay, but virtual environment is recommended")
        return True

def test_dependencies():
    """Test that all required dependencies are installed."""
    print("\nTesting dependencies...")
    
    dependencies = [
        'requests',
        'flask',
        'feedparser',
        'bs4',  # beautifulsoup4 imports as bs4
        'lxml',
        'aiohttp',
        'gunicorn',
        'pytest'
    ]
    
    all_installed = True
    
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"  ✓ {dep}")
        except ImportError:
            print(f"  ✗ {dep} - Not installed")
            all_installed = False
    
    return all_installed

def test_project_imports():
    """Test that project modules can be imported."""
    print("\nTesting project imports...")
    
    # Add src to path
    sys.path.insert(0, str(Path(__file__).parent / "src"))
    
    modules_to_test = [
        ('news_feed_app', 'src.news_feed_app'),
        ('web_news_app', 'src.web_news_app'),
        ('news_fetcher', 'src.core.news_fetcher'),
        ('summarizer', 'src.core.summarizer'),
    ]
    
    all_imported = True
    
    for name, module in modules_to_test:
        try:
            __import__(module)
            print(f"  ✓ {name}")
        except ImportError as e:
            print(f"  ✗ {name} - Import error: {e}")
            all_imported = False
    
    return all_imported

def test_flask_app():
    """Test that Flask app can be created."""
    print("\nTesting Flask app creation...")
    
    try:
        sys.path.insert(0, str(Path(__file__).parent / "src"))
        from web_news_app import app
        
        with app.test_client() as client:
            # Test that app can handle a basic request
            response = client.get('/')
            print(f"  ✓ Flask app created successfully")
            print(f"  ✓ Home page responds with status: {response.status_code}")
            return True
            
    except Exception as e:
        print(f"  ✗ Flask app creation failed: {e}")
        return False

def main():
    """Run all tests."""
    print("Virtual Environment Setup Test")
    print("=" * 50)
    
    tests = [
        test_python_version,
        test_virtual_environment, 
        test_dependencies,
        test_project_imports,
        test_flask_app
    ]
    
    results = []
    
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"  ✗ Test failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("Test Summary:")
    print(f"  Passed: {sum(results)}/{len(results)}")
    
    if all(results):
        print("  ✓ All tests passed! Virtual environment is ready for testing.")
        print("\nYou can now run:")
        print("  - python main.py (CLI version)")
        print("  - python main.py --web (Web version)")
        print("  - python run_web.py (Web server)")
        print("  - pytest (Run unit tests)")
    else:
        print("  ⚠ Some tests failed. Check the output above for details.")
    
    return all(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
