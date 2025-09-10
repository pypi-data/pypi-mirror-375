"""
Base Router module with Web Framework Abstraction
"""

import json
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, Generic
from enum import Enum
from pydantic import BaseModel, create_model

from ports.router import RouterPort
from ports.repository import FilterCondition, FilterList
from controllers.base import BaseController

T = TypeVar('T', bound=BaseModel)


# ============================================================================
# Web Framework Abstraction Layer
# ============================================================================

class HTTPMethod(Enum):
    """HTTP methods enumeration"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"


class RouteDefinition:
    """Route definition class"""
    
    def __init__(
        self,
        path: str,
        method: HTTPMethod,
        handler: Callable,
        response_model: Optional[Type] = None,
        status_code: int = 200,
        summary: Optional[str] = None,
        description: Optional[str] = None
    ):
        self.path = path
        self.method = method
        self.handler = handler
        self.response_model = response_model
        self.status_code = status_code
        self.summary = summary
        self.description = description


class WebFrameworkAdapter(ABC):
    """Abstract web framework adapter"""
    
    @abstractmethod
    def create_router(self, prefix: str, tags: Optional[List[str]] = None) -> Any:
        """Create a router instance"""
        pass
    
    @abstractmethod
    def add_route(self, router: Any, route: RouteDefinition) -> None:
        """Add a route to the router"""
        pass
    
    @abstractmethod
    def get_request_data(self, request: Any) -> Dict[str, Any]:
        """Extract request data"""
        pass
    
    @abstractmethod
    def get_query_params(self, request: Any) -> Dict[str, Any]:
        """Extract query parameters"""
        pass
    
    @abstractmethod
    def create_response(self, data: Any, status_code: int = 200) -> Any:
        """Create a response object"""
        pass


class FastAPIAdapter(WebFrameworkAdapter):
    """FastAPI framework adapter"""
    
    def __init__(self):
        try:
            from fastapi import APIRouter, Body, Query, Request, status
            from pydantic import BaseModel
            self.APIRouter = APIRouter
            self.Body = Body
            self.Query = Query
            self.Request = Request
            self.status = status
            self.BaseModel = BaseModel
        except ImportError:
            raise ImportError("FastAPI is not installed. Please install it with: pip install fastapi")
    
    def create_router(self, prefix: str, tags: Optional[List[str]] = None) -> Any:
        """Create a FastAPI router"""
        return self.APIRouter(prefix=prefix, tags=tags)
    
    def add_route(self, router: Any, route: RouteDefinition) -> None:
        """Add a route to FastAPI router"""
        method_map = {
            HTTPMethod.GET: router.get,
            HTTPMethod.POST: router.post,
            HTTPMethod.PUT: router.put,
            HTTPMethod.PATCH: router.patch,
            HTTPMethod.DELETE: router.delete,
        }
        
        decorator_kwargs = {
            "path": route.path,
            "status_code": route.status_code,
        }
        
        if route.response_model:
            decorator_kwargs["response_model"] = route.response_model
        
        if route.summary:
            decorator_kwargs["summary"] = route.summary
            
        if route.description:
            decorator_kwargs["description"] = route.description
        
        method_map[route.method](**decorator_kwargs)(route.handler)
    
    def get_request_data(self, request: Any) -> Dict[str, Any]:
        """Extract request data from FastAPI request"""
        # FastAPI handles this automatically through dependency injection
        return {}
    
    def get_query_params(self, request: Any) -> Dict[str, Any]:
        """Extract query parameters from FastAPI request"""
        return dict(request.query_params)
    
    def create_response(self, data: Any, status_code: int = 200) -> Any:
        """Create FastAPI response"""
        # FastAPI handles response creation automatically
        return data


class FlaskAdapter(WebFrameworkAdapter):
    """Flask framework adapter"""
    
    def __init__(self):
        try:
            from flask import Blueprint, request, jsonify
            self.Blueprint = Blueprint
            self.request = request
            self.jsonify = jsonify
        except ImportError:
            raise ImportError("Flask is not installed. Please install it with: pip install flask")
    
    def create_router(self, prefix: str, tags: Optional[List[str]] = None) -> Any:
        """Create a Flask Blueprint"""
        return self.Blueprint(
            name=prefix.strip('/').replace('/', '_'),
            import_name=__name__,
            url_prefix=prefix
        )
    
    def add_route(self, router: Any, route: RouteDefinition) -> None:
        """Add a route to Flask Blueprint"""
        methods = [route.method.value]
        
        def wrapper(*args, **kwargs):
            # Convert async handler to sync if needed
            import asyncio
            import inspect
            
            if inspect.iscoroutinefunction(route.handler):
                # Handle async functions
                loop = None
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                
                # Pass path parameters to the handler
                result = loop.run_until_complete(route.handler(*args, **kwargs))
            else:
                result = route.handler(*args, **kwargs)
            
            return self.create_response(result, route.status_code)
        
        wrapper.__name__ = f"{route.method.value.lower()}_{route.path.replace('/', '_').replace('{', '').replace('}', '').replace('<', '').replace('>', '')}"
        
        # Convert FastAPI path parameters to Flask format
        flask_path = route.path.replace('{', '<').replace('}', '>')
        
        router.add_url_rule(
            rule=flask_path,
            endpoint=wrapper.__name__,
            view_func=wrapper,
            methods=methods
        )
    
    def get_request_data(self, request: Any = None) -> Dict[str, Any]:
        """Extract request data from Flask request"""
        if request is None:
            request = self.request
        
        if request.is_json:
            return request.get_json() or {}
        return {}
    
    def get_query_params(self, request: Any = None) -> Dict[str, Any]:
        """Extract query parameters from Flask request"""
        if request is None:
            request = self.request
        return dict(request.args)
    
    def create_response(self, data: Any, status_code: int = 200) -> Any:
        """Create Flask response"""
        if data is None:
            return '', status_code
        return self.jsonify(data), status_code


class TornadoAdapter(WebFrameworkAdapter):
    """Tornado framework adapter"""
    
    def __init__(self):
        try:
            import tornado.web
            import tornado.escape
            self.tornado_web = tornado.web
            self.tornado_escape = tornado.escape
        except ImportError:
            raise ImportError("Tornado is not installed. Please install it with: pip install tornado")
    
    def create_router(self, prefix: str, tags: Optional[List[str]] = None) -> Any:
        """Create a Tornado Application with handlers list"""
        # Tornado doesn't have a router concept like Flask/FastAPI
        # We'll return a list to collect handlers and create the app later
        return {
            'handlers': [],
            'prefix': prefix,
            'tags': tags
        }
    
    def add_route(self, router: Any, route: RouteDefinition) -> None:
        """Add a route to Tornado handlers list"""
        
        class TornadoHandler(self.tornado_web.RequestHandler):
            def __init__(self, application, request, **kwargs):
                super().__init__(application, request, **kwargs)
                self.route_handler = route.handler
                self.route_definition = route
            
            async def get(self, *args):
                await self._handle_request(*args)
            
            async def post(self, *args):
                await self._handle_request(*args)
            
            async def patch(self, *args):
                await self._handle_request(*args)
            
            async def put(self, *args):
                await self._handle_request(*args)
            
            async def delete(self, *args):
                await self._handle_request(*args)
            
            async def _handle_request(self, *args):
                try:
                    # Handle request based on method
                    if self.request.method.upper() != route.method.value:
                        self.set_status(405)  # Method Not Allowed
                        return
                    
                    # Get request data for POST/PATCH/PUT
                    if self.request.method in ['POST', 'PATCH', 'PUT']:
                        if self.request.body:
                            try:
                                # Parse JSON body
                                request_data = self.tornado_escape.json_decode(self.request.body)
                                # For create/update operations, we need to pass the data
                                if args:  # Has path parameters (update/delete/detail)
                                    result = await self.route_handler(args[0], request_data)
                                else:  # No path parameters (create)
                                    # We need to create the model instance here
                                    # This is a bit tricky without access to the model
                                    result = await self.route_handler()
                            except Exception as e:
                                self.set_status(400)
                                self.write({"error": f"Invalid JSON: {str(e)}"})
                                return
                        else:
                            if args:
                                result = await self.route_handler(args[0], {})
                            else:
                                result = await self.route_handler()
                    else:
                        # GET/DELETE operations
                        if args:
                            result = await self.route_handler(*args)
                        else:
                            result = await self.route_handler()
                    
                    # Handle response
                    self.set_status(route.status_code)
                    
                    if result is not None:
                        if hasattr(result, 'dict'):
                            # Pydantic model
                            self.write(result.dict())
                        elif isinstance(result, list):
                            # List of models
                            response_list = []
                            for item in result:
                                if hasattr(item, 'dict'):
                                    response_list.append(item.dict())
                                else:
                                    response_list.append(item)
                            self.write(response_list)
                        else:
                            self.write(result)
                    
                except Exception as e:
                    self.set_status(500)
                    self.write({"error": str(e)})
        
        # Convert path format from FastAPI to Tornado
        tornado_path = route.path.replace('{', '(').replace('}', ')')
        if tornado_path.count('(') > 0:
            # Add regex pattern for path parameters
            tornado_path = tornado_path.replace('(pk)', r'([^/]+)')
        
        # Add prefix
        full_path = router['prefix'].rstrip('/') + tornado_path
        if not full_path:
            full_path = router['prefix'].rstrip('/') + '/'
        
        # Add handler to the list
        router['handlers'].append((full_path, TornadoHandler))
    
    def get_request_data(self, request: Any = None) -> Dict[str, Any]:
        """Extract request data from Tornado request"""
        if request and hasattr(request, 'body') and request.body:
            try:
                return self.tornado_escape.json_decode(request.body)
            except:
                return {}
        return {}
    
    def get_query_params(self, request: Any = None) -> Dict[str, Any]:
        """Extract query parameters from Tornado request"""
        if request and hasattr(request, 'arguments'):
            # Convert Tornado's arguments format to dict
            params = {}
            for key, values in request.arguments.items():
                # Tornado stores query params as lists of bytes
                if values:
                    params[key] = values[0].decode('utf-8') if isinstance(values[0], bytes) else values[0]
            return params
        return {}
    
    def create_response(self, data: Any, status_code: int = 200) -> Any:
        """Create Tornado response - handled by RequestHandler"""
        return data


class WebFrameworkFactory:
    """Factory for creating web framework adapters"""
    
    _adapters = {
        'fastapi': FastAPIAdapter,
        'flask': FlaskAdapter,
        'tornado': TornadoAdapter,
    }
    
    @classmethod
    def create_adapter(cls, framework: str) -> WebFrameworkAdapter:
        """Create a web framework adapter"""
        if framework.lower() not in cls._adapters:
            raise ValueError(f"Unsupported framework: {framework}. Supported: {list(cls._adapters.keys())}")
        
        return cls._adapters[framework.lower()]()
    
    @classmethod
    def register_adapter(cls, name: str, adapter_class: Type[WebFrameworkAdapter]) -> None:
        """Register a new framework adapter"""
        cls._adapters[name.lower()] = adapter_class  # type: ignore


# ============================================================================
# Base Router Implementation
# ============================================================================

class BaseRouter(RouterPort[T], Generic[T]):
    """Base router class with multi-framework support"""

    def __init__(
        self,
        model: Type[T],
        controller: Type[BaseController[T]],
        prefix: str,
        tags: Any,
        framework: str = "fastapi"
    ) -> None:
        """Initialize router with model and controller"""

        self.model = model
        self.controller = controller()
        self.framework_adapter = WebFrameworkFactory.create_adapter(framework)
        self.router = self.framework_adapter.create_router(prefix=prefix, tags=tags)
        
        # Create a partial model for updates
        fields = {}
        for field_name, field in model.__annotations__.items():
            fields[field_name] = (Optional[field], None)
        self.update_model = create_model(f"{model.__name__}Update", **fields)
        
        self._register_routes()

    def get_router(self):
        """Get the web framework router instance"""
        return self.router
    
    def get_tornado_application(self, **kwargs):
        """Get Tornado Application instance (only for Tornado framework)"""
        if isinstance(self.framework_adapter, TornadoAdapter):
            import tornado.web
            return tornado.web.Application(self.router['handlers'], **kwargs)
        else:
            raise ValueError("get_tornado_application() can only be called when using Tornado framework")

    def _parse_filters_from_query(self, filters_json: Optional[str] = None) -> Optional[FilterList]:
        """Parse filters from JSON string or return None"""
        
        if not filters_json:
            return None
        
        try:
            filters_data = json.loads(filters_json)
            filters = []
            
            for filter_data in filters_data:
                if isinstance(filter_data, dict) and all(k in filter_data for k in ['attribute', 'operator', 'value']):
                    filters.append(FilterCondition(
                        attribute=filter_data['attribute'],
                        operator=filter_data['operator'],
                        value=filter_data['value']
                    ))
            
            return filters if filters else None
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            print(f"Error parsing filters JSON: {e}")
            return None

    def _register_routes(self) -> None:
        """Register all routes"""

        # Create route handler functions
        async def create_handler() -> T:
            # Get request data based on framework
            if hasattr(self.framework_adapter, 'request'):
                # Flask
                data = self.framework_adapter.get_request_data()
                item = self.model(**data)
            else:
                # FastAPI - data injection handled by framework
                # This will be overridden by the actual route decorator
                pass
            return await self.create(item)

        async def list_handler() -> List[T]:
            # Get query parameters based on framework
            if hasattr(self.framework_adapter, 'request'):
                # Flask
                query_params = self.framework_adapter.get_query_params()
                filters = query_params.get('filters')
                return await self.list(None, filters)
            else:
                # FastAPI - handled by dependency injection
                pass
            return await self.list(None, None)

        async def detail_handler(pk: str) -> T:
            return await self.detail(pk)

        async def update_handler(pk: str) -> T:
            # Get request data based on framework
            if hasattr(self.framework_adapter, 'request'):
                # Flask
                data = self.framework_adapter.get_request_data()
                return await self.update(pk, data)
            else:
                # FastAPI - handled by dependency injection
                pass
            return await self.update(pk, {})

        async def delete_handler(pk: str) -> None:
            await self.delete(pk)

        # Register routes using the framework adapter
        routes = [
            RouteDefinition(
                path="",
                method=HTTPMethod.POST,
                handler=create_handler,
                response_model=self.model,
                status_code=201,
                summary=f"Create {self.model.__name__}",
                description=f"Create a new {self.model.__name__} instance"
            ),
            RouteDefinition(
                path="",
                method=HTTPMethod.GET,
                handler=list_handler,
                response_model=List[self.model],
                status_code=200,
                summary=f"List {self.model.__name__}s",
                description=f"Get a list of {self.model.__name__} instances with optional filters"
            ),
            RouteDefinition(
                path="/{pk}",
                method=HTTPMethod.GET,
                handler=detail_handler,
                response_model=self.model,
                status_code=200,
                summary=f"Get {self.model.__name__}",
                description=f"Get a specific {self.model.__name__} by ID"
            ),
            RouteDefinition(
                path="/{pk}",
                method=HTTPMethod.PATCH,
                handler=update_handler,
                response_model=self.model,
                status_code=200,
                summary=f"Update {self.model.__name__}",
                description=f"Update a specific {self.model.__name__} by ID"
            ),
            RouteDefinition(
                path="/{pk}",
                method=HTTPMethod.DELETE,
                handler=delete_handler,
                status_code=204,
                summary=f"Delete {self.model.__name__}",
                description=f"Delete a specific {self.model.__name__} by ID"
            )
        ]

        for route in routes:
            self.framework_adapter.add_route(self.router, route)

    async def create(self, item: T) -> T:
        """Create endpoint handler"""
        return await self.controller.create(item)

    async def list(self, request: Optional[Any] = None, filters: Optional[str] = None) -> List[T]:
        """List endpoint handler with optional filters"""
        parsed_filters = self._parse_filters_from_query(filters)
        return await self.controller.list(filters=parsed_filters)

    async def detail(self, pk: str) -> T:
        """Detail endpoint handler"""
        return await self.controller.detail(pk)

    async def update(self, pk: str, item_update: Any) -> T:
        """Update endpoint handler"""
        update_data = self.update_model(**item_update)
        return await self.controller.update(pk, update_data)

    async def delete(self, pk: str) -> None:
        """Delete endpoint handler"""
        await self.controller.delete(pk)