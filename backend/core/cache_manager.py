"""
Cache management for API responses.
Supports both disk-based and Redis caching with configurable TTL.
"""
import asyncio
import hashlib
import json
import pickle
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union

import diskcache
from pydantic import BaseModel

from config.settings import settings
from utils.logger import logger


class CacheEntry(BaseModel):
    """Cache entry model with metadata."""
    data: Any
    created_at: datetime
    expires_at: Optional[datetime] = None
    access_count: int = 0
    last_accessed: datetime


class CacheManagerBase(ABC):
    """Abstract base class for cache managers."""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with optional TTL."""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        pass
    
    @abstractmethod
    async def clear(self) -> bool:
        """Clear all cache entries."""
        pass
    
    @abstractmethod
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        pass


class DiskCacheManager(CacheManagerBase):
    """Disk-based cache manager using diskcache."""
    
    def __init__(self, cache_dir: str = None, max_size: int = None):
        self.cache_dir = cache_dir or str(settings.cache_path)
        self.max_size = max_size or settings.cache_max_size
        self._cache = diskcache.Cache(
            self.cache_dir,
            size_limit=self.max_size * 1024 * 1024  # Convert to bytes
        )
        logger.info(f"Initialized disk cache at {self.cache_dir}")
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from disk cache."""
        try:
            entry_data = self._cache.get(key)
            if entry_data is None:
                return None
            
            # Update access statistics
            entry = CacheEntry(**entry_data)
            entry.access_count += 1
            entry.last_accessed = datetime.now()
            
            # Check if expired
            if entry.expires_at and datetime.now() > entry.expires_at:
                await self.delete(key)
                return None
            
            # Update cache with new access stats
            self._cache.set(key, entry.dict())
            return entry.data
            
        except Exception as e:
            logger.error(f"Error getting cache key {key}: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in disk cache."""
        try:
            ttl = ttl or settings.cache_ttl
            expires_at = datetime.now() + timedelta(seconds=ttl) if ttl > 0 else None
            
            entry = CacheEntry(
                data=value,
                created_at=datetime.now(),
                expires_at=expires_at,
                access_count=0,
                last_accessed=datetime.now()
            )
            
            self._cache.set(key, entry.dict())
            logger.debug(f"Cached key {key} with TTL {ttl}")
            return True
            
        except Exception as e:
            logger.error(f"Error setting cache key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from disk cache."""
        try:
            return self._cache.delete(key)
        except Exception as e:
            logger.error(f"Error deleting cache key {key}: {e}")
            return False
    
    async def clear(self) -> bool:
        """Clear all disk cache entries."""
        try:
            self._cache.clear()
            logger.info("Cleared all cache entries")
            return True
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return False
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get disk cache statistics."""
        try:
            stats = {
                "type": "disk",
                "directory": self.cache_dir,
                "size": len(self._cache),
                "max_size": self.max_size,
                "volume": self._cache.volume(),
                "hits": getattr(self._cache, 'hits', 0),
                "misses": getattr(self._cache, 'misses', 0)
            }
            
            # Calculate hit rate
            total_requests = stats["hits"] + stats["misses"]
            stats["hit_rate"] = stats["hits"] / total_requests if total_requests > 0 else 0
            
            return stats
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {"type": "disk", "error": str(e)}


class RedisCacheManager(CacheManagerBase):
    """Redis-based cache manager (for future implementation)."""
    
    def __init__(self, host: str = None, port: int = None, db: int = None):
        self.host = host or settings.redis_host
        self.port = port or settings.redis_port
        self.db = db or settings.redis_db
        # TODO: Initialize Redis connection
        logger.info(f"Redis cache manager initialized (not implemented)")
    
    async def get(self, key: str) -> Optional[Any]:
        # TODO: Implement Redis get
        raise NotImplementedError("Redis cache not implemented yet")
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        # TODO: Implement Redis set
        raise NotImplementedError("Redis cache not implemented yet")
    
    async def delete(self, key: str) -> bool:
        # TODO: Implement Redis delete
        raise NotImplementedError("Redis cache not implemented yet")
    
    async def clear(self) -> bool:
        # TODO: Implement Redis clear
        raise NotImplementedError("Redis cache not implemented yet")
    
    async def get_stats(self) -> Dict[str, Any]:
        # TODO: Implement Redis stats
        return {"type": "redis", "status": "not_implemented"}


class CacheManager:
    """Main cache manager that delegates to specific implementations."""
    
    def __init__(self):
        self._manager = self._create_manager()
    
    def _create_manager(self) -> CacheManagerBase:
        """Create appropriate cache manager based on settings."""
        if settings.cache_type == "redis":
            return RedisCacheManager()
        else:
            return DiskCacheManager()
    
    def _generate_cache_key(self, data: Union[str, Dict, List]) -> str:
        """Generate consistent cache key from data."""
        if isinstance(data, str):
            content = data
        else:
            # Convert to JSON string for consistent hashing
            content = json.dumps(data, sort_keys=True, ensure_ascii=False)
        
        # Create hash
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        return await self._manager.get(key)
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache."""
        return await self._manager.set(key, value, ttl)
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        return await self._manager.delete(key)
    
    async def clear(self) -> bool:
        """Clear all cache entries."""
        return await self._manager.clear()
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return await self._manager.get_stats()
    
    async def get_or_set(
        self, 
        key: str, 
        factory_func, 
        ttl: Optional[int] = None,
        *args, 
        **kwargs
    ) -> Any:
        """Get value from cache or compute and cache it."""
        # Try to get from cache first
        cached_value = await self.get(key)
        if cached_value is not None:
            logger.debug(f"Cache hit for key: {key}")
            return cached_value
        
        # Cache miss - compute value
        logger.debug(f"Cache miss for key: {key}")
        if asyncio.iscoroutinefunction(factory_func):
            value = await factory_func(*args, **kwargs)
        else:
            value = factory_func(*args, **kwargs)
        
        # Cache the computed value
        await self.set(key, value, ttl)
        return value
    
    def create_messages_key(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Create cache key for chat messages."""
        # Include model and other parameters in the key
        cache_data = {
            "messages": messages,
            "model": settings.openai_model,
            "temperature": settings.openai_temperature,
            **kwargs
        }
        return self._generate_cache_key(cache_data)


# Global cache manager instance
cache_manager = CacheManager()
