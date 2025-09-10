"""
Base Cache module with Cache Abstraction
"""

from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional, Type, Dict, List, Any
from pydantic import BaseModel

from ...ports.cache import CachePort
from ...config.settings import settings

T = TypeVar('T', bound=BaseModel)


# ============================================================================
# Cache Abstraction Layer
# ============================================================================

class CacheAdapter(ABC):
    """Abstract cache adapter"""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[str]:
        """Get item from cache as string"""
        pass
    
    @abstractmethod
    async def set(self, key: str, value: str, ttl: Optional[int] = None) -> None:
        """Set item in cache with optional TTL"""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> None:
        """Delete item from cache"""
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        pass
    
    @abstractmethod
    async def clear(self) -> None:
        """Clear all cache entries"""
        pass


class RedisAdapter(CacheAdapter):
    """Redis cache adapter"""
    
    def __init__(self, url: str, **kwargs: Any):
        try:
            from redis.asyncio import from_url
            self.client = from_url(
                url=url,
                encoding="UTF-8",
                decode_responses=True,
                **kwargs
            )
        except ImportError:
            raise ImportError("Redis is not installed. Please install it with: pip install redis")
    
    async def get(self, key: str) -> Optional[str]:
        """Get item from Redis cache"""
        return await self.client.get(key)
    
    async def set(self, key: str, value: str, ttl: Optional[int] = None) -> None:
        """Set item in Redis cache with optional TTL"""
        await self.client.set(key, value, ex=ttl)
    
    async def delete(self, key: str) -> None:
        """Delete item from Redis cache"""
        await self.client.delete(key)
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in Redis cache"""
        result = await self.client.exists(key)
        return bool(result)
    
    async def clear(self) -> None:
        """Clear all Redis cache entries"""
        await self.client.flushdb()


class MemCacheAdapter(CacheAdapter):
    """MemCache adapter"""
    
    def __init__(self, servers: Optional[List[str]] = None, **kwargs: Any):
        try:
            import aiomcache
            self.servers = servers or ['127.0.0.1:11211']
            self.client = aiomcache.Client(*self.servers, **kwargs)
        except ImportError:
            raise ImportError("aiomcache is not installed. Please install it with: pip install aiomcache")
    
    async def get(self, key: str) -> Optional[str]:
        """Get item from MemCache"""
        try:
            result = await self.client.get(key.encode('utf-8'))
            return result.decode('utf-8') if result else None
        except Exception:
            return None
    
    async def set(self, key: str, value: str, ttl: Optional[int] = None) -> None:
        """Set item in MemCache with optional TTL"""
        exptime = ttl or 0  # 0 means no expiration in memcache
        await self.client.set(
            key.encode('utf-8'),
            value.encode('utf-8'),
            exptime=exptime
        )
    
    async def delete(self, key: str) -> None:
        """Delete item from MemCache"""
        await self.client.delete(key.encode('utf-8'))
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in MemCache"""
        result = await self.get(key)
        return result is not None
    
    async def clear(self) -> None:
        """Clear all MemCache entries"""
        await self.client.flush_all()


class InMemoryAdapter(CacheAdapter):
    """In-memory cache adapter for testing/development"""
    
    def __init__(self):
        self._cache: Dict[str, str] = {}
    
    async def get(self, key: str) -> Optional[str]:
        """Get item from in-memory cache"""
        return self._cache.get(key)
    
    async def set(self, key: str, value: str, ttl: Optional[int] = None) -> None:
        """Set item in in-memory cache (TTL not implemented)"""
        self._cache[key] = value
    
    async def delete(self, key: str) -> None:
        """Delete item from in-memory cache"""
        self._cache.pop(key, None)
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in in-memory cache"""
        return key in self._cache
    
    async def clear(self) -> None:
        """Clear all in-memory cache entries"""
        self._cache.clear()


class CacheFactory:
    """Factory for creating cache adapters"""
    
    _adapters = {
        'redis': RedisAdapter,
        'memcache': MemCacheAdapter,
        'memory': InMemoryAdapter,
    }
    
    @classmethod
    def create_adapter(cls, cache_type: str, **config: Any) -> CacheAdapter:
        """Create a cache adapter"""
        if cache_type.lower() not in cls._adapters:
            raise ValueError(f"Unsupported cache type: {cache_type}. Supported: {list(cls._adapters.keys())}")
        
        adapter_class = cls._adapters[cache_type.lower()]
        
        if cache_type.lower() == 'redis':
            url = config.get('url', settings.redis_url)
            return adapter_class(url=url)
        elif cache_type.lower() == 'memcache':
            servers = config.get('servers', ['127.0.0.1:11211'])
            return adapter_class(servers=servers)
        elif cache_type.lower() == 'memory':
            return adapter_class()
        
        return adapter_class(**config)
    
    @classmethod
    def register_adapter(cls, name: str, adapter_class: Type[CacheAdapter]) -> None:
        """Register a new cache adapter"""
        cls._adapters[name.lower()] = adapter_class


# ============================================================================
# Base Cache Implementation
# ============================================================================

class BaseCache(CachePort[T], Generic[T]):
    """Base cache class with multi-backend support"""
    
    def __init__(
        self,
        model: Type[T],
        cache_type: str = "redis",
        ttl: Optional[int] = None,
        **cache_config: Any
    ):
        """Initialize cache with model and adapter"""
        self.model = model
        self.ttl = ttl or getattr(settings, 'cache_ttl', getattr(settings, 'redis_ttl', 3600))
        self.cache_adapter = CacheFactory.create_adapter(cache_type, **cache_config)

    async def get(self, key: str) -> Optional[T]:
        """Get item from cache"""
        data = await self.cache_adapter.get(key)
        
        if data:
            try:
                return self.model.model_validate_json(data)
            except Exception:
                # If deserialization fails, remove the corrupted entry
                await self.cache_adapter.delete(key)
        
        return None

    async def set(self, key: str, data: T) -> None:
        """Set item in cache"""
        json_data = data.model_dump_json()
        await self.cache_adapter.set(key, json_data, self.ttl)

    async def delete(self, key: str) -> None:
        """Delete item from cache"""
        await self.cache_adapter.delete(key)
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        return await self.cache_adapter.exists(key)
    
    async def clear(self) -> None:
        """Clear all cache entries"""
        await self.cache_adapter.clear()