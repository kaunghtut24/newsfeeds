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
        try:
            # Try to get the current event loop
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If we're already in an event loop, we need to run in a thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(self._run_async_in_new_loop, news_items, **kwargs)
                    return future.result()
            else:
                # No running loop, safe to use asyncio.run
                return asyncio.run(self.summarize_news_items_async(news_items, **kwargs))
        except RuntimeError:
            # No event loop exists, create one
            return asyncio.run(self.summarize_news_items_async(news_items, **kwargs))

    def _run_async_in_new_loop(self, news_items: List[Dict], **kwargs) -> List[Dict]:
        """Helper method to run async code in a new event loop"""
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        try:
            return new_loop.run_until_complete(self.summarize_news_items_async(news_items, **kwargs))
        finally:
            new_loop.close()
    
    async def summarize_news_items_async(self, news_items: List[Dict], **kwargs) -> List[Dict]:
        """
        Summarize multiple news items asynchronously with intelligent batching

        Args:
            news_items: List of news items to summarize
            **kwargs: Additional parameters including:
                - max_text_length: Maximum text length per article (default: 2000)
                - batch_delay: Delay between articles in seconds (default: 0.5)
                - max_retries: Maximum retries per article (default: 2)

        Returns:
            List of news items with summaries added
        """
        summarized_items = []
        max_text_length = kwargs.get('max_text_length', 2000)
        batch_delay = kwargs.get('batch_delay', 0.5)
        max_retries = kwargs.get('max_retries', 2)

        for i, item in enumerate(news_items):
            print(f"Summarizing {i+1}/{len(news_items)}: {item['title'][:50]}...")

            # Get text to summarize (prioritize full_text, fallback to title)
            text_to_summarize = item.get('full_text') or f"Title: {item['title']}\nSource: {item['source']}"

            # Truncate text if too long to prevent token overflow
            if len(text_to_summarize) > max_text_length:
                text_to_summarize = text_to_summarize[:max_text_length] + "..."
                print(f"  📝 Truncated article to {max_text_length} characters")

            # Retry logic for failed summarizations
            retry_count = 0
            response = None

            while retry_count <= max_retries:
                try:
                    # Summarize the text
                    response = await self.summarize_text(text_to_summarize, **kwargs)

                    if response.success:
                        break
                    else:
                        print(f"  ⚠️ Attempt {retry_count + 1} failed: {response.error_message}")

                except Exception as e:
                    print(f"  ⚠️ Attempt {retry_count + 1} error: {str(e)}")

                retry_count += 1
                if retry_count <= max_retries:
                    await asyncio.sleep(1)  # Wait before retry

            # Add summary to item
            if response and response.success:
                item['summary'] = response.content
                item['llm_provider'] = response.provider
                item['llm_model'] = response.model
                item['llm_cost'] = response.cost
                item['llm_tokens'] = response.tokens_used
                item['llm_response_time'] = response.response_time
            else:
                # Create a fallback summary from the article text
                item['summary'] = self._create_fallback_summary(item)
                item['llm_provider'] = 'fallback'
                item['llm_model'] = 'none'
                item['llm_cost'] = 0.0
                item['llm_tokens'] = 0
                item['llm_response_time'] = 0.0
                print(f"  ⚠️ Using fallback summary for: {item['title'][:50]}...")

            summarized_items.append(item)

            # Add delay between articles to prevent overwhelming the model
            if i < len(news_items) - 1:  # Don't delay after the last item
                await asyncio.sleep(batch_delay)

        return summarized_items

    def _create_fallback_summary(self, item):
        """Create a basic summary when LLM providers fail"""
        try:
            # Get the text content
            text = item.get('full_text', '') or item.get('description', '') or item.get('title', '')

            if not text:
                return f"Article from {item.get('source', 'Unknown source')} - Summary not available"

            # Clean the text
            import re
            # Remove extra whitespace and newlines
            text = re.sub(r'\s+', ' ', text).strip()

            # Remove common website elements
            text = re.sub(r'(Get businessline apps on|Connect with us|TO ENJOY ADDITIONAL BENEFITS|Copyright©.*|Terms & conditions.*)', '', text, flags=re.IGNORECASE)

            # Remove financial data patterns (numbers with +/- signs, decimals, currency symbols)
            text = re.sub(r'[-+]?\d+\.\d+\s*[-+]?\s*\d*\.?\d*\s*[-+]?\s*\d*\.?\d*', '', text)
            text = re.sub(r'[-+]\s*\d+\.\d+', '', text)
            text = re.sub(r'\b\d+\.\d+\s*[-+]\s*\d+\.\d+\b', '', text)
            text = re.sub(r'[-+]?\s*\d+\.\d+\s*[-+]?\s*\d+\.\d+\s*[-+]?\s*\d+\.\d+', '', text)

            # Remove standalone numbers and financial symbols
            text = re.sub(r'\b[-+]?\d+\.\d+\b', '', text)
            text = re.sub(r'[₹$€£¥]\s*\d+', '', text)
            text = re.sub(r'\b\d+\s*cr\b|\b\d+\s*crore\b|\b\d+\s*mn\b|\b\d+\s*million\b', '', text)

            # Remove percentage and stock-like patterns
            text = re.sub(r'\d+\.\d+%|\d+%', '', text)
            text = re.sub(r'\(\d+\.\d+%\)|\(\d+%\)', '', text)

            # Remove multiple spaces created by removals
            text = re.sub(r'\s+', ' ', text).strip()

            # Take first few sentences (up to 200 characters)
            sentences = text.split('. ')
            summary = ""
            for sentence in sentences:
                # Skip sentences that are mostly numbers or very short
                if len(sentence.strip()) < 10 or re.match(r'^[\d\s\-+.%₹$€£¥]+$', sentence.strip()):
                    continue

                if len(summary + sentence) < 200:
                    summary += sentence + ". "
                else:
                    break

            # If summary is too short, try to get meaningful content
            if len(summary.strip()) < 50:
                # Look for sentences with actual words (not just numbers)
                meaningful_sentences = []
                for sentence in sentences:
                    # Check if sentence has at least 5 words and isn't mostly numbers
                    words = re.findall(r'\b[a-zA-Z]+\b', sentence)
                    if len(words) >= 5:
                        meaningful_sentences.append(sentence)
                        if len(' '.join(meaningful_sentences)) > 150:
                            break

                if meaningful_sentences:
                    summary = '. '.join(meaningful_sentences[:2]) + "."
                else:
                    # Last resort: use title-based summary
                    summary = f"Article about {item.get('title', 'news topic')} from {item.get('source', 'news source')}"

            return summary.strip() or f"Article from {item.get('source', 'Unknown source')} about {item.get('title', 'news topic')}"

        except Exception as e:
            return f"Article from {item.get('source', 'Unknown source')} - Summary generation failed"
    
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
