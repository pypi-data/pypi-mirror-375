"""
Repository System Usage Examples

This example demonstrates how to use the refactored repository system
with different database backends (PostgreSQL, MariaDB, SQL Server, Oracle).
"""

import asyncio
from typing import Optional
from pydantic import BaseModel

# Import the repository components
from src.adapters.repositories.base import BaseRepository, DatabaseFactory
from src.adapters.repositories.user import UserRepository
from src.models.user import User


class Product(BaseModel):
    """Example product model"""
    id: Optional[str] = None
    name: str
    price: float
    category: str
    description: Optional[str] = None

    class Config:
        pk_field = "id"


class ProductRepository(BaseRepository[Product]):
    """Product-specific repository implementation"""
    
    def __init__(self, db_type: str = "postgresql", **kwargs):
        # Note: In a real scenario, you'd have a ProductSchema for SQLAlchemy
        # For this example, we'll assume it exists
        super().__init__(
            model=Product,
            schema=Product,  # In reality, this would be ProductSchema
            db_type=db_type,
            **kwargs
        )


async def example_postgresql_repository():
    """Example using PostgreSQL repository"""
    print("=== PostgreSQL Repository Example ===")
    
    try:
        # Create user repository with PostgreSQL backend (default)
        user_repo = UserRepository()
        
        # Create a test user
        user = User(name="John Doe", email="john@example.com")
        
        # Create user
        created_user = await user_repo.create(user)
        print(f"Created user: {created_user.name} (ID: {created_user.id})")
        
        # List users
        users = await user_repo.list()
        print(f"Total users: {len(users)}")
        
        # Get user by ID
        if created_user.id:
            retrieved_user = await user_repo.detail(created_user.id)
            print(f"Retrieved user: {retrieved_user.name}")
        
        # Update user
        if created_user.id:
            user.name = "John Smith"
            updated_user = await user_repo.update(created_user.id, user)
            print(f"Updated user: {updated_user.name}")
        
        # Close connection
        await user_repo.close()
        
    except ImportError as e:
        print(f"PostgreSQL dependencies not available: {e}")
    except Exception as e:
        print(f"PostgreSQL error (database might not be configured): {e}")
    
    print()


async def example_mariadb_repository():
    """Example using MariaDB repository"""
    print("=== MariaDB Repository Example ===")
    
    try:
        # Create product repository with MariaDB backend
        product_repo = ProductRepository(
            db_type="mariadb",
            connection_url="mysql+aiomysql://user:password@localhost:3306/testdb"
        )
        
        # Create a test product
        product = Product(
            name="Laptop",
            price=999.99,
            category="Electronics",
            description="High-performance laptop"
        )
        
        # Create product
        created_product = await product_repo.create(product)
        print(f"Created product: {created_product.name} (Price: ${created_product.price})")
        
        # List products
        products = await product_repo.list()
        print(f"Total products: {len(products)}")
        
        # Close connection
        await product_repo.close()
        
    except ImportError as e:
        print(f"MariaDB dependencies not available: {e}")
    except Exception as e:
        print(f"MariaDB error (database might not be configured): {e}")
    
    print()


async def example_sqlserver_repository():
    """Example using SQL Server repository"""
    print("=== SQL Server Repository Example ===")
    
    try:
        # Create user repository with SQL Server backend
        user_repo = UserRepository(
            db_type="sqlserver",
            connection_url="mssql+aioodbc://user:password@localhost:1433/testdb"
        )
        
        # Create a test user
        user = User(name="Alice Johnson", email="alice@example.com")
        
        # Create user
        created_user = await user_repo.create(user)
        print(f"Created user in SQL Server: {created_user.name}")
        
        # Close connection
        await user_repo.close()
        
    except ImportError as e:
        print(f"SQL Server dependencies not available: {e}")
    except Exception as e:
        print(f"SQL Server error (database might not be configured): {e}")
    
    print()


async def example_oracle_repository():
    """Example using Oracle repository"""
    print("=== Oracle Repository Example ===")
    
    try:
        # Create user repository with Oracle backend
        user_repo = UserRepository(
            db_type="oracle",
            connection_url="oracle+cx_oracle_async://user:password@localhost:1521/xe"
        )
        
        # Create a test user
        user = User(name="Bob Wilson", email="bob@example.com")
        
        # Create user
        created_user = await user_repo.create(user)
        print(f"Created user in Oracle: {created_user.name}")
        
        # Close connection
        await user_repo.close()
        
    except ImportError as e:
        print(f"Oracle dependencies not available: {e}")
    except Exception as e:
        print(f"Oracle error (database might not be configured): {e}")
    
    print()


async def example_factory_usage():
    """Example showing direct factory usage"""
    print("=== Database Factory Example ===")
    
    try:
        # Create different database adapters directly
        postgres_adapter = DatabaseFactory.create_adapter(
            "postgresql", 
            "postgresql+asyncpg://user:password@localhost:5432/testdb"
        )
        
        mariadb_adapter = DatabaseFactory.create_adapter(
            "mariadb",
            "mysql+aiomysql://user:password@localhost:3306/testdb"
        )
        
        print(f"PostgreSQL adapter driver: {postgres_adapter.get_driver_name()}")
        print(f"MariaDB adapter driver: {mariadb_adapter.get_driver_name()}")
        
        # Test connection URLs
        print(f"PostgreSQL URL: {postgres_adapter.get_connection_url()}")
        print(f"MariaDB URL: {mariadb_adapter.get_connection_url()}")
        
        # Close adapters
        await postgres_adapter.close()
        await mariadb_adapter.close()
        
    except Exception as e:
        print(f"Factory error: {e}")
    
    print()


async def example_custom_adapter():
    """Example showing how to register a custom adapter"""
    print("=== Custom Database Adapter Example ===")
    
    try:
        from src.adapters.repositories.base import DatabaseAdapter
        from typing import Dict, Any
        
        class SQLiteAdapter(DatabaseAdapter):
            """SQLite database adapter"""
            
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
                # SQLite specific adaptations
                return query
        
        # Register the custom adapter
        DatabaseFactory.register_adapter("sqlite", SQLiteAdapter)
        
        # Use the custom adapter
        sqlite_adapter = DatabaseFactory.create_adapter(
            "sqlite", 
            "/tmp/test.db"
        )
        
        print(f"SQLite adapter registered and created: {sqlite_adapter.get_driver_name()}")
        print(f"SQLite connection URL: {sqlite_adapter.get_connection_url()}")
        
        await sqlite_adapter.close()
        
    except Exception as e:
        print(f"Custom adapter error: {e}")
    
    print()


async def example_filtering_and_relations():
    """Example showing filtering and relations"""
    print("=== Filtering and Relations Example ===")
    
    try:
        from src.ports.repository import FilterCondition
        
        # Create repository
        user_repo = UserRepository()
        
        # Create test users
        users_data = [
            User(name="Alice Smith", email="alice@example.com"),
            User(name="Bob Johnson", email="bob@example.com"),
            User(name="Charlie Brown", email="charlie@example.com")
        ]
        
        created_users = []
        for user_data in users_data:
            created_user = await user_repo.create(user_data)
            created_users.append(created_user)
            print(f"Created user: {created_user.name}")
        
        # Filter users by name containing "Alice"
        filters = [
            FilterCondition(attribute="name", operator="like", value="%Alice%")
        ]
        
        filtered_users = await user_repo.list(filters=filters)
        print(f"Users with 'Alice' in name: {len(filtered_users)}")
        
        # Filter users by email domain
        filters = [
            FilterCondition(attribute="email", operator="like", value="%@example.com")
        ]
        
        domain_users = await user_repo.list(filters=filters)
        print(f"Users with @example.com domain: {len(domain_users)}")
        
        # Close connection
        await user_repo.close()
        
    except Exception as e:
        print(f"Filtering example error: {e}")
    
    print()


async def example_configuration_patterns():
    """Example showing different configuration patterns"""
    print("=== Configuration Patterns Example ===")
    
    # 1. Default configuration (from settings)
    user_repo_default = UserRepository()
    print("✅ Default configuration loaded from settings")
    
    # 2. Explicit database type
    user_repo_explicit = UserRepository(db_type="postgresql")
    print("✅ Explicit database type specified")
    
    # 3. Custom connection URL
    user_repo_custom = UserRepository(
        db_type="postgresql",
        connection_url="postgresql+asyncpg://custom_user:password@custom_host:5432/custom_db"
    )
    print("✅ Custom connection URL specified")
    
    # 4. Advanced configuration
    user_repo_advanced = UserRepository(
        db_type="postgresql",
        pool_size=20,
        max_overflow=30,
        echo=True
    )
    print("✅ Advanced configuration with pool settings")
    
    # Close all repositories
    for repo in [user_repo_default, user_repo_explicit, user_repo_custom, user_repo_advanced]:
        await repo.close()
    
    print()


async def main():
    """Run all examples"""
    print("Repository System Examples")
    print("=" * 50)
    
    # Run examples
    await example_postgresql_repository()
    await example_mariadb_repository()
    await example_sqlserver_repository()
    await example_oracle_repository()
    await example_factory_usage()
    await example_custom_adapter()
    await example_filtering_and_relations()
    await example_configuration_patterns()
    
    print("All examples completed!")


if __name__ == "__main__":
    asyncio.run(main())
