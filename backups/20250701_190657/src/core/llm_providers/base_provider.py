"""
Base LLM Provider Interface
Provides a unified interface for all LLM providers
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import time


@dataclass
class LLMResponse:
    """Standardized response from any LLM provider"""
    content: str
    model: str
    provider: str
    tokens_used: int
    cost: float
    response_time: float
    timestamp: datetime
    metadata: Dict[str, Any]
    success: bool = True
    error_message: Optional[str] = None


@dataclass
class LLMConfig:
    """Configuration for an LLM provider"""
    provider_name: str
    enabled: bool
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    models: Dict[str, Dict] = None
    rate_limits: Dict[str, int] = None
    priority: int = 0
    cost_per_1k_tokens: float = 0.0
    max_tokens: int = 4096
    timeout: int = 30
    retry_attempts: int = 3
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.models is None:
            self.models = {}
        if self.rate_limits is None:
            self.rate_limits = {"requests_per_minute": 60}
        if self.metadata is None:
            self.metadata = {}


class BaseLLMProvider(ABC):
    """Abstract base class for all LLM providers"""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.name = config.provider_name
        self.enabled = config.enabled
        self.health_score = 1.0
        self.last_health_check = None
        self.request_count = 0
        self.error_count = 0
        self.total_cost = 0.0
        self.total_tokens = 0
        
    @abstractmethod
    async def summarize(self, text: str, **kwargs) -> LLMResponse:
        """
        Summarize the given text
        
        Args:
            text: Text to summarize
            **kwargs: Additional parameters (model, max_tokens, etc.)
            
        Returns:
            LLMResponse object with standardized response
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is available and healthy"""
        pass
    
    @abstractmethod
    def get_models(self) -> List[str]:
        """Get list of available models for this provider"""
        pass
    
    @abstractmethod
    def estimate_cost(self, text: str, model: str = None) -> float:
        """Estimate the cost for processing the given text"""
        pass
    
    def get_health_score(self) -> float:
        """Get the current health score (0.0 to 1.0)"""
        if self.request_count == 0:
            return 1.0
        return max(0.0, 1.0 - (self.error_count / self.request_count))
    
    def update_health_score(self, success: bool):
        """Update health score based on request success/failure"""
        self.request_count += 1
        if not success:
            self.error_count += 1
        
        # Calculate new health score
        self.health_score = self.get_health_score()
        self.last_health_check = datetime.now()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get provider statistics"""
        return {
            "name": self.name,
            "enabled": self.enabled,
            "health_score": self.health_score,
            "request_count": self.request_count,
            "error_count": self.error_count,
            "success_rate": (self.request_count - self.error_count) / max(1, self.request_count),
            "total_cost": self.total_cost,
            "total_tokens": self.total_tokens,
            "last_health_check": self.last_health_check,
            "available_models": self.get_models() if self.is_available() else []
        }
    
    def reset_stats(self):
        """Reset provider statistics"""
        self.request_count = 0
        self.error_count = 0
        self.total_cost = 0.0
        self.total_tokens = 0
        self.health_score = 1.0
    
    def _create_response(self, content: str, model: str, tokens_used: int, 
                        cost: float, response_time: float, success: bool = True, 
                        error_message: str = None, **metadata) -> LLMResponse:
        """Helper method to create standardized LLM response"""
        return LLMResponse(
            content=content,
            model=model,
            provider=self.name,
            tokens_used=tokens_used,
            cost=cost,
            response_time=response_time,
            timestamp=datetime.now(),
            metadata=metadata,
            success=success,
            error_message=error_message
        )
    
    def _estimate_tokens(self, text: str) -> int:
        """Rough estimation of tokens (4 characters ≈ 1 token)"""
        return len(text) // 4
    
    def _calculate_cost(self, tokens: int, model: str = None) -> float:
        """Calculate cost based on tokens and model"""
        if model and model in self.config.models:
            cost_per_1k = self.config.models[model].get("cost_per_1k_tokens", 0.0)
        else:
            cost_per_1k = self.config.cost_per_1k_tokens
        
        return (tokens / 1000) * cost_per_1k
    
    async def _execute_with_retry(self, func, *args, **kwargs):
        """Execute function with retry logic"""
        last_exception = None
        
        for attempt in range(self.config.retry_attempts):
            try:
                start_time = time.time()
                result = await func(*args, **kwargs)
                response_time = time.time() - start_time
                
                self.update_health_score(True)
                return result, response_time
                
            except Exception as e:
                last_exception = e
                self.update_health_score(False)
                
                if attempt < self.config.retry_attempts - 1:
                    # Wait before retry (exponential backoff)
                    wait_time = 2 ** attempt
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    break
        
        # All retries failed
        response_time = time.time() - start_time if 'start_time' in locals() else 0
        raise last_exception


class LLMProviderError(Exception):
    """Base exception for LLM provider errors"""
    pass


class LLMProviderUnavailableError(LLMProviderError):
    """Raised when LLM provider is unavailable"""
    pass


class LLMProviderRateLimitError(LLMProviderError):
    """Raised when rate limit is exceeded"""
    pass


class LLMProviderAuthenticationError(LLMProviderError):
    """Raised when authentication fails"""
    pass


class LLMProviderQuotaExceededError(LLMProviderError):
    """Raised when quota is exceeded"""
    pass
