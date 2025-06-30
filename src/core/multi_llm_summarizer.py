"""
Multi-LLM Summarizer
Manages multiple LLM providers for news summarization with intelligent routing
"""

import asyncio
import logging
import os
from typing import Dict, List, Optional, Any
import json

from .llm_providers.registry import LLMProviderRegistry
from .llm_providers.base_provider import LLMConfig, LLMResponse
from .llm_providers.openai_provider import OpenAIProvider
from .llm_providers.anthropic_provider import AnthropicProvider
from .llm_providers.google_provider import GoogleProvider
from .llm_providers.ollama_provider import OllamaProvider


class MultiLLMSummarizer:
    """Multi-LLM summarizer with intelligent provider selection and fallback"""
    
    def __init__(self, config_file: str = None):
        self.registry = LLMProviderRegistry(config_file)
        self.logger = logging.getLogger(__name__)
        self.config_file = config_file or "llm_config.json"
        
        # Initialize providers
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize all LLM providers based on configuration"""
        config = self._load_config()
        
        # Initialize OpenAI provider
        if config.get("openai", {}).get("enabled", False):
            openai_config = LLMConfig(
                provider_name="openai",
                enabled=True,
                api_key=os.getenv("OPENAI_API_KEY") or config["openai"].get("api_key"),
                priority=config["openai"].get("priority", 1),
                models=config["openai"].get("models", {}),
                rate_limits=config["openai"].get("rate_limits", {}),
                timeout=config["openai"].get("timeout", 30)
            )
            
            if openai_config.api_key:
                provider = OpenAIProvider(openai_config)
                self.registry.register_provider(provider, openai_config.priority)
                self.logger.info("OpenAI provider initialized")
            else:
                self.logger.warning("OpenAI API key not found, skipping OpenAI provider")
        
        # Initialize Anthropic provider
        if config.get("anthropic", {}).get("enabled", False):
            anthropic_config = LLMConfig(
                provider_name="anthropic",
                enabled=True,
                api_key=os.getenv("ANTHROPIC_API_KEY") or config["anthropic"].get("api_key"),
                priority=config["anthropic"].get("priority", 2),
                models=config["anthropic"].get("models", {}),
                rate_limits=config["anthropic"].get("rate_limits", {}),
                timeout=config["anthropic"].get("timeout", 30)
            )
            
            if anthropic_config.api_key:
                provider = AnthropicProvider(anthropic_config)
                self.registry.register_provider(provider, anthropic_config.priority)
                self.logger.info("Anthropic provider initialized")
            else:
                self.logger.warning("Anthropic API key not found, skipping Anthropic provider")
        
        # Initialize Google AI provider
        if config.get("google", {}).get("enabled", False):
            google_config = LLMConfig(
                provider_name="google",
                enabled=True,
                api_key=os.getenv("GOOGLE_AI_API_KEY") or config["google"].get("api_key"),
                priority=config["google"].get("priority", 3),
                models=config["google"].get("models", {}),
                rate_limits=config["google"].get("rate_limits", {}),
                timeout=config["google"].get("timeout", 30)
            )
            
            if google_config.api_key:
                provider = GoogleProvider(google_config)
                self.registry.register_provider(provider, google_config.priority)
                self.logger.info("Google AI provider initialized")
            else:
                self.logger.warning("Google AI API key not found, skipping Google provider")
        
        # Initialize Ollama provider (always enabled if available)
        ollama_config = LLMConfig(
            provider_name="ollama",
            enabled=config.get("ollama", {}).get("enabled", True),
            base_url=config.get("ollama", {}).get("base_url", "http://localhost:11434"),
            priority=config.get("ollama", {}).get("priority", 10),  # Lower priority (fallback)
            models=config.get("ollama", {}).get("models", {}),
            timeout=config.get("ollama", {}).get("timeout", 60)
        )
        
        provider = OllamaProvider(ollama_config)
        self.registry.register_provider(provider, ollama_config.priority)
        self.logger.info("Ollama provider initialized")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load LLM configuration from file"""
        default_config = {
            "openai": {
                "enabled": False,
                "priority": 1,
                "models": {
                    "gpt-3.5-turbo": {"cost_per_1k_tokens": 0.002},
                    "gpt-4": {"cost_per_1k_tokens": 0.03}
                }
            },
            "anthropic": {
                "enabled": False,
                "priority": 2,
                "models": {
                    "claude-3-haiku-20240307": {"cost_per_1k_tokens": 0.00025},
                    "claude-3-sonnet-20240229": {"cost_per_1k_tokens": 0.003}
                }
            },
            "google": {
                "enabled": False,
                "priority": 3,
                "models": {
                    "gemini-1.5-flash": {"cost_per_1k_tokens": 0.00015},
                    "gemini-1.5-pro": {"cost_per_1k_tokens": 0.0035}
                }
            },
            "ollama": {
                "enabled": True,
                "priority": 10,
                "base_url": "http://localhost:11434"
            },
            "budget": {
                "daily_limit": 10.0,
                "monthly_limit": 200.0
            }
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                # Merge with defaults
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                    elif isinstance(value, dict):
                        for subkey, subvalue in value.items():
                            if subkey not in config[key]:
                                config[key][subkey] = subvalue
                return config
            else:
                return default_config
        except Exception as e:
            self.logger.error(f"Error loading config: {e}")
            return default_config
    
    def save_config(self, config: Dict[str, Any]):
        """Save LLM configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            self.logger.info(f"Configuration saved to {self.config_file}")
        except Exception as e:
            self.logger.error(f"Error saving config: {e}")
    
    async def summarize_text(self, text: str, preferred_provider: str = None, 
                           model: str = None, **kwargs) -> LLMResponse:
        """
        Summarize text using the best available LLM provider
        
        Args:
            text: Text to summarize
            preferred_provider: Preferred provider name (optional)
            model: Specific model to use (optional)
            **kwargs: Additional parameters
            
        Returns:
            LLMResponse from the successful provider
        """
        try:
            response = await self.registry.get_summary(
                text=text,
                preferred_provider=preferred_provider,
                model=model,
                **kwargs
            )
            
            self.logger.info(
                f"Successfully summarized with {response.provider} "
                f"({response.model}): {response.tokens_used} tokens, "
                f"${response.cost:.4f}, {response.response_time:.2f}s"
            )
            
            return response
            
        except Exception as e:
            self.logger.error(f"Summarization failed: {str(e)}")
            
            # Return a fallback response
            return LLMResponse(
                content=f"Summary unavailable: {str(e)}",
                model="fallback",
                provider="fallback",
                tokens_used=0,
                cost=0.0,
                response_time=0.0,
                timestamp=None,
                metadata={},
                success=False,
                error_message=str(e)
            )
    
    def summarize_news_items(self, news_items: List[Dict], **kwargs) -> List[Dict]:
        """
        Summarize multiple news items (synchronous wrapper for async method)
        
        Args:
            news_items: List of news items to summarize
            **kwargs: Additional parameters
            
        Returns:
            List of news items with summaries added
        """
        return asyncio.run(self.summarize_news_items_async(news_items, **kwargs))
    
    async def summarize_news_items_async(self, news_items: List[Dict], **kwargs) -> List[Dict]:
        """
        Summarize multiple news items asynchronously
        
        Args:
            news_items: List of news items to summarize
            **kwargs: Additional parameters
            
        Returns:
            List of news items with summaries added
        """
        summarized_items = []
        
        for i, item in enumerate(news_items):
            print(f"Summarizing {i+1}/{len(news_items)}: {item['title'][:50]}...")
            
            # Get text to summarize (prioritize full_text, fallback to title)
            text_to_summarize = item.get('full_text') or f"Title: {item['title']}\nSource: {item['source']}"
            
            # Summarize the text
            response = await self.summarize_text(text_to_summarize, **kwargs)
            
            # Add summary to item
            item['summary'] = response.content if response.success else "Summary unavailable"
            item['llm_provider'] = response.provider
            item['llm_model'] = response.model
            item['llm_cost'] = response.cost
            item['llm_tokens'] = response.tokens_used
            item['llm_response_time'] = response.response_time
            
            summarized_items.append(item)
        
        return summarized_items
    
    def get_provider_stats(self) -> Dict[str, Any]:
        """Get statistics for all providers"""
        return self.registry.get_provider_stats()
    
    def get_available_providers(self) -> List[str]:
        """Get list of available provider names"""
        return [name for name, provider in self.registry.providers.items() 
                if provider.enabled and provider.is_available()]
    
    def get_available_models(self, provider_name: str = None) -> Dict[str, List[str]]:
        """Get available models for all providers or a specific provider"""
        if provider_name:
            if provider_name in self.registry.providers:
                provider = self.registry.providers[provider_name]
                return {provider_name: provider.get_models()}
            else:
                return {}
        else:
            models = {}
            for name, provider in self.registry.providers.items():
                if provider.enabled and provider.is_available():
                    models[name] = provider.get_models()
            return models
    
    def set_budget_limits(self, daily_limit: float = None, monthly_limit: float = None):
        """Set budget limits for cost control"""
        self.registry.set_budget_limits(daily_limit, monthly_limit)
    
    async def health_check_all(self) -> Dict[str, bool]:
        """Perform health check on all providers"""
        return await self.registry.health_check_all()
    
    def enable_provider(self, provider_name: str):
        """Enable a specific provider"""
        if provider_name in self.registry.providers:
            self.registry.providers[provider_name].enabled = True
            self.logger.info(f"Enabled provider: {provider_name}")
    
    def disable_provider(self, provider_name: str):
        """Disable a specific provider"""
        if provider_name in self.registry.providers:
            self.registry.providers[provider_name].enabled = False
            self.logger.info(f"Disabled provider: {provider_name}")
    
    async def close_all(self):
        """Close all provider connections"""
        for provider in self.registry.providers.values():
            if hasattr(provider, 'close'):
                await provider.close()
