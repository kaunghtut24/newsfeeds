#!/usr/bin/env python3
"""
Setup script for News Feed Application
======================================

Installation:
    pip install -e .
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text() if readme_path.exists() else ""

# Read requirements
requirements_path = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_path.exists():
    requirements = [line.strip() for line in requirements_path.read_text().split('\n') 
                   if line.strip() and not line.startswith('#')]

setup(
    name="news-feed-application",
    version="1.0.0",
    author="Agentic AI Engineer",
    description="A news feed application that fetches and summarizes news from multiple sources",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "news-feed=main:main",
            "news-feed-cli=run_cli:main",
            "news-feed-web=run_web:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="news feed aggregator summarizer ollama",
    project_urls={
        "Source": "https://github.com/example/news-feed-application",
        "Bug Reports": "https://github.com/example/news-feed-application/issues",
    },
) 