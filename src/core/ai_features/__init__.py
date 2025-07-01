"""
AI Features Module for News Feed Application
===========================================

This module contains advanced AI-powered features for content intelligence,
analysis, and enhancement.

Modules:
- smart_categorizer: Advanced topic detection and categorization
- sentiment_analyzer: Multi-dimensional sentiment and emotion analysis
- content_recommender: Intelligent content recommendation system
- semantic_search: Enhanced search with natural language processing
"""

from .smart_categorizer import SmartCategorizer
from .sentiment_analyzer import AdvancedSentimentAnalyzer
from .content_recommender import ContentRecommender
from .semantic_search import SemanticSearchEngine
from .content_relationship_mapper import ContentRelationshipMapper
from .trend_analyzer import TrendAnalyzer
from .ai_news_assistant import AINewsAssistant
from .smart_briefing_generator import SmartBriefingGenerator

__all__ = [
    'SmartCategorizer',
    'AdvancedSentimentAnalyzer',
    'ContentRecommender',
    'SemanticSearchEngine',
    'ContentRelationshipMapper',
    'TrendAnalyzer',
    'AINewsAssistant',
    'SmartBriefingGenerator'
]

__version__ = '1.0.0'
