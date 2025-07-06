"""
Performance Optimizer for News Fetching and Summarization
Dynamically adjusts batch sizes and processing parameters based on load
"""

import json
import time
import logging
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

@dataclass
class PerformanceProfile:
    """Performance profile for different load scenarios"""
    name: str
    max_articles_per_source: int
    batch_size: int
    batch_delay: float
    max_text_length: int
    max_concurrent_sources: int
    timeout_per_article: int
    max_retries: int
    enable_parallel_processing: bool
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class PerformanceOptimizer:
    """
    Dynamically optimizes performance based on:
    - Number of sources
    - Total articles to process
    - System load
    - User preferences
    """
    
    def __init__(self, config_path: str = "data/performance_config.json"):
        self.config_path = config_path
        self.profiles = self._load_profiles()
        self.current_profile = "balanced"
        self.performance_stats = {
            "total_requests": 0,
            "avg_processing_time": 0,
            "last_optimization": None
        }
    
    def _load_profiles(self) -> Dict[str, PerformanceProfile]:
        """Load performance profiles from config"""
        default_profiles = {
            "fast": PerformanceProfile(
                name="fast",
                max_articles_per_source=3,
                batch_size=2,
                batch_delay=0.2,
                max_text_length=1500,
                max_concurrent_sources=1,
                timeout_per_article=15,
                max_retries=1,
                enable_parallel_processing=False
            ),
            "balanced": PerformanceProfile(
                name="balanced",
                max_articles_per_source=5,
                batch_size=3,
                batch_delay=0.5,
                max_text_length=2000,
                max_concurrent_sources=2,
                timeout_per_article=30,
                max_retries=2,
                enable_parallel_processing=True
            ),
            "comprehensive": PerformanceProfile(
                name="comprehensive",
                max_articles_per_source=10,
                batch_size=5,
                batch_delay=1.0,
                max_text_length=3000,
                max_concurrent_sources=3,
                timeout_per_article=45,
                max_retries=3,
                enable_parallel_processing=True
            ),
            "minimal": PerformanceProfile(
                name="minimal",
                max_articles_per_source=2,
                batch_size=1,
                batch_delay=0.1,
                max_text_length=1000,
                max_concurrent_sources=1,
                timeout_per_article=10,
                max_retries=1,
                enable_parallel_processing=False
            )
        }
        
        try:
            with open(self.config_path, 'r') as f:
                config_data = json.load(f)
                profiles = {}
                for name, data in config_data.get('profiles', {}).items():
                    profiles[name] = PerformanceProfile(**data)
                return profiles if profiles else default_profiles
        except (FileNotFoundError, json.JSONDecodeError):
            logger.info("Using default performance profiles")
            self._save_profiles(default_profiles)
            return default_profiles
    
    def _save_profiles(self, profiles: Dict[str, PerformanceProfile]):
        """Save performance profiles to config"""
        try:
            config_data = {
                "profiles": {name: profile.to_dict() for name, profile in profiles.items()},
                "last_updated": datetime.now().isoformat()
            }
            with open(self.config_path, 'w') as f:
                json.dump(config_data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save performance profiles: {e}")
    
    def get_optimal_profile(self, num_sources: int, total_articles: int, user_preference: str = None) -> PerformanceProfile:
        """
        Determine optimal performance profile based on load
        
        Args:
            num_sources: Number of sources to process
            total_articles: Estimated total articles to process
            user_preference: User's preferred profile (fast/balanced/comprehensive)
        
        Returns:
            Optimal PerformanceProfile
        """
        # User preference takes priority
        if user_preference and user_preference in self.profiles:
            return self.profiles[user_preference]
        
        # Auto-select based on load
        if total_articles <= 10:
            return self.profiles["fast"]
        elif total_articles <= 30:
            return self.profiles["balanced"]
        elif total_articles <= 60:
            return self.profiles["comprehensive"]
        else:
            # For very large loads, use minimal to avoid timeouts
            return self.profiles["minimal"]
    
    def get_processing_parameters(self, num_sources: int, estimated_articles: int, 
                                user_preference: str = None) -> Dict[str, Any]:
        """
        Get optimized processing parameters
        
        Returns:
            Dictionary with optimized parameters for news processing
        """
        profile = self.get_optimal_profile(num_sources, estimated_articles, user_preference)
        
        # Calculate dynamic adjustments
        processing_time_estimate = estimated_articles * 0.8  # ~0.8s per article
        
        return {
            "max_articles_per_source": profile.max_articles_per_source,
            "batch_size": profile.batch_size,
            "batch_delay": profile.batch_delay,
            "max_text_length": profile.max_text_length,
            "max_concurrent_sources": profile.max_concurrent_sources,
            "timeout_per_article": profile.timeout_per_article,
            "max_retries": profile.max_retries,
            "enable_parallel_processing": profile.enable_parallel_processing,
            "estimated_processing_time": processing_time_estimate,
            "profile_name": profile.name
        }
    
    def update_performance_stats(self, processing_time: float, articles_processed: int):
        """Update performance statistics for future optimization"""
        self.performance_stats["total_requests"] += 1
        
        # Update rolling average
        current_avg = self.performance_stats["avg_processing_time"]
        new_avg = (current_avg + processing_time) / 2 if current_avg > 0 else processing_time
        self.performance_stats["avg_processing_time"] = new_avg
        self.performance_stats["last_optimization"] = datetime.now().isoformat()
        
        logger.info(f"Performance update: {processing_time:.2f}s for {articles_processed} articles")
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get current performance statistics"""
        return {
            "current_profile": self.current_profile,
            "available_profiles": list(self.profiles.keys()),
            "performance_stats": self.performance_stats,
            "recommendations": self._get_recommendations()
        }
    
    def _get_recommendations(self) -> List[str]:
        """Get performance recommendations based on current stats"""
        recommendations = []
        
        avg_time = self.performance_stats["avg_processing_time"]
        if avg_time > 60:  # More than 1 minute
            recommendations.append("Consider using 'fast' profile for quicker processing")
        elif avg_time < 10:  # Less than 10 seconds
            recommendations.append("System performing well - consider 'comprehensive' for more articles")
        
        return recommendations

# Global instance
performance_optimizer = PerformanceOptimizer()
