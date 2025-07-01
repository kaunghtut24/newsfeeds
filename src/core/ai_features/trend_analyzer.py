"""
Trend Analysis & Prediction System
==================================

Advanced system for detecting emerging topics, analyzing sentiment trends,
scoring source reliability, and predicting market impact.
"""

import json
import math
import statistics
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from collections import defaultdict, Counter, deque
import logging

logger = logging.getLogger(__name__)

class TrendAnalyzer:
    """
    Advanced trend analysis and prediction system for news content.
    Detects emerging topics, analyzes sentiment trends, and predicts impact.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the trend analyzer."""
        self.config = self._load_config(config_path)
        self.topic_history = defaultdict(deque)
        self.sentiment_history = defaultdict(deque)
        self.source_reliability_scores = defaultdict(float)
        self.market_indicators = self._build_market_indicators()
        self.trend_cache = {}
        
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load trend analysis configuration."""
        default_config = {
            "trend_window_days": 7,
            "emerging_threshold": 0.3,
            "sentiment_trend_threshold": 0.2,
            "reliability_decay_factor": 0.95,
            "market_impact_threshold": 0.6,
            "min_articles_for_trend": 3,
            "max_history_days": 30,
            "trend_weights": {
                "frequency": 0.4,
                "velocity": 0.3,
                "sentiment_momentum": 0.2,
                "source_quality": 0.1
            }
        }
        
        if config_path:
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            except Exception as e:
                logger.warning(f"Could not load config from {config_path}: {e}")
                
        return default_config
    
    def _build_market_indicators(self) -> Dict[str, Dict[str, float]]:
        """Build market impact indicators."""
        return {
            "high_impact_keywords": {
                "earnings": 0.9, "merger": 0.8, "acquisition": 0.8,
                "ipo": 0.9, "bankruptcy": 0.9, "lawsuit": 0.7,
                "regulation": 0.8, "approval": 0.7, "ban": 0.8,
                "partnership": 0.6, "investment": 0.7, "funding": 0.6
            },
            "market_sectors": {
                "technology": 0.8, "finance": 0.9, "healthcare": 0.7,
                "energy": 0.8, "automotive": 0.6, "retail": 0.5,
                "real_estate": 0.6, "telecommunications": 0.6
            },
            "sentiment_multipliers": {
                "positive": 1.2, "negative": 1.5, "neutral": 1.0
            }
        }
    
    def analyze_trends(self, articles: List[Dict], 
                      historical_data: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        Perform comprehensive trend analysis.
        
        Args:
            articles: Current articles to analyze
            historical_data: Historical articles for trend comparison
            
        Returns:
            Dictionary containing trend analysis results
        """
        # Update internal data structures
        self._update_topic_history(articles)
        self._update_sentiment_history(articles)
        self._update_source_reliability(articles)
        
        # Detect emerging topics
        emerging_topics = self._detect_emerging_topics(articles, historical_data)
        
        # Analyze sentiment trends
        sentiment_trends = self._analyze_sentiment_trends(articles)
        
        # Score source reliability
        source_reliability = self._calculate_source_reliability_scores(articles)
        
        # Predict market impact
        market_impact = self._predict_market_impact(articles)
        
        # Detect trending keywords
        trending_keywords = self._detect_trending_keywords(articles)
        
        # Calculate trend momentum
        trend_momentum = self._calculate_trend_momentum(articles)
        
        return {
            "emerging_topics": emerging_topics,
            "sentiment_trends": sentiment_trends,
            "source_reliability": source_reliability,
            "market_impact_predictions": market_impact,
            "trending_keywords": trending_keywords,
            "trend_momentum": trend_momentum,
            "metadata": {
                "analyzed_at": datetime.now().isoformat(),
                "articles_analyzed": len(articles),
                "trend_window_days": self.config["trend_window_days"],
                "method": "trend_analyzer_v1"
            }
        }
    
    def _update_topic_history(self, articles: List[Dict]):
        """Update topic frequency history."""
        current_time = datetime.now()
        
        # Count topics in current articles
        topic_counts = Counter()
        for article in articles:
            if article.get('smart_categorization', {}).get('topics'):
                for topic_info in article['smart_categorization']['topics']:
                    topic = topic_info['topic']
                    confidence = topic_info['confidence']
                    topic_counts[topic] += confidence
        
        # Update history with timestamp
        for topic, count in topic_counts.items():
            self.topic_history[topic].append({
                'timestamp': current_time,
                'count': count,
                'articles': len([a for a in articles 
                               if any(t['topic'] == topic 
                                     for t in a.get('smart_categorization', {}).get('topics', []))])
            })
            
            # Keep only recent history
            max_age = timedelta(days=self.config["max_history_days"])
            while (self.topic_history[topic] and 
                   current_time - self.topic_history[topic][0]['timestamp'] > max_age):
                self.topic_history[topic].popleft()
    
    def _update_sentiment_history(self, articles: List[Dict]):
        """Update sentiment trend history."""
        current_time = datetime.now()
        
        # Calculate sentiment distribution
        sentiment_counts = Counter()
        sentiment_scores = defaultdict(list)
        
        for article in articles:
            sentiment_data = article.get('sentiment_analysis', {})
            overall_sentiment = sentiment_data.get('overall_sentiment')
            compound_score = sentiment_data.get('sentiment_scores', {}).get('compound', 0)
            
            if overall_sentiment:
                sentiment_counts[overall_sentiment] += 1
                sentiment_scores[overall_sentiment].append(compound_score)
        
        # Calculate average sentiment scores
        avg_sentiment_scores = {}
        for sentiment, scores in sentiment_scores.items():
            avg_sentiment_scores[sentiment] = statistics.mean(scores) if scores else 0
        
        # Update history
        sentiment_entry = {
            'timestamp': current_time,
            'distribution': dict(sentiment_counts),
            'average_scores': avg_sentiment_scores,
            'total_articles': len(articles)
        }
        
        self.sentiment_history['global'].append(sentiment_entry)
        
        # Keep only recent history
        max_age = timedelta(days=self.config["max_history_days"])
        while (self.sentiment_history['global'] and 
               current_time - self.sentiment_history['global'][0]['timestamp'] > max_age):
            self.sentiment_history['global'].popleft()
    
    def _update_source_reliability(self, articles: List[Dict]):
        """Update source reliability scores."""
        source_metrics = defaultdict(lambda: {'total': 0, 'quality_score': 0})
        
        for article in articles:
            source = article.get('source', 'unknown')
            
            # Calculate quality indicators
            quality_score = 0.0
            
            # Has AI summary
            if article.get('summary'):
                quality_score += 0.2
            
            # Has smart categorization
            if article.get('smart_categorization'):
                quality_score += 0.2
            
            # Has sentiment analysis
            if article.get('sentiment_analysis'):
                quality_score += 0.1
            
            # Content length indicator
            content_length = len(article.get('content', ''))
            if content_length > 500:
                quality_score += 0.2
            elif content_length > 200:
                quality_score += 0.1
            
            # Title quality (not too short, not too long)
            title_length = len(article.get('title', ''))
            if 30 <= title_length <= 100:
                quality_score += 0.1
            
            # Update metrics
            source_metrics[source]['total'] += 1
            source_metrics[source]['quality_score'] += quality_score
        
        # Update reliability scores with decay
        decay_factor = self.config["reliability_decay_factor"]
        for source in self.source_reliability_scores:
            self.source_reliability_scores[source] *= decay_factor
        
        # Add new scores
        for source, metrics in source_metrics.items():
            if metrics['total'] > 0:
                avg_quality = metrics['quality_score'] / metrics['total']
                self.source_reliability_scores[source] += avg_quality
    
    def _detect_emerging_topics(self, articles: List[Dict], 
                               historical_data: Optional[List[Dict]]) -> List[Dict]:
        """Detect emerging topics."""
        emerging_topics = []
        
        # Get current topic frequencies
        current_topics = Counter()
        for article in articles:
            if article.get('smart_categorization', {}).get('topics'):
                for topic_info in article['smart_categorization']['topics']:
                    topic = topic_info['topic']
                    confidence = topic_info['confidence']
                    current_topics[topic] += confidence
        
        # Compare with historical data if available
        historical_topics = Counter()
        if historical_data:
            for article in historical_data:
                if article.get('smart_categorization', {}).get('topics'):
                    for topic_info in article['smart_categorization']['topics']:
                        topic = topic_info['topic']
                        confidence = topic_info['confidence']
                        historical_topics[topic] += confidence
        
        # Calculate emergence scores
        for topic, current_freq in current_topics.items():
            historical_freq = historical_topics.get(topic, 0)
            
            # Calculate growth rate
            if historical_freq > 0:
                growth_rate = (current_freq - historical_freq) / historical_freq
            else:
                growth_rate = float('inf') if current_freq > 0 else 0
            
            # Calculate velocity (frequency in topic history)
            velocity = self._calculate_topic_velocity(topic)
            
            # Calculate emergence score
            emergence_score = min(growth_rate * 0.6 + velocity * 0.4, 1.0)
            
            if emergence_score >= self.config["emerging_threshold"]:
                emerging_topics.append({
                    "topic": topic,
                    "emergence_score": emergence_score,
                    "current_frequency": current_freq,
                    "historical_frequency": historical_freq,
                    "growth_rate": growth_rate,
                    "velocity": velocity,
                    "article_count": len([a for a in articles 
                                        if any(t['topic'] == topic 
                                              for t in a.get('smart_categorization', {}).get('topics', []))])
                })
        
        # Sort by emergence score
        emerging_topics.sort(key=lambda x: x["emergence_score"], reverse=True)
        return emerging_topics[:10]  # Top 10 emerging topics

    def _calculate_topic_velocity(self, topic: str) -> float:
        """Calculate velocity of topic mentions over time."""
        if topic not in self.topic_history or len(self.topic_history[topic]) < 2:
            return 0.0

        history = list(self.topic_history[topic])

        # Calculate rate of change in recent periods
        recent_counts = [entry['count'] for entry in history[-5:]]  # Last 5 periods

        if len(recent_counts) < 2:
            return 0.0

        # Simple velocity calculation
        velocity = (recent_counts[-1] - recent_counts[0]) / len(recent_counts)
        return max(velocity, 0.0)  # Only positive velocity

    def _analyze_sentiment_trends(self, articles: List[Dict]) -> Dict[str, Any]:
        """Analyze sentiment trends over time."""
        if not self.sentiment_history['global']:
            return {"trend": "insufficient_data"}

        history = list(self.sentiment_history['global'])

        if len(history) < 2:
            return {"trend": "insufficient_data"}

        # Calculate sentiment trend
        recent_sentiment = history[-1]['average_scores']
        previous_sentiment = history[-2]['average_scores']

        sentiment_changes = {}
        for sentiment in ['positive', 'negative', 'neutral']:
            current = recent_sentiment.get(sentiment, 0)
            previous = previous_sentiment.get(sentiment, 0)
            change = current - previous
            sentiment_changes[sentiment] = {
                "current_score": current,
                "previous_score": previous,
                "change": change,
                "trend": "increasing" if change > 0.1 else "decreasing" if change < -0.1 else "stable"
            }

        # Overall trend analysis
        positive_trend = sentiment_changes.get('positive', {}).get('change', 0)
        negative_trend = sentiment_changes.get('negative', {}).get('change', 0)

        overall_trend = "improving" if positive_trend > 0.1 else "declining" if negative_trend > 0.1 else "stable"

        return {
            "overall_trend": overall_trend,
            "sentiment_changes": sentiment_changes,
            "trend_strength": abs(positive_trend - negative_trend),
            "analysis_period": f"{len(history)} periods"
        }

    def _calculate_source_reliability_scores(self, articles: List[Dict]) -> Dict[str, Dict]:
        """Calculate and return source reliability scores."""
        source_scores = {}

        for source, score in self.source_reliability_scores.items():
            # Normalize score to 0-1 range
            normalized_score = min(score / 5.0, 1.0)  # Assuming max score of 5

            # Calculate article count for this source
            article_count = len([a for a in articles if a.get('source') == source])

            # Calculate reliability tier
            if normalized_score >= 0.8:
                tier = "high"
            elif normalized_score >= 0.6:
                tier = "medium"
            elif normalized_score >= 0.4:
                tier = "low"
            else:
                tier = "very_low"

            source_scores[source] = {
                "reliability_score": normalized_score,
                "tier": tier,
                "article_count": article_count,
                "raw_score": score
            }

        return source_scores

    def _predict_market_impact(self, articles: List[Dict]) -> List[Dict]:
        """Predict potential market impact of articles."""
        market_predictions = []

        for article in articles:
            impact_score = 0.0
            impact_factors = []

            # Check for high-impact keywords
            text = (article.get('title', '') + ' ' +
                   article.get('summary', '') + ' ' +
                   article.get('description', '')).lower()

            for keyword, weight in self.market_indicators["high_impact_keywords"].items():
                if keyword in text:
                    impact_score += weight * 0.3
                    impact_factors.append(f"keyword: {keyword}")

            # Check industry/sector impact
            if article.get('smart_categorization', {}).get('industries'):
                for industry_info in article['smart_categorization']['industries']:
                    industry = industry_info['industry']
                    confidence = industry_info['confidence']
                    sector_weight = self.market_indicators["market_sectors"].get(industry, 0.5)
                    impact_score += sector_weight * confidence * 0.4
                    impact_factors.append(f"industry: {industry}")

            # Sentiment multiplier
            sentiment = article.get('sentiment_analysis', {}).get('overall_sentiment', 'neutral')
            sentiment_multiplier = self.market_indicators["sentiment_multipliers"].get(sentiment, 1.0)
            impact_score *= sentiment_multiplier

            # Source reliability factor
            source = article.get('source', '')
            source_reliability = self.source_reliability_scores.get(source, 0.5)
            impact_score *= (0.5 + source_reliability * 0.5)  # 0.5 to 1.0 multiplier

            # Event type boost
            if article.get('smart_categorization', {}).get('events'):
                for event_info in article['smart_categorization']['events']:
                    event_type = event_info['event_type']
                    if event_type in ['earnings_report', 'merger_acquisition', 'ipo']:
                        impact_score += 0.2
                        impact_factors.append(f"event: {event_type}")

            # Only include articles with significant predicted impact
            if impact_score >= self.config["market_impact_threshold"]:
                # Classify impact level
                if impact_score >= 0.9:
                    impact_level = "very_high"
                elif impact_score >= 0.8:
                    impact_level = "high"
                elif impact_score >= 0.7:
                    impact_level = "medium"
                else:
                    impact_level = "low"

                market_predictions.append({
                    "article": {
                        "id": article.get('id'),
                        "title": article.get('title'),
                        "source": article.get('source')
                    },
                    "impact_score": impact_score,
                    "impact_level": impact_level,
                    "impact_factors": impact_factors,
                    "predicted_sectors": self._get_affected_sectors(article),
                    "confidence": min(impact_score, 1.0)
                })

        # Sort by impact score
        market_predictions.sort(key=lambda x: x["impact_score"], reverse=True)
        return market_predictions[:20]  # Top 20 predictions

    def _get_affected_sectors(self, article: Dict) -> List[str]:
        """Get sectors likely to be affected by the article."""
        sectors = []

        if article.get('smart_categorization', {}).get('industries'):
            for industry_info in article['smart_categorization']['industries']:
                sectors.append(industry_info['industry'])

        # Add related sectors based on content
        text = article.get('title', '').lower()
        if 'tech' in text or 'ai' in text:
            sectors.append('technology')
        if 'bank' in text or 'finance' in text:
            sectors.append('finance')
        if 'health' in text or 'medical' in text:
            sectors.append('healthcare')

        return list(set(sectors))

    def _detect_trending_keywords(self, articles: List[Dict]) -> List[Dict]:
        """Detect trending keywords across articles."""
        keyword_counts = Counter()
        keyword_articles = defaultdict(list)

        # Extract keywords from titles and summaries
        for article in articles:
            text = (article.get('title', '') + ' ' +
                   article.get('summary', '')).lower()

            # Simple keyword extraction (in practice, use NLP libraries)
            words = text.split()
            for word in words:
                if len(word) > 3 and word.isalpha():
                    keyword_counts[word] += 1
                    keyword_articles[word].append(article.get('id', ''))

        # Calculate trending scores
        trending_keywords = []
        for keyword, count in keyword_counts.most_common(50):
            if count >= self.config["min_articles_for_trend"]:
                # Calculate trend score based on frequency and recency
                trend_score = count / len(articles)

                trending_keywords.append({
                    "keyword": keyword,
                    "frequency": count,
                    "trend_score": trend_score,
                    "article_count": count,
                    "articles": keyword_articles[keyword][:5]  # Sample articles
                })

        return trending_keywords[:20]  # Top 20 trending keywords

    def _calculate_trend_momentum(self, articles: List[Dict]) -> Dict[str, float]:
        """Calculate overall trend momentum metrics."""
        momentum = {}

        # Topic momentum
        topic_momentum = 0.0
        if self.topic_history:
            for topic, history in self.topic_history.items():
                if len(history) >= 2:
                    recent_avg = statistics.mean([h['count'] for h in list(history)[-3:]])
                    older_avg = statistics.mean([h['count'] for h in list(history)[-6:-3]]) if len(history) >= 6 else 0
                    if older_avg > 0:
                        topic_momentum += (recent_avg - older_avg) / older_avg

        momentum['topic_momentum'] = topic_momentum / len(self.topic_history) if self.topic_history else 0

        # Sentiment momentum
        sentiment_momentum = 0.0
        if len(self.sentiment_history['global']) >= 2:
            recent = self.sentiment_history['global'][-1]['average_scores']
            previous = self.sentiment_history['global'][-2]['average_scores']

            for sentiment in ['positive', 'negative']:
                current = recent.get(sentiment, 0)
                prev = previous.get(sentiment, 0)
                if prev != 0:
                    sentiment_momentum += (current - prev) / abs(prev)

        momentum['sentiment_momentum'] = sentiment_momentum

        # Overall momentum
        momentum['overall_momentum'] = (momentum['topic_momentum'] + momentum['sentiment_momentum']) / 2

        return momentum
