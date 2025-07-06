"""
Enhanced Ollama LLM Provider
Implements local Ollama models for news summarization with improved features
"""

import asyncio
import aiohttp
import json
import time
import subprocess
import requests
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
            "qwen3:8b": {"cost_per_1k_tokens": 0.0, "max_tokens": 8192},
            "llama3:8b": {"cost_per_1k_tokens": 0.0, "max_tokens": 8192},
            "gemma3:4b": {"cost_per_1k_tokens": 0.0, "max_tokens": 4096},
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
            # Create session without timeout - we'll handle timeout per request
            self.session = aiohttp.ClientSession()
        return self.session

    async def close_session(self):
        """Close the aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()
            self.session = None
    
    async def summarize(self, text: str, **kwargs) -> LLMResponse:
        """Summarize text using Ollama models"""
        # Use synchronous method to avoid async context issues with Flask
        return self._summarize_sync(text, **kwargs)

    def _summarize_sync(self, text: str, **kwargs) -> LLMResponse:
        """Synchronous fallback for summarization"""
        model = kwargs.get('model')
        if not model:
            # Get the first available model from actual Ollama installation
            available_models = self.get_models()
            if available_models:
                # Prefer models in this order: qwen3:8b, llama3:8b, gemma3:4b, then any other
                preferred_order = ['qwen3:8b', 'llama3:8b', 'gemma3:4b']
                for preferred in preferred_order:
                    if preferred in available_models:
                        model = preferred
                        break
                else:
                    model = available_models[0]
            else:
                # Fallback to a reasonable default
                model = 'qwen3:8b'
        else:
            # Validate that the specified model is available
            available_models = self.get_models()
            if available_models and model not in available_models:
                print(f"⚠️ Specified model '{model}' not available. Available models: {available_models}")
                # Fall back to first available model
                model = available_models[0] if available_models else "llama3:8b"
                print(f"   Using fallback model: {model}")
        max_tokens = kwargs.get('max_tokens', 150)
        temperature = kwargs.get('temperature', 0.3)

        # Check if Ollama is available
        if not self.is_available():
            return self._create_response(
                content="", model=model, tokens_used=0, cost=0.0,
                response_time=0.0, success=False,
                error_message="Ollama service is not available"
            )

        start_time = time.time()

        # Create prompt for summarization
        prompt = f"""Read this news article and write a 2-3 sentence summary. Do not include any introductory phrases like "Here is" or "This is". Do not use thinking tags like <think> or show your reasoning process. Start directly with the facts:

{text[:2000]}

Summary:"""

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }

        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=self.config.timeout
            )

            response_time = time.time() - start_time

            if response.status_code == 200:
                response_data = response.json()
                content = response_data.get("response", "").strip()

                # Clean up reasoning model output and prefixes
                content = self._clean_reasoning_output(content)
                content = self._clean_summary_prefixes(content)

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
                raise LLMProviderError(f"Ollama API error: {response.text}")

        except requests.RequestException as e:
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

    async def _summarize_async(self, text: str, **kwargs) -> LLMResponse:
        """Async version of summarization"""
        model = kwargs.get('model')
        if not model:
            # Get the first available model from actual Ollama installation
            available_models = self.get_models()
            if available_models:
                # Prefer models in this order: qwen3:8b, llama3:8b, gemma3:4b, then any other
                preferred_order = ['qwen3:8b', 'llama3:8b', 'gemma3:4b']
                for preferred in preferred_order:
                    if preferred in available_models:
                        model = preferred
                        break
                else:
                    model = available_models[0]
            else:
                # Fallback to a reasonable default
                model = 'qwen3:8b'
        else:
            # Validate that the specified model is available
            available_models = self.get_models()
            if available_models and model not in available_models:
                print(f"⚠️ Specified model '{model}' not available. Available models: {available_models}")
                # Fall back to first available model
                model = available_models[0] if available_models else "llama3:8b"
                print(f"   Using fallback model: {model}")
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
        prompt = f"""Read this news article and write a 2-3 sentence summary. Do not include any introductory phrases like "Here is" or "This is". Do not use thinking tags like <think> or show your reasoning process. Start directly with the facts:

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
            
            # Create timeout for this specific request
            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            async with session.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=timeout
            ) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    response_data = await response.json()
                    content = response_data.get("response", "").strip()

                    # Clean up reasoning model output and prefixes
                    content = self._clean_reasoning_output(content)
                    content = self._clean_summary_prefixes(content)

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
            
            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            async with session.post(
                f"{self.base_url}/api/pull",
                json=payload,
                timeout=timeout
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
            
            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            async with session.post(
                f"{self.base_url}/api/show",
                json={"name": model},
                timeout=timeout
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
            
            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            async with session.get(f"{self.base_url}/api/tags", timeout=timeout) as response:
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
    
    def _clean_reasoning_output(self, content: str) -> str:
        """Clean reasoning model output to extract the final answer"""
        if not content:
            return content

        import re

        # Handle models that use <think> tags (like qwen3)
        if '<think>' in content:
            if '</think>' in content:
                # Extract content after </think> tag
                parts = content.split('</think>')
                if len(parts) > 1:
                    content = parts[-1].strip()
                else:
                    # If no content after </think>, try to extract from before
                    content = ""
            else:
                # If only <think> tag without closing, the output is incomplete
                # This often happens with reasoning models that get cut off
                print(f"⚠️ Incomplete reasoning output detected: {content[:100]}...")
                return "Summary unavailable due to incomplete model response."

        # Handle models that output thinking without tags
        # Remove common reasoning patterns at the start
        reasoning_start_patterns = [
            r'^<think>.*?</think>\s*',  # Remove complete think blocks
            r'^<think>.*',  # Remove incomplete think blocks
            r'^(okay|alright|well|so|hmm),?\s+.*?(?=\.|$)',
            r'^(let me|i need to|i should|i\'ll|i will)\s+.*?(?=\.|$)',
            r'^(the user wants|they specified|they asked).*?(?=\.|$)',
            r'^(thinking|considering|analyzing).*?(?=\.|$)',
            r'^(let me read|let me think|let me consider).*?(?=\.|$)',
        ]

        for pattern in reasoning_start_patterns:
            content = re.sub(pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
            content = content.strip()

        # Handle line-by-line reasoning patterns
        lines = content.split('\n')
        cleaned_lines = []

        # Skip lines that look like reasoning/thinking
        reasoning_line_patterns = [
            r'^(okay|alright|well|so|hmm),?\s+',
            r'^(let me|i need to|i should|i\'ll|i will)\s+',
            r'^(first|second|third|next|then|finally),?\s+',
            r'^(the user wants|they specified|they asked)\s+',
            r'^(thinking|considering|analyzing)\s+',
            r'^(let me read|let me think|let me consider)\s+',
            r'^\s*\*\s*(thinking|reasoning|analysis)',
            r'^\s*\[thinking\]',
            r'^\s*\(thinking\)',
            r'^\s*<think>',
            r'^\s*</think>',
        ]

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Skip lines that match reasoning patterns
            is_reasoning = False
            for pattern in reasoning_line_patterns:
                if re.match(pattern, line, re.IGNORECASE):
                    is_reasoning = True
                    break

            if not is_reasoning:
                cleaned_lines.append(line)

        if cleaned_lines:
            content = ' '.join(cleaned_lines)

        # Final cleanup for remaining reasoning artifacts
        final_cleanup_patterns = [
            r'^(okay|alright|well|so|hmm),?\s+',
            r'^(let me|i need to|i should)\s+[^.]*\.\s*',
            r'^(the user wants|they specified|they asked)[^.]*\.\s*',
            r'^(first|second|third|next|then|finally),?\s+[^.]*\.\s*',
            r'\s*<think>.*?</think>\s*',  # Remove any remaining think blocks
            r'\s*<think>.*',  # Remove incomplete think blocks
        ]

        for pattern in final_cleanup_patterns:
            content = re.sub(pattern, '', content, flags=re.IGNORECASE | re.DOTALL)

        content = content.strip()

        # If content is empty or too short after cleaning, return a fallback
        if not content or len(content) < 10:
            return "Summary unavailable due to reasoning model output issues."

        return content

    def _clean_summary_prefixes(self, content: str) -> str:
        """Remove common AI-generated prefixes from summaries"""
        # List of common prefixes to remove
        prefixes_to_remove = [
            "Here is a summary of the article in 2-3 clear sentences:",
            "Here is a summary of the article in 2-3 sentences:",
            "Here is a concise summary of the article in 2-3 sentences:",
            "Here is a summary of the article:",
            "Here is a concise summary:",
            "Here's a summary:",
            "Here's a concise summary:",
            "This is a summary:",
            "The article discusses:",
            "Summary:",
            "Article summary:",
            "In summary:",
            "To summarize:",
            "Here is",
            "Here's",
            "This is",
            "The article"
        ]

        # Clean the content
        cleaned_content = content.strip()

        # Remove prefixes (case insensitive)
        for prefix in prefixes_to_remove:
            if cleaned_content.lower().startswith(prefix.lower()):
                cleaned_content = cleaned_content[len(prefix):].strip()
                # Remove any leading colon or dash
                if cleaned_content.startswith((':','-')):
                    cleaned_content = cleaned_content[1:].strip()
                break

        return cleaned_content

    def __del__(self):
        """Cleanup when provider is destroyed"""
        if self.session and not self.session.closed:
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(self.close())
            except:
                pass
