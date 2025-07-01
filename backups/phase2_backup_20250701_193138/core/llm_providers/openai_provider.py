"""
OpenAI LLM Provider
Implements OpenAI GPT models for news summarization
"""

import asyncio
import aiohttp
import json
import time
from typing import Dict, List, Optional, Any

from .base_provider import (
    BaseLLMProvider, LLMResponse, LLMConfig, 
    LLMProviderError, LLMProviderAuthenticationError,
    LLMProviderRateLimitError, LLMProviderQuotaExceededError
)


class OpenAIProvider(BaseLLMProvider):
    """OpenAI GPT provider for news summarization"""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.api_key = config.api_key
        self.base_url = config.base_url or "https://api.openai.com/v1"
        
        # Default models with pricing (per 1K tokens)
        self.default_models = {
            "gpt-3.5-turbo": {
                "cost_per_1k_tokens": 0.002,
                "max_tokens": 4096,
                "context_window": 4096
            },
            "gpt-3.5-turbo-16k": {
                "cost_per_1k_tokens": 0.004,
                "max_tokens": 16384,
                "context_window": 16384
            },
            "gpt-4": {
                "cost_per_1k_tokens": 0.03,
                "max_tokens": 8192,
                "context_window": 8192
            },
            "gpt-4-turbo": {
                "cost_per_1k_tokens": 0.01,
                "max_tokens": 4096,
                "context_window": 128000
            },
            "gpt-4o": {
                "cost_per_1k_tokens": 0.005,
                "max_tokens": 4096,
                "context_window": 128000
            }
        }
        
        # Merge with config models
        if config.models:
            self.default_models.update(config.models)
        
        self.session = None
    
    async def _get_session(self):
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            self.session = aiohttp.ClientSession(timeout=timeout)
        return self.session
    
    async def summarize(self, text: str, **kwargs) -> LLMResponse:
        """Summarize text using OpenAI GPT models"""
        model = kwargs.get('model', 'gpt-3.5-turbo')
        max_tokens = kwargs.get('max_tokens', 150)
        temperature = kwargs.get('temperature', 0.3)
        
        if not self.api_key:
            return self._create_response(
                content="", model=model, tokens_used=0, cost=0.0, 
                response_time=0.0, success=False,
                error_message="OpenAI API key not configured"
            )
        
        # Prepare the prompt
        system_prompt = """You are a professional news summarizer. Create a concise, informative summary of the following news article in 2-3 sentences. Focus on the key facts, main points, and important details. Be objective and factual."""
        
        user_prompt = f"Please summarize this news article:\n\n{text}"
        
        # Prepare request payload
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": 1.0,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        start_time = time.time()
        
        try:
            session = await self._get_session()
            
            async with session.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=headers
            ) as response:
                response_time = time.time() - start_time
                response_data = await response.json()
                
                if response.status == 200:
                    # Successful response
                    choice = response_data["choices"][0]
                    content = choice["message"]["content"].strip()
                    
                    # Extract usage information
                    usage = response_data.get("usage", {})
                    tokens_used = usage.get("total_tokens", 0)
                    
                    # Calculate cost
                    cost = self._calculate_cost(tokens_used, model)
                    
                    # Update provider stats
                    self.total_cost += cost
                    self.total_tokens += tokens_used
                    
                    return self._create_response(
                        content=content,
                        model=model,
                        tokens_used=tokens_used,
                        cost=cost,
                        response_time=response_time,
                        success=True,
                        finish_reason=choice.get("finish_reason"),
                        usage=usage
                    )
                
                elif response.status == 401:
                    raise LLMProviderAuthenticationError("Invalid OpenAI API key")
                elif response.status == 429:
                    raise LLMProviderRateLimitError("OpenAI rate limit exceeded")
                elif response.status == 402:
                    raise LLMProviderQuotaExceededError("OpenAI quota exceeded")
                else:
                    error_msg = response_data.get("error", {}).get("message", "Unknown error")
                    raise LLMProviderError(f"OpenAI API error: {error_msg}")
                    
        except aiohttp.ClientError as e:
            response_time = time.time() - start_time
            return self._create_response(
                content="", model=model, tokens_used=0, cost=0.0,
                response_time=response_time, success=False,
                error_message=f"Network error: {str(e)}"
            )
        except Exception as e:
            response_time = time.time() - start_time
            return self._create_response(
                content="", model=model, tokens_used=0, cost=0.0,
                response_time=response_time, success=False,
                error_message=f"Unexpected error: {str(e)}"
            )
    
    def is_available(self) -> bool:
        """Check if OpenAI provider is available"""
        return bool(self.api_key and self.enabled)
    
    def get_models(self) -> List[str]:
        """Get list of available OpenAI models"""
        return list(self.default_models.keys())
    
    def estimate_cost(self, text: str, model: str = None) -> float:
        """Estimate cost for processing the given text"""
        if not model:
            model = "gpt-3.5-turbo"
        
        # Estimate input tokens (text + system prompt)
        system_prompt_tokens = 50  # Approximate
        input_tokens = self._estimate_tokens(text) + system_prompt_tokens
        
        # Estimate output tokens (summary is typically much shorter)
        output_tokens = min(150, input_tokens // 4)  # Conservative estimate
        
        total_tokens = input_tokens + output_tokens
        
        return self._calculate_cost(total_tokens, model)
    
    def _calculate_cost(self, tokens: int, model: str) -> float:
        """Calculate cost based on tokens and model"""
        if model in self.default_models:
            cost_per_1k = self.default_models[model]["cost_per_1k_tokens"]
        else:
            cost_per_1k = 0.002  # Default to GPT-3.5-turbo pricing
        
        return (tokens / 1000) * cost_per_1k
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test connection to OpenAI API"""
        if not self.api_key:
            return {
                "success": False,
                "error": "API key not configured"
            }
        
        try:
            # Test with a simple completion
            response = await self.summarize(
                "This is a test message to verify OpenAI API connectivity.",
                model="gpt-3.5-turbo",
                max_tokens=10
            )
            
            return {
                "success": response.success,
                "response_time": response.response_time,
                "model": response.model,
                "error": response.error_message if not response.success else None
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_available_models_from_api(self) -> List[Dict[str, Any]]:
        """Get available models from OpenAI API"""
        if not self.api_key:
            return []
        
        try:
            session = await self._get_session()
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            async with session.get(
                f"{self.base_url}/models",
                headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    models = data.get("data", [])
                    
                    # Filter for GPT models suitable for chat completion
                    chat_models = [
                        model for model in models 
                        if model["id"].startswith(("gpt-3.5", "gpt-4"))
                    ]
                    
                    return chat_models
                else:
                    return []
                    
        except Exception:
            return []
    
    async def close(self):
        """Close the aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    def __del__(self):
        """Cleanup when provider is destroyed"""
        if self.session and not self.session.closed:
            # Note: This is not ideal for async cleanup, but serves as a fallback
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(self.close())
            except:
                pass
