"""
py-hexagonal-arch: A comprehensive Python framework implementing Hexagonal Architecture

This package provides a complete implementation of hexagonal architecture (ports and adapters)
with support for multiple web frameworks, databases, caching systems, and event messaging.

Key Features:
- Multi-framework support: FastAPI, Flask, Tornado
- Multi-database support: PostgreSQL, MariaDB/MySQL, SQL Server, Oracle
- Multi-cache support: Redis, MemCache, In-Memory
- Multi-messaging support: Kafka, RabbitMQ, AWS Kinesis, GCP Pub/Sub
- Type safety with full type hints
- Clean architecture patterns
"""

__version__ = "1.0.0"
__author__ = "Alberto Sanmartin Martinez"
__email__ = "albertosanmartinmartinez@gmail.com"
__license__ = "MIT"

# Core imports
from .models.base import CustomModel
from .controllers.base import BaseController
from .config.settings import settings

# Repository system
from .adapters.repositories.base import BaseRepository, DatabaseFactory
from .ports.repository import RepositoryPort, FilterCondition

# Router system  
from .adapters.routers.base import BaseRouter, WebFrameworkFactory
from .ports.router import RouterPort

# Cache system
from .adapters.caches.base import BaseCache, CacheFactory
from .ports.cache import CachePort

# Event system
from .adapters.events.base import BaseEvent, EventFactory, EventMessage
from .ports.event import EventPort

# Version info
VERSION = __version__
VERSION_INFO = tuple(int(v) for v in __version__.split('.'))

__all__ = [
    # Version
    "__version__",
    "VERSION",
    "VERSION_INFO",
    
    # Core
    "CustomModel",
    "BaseController", 
    "settings",
    
    # Repository system
    "BaseRepository",
    "DatabaseFactory", 
    "RepositoryPort",
    "FilterCondition",
    
    # Router system
    "BaseRouter",
    "WebFrameworkFactory",
    "RouterPort",
    
    # Cache system
    "BaseCache",
    "CacheFactory",
    "CachePort",
    
    # Event system
    "BaseEvent",
    "EventFactory",
    "EventMessage",
    "EventPort",
]
