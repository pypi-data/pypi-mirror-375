# Python Hexagonal Architecture Package

A Python package implementing hexagonal architecture pattern with multi-framework web support.

## Features

- ✅ **Hexagonal Architecture**: Clean separation of concerns with ports and adapters
- ✅ **Multi-Framework Support**: FastAPI, Flask, and Tornado support out of the box
- ✅ **Base Controllers**: Generic CRUD operations with filtering
- ✅ **Multi-Database Support**: PostgreSQL, MariaDB, SQL Server, Oracle
- ✅ **Multi-Messaging Support**: Kafka, RabbitMQ, AWS Kinesis, GCP Pub/Sub
- ✅ **Multi-Cache Support**: Redis, MemCache, and In-Memory caching
- ✅ **Type Safety**: Full type hints support

## Structure

```bash
src/
├── adapters/           # External adapters (web, db, cache, etc.)
│   ├── routers/       # Web framework routers
│   ├── repositories/  # Data access implementations
│   ├── caches/        # Cache implementations
│   └── events/        # Event handlers
├── controllers/        # Application controllers
├── models/            # Domain models
├── ports/             # Application ports (interfaces)
├── schemas/           # Data schemas
└── config/            # Configuration
```

## Installation

### Quick Install

```bash
# Basic installation (includes PostgreSQL and FastAPI)
pip install py-hexagonal-arch

# Install with specific extras
pip install py-hexagonal-arch[redis,kafka,flask]

# Install everything (all adapters)
pip install py-hexagonal-arch[all]
```

### Available Extras

```bash
# Web frameworks
pip install py-hexagonal-arch[flask]      # Flask support
pip install py-hexagonal-arch[tornado]    # Tornado support

# Databases  
pip install py-hexagonal-arch[mysql]      # MariaDB/MySQL support
pip install py-hexagonal-arch[sqlserver]  # SQL Server support
pip install py-hexagonal-arch[oracle]     # Oracle support

# Cache systems
pip install py-hexagonal-arch[redis]      # Redis support
pip install py-hexagonal-arch[memcache]   # MemCache support

# Event messaging
pip install py-hexagonal-arch[kafka]      # Kafka support
pip install py-hexagonal-arch[rabbitmq]   # RabbitMQ support  
pip install py-hexagonal-arch[kinesis]    # AWS Kinesis support
pip install py-hexagonal-arch[pubsub]     # GCP Pub/Sub support

# Development tools
pip install py-hexagonal-arch[dev]        # Development dependencies
pip install py-hexagonal-arch[docs]       # Documentation tools
```

## Quick Start

### 1. Create a Model

```python
from py_hexagonal_arch import CustomModel
from typing import Optional

class User(CustomModel):
    id: Optional[str] = None
    name: str
    email: str
    age: int
```

### 2. Create a Controller

```python
from py_hexagonal_arch import BaseController

class UserController(BaseController[User]):
    # Implement your business logic
    pass
```

### 3. Set Up Repository

```python
from py_hexagonal_arch import BaseRepository

class UserRepository(BaseRepository[User]):
    def __init__(self):
        super().__init__(model=User, schema=UserSchema)

# PostgreSQL (default)
user_repo = UserRepository()

# MariaDB/MySQL
user_repo = UserRepository(db_type="mariadb")

# SQL Server
user_repo = UserRepository(db_type="sqlserver")

# Oracle
user_repo = UserRepository(db_type="oracle")

# Basic operations
user = User(name="John", email="john@example.com")
created_user = await user_repo.create(user)
users = await user_repo.list()
```

📖 **For detailed repository documentation, configuration, and advanced usage, see: [`src/adapters/repositories/README.md`](src/adapters/repositories/README.md)**

### 4. Create a Router

```python
from py_hexagonal_arch import BaseRouter

# FastAPI (default)
user_router = BaseRouter(
    model=User,
    controller=UserController,
    prefix="/users",
    tags=["users"]
)

# Flask
user_router = BaseRouter(
    model=User,
    controller=UserController,
    prefix="/users",
    tags=["users"],
    framework="flask"
)

# Tornado
user_router = BaseRouter(
    model=User,
    controller=UserController,
    prefix="/users",
    tags=["users"],
    framework="tornado"
)
```

📖 **For detailed router documentation, patterns, and advanced usage, see: [`src/adapters/routers/README.md`](src/adapters/routers/README.md)**

### 5. Set Up Caching

```python
from py_hexagonal_arch import BaseCache

class UserCache(BaseCache[User]):
    def __init__(self):
        super().__init__(model=User)

# Redis (default)
user_cache = UserCache()

# MemCache
user_cache = UserCache(
    cache_type="memcache",
    servers=["localhost:11211"]
)

# In-Memory (for testing)
user_cache = UserCache(cache_type="memory")

# Usage
user = User(id="1", name="John", email="john@example.com", age=30)
await user_cache.set("user:1", user)
cached_user = await user_cache.get("user:1")
```

📖 **For detailed cache documentation, patterns, and advanced usage, see: [`src/adapters/caches/README.md`](src/adapters/caches/README.md)**

### 6. Set Up Events

```python
from py_hexagonal_arch import BaseEvent

class UserEvent(BaseEvent[User]):
    def __init__(self):
        super().__init__(model=User)

# Kafka (default)
user_events = UserEvent()

# RabbitMQ
user_events = UserEvent(event_type="rabbitmq")

# AWS Kinesis
user_events = UserEvent(event_type="kinesis")

# Basic operations
await user_events.push("created", user, key=user.id)
async for user_data in user_events.pull("created"):
    print(f"User event: {user_data.name}")
```

📖 **For detailed event documentation, patterns, and advanced usage, see: [`src/adapters/events/README.md`](src/adapters/events/README.md)**

## Examples

See the `examples/` directory for complete working examples with each framework and caching system.

- `fastapi_example.py` - FastAPI implementation
- `flask_example.py` - Flask implementation  
- `tornado_example.py` - Tornado implementation
- `repositories_example.py` - Multi-database repository examples
- `cache_example.py` - Comprehensive caching examples
- `events_example.py` - Multi-backend event messaging examples

## License

MIT License
