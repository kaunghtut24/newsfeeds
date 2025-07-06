"""
AI News Assistant
=================

Conversational AI assistant for news exploration, explanation, and analysis.
Provides context, answers questions, and suggests follow-up inquiries.
"""

import re
import json
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class AINewsAssistant:
    """
    Conversational AI assistant for intelligent news interaction.
    Provides explanations, context, and follow-up suggestions.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the AI news assistant."""
        self.config = self._load_config(config_path)
        self.conversation_history = []
        self.context_cache = {}
        self.explanation_templates = self._build_explanation_templates()
        self.question_patterns = self._build_question_patterns()
        self.follow_up_generators = self._build_follow_up_generators()
        
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load AI assistant configuration."""
        default_config = {
            "max_conversation_history": 10,
            "context_window_size": 5,
            "explanation_detail_level": "medium",
            "enable_follow_up_suggestions": True,
            "enable_context_provision": True,
            "response_style": "professional",
            "max_explanation_length": 500,
            "confidence_threshold": 0.7
        }
        
        if config_path:
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            except Exception as e:
                logger.warning(f"Could not load config from {config_path}: {e}")
                
        return default_config
    
    def _build_explanation_templates(self) -> Dict[str, str]:
        """Build explanation templates for different content types."""
        return {
            "financial": "This article discusses {topic} in the financial sector. {context} The key points are: {key_points}. This could impact {impact_areas}.",
            "technology": "This technology news covers {topic}. {context} The main developments include: {key_points}. This advancement may affect {impact_areas}.",
            "politics": "This political news focuses on {topic}. {context} The important aspects are: {key_points}. This could influence {impact_areas}.",
            "healthcare": "This healthcare article examines {topic}. {context} The significant findings are: {key_points}. This may affect {impact_areas}.",
            "general": "This article covers {topic}. {context} The main points include: {key_points}. The potential implications are {impact_areas}.",
            "simple": "In simple terms: {topic}. {simplified_explanation}. Why it matters: {importance}."
        }
    
    def _build_question_patterns(self) -> Dict[str, List[str]]:
        """Build question pattern recognition."""
        return {
            "what": [
                r"what is (.+)",
                r"what does (.+) mean",
                r"what happened (.+)",
                r"what are (.+)"
            ],
            "why": [
                r"why (.+)",
                r"why is (.+) important",
                r"why did (.+) happen"
            ],
            "how": [
                r"how (.+) work",
                r"how does (.+)",
                r"how will (.+) affect"
            ],
            "when": [
                r"when (.+)",
                r"when did (.+) happen",
                r"when will (.+)"
            ],
            "who": [
                r"who (.+)",
                r"who is (.+)",
                r"who are (.+)"
            ],
            "explain": [
                r"explain (.+)",
                r"tell me about (.+)",
                r"help me understand (.+)"
            ],
            "impact": [
                r"what impact (.+)",
                r"how will this affect (.+)",
                r"what are the consequences (.+)"
            ]
        }
    
    def _build_follow_up_generators(self) -> Dict[str, List[str]]:
        """Build follow-up question generators."""
        return {
            "financial": [
                "How might this affect stock prices?",
                "What are the broader market implications?",
                "Which companies could be impacted?",
                "What should investors watch for next?"
            ],
            "technology": [
                "How does this compare to existing solutions?",
                "What are the potential applications?",
                "Which industries might adopt this?",
                "What are the technical challenges?"
            ],
            "politics": [
                "What are the opposing viewpoints?",
                "How might this affect upcoming elections?",
                "What are the policy implications?",
                "Which stakeholders are involved?"
            ],
            "healthcare": [
                "What are the clinical implications?",
                "How might this affect patients?",
                "What are the regulatory considerations?",
                "What further research is needed?"
            ],
            "general": [
                "What are the key takeaways?",
                "Who are the main stakeholders?",
                "What might happen next?",
                "How does this relate to recent trends?"
            ]
        }
    
    def chat(self, user_message: str, articles: List[Dict], 
             conversation_context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Handle conversational interaction with the user.
        
        Args:
            user_message: User's message/question
            articles: Available articles for context
            conversation_context: Previous conversation context
            
        Returns:
            Assistant response with analysis and suggestions
        """
        # Update conversation history
        self._update_conversation_history(user_message, conversation_context)
        
        # Analyze user intent
        intent = self._analyze_user_intent(user_message)
        
        # Find relevant articles
        relevant_articles = self._find_relevant_articles(user_message, articles)
        
        # Generate response based on intent
        response = self._generate_response(intent, user_message, relevant_articles)
        
        # Add follow-up suggestions
        if self.config["enable_follow_up_suggestions"]:
            response["follow_up_suggestions"] = self._generate_follow_up_suggestions(
                intent, relevant_articles
            )
        
        # Add conversation metadata
        response["conversation_metadata"] = {
            "intent": intent,
            "relevant_articles_count": len(relevant_articles),
            "response_generated_at": datetime.now().isoformat(),
            "confidence": response.get("confidence", 0.5)
        }
        
        return response
    
    def explain_article(self, article: Dict, detail_level: Optional[str] = None) -> Dict[str, Any]:
        """
        Provide detailed explanation of an article.
        
        Args:
            article: Article to explain
            detail_level: Level of detail (simple, medium, detailed)
            
        Returns:
            Comprehensive explanation of the article
        """
        detail_level = detail_level or self.config["explanation_detail_level"]
        
        # Extract key information
        key_info = self._extract_key_information(article)
        
        # Determine article category for appropriate explanation style
        category = self._determine_article_category(article)
        
        # Generate explanation
        explanation = self._generate_explanation(article, key_info, category, detail_level)
        
        # Provide context
        context = self._provide_context(article) if self.config["enable_context_provision"] else {}
        
        # Generate follow-up questions
        follow_ups = self._generate_article_follow_ups(article, category)
        
        return {
            "explanation": explanation,
            "key_information": key_info,
            "context": context,
            "follow_up_questions": follow_ups,
            "article_category": category,
            "detail_level": detail_level,
            "explanation_metadata": {
                "generated_at": datetime.now().isoformat(),
                "method": "ai_news_assistant_v1"
            }
        }
    
    def provide_context(self, topic: str, articles: List[Dict]) -> Dict[str, Any]:
        """
        Provide background context for a topic.
        
        Args:
            topic: Topic to provide context for
            articles: Articles to search for context
            
        Returns:
            Contextual information about the topic
        """
        # Find related articles
        related_articles = self._find_topic_related_articles(topic, articles)
        
        # Extract timeline of events
        timeline = self._extract_topic_timeline(topic, related_articles)
        
        # Identify key players/entities
        key_entities = self._identify_key_entities(topic, related_articles)
        
        # Analyze sentiment evolution
        sentiment_evolution = self._analyze_topic_sentiment_evolution(topic, related_articles)
        
        # Generate context summary
        context_summary = self._generate_context_summary(
            topic, related_articles, timeline, key_entities
        )
        
        return {
            "topic": topic,
            "context_summary": context_summary,
            "timeline": timeline,
            "key_entities": key_entities,
            "sentiment_evolution": sentiment_evolution,
            "related_articles_count": len(related_articles),
            "context_metadata": {
                "generated_at": datetime.now().isoformat(),
                "articles_analyzed": len(related_articles)
            }
        }
    
    def suggest_follow_up_questions(self, article: Dict, 
                                  conversation_history: Optional[List] = None) -> List[str]:
        """
        Suggest relevant follow-up questions for an article.
        
        Args:
            article: Article to generate questions for
            conversation_history: Previous conversation for context
            
        Returns:
            List of suggested follow-up questions
        """
        category = self._determine_article_category(article)
        base_questions = self.follow_up_generators.get(category, self.follow_up_generators["general"])
        
        # Customize questions based on article content
        customized_questions = []
        
        # Extract entities for personalized questions
        entities = self._extract_article_entities(article)
        
        # Generate entity-specific questions
        if entities.get("companies"):
            for company in entities["companies"][:2]:
                customized_questions.append(f"How might this affect {company}?")
        
        if entities.get("people"):
            for person in entities["people"][:1]:
                customized_questions.append(f"What is {person}'s role in this situation?")
        
        # Add topic-specific questions
        if article.get('smart_categorization', {}).get('topics'):
            for topic_info in article['smart_categorization']['topics'][:2]:
                topic = topic_info['topic'].replace('_', ' ').title()
                customized_questions.append(f"What are the latest trends in {topic}?")
        
        # Combine base and customized questions
        all_questions = customized_questions + base_questions
        
        # Remove duplicates and limit
        unique_questions = list(dict.fromkeys(all_questions))
        return unique_questions[:6]

    def _update_conversation_history(self, user_message: str, context: Optional[Dict]):
        """Update conversation history."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "user_message": user_message,
            "context": context
        }

        self.conversation_history.append(entry)

        # Keep only recent history
        max_history = self.config["max_conversation_history"]
        if len(self.conversation_history) > max_history:
            self.conversation_history = self.conversation_history[-max_history:]

    def _analyze_user_intent(self, user_message: str) -> Dict[str, Any]:
        """Analyze user intent from message."""
        message_lower = user_message.lower()

        # Check question patterns
        for intent_type, patterns in self.question_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, message_lower)
                if match:
                    return {
                        "type": intent_type,
                        "confidence": 0.8,
                        "extracted_entity": match.group(1) if match.groups() else None,
                        "original_message": user_message
                    }

        # Fallback intent analysis
        if any(word in message_lower for word in ["explain", "tell me", "help"]):
            return {"type": "explain", "confidence": 0.6, "original_message": user_message}
        elif any(word in message_lower for word in ["what", "how", "why"]):
            return {"type": "question", "confidence": 0.5, "original_message": user_message}
        else:
            return {"type": "general", "confidence": 0.3, "original_message": user_message}

    def _find_relevant_articles(self, user_message: str, articles: List[Dict]) -> List[Dict]:
        """Find articles relevant to user message."""
        message_words = set(user_message.lower().split())
        relevant_articles = []

        for article in articles:
            relevance_score = 0.0

            # Check title relevance
            title_words = set(article.get('title', '').lower().split())
            title_overlap = len(message_words.intersection(title_words))
            relevance_score += title_overlap * 0.4

            # Check summary relevance
            summary_words = set(article.get('summary', '').lower().split())
            summary_overlap = len(message_words.intersection(summary_words))
            relevance_score += summary_overlap * 0.3

            # Check topic relevance
            if article.get('smart_categorization', {}).get('topics'):
                for topic_info in article['smart_categorization']['topics']:
                    topic_words = set(topic_info['topic'].replace('_', ' ').lower().split())
                    topic_overlap = len(message_words.intersection(topic_words))
                    relevance_score += topic_overlap * topic_info['confidence'] * 0.3

            if relevance_score > 0:
                relevant_articles.append({
                    "article": article,
                    "relevance_score": relevance_score
                })

        # Sort by relevance and return top articles
        relevant_articles.sort(key=lambda x: x["relevance_score"], reverse=True)
        return [item["article"] for item in relevant_articles[:5]]

    def _generate_response(self, intent: Dict, user_message: str,
                          relevant_articles: List[Dict]) -> Dict[str, Any]:
        """Generate response based on intent and relevant articles."""
        intent_type = intent["type"]

        if intent_type == "explain" and relevant_articles:
            return self._generate_explanation_response(relevant_articles[0])
        elif intent_type in ["what", "how", "why"] and relevant_articles:
            return self._generate_question_response(intent, relevant_articles)
        elif intent_type == "impact" and relevant_articles:
            return self._generate_impact_response(relevant_articles)
        else:
            return self._generate_general_response(user_message, relevant_articles)

    def _generate_explanation_response(self, article: Dict) -> Dict[str, Any]:
        """Generate explanation response for an article."""
        explanation_result = self.explain_article(article)

        return {
            "response_type": "explanation",
            "message": explanation_result["explanation"]["main_explanation"],
            "detailed_explanation": explanation_result,
            "confidence": 0.8
        }

    def _generate_question_response(self, intent: Dict, articles: List[Dict]) -> Dict[str, Any]:
        """Generate response to user questions."""
        intent_type = intent["type"]
        entity = intent.get("extracted_entity", "")

        if not articles:
            return {
                "response_type": "no_information",
                "message": f"I don't have specific information about {entity} in the current news.",
                "confidence": 0.3
            }

        article = articles[0]

        if intent_type == "what":
            response = f"Based on recent news, {entity} refers to {self._extract_definition(article, entity)}"
        elif intent_type == "why":
            response = f"According to the news, {entity} because {self._extract_reasoning(article, entity)}"
        elif intent_type == "how":
            response = f"The news indicates that {entity} works by {self._extract_mechanism(article, entity)}"
        else:
            response = f"Here's what I found about {entity}: {self._extract_summary(article, entity)}"

        return {
            "response_type": "question_answer",
            "message": response,
            "source_article": {
                "title": article.get("title"),
                "source": article.get("source")
            },
            "confidence": 0.7
        }

    def _generate_impact_response(self, articles: List[Dict]) -> Dict[str, Any]:
        """Generate response about impact/consequences."""
        impacts = []

        for article in articles[:3]:
            if article.get('smart_categorization', {}).get('industries'):
                for industry_info in article['smart_categorization']['industries']:
                    impacts.append(f"Impact on {industry_info['industry']} sector")

            if article.get('sentiment_analysis', {}).get('market_sentiment'):
                market_sentiment = article['sentiment_analysis']['market_sentiment']
                for sentiment_type, data in market_sentiment.items():
                    impacts.append(f"{sentiment_type.title()} market sentiment detected")

        impact_summary = "; ".join(impacts[:5]) if impacts else "No specific impacts identified"

        return {
            "response_type": "impact_analysis",
            "message": f"Potential impacts include: {impact_summary}",
            "detailed_impacts": impacts,
            "confidence": 0.6
        }

    def _generate_general_response(self, user_message: str, articles: List[Dict]) -> Dict[str, Any]:
        """Generate general response when intent is unclear."""
        if articles:
            article = articles[0]
            response = f"I found relevant news about '{article.get('title', 'this topic')}'. {self._extract_summary(article)}"
        else:
            response = "I don't have specific information about that topic in the current news. Could you be more specific?"

        return {
            "response_type": "general",
            "message": response,
            "confidence": 0.4
        }

    def _extract_key_information(self, article: Dict) -> Dict[str, Any]:
        """Extract key information from an article."""
        key_info = {
            "title": article.get("title", ""),
            "source": article.get("source", ""),
            "published_date": article.get("published_date", ""),
            "main_topics": [],
            "key_entities": {},
            "sentiment": "neutral",
            "summary_points": []
        }

        # Extract topics
        if article.get('smart_categorization', {}).get('topics'):
            key_info["main_topics"] = [
                topic_info['topic'] for topic_info in
                article['smart_categorization']['topics'][:3]
            ]

        # Extract entities
        key_info["key_entities"] = self._extract_article_entities(article)

        # Extract sentiment
        if article.get('sentiment_analysis'):
            key_info["sentiment"] = article['sentiment_analysis'].get('overall_sentiment', 'neutral')

        # Extract summary points
        summary = article.get('summary', article.get('description', ''))
        if summary:
            # Simple sentence splitting for key points
            sentences = summary.split('. ')
            key_info["summary_points"] = sentences[:3]

        return key_info

    def _determine_article_category(self, article: Dict) -> str:
        """Determine the category of an article for appropriate explanation style."""
        # Check smart categorization
        if article.get('smart_categorization', {}).get('industries'):
            industries = [ind['industry'] for ind in article['smart_categorization']['industries']]
            if 'finance' in industries:
                return 'financial'
            elif 'technology' in industries:
                return 'technology'
            elif 'healthcare' in industries:
                return 'healthcare'

        # Check basic category
        category = article.get('category', '').lower()
        if category in ['business', 'finance', 'market']:
            return 'financial'
        elif category in ['technology', 'tech']:
            return 'technology'
        elif category in ['politics', 'government']:
            return 'politics'
        elif category in ['health', 'medical']:
            return 'healthcare'

        return 'general'

    def _extract_summary(self, article: Dict, entity: str = "") -> str:
        """Extract summary information from article."""
        summary = article.get('summary', article.get('description', ''))
        if summary:
            return summary[:200] + "..." if len(summary) > 200 else summary
        return f"Information about {entity}" if entity else "No summary available"

    def _extract_definition(self, article: Dict, entity: str) -> str:
        """Extract definition for an entity from article."""
        text = self._get_article_text(article).lower()

        # Simple definition extraction
        sentences = text.split('.')
        for sentence in sentences:
            if entity.lower() in sentence:
                return sentence.strip()[:150] + "..."

        return f"a topic mentioned in recent news about {article.get('title', 'current events')}"

    def _extract_reasoning(self, article: Dict, entity: str) -> str:
        """Extract reasoning/explanation for an entity from article."""
        text = self._get_article_text(article)

        # Look for causal indicators
        causal_words = ['because', 'due to', 'as a result', 'caused by', 'led to']
        sentences = text.split('.')

        for sentence in sentences:
            if entity.lower() in sentence.lower():
                for causal_word in causal_words:
                    if causal_word in sentence.lower():
                        return sentence.strip()[:150] + "..."

        return f"it relates to developments mentioned in {article.get('source', 'recent news')}"

    def _extract_mechanism(self, article: Dict, entity: str) -> str:
        """Extract mechanism/process information for an entity."""
        text = self._get_article_text(article)

        # Look for process indicators
        process_words = ['works by', 'operates', 'functions', 'process', 'method']
        sentences = text.split('.')

        for sentence in sentences:
            if entity.lower() in sentence.lower():
                for process_word in process_words:
                    if process_word in sentence.lower():
                        return sentence.strip()[:150] + "..."

        return f"utilizing methods described in {article.get('title', 'the article')}"

    def _extract_article_entities(self, article: Dict) -> Dict[str, List[str]]:
        """Extract entities from an article."""
        entities = {
            "companies": [],
            "people": [],
            "locations": [],
            "topics": []
        }

        # Extract from smart categorization if available
        if article.get('smart_categorization'):
            # Get topics
            if article['smart_categorization'].get('topics'):
                entities["topics"] = [topic['topic'] for topic in article['smart_categorization']['topics']]

            # Get geographic tags
            if article['smart_categorization'].get('geographic_tags'):
                entities["locations"] = [tag['region'] for tag in article['smart_categorization']['geographic_tags']]

        # Simple entity extraction from text
        text = self._get_article_text(article)

        # Extract company names (simple patterns)
        import re
        company_patterns = [
            r'\b[A-Z][a-z]+ (?:Inc|Corp|Ltd|LLC|Co|Company)\b',
            r'\b(?:Apple|Google|Microsoft|Amazon|Tesla|Meta|Netflix)\b'
        ]

        for pattern in company_patterns:
            matches = re.findall(pattern, text)
            entities["companies"].extend(matches)

        # Remove duplicates
        for key in entities:
            entities[key] = list(set(entities[key]))

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
            text_parts.append(article['content'][:500])  # Limit content

        return ' '.join(text_parts)

    def _generate_explanation(self, article: Dict, key_info: Dict,
                            category: str, detail_level: str) -> Dict[str, str]:
        """Generate explanation based on article and category."""
        template = self.explanation_templates.get(category, self.explanation_templates["general"])

        if detail_level == "simple":
            template = self.explanation_templates["simple"]

        # Extract information for template
        topic = ", ".join(key_info.get("main_topics", ["this topic"]))
        context = f"Published by {key_info.get('source', 'a news source')}"
        key_points = "; ".join(key_info.get("summary_points", ["Key information available"])[:3])
        impact_areas = "various sectors and stakeholders"

        if detail_level == "simple":
            main_explanation = template.format(
                topic=topic,
                simplified_explanation=key_points,
                importance="it affects current developments"
            )
        else:
            main_explanation = template.format(
                topic=topic,
                context=context,
                key_points=key_points,
                impact_areas=impact_areas
            )

        return {
            "main_explanation": main_explanation,
            "detail_level": detail_level,
            "category": category
        }

    def _provide_context(self, article: Dict) -> Dict[str, Any]:
        """Provide contextual information for an article."""
        context = {
            "background": "This article is part of ongoing news coverage",
            "related_topics": [],
            "timeline_position": "current",
            "significance": "moderate"
        }

        # Extract related topics
        if article.get('smart_categorization', {}).get('topics'):
            context["related_topics"] = [
                topic['topic'] for topic in article['smart_categorization']['topics'][:3]
            ]

        # Assess significance based on sentiment and events
        if article.get('smart_categorization', {}).get('events'):
            context["significance"] = "high"
        elif article.get('sentiment_analysis', {}).get('overall_sentiment') in ['positive', 'negative']:
            context["significance"] = "moderate-high"

        return context

    def _generate_article_follow_ups(self, article: Dict, category: str) -> List[str]:
        """Generate follow-up questions for an article."""
        base_questions = self.follow_up_generators.get(category, self.follow_up_generators["general"])

        # Customize based on article content
        customized = []

        # Add entity-specific questions
        entities = self._extract_article_entities(article)

        if entities.get("companies"):
            company = entities["companies"][0]
            customized.append(f"How might this affect {company}?")

        if entities.get("topics"):
            topic = entities["topics"][0].replace('_', ' ').title()
            customized.append(f"What are the implications for {topic}?")

        # Combine and limit
        all_questions = customized + base_questions
        return list(dict.fromkeys(all_questions))[:6]  # Remove duplicates, limit to 6

    def _generate_follow_up_suggestions(self, intent: Dict, articles: List[Dict]) -> List[str]:
        """Generate follow-up suggestions based on intent and articles."""
        intent_type = intent.get("type", "general")

        # Base suggestions by intent type
        base_suggestions = {
            "what": [
                "How does this impact the market?",
                "What are the next steps?",
                "Who are the key players involved?"
            ],
            "why": [
                "What are the broader implications?",
                "How might this affect other sectors?",
                "What should we watch for next?"
            ],
            "how": [
                "What are the technical details?",
                "How does this compare to alternatives?",
                "What are the implementation challenges?"
            ],
            "explain": [
                "Can you provide more context?",
                "What are the key takeaways?",
                "How does this relate to recent trends?"
            ]
        }

        suggestions = base_suggestions.get(intent_type, base_suggestions["explain"])

        # Add article-specific suggestions
        if articles:
            article = articles[0]

            # Add source-specific suggestion
            source = article.get('source', '')
            if source:
                suggestions.append(f"What else is {source} reporting?")

            # Add topic-specific suggestions
            if article.get('smart_categorization', {}).get('topics'):
                topic = article['smart_categorization']['topics'][0]['topic']
                topic_name = topic.replace('_', ' ').title()
                suggestions.append(f"What are the latest trends in {topic_name}?")

        return suggestions[:5]  # Limit to 5 suggestions
