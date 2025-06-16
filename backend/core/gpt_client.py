"""
GPT API client with retry logic, rate limiting, and error handling.
"""
import asyncio
import time
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from datetime import datetime, timedelta

import aiohttp
import openai
from openai import AsyncOpenAI

from backend.config.settings import settings
from backend.core.cache_manager import cache_manager
from backend.core.token_counter import token_counter
from backend.utils.logger import logger


@dataclass
class APIUsage:
    """Track API usage statistics."""
    requests_count: int = 0
    tokens_used: int = 0
    last_request_time: Optional[datetime] = None
    errors_count: int = 0


class RateLimiter:
    """Simple rate limiter for API requests."""
    
    def __init__(self, max_requests_per_minute: int = None):
        self.max_requests = max_requests_per_minute or settings.max_requests_per_minute
        self.requests = []
    
    async def acquire(self):
        """Wait if necessary to respect rate limits."""
        now = time.time()
        
        # Remove requests older than 1 minute
        self.requests = [req_time for req_time in self.requests if now - req_time < 60]
        
        # If we're at the limit, wait
        if len(self.requests) >= self.max_requests:
            wait_time = 60 - (now - self.requests[0])
            if wait_time > 0:
                logger.info(f"Rate limit reached, waiting {wait_time:.2f} seconds")
                await asyncio.sleep(wait_time)
                return await self.acquire()  # Recursive call after waiting
        
        # Record this request
        self.requests.append(now)


class GPTClient:
    """
    Async GPT API client with caching, retry logic, and rate limiting.
    """
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.rate_limiter = RateLimiter()
        self.usage = APIUsage()
        
        # Retry configuration
        self.max_retries = 3
        self.retry_delays = [1, 2, 4]  # Exponential backoff
        
        logger.info("GPT Client initialized")
    
    async def _make_request_with_retry(
        self, 
        request_func, 
        *args, 
        **kwargs
    ) -> Any:
        """Make API request with retry logic."""
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                # Apply rate limiting
                await self.rate_limiter.acquire()
                
                # Make the request
                response = await request_func(*args, **kwargs)
                
                # Update usage statistics
                self.usage.requests_count += 1
                self.usage.last_request_time = datetime.now()
                
                if hasattr(response, 'usage') and response.usage:
                    self.usage.tokens_used += response.usage.total_tokens
                
                return response
                
            except openai.RateLimitError as e:
                logger.warning(f"Rate limit error on attempt {attempt + 1}: {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delays[attempt])
                last_exception = e
                
            except openai.APITimeoutError as e:
                logger.warning(f"Timeout error on attempt {attempt + 1}: {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delays[attempt])
                last_exception = e
                
            except openai.APIConnectionError as e:
                logger.warning(f"Connection error on attempt {attempt + 1}: {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delays[attempt])
                last_exception = e
                
            except openai.AuthenticationError as e:
                logger.error(f"Authentication error: {e}")
                self.usage.errors_count += 1
                raise  # Don't retry auth errors
                
            except openai.BadRequestError as e:
                logger.error(f"Bad request error: {e}")
                self.usage.errors_count += 1
                raise  # Don't retry bad requests
                
            except Exception as e:
                logger.error(f"Unexpected error on attempt {attempt + 1}: {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delays[attempt])
                last_exception = e
        
        # All retries failed
        self.usage.errors_count += 1
        raise last_exception
    
    async def chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        use_cache: bool = True,
        **kwargs
    ) -> Union[Dict[str, Any], AsyncIteration]:
        """
        Create a chat completion with caching and error handling.
        
        Args:
            messages: List of message dictionaries
            model: OpenAI model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            stream: Whether to stream the response
            use_cache: Whether to use caching
            **kwargs: Additional parameters for OpenAI API
        
        Returns:
            Chat completion response or async iterator for streaming
        """
        # Use default values from settings
        model = model or settings.openai_model
        temperature = temperature or settings.openai_temperature
        max_tokens = max_tokens or settings.openai_max_tokens
        
        # Validate token limits
        if not token_counter.is_within_limit(messages, max_tokens):
            logger.warning("Messages exceed token limit, truncating...")
            messages = token_counter.truncate_messages(messages, max_tokens)
        
        # Create cache key if caching is enabled
        cache_key = None
        if use_cache and not stream:
            cache_params = {
                "model": model,
                "temperature": temperature,
                "max_tokens": max_tokens,
                **kwargs
            }
            cache_key = cache_manager.create_messages_key(messages, **cache_params)
            
            # Try to get from cache
            cached_response = await cache_manager.get(cache_key)
            if cached_response is not None:
                logger.debug("Retrieved response from cache")
                return cached_response
        
        # Prepare API request
        request_params = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream,
            **kwargs
        }
        
        logger.info(f"Making chat completion request with {len(messages)} messages")
        
        try:
            # Make the API request
            response = await self._make_request_with_retry(
                self.client.chat.completions.create,
                **request_params
            )
            
            # For streaming responses, return the iterator directly
            if stream:
                return response
            
            # Convert response to dict for easier handling
            response_dict = {
                "id": response.id,
                "object": response.object,
                "created": response.created,
                "model": response.model,
                "choices": [
                    {
                        "index": choice.index,
                        "message": {
                            "role": choice.message.role,
                            "content": choice.message.content
                        },
                        "finish_reason": choice.finish_reason
                    }
                    for choice in response.choices
                ],
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                } if response.usage else None
            }
            
            # Cache the response if caching is enabled
            if use_cache and cache_key:
                await cache_manager.set(cache_key, response_dict)
                logger.debug("Cached API response")
            
            return response_dict
            
        except Exception as e:
            logger.error(f"Error in chat completion: {e}")
            raise
    
    async def get_embedding(
        self, 
        text: str, 
        model: str = "text-embedding-ada-002",
        use_cache: bool = True
    ) -> List[float]:
        """
        Get text embedding with caching.
        
        Args:
            text: Text to embed
            model: Embedding model to use
            use_cache: Whether to use caching
        
        Returns:
            List of embedding values
        """
        # Create cache key if caching is enabled
        cache_key = None
        if use_cache:
            cache_key = cache_manager._generate_cache_key({
                "text": text,
                "model": model,
                "type": "embedding"
            })
            
            # Try to get from cache
            cached_embedding = await cache_manager.get(cache_key)
            if cached_embedding is not None:
                logger.debug("Retrieved embedding from cache")
                return cached_embedding
        
        logger.info(f"Getting embedding for text (length: {len(text)})")
        
        try:
            # Make the API request
            response = await self._make_request_with_retry(
                self.client.embeddings.create,
                input=text,
                model=model
            )
            
            embedding = response.data[0].embedding
            
            # Cache the embedding if caching is enabled
            if use_cache and cache_key:
                await cache_manager.set(cache_key, embedding)
                logger.debug("Cached embedding")
            
            return embedding
            
        except Exception as e:
            logger.error(f"Error getting embedding: {e}")
            raise
    
    async def get_usage_stats(self) -> Dict[str, Any]:
        """Get API usage statistics."""
        cache_stats = await cache_manager.get_stats()
        
        return {
            "api_usage": {
                "requests_count": self.usage.requests_count,
                "tokens_used": self.usage.tokens_used,
                "errors_count": self.usage.errors_count,
                "last_request_time": self.usage.last_request_time.isoformat() if self.usage.last_request_time else None,
            },
            "cache_stats": cache_stats,
            "rate_limit": {
                "max_requests_per_minute": self.rate_limiter.max_requests,
                "current_requests_in_window": len(self.rate_limiter.requests)
            }
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform a health check on the GPT API."""
        try:
            # Simple test request
            test_messages = [{"role": "user", "content": "Hello"}]
            response = await self.chat_completion(
                messages=test_messages,
                max_tokens=10,
                use_cache=False
            )
            
            return {
                "status": "healthy",
                "api_accessible": True,
                "response_received": True,
                "test_response": response.get("choices", [{}])[0].get("message", {}).get("content", "")
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "api_accessible": False,
                "error": str(e)
            }


# Global GPT client instance
gpt_client = GPTClient()
