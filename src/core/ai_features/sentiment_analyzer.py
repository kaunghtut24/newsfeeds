"""
Advanced Sentiment Analyzer
===========================

Multi-dimensional sentiment and emotion analysis system that goes beyond
basic positive/negative classification to provide nuanced emotional insights.
"""

import re
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class AdvancedSentimentAnalyzer:
    """
    Advanced sentiment analysis system providing multi-dimensional emotional insights.
    Includes sentiment, emotion, market sentiment, and bias detection.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the advanced sentiment analyzer."""
        self.config = self._load_config(config_path)
        self.sentiment_lexicon = self._build_sentiment_lexicon()
        self.emotion_lexicon = self._build_emotion_lexicon()
        self.market_sentiment_lexicon = self._build_market_sentiment_lexicon()
        self.bias_indicators = self._build_bias_indicators()
        self.intensity_modifiers = self._build_intensity_modifiers()
        
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load sentiment analysis configuration."""
        default_config = {
            "sentiment_threshold": 0.1,
            "emotion_threshold": 0.2,
            "enable_market_sentiment": True,
            "enable_bias_detection": True,
            "enable_emotion_analysis": True,
            "context_window": 5  # words around sentiment words
        }
        
        if config_path:
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            except Exception as e:
                logger.warning(f"Could not load config from {config_path}: {e}")
                
        return default_config
    
    def _build_sentiment_lexicon(self) -> Dict[str, Dict[str, float]]:
        """Build comprehensive sentiment lexicon with intensity scores."""
        return {
            "positive": {
                # Strong positive
                "excellent": 1.0, "outstanding": 1.0, "exceptional": 1.0,
                "amazing": 0.9, "fantastic": 0.9, "brilliant": 0.9,
                "wonderful": 0.8, "great": 0.8, "superb": 0.8,
                "good": 0.6, "nice": 0.5, "positive": 0.6,
                "success": 0.7, "achievement": 0.7, "victory": 0.8,
                "growth": 0.6, "improvement": 0.6, "progress": 0.6,
                "opportunity": 0.5, "benefit": 0.6, "advantage": 0.6,
                "innovation": 0.7, "breakthrough": 0.8, "milestone": 0.7
            },
            "negative": {
                # Strong negative
                "terrible": -1.0, "awful": -1.0, "horrible": -1.0,
                "disaster": -0.9, "crisis": -0.8, "catastrophe": -0.9,
                "failure": -0.8, "problem": -0.6, "issue": -0.5,
                "bad": -0.6, "poor": -0.6, "weak": -0.5,
                "decline": -0.6, "loss": -0.7, "drop": -0.5,
                "concern": -0.5, "worry": -0.6, "fear": -0.7,
                "risk": -0.5, "threat": -0.7, "challenge": -0.4,
                "controversy": -0.6, "scandal": -0.8, "fraud": -0.9
            }
        }
    
    def _build_emotion_lexicon(self) -> Dict[str, Dict[str, float]]:
        """Build emotion detection lexicon."""
        return {
            "excitement": {
                "excited": 0.8, "thrilled": 0.9, "enthusiastic": 0.8,
                "eager": 0.7, "anticipation": 0.6, "buzz": 0.6,
                "momentum": 0.6, "energy": 0.5
            },
            "concern": {
                "concerned": 0.7, "worried": 0.8, "anxious": 0.8,
                "uncertain": 0.6, "doubt": 0.6, "skeptical": 0.7,
                "cautious": 0.5, "hesitant": 0.6
            },
            "optimism": {
                "optimistic": 0.8, "hopeful": 0.7, "confident": 0.8,
                "bullish": 0.8, "positive outlook": 0.7, "upbeat": 0.7,
                "promising": 0.6, "encouraging": 0.6
            },
            "pessimism": {
                "pessimistic": 0.8, "gloomy": 0.7, "bearish": 0.8,
                "negative outlook": 0.7, "downbeat": 0.7, "bleak": 0.8,
                "discouraging": 0.6, "disappointing": 0.6
            },
            "urgency": {
                "urgent": 0.8, "immediate": 0.7, "critical": 0.8,
                "pressing": 0.7, "time-sensitive": 0.6, "deadline": 0.6,
                "rush": 0.6, "emergency": 0.9
            },
            "surprise": {
                "surprising": 0.7, "unexpected": 0.8, "shocking": 0.9,
                "sudden": 0.6, "abrupt": 0.6, "unforeseen": 0.7,
                "dramatic": 0.7, "remarkable": 0.6
            }
        }
    
    def _build_market_sentiment_lexicon(self) -> Dict[str, Dict[str, float]]:
        """Build market-specific sentiment lexicon."""
        return {
            "bullish": {
                "rally": 0.8, "surge": 0.8, "soar": 0.9, "climb": 0.6,
                "gain": 0.6, "rise": 0.6, "upturn": 0.7, "recovery": 0.7,
                "bull market": 0.9, "uptrend": 0.7, "momentum": 0.6,
                "outperform": 0.7, "beat expectations": 0.8
            },
            "bearish": {
                "plunge": 0.9, "crash": 1.0, "tumble": 0.8, "fall": 0.6,
                "decline": 0.6, "drop": 0.6, "downturn": 0.7, "recession": 0.9,
                "bear market": 0.9, "downtrend": 0.7, "correction": 0.7,
                "underperform": 0.7, "miss expectations": 0.8
            },
            "volatile": {
                "volatile": 0.8, "volatility": 0.8, "fluctuation": 0.6,
                "swing": 0.6, "unstable": 0.7, "erratic": 0.7,
                "turbulent": 0.8, "choppy": 0.6
            }
        }
    
    def _build_bias_indicators(self) -> Dict[str, List[str]]:
        """Build bias detection indicators."""
        return {
            "strong_opinion": [
                "clearly", "obviously", "undoubtedly", "certainly",
                "definitely", "absolutely", "without question"
            ],
            "emotional_language": [
                "outrageous", "ridiculous", "absurd", "shocking",
                "unbelievable", "incredible", "stunning"
            ],
            "loaded_terms": [
                "scheme", "plot", "manipulation", "propaganda",
                "spin", "agenda", "conspiracy"
            ],
            "superlatives": [
                "best", "worst", "greatest", "terrible", "perfect",
                "complete", "total", "ultimate", "extreme"
            ]
        }
    
    def _build_intensity_modifiers(self) -> Dict[str, float]:
        """Build intensity modifier words."""
        return {
            # Amplifiers
            "very": 1.3, "extremely": 1.5, "incredibly": 1.4,
            "highly": 1.2, "significantly": 1.3, "substantially": 1.3,
            "tremendously": 1.4, "enormously": 1.4, "exceptionally": 1.4,
            
            # Diminishers
            "slightly": 0.7, "somewhat": 0.8, "rather": 0.8,
            "fairly": 0.8, "moderately": 0.7, "relatively": 0.8,
            "quite": 0.9, "pretty": 0.8, "kind of": 0.7,
            
            # Negators
            "not": -1.0, "no": -1.0, "never": -1.0, "none": -1.0,
            "nothing": -1.0, "neither": -1.0, "without": -0.8
        }

    def analyze_sentiment(self, article: Dict) -> Dict:
        """
        Perform comprehensive sentiment analysis on an article.

        Args:
            article: Article dictionary with title, content, description

        Returns:
            Dictionary with sentiment analysis results
        """
        text = self._extract_text(article)
        words = text.lower().split()

        # Basic sentiment analysis
        sentiment_scores = self._calculate_sentiment_scores(words)

        # Emotion analysis
        emotions = self._analyze_emotions(words) if self.config["enable_emotion_analysis"] else {}

        # Market sentiment (for business/finance articles)
        market_sentiment = self._analyze_market_sentiment(words) if self.config["enable_market_sentiment"] else {}

        # Bias detection
        bias_indicators = self._detect_bias(text) if self.config["enable_bias_detection"] else {}

        # Overall sentiment classification
        overall_sentiment = self._classify_overall_sentiment(sentiment_scores)

        result = {
            "overall_sentiment": overall_sentiment,
            "sentiment_scores": sentiment_scores,
            "emotions": emotions,
            "market_sentiment": market_sentiment,
            "bias_indicators": bias_indicators,
            "emotional_impact": self._calculate_emotional_impact(sentiment_scores, emotions),
            "metadata": {
                "processed_at": datetime.now().isoformat(),
                "text_length": len(text),
                "word_count": len(words),
                "method": "advanced_sentiment_v1"
            }
        }

        return result

    def _extract_text(self, article: Dict) -> str:
        """Extract and combine text from article fields."""
        text_parts = []

        # Prioritize title and summary for sentiment analysis
        if article.get('title'):
            text_parts.append(article['title'] * 2)  # Weight title more heavily
        if article.get('summary'):
            text_parts.append(article['summary'])
        if article.get('description'):
            text_parts.append(article['description'])
        if article.get('content'):
            # Limit content to avoid overwhelming with too much text
            content = article['content'][:1000]
            text_parts.append(content)

        return ' '.join(text_parts)

    def _calculate_sentiment_scores(self, words: List[str]) -> Dict[str, float]:
        """Calculate sentiment scores with intensity modifiers."""
        positive_score = 0.0
        negative_score = 0.0
        neutral_count = 0

        for i, word in enumerate(words):
            # Check for sentiment words
            pos_score = self.sentiment_lexicon["positive"].get(word, 0)
            neg_score = self.sentiment_lexicon["negative"].get(word, 0)

            if pos_score > 0 or neg_score < 0:
                # Apply intensity modifiers
                modifier = self._get_intensity_modifier(words, i)

                if pos_score > 0:
                    positive_score += pos_score * modifier
                if neg_score < 0:
                    negative_score += abs(neg_score) * modifier
            else:
                neutral_count += 1

        total_words = len(words)

        return {
            "positive": positive_score / total_words if total_words > 0 else 0,
            "negative": negative_score / total_words if total_words > 0 else 0,
            "neutral": neutral_count / total_words if total_words > 0 else 1,
            "compound": (positive_score - negative_score) / total_words if total_words > 0 else 0
        }

    def _get_intensity_modifier(self, words: List[str], index: int) -> float:
        """Get intensity modifier for a word based on surrounding context."""
        modifier = 1.0
        context_window = self.config["context_window"]

        # Check words before the sentiment word
        start = max(0, index - context_window)
        for i in range(start, index):
            word = words[i]
            if word in self.intensity_modifiers:
                modifier *= self.intensity_modifiers[word]

        return abs(modifier)  # Ensure positive modifier

    def _analyze_emotions(self, words: List[str]) -> Dict[str, float]:
        """Analyze emotional content of the text."""
        emotions = {}

        for emotion, emotion_words in self.emotion_lexicon.items():
            score = 0.0
            matches = 0

            for word in words:
                if word in emotion_words:
                    score += emotion_words[word]
                    matches += 1

            if matches > 0:
                normalized_score = score / len(words)
                if normalized_score >= self.config["emotion_threshold"]:
                    emotions[emotion] = {
                        "intensity": normalized_score,
                        "matches": matches
                    }

        return emotions

    def _analyze_market_sentiment(self, words: List[str]) -> Dict[str, Dict]:
        """Analyze market-specific sentiment."""
        market_sentiments = {}

        for sentiment_type, sentiment_words in self.market_sentiment_lexicon.items():
            score = 0.0
            matches = 0

            for word in words:
                if word in sentiment_words:
                    score += sentiment_words[word]
                    matches += 1

            if matches > 0:
                normalized_score = score / len(words)
                market_sentiments[sentiment_type] = {
                    "intensity": normalized_score,
                    "matches": matches
                }

        return market_sentiments

    def _detect_bias(self, text: str) -> Dict[str, List]:
        """Detect potential bias indicators in text."""
        bias_detected = {}

        for bias_type, indicators in self.bias_indicators.items():
            matches = []
            for indicator in indicators:
                if indicator.lower() in text.lower():
                    matches.append(indicator)

            if matches:
                bias_detected[bias_type] = matches

        return bias_detected

    def _classify_overall_sentiment(self, sentiment_scores: Dict[str, float]) -> str:
        """Classify overall sentiment based on scores."""
        compound = sentiment_scores.get("compound", 0)

        if compound >= 0.05:
            return "positive"
        elif compound <= -0.05:
            return "negative"
        else:
            return "neutral"

    def _calculate_emotional_impact(self, sentiment_scores: Dict[str, float],
                                  emotions: Dict[str, Dict]) -> float:
        """Calculate overall emotional impact score."""
        base_impact = abs(sentiment_scores.get("compound", 0))

        # Boost impact based on detected emotions
        emotion_boost = 0.0
        for emotion, data in emotions.items():
            intensity = data.get("intensity", 0)
            if emotion in ["excitement", "concern", "urgency", "surprise"]:
                emotion_boost += intensity * 0.5

        return min(base_impact + emotion_boost, 1.0)
