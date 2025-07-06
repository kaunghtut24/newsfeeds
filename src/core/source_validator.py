"""
Source validation and testing module for news feed sources
"""

import requests
import feedparser
import time
import re
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class SourceValidationResult:
    """Result of source validation"""
    
    def __init__(self):
        self.is_valid = False
        self.score = 0  # 0-100 quality score
        self.errors = []
        self.warnings = []
        self.details = {}
        self.test_results = {}
    
    def add_error(self, message: str):
        self.errors.append(message)
        self.is_valid = False
    
    def add_warning(self, message: str):
        self.warnings.append(message)
    
    def add_test_result(self, test_name: str, passed: bool, details: str = ""):
        self.test_results[test_name] = {
            'passed': passed,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        if passed:
            self.score += 10  # Each passed test adds 10 points
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'is_valid': self.is_valid,
            'score': min(self.score, 100),  # Cap at 100
            'errors': self.errors,
            'warnings': self.warnings,
            'details': self.details,
            'test_results': self.test_results,
            'validated_at': datetime.now().isoformat()
        }

class SourceValidator:
    """Validates and tests news feed sources"""
    
    def __init__(self):
        self.timeout = 30  # seconds
        self.user_agent = 'NewsFeeds-Validator/1.0'
        self.max_articles_to_check = 5
    
    def validate_source(self, url: str, name: str = "", category: str = "") -> SourceValidationResult:
        """
        Comprehensive validation of a news source
        
        Tests performed:
        1. URL format validation
        2. HTTP accessibility
        3. Feed format compliance
        4. Content availability
        5. Update frequency estimation
        6. Security checks
        7. Content quality assessment
        """
        result = SourceValidationResult()
        result.details['url'] = url
        result.details['name'] = name
        result.details['category'] = category
        
        try:
            # Test 1: URL Format Validation
            self._test_url_format(url, result)
            
            # Test 2: HTTP Accessibility
            response = self._test_http_accessibility(url, result)
            if not response:
                return result
            
            # Test 3: Feed Format Compliance
            feed_data = self._test_feed_format(url, result)
            if not feed_data:
                return result
            
            # Test 4: Content Availability
            self._test_content_availability(feed_data, result)
            
            # Test 5: Update Frequency
            self._test_update_frequency(feed_data, result)
            
            # Test 6: Security Checks
            self._test_security(url, feed_data, result)
            
            # Test 7: Content Quality
            self._test_content_quality(feed_data, result)
            
            # Final validation
            if len(result.errors) == 0 and result.score >= 50:
                result.is_valid = True
            
        except Exception as e:
            result.add_error(f"Validation failed with exception: {str(e)}")
            logger.error(f"Source validation error for {url}: {e}")
        
        return result
    
    def _test_url_format(self, url: str, result: SourceValidationResult):
        """Test if URL format is valid"""
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                result.add_error("Invalid URL format")
                return
            
            if parsed.scheme not in ['http', 'https']:
                result.add_error("URL must use HTTP or HTTPS protocol")
                return
            
            if parsed.scheme == 'http':
                result.add_warning("HTTP URLs are less secure than HTTPS")
            
            result.add_test_result("url_format", True, f"Valid {parsed.scheme.upper()} URL")
            
        except Exception as e:
            result.add_error(f"URL format validation failed: {str(e)}")
    
    def _test_http_accessibility(self, url: str, result: SourceValidationResult) -> Optional[requests.Response]:
        """Test if URL is accessible via HTTP"""
        try:
            headers = {'User-Agent': self.user_agent}
            response = requests.get(url, headers=headers, timeout=self.timeout, allow_redirects=True)
            
            if response.status_code == 200:
                result.add_test_result("http_accessibility", True, f"HTTP {response.status_code} OK")
                result.details['content_type'] = response.headers.get('content-type', 'unknown')
                result.details['content_length'] = len(response.content)
                return response
            else:
                result.add_error(f"HTTP error: {response.status_code}")
                return None
                
        except requests.exceptions.Timeout:
            result.add_error(f"Request timeout after {self.timeout} seconds")
        except requests.exceptions.ConnectionError:
            result.add_error("Connection failed - URL may be unreachable")
        except Exception as e:
            result.add_error(f"HTTP accessibility test failed: {str(e)}")
        
        return None
    
    def _test_feed_format(self, url: str, result: SourceValidationResult) -> Optional[feedparser.FeedParserDict]:
        """Test if URL provides a valid RSS/Atom feed"""
        try:
            feed = feedparser.parse(url)
            
            if feed.bozo:
                if hasattr(feed, 'bozo_exception'):
                    result.add_warning(f"Feed parsing warning: {feed.bozo_exception}")
                else:
                    result.add_warning("Feed has minor formatting issues")
            
            if not hasattr(feed, 'feed') or not feed.feed:
                result.add_error("No valid feed found at URL")
                return None
            
            if not hasattr(feed, 'entries') or len(feed.entries) == 0:
                result.add_error("Feed contains no articles")
                return None
            
            # Check feed metadata
            feed_title = getattr(feed.feed, 'title', 'Unknown')
            feed_description = getattr(feed.feed, 'description', '')
            
            result.details['feed_title'] = feed_title
            result.details['feed_description'] = feed_description
            result.details['article_count'] = len(feed.entries)
            
            result.add_test_result("feed_format", True, f"Valid feed with {len(feed.entries)} articles")
            return feed
            
        except Exception as e:
            result.add_error(f"Feed format test failed: {str(e)}")
            return None
    
    def _test_content_availability(self, feed_data: feedparser.FeedParserDict, result: SourceValidationResult):
        """Test if feed has sufficient content"""
        try:
            entries = feed_data.entries[:self.max_articles_to_check]
            
            articles_with_content = 0
            articles_with_links = 0
            
            for entry in entries:
                # Check for title
                if hasattr(entry, 'title') and entry.title.strip():
                    articles_with_content += 1
                
                # Check for link
                if hasattr(entry, 'link') and entry.link.strip():
                    articles_with_links += 1
            
            if articles_with_content == 0:
                result.add_error("No articles have titles")
                return
            
            if articles_with_links == 0:
                result.add_error("No articles have links")
                return
            
            content_ratio = articles_with_content / len(entries)
            link_ratio = articles_with_links / len(entries)
            
            if content_ratio >= 0.8 and link_ratio >= 0.8:
                result.add_test_result("content_availability", True, 
                                     f"{articles_with_content}/{len(entries)} articles have content")
            else:
                result.add_warning("Some articles missing titles or links")
            
        except Exception as e:
            result.add_error(f"Content availability test failed: {str(e)}")
    
    def _test_update_frequency(self, feed_data: feedparser.FeedParserDict, result: SourceValidationResult):
        """Estimate update frequency based on article timestamps"""
        try:
            entries = feed_data.entries[:10]  # Check last 10 articles
            timestamps = []
            
            for entry in entries:
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    timestamps.append(time.mktime(entry.published_parsed))
                elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                    timestamps.append(time.mktime(entry.updated_parsed))
            
            if len(timestamps) < 2:
                result.add_warning("Cannot determine update frequency - insufficient timestamp data")
                return
            
            timestamps.sort(reverse=True)  # Most recent first
            
            # Calculate average time between articles
            intervals = []
            for i in range(len(timestamps) - 1):
                interval = timestamps[i] - timestamps[i + 1]
                intervals.append(interval)
            
            if intervals:
                avg_interval = sum(intervals) / len(intervals)
                avg_hours = avg_interval / 3600
                
                result.details['estimated_update_frequency_hours'] = avg_hours
                
                if avg_hours <= 24:
                    result.add_test_result("update_frequency", True, f"Updates approximately every {avg_hours:.1f} hours")
                elif avg_hours <= 168:  # 1 week
                    result.add_test_result("update_frequency", True, f"Updates approximately every {avg_hours/24:.1f} days")
                else:
                    result.add_warning(f"Infrequent updates (every {avg_hours/24:.1f} days)")
            
        except Exception as e:
            result.add_warning(f"Update frequency test failed: {str(e)}")
    
    def _test_security(self, url: str, feed_data: feedparser.FeedParserDict, result: SourceValidationResult):
        """Basic security checks"""
        try:
            # Check for HTTPS
            if url.startswith('https://'):
                result.add_test_result("security_https", True, "Uses secure HTTPS protocol")
            else:
                result.add_warning("HTTP is less secure than HTTPS")
            
            # Check for suspicious content patterns
            suspicious_patterns = [
                r'<script[^>]*>.*?</script>',  # JavaScript
                r'javascript:',  # JavaScript URLs
                r'data:.*base64',  # Base64 data URLs
            ]
            
            feed_content = str(feed_data)
            for pattern in suspicious_patterns:
                if re.search(pattern, feed_content, re.IGNORECASE):
                    result.add_warning("Feed contains potentially suspicious content")
                    break
            else:
                result.add_test_result("security_content", True, "No suspicious content patterns detected")
            
        except Exception as e:
            result.add_warning(f"Security test failed: {str(e)}")
    
    def _test_content_quality(self, feed_data: feedparser.FeedParserDict, result: SourceValidationResult):
        """Assess content quality"""
        try:
            entries = feed_data.entries[:self.max_articles_to_check]
            
            quality_score = 0
            total_checks = 0
            
            for entry in entries:
                # Check title length (reasonable titles)
                if hasattr(entry, 'title') and entry.title:
                    title_len = len(entry.title.strip())
                    if 10 <= title_len <= 200:
                        quality_score += 1
                    total_checks += 1
                
                # Check for description/summary
                if hasattr(entry, 'summary') and entry.summary.strip():
                    quality_score += 1
                total_checks += 1
                
                # Check for publication date
                if hasattr(entry, 'published') or hasattr(entry, 'updated'):
                    quality_score += 1
                total_checks += 1
            
            if total_checks > 0:
                quality_ratio = quality_score / total_checks
                if quality_ratio >= 0.7:
                    result.add_test_result("content_quality", True, f"Good content quality ({quality_ratio:.1%})")
                else:
                    result.add_warning(f"Content quality could be improved ({quality_ratio:.1%})")
            
        except Exception as e:
            result.add_warning(f"Content quality test failed: {str(e)}")
