"""
Advanced Search Engine for News Feed Application
Provides full-text search, filtering, and ranking capabilities
"""

import re
import json
from typing import List, Dict, Any, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass
from collections import defaultdict
import math


@dataclass
class SearchQuery:
    """Represents a search query with various filters"""
    text: str = ""
    sources: List[str] = None
    categories: List[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    sentiment: Optional[str] = None
    min_relevance: float = 0.0
    sort_by: str = "relevance"  # relevance, date, title
    sort_order: str = "desc"  # asc, desc
    limit: int = 50

    def __post_init__(self):
        if self.sources is None:
            self.sources = []
        if self.categories is None:
            self.categories = []


@dataclass
class SearchResult:
    """Represents a search result with relevance score"""
    article: Dict[str, Any]
    relevance_score: float
    matched_fields: List[str]
    highlighted_text: Dict[str, str]


class NewsSearchEngine:
    """Advanced search engine for news articles"""
    
    def __init__(self):
        self.stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have',
            'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
            'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those'
        }
        
        # TF-IDF cache for performance
        self.tf_idf_cache = {}
        self.document_frequencies = {}
        self.total_documents = 0
        
    def index_articles(self, articles: List[Dict[str, Any]]):
        """Build search index for articles"""
        self.total_documents = len(articles)
        self.document_frequencies = defaultdict(int)
        
        # Calculate document frequencies for TF-IDF
        for article in articles:
            text_content = self._extract_searchable_text(article)
            terms = self._tokenize(text_content)
            unique_terms = set(terms)
            
            for term in unique_terms:
                self.document_frequencies[term] += 1
    
    def search(self, query: SearchQuery, articles: List[Dict[str, Any]]) -> List[SearchResult]:
        """
        Perform advanced search on articles
        
        Args:
            query: SearchQuery object with search parameters
            articles: List of articles to search
            
        Returns:
            List of SearchResult objects sorted by relevance
        """
        # Re-index if needed
        if self.total_documents != len(articles):
            self.index_articles(articles)
        
        results = []
        
        for article in articles:
            # Apply filters first
            if not self._passes_filters(article, query):
                continue
            
            # Calculate relevance score
            relevance_score = self._calculate_relevance(article, query)
            
            if relevance_score >= query.min_relevance:
                # Find matched fields and create highlights
                matched_fields = self._find_matched_fields(article, query)
                highlighted_text = self._create_highlights(article, query)
                
                result = SearchResult(
                    article=article,
                    relevance_score=relevance_score,
                    matched_fields=matched_fields,
                    highlighted_text=highlighted_text
                )
                results.append(result)
        
        # Sort results
        results = self._sort_results(results, query)
        
        # Apply limit
        return results[:query.limit]
    
    def _extract_searchable_text(self, article: Dict[str, Any]) -> str:
        """Extract all searchable text from an article"""
        text_parts = []
        
        # Title (weighted more heavily)
        if article.get('title'):
            text_parts.append(article['title'] * 3)  # Triple weight for title
        
        # Summary
        if article.get('summary'):
            text_parts.append(article['summary'] * 2)  # Double weight for summary
        
        # Full text
        if article.get('full_text'):
            text_parts.append(article['full_text'])
        
        # Source and category
        if article.get('source'):
            text_parts.append(article['source'])
        
        if article.get('category'):
            text_parts.append(article['category'])
        
        return ' '.join(text_parts)
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into searchable terms"""
        if not text:
            return []
        
        # Convert to lowercase and extract words
        text = text.lower()
        words = re.findall(r'\b[a-zA-Z]{2,}\b', text)
        
        # Remove stop words
        words = [word for word in words if word not in self.stop_words]
        
        return words
    
    def _passes_filters(self, article: Dict[str, Any], query: SearchQuery) -> bool:
        """Check if article passes all filters"""
        
        # Source filter
        if query.sources and article.get('source') not in query.sources:
            return False
        
        # Category filter
        if query.categories and article.get('category') not in query.categories:
            return False
        
        # Date filter
        if query.date_from or query.date_to:
            article_date = self._parse_article_date(article)
            if article_date:
                if query.date_from and article_date < query.date_from:
                    return False
                if query.date_to and article_date > query.date_to:
                    return False
        
        # Sentiment filter
        if query.sentiment and article.get('sentiment') != query.sentiment:
            return False
        
        return True
    
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
    
    def _calculate_relevance(self, article: Dict[str, Any], query: SearchQuery) -> float:
        """Calculate relevance score using TF-IDF and other factors"""
        if not query.text.strip():
            return 1.0  # No text query, all articles are equally relevant
        
        query_terms = self._tokenize(query.text)
        if not query_terms:
            return 1.0
        
        article_text = self._extract_searchable_text(article)
        article_terms = self._tokenize(article_text)
        
        if not article_terms:
            return 0.0
        
        # Calculate TF-IDF score
        tf_idf_score = 0.0
        
        for term in query_terms:
            # Term frequency in document
            tf = article_terms.count(term) / len(article_terms)
            
            # Inverse document frequency
            df = self.document_frequencies.get(term, 0)
            if df > 0:
                idf = math.log(self.total_documents / df)
            else:
                idf = 0
            
            tf_idf_score += tf * idf
        
        # Boost score for exact phrase matches
        if len(query_terms) > 1:
            query_phrase = ' '.join(query_terms)
            if query_phrase in article_text.lower():
                tf_idf_score *= 1.5
        
        # Boost score for title matches
        title_text = article.get('title', '').lower()
        title_matches = sum(1 for term in query_terms if term in title_text)
        if title_matches > 0:
            tf_idf_score *= (1 + title_matches * 0.3)
        
        return tf_idf_score
    
    def _find_matched_fields(self, article: Dict[str, Any], query: SearchQuery) -> List[str]:
        """Find which fields contain query terms"""
        if not query.text.strip():
            return []
        
        query_terms = self._tokenize(query.text)
        matched_fields = []
        
        fields_to_check = {
            'title': article.get('title', ''),
            'summary': article.get('summary', ''),
            'full_text': article.get('full_text', ''),
            'source': article.get('source', ''),
            'category': article.get('category', '')
        }
        
        for field_name, field_value in fields_to_check.items():
            field_tokens = self._tokenize(field_value)
            if any(term in field_tokens for term in query_terms):
                matched_fields.append(field_name)
        
        return matched_fields
    
    def _create_highlights(self, article: Dict[str, Any], query: SearchQuery) -> Dict[str, str]:
        """Create highlighted text snippets"""
        if not query.text.strip():
            return {}
        
        query_terms = self._tokenize(query.text)
        highlights = {}
        
        fields_to_highlight = {
            'title': article.get('title', ''),
            'summary': article.get('summary', ''),
        }
        
        for field_name, field_value in fields_to_highlight.items():
            if field_value:
                highlighted = self._highlight_text(field_value, query_terms)
                if highlighted != field_value:  # Only include if there are highlights
                    highlights[field_name] = highlighted
        
        return highlights
    
    def _highlight_text(self, text: str, terms: List[str], max_length: int = 200) -> str:
        """Highlight search terms in text"""
        if not text or not terms:
            return text
        
        # Create pattern for all terms
        pattern = '|'.join(re.escape(term) for term in terms)
        
        # Find matches
        matches = list(re.finditer(pattern, text, re.IGNORECASE))
        
        if not matches:
            return text[:max_length] + ('...' if len(text) > max_length else '')
        
        # Create highlighted version
        highlighted = text
        offset = 0
        
        for match in matches:
            start, end = match.span()
            start += offset
            end += offset
            
            original = highlighted[start:end]
            replacement = f'<mark>{original}</mark>'
            highlighted = highlighted[:start] + replacement + highlighted[end:]
            offset += len(replacement) - len(original)
        
        # Truncate if too long, trying to keep highlights
        if len(highlighted) > max_length:
            first_highlight = highlighted.find('<mark>')
            if first_highlight != -1:
                start = max(0, first_highlight - 50)
                end = min(len(highlighted), start + max_length)
                highlighted = highlighted[start:end]
                if start > 0:
                    highlighted = '...' + highlighted
                if end < len(text):
                    highlighted = highlighted + '...'
        
        return highlighted
    
    def _sort_results(self, results: List[SearchResult], query: SearchQuery) -> List[SearchResult]:
        """Sort search results based on query parameters"""
        reverse = query.sort_order == "desc"
        
        if query.sort_by == "relevance":
            return sorted(results, key=lambda x: x.relevance_score, reverse=reverse)
        elif query.sort_by == "date":
            return sorted(results, 
                         key=lambda x: self._parse_article_date(x.article) or datetime.min, 
                         reverse=reverse)
        elif query.sort_by == "title":
            return sorted(results, 
                         key=lambda x: x.article.get('title', '').lower(), 
                         reverse=reverse)
        else:
            return results
    
    def get_search_suggestions(self, partial_query: str, articles: List[Dict[str, Any]], 
                             limit: int = 10) -> List[str]:
        """Get search suggestions based on partial query"""
        if len(partial_query) < 2:
            return []
        
        suggestions = set()
        partial_lower = partial_query.lower()
        
        # Extract terms from all articles
        all_terms = set()
        for article in articles:
            text = self._extract_searchable_text(article)
            terms = self._tokenize(text)
            all_terms.update(terms)
        
        # Find matching terms
        for term in all_terms:
            if term.startswith(partial_lower) and len(term) > len(partial_query):
                suggestions.add(term)
        
        # Also check for phrase completions in titles
        for article in articles:
            title = article.get('title', '').lower()
            if partial_lower in title:
                # Extract phrases containing the partial query
                words = title.split()
                for i, word in enumerate(words):
                    if partial_lower in word:
                        # Get phrase around this word
                        start = max(0, i - 1)
                        end = min(len(words), i + 3)
                        phrase = ' '.join(words[start:end])
                        if len(phrase) > len(partial_query):
                            suggestions.add(phrase)
        
        return sorted(list(suggestions))[:limit]
