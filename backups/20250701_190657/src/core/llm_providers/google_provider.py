"""
Google AI LLM Provider
Implements Google Gemini models for news summarization
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


class GoogleProvider(BaseLLMProvider):
    """Google AI provider for news summarization"""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.api_key = config.api_key
        self.base_url = config.base_url or "https://generativelanguage.googleapis.com/v1beta"
        
        # Default models with pricing (per 1K tokens)
        self.default_models = {
            "gemini-1.5-flash": {
                "cost_per_1k_tokens": 0.00015,
                "max_tokens": 8192,
                "context_window": 1000000
            },
            "gemini-1.5-pro": {
                "cost_per_1k_tokens": 0.0035,
                "max_tokens": 8192,
                "context_window": 2000000
            },
            "gemini-pro": {
                "cost_per_1k_tokens": 0.0005,
                "max_tokens": 8192,
                "context_window": 32768
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
        """Summarize text using Google Gemini models"""
        model = kwargs.get('model', 'gemini-1.5-flash')
        max_tokens = kwargs.get('max_tokens', 150)
        temperature = kwargs.get('temperature', 0.3)
        
        if not self.api_key:
            return self._create_response(
                content="", model=model, tokens_used=0, cost=0.0, 
                response_time=0.0, success=False,
                error_message="Google AI API key not configured"
            )
        
        # Prepare the prompt
        prompt = f"""You are a professional news summarizer. Create a concise, informative summary of the following news article in 2-3 sentences. Focus on the key facts, main points, and important details. Be objective and factual.

News Article:
{text}

Summary:"""
        
        # Prepare request payload for Gemini
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
                "topP": 0.8,
                "topK": 10
            }
        }
        
        start_time = time.time()
        
        try:
            session = await self._get_session()
            
            # Construct URL with API key
            url = f"{self.base_url}/models/{model}:generateContent?key={self.api_key}"
            
            async with session.post(url, json=payload) as response:
                response_time = time.time() - start_time
                response_data = await response.json()
                
                if response.status == 200:
                    # Successful response
                    candidates = response_data.get("candidates", [])
                    if candidates and len(candidates) > 0:
                        content_parts = candidates[0].get("content", {}).get("parts", [])
                        if content_parts:
                            content = content_parts[0].get("text", "").strip()
                        else:
                            content = ""
                    else:
                        content = ""
                    
                    # Extract usage information (if available)
                    usage_metadata = response_data.get("usageMetadata", {})
                    prompt_tokens = usage_metadata.get("promptTokenCount", 0)
                    completion_tokens = usage_metadata.get("candidatesTokenCount", 0)
                    tokens_used = prompt_tokens + completion_tokens
                    
                    # If no usage data, estimate
                    if tokens_used == 0:
                        tokens_used = self._estimate_tokens(prompt + content)
                    
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
                        finish_reason=candidates[0].get("finishReason") if candidates else None,
                        usage_metadata=usage_metadata
                    )
                
                elif response.status == 400:
                    error_msg = response_data.get("error", {}).get("message", "Bad request")
                    if "API_KEY" in error_msg:
                        raise LLMProviderAuthenticationError("Invalid Google AI API key")
                    else:
                        raise LLMProviderError(f"Google AI API error: {error_msg}")
                elif response.status == 429:
                    raise LLMProviderRateLimitError("Google AI rate limit exceeded")
                elif response.status == 403:
                    raise LLMProviderQuotaExceededError("Google AI quota exceeded")
                else:
                    error_msg = response_data.get("error", {}).get("message", "Unknown error")
                    raise LLMProviderError(f"Google AI API error: {error_msg}")
                    
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
        """Check if Google AI provider is available"""
        return bool(self.api_key and self.enabled)
    
    def get_models(self) -> List[str]:
        """Get list of available Google AI models"""
        return list(self.default_models.keys())
    
    def estimate_cost(self, text: str, model: str = None) -> float:
        """Estimate cost for processing the given text"""
        if not model:
            model = "gemini-1.5-flash"
        
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
            cost_per_1k = 0.00015  # Default to Gemini Flash pricing
        
        return (tokens / 1000) * cost_per_1k
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test connection to Google AI API"""
        if not self.api_key:
            return {
                "success": False,
                "error": "API key not configured"
            }
        
        try:
            # Test with a simple completion
            response = await self.summarize(
                "This is a test message to verify Google AI API connectivity.",
                model="gemini-1.5-flash",
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
        """Get available models from Google AI API"""
        if not self.api_key:
            return []
        
        try:
            session = await self._get_session()
            url = f"{self.base_url}/models?key={self.api_key}"
            
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    models = data.get("models", [])
                    
                    # Filter for generative models
                    generative_models = [
                        model for model in models 
                        if "generateContent" in model.get("supportedGenerationMethods", [])
                    ]
                    
                    return generative_models
                else:
                    return []
                    
        except Exception:
            return []
    
    def get_model_info(self, model: str) -> Dict[str, Any]:
        """Get detailed information about a specific model"""
        if model in self.default_models:
            info = self.default_models[model].copy()
            info["provider"] = "Google AI"
            info["model_name"] = model
            return info
        return {}
    
    async def close(self):
        """Close the aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    def __del__(self):
        """Cleanup when provider is destroyed"""
        if self.session and not self.session.closed:
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(self.close())
            except:
                pass
