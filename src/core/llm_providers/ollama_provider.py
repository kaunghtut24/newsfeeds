"""
Enhanced Ollama LLM Provider
Implements local Ollama models for news summarization with improved features
"""

import asyncio
import aiohttp
import json
import time
import subprocess
from typing import Dict, List, Optional, Any

from .base_provider import (
    BaseLLMProvider, LLMResponse, LLMConfig, 
    LLMProviderError, LLMProviderUnavailableError
)


class OllamaProvider(BaseLLMProvider):
    """Enhanced Ollama provider for local LLM models"""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.base_url = config.base_url or "http://localhost:11434"
        self.session = None
        
        # Default models (cost is 0 for local models)
        self.default_models = {
            "llama3:8b": {"cost_per_1k_tokens": 0.0, "max_tokens": 8192},
            "llama3:70b": {"cost_per_1k_tokens": 0.0, "max_tokens": 8192},
            "mistral:7b": {"cost_per_1k_tokens": 0.0, "max_tokens": 8192},
            "mistral:latest": {"cost_per_1k_tokens": 0.0, "max_tokens": 8192},
            "codellama:7b": {"cost_per_1k_tokens": 0.0, "max_tokens": 8192},
            "gemma:7b": {"cost_per_1k_tokens": 0.0, "max_tokens": 8192},
            "phi3:mini": {"cost_per_1k_tokens": 0.0, "max_tokens": 4096},
            "qwen2:7b": {"cost_per_1k_tokens": 0.0, "max_tokens": 8192}
        }
        
        if config.models:
            self.default_models.update(config.models)
    
    async def _get_session(self):
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            self.session = aiohttp.ClientSession(timeout=timeout)
        return self.session
    
    async def summarize(self, text: str, **kwargs) -> LLMResponse:
        """Summarize text using Ollama models"""
        model = kwargs.get('model')
        if not model:
            # Get the first available model
            available_models = self.get_models()
            model = available_models[0] if available_models else 'llama3:8b'
        max_tokens = kwargs.get('max_tokens', 150)
        temperature = kwargs.get('temperature', 0.3)
        
        # Check if Ollama is available
        if not self.is_available():
            return self._create_response(
                content="", model=model, tokens_used=0, cost=0.0, 
                response_time=0.0, success=False,
                error_message="Ollama service is not available"
            )
        
        # Prepare the prompt
        prompt = f"""You are a professional news summarizer. Create a concise, informative summary of the following news article in 2-3 sentences. Focus on the key facts, main points, and important details. Be objective and factual.

News Article:
{text}

Summary:"""
        
        # Prepare request payload
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
                "top_p": 0.9,
                "top_k": 40
            }
        }
        
        start_time = time.time()
        
        try:
            session = await self._get_session()
            
            async with session.post(
                f"{self.base_url}/api/generate",
                json=payload
            ) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    response_data = await response.json()
                    content = response_data.get("response", "").strip()
                    
                    # Estimate tokens (Ollama doesn't provide exact counts)
                    tokens_used = self._estimate_tokens(prompt + content)
                    
                    # Cost is always 0 for local models
                    cost = 0.0
                    
                    # Update provider stats
                    self.total_tokens += tokens_used
                    
                    return self._create_response(
                        content=content,
                        model=model,
                        tokens_used=tokens_used,
                        cost=cost,
                        response_time=response_time,
                        success=True,
                        done=response_data.get("done", True),
                        context=response_data.get("context", [])
                    )
                else:
                    error_text = await response.text()
                    raise LLMProviderError(f"Ollama API error: {error_text}")
                    
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
        """Check if Ollama service is available"""
        if not self.enabled:
            return False
        
        try:
            # Try to connect to Ollama API
            result = subprocess.run(
                ['curl', '-s', f'{self.base_url}/api/tags'],
                capture_output=True, text=True, timeout=5
            )
            return result.returncode == 0
        except:
            return False
    
    def get_models(self) -> List[str]:
        """Get list of available Ollama models"""
        try:
            # Get models from Ollama API
            result = subprocess.run(
                ['curl', '-s', f'{self.base_url}/api/tags'],
                capture_output=True, text=True, timeout=5
            )
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                models = [model['name'] for model in data.get('models', [])]
                return models
            else:
                # Fallback to default models
                return list(self.default_models.keys())
        except:
            return list(self.default_models.keys())
    
    def estimate_cost(self, text: str, model: str = None) -> float:
        """Estimate cost for processing (always 0 for local models)"""
        return 0.0
    
    async def pull_model(self, model: str) -> Dict[str, Any]:
        """Pull a model from Ollama registry"""
        try:
            session = await self._get_session()
            
            payload = {"name": model}
            
            async with session.post(
                f"{self.base_url}/api/pull",
                json=payload
            ) as response:
                if response.status == 200:
                    return {"success": True, "message": f"Model {model} pulled successfully"}
                else:
                    error_text = await response.text()
                    return {"success": False, "error": error_text}
                    
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def delete_model(self, model: str) -> Dict[str, Any]:
        """Delete a model from Ollama"""
        try:
            session = await self._get_session()
            
            async with session.delete(
                f"{self.base_url}/api/delete",
                json={"name": model}
            ) as response:
                if response.status == 200:
                    return {"success": True, "message": f"Model {model} deleted successfully"}
                else:
                    error_text = await response.text()
                    return {"success": False, "error": error_text}
                    
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_model_info(self, model: str) -> Dict[str, Any]:
        """Get detailed information about a model"""
        try:
            session = await self._get_session()
            
            async with session.post(
                f"{self.base_url}/api/show",
                json={"name": model}
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {}
                    
        except Exception:
            return {}
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test connection to Ollama service"""
        try:
            session = await self._get_session()
            
            async with session.get(f"{self.base_url}/api/tags") as response:
                if response.status == 200:
                    data = await response.json()
                    models = [model['name'] for model in data.get('models', [])]
                    return {
                        "success": True,
                        "available_models": models,
                        "model_count": len(models)
                    }
                else:
                    return {
                        "success": False,
                        "error": f"HTTP {response.status}"
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def check_ollama_service(self) -> Dict[str, Any]:
        """Check if Ollama service is running using subprocess"""
        try:
            result = subprocess.run(
                ['ollama', 'list'], 
                capture_output=True, text=True, timeout=5
            )
            
            if result.returncode == 0:
                # Parse model list
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                models = []
                for line in lines:
                    if line.strip():
                        model_name = line.split()[0]
                        models.append(model_name)
                
                return {
                    "success": True,
                    "service_running": True,
                    "available_models": models
                }
            else:
                return {
                    "success": False,
                    "service_running": False,
                    "error": result.stderr
                }
                
        except FileNotFoundError:
            return {
                "success": False,
                "service_running": False,
                "error": "Ollama command not found"
            }
        except Exception as e:
            return {
                "success": False,
                "service_running": False,
                "error": str(e)
            }
    
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
