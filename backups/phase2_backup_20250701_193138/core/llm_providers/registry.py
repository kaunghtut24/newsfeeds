"""
LLM Provider Registry
Manages multiple LLM providers with intelligent routing and fallback
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json

from .base_provider import BaseLLMProvider, LLMResponse, LLMConfig, LLMProviderError


class LLMProviderRegistry:
    """Registry for managing multiple LLM providers"""
    
    def __init__(self, config_file: str = None):
        self.providers: Dict[str, BaseLLMProvider] = {}
        self.config_file = config_file
        self.fallback_order: List[str] = []
        self.cost_budget = {
            "daily_limit": 10.0,
            "monthly_limit": 200.0,
            "current_daily": 0.0,
            "current_monthly": 0.0,
            "last_reset": datetime.now()
        }
        self.logger = logging.getLogger(__name__)
        
    def register_provider(self, provider: BaseLLMProvider, priority: int = 0):
        """Register a new LLM provider"""
        self.providers[provider.name] = provider
        provider.config.priority = priority
        self._update_fallback_order()
        self.logger.info(f"Registered LLM provider: {provider.name}")
    
    def unregister_provider(self, provider_name: str):
        """Unregister an LLM provider"""
        if provider_name in self.providers:
            del self.providers[provider_name]
            self._update_fallback_order()
            self.logger.info(f"Unregistered LLM provider: {provider_name}")
    
    def _update_fallback_order(self):
        """Update fallback order based on priority and health scores"""
        enabled_providers = [
            (name, provider) for name, provider in self.providers.items() 
            if provider.enabled and provider.is_available()
        ]
        
        # Sort by priority (higher first), then by health score
        enabled_providers.sort(
            key=lambda x: (x[1].config.priority, x[1].health_score), 
            reverse=True
        )
        
        self.fallback_order = [name for name, _ in enabled_providers]
        self.logger.debug(f"Updated fallback order: {self.fallback_order}")
    
    async def get_summary(self, text: str, preferred_provider: str = None, 
                         model: str = None, **kwargs) -> LLMResponse:
        """
        Get summary using the best available provider
        
        Args:
            text: Text to summarize
            preferred_provider: Preferred provider name (optional)
            model: Specific model to use (optional)
            **kwargs: Additional parameters
            
        Returns:
            LLMResponse from the successful provider
        """
        # Check budget limits
        if not self._check_budget_limits():
            raise LLMProviderError("Budget limit exceeded")
        
        # Update fallback order
        self._update_fallback_order()
        
        # Determine provider order
        provider_order = self._get_provider_order(preferred_provider)
        
        if not provider_order:
            raise LLMProviderError("No available LLM providers")
        
        last_error = None
        
        # Try providers in order
        for provider_name in provider_order:
            provider = self.providers[provider_name]
            
            try:
                self.logger.info(f"Attempting summary with provider: {provider_name}")
                
                # Check if provider is available
                if not provider.is_available():
                    self.logger.warning(f"Provider {provider_name} is not available")
                    continue
                
                # Check cost estimate
                estimated_cost = provider.estimate_cost(text, model)
                if not self._check_cost_limit(estimated_cost):
                    self.logger.warning(f"Cost estimate {estimated_cost} exceeds budget")
                    continue
                
                # Attempt summarization
                response = await provider.summarize(text, model=model, **kwargs)
                
                if response.success:
                    # Update budget tracking
                    self._update_budget(response.cost)
                    
                    # Log successful request
                    self.logger.info(
                        f"Successful summary from {provider_name}: "
                        f"{response.tokens_used} tokens, ${response.cost:.4f}, "
                        f"{response.response_time:.2f}s"
                    )
                    
                    return response
                else:
                    self.logger.warning(
                        f"Provider {provider_name} returned unsuccessful response: "
                        f"{response.error_message}"
                    )
                    last_error = response.error_message
                    
            except Exception as e:
                self.logger.error(f"Error with provider {provider_name}: {str(e)}")
                last_error = str(e)
                continue
        
        # All providers failed
        error_msg = f"All LLM providers failed. Last error: {last_error}"
        self.logger.error(error_msg)
        raise LLMProviderError(error_msg)
    
    def _get_provider_order(self, preferred_provider: str = None) -> List[str]:
        """Get the order of providers to try"""
        if preferred_provider and preferred_provider in self.providers:
            provider = self.providers[preferred_provider]
            if provider.enabled and provider.is_available():
                # Put preferred provider first, then fallback order
                order = [preferred_provider]
                order.extend([p for p in self.fallback_order if p != preferred_provider])
                return order
        
        return self.fallback_order.copy()
    
    def _check_budget_limits(self) -> bool:
        """Check if we're within budget limits"""
        self._reset_budget_if_needed()
        
        daily_ok = self.cost_budget["current_daily"] < self.cost_budget["daily_limit"]
        monthly_ok = self.cost_budget["current_monthly"] < self.cost_budget["monthly_limit"]
        
        return daily_ok and monthly_ok
    
    def _check_cost_limit(self, estimated_cost: float) -> bool:
        """Check if estimated cost is within limits"""
        daily_remaining = self.cost_budget["daily_limit"] - self.cost_budget["current_daily"]
        monthly_remaining = self.cost_budget["monthly_limit"] - self.cost_budget["current_monthly"]
        
        return estimated_cost <= min(daily_remaining, monthly_remaining)
    
    def _update_budget(self, cost: float):
        """Update budget tracking"""
        self.cost_budget["current_daily"] += cost
        self.cost_budget["current_monthly"] += cost
    
    def _reset_budget_if_needed(self):
        """Reset budget counters if needed"""
        now = datetime.now()
        last_reset = self.cost_budget["last_reset"]
        
        # Reset daily budget if it's a new day
        if now.date() > last_reset.date():
            self.cost_budget["current_daily"] = 0.0
            self.cost_budget["last_reset"] = now
        
        # Reset monthly budget if it's a new month
        if now.month != last_reset.month or now.year != last_reset.year:
            self.cost_budget["current_monthly"] = 0.0
    
    def get_provider_stats(self) -> Dict[str, Any]:
        """Get statistics for all providers"""
        stats = {}
        for name, provider in self.providers.items():
            stats[name] = provider.get_stats()
        
        return {
            "providers": stats,
            "fallback_order": self.fallback_order,
            "budget": self.cost_budget,
            "total_providers": len(self.providers),
            "enabled_providers": len([p for p in self.providers.values() if p.enabled]),
            "available_providers": len([p for p in self.providers.values() if p.is_available()])
        }
    
    def get_best_provider(self, text: str = None) -> Optional[str]:
        """Get the name of the best provider for the given text"""
        if not self.fallback_order:
            self._update_fallback_order()
        
        if not self.fallback_order:
            return None
        
        # If text is provided, consider cost
        if text:
            for provider_name in self.fallback_order:
                provider = self.providers[provider_name]
                estimated_cost = provider.estimate_cost(text)
                if self._check_cost_limit(estimated_cost):
                    return provider_name
        
        return self.fallback_order[0] if self.fallback_order else None
    
    def set_budget_limits(self, daily_limit: float = None, monthly_limit: float = None):
        """Set budget limits"""
        if daily_limit is not None:
            self.cost_budget["daily_limit"] = daily_limit
        if monthly_limit is not None:
            self.cost_budget["monthly_limit"] = monthly_limit
    
    def reset_provider_stats(self, provider_name: str = None):
        """Reset statistics for a provider or all providers"""
        if provider_name:
            if provider_name in self.providers:
                self.providers[provider_name].reset_stats()
        else:
            for provider in self.providers.values():
                provider.reset_stats()
    
    async def health_check_all(self) -> Dict[str, bool]:
        """Perform health check on all providers"""
        results = {}
        
        for name, provider in self.providers.items():
            try:
                is_healthy = provider.is_available()
                results[name] = is_healthy
                self.logger.debug(f"Health check {name}: {'✓' if is_healthy else '✗'}")
            except Exception as e:
                results[name] = False
                self.logger.error(f"Health check failed for {name}: {str(e)}")
        
        # Update fallback order after health checks
        self._update_fallback_order()
        
        return results
    
    def save_config(self):
        """Save current configuration to file"""
        if not self.config_file:
            return
        
        config_data = {
            "providers": {},
            "budget": self.cost_budget,
            "fallback_order": self.fallback_order
        }
        
        for name, provider in self.providers.items():
            config_data["providers"][name] = {
                "enabled": provider.enabled,
                "priority": provider.config.priority,
                "stats": provider.get_stats()
            }
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config_data, f, indent=2, default=str)
            self.logger.info(f"Configuration saved to {self.config_file}")
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {str(e)}")
    
    def load_config(self):
        """Load configuration from file"""
        if not self.config_file:
            return
        
        try:
            with open(self.config_file, 'r') as f:
                config_data = json.load(f)
            
            # Load budget settings
            if "budget" in config_data:
                self.cost_budget.update(config_data["budget"])
            
            self.logger.info(f"Configuration loaded from {self.config_file}")
        except FileNotFoundError:
            self.logger.info(f"Configuration file {self.config_file} not found, using defaults")
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {str(e)}")
