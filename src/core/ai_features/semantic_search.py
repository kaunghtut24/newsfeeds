"""
Semantic Search Engine
======================

Enhanced search engine with natural language processing capabilities,
concept-based search, and intelligent query understanding.
"""

import re
import json
import math
from typing import Dict, List, Optional, Set, Tuple
from collections import defaultdict, Counter
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class SemanticSearchEngine:
    """
    Advanced search engine with semantic understanding and natural language processing.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the semantic search engine."""
        self.config = self._load_config(config_path)
        self.concept_mappings = self._build_concept_mappings()
        self.query_expansions = self._build_query_expansions()
        self.stop_words = self._build_stop_words()
        self.search_index = {}
        self.document_frequencies = defaultdict(int)
        
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load search configuration."""
        default_config = {
            "max_results": 50,
            "relevance_threshold": 0.1,
            "enable_query_expansion": True,
            "enable_concept_search": True,
            "enable_fuzzy_matching": True,
            "fuzzy_threshold": 0.8,
            "boost_factors": {
                "title": 3.0,
                "summary": 2.0,
                "content": 1.0,
                "topics": 2.5,
                "exact_match": 2.0
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
    
    def _build_concept_mappings(self) -> Dict[str, List[str]]:
        """Build concept to keyword mappings for semantic search."""
        return {
            "artificial_intelligence": [
                "ai", "machine learning", "deep learning", "neural networks",
                "automation", "algorithms", "chatgpt", "llm", "generative ai"
            ],
            "financial_performance": [
                "earnings", "revenue", "profit", "loss", "growth", "decline",
                "quarterly results", "financial results", "performance"
            ],
            "market_movement": [
                "stock price", "market", "trading", "shares", "rally", "crash",
                "bull market", "bear market", "volatility"
            ],
            "technology_innovation": [
                "innovation", "breakthrough", "technology", "startup", "launch",
                "product", "development", "research", "patent"
            ],
            "business_strategy": [
                "strategy", "merger", "acquisition", "partnership", "expansion",
                "restructuring", "investment", "funding"
            ],
            "regulatory_changes": [
                "regulation", "policy", "law", "compliance", "approval",
                "ban", "restriction", "government", "regulatory"
            ],
            "environmental_impact": [
                "environment", "climate", "sustainability", "green", "carbon",
                "renewable", "pollution", "emissions"
            ],
            "cybersecurity": [
                "security", "cyber", "hacking", "breach", "malware", "privacy",
                "data protection", "vulnerability"
            ]
        }
    
    def _build_query_expansions(self) -> Dict[str, List[str]]:
        """Build query expansion mappings."""
        return {
            "increase": ["rise", "grow", "surge", "climb", "gain", "boost"],
            "decrease": ["fall", "drop", "decline", "plunge", "reduce", "cut"],
            "company": ["corporation", "firm", "business", "enterprise", "organization"],
            "profit": ["earnings", "income", "revenue", "gains", "returns"],
            "loss": ["deficit", "shortfall", "decline", "reduction"],
            "new": ["latest", "recent", "fresh", "novel", "emerging"],
            "big": ["large", "major", "significant", "substantial", "huge"],
            "small": ["minor", "little", "slight", "modest", "limited"]
        }
    
    def _build_stop_words(self) -> Set[str]:
        """Build stop words list."""
        return {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to",
            "for", "of", "with", "by", "is", "are", "was", "were", "be",
            "been", "have", "has", "had", "do", "does", "did", "will",
            "would", "could", "should", "may", "might", "can", "this",
            "that", "these", "those", "i", "you", "he", "she", "it", "we", "they"
        }
    
    def index_articles(self, articles: List[Dict]):
        """Build search index from articles."""
        self.search_index = {}
        self.document_frequencies = defaultdict(int)
        
        for i, article in enumerate(articles):
            article_id = article.get('id', str(i))
            
            # Extract and process text
            text_content = self._extract_searchable_text(article)
            terms = self._process_text(text_content)
            
            # Build inverted index
            self.search_index[article_id] = {
                "terms": terms,
                "article": article,
                "term_frequencies": Counter(terms)
            }
            
            # Update document frequencies
            unique_terms = set(terms)
            for term in unique_terms:
                self.document_frequencies[term] += 1
    
    def search(self, query: str, articles: List[Dict], 
               filters: Optional[Dict] = None) -> List[Dict]:
        """
        Perform semantic search on articles.
        
        Args:
            query: Search query
            articles: Articles to search
            filters: Additional filters (date, source, category, etc.)
            
        Returns:
            List of search results with relevance scores
        """
        if not query.strip():
            return []
        
        # Index articles if not already done
        if not self.search_index:
            self.index_articles(articles)
        
        # Process query
        processed_query = self._process_query(query)
        
        # Calculate relevance scores
        results = []
        for article_id, article_data in self.search_index.items():
            article = article_data["article"]
            
            # Apply filters first
            if filters and not self._passes_filters(article, filters):
                continue
            
            # Calculate relevance score
            relevance_score = self._calculate_relevance_score(
                processed_query, article_data, article
            )
            
            if relevance_score >= self.config["relevance_threshold"]:
                results.append({
                    "article": article,
                    "relevance_score": relevance_score,
                    "matched_terms": self._get_matched_terms(processed_query, article_data),
                    "highlights": self._generate_highlights(query, article)
                })
        
        # Sort by relevance score
        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        return results[:self.config["max_results"]]
    
    def get_search_suggestions(self, partial_query: str, limit: int = 5) -> List[str]:
        """
        Get search suggestions based on partial query.
        
        Args:
            partial_query: Partial search query
            limit: Maximum number of suggestions
            
        Returns:
            List of search suggestions
        """
        suggestions = []
        query_lower = partial_query.lower().strip()
        
        if len(query_lower) < 2:
            return suggestions
        
        # Concept-based suggestions
        for concept, keywords in self.concept_mappings.items():
            if query_lower in concept.replace("_", " "):
                suggestions.append(concept.replace("_", " ").title())
            
            for keyword in keywords:
                if query_lower in keyword:
                    suggestions.append(keyword.title())
        
        # Term-based suggestions from index
        for term in self.document_frequencies.keys():
            if query_lower in term and len(term) > len(query_lower):
                suggestions.append(term.title())
        
        # Remove duplicates and sort by relevance
        suggestions = list(set(suggestions))
        suggestions.sort(key=lambda x: (
            -len(x) if query_lower in x.lower() else 0,
            self.document_frequencies.get(x.lower(), 0)
        ), reverse=True)
        
        return suggestions[:limit]
    
    def answer_question(self, question: str, articles: List[Dict]) -> Optional[Dict]:
        """
        Attempt to answer a question based on article content.
        
        Args:
            question: Natural language question
            articles: Articles to search for answers
            
        Returns:
            Answer information or None if no answer found
        """
        # Identify question type
        question_type = self._identify_question_type(question)
        
        # Extract key entities from question
        entities = self._extract_entities(question)
        
        # Search for relevant articles
        search_results = self.search(question, articles)
        
        if not search_results:
            return None
        
        # Attempt to extract answer
        answer = self._extract_answer(question, question_type, entities, search_results)
        
        return answer if answer else None
    
    def _extract_searchable_text(self, article: Dict) -> str:
        """Extract searchable text from article."""
        text_parts = []
        
        # Title (highest weight)
        if article.get('title'):
            text_parts.append(article['title'])
        
        # Summary/description
        if article.get('summary'):
            text_parts.append(article['summary'])
        elif article.get('description'):
            text_parts.append(article['description'])
        
        # Content (limited to avoid overwhelming)
        if article.get('content'):
            content = article['content'][:2000]  # Limit content length
            text_parts.append(content)
        
        # Topics from smart categorization
        if article.get('smart_categorization', {}).get('topics'):
            topics = [topic['topic'] for topic in article['smart_categorization']['topics']]
            text_parts.append(' '.join(topics))
        
        return ' '.join(text_parts)
    
    def _process_text(self, text: str) -> List[str]:
        """Process text into searchable terms."""
        # Convert to lowercase and remove special characters
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        
        # Split into words
        words = text.split()
        
        # Remove stop words and short words
        terms = [
            word for word in words 
            if word not in self.stop_words and len(word) > 2
        ]
        
        return terms

    def _process_query(self, query: str) -> Dict:
        """Process search query into structured format."""
        processed = {
            "original": query,
            "terms": self._process_text(query),
            "concepts": [],
            "expanded_terms": []
        }

        # Detect concepts
        if self.config["enable_concept_search"]:
            processed["concepts"] = self._detect_concepts(query)

        # Expand query terms
        if self.config["enable_query_expansion"]:
            processed["expanded_terms"] = self._expand_query_terms(processed["terms"])

        return processed

    def _detect_concepts(self, query: str) -> List[str]:
        """Detect concepts in the query."""
        concepts = []
        query_lower = query.lower()

        for concept, keywords in self.concept_mappings.items():
            # Check if concept name matches
            if concept.replace("_", " ") in query_lower:
                concepts.append(concept)
                continue

            # Check if any keywords match
            for keyword in keywords:
                if keyword in query_lower:
                    concepts.append(concept)
                    break

        return concepts

    def _expand_query_terms(self, terms: List[str]) -> List[str]:
        """Expand query terms using synonyms."""
        expanded = []

        for term in terms:
            expanded.append(term)
            if term in self.query_expansions:
                expanded.extend(self.query_expansions[term])

        return list(set(expanded))

    def _calculate_relevance_score(self, processed_query: Dict,
                                 article_data: Dict, article: Dict) -> float:
        """Calculate relevance score for an article."""
        score = 0.0
        boost_factors = self.config["boost_factors"]

        query_terms = processed_query["terms"]
        expanded_terms = processed_query.get("expanded_terms", [])
        concepts = processed_query.get("concepts", [])

        all_search_terms = set(query_terms + expanded_terms)

        # Calculate TF-IDF scores
        article_terms = article_data["term_frequencies"]

        for term in all_search_terms:
            if term in article_terms:
                tf = article_terms[term]
                df = self.document_frequencies.get(term, 1)
                idf = math.log(len(self.search_index) / df) if df > 0 else 0

                tfidf_score = tf * idf

                # Apply field-specific boosts
                if term in article.get("title", "").lower():
                    tfidf_score *= boost_factors["title"]
                elif term in article.get("summary", "").lower():
                    tfidf_score *= boost_factors["summary"]

                score += tfidf_score

        # Boost for concept matches
        if concepts:
            concept_boost = self._calculate_concept_boost(concepts, article)
            score += concept_boost * boost_factors.get("concepts", 1.0)

        # Boost for exact phrase matches
        original_query = processed_query["original"].lower()
        article_text = self._extract_searchable_text(article).lower()
        if original_query in article_text:
            score *= boost_factors["exact_match"]

        return score

    def _calculate_concept_boost(self, concepts: List[str], article: Dict) -> float:
        """Calculate boost score for concept matches."""
        boost = 0.0

        for concept in concepts:
            keywords = self.concept_mappings.get(concept, [])
            article_text = self._extract_searchable_text(article).lower()

            matches = sum(1 for keyword in keywords if keyword in article_text)
            if matches > 0:
                boost += matches / len(keywords)

        return boost

    def _passes_filters(self, article: Dict, filters: Dict) -> bool:
        """Check if article passes the given filters."""
        # Date filter
        if "date_from" in filters or "date_to" in filters:
            # Implement date filtering logic
            pass

        # Source filter
        if "sources" in filters:
            if article.get("source") not in filters["sources"]:
                return False

        # Category filter
        if "categories" in filters:
            if article.get("category") not in filters["categories"]:
                return False

        # Sentiment filter
        if "sentiment" in filters:
            article_sentiment = article.get("sentiment_analysis", {}).get("overall_sentiment")
            if article_sentiment != filters["sentiment"]:
                return False

        return True

    def _get_matched_terms(self, processed_query: Dict, article_data: Dict) -> List[str]:
        """Get terms that matched in the article."""
        query_terms = set(processed_query["terms"] + processed_query.get("expanded_terms", []))
        article_terms = set(article_data["term_frequencies"].keys())

        return list(query_terms.intersection(article_terms))

    def _generate_highlights(self, query: str, article: Dict) -> Dict[str, List[str]]:
        """Generate highlighted snippets for search results."""
        highlights = {}
        query_terms = self._process_text(query)

        # Highlight in title
        title = article.get("title", "")
        if any(term in title.lower() for term in query_terms):
            highlights["title"] = [title]

        # Highlight in summary
        summary = article.get("summary", "")
        if summary and any(term in summary.lower() for term in query_terms):
            highlights["summary"] = [summary[:200] + "..."]

        return highlights

    def _identify_question_type(self, question: str) -> str:
        """Identify the type of question being asked."""
        question_lower = question.lower()

        if question_lower.startswith(("what", "which")):
            return "what"
        elif question_lower.startswith(("when", "how long")):
            return "when"
        elif question_lower.startswith(("where")):
            return "where"
        elif question_lower.startswith(("who")):
            return "who"
        elif question_lower.startswith(("how")):
            return "how"
        elif question_lower.startswith(("why")):
            return "why"
        else:
            return "general"

    def _extract_entities(self, question: str) -> List[str]:
        """Extract key entities from the question."""
        # Simple entity extraction - in practice, you'd use NLP libraries
        words = self._process_text(question)

        # Filter for potential entities (longer words, capitalized words, etc.)
        entities = [word for word in words if len(word) > 3]

        return entities[:5]  # Limit to top 5 entities

    def _extract_answer(self, question: str, question_type: str,
                       entities: List[str], search_results: List[Dict]) -> Optional[Dict]:
        """Extract answer from search results."""
        if not search_results:
            return None

        # Simple answer extraction - return the most relevant article
        best_result = search_results[0]
        article = best_result["article"]

        return {
            "answer_type": "article_reference",
            "confidence": best_result["relevance_score"],
            "source_article": {
                "title": article.get("title", ""),
                "summary": article.get("summary", "")[:200] + "...",
                "source": article.get("source", ""),
                "url": article.get("url", "")
            },
            "question_type": question_type,
            "entities": entities
        }
