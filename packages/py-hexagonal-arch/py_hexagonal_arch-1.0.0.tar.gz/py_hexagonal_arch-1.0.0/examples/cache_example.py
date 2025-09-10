"""
Cache Usage Examples

This example demonstrates how to use the refactored cache system
with different backends (Redis, MemCache, In-Memory).
"""

import asyncio
from typing import Optional
from pydantic import BaseModel

# Import the cache components
from src.adapters.caches.base import BaseCache, CacheFactory
from src.adapters.caches.user import UserCache
from src.models.user import User


class Product(BaseModel):
    """Example product model"""
    id: str
    name: str
    price: float
    category: str


class ProductCache(BaseCache[Product]):
    """Product-specific cache implementation"""
    
    def __init__(self, cache_type: str = "redis", **kwargs):
        super().__init__(
            model=Product,
            cache_type=cache_type,
            **kwargs
        )


async def example_redis_cache():
    """Example using Redis cache"""
    print("=== Redis Cache Example ===")
    
    # Create a user cache with Redis backend
    user_cache = UserCache(cache_type="redis")
    
    # Create a test user
    user = User(id="1", name="John Doe", email="john@example.com")
    
    # Store in cache
    await user_cache.set("user:1", user)
    print(f"Stored user: {user}")
    
    # Retrieve from cache
    cached_user = await user_cache.get("user:1")
    print(f"Retrieved user: {cached_user}")
    
    # Check if exists
    exists = await user_cache.exists("user:1")
    print(f"User exists in cache: {exists}")
    
    # Delete from cache
    await user_cache.delete("user:1")
    
    # Verify deletion
    cached_user_after_delete = await user_cache.get("user:1")
    print(f"User after deletion: {cached_user_after_delete}")
    print()


async def example_memcache():
    """Example using MemCache"""
    print("=== MemCache Example ===")
    
    try:
        # Create a product cache with MemCache backend
        product_cache = ProductCache(
            cache_type="memcache",
            servers=["127.0.0.1:11211"],
            ttl=1800
        )
        
        # Create a test product
        product = Product(
            id="prod-1",
            name="Laptop",
            price=999.99,
            category="Electronics"
        )
        
        # Store in cache
        await product_cache.set("product:prod-1", product)
        print(f"Stored product: {product}")
        
        # Retrieve from cache
        cached_product = await product_cache.get("product:prod-1")
        print(f"Retrieved product: {cached_product}")
        
        # Check if exists
        exists = await product_cache.exists("product:prod-1")
        print(f"Product exists in cache: {exists}")
        
    except ImportError as e:
        print(f"MemCache not available: {e}")
    except Exception as e:
        print(f"MemCache error (server might not be running): {e}")
    
    print()


async def example_memory_cache():
    """Example using in-memory cache"""
    print("=== In-Memory Cache Example ===")
    
    # Create a user cache with in-memory backend
    user_cache = UserCache(cache_type="memory")
    
    # Create test users
    users = [
        User(id="1", name="Alice", email="alice@example.com"),
        User(id="2", name="Bob", email="bob@example.com"),
        User(id="3", name="Charlie", email="charlie@example.com")
    ]
    
    # Store multiple users
    for user in users:
        await user_cache.set(f"user:{user.id}", user)
        print(f"Stored user: {user.name}")
    
    # Retrieve all users
    print("\nRetrieving users:")
    for i in range(1, 4):
        cached_user = await user_cache.get(f"user:{i}")
        if cached_user:
            print(f"Retrieved user {i}: {cached_user.name}")
    
    # Clear all cache
    await user_cache.clear()
    print("\nCache cleared")
    
    # Verify cache is empty
    cached_user = await user_cache.get("user:1")
    print(f"User after clear: {cached_user}")
    print()


async def example_factory_usage():
    """Example showing direct factory usage"""
    print("=== Factory Usage Example ===")
    
    # Create different cache adapters directly
    redis_adapter = CacheFactory.create_adapter("redis")
    memory_adapter = CacheFactory.create_adapter("memory")
    
    # Use adapters directly (string-based operations)
    await redis_adapter.set("test_key", "Hello Redis!", ttl=60)
    await memory_adapter.set("test_key", "Hello Memory!")
    
    # Retrieve values
    redis_value = await redis_adapter.get("test_key")
    memory_value = await memory_adapter.get("test_key")
    
    print(f"Redis value: {redis_value}")
    print(f"Memory value: {memory_value}")
    
    print()


async def example_custom_adapter():
    """Example showing how to register a custom adapter"""
    print("=== Custom Adapter Example ===")
    
    from src.adapters.caches.base import CacheAdapter
    
    class LoggingCacheAdapter(CacheAdapter):
        """A cache adapter that logs all operations"""
        
        def __init__(self):
            self._cache = {}
        
        async def get(self, key: str) -> Optional[str]:
            print(f"[LOG] Getting key: {key}")
            return self._cache.get(key)
        
        async def set(self, key: str, value: str, ttl: Optional[int] = None) -> None:
            print(f"[LOG] Setting key: {key}, TTL: {ttl}")
            self._cache[key] = value
        
        async def delete(self, key: str) -> None:
            print(f"[LOG] Deleting key: {key}")
            self._cache.pop(key, None)
        
        async def exists(self, key: str) -> bool:
            exists = key in self._cache
            print(f"[LOG] Checking existence of key: {key}, exists: {exists}")
            return exists
        
        async def clear(self) -> None:
            print("[LOG] Clearing all cache")
            self._cache.clear()
    
    # Register the custom adapter
    CacheFactory.register_adapter("logging", LoggingCacheAdapter)
    
    # Use the custom adapter
    user_cache = UserCache(cache_type="logging")
    
    user = User(id="1", name="Test User", email="test@example.com")
    await user_cache.set("user:1", user)
    retrieved_user = await user_cache.get("user:1")
    await user_cache.exists("user:1")
    await user_cache.delete("user:1")
    
    print()


async def main():
    """Run all examples"""
    print("Cache System Examples")
    print("=" * 50)
    
    # Run examples
    await example_redis_cache()
    await example_memcache()
    await example_memory_cache()
    await example_factory_usage()
    await example_custom_adapter()
    
    print("All examples completed!")


if __name__ == "__main__":
    asyncio.run(main())
