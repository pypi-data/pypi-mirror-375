"""
Tornado example using the updated BaseRouter
"""

import tornado.ioloop
import tornado.web
from pydantic import BaseModel
from typing import Optional

# Import your base classes (adjust imports as needed)
from adapters.routers.base import BaseRouter
from controllers.base import BaseController

# Example model
class User(BaseModel):
    id: Optional[str] = None
    name: str
    email: str
    age: int

# Example controller
class UserController(BaseController[User]):
    """User controller implementation"""
    
    def __init__(self):
        # Initialize with your repository
        super().__init__()
    
    async def create(self, item: User) -> User:
        # Implement creation logic
        print(f"Creating user: {item}")
        return item
    
    async def list(self, filters=None):
        # Implement list logic
        return [
            User(id="1", name="John Doe", email="john@example.com", age=30),
            User(id="2", name="Jane Smith", email="jane@example.com", age=25)
        ]
    
    async def detail(self, pk: str) -> User:
        # Implement detail logic
        return User(id=pk, name="John Doe", email="john@example.com", age=30)
    
    async def update(self, pk: str, item_update) -> User:
        # Implement update logic
        print(f"Updating user {pk} with: {item_update}")
        return User(id=pk, name="Updated User", email="updated@example.com", age=35)
    
    async def delete(self, pk: str) -> None:
        # Implement delete logic
        print(f"Deleting user: {pk}")

# Create router with Tornado framework
user_router = BaseRouter(
    model=User,
    controller=UserController,
    prefix="/users",
    tags=["users"],
    framework="tornado"  # Explicitly specify Tornado
)

# Create Tornado Application
app = user_router.get_tornado_application(
    debug=True,
    autoreload=True
)

# Add a simple health check endpoint
class HealthHandler(tornado.web.RequestHandler):
    async def get(self):
        self.write({"status": "healthy", "framework": "tornado"})

# Add additional routes if needed
app.add_handlers(".*$", [
    (r"/health", HealthHandler),
])

if __name__ == "__main__":
    print("Starting Tornado server on http://localhost:8000")
    print("Available endpoints:")
    print("  GET /health - Health check")
    print("  POST /users - Create user")
    print("  GET /users - List users")
    print("  GET /users/{id} - Get user by ID")
    print("  PATCH /users/{id} - Update user")
    print("  DELETE /users/{id} - Delete user")
    
    app.listen(8000)
    tornado.ioloop.IOLoop.current().start()
