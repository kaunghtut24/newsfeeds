import os
from datetime import datetime
from typing import List, Dict

class ReportGenerator:
    def __init__(self, base_path: str = '/home/yuthar/Documents/news_feed_application/'):
        self.base_path = base_path

    def create_html_report(self, news_data: List[Dict], filename: str = "news_report.html"):
        """Create an HTML report of the news"""
        full_path = os.path.join(self.base_path, filename)
        html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>News Feed Report</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .header {
            background-color: #2c3e50;
            color: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .news-item {
            background-color: white;
            margin-bottom: 20px;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .news-title {
            color: #2c3e50;
            font-size: 1.2em;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .news-meta {
            color: #7f8c8d;
            font-size: 0.9em;
            margin-bottom: 10px;
        }
        .news-link {
            color: #3498db;
            text-decoration: none;
        }
        .news-link:hover {
            text-decoration: underline;
        }
        .news-summary {
            background-color: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            margin-top: 10px;
        }
        .timestamp {
            color: #95a5a6;
            font-size: 0.8em;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🗞️ News Feed Report</h1>
        <p>Generated on: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>
    </div>
"""
        
        for i, item in enumerate(news_data, 1):
            html_content += f"""
    <div class="news-item">
        <div class="news-title">{i}. {item['title']}</div>
        <div class="news-meta">
            Source: {item['source']} | Category: {item.get('category', 'N/A')} | 
            <a href="{item['link']}" class="news-link" target="_blank">Read Full Article</a>
        </div>
        <div class="timestamp">Published: {item['timestamp']}</div>
        <div class="news-summary">
            <strong>Summary:</strong> {item.get('summary', 'No summary available')}
        </div>
    </div>
"""
        
        html_content += """
</body>
</html>
"""
        
        try:
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"✅ HTML report saved to {full_path}")
        except Exception as e:
            print(f"❌ Error saving HTML report: {e}")