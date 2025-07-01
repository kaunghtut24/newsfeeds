"""
Content Relationship Mapper
===========================

Advanced system for mapping relationships between news articles including
story clustering, follow-up detection, contradiction detection, and timeline construction.
"""

import re
import json
import math
from typing import Dict, List, Optional, Set, Tuple, Any
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from difflib import SequenceMatcher
import logging

logger = logging.getLogger(__name__)

class ContentRelationshipMapper:
    """
    Advanced content relationship mapping system for news articles.
    Identifies related stories, follow-ups, contradictions, and builds timelines.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the content relationship mapper."""
        self.config = self._load_config(config_path)
        self.entity_patterns = self._build_entity_patterns()
        self.contradiction_indicators = self._build_contradiction_indicators()
        self.follow_up_indicators = self._build_follow_up_indicators()
        self.story_clusters = {}
        self.article_relationships = defaultdict(list)
        
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load relationship mapping configuration."""
        default_config = {
            "similarity_threshold": 0.7,
            "entity_match_threshold": 0.6,
            "time_window_hours": 168,  # 1 week
            "max_cluster_size": 20,
            "contradiction_threshold": 0.8,
            "follow_up_threshold": 0.7,
            "entity_weights": {
                "companies": 0.4,
                "people": 0.3,
                "locations": 0.2,
                "topics": 0.1
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
    
    def _build_entity_patterns(self) -> Dict[str, List[str]]:
        """Build entity extraction patterns."""
        return {
            "companies": [
                r"\b[A-Z][a-z]+ (?:Inc|Corp|Ltd|LLC|Co|Company|Corporation)\b",
                r"\b(?:Apple|Google|Microsoft|Amazon|Tesla|Meta|Netflix|Uber|Airbnb)\b",
                r"\b[A-Z]{2,5}\b(?=\s+(?:stock|shares|trading))"
            ],
            "people": [
                r"\b(?:CEO|CTO|CFO|President|Chairman|Director)\s+[A-Z][a-z]+\s+[A-Z][a-z]+\b",
                r"\b[A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+said|\s+announced|\s+stated)\b"
            ],
            "locations": [
                r"\b(?:New York|California|Texas|London|Tokyo|Beijing|Mumbai|Singapore)\b",
                r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*,\s+[A-Z]{2}\b"
            ],
            "financial_terms": [
                r"\$\d+(?:\.\d+)?\s*(?:billion|million|thousand|B|M|K)\b",
                r"\b\d+(?:\.\d+)?%\s*(?:increase|decrease|growth|decline)\b"
            ]
        }
    
    def _build_contradiction_indicators(self) -> List[str]:
        """Build contradiction detection indicators."""
        return [
            "however", "but", "nevertheless", "on the contrary", "in contrast",
            "despite", "although", "while", "whereas", "contradicts",
            "denies", "refutes", "disputes", "challenges", "opposes",
            "disagrees", "conflicts with", "contrary to", "unlike"
        ]
    
    def _build_follow_up_indicators(self) -> List[str]:
        """Build follow-up detection indicators."""
        return [
            "following", "after", "subsequently", "later", "then", "next",
            "update", "development", "progress", "continuation", "sequel",
            "follow-up", "additional", "further", "more", "also", "moreover",
            "furthermore", "in addition", "building on", "expanding on"
        ]
    
    def analyze_relationships(self, articles: List[Dict]) -> Dict[str, Any]:
        """
        Analyze relationships between articles.
        
        Args:
            articles: List of articles to analyze
            
        Returns:
            Dictionary containing relationship analysis results
        """
        # Extract entities from all articles
        article_entities = {}
        for article in articles:
            article_id = article.get('id', str(hash(article.get('title', ''))))
            article['id'] = article_id
            article_entities[article_id] = self._extract_entities(article)
        
        # Find story clusters
        clusters = self._cluster_stories(articles, article_entities)
        
        # Detect follow-ups
        follow_ups = self._detect_follow_ups(articles, article_entities)
        
        # Detect contradictions
        contradictions = self._detect_contradictions(articles, article_entities)
        
        # Build timelines
        timelines = self._build_timelines(articles, clusters)
        
        # Calculate relationship scores
        relationship_matrix = self._calculate_relationship_matrix(articles, article_entities)
        
        return {
            "story_clusters": clusters,
            "follow_ups": follow_ups,
            "contradictions": contradictions,
            "timelines": timelines,
            "relationship_matrix": relationship_matrix,
            "entity_analysis": article_entities,
            "metadata": {
                "processed_at": datetime.now().isoformat(),
                "total_articles": len(articles),
                "total_clusters": len(clusters),
                "total_follow_ups": len(follow_ups),
                "total_contradictions": len(contradictions),
                "method": "content_relationship_mapper_v1"
            }
        }
    
    def _extract_entities(self, article: Dict) -> Dict[str, List[str]]:
        """Extract entities from an article."""
        text = self._get_article_text(article)
        entities = {}
        
        for entity_type, patterns in self.entity_patterns.items():
            found_entities = []
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                found_entities.extend(matches)
            
            # Clean and deduplicate entities
            entities[entity_type] = list(set([
                entity.strip() for entity in found_entities 
                if len(entity.strip()) > 2
            ]))
        
        # Extract topics from smart categorization if available
        if article.get('smart_categorization', {}).get('topics'):
            topics = [topic['topic'] for topic in article['smart_categorization']['topics']]
            entities['topics'] = topics
        
        return entities
    
    def _get_article_text(self, article: Dict) -> str:
        """Get combined text from article."""
        text_parts = []
        
        if article.get('title'):
            text_parts.append(article['title'])
        if article.get('summary'):
            text_parts.append(article['summary'])
        elif article.get('description'):
            text_parts.append(article['description'])
        if article.get('content'):
            text_parts.append(article['content'][:1000])  # Limit content
        
        return ' '.join(text_parts)
    
    def _cluster_stories(self, articles: List[Dict], 
                        article_entities: Dict[str, Dict]) -> List[Dict]:
        """Cluster related stories together."""
        clusters = []
        processed_articles = set()
        
        for article in articles:
            article_id = article['id']
            
            if article_id in processed_articles:
                continue
            
            # Start new cluster
            cluster = {
                "cluster_id": f"cluster_{len(clusters)}",
                "articles": [article],
                "common_entities": article_entities[article_id].copy(),
                "cluster_score": 1.0,
                "created_at": datetime.now().isoformat()
            }
            
            processed_articles.add(article_id)
            
            # Find related articles
            for other_article in articles:
                other_id = other_article['id']
                
                if other_id in processed_articles:
                    continue
                
                similarity = self._calculate_entity_similarity(
                    article_entities[article_id],
                    article_entities[other_id]
                )
                
                if similarity >= self.config["similarity_threshold"]:
                    cluster["articles"].append(other_article)
                    processed_articles.add(other_id)
                    
                    # Update common entities
                    cluster["common_entities"] = self._merge_common_entities(
                        cluster["common_entities"],
                        article_entities[other_id]
                    )
                    
                    # Stop if cluster gets too large
                    if len(cluster["articles"]) >= self.config["max_cluster_size"]:
                        break
            
            # Only keep clusters with multiple articles
            if len(cluster["articles"]) > 1:
                cluster["cluster_score"] = self._calculate_cluster_score(cluster)
                clusters.append(cluster)
        
        return clusters

    def _calculate_entity_similarity(self, entities1: Dict[str, List],
                                   entities2: Dict[str, List]) -> float:
        """Calculate similarity between two entity sets."""
        total_similarity = 0.0
        weights = self.config["entity_weights"]

        for entity_type, weight in weights.items():
            if entity_type in entities1 and entity_type in entities2:
                set1 = set(entities1[entity_type])
                set2 = set(entities2[entity_type])

                if set1 and set2:
                    intersection = len(set1.intersection(set2))
                    union = len(set1.union(set2))
                    jaccard_similarity = intersection / union if union > 0 else 0
                    total_similarity += jaccard_similarity * weight

        return total_similarity

    def _merge_common_entities(self, entities1: Dict[str, List],
                             entities2: Dict[str, List]) -> Dict[str, List]:
        """Merge common entities between two entity sets."""
        common = {}

        for entity_type in entities1:
            if entity_type in entities2:
                set1 = set(entities1[entity_type])
                set2 = set(entities2[entity_type])
                common[entity_type] = list(set1.intersection(set2))

        return common

    def _calculate_cluster_score(self, cluster: Dict) -> float:
        """Calculate quality score for a cluster."""
        num_articles = len(cluster["articles"])

        # Base score from number of articles
        base_score = min(num_articles / 5.0, 1.0)

        # Boost for common entities
        entity_boost = 0.0
        for entity_type, entities in cluster["common_entities"].items():
            if entities:
                entity_boost += len(entities) * 0.1

        return min(base_score + entity_boost, 1.0)

    def _detect_follow_ups(self, articles: List[Dict],
                          article_entities: Dict[str, Dict]) -> List[Dict]:
        """Detect follow-up articles."""
        follow_ups = []

        # Sort articles by date (if available)
        sorted_articles = self._sort_articles_by_date(articles)

        for i, article in enumerate(sorted_articles):
            article_id = article['id']
            article_text = self._get_article_text(article).lower()

            # Check for follow-up indicators
            follow_up_score = 0.0
            for indicator in self.follow_up_indicators:
                if indicator in article_text:
                    follow_up_score += 0.1

            if follow_up_score >= self.config["follow_up_threshold"]:
                # Find potential original articles
                for j in range(max(0, i-10), i):  # Look at previous 10 articles
                    original_article = sorted_articles[j]
                    original_id = original_article['id']

                    # Check entity similarity
                    similarity = self._calculate_entity_similarity(
                        article_entities[article_id],
                        article_entities[original_id]
                    )

                    if similarity >= self.config["entity_match_threshold"]:
                        follow_ups.append({
                            "follow_up_article": article,
                            "original_article": original_article,
                            "similarity_score": similarity,
                            "follow_up_score": follow_up_score,
                            "detected_at": datetime.now().isoformat()
                        })
                        break

        return follow_ups

    def _detect_contradictions(self, articles: List[Dict],
                             article_entities: Dict[str, Dict]) -> List[Dict]:
        """Detect contradictory articles."""
        contradictions = []

        for i, article1 in enumerate(articles):
            article1_id = article1['id']
            article1_text = self._get_article_text(article1).lower()

            # Check for contradiction indicators
            contradiction_score = 0.0
            for indicator in self.contradiction_indicators:
                if indicator in article1_text:
                    contradiction_score += 0.1

            if contradiction_score >= self.config["contradiction_threshold"]:
                # Find potentially contradicted articles
                for j, article2 in enumerate(articles[i+1:], i+1):
                    article2_id = article2['id']

                    # Check entity similarity (same topic/entities)
                    similarity = self._calculate_entity_similarity(
                        article_entities[article1_id],
                        article_entities[article2_id]
                    )

                    if similarity >= self.config["entity_match_threshold"]:
                        # Check sentiment contradiction
                        sentiment_contradiction = self._check_sentiment_contradiction(
                            article1, article2
                        )

                        if sentiment_contradiction:
                            contradictions.append({
                                "article1": article1,
                                "article2": article2,
                                "similarity_score": similarity,
                                "contradiction_score": contradiction_score,
                                "sentiment_contradiction": sentiment_contradiction,
                                "detected_at": datetime.now().isoformat()
                            })

        return contradictions

    def _check_sentiment_contradiction(self, article1: Dict, article2: Dict) -> bool:
        """Check if two articles have contradictory sentiments."""
        sentiment1 = article1.get('sentiment_analysis', {}).get('overall_sentiment')
        sentiment2 = article2.get('sentiment_analysis', {}).get('overall_sentiment')

        if sentiment1 and sentiment2:
            contradictory_pairs = [
                ('positive', 'negative'),
                ('negative', 'positive'),
                ('optimistic', 'pessimistic'),
                ('pessimistic', 'optimistic')
            ]

            return (sentiment1, sentiment2) in contradictory_pairs

        return False

    def _build_timelines(self, articles: List[Dict],
                        clusters: List[Dict]) -> List[Dict]:
        """Build timelines for story clusters."""
        timelines = []

        for cluster in clusters:
            cluster_articles = cluster["articles"]

            # Sort articles by date
            sorted_articles = self._sort_articles_by_date(cluster_articles)

            if len(sorted_articles) >= 2:
                timeline = {
                    "timeline_id": f"timeline_{cluster['cluster_id']}",
                    "cluster_id": cluster["cluster_id"],
                    "events": [],
                    "duration_days": 0,
                    "created_at": datetime.now().isoformat()
                }

                # Create timeline events
                for i, article in enumerate(sorted_articles):
                    event = {
                        "event_id": f"event_{i}",
                        "article": article,
                        "sequence_number": i,
                        "event_type": self._classify_event_type(article),
                        "timestamp": article.get('published_date', ''),
                        "summary": article.get('title', '')[:100]
                    }
                    timeline["events"].append(event)

                # Calculate timeline duration
                if len(timeline["events"]) >= 2:
                    timeline["duration_days"] = self._calculate_timeline_duration(
                        timeline["events"]
                    )

                timelines.append(timeline)

        return timelines

    def _sort_articles_by_date(self, articles: List[Dict]) -> List[Dict]:
        """Sort articles by publication date."""
        def get_date_key(article):
            date_str = article.get('published_date', '')
            if date_str:
                try:
                    return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                except:
                    pass
            return datetime.min

        return sorted(articles, key=get_date_key)

    def _classify_event_type(self, article: Dict) -> str:
        """Classify the type of event in an article."""
        if article.get('smart_categorization', {}).get('events'):
            events = article['smart_categorization']['events']
            if events:
                return events[0]['event_type']

        # Fallback classification based on title/content
        title = article.get('title', '').lower()

        if any(word in title for word in ['announce', 'launch', 'unveil']):
            return 'announcement'
        elif any(word in title for word in ['earnings', 'results', 'profit']):
            return 'earnings'
        elif any(word in title for word in ['merger', 'acquisition', 'deal']):
            return 'business_deal'
        else:
            return 'general_news'

    def _calculate_timeline_duration(self, events: List[Dict]) -> int:
        """Calculate duration of timeline in days."""
        if len(events) < 2:
            return 0

        first_date = events[0].get('timestamp', '')
        last_date = events[-1].get('timestamp', '')

        try:
            first_dt = datetime.fromisoformat(first_date.replace('Z', '+00:00'))
            last_dt = datetime.fromisoformat(last_date.replace('Z', '+00:00'))
            return (last_dt - first_dt).days
        except:
            return 0

    def _calculate_relationship_matrix(self, articles: List[Dict],
                                     article_entities: Dict[str, Dict]) -> Dict[str, Dict]:
        """Calculate relationship matrix between all articles."""
        matrix = {}

        for i, article1 in enumerate(articles):
            article1_id = article1['id']
            matrix[article1_id] = {}

            for j, article2 in enumerate(articles):
                article2_id = article2['id']

                if i == j:
                    matrix[article1_id][article2_id] = 1.0
                else:
                    similarity = self._calculate_entity_similarity(
                        article_entities[article1_id],
                        article_entities[article2_id]
                    )
                    matrix[article1_id][article2_id] = similarity

        return matrix
