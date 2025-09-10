"""
User Repository module
"""

from typing import Optional, Any

from adapters.repositories.base import BaseRepository
from models.user import User
from schemas.user import UserSchema
from config.settings import settings


class UserRepository(BaseRepository[User]):
    """Repository for handling User model operations"""
    
    def __init__(
        self,
        db_type: Optional[str] = None,
        connection_url: Optional[str] = None,
        **db_config: Any
    ):
        """Initialize user repository with configurable database backend"""
        
        # Use settings default if not specified
        db_type = db_type or settings.database_type
        
        super().__init__(
            model=User,
            schema=UserSchema,
            db_type=db_type,
            connection_url=connection_url,
            **db_config
        )
