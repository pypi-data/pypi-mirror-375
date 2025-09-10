"""
User Cache module
"""

from typing import TYPE_CHECKING, Optional, Any

from .base import BaseCache
from ...models.user import User
from ...config.settings import settings


if TYPE_CHECKING:
    pass


class UserCache(BaseCache[User]):
    """User-specific cache implementation"""

    def __init__(
        self,
        cache_type: Optional[str] = None,
        ttl: Optional[int] = None,
        **cache_config: Any
    ):
        """Initialize user cache with configurable backend"""
        
        # Use settings default if not specified
        cache_type = cache_type or settings.cache_type
        
        # Use memcache-specific settings if using memcache
        if cache_type == "memcache" and "servers" not in cache_config:
            cache_config["servers"] = settings.memcache_servers
            ttl = ttl or settings.memcache_ttl
        
        super().__init__(
            model=User,
            cache_type=cache_type,
            ttl=ttl,
            **cache_config
        )