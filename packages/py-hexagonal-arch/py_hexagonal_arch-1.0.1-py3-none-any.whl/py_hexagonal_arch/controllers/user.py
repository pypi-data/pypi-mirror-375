"""
User Controller module
"""

from typing import TYPE_CHECKING

from .base import BaseController

from ..adapters.repositories.user import UserRepository
from ..adapters.caches.user import UserCache
from ..adapters.events.user import UserEvent


if TYPE_CHECKING:
    pass


class UserController(BaseController):
    """..."""

    def __init__(self):
        """..."""

        super().__init__(
            repository=UserRepository(),
            cache=UserCache(),
            event=UserEvent()
        )