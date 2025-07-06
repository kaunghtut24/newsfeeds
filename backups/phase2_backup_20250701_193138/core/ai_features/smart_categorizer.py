"""
Smart Content Categorizer
========================

Advanced AI-powered categorization system that goes beyond basic categories
to provide detailed topic detection, industry classification, and event recognition.
"""

import re
import json
from typing import Dict, List, Set, Optional, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class SmartCategorizer:
    """
    Advanced categorization system using rule-based AI and keyword analysis.
    Provides multi-dimensional categorization including topics, industries, and events.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the smart categorizer with configuration."""
        self.config = self._load_config(config_path)
        self.topic_keywords = self._build_topic_keywords()
        self.industry_keywords = self._build_industry_keywords()
        self.event_patterns = self._build_event_patterns()
        self.geographic_keywords = self._build_geographic_keywords()
        
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load categorization configuration."""
        default_config = {
            "confidence_threshold": 0.6,
            "max_topics_per_article": 3,
            "enable_geographic_tagging": True,
            "enable_event_detection": True,
            "enable_industry_classification": True
        }
        
        if config_path:
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            except Exception as e:
                logger.warning(f"Could not load config from {config_path}: {e}")
                
        return default_config
    
    def _build_topic_keywords(self) -> Dict[str, Dict[str, float]]:
        """Build comprehensive topic keyword mappings with weights."""
        return {
            "artificial_intelligence": {
                "artificial intelligence": 1.0, "ai": 0.9, "machine learning": 0.9,
                "deep learning": 0.8, "neural network": 0.8, "chatgpt": 0.7,
                "llm": 0.7, "generative ai": 0.9, "automation": 0.6,
                "algorithm": 0.5, "data science": 0.6, "computer vision": 0.7
            },
            "cryptocurrency": {
                "bitcoin": 1.0, "cryptocurrency": 1.0, "crypto": 0.9,
                "blockchain": 0.8, "ethereum": 0.9, "defi": 0.8,
                "nft": 0.7, "digital currency": 0.8, "mining": 0.6,
                "wallet": 0.5, "exchange": 0.6, "token": 0.6
            },
            "climate_change": {
                "climate change": 1.0, "global warming": 0.9, "carbon": 0.7,
                "renewable energy": 0.8, "solar": 0.6, "wind energy": 0.6,
                "emissions": 0.7, "sustainability": 0.7, "green": 0.5,
                "environment": 0.6, "pollution": 0.6, "clean energy": 0.8
            },
            "cybersecurity": {
                "cybersecurity": 1.0, "hacking": 0.8, "data breach": 0.9,
                "malware": 0.8, "ransomware": 0.8, "phishing": 0.7,
                "security": 0.6, "vulnerability": 0.7, "encryption": 0.6,
                "firewall": 0.6, "cyber attack": 0.9, "privacy": 0.5
            },
            "space_technology": {
                "space": 0.7, "satellite": 0.8, "rocket": 0.7, "nasa": 0.8,
                "spacex": 0.9, "mars": 0.6, "astronaut": 0.7, "orbit": 0.6,
                "launch": 0.5, "space station": 0.8, "aerospace": 0.7
            },
            "healthcare": {
                "healthcare": 1.0, "medical": 0.8, "hospital": 0.7,
                "vaccine": 0.8, "drug": 0.6, "treatment": 0.7,
                "disease": 0.6, "patient": 0.6, "clinical": 0.7,
                "pharmaceutical": 0.8, "therapy": 0.6, "diagnosis": 0.7
            },
            "electric_vehicles": {
                "electric vehicle": 1.0, "ev": 0.9, "tesla": 0.8,
                "battery": 0.6, "charging": 0.7, "autonomous": 0.7,
                "self-driving": 0.8, "electric car": 0.9, "hybrid": 0.6
            },
            "fintech": {
                "fintech": 1.0, "digital payment": 0.8, "mobile payment": 0.8,
                "payment": 0.5, "banking": 0.6, "financial technology": 0.9,
                "digital wallet": 0.7, "peer-to-peer": 0.6, "p2p": 0.6
            }
        }
    
    def _build_industry_keywords(self) -> Dict[str, Dict[str, float]]:
        """Build industry classification keywords."""
        return {
            "technology": {
                "software": 0.8, "hardware": 0.7, "tech": 0.6, "startup": 0.7,
                "silicon valley": 0.8, "app": 0.6, "platform": 0.6, "cloud": 0.7,
                "saas": 0.8, "api": 0.6, "developer": 0.6, "programming": 0.7
            },
            "finance": {
                "bank": 0.8, "investment": 0.8, "stock": 0.7, "market": 0.6,
                "trading": 0.7, "fund": 0.6, "financial": 0.7, "economy": 0.6,
                "gdp": 0.7, "inflation": 0.7, "interest rate": 0.8, "fed": 0.7
            },
            "healthcare": {
                "pharmaceutical": 0.8, "biotech": 0.8, "medical device": 0.8,
                "clinical trial": 0.8, "fda": 0.7, "drug approval": 0.8,
                "health insurance": 0.7, "telemedicine": 0.7
            },
            "energy": {
                "oil": 0.7, "gas": 0.6, "renewable": 0.8, "solar": 0.7,
                "wind": 0.6, "nuclear": 0.7, "coal": 0.6, "electricity": 0.6,
                "power": 0.5, "utility": 0.6, "grid": 0.6
            },
            "automotive": {
                "car": 0.6, "vehicle": 0.7, "automotive": 0.8, "manufacturer": 0.6,
                "dealership": 0.6, "assembly": 0.6, "production": 0.5
            },
            "retail": {
                "retail": 0.8, "e-commerce": 0.8, "shopping": 0.6, "consumer": 0.6,
                "store": 0.5, "sales": 0.5, "merchandise": 0.6, "brand": 0.5
            }
        }

    def _build_event_patterns(self) -> Dict[str, List[str]]:
        """Build event detection patterns."""
        return {
            "earnings_report": [
                r"earnings", r"quarterly results", r"q[1-4] \d{4}",
                r"revenue", r"profit", r"eps", r"guidance"
            ],
            "product_launch": [
                r"launch", r"unveil", r"announce", r"release",
                r"debut", r"introduce", r"new product"
            ],
            "merger_acquisition": [
                r"merger", r"acquisition", r"acquire", r"merge",
                r"takeover", r"buyout", r"deal"
            ],
            "ipo": [
                r"ipo", r"initial public offering", r"goes public",
                r"public listing", r"stock debut"
            ],
            "breaking_news": [
                r"breaking", r"urgent", r"alert", r"developing",
                r"just in", r"live"
            ],
            "regulatory": [
                r"regulation", r"regulatory", r"compliance",
                r"approval", r"ban", r"restriction", r"policy"
            ]
        }

    def _build_geographic_keywords(self) -> Dict[str, List[str]]:
        """Build geographic location keywords."""
        return {
            "north_america": ["usa", "united states", "canada", "mexico", "america"],
            "europe": ["europe", "eu", "uk", "germany", "france", "italy", "spain"],
            "asia": ["asia", "china", "japan", "india", "korea", "singapore"],
            "middle_east": ["middle east", "saudi arabia", "uae", "israel", "iran"],
            "africa": ["africa", "south africa", "nigeria", "egypt"],
            "oceania": ["australia", "new zealand"],
            "global": ["global", "worldwide", "international", "multinational"]
        }

    def categorize_article(self, article: Dict) -> Dict:
        """
        Perform comprehensive categorization of an article.

        Args:
            article: Article dictionary with title, content, description

        Returns:
            Dictionary with categorization results
        """
        text = self._extract_text(article)

        result = {
            "primary_category": self._get_primary_category(article),
            "topics": self._detect_topics(text),
            "industries": self._classify_industries(text),
            "events": self._detect_events(text),
            "geographic_tags": self._detect_geography(text),
            "confidence_scores": {},
            "metadata": {
                "processed_at": datetime.now().isoformat(),
                "text_length": len(text),
                "method": "smart_categorizer_v1"
            }
        }

        return result

    def _extract_text(self, article: Dict) -> str:
        """Extract and combine text from article fields."""
        text_parts = []

        if article.get('title'):
            text_parts.append(article['title'])
        if article.get('description'):
            text_parts.append(article['description'])
        if article.get('content'):
            text_parts.append(article['content'])
        if article.get('summary'):
            text_parts.append(article['summary'])

        return ' '.join(text_parts).lower()

    def _get_primary_category(self, article: Dict) -> str:
        """Get the primary category (existing logic)."""
        return article.get('category', 'General')

    def _detect_topics(self, text: str) -> List[Dict]:
        """Detect specific topics in the text."""
        detected_topics = []

        for topic, keywords in self.topic_keywords.items():
            score = 0.0
            matched_keywords = []

            for keyword, weight in keywords.items():
                if keyword in text:
                    score += weight
                    matched_keywords.append(keyword)

            # Normalize score
            max_possible_score = sum(keywords.values())
            normalized_score = score / max_possible_score if max_possible_score > 0 else 0

            if normalized_score >= self.config["confidence_threshold"]:
                detected_topics.append({
                    "topic": topic,
                    "confidence": normalized_score,
                    "matched_keywords": matched_keywords
                })

        # Sort by confidence and limit results
        detected_topics.sort(key=lambda x: x["confidence"], reverse=True)
        return detected_topics[:self.config["max_topics_per_article"]]

    def _classify_industries(self, text: str) -> List[Dict]:
        """Classify article by industry sectors."""
        if not self.config["enable_industry_classification"]:
            return []

        industries = []

        for industry, keywords in self.industry_keywords.items():
            score = 0.0
            matched_keywords = []

            for keyword, weight in keywords.items():
                if keyword in text:
                    score += weight
                    matched_keywords.append(keyword)

            max_possible_score = sum(keywords.values())
            normalized_score = score / max_possible_score if max_possible_score > 0 else 0

            if normalized_score >= self.config["confidence_threshold"]:
                industries.append({
                    "industry": industry,
                    "confidence": normalized_score,
                    "matched_keywords": matched_keywords
                })

        industries.sort(key=lambda x: x["confidence"], reverse=True)
        return industries[:2]  # Top 2 industries

    def _detect_events(self, text: str) -> List[Dict]:
        """Detect event types in the article."""
        if not self.config["enable_event_detection"]:
            return []

        events = []

        for event_type, patterns in self.event_patterns.items():
            matches = []
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    matches.append(pattern)

            if matches:
                confidence = len(matches) / len(patterns)
                events.append({
                    "event_type": event_type,
                    "confidence": confidence,
                    "matched_patterns": matches
                })

        events.sort(key=lambda x: x["confidence"], reverse=True)
        return events

    def _detect_geography(self, text: str) -> List[Dict]:
        """Detect geographic regions mentioned in the article."""
        if not self.config["enable_geographic_tagging"]:
            return []

        regions = []

        for region, keywords in self.geographic_keywords.items():
            matched_keywords = []
            for keyword in keywords:
                if keyword in text:
                    matched_keywords.append(keyword)

            if matched_keywords:
                confidence = len(matched_keywords) / len(keywords)
                regions.append({
                    "region": region,
                    "confidence": confidence,
                    "matched_keywords": matched_keywords
                })

        regions.sort(key=lambda x: x["confidence"], reverse=True)
        return regions[:3]  # Top 3 regions
