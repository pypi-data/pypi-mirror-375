# Repository System Documentation

The repository system provides a flexible multi-database abstraction layer following hexagonal architecture principles. It supports multiple SQL databases with a consistent API and automatic configuration.

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Supported Databases](#supported-databases)
- [Quick Start](#quick-start)
- [Database Adapters](#database-adapters)
- [Configuration](#configuration)
- [Advanced Usage](#advanced-usage)
- [Custom Adapters](#custom-adapters)
- [Error Handling](#error-handling)
- [Best Practices](#best-practices)

## Architecture Overview

The repository system follows the Adapter pattern with these core components:

```
RepositoryPort (Interface)
    ↓
BaseRepository (Implementation)
    ↓
DatabaseAdapter (Abstraction)
    ↓
[PostgreSQL|MariaDB|SQLServer|Oracle]Adapter (Concrete Implementations)
```

### Key Components

- **`RepositoryPort`**: Interface defining repository operations
- **`BaseRepository`**: Generic repository implementation with database abstraction
- **`DatabaseAdapter`**: Abstract base class for database-specific adapters
- **`DatabaseFactory`**: Factory for creating database adapter instances
- **Database-specific adapters**: Concrete implementations for each database type

## Supported Databases

| Database | Driver | Adapter Class | Status |
|----------|--------|---------------|---------|
| **PostgreSQL** | `asyncpg` | `PostgreSQLAdapter` | ✅ Production Ready |
| **MariaDB/MySQL** | `aiomysql` | `MariaDBAdapter` | ✅ Production Ready |
| **SQL Server** | `aioodbc` | `SQLServerAdapter` | ✅ Production Ready |
| **Oracle** | `cx_oracle_async` | `OracleAdapter` | ✅ Production Ready |

### Installation Requirements

```bash
# PostgreSQL (default)
pip install asyncpg

# MariaDB/MySQL
pip install aiomysql

# SQL Server
pip install aioodbc

# Oracle
pip install cx_oracle_async
```

## Quick Start

### Basic Repository Usage

```python
from adapters.repositories.user import UserRepository
from models.user import User

# PostgreSQL (default)
user_repo = UserRepository()

# MariaDB/MySQL
user_repo = UserRepository(db_type="mariadb")

# SQL Server
user_repo = UserRepository(db_type="sqlserver")

# Oracle
user_repo = UserRepository(db_type="oracle")

# CRUD operations
user = User(name="John Doe", email="john@example.com")

# Create
created_user = await user_repo.create(user)
print(f"Created: {created_user.id}")

# Read
users = await user_repo.list()
user_detail = await user_repo.detail(created_user.id)

# Update
user.name = "John Smith"
updated_user = await user_repo.update(created_user.id, user)

# Delete
await user_repo.delete(created_user.id)

# Always close connections
await user_repo.close()
```

### Custom Repository Implementation

```python
from adapters.repositories.base import BaseRepository
from models.product import Product
from schemas.product import ProductSchema

class ProductRepository(BaseRepository[Product]):
    """Product-specific repository"""
    
    def __init__(self, db_type: str = "postgresql", **kwargs):
        super().__init__(
            model=Product,
            schema=ProductSchema,
            db_type=db_type,
            **kwargs
        )
    
    async def find_by_category(self, category: str) -> List[Product]:
        """Custom method to find products by category"""
        from ports.repository import FilterCondition
        
        filters = [FilterCondition(
            attribute="category", 
            operator="eq", 
            value=category
        )]
        
        return await self.list(filters=filters)
```

## Database Adapters

### PostgreSQL Adapter

```python
# Default configuration
user_repo = UserRepository()  # Uses PostgreSQL by default

# Custom configuration
user_repo = UserRepository(
    db_type="postgresql",
    connection_url="postgresql+asyncpg://user:pass@localhost:5432/mydb",
    pool_size=15,
    max_overflow=25,
    echo=True
)
```

**Features:**

- Advanced PostgreSQL features support
- Connection pooling with asyncpg
- Query optimization for PostgreSQL dialect

### MariaDB/MySQL Adapter

```python
# Basic usage
user_repo = UserRepository(db_type="mariadb")

# Custom configuration
user_repo = UserRepository(
    db_type="mysql",  # Alias for mariadb
    connection_url="mysql+aiomysql://user:pass@localhost:3306/mydb",
    connect_args={"charset": "utf8mb4"}
)
```

**Features:**

- Full UTF-8 support with utf8mb4 charset
- MySQL/MariaDB specific optimizations
- Connection pooling with aiomysql

### SQL Server Adapter

```python
# Basic usage
user_repo = UserRepository(db_type="sqlserver")

# Custom configuration
user_repo = UserRepository(
    db_type="mssql",  # Alias for sqlserver
    connection_url="mssql+aioodbc://user:pass@server:1433/mydb",
    connect_args={"driver": "ODBC Driver 17 for SQL Server"}
)
```

**Features:**

- Enterprise SQL Server features
- ODBC driver integration
- Windows Authentication support

### Oracle Adapter

```python
# Basic usage
user_repo = UserRepository(db_type="oracle")

# Custom configuration
user_repo = UserRepository(
    db_type="oracle",
    connection_url="oracle+cx_oracle_async://user:pass@server:1521/xe"
)
```

**Features:**

- Oracle-specific data types
- Advanced Oracle features
- Connection pooling optimized for Oracle

## Configuration

### Environment Variables

```bash
# General database settings
DATABASE_TYPE=postgresql  # Default database type

# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=myuser
POSTGRES_PASSWORD=mypassword
POSTGRES_NAME=mydatabase

# MariaDB/MySQL
MARIADB_HOST=localhost
MARIADB_PORT=3306
MARIADB_USER=myuser
MARIADB_PASSWORD=mypassword
MARIADB_NAME=mydatabase

# SQL Server
SQLSERVER_HOST=localhost
SQLSERVER_PORT=1433
SQLSERVER_USER=myuser
SQLSERVER_PASSWORD=mypassword
SQLSERVER_NAME=mydatabase

# Oracle
ORACLE_HOST=localhost
ORACLE_PORT=1521
ORACLE_USER=myuser
ORACLE_PASSWORD=mypassword
ORACLE_NAME=xe

# Connection Pool Settings
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
DB_ECHO=false
```

### Settings Configuration

```python
# config/settings.py
class Settings:
    database_type: str = "postgresql"
    postgres_url: str = "postgresql+asyncpg://user:pass@localhost:5432/db"
    mariadb_url: str = "mysql+aiomysql://user:pass@localhost:3306/db"
    sqlserver_url: str = "mssql+aioodbc://user:pass@localhost:1433/db"
    oracle_url: str = "oracle+cx_oracle_async://user:pass@localhost:1521/xe"
    
    db_pool_size: int = 10
    db_max_overflow: int = 20
    db_echo: bool = False
```

### Programmatic Configuration

```python
# Override default settings
user_repo = UserRepository(
    db_type="postgresql",
    connection_url="postgresql+asyncpg://custom:pass@custom-host:5432/custom-db",
    pool_size=20,
    max_overflow=40,
    echo=True,
    pool_pre_ping=True,
    pool_recycle=7200
)
```

## Advanced Usage

### Filtering and Querying

```python
from ports.repository import FilterCondition

# Single filter
filters = [FilterCondition(
    attribute="name", 
    operator="like", 
    value="%John%"
)]
users = await user_repo.list(filters=filters)

# Multiple filters
filters = [
    FilterCondition(attribute="age", operator="gte", value=18),
    FilterCondition(attribute="status", operator="eq", value="active"),
    FilterCondition(attribute="email", operator="like", value="%@company.com")
]
users = await user_repo.list(filters=filters)

# Supported operators
operators = [
    "eq",      # Equal
    "ne",      # Not equal
    "gt",      # Greater than
    "gte",     # Greater than or equal
    "lt",      # Less than
    "lte",     # Less than or equal
    "like",    # SQL LIKE
    "ilike",   # Case-insensitive LIKE
    "in",      # IN clause
    "not_in"   # NOT IN clause
]
```

### Relations and Eager Loading

```python
# Load user with related data
user = await user_repo.detail(
    pk="user-id",
    include_relations=["profile", "orders", "addresses"]
)
```

### Transaction Management

```python
# Using database adapter directly for transactions
async with await user_repo.db_adapter.get_session() as session:
    async with session.begin():
        # Multiple operations in transaction
        user1 = await user_repo.create(user_data1)
        user2 = await user_repo.create(user_data2)
        # Automatically committed or rolled back
```

### Connection Management

```python
# Manual connection management
user_repo = UserRepository()

try:
    # Perform operations
    users = await user_repo.list()
    # ... more operations
finally:
    # Always close connections
    await user_repo.close()

# Using context manager (recommended)
async with UserRepository() as repo:
    users = await repo.list()
    # Connection automatically closed
```

## Custom Adapters

### Creating a Custom Database Adapter

```python
from adapters.repositories.base import DatabaseAdapter, DatabaseFactory
from typing import Dict, Any

class SQLiteAdapter(DatabaseAdapter):
    """SQLite database adapter for development/testing"""
    
    def get_driver_name(self) -> str:
        return "sqlite+aiosqlite"
    
    def get_connection_url(self) -> str:
        if not self.connection_url.startswith("sqlite+aiosqlite://"):
            return f"sqlite+aiosqlite:///{self.connection_url}"
        return self.connection_url
    
    def get_engine_config(self) -> Dict[str, Any]:
        return {
            "echo": self.config.get("echo", False),
            "connect_args": {"check_same_thread": False}
        }
    
    def adapt_query_for_dialect(self, query: Any) -> Any:
        # SQLite-specific query adaptations
        return query

# Register the custom adapter
DatabaseFactory.register_adapter("sqlite", SQLiteAdapter)

# Use the custom adapter
user_repo = UserRepository(
    db_type="sqlite",
    connection_url="/path/to/database.db"
)
```

### Custom Repository with Business Logic

```python
from datetime import datetime, timedelta
from typing import List, Optional

class UserRepository(BaseRepository[User]):
    """Enhanced user repository with business methods"""
    
    async def find_active_users(self) -> List[User]:
        """Find all active users"""
        filters = [FilterCondition(
            attribute="is_active", 
            operator="eq", 
            value=True
        )]
        return await self.list(filters=filters)
    
    async def find_recent_users(self, days: int = 7) -> List[User]:
        """Find users created in the last N days"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        filters = [FilterCondition(
            attribute="created_at", 
            operator="gte", 
            value=cutoff_date
        )]
        return await self.list(filters=filters)
    
    async def find_by_email_domain(self, domain: str) -> List[User]:
        """Find users by email domain"""
        filters = [FilterCondition(
            attribute="email", 
            operator="like", 
            value=f"%@{domain}"
        )]
        return await self.list(filters=filters)
    
    async def deactivate_user(self, user_id: str) -> User:
        """Soft delete a user"""
        user_update = User(is_active=False, deactivated_at=datetime.utcnow())
        return await self.update(user_id, user_update)
```

## Error Handling

### Common Error Scenarios

```python
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError, OperationalError

async def safe_create_user(user_data: User) -> Optional[User]:
    """Safely create a user with error handling"""
    user_repo = UserRepository()
    
    try:
        return await user_repo.create(user_data)
    
    except IntegrityError as e:
        # Handle unique constraint violations
        if "email" in str(e):
            raise HTTPException(
                status_code=400,
                detail="Email already exists"
            )
        raise HTTPException(
            status_code=400,
            detail="Data integrity error"
        )
    
    except OperationalError as e:
        # Handle database connection issues
        raise HTTPException(
            status_code=503,
            detail="Database temporarily unavailable"
        )
    
    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )
    
    finally:
        await user_repo.close()
```

### Connection Retry Logic

```python
import asyncio
from typing import TypeVar, Callable, Any

T = TypeVar('T')

async def with_retry(
    operation: Callable[[], T], 
    max_retries: int = 3,
    delay: float = 1.0
) -> T:
    """Execute operation with retry logic"""
    
    for attempt in range(max_retries):
        try:
            return await operation()
        except OperationalError as e:
            if attempt == max_retries - 1:
                raise e
            
            await asyncio.sleep(delay * (2 ** attempt))  # Exponential backoff
    
    raise Exception("Max retries exceeded")

# Usage
user_repo = UserRepository()
users = await with_retry(lambda: user_repo.list())
```

## Best Practices

### 1. Connection Management

```python
# ✅ Good: Always close connections
user_repo = UserRepository()
try:
    users = await user_repo.list()
finally:
    await user_repo.close()

# ✅ Better: Use context managers
async with UserRepository() as repo:
    users = await repo.list()

# ❌ Bad: Leaving connections open
user_repo = UserRepository()
users = await user_repo.list()  # Connection never closed
```

### 2. Configuration Management

```python
# ✅ Good: Use environment-specific configurations
class Config:
    DATABASE_CONFIGS = {
        "development": {
            "db_type": "sqlite",
            "connection_url": "/tmp/dev.db"
        },
        "testing": {
            "db_type": "sqlite",
            "connection_url": ":memory:"
        },
        "production": {
            "db_type": "postgresql",
            "pool_size": 20,
            "max_overflow": 40
        }
    }

config = Config.DATABASE_CONFIGS[os.getenv("ENVIRONMENT", "development")]
user_repo = UserRepository(**config)
```

### 3. Error Handling

```python
# ✅ Good: Specific error handling
try:
    user = await user_repo.create(user_data)
except IntegrityError:
    # Handle specific database errors
    pass
except OperationalError:
    # Handle connection errors
    pass

# ❌ Bad: Generic error handling
try:
    user = await user_repo.create(user_data)
except Exception:
    # Too generic, loses important error information
    pass
```

### 4. Repository Design

```python
# ✅ Good: Domain-specific repositories
class UserRepository(BaseRepository[User]):
    async def find_by_email(self, email: str) -> Optional[User]:
        # Business logic specific to users
        pass

# ✅ Good: Composition over inheritance
class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
    
    async def register_user(self, user_data: User) -> User:
        # Business logic using repository
        pass
```

### 5. Testing

```python
# ✅ Good: Use in-memory database for tests
@pytest.fixture
async def test_user_repo():
    repo = UserRepository(
        db_type="sqlite",
        connection_url=":memory:"
    )
    # Setup test data
    yield repo
    await repo.close()

async def test_create_user(test_user_repo):
    user = User(name="Test", email="test@example.com")
    created = await test_user_repo.create(user)
    assert created.id is not None
```

### 6. Performance Optimization

```python
# ✅ Good: Use connection pooling
user_repo = UserRepository(
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=3600
)

# ✅ Good: Use eager loading for relations
user = await user_repo.detail(
    pk="user-id",
    include_relations=["profile", "orders"]
)

# ✅ Good: Use appropriate filters
filters = [FilterCondition(
    attribute="created_at",
    operator="gte", 
    value=datetime.utcnow() - timedelta(days=30)
)]
recent_users = await user_repo.list(filters=filters)
```

## Troubleshooting

### Common Issues

1. **Connection Pool Exhausted**

   ```python
   # Solution: Increase pool size or ensure connections are closed
   user_repo = UserRepository(pool_size=20, max_overflow=40)
   ```

2. **Database Driver Not Found**

   ```bash
   # Solution: Install the required driver
   pip install asyncpg  # For PostgreSQL
   pip install aiomysql  # For MariaDB/MySQL
   ```

3. **Connection Timeout**

   ```python
   # Solution: Configure connection timeout
   user_repo = UserRepository(
       connect_args={"connect_timeout": 30}
   )
   ```

4. **Query Performance Issues**

   ```python
   # Solution: Enable query logging and optimize
   user_repo = UserRepository(echo=True)  # Enable SQL logging
   ```

For more examples and advanced patterns, see the complete example in `examples/repositories_example.py`.
