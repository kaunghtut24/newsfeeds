#!/usr/bin/env python3
"""
Script to add @login_required decorators to AI features endpoints
"""

import re

def add_auth_decorators():
    # Read the file
    with open('full_server.py', 'r') as f:
        content = f.read()
    
    # List of AI features endpoints that need authentication
    endpoints = [
        '/api/ai-features/recommendations',
        '/api/ai-features/semantic-search',
        '/api/ai-features/search-suggestions',
        '/api/ai-features/status',
        '/api/ai-features/relationship-analysis',
        '/api/ai-features/trend-analysis',
        '/api/ai-features/ai-chat',
        '/api/ai-features/explain-article',
        '/api/ai-features/daily-briefing',
        '/api/ai-features/topic-deep-dive',
        '/api/trending-analysis',
        '/api/content-insights',
        '/api/llm-providers',
        '/report'
    ]
    
    # Add @login_required decorator to each endpoint
    for endpoint in endpoints:
        # Escape special regex characters
        escaped_endpoint = re.escape(endpoint)
        
        # Pattern to match the route decorator
        pattern = f"(@app\\.route\\('{escaped_endpoint}'[^)]*\\))\n(def [^(]+\\([^)]*\\):)"
        
        # Replacement with @login_required decorator
        replacement = r"\1\n@login_required\n\2"
        
        # Apply the replacement
        content = re.sub(pattern, replacement, content)
    
    # Write the modified content back
    with open('full_server.py', 'w') as f:
        f.write(content)
    
    print("✅ Added @login_required decorators to AI features endpoints")

if __name__ == "__main__":
    add_auth_decorators()
