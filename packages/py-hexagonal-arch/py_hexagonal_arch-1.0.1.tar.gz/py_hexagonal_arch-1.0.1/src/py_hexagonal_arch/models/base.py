"""
Base Model
"""

from typing import ClassVar
from uuid import uuid4
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


class CustomModel(BaseModel):
    
    pk_field: ClassVar[str] = "uuid"

    uuid: str = Field(default_factory=lambda: str(uuid4()))