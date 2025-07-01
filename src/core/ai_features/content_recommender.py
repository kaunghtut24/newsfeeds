"""
Content Recommender System
==========================

Intelligent content recommendation system that learns user preferences
and provides personalized article suggestions.
"""

import json
import math
from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import logging

logger = logging.getLogger(__name__)

class ContentRecommender:
    """
    Intelligent content recommendation system using collaborative filtering
    and content-based approaches.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the content recommender."""
        self.config = self._load_config(config_path)
        self.user_profiles = {}
        self.article_features = {}
        self.interaction_history = defaultdict(list)
        self.similarity_cache = {}
        
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load recommendation configuration."""
        default_config = {
            "max_recommendations": 10,
            "similarity_threshold": 0.3,
            "recency_weight": 0.3,
            "popularity_weight": 0.2,
            "personalization_weight": 0.5,
            "min_interactions_for_personalization": 5,
            "feature_weights": {
                "topics": 0.4,
                "sentiment": 0.2,
                "source": 0.2,
                "category": 0.2
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
    
    def track_interaction(self, user_id: str, article_id: str, 
                         interaction_type: str, article_data: Dict):
        """
        Track user interaction with an article.
        
        Args:
            user_id: User identifier
            article_id: Article identifier
            interaction_type: Type of interaction (view, like, share, etc.)
            article_data: Article metadata
        """
        interaction = {
            "article_id": article_id,
            "interaction_type": interaction_type,
            "timestamp": datetime.now().isoformat(),
            "article_data": article_data
        }
        
        self.interaction_history[user_id].append(interaction)
        self._update_user_profile(user_id, article_data, interaction_type)
        self._update_article_features(article_id, article_data)
    
    def get_recommendations(self, user_id: str, articles: List[Dict], 
                          exclude_ids: Optional[Set[str]] = None) -> List[Dict]:
        """
        Get personalized recommendations for a user.
        
        Args:
            user_id: User identifier
            articles: Available articles to recommend from
            exclude_ids: Article IDs to exclude from recommendations
            
        Returns:
            List of recommended articles with scores
        """
        if exclude_ids is None:
            exclude_ids = set()
            
        # Filter out excluded articles
        candidate_articles = [
            article for article in articles 
            if article.get('id') not in exclude_ids
        ]
        
        if not candidate_articles:
            return []
        
        # Get user profile
        user_profile = self.user_profiles.get(user_id, {})
        
        # Calculate recommendation scores
        recommendations = []
        for article in candidate_articles:
            score = self._calculate_recommendation_score(user_profile, article)
            
            recommendations.append({
                "article": article,
                "score": score,
                "reasons": self._get_recommendation_reasons(user_profile, article)
            })
        
        # Sort by score and return top recommendations
        recommendations.sort(key=lambda x: x["score"], reverse=True)
        return recommendations[:self.config["max_recommendations"]]
    
    def get_similar_articles(self, article: Dict, articles: List[Dict], 
                           limit: Optional[int] = None) -> List[Dict]:
        """
        Find articles similar to a given article.
        
        Args:
            article: Reference article
            articles: Pool of articles to search
            limit: Maximum number of similar articles to return
            
        Returns:
            List of similar articles with similarity scores
        """
        if limit is None:
            limit = self.config["max_recommendations"]
            
        article_id = article.get('id', '')
        similar_articles = []
        
        for candidate in articles:
            candidate_id = candidate.get('id', '')
            if candidate_id == article_id:
                continue
                
            similarity = self._calculate_article_similarity(article, candidate)
            
            if similarity >= self.config["similarity_threshold"]:
                similar_articles.append({
                    "article": candidate,
                    "similarity": similarity,
                    "common_features": self._get_common_features(article, candidate)
                })
        
        similar_articles.sort(key=lambda x: x["similarity"], reverse=True)
        return similar_articles[:limit]
    
    def get_trending_for_user(self, user_id: str, articles: List[Dict]) -> List[Dict]:
        """
        Get trending articles personalized for a specific user.
        
        Args:
            user_id: User identifier
            articles: Available articles
            
        Returns:
            List of trending articles relevant to the user
        """
        user_profile = self.user_profiles.get(user_id, {})
        
        # Calculate trending scores with personalization
        trending_articles = []
        for article in articles:
            base_score = self._calculate_trending_score(article)
            personalization_boost = self._calculate_personalization_boost(user_profile, article)
            
            final_score = base_score + personalization_boost
            
            trending_articles.append({
                "article": article,
                "trending_score": final_score,
                "base_score": base_score,
                "personalization_boost": personalization_boost
            })
        
        trending_articles.sort(key=lambda x: x["trending_score"], reverse=True)
        return trending_articles[:self.config["max_recommendations"]]
    
    def _update_user_profile(self, user_id: str, article_data: Dict, interaction_type: str):
        """Update user profile based on interaction."""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = {
                "topics": defaultdict(float),
                "sources": defaultdict(float),
                "categories": defaultdict(float),
                "sentiment_preference": defaultdict(float),
                "interaction_counts": defaultdict(int),
                "last_updated": datetime.now().isoformat()
            }
        
        profile = self.user_profiles[user_id]
        
        # Weight different interaction types
        interaction_weights = {
            "view": 1.0,
            "like": 2.0,
            "share": 3.0,
            "comment": 2.5,
            "bookmark": 2.0
        }
        
        weight = interaction_weights.get(interaction_type, 1.0)
        
        # Update topic preferences
        if "smart_categorization" in article_data:
            topics = article_data["smart_categorization"].get("topics", [])
            for topic_info in topics:
                topic = topic_info.get("topic", "")
                confidence = topic_info.get("confidence", 0)
                profile["topics"][topic] += weight * confidence
        
        # Update source preferences
        source = article_data.get("source", "")
        if source:
            profile["sources"][source] += weight
        
        # Update category preferences
        category = article_data.get("category", "")
        if category:
            profile["categories"][category] += weight
        
        # Update sentiment preferences
        if "sentiment_analysis" in article_data:
            sentiment = article_data["sentiment_analysis"].get("overall_sentiment", "")
            if sentiment:
                profile["sentiment_preference"][sentiment] += weight
        
        profile["interaction_counts"][interaction_type] += 1
        profile["last_updated"] = datetime.now().isoformat()
    
    def _update_article_features(self, article_id: str, article_data: Dict):
        """Update article feature cache."""
        features = {
            "topics": [],
            "sentiment": "",
            "source": article_data.get("source", ""),
            "category": article_data.get("category", ""),
            "published_date": article_data.get("published_date", ""),
            "popularity_score": 0.0
        }
        
        # Extract topics
        if "smart_categorization" in article_data:
            topics = article_data["smart_categorization"].get("topics", [])
            features["topics"] = [topic["topic"] for topic in topics]
        
        # Extract sentiment
        if "sentiment_analysis" in article_data:
            features["sentiment"] = article_data["sentiment_analysis"].get("overall_sentiment", "")
        
        self.article_features[article_id] = features

    def _calculate_recommendation_score(self, user_profile: Dict, article: Dict) -> float:
        """Calculate recommendation score for an article."""
        if not user_profile:
            # No user profile, use popularity-based scoring
            return self._calculate_popularity_score(article)

        score = 0.0
        weights = self.config["feature_weights"]

        # Topic similarity
        if "topics" in user_profile and article.get("smart_categorization", {}).get("topics"):
            topic_score = self._calculate_topic_similarity(user_profile, article)
            score += topic_score * weights["topics"]

        # Source preference
        if "sources" in user_profile:
            source_score = self._calculate_source_preference(user_profile, article)
            score += source_score * weights["source"]

        # Category preference
        if "categories" in user_profile:
            category_score = self._calculate_category_preference(user_profile, article)
            score += category_score * weights["category"]

        # Sentiment preference
        if "sentiment_preference" in user_profile and article.get("sentiment_analysis"):
            sentiment_score = self._calculate_sentiment_preference(user_profile, article)
            score += sentiment_score * weights["sentiment"]

        # Apply recency and popularity weights
        recency_score = self._calculate_recency_score(article)
        popularity_score = self._calculate_popularity_score(article)

        final_score = (
            score * self.config["personalization_weight"] +
            recency_score * self.config["recency_weight"] +
            popularity_score * self.config["popularity_weight"]
        )

        return final_score

    def _calculate_topic_similarity(self, user_profile: Dict, article: Dict) -> float:
        """Calculate topic similarity score."""
        user_topics = user_profile.get("topics", {})
        article_topics = article.get("smart_categorization", {}).get("topics", [])

        if not user_topics or not article_topics:
            return 0.0

        similarity = 0.0
        for topic_info in article_topics:
            topic = topic_info.get("topic", "")
            confidence = topic_info.get("confidence", 0)
            user_preference = user_topics.get(topic, 0)

            similarity += confidence * user_preference

        return min(similarity / len(article_topics), 1.0)

    def _calculate_source_preference(self, user_profile: Dict, article: Dict) -> float:
        """Calculate source preference score."""
        user_sources = user_profile.get("sources", {})
        article_source = article.get("source", "")

        if not user_sources or not article_source:
            return 0.0

        max_preference = max(user_sources.values()) if user_sources else 1
        source_preference = user_sources.get(article_source, 0)

        return source_preference / max_preference if max_preference > 0 else 0

    def _calculate_category_preference(self, user_profile: Dict, article: Dict) -> float:
        """Calculate category preference score."""
        user_categories = user_profile.get("categories", {})
        article_category = article.get("category", "")

        if not user_categories or not article_category:
            return 0.0

        max_preference = max(user_categories.values()) if user_categories else 1
        category_preference = user_categories.get(article_category, 0)

        return category_preference / max_preference if max_preference > 0 else 0

    def _calculate_sentiment_preference(self, user_profile: Dict, article: Dict) -> float:
        """Calculate sentiment preference score."""
        user_sentiments = user_profile.get("sentiment_preference", {})
        article_sentiment = article.get("sentiment_analysis", {}).get("overall_sentiment", "")

        if not user_sentiments or not article_sentiment:
            return 0.0

        max_preference = max(user_sentiments.values()) if user_sentiments else 1
        sentiment_preference = user_sentiments.get(article_sentiment, 0)

        return sentiment_preference / max_preference if max_preference > 0 else 0

    def _calculate_recency_score(self, article: Dict) -> float:
        """Calculate recency score based on publication date."""
        # Simple recency scoring - newer articles get higher scores
        # In a real implementation, you'd parse the published_date
        return 0.5  # Placeholder

    def _calculate_popularity_score(self, article: Dict) -> float:
        """Calculate popularity score."""
        # Simple popularity scoring based on article features
        score = 0.0

        # Boost for articles with AI summaries
        if article.get("summary"):
            score += 0.3

        # Boost for articles with smart categorization
        if article.get("smart_categorization"):
            score += 0.2

        # Boost for articles with sentiment analysis
        if article.get("sentiment_analysis"):
            score += 0.2

        return min(score, 1.0)

    def _get_recommendation_reasons(self, user_profile: Dict, article: Dict) -> List[str]:
        """Get reasons for recommendation."""
        reasons = []

        if not user_profile:
            reasons.append("Popular article")
            return reasons

        # Check topic matches
        user_topics = user_profile.get("topics", {})
        article_topics = article.get("smart_categorization", {}).get("topics", [])

        for topic_info in article_topics:
            topic = topic_info.get("topic", "")
            if topic in user_topics and user_topics[topic] > 0:
                reasons.append(f"Matches your interest in {topic}")

        # Check source preference
        user_sources = user_profile.get("sources", {})
        article_source = article.get("source", "")
        if article_source in user_sources and user_sources[article_source] > 0:
            reasons.append(f"From your preferred source: {article_source}")

        # Check category preference
        user_categories = user_profile.get("categories", {})
        article_category = article.get("category", "")
        if article_category in user_categories and user_categories[article_category] > 0:
            reasons.append(f"Matches your interest in {article_category}")

        if not reasons:
            reasons.append("Trending article")

        return reasons[:3]  # Limit to top 3 reasons

    def _calculate_article_similarity(self, article1: Dict, article2: Dict) -> float:
        """Calculate similarity between two articles."""
        similarity = 0.0

        # Topic similarity
        topics1 = set()
        topics2 = set()

        if article1.get("smart_categorization", {}).get("topics"):
            topics1 = {t["topic"] for t in article1["smart_categorization"]["topics"]}

        if article2.get("smart_categorization", {}).get("topics"):
            topics2 = {t["topic"] for t in article2["smart_categorization"]["topics"]}

        if topics1 and topics2:
            topic_similarity = len(topics1.intersection(topics2)) / len(topics1.union(topics2))
            similarity += topic_similarity * 0.4

        # Source similarity
        if article1.get("source") == article2.get("source"):
            similarity += 0.2

        # Category similarity
        if article1.get("category") == article2.get("category"):
            similarity += 0.2

        # Sentiment similarity
        sentiment1 = article1.get("sentiment_analysis", {}).get("overall_sentiment")
        sentiment2 = article2.get("sentiment_analysis", {}).get("overall_sentiment")
        if sentiment1 and sentiment2 and sentiment1 == sentiment2:
            similarity += 0.2

        return similarity

    def _get_common_features(self, article1: Dict, article2: Dict) -> List[str]:
        """Get common features between two articles."""
        features = []

        # Common topics
        topics1 = set()
        topics2 = set()

        if article1.get("smart_categorization", {}).get("topics"):
            topics1 = {t["topic"] for t in article1["smart_categorization"]["topics"]}

        if article2.get("smart_categorization", {}).get("topics"):
            topics2 = {t["topic"] for t in article2["smart_categorization"]["topics"]}

        common_topics = topics1.intersection(topics2)
        if common_topics:
            features.extend([f"Topic: {topic}" for topic in common_topics])

        # Common source
        if article1.get("source") == article2.get("source"):
            features.append(f"Source: {article1.get('source')}")

        # Common category
        if article1.get("category") == article2.get("category"):
            features.append(f"Category: {article1.get('category')}")

        return features

    def _calculate_trending_score(self, article: Dict) -> float:
        """Calculate trending score for an article."""
        score = 0.0

        # Boost for recent articles
        score += 0.3

        # Boost for articles with high engagement potential
        if article.get("smart_categorization", {}).get("topics"):
            # More topics = potentially more interesting
            num_topics = len(article["smart_categorization"]["topics"])
            score += min(num_topics * 0.1, 0.3)

        # Boost for articles with strong sentiment
        if article.get("sentiment_analysis"):
            compound = abs(article["sentiment_analysis"].get("sentiment_scores", {}).get("compound", 0))
            score += compound * 0.2

        # Boost for articles with events
        if article.get("smart_categorization", {}).get("events"):
            score += 0.2

        return min(score, 1.0)

    def _calculate_personalization_boost(self, user_profile: Dict, article: Dict) -> float:
        """Calculate personalization boost for trending articles."""
        if not user_profile:
            return 0.0

        boost = 0.0

        # Boost based on user's topic interests
        user_topics = user_profile.get("topics", {})
        article_topics = article.get("smart_categorization", {}).get("topics", [])

        for topic_info in article_topics:
            topic = topic_info.get("topic", "")
            if topic in user_topics:
                boost += user_topics[topic] * 0.1

        # Boost based on source preference
        user_sources = user_profile.get("sources", {})
        article_source = article.get("source", "")
        if article_source in user_sources:
            boost += user_sources[article_source] * 0.1

        return min(boost, 0.5)
