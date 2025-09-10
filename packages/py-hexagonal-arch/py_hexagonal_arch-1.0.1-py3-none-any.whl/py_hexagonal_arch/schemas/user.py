"""
User Schema module
"""

from uuid import uuid4
from sqlalchemy import Column, String, Table
from sqlalchemy.orm import relationship

from .base import BaseSchema


class UserSchema(BaseSchema):
    """..."""

    __tablename__ = "user"
    __table__ = Table(
        __tablename__,
        BaseSchema.metadata,
        Column("uuid", String, primary_key=True, index=True, default=lambda: str(uuid4())),
        Column("first_name", String, nullable=True),
        Column("last_name", String, nullable=True),
        Column("email", String, unique=True, nullable=False),
        extend_existing=True
    )