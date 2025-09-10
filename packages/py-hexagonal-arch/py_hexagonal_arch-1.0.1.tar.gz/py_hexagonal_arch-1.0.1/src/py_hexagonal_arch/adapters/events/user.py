"""
User Event module
"""

from typing import TYPE_CHECKING, Optional, Any

from .base import BaseEvent
from ...models.user import User


if TYPE_CHECKING:
    pass


class UserEvent(BaseEvent[User]):
    """User-specific event implementation"""

    def __init__(
        self,
        event_type: Optional[str] = None,
        topic_prefix: Optional[str] = None,
        **event_config: Any
    ):
        """Initialize user event with configurable backend"""
        
        super().__init__(
            model=User,
            event_type=event_type or "kafka",  # Default to kafka if not specified
            topic_prefix=topic_prefix or "user",
            **event_config
        )