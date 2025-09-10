"""
User Router module
"""

from adapters.routers.base import BaseRouter
from models.user import User
from controllers.user import UserController


router = BaseRouter(
    model=User,
    controller=UserController,
    prefix="/user",
    tags=["user"]
).router