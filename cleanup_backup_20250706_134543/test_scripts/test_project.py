#!/usr/bin/env python3
"""
Test script for News Feed Application
=====================================

This script tests the project structure and basic functionality.
"""

import sys
import os
from pathlib import Path

def test_project_structure():
    """Test that all required files and directories exist."""
    print("Testing project structure...")
    
    required_files = [
        "main.py",
        "run_cli.py", 
        "run_web.py",
        "setup.py",
        "requirements.txt",
        "README.md",
        ".gitignore",
        "src/__init__.py",
        "src/news_feed_app.py",
        "src/web_news_app.py"
    ]
    
    required_dirs = [
        "src",
        "templates", 
        "static"
    ]
    
    all_good = True
    
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path} - MISSING")
            all_good = False
    
    for dir_path in required_dirs:
        if Path(dir_path).is_dir():
            print(f"✓ {dir_path}/")
        else:
            print(f"✗ {dir_path}/ - MISSING")
            all_good = False
    
    return all_good

def test_imports():
    """Test that modules can be imported."""
    print("\nTesting imports...")
    
    # Add src to path
    sys.path.insert(0, str(Path(__file__).parent.absolute()))
    
    try:
        from src import news_feed_app
        print("✓ news_feed_app imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import news_feed_app: {e}")
        return False
    
    try:
        from src import web_news_app
        print("✓ web_news_app imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import web_news_app: {e}")
        return False
    
    return True

def test_requirements():
    """Test that requirements.txt is valid."""
    print("\nTesting requirements.txt...")
    
    try:
        with open("requirements.txt", "r") as f:
            requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]
        
        print(f"✓ Found {len(requirements)} requirements")
        for req in requirements:
            print(f"  - {req}")
        
        return True
    except Exception as e:
        print(f"✗ Error reading requirements.txt: {e}")
        return False

def main():
    """Run all tests."""
    print("News Feed Application - Project Test")
    print("=" * 40)
    
    # Change to project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    tests = [
        ("Project Structure", test_project_structure),
        ("Imports", test_imports),
        ("Requirements", test_requirements)
    ]
    
    all_passed = True
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * len(test_name))
        
        try:
            result = test_func()
            if not result:
                all_passed = False
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
            all_passed = False
    
    print("\n" + "=" * 40)
    if all_passed:
        print("✓ All tests passed! Project is ready to use.")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Run CLI version: python main.py")
        print("3. Run web version: python main.py --web")
    else:
        print("✗ Some tests failed. Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 