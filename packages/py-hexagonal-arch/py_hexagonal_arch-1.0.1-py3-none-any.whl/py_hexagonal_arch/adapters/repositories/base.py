"""
Base Repository module with Multi-Database Support
"""

from abc import ABC, abstractmethod
from typing import TypeVar, Generic, List, Optional, Type, Any, Dict
# Custom exception to avoid FastAPI dependency
class RepositoryException(Exception):
    """Repository exception"""
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, AsyncEngine
from sqlalchemy import select, and_, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import selectinload

from ...ports.repository import RepositoryPort, FilterList, FilterCondition
from ...config.settings import settings
from ...models.base import CustomModel

T = TypeVar('T', bound=CustomModel)

BaseSchema = declarative_base()


# ============================================================================
# Database Abstraction Layer
# ============================================================================

class DatabaseAdapter(ABC):
    """Abstract database adapter"""
    
    def __init__(self, connection_url: str, **kwargs: Any):
        self.connection_url = connection_url
        self.config = kwargs
        self.engine: Optional[AsyncEngine] = None
        self.metadata = MetaData()
    
    @abstractmethod
    def get_driver_name(self) -> str:
        """Get the database driver name"""
        pass
    
    @abstractmethod
    def get_connection_url(self) -> str:
        """Get the formatted connection URL"""
        pass
    
    @abstractmethod
    def get_engine_config(self) -> Dict[str, Any]:
        """Get database-specific engine configuration"""
        pass
    
    @abstractmethod
    def adapt_query_for_dialect(self, query: Any) -> Any:
        """Adapt query for specific database dialect"""
        pass
    
    async def get_engine(self) -> AsyncEngine:
        """Get or create database engine"""
        if not self.engine:
            engine_config = self.get_engine_config()
            self.engine = create_async_engine(
                self.get_connection_url(),
                **engine_config
            )
        return self.engine
    
    async def get_session(self) -> AsyncSession:
        """Get database session"""
        engine = await self.get_engine()
        return AsyncSession(engine)
    
    async def close(self) -> None:
        """Close database connection"""
        if self.engine:
            await self.engine.dispose()
            self.engine = None


class PostgreSQLAdapter(DatabaseAdapter):
    """PostgreSQL database adapter"""
    
    def get_driver_name(self) -> str:
        return "postgresql+asyncpg"
    
    def get_connection_url(self) -> str:
        if self.connection_url.startswith("postgresql://"):
            return self.connection_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        elif not self.connection_url.startswith("postgresql+asyncpg://"):
            return f"{self.get_driver_name()}://{self.connection_url}"
        return self.connection_url
    
    def get_engine_config(self) -> Dict[str, Any]:
        return {
            "echo": self.config.get("echo", False),
            "pool_size": self.config.get("pool_size", 10),
            "max_overflow": self.config.get("max_overflow", 20),
            "pool_pre_ping": self.config.get("pool_pre_ping", True),
            "pool_recycle": self.config.get("pool_recycle", 3600),
        }
    
    def adapt_query_for_dialect(self, query: Any) -> Any:
        # PostgreSQL specific query adaptations
        return query


class MariaDBAdapter(DatabaseAdapter):
    """MariaDB/MySQL database adapter"""
    
    def get_driver_name(self) -> str:
        return "mysql+aiomysql"
    
    def get_connection_url(self) -> str:
        if self.connection_url.startswith("mysql://"):
            return self.connection_url.replace("mysql://", "mysql+aiomysql://", 1)
        elif not self.connection_url.startswith("mysql+aiomysql://"):
            return f"{self.get_driver_name()}://{self.connection_url}"
        return self.connection_url
    
    def get_engine_config(self) -> Dict[str, Any]:
        return {
            "echo": self.config.get("echo", False),
            "pool_size": self.config.get("pool_size", 10),
            "max_overflow": self.config.get("max_overflow", 20),
            "pool_pre_ping": self.config.get("pool_pre_ping", True),
            "pool_recycle": self.config.get("pool_recycle", 3600),
            "connect_args": {
                "charset": "utf8mb4",
                **self.config.get("connect_args", {})
            }
        }
    
    def adapt_query_for_dialect(self, query: Any) -> Any:
        # MySQL/MariaDB specific query adaptations
        return query


class SQLServerAdapter(DatabaseAdapter):
    """Microsoft SQL Server database adapter"""
    
    def get_driver_name(self) -> str:
        return "mssql+aioodbc"
    
    def get_connection_url(self) -> str:
        if self.connection_url.startswith("mssql://"):
            return self.connection_url.replace("mssql://", "mssql+aioodbc://", 1)
        elif not self.connection_url.startswith("mssql+aioodbc://"):
            return f"{self.get_driver_name()}://{self.connection_url}"
        return self.connection_url
    
    def get_engine_config(self) -> Dict[str, Any]:
        return {
            "echo": self.config.get("echo", False),
            "pool_size": self.config.get("pool_size", 10),
            "max_overflow": self.config.get("max_overflow", 20),
            "pool_pre_ping": self.config.get("pool_pre_ping", True),
            "connect_args": {
                "driver": "ODBC Driver 17 for SQL Server",
                **self.config.get("connect_args", {})
            }
        }
    
    def adapt_query_for_dialect(self, query: Any) -> Any:
        # SQL Server specific query adaptations
        return query


class OracleAdapter(DatabaseAdapter):
    """Oracle Database adapter"""
    
    def get_driver_name(self) -> str:
        return "oracle+cx_oracle_async"
    
    def get_connection_url(self) -> str:
        if self.connection_url.startswith("oracle://"):
            return self.connection_url.replace("oracle://", "oracle+cx_oracle_async://", 1)
        elif not self.connection_url.startswith("oracle+cx_oracle_async://"):
            return f"{self.get_driver_name()}://{self.connection_url}"
        return self.connection_url
    
    def get_engine_config(self) -> Dict[str, Any]:
        return {
            "echo": self.config.get("echo", False),
            "pool_size": self.config.get("pool_size", 10),
            "max_overflow": self.config.get("max_overflow", 20),
            "pool_pre_ping": self.config.get("pool_pre_ping", True),
            "connect_args": {
                **self.config.get("connect_args", {})
            }
        }
    
    def adapt_query_for_dialect(self, query: Any) -> Any:
        # Oracle specific query adaptations
        return query


class DatabaseFactory:
    """Factory for creating database adapters"""
    
    _adapters = {
        'postgresql': PostgreSQLAdapter,
        'postgres': PostgreSQLAdapter,  # Alias
        'mariadb': MariaDBAdapter,
        'mysql': MariaDBAdapter,  # Alias
        'sqlserver': SQLServerAdapter,
        'mssql': SQLServerAdapter,  # Alias
        'oracle': OracleAdapter,
    }
    
    @classmethod
    def create_adapter(cls, db_type: str, connection_url: str, **config: Any) -> DatabaseAdapter:
        """Create a database adapter"""
        if db_type.lower() not in cls._adapters:
            raise ValueError(f"Unsupported database type: {db_type}. Supported: {list(cls._adapters.keys())}")
        
        adapter_class = cls._adapters[db_type.lower()]
        return adapter_class(connection_url=connection_url, **config)
    
    @classmethod
    def register_adapter(cls, name: str, adapter_class: Type[DatabaseAdapter]) -> None:
        """Register a new database adapter"""
        cls._adapters[name.lower()] = adapter_class


# ============================================================================
# Base Repository Implementation
# ============================================================================

class BaseRepository(RepositoryPort[T], Generic[T]):
    """Base repository class with multi-database support"""
    
    def __init__(
        self,
        model: Type[T],
        schema: Type[T],
        db_type: str = "postgresql",
        connection_url: Optional[str] = None,
        **db_config: Any
    ):
        """Initialize repository with model, schema and database adapter"""
        self.model = model
        self.schema = schema
        
        # Use default connection URL if not provided
        if not connection_url:
            connection_url = self._get_default_connection_url(db_type)
        
        # Apply default database configuration
        self._apply_default_db_config(db_type, db_config)
        
        self.db_adapter = DatabaseFactory.create_adapter(db_type, connection_url, **db_config)
    
    def _get_default_connection_url(self, db_type: str) -> str:
        """Get default connection URL based on database type"""
        if db_type.lower() in ['postgresql', 'postgres']:
            return settings.postgres_url
        elif db_type.lower() in ['mariadb', 'mysql']:
            return getattr(settings, 'mariadb_url', getattr(settings, 'mysql_url', ''))
        elif db_type.lower() in ['sqlserver', 'mssql']:
            return getattr(settings, 'sqlserver_url', '')
        elif db_type.lower() == 'oracle':
            return getattr(settings, 'oracle_url', '')
        else:
            return settings.postgres_url  # Default fallback
    
    def _apply_default_db_config(self, db_type: str, db_config: Dict[str, Any]) -> None:
        """Apply default database configuration"""
        # Common defaults
        if "echo" not in db_config:
            db_config["echo"] = getattr(settings, 'db_echo', False)
        if "pool_size" not in db_config:
            db_config["pool_size"] = getattr(settings, 'db_pool_size', 10)
        if "max_overflow" not in db_config:
            db_config["max_overflow"] = getattr(settings, 'db_max_overflow', 20)
    
    def _build_filter_condition(self, filter_condition: FilterCondition) -> Any:
        """Build SQLAlchemy filter condition from FilterCondition"""
        try:
            attribute = getattr(self.schema, filter_condition.attribute)
        except AttributeError:
            raise ValueError(f"Invalid filter attribute: {filter_condition.attribute}")
        
        if filter_condition.operator == "eq":
            return attribute == filter_condition.value
        elif filter_condition.operator == "ne":
            return attribute != filter_condition.value
        elif filter_condition.operator == "gt":
            return attribute > filter_condition.value
        elif filter_condition.operator == "gte":
            return attribute >= filter_condition.value
        elif filter_condition.operator == "lt":
            return attribute < filter_condition.value
        elif filter_condition.operator == "lte":
            return attribute <= filter_condition.value
        elif filter_condition.operator == "like":
            return attribute.like(filter_condition.value)
        elif filter_condition.operator == "ilike":
            return attribute.ilike(filter_condition.value)
        elif filter_condition.operator == "in":
            return attribute.in_(filter_condition.value)
        elif filter_condition.operator == "not_in":
            return ~attribute.in_(filter_condition.value)
        else:
            raise ValueError(f"Unsupported operator: {filter_condition.operator}")

    async def create(self, item: T) -> T:
        """Create a new item"""
        async with await self.db_adapter.get_session() as session:
            item_data = item.model_dump(exclude_none=True)
            db_item = self.schema(**item_data)
            session.add(db_item)
            await session.commit()
            await session.refresh(db_item)
            
            return self.model.model_validate(db_item.__dict__)

    async def list(self, filters: Optional[FilterList] = None) -> List[T]:
        """List all items with optional filters"""
        async with await self.db_adapter.get_session() as session:
            query = select(self.schema)
            
            if filters:
                filter_conditions = []
                for filter_condition in filters:
                    try:
                        condition = self._build_filter_condition(filter_condition)
                        filter_conditions.append(condition)
                    except (AttributeError, ValueError) as e:
                        print(f"Invalid filter condition: {filter_condition}, error: {e}")
                        continue
                
                if filter_conditions:
                    query = query.where(and_(*filter_conditions))
            
            # Apply database-specific query adaptations
            query = self.db_adapter.adapt_query_for_dialect(query)
            
            result = await session.execute(query)
            items = result.scalars().all()
            
            return [self.model.model_validate(item.__dict__) for item in items]

    async def detail(
        self,
        pk: str,
        include_relations: Optional[List[str]] = None
    ) -> Optional[T]:
        """Get item by primary key"""
        async with await self.db_adapter.get_session() as session:
            query = select(self.schema).where(
                getattr(self.schema, self.model.pk_field) == pk
            )
            
            if include_relations:
                for relation in include_relations:
                    if hasattr(self.schema, relation):
                        query = query.options(selectinload(getattr(self.schema, relation)))
            
            # Apply database-specific query adaptations
            query = self.db_adapter.adapt_query_for_dialect(query)
            
            result = await session.execute(query)
            item = result.scalar_one_or_none()
            
            if not item:
                raise RepositoryException(
                    status_code=404,
                    detail=f"{self.model.__name__} with pk: {pk} not found"
                )
            
            return self.model.model_validate(item.__dict__)

    async def update(self, pk: str, item_update: T) -> T:
        """Update an item"""
        async with await self.db_adapter.get_session() as session:
            result = await session.execute(
                select(self.schema).where(
                    getattr(self.schema, self.model.pk_field) == pk
                )
            )
            item = result.scalar_one_or_none()
            
            if not item:
                raise RepositoryException(
                    status_code=404,
                    detail=f"{self.model.__name__} with pk: {pk} not found"
                )
            
            item_data = item_update.model_dump(exclude_unset=True)
            for key, value in item_data.items():
                setattr(item, key, value)
            
            session.add(item)
            await session.commit()
            await session.refresh(item)
            
            return self.model.model_validate(item.__dict__)

    async def delete(self, pk: str) -> None:
        """Delete an item"""
        async with await self.db_adapter.get_session() as session:
            result = await session.execute(
                select(self.schema).where(
                    getattr(self.schema, self.model.pk_field) == pk
                )
            )
            item = result.scalar_one_or_none()
            
            if not item:
                raise RepositoryException(
                    status_code=404,
                    detail=f"{self.model.__name__} with pk: {pk} not found"
                )
            
            await session.delete(item)
            await session.commit()
    
    async def close(self) -> None:
        """Close database connection"""
        await self.db_adapter.close()