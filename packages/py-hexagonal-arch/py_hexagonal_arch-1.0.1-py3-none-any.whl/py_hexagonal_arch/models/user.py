"""
User Model module
"""

from __future__ import annotations

from typing import Optional, List, TYPE_CHECKING

from .base import CustomModel

if TYPE_CHECKING:
    from models.chat import Chat
    from models.message import Message

class User(CustomModel):
    
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None