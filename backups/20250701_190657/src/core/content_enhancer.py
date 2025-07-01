"""
Content Enhancement Module
Provides sentiment analysis, trending detection, and content enrichment
"""

import re
import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import math


class SentimentAnalyzer:
    """Simple rule-based sentiment analysis for news articles"""
    
    def __init__(self):
        # Positive sentiment words
        self.positive_words = {
            'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'outstanding',
            'success', 'successful', 'achievement', 'breakthrough', 'innovation', 'progress',
            'growth', 'improvement', 'benefit', 'advantage', 'positive', 'optimistic',
            'hope', 'hopeful', 'promising', 'bright', 'strong', 'robust', 'healthy',
            'win', 'victory', 'triumph', 'celebrate', 'celebration', 'joy', 'happy',
            'pleased', 'satisfied', 'confident', 'secure', 'stable', 'recovery',
            'boom', 'surge', 'rise', 'increase', 'gain', 'profit', 'revenue'
        }
        
        # Negative sentiment words
        self.negative_words = {
            'bad', 'terrible', 'awful', 'horrible', 'disaster', 'crisis', 'problem',
            'issue', 'concern', 'worry', 'fear', 'afraid', 'scared', 'panic',
            'fail', 'failure', 'failed', 'collapse', 'crash', 'decline', 'drop',
            'fall', 'loss', 'lose', 'losing', 'deficit', 'debt', 'bankruptcy',
            'recession', 'depression', 'unemployment', 'layoffs', 'cuts', 'reduction',
            'violence', 'war', 'conflict', 'attack', 'threat', 'danger', 'risk',
            'death', 'died', 'killed', 'murder', 'crime', 'illegal', 'scandal',
            'corruption', 'fraud', 'controversy', 'protest', 'riot', 'chaos'
        }
        
        # Neutral/factual words that might appear in news
        self.neutral_indicators = {
            'report', 'reports', 'according', 'statement', 'announced', 'said',
            'meeting', 'conference', 'study', 'research', 'data', 'statistics',
            'government', 'official', 'company', 'organization', 'department'
        }
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of text
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with sentiment analysis results
        """
        if not text:
            return {
                'sentiment': 'neutral',
                'confidence': 0.0,
                'positive_score': 0.0,
                'negative_score': 0.0,
                'neutral_score': 1.0
            }
        
        # Tokenize and clean text
        words = self._tokenize(text.lower())
        
        # Count sentiment words
        positive_count = sum(1 for word in words if word in self.positive_words)
        negative_count = sum(1 for word in words if word in self.negative_words)
        neutral_count = sum(1 for word in words if word in self.neutral_indicators)
        
        total_sentiment_words = positive_count + negative_count + neutral_count
        
        if total_sentiment_words == 0:
            return {
                'sentiment': 'neutral',
                'confidence': 0.5,
                'positive_score': 0.0,
                'negative_score': 0.0,
                'neutral_score': 1.0
            }
        
        # Calculate scores
        positive_score = positive_count / len(words)
        negative_score = negative_count / len(words)
        neutral_score = max(0.1, 1.0 - positive_score - negative_score)
        
        # Determine overall sentiment
        if positive_score > negative_score and positive_score > 0.02:
            sentiment = 'positive'
            confidence = min(0.9, positive_score * 10)
        elif negative_score > positive_score and negative_score > 0.02:
            sentiment = 'negative'
            confidence = min(0.9, negative_score * 10)
        else:
            sentiment = 'neutral'
            confidence = 0.5 + (neutral_count / total_sentiment_words) * 0.3
        
        return {
            'sentiment': sentiment,
            'confidence': confidence,
            'positive_score': positive_score,
            'negative_score': negative_score,
            'neutral_score': neutral_score
        }
    
    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization"""
        return re.findall(r'\b[a-zA-Z]{2,}\b', text)


class TrendingDetector:
    """Detects trending topics and keywords in news articles"""
    
    def __init__(self, time_window_hours: int = 24):
        self.time_window_hours = time_window_hours
        self.stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have',
            'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
            'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those',
            'said', 'says', 'new', 'news', 'report', 'reports', 'according'
        }
    
    def detect_trending_topics(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Detect trending topics from recent articles
        
        Args:
            articles: List of news articles
            
        Returns:
            List of trending topics with scores
        """
        # Filter recent articles
        cutoff_time = datetime.now() - timedelta(hours=self.time_window_hours)
        recent_articles = []
        
        for article in articles:
            article_time = self._parse_article_date(article)
            if article_time and article_time >= cutoff_time:
                recent_articles.append(article)
        
        if not recent_articles:
            return []
        
        # Extract keywords from titles and summaries
        keyword_counts = defaultdict(int)
        keyword_articles = defaultdict(set)
        
        for i, article in enumerate(recent_articles):
            text = f"{article.get('title', '')} {article.get('summary', '')}"
            keywords = self._extract_keywords(text)
            
            for keyword in keywords:
                keyword_counts[keyword] += 1
                keyword_articles[keyword].add(i)
        
        # Calculate trending scores
        trending_topics = []
        total_articles = len(recent_articles)
        
        for keyword, count in keyword_counts.items():
            if count >= 2:  # Must appear in at least 2 articles
                # Calculate trend score based on frequency and article spread
                frequency_score = count / total_articles
                spread_score = len(keyword_articles[keyword]) / total_articles
                trend_score = (frequency_score + spread_score) / 2
                
                trending_topics.append({
                    'keyword': keyword,
                    'count': count,
                    'trend_score': trend_score,
                    'article_count': len(keyword_articles[keyword]),
                    'articles': list(keyword_articles[keyword])[:5]  # Sample articles
                })
        
        # Sort by trend score
        trending_topics.sort(key=lambda x: x['trend_score'], reverse=True)
        return trending_topics[:20]  # Top 20 trending topics
    
    def detect_trending_sources(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect which news sources are most active recently"""
        cutoff_time = datetime.now() - timedelta(hours=self.time_window_hours)
        recent_articles = []
        
        for article in articles:
            article_time = self._parse_article_date(article)
            if article_time and article_time >= cutoff_time:
                recent_articles.append(article)
        
        source_counts = Counter()
        for article in recent_articles:
            source = article.get('source')
            if source:
                source_counts[source] += 1
        
        trending_sources = []
        for source, count in source_counts.most_common(10):
            trending_sources.append({
                'source': source,
                'article_count': count,
                'activity_score': count / len(recent_articles) if recent_articles else 0
            })
        
        return trending_sources
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract meaningful keywords from text"""
        if not text:
            return []
        
        # Simple keyword extraction
        words = re.findall(r'\b[A-Z][a-zA-Z]{2,}\b', text)  # Capitalized words
        words.extend(re.findall(r'\b[a-zA-Z]{4,}\b', text.lower()))  # Longer words
        
        # Filter out stop words and common terms
        keywords = [word.lower() for word in words if word.lower() not in self.stop_words]
        
        # Remove duplicates while preserving order
        seen = set()
        unique_keywords = []
        for keyword in keywords:
            if keyword not in seen:
                seen.add(keyword)
                unique_keywords.append(keyword)
        
        return unique_keywords[:10]  # Top 10 keywords per article
    
    def _parse_article_date(self, article: Dict[str, Any]) -> Optional[datetime]:
        """Parse article date from various possible fields"""
        date_fields = ['timestamp', 'published_at', 'date', 'created_at']
        
        for field in date_fields:
            if field in article and article[field]:
                try:
                    if isinstance(article[field], datetime):
                        return article[field]
                    elif isinstance(article[field], str):
                        # Try common date formats
                        for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%Y-%m-%dT%H:%M:%S']:
                            try:
                                return datetime.strptime(article[field], fmt)
                            except ValueError:
                                continue
                except:
                    continue
        
        return None


class ContentEnhancer:
    """Main content enhancement class that combines various analysis tools"""
    
    def __init__(self):
        self.sentiment_analyzer = SentimentAnalyzer()
        self.trending_detector = TrendingDetector()
    
    def enhance_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Enhance articles with sentiment analysis and other metadata
        
        Args:
            articles: List of articles to enhance
            
        Returns:
            Enhanced articles with additional metadata
        """
        enhanced_articles = []
        
        for article in articles:
            enhanced_article = article.copy()
            
            # Add sentiment analysis
            text_for_analysis = f"{article.get('title', '')} {article.get('summary', '')}"
            sentiment_result = self.sentiment_analyzer.analyze_sentiment(text_for_analysis)
            
            enhanced_article.update({
                'sentiment': sentiment_result['sentiment'],
                'sentiment_confidence': sentiment_result['confidence'],
                'sentiment_scores': {
                    'positive': sentiment_result['positive_score'],
                    'negative': sentiment_result['negative_score'],
                    'neutral': sentiment_result['neutral_score']
                }
            })
            
            # Add reading time estimate (assuming 200 words per minute)
            content_length = len(article.get('summary', '') + article.get('full_text', ''))
            reading_time = max(1, content_length // 1000)  # Rough estimate
            enhanced_article['estimated_reading_time'] = reading_time
            
            # Add content quality score
            enhanced_article['content_quality_score'] = self._calculate_content_quality(article)
            
            enhanced_articles.append(enhanced_article)
        
        return enhanced_articles
    
    def get_trending_analysis(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get comprehensive trending analysis
        
        Args:
            articles: List of articles to analyze
            
        Returns:
            Dictionary with trending topics, sources, and sentiment trends
        """
        trending_topics = self.trending_detector.detect_trending_topics(articles)
        trending_sources = self.trending_detector.detect_trending_sources(articles)
        
        # Analyze sentiment trends
        sentiment_trends = self._analyze_sentiment_trends(articles)
        
        return {
            'trending_topics': trending_topics,
            'trending_sources': trending_sources,
            'sentiment_trends': sentiment_trends,
            'analysis_timestamp': datetime.now().isoformat()
        }
    
    def _calculate_content_quality(self, article: Dict[str, Any]) -> float:
        """Calculate a content quality score based on various factors"""
        score = 0.5  # Base score
        
        # Title quality
        title = article.get('title', '')
        if title:
            if len(title) > 20:
                score += 0.1
            if not title.isupper():  # Not all caps
                score += 0.1
        
        # Summary quality
        summary = article.get('summary', '')
        if summary:
            if len(summary) > 50:
                score += 0.1
            if len(summary) < 500:  # Not too long
                score += 0.1
        
        # Source credibility (simple heuristic)
        source = article.get('source', '')
        if source:
            # Prefer sources with domain names
            if '.' in source:
                score += 0.1
        
        # Has link
        if article.get('link'):
            score += 0.1
        
        return min(1.0, score)
    
    def _analyze_sentiment_trends(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze sentiment trends over time"""
        cutoff_time = datetime.now() - timedelta(hours=24)
        recent_articles = []
        
        for article in articles:
            article_time = self.trending_detector._parse_article_date(article)
            if article_time and article_time >= cutoff_time:
                recent_articles.append(article)
        
        if not recent_articles:
            return {
                'overall_sentiment': 'neutral',
                'positive_percentage': 33.3,
                'negative_percentage': 33.3,
                'neutral_percentage': 33.3
            }
        
        sentiment_counts = Counter()
        for article in recent_articles:
            sentiment = article.get('sentiment', 'neutral')
            sentiment_counts[sentiment] += 1
        
        total = len(recent_articles)
        return {
            'overall_sentiment': sentiment_counts.most_common(1)[0][0] if sentiment_counts else 'neutral',
            'positive_percentage': (sentiment_counts['positive'] / total) * 100,
            'negative_percentage': (sentiment_counts['negative'] / total) * 100,
            'neutral_percentage': (sentiment_counts['neutral'] / total) * 100,
            'total_articles': total
        }
