# BaseRouter Multi-Framework Support

El `BaseRouter` ha sido modificado para soportar **FastAPI**, **Flask** y **Tornado** a través de una capa de abstracción que permite intercambiar frameworks web sin cambiar la lógica de negocio.

## Características

- ✅ **Soporte para FastAPI**: Funcionalidad original mantenida
- ✅ **Soporte para Flask**: Nueva funcionalidad añadida
- ✅ **Soporte para Tornado**: Soporte completo para aplicaciones asíncronas
- ✅ **Interfaz unificada**: Misma API para todos los frameworks
- ✅ **Extensible**: Fácil agregar soporte para otros frameworks
- ✅ **Asíncrono**: Soporte completo para operaciones async/await

## Uso

### FastAPI (Por defecto)

```python
from adapters.routers.base import BaseRouter

# Crear router para FastAPI (comportamiento por defecto)
user_router = BaseRouter(
    model=User,
    controller=UserController,
    prefix="/users",
    tags=["users"]
    # framework="fastapi" es opcional (por defecto)
)

# Usar con FastAPI
app = FastAPI()
app.include_router(user_router.get_router())
```

### Flask

```python
from adapters.routers.base import BaseRouter

# Crear router para Flask
user_router = BaseRouter(
    model=User,
    controller=UserController,
    prefix="/users",
    tags=["users"],
    framework="flask"  # Especificar Flask
)

# Usar con Flask
app = Flask(__name__)
app.register_blueprint(user_router.get_router())
```

### Tornado

```python
from adapters.routers.base import BaseRouter
import tornado.ioloop

# Crear router para Tornado
user_router = BaseRouter(
    model=User,
    controller=UserController,
    prefix="/users",
    tags=["users"],
    framework="tornado"  # Especificar Tornado
)

# Crear aplicación Tornado
app = user_router.get_tornado_application(debug=True)
app.listen(8000)
tornado.ioloop.IOLoop.current().start()
```

## Arquitectura

### Capa de Abstracción

La nueva implementación utiliza el patrón **Adapter** para abstraer las diferencias entre frameworks:

- `WebFrameworkAdapter`: Interfaz base para adaptadores
- `FastAPIAdapter`: Implementación específica para FastAPI
- `FlaskAdapter`: Implementación específica para Flask
- `TornadoAdapter`: Implementación específica para Tornado
- `WebFrameworkFactory`: Factory para crear adaptadores

### Flujo de Trabajo

1. **Inicialización**: El `BaseRouter` recibe el parámetro `framework`
2. **Adaptador**: Se crea el adaptador correspondiente usando el Factory
3. **Router**: Se crea el router específico del framework
4. **Rutas**: Se registran las rutas usando la abstracción común

## Rutas Generadas

Para ambos frameworks, se generan automáticamente las siguientes rutas:

- `POST /` - Crear nuevo elemento
- `GET /` - Listar elementos (con filtros opcionales)
- `GET /{pk}` - Obtener elemento por ID
- `PATCH /{pk}` - Actualizar elemento por ID
- `DELETE /{pk}` - Eliminar elemento por ID

## Diferencias entre Frameworks

### FastAPI
- Inyección de dependencias automática
- Validación automática con Pydantic
- Documentación OpenAPI automática
- Soporte nativo para async/await

### Flask
- Manejo manual de request/response
- Conversión automática async/sync
- Blueprints para organización
- Serialización manual de respuestas

### Tornado
- Arquitectura completamente asíncrona
- RequestHandler basado en clases
- Soporte nativo para WebSockets
- Manejo manual de request/response
- Ideal para aplicaciones de alta concurrencia

## Extensibilidad

Para agregar soporte a un nuevo framework:

1. Crear una clase que herede de `WebFrameworkAdapter`
2. Implementar todos los métodos abstractos
3. Registrar el adaptador en el Factory

```python
class DjangoAdapter(WebFrameworkAdapter):
    # Implementar métodos...
    pass

# Registrar
WebFrameworkFactory.register_adapter("django", DjangoAdapter)
```

## Dependencias

### FastAPI
```bash
pip install fastapi uvicorn pydantic
```

### Flask
```bash
pip install flask pydantic
```

### Tornado
```bash
pip install tornado pydantic
```

## Ejemplos Completos

Ver los archivos:
- `fastapi_example.py` - Ejemplo completo con FastAPI
- `flask_example.py` - Ejemplo completo con Flask
- `tornado_example.py` - Ejemplo completo con Tornado
