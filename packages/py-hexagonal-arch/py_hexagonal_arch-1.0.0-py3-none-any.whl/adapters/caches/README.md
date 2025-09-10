# Multi-Backend Cache System

El sistema de caché ha sido refactorizado para soportar **Redis**, **MemCache** e **In-Memory** a través de una capa de abstracción que permite intercambiar backends de caché sin cambiar la lógica de negocio.

## Características

- ✅ **Soporte para Redis**: Backend de producción con persistencia
- ✅ **Soporte para MemCache**: Caché distribuido de alto rendimiento  
- ✅ **Soporte In-Memory**: Caché rápido para testing y desarrollo
- ✅ **Interfaz unificada**: Misma API para todos los backends
- ✅ **Extensible**: Fácil agregar soporte para otros sistemas de caché
- ✅ **Type Safety**: Soporte completo para tipos genéricos
- ✅ **TTL Configurable**: Tiempo de vida configurable por instancia
- ✅ **Error Handling**: Manejo robusto de errores y entradas corruptas

## Arquitectura

### Capa de Abstracción

La implementación utiliza el patrón **Adapter** para abstraer las diferencias entre backends:

- `CacheAdapter`: Interfaz base para adaptadores de caché
- `RedisAdapter`: Implementación específica para Redis
- `MemCacheAdapter`: Implementación específica para MemCache
- `InMemoryAdapter`: Implementación específica para caché en memoria
- `CacheFactory`: Factory para crear adaptadores
- `BaseCache`: Clase base que implementa `CachePort` usando adaptadores

### Flujo de Trabajo

1. **Inicialización**: El `BaseCache` recibe el tipo de caché y configuración
2. **Adaptador**: Se crea el adaptador correspondiente usando el Factory
3. **Cliente**: Se inicializa el cliente específico del backend
4. **Operaciones**: Se ejecutan las operaciones usando la abstracción común

## Uso Básico

### Redis (Recomendado para Producción)

```python
from adapters.caches.user import UserCache

# Configuración por defecto (desde settings)
user_cache = UserCache()

# Configuración personalizada
user_cache = UserCache(
    cache_type="redis",
    ttl=7200,  # 2 horas
    url="redis://localhost:6379/0"
)
```

### MemCache (Alto Rendimiento)

```python
from adapters.caches.user import UserCache

# Configuración básica
user_cache = UserCache(
    cache_type="memcache",
    servers=["localhost:11211"]
)

# Múltiples servidores
user_cache = UserCache(
    cache_type="memcache",
    servers=["server1:11211", "server2:11211", "server3:11211"],
    ttl=3600
)
```

### In-Memory (Testing y Desarrollo)

```python
from adapters.caches.user import UserCache

# Caché en memoria (sin dependencias externas)
user_cache = UserCache(cache_type="memory")
```

## Operaciones de Caché

### Operaciones Básicas

```python
from models.user import User

# Crear usuario
user = User(id="123", name="Alice", email="alice@example.com", age=25)

# Almacenar en caché
await user_cache.set("user:123", user)

# Recuperar desde caché
cached_user = await user_cache.get("user:123")
if cached_user:
    print(f"Usuario encontrado: {cached_user.name}")

# Verificar existencia
exists = await user_cache.exists("user:123")
print(f"Usuario existe: {exists}")

# Eliminar del caché
await user_cache.delete("user:123")

# Limpiar todo el caché
await user_cache.clear()
```

### Operaciones Avanzadas

```python
from adapters.caches.base import BaseCache
from models.product import Product

# Cache personalizado para productos
product_cache = BaseCache(
    model=Product,
    cache_type="redis",
    ttl=1800  # 30 minutos
)

# Operaciones con manejo de errores
try:
    product = await product_cache.get("product:456")
    if not product:
        # Cargar desde base de datos
        product = await load_product_from_db("456")
        # Almacenar en caché para próximas consultas
        await product_cache.set("product:456", product)
except Exception as e:
    print(f"Error en caché: {e}")
    # Fallback a base de datos
    product = await load_product_from_db("456")
```

## Configuración

### Variables de Entorno

#### Configuración General

```bash
# Tipo de caché por defecto
CACHE_TYPE=redis  # redis, memcache, memory

# TTL general (fallback)
CACHE_TTL=3600
```

#### Configuración Redis

```bash
REDIS_PROTOCOL=redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_USER=default
REDIS_PASSWORD=yourpassword
REDIS_TTL=3600
```

#### Configuración MemCache

```bash
MEMCACHE_SERVERS=localhost:11211,server2:11211
MEMCACHE_TTL=3600
```

### Configuración Programática

```python
from config.settings import settings

# Modificar configuración en runtime
settings.cache_type = "memcache"
settings.memcache_servers = ["cache1:11211", "cache2:11211"]
settings.cache_ttl = 7200
```

## Creando Adaptadores Personalizados

### Implementar Adaptador

```python
from adapters.caches.base import CacheAdapter
from typing import Optional

class RedisCluterAdapter(CacheAdapter):
    """Adaptador para Redis Cluster"""
    
    def __init__(self, nodes: list, **kwargs):
        try:
            from rediscluster import RedisCluster
            self.client = RedisCluster(
                startup_nodes=nodes,
                decode_responses=True,
                **kwargs
            )
        except ImportError:
            raise ImportError("redis-py-cluster no está instalado")
    
    async def get(self, key: str) -> Optional[str]:
        """Obtener valor del cluster"""
        return await self.client.get(key)
    
    async def set(self, key: str, value: str, ttl: Optional[int] = None) -> None:
        """Almacenar valor en el cluster"""
        await self.client.set(key, value, ex=ttl)
    
    async def delete(self, key: str) -> None:
        """Eliminar valor del cluster"""
        await self.client.delete(key)
    
    async def exists(self, key: str) -> bool:
        """Verificar existencia en el cluster"""
        return bool(await self.client.exists(key))
    
    async def clear(self) -> None:
        """Limpiar todo el cluster"""
        await self.client.flushall()
```

### Registrar Adaptador

```python
from adapters.caches.base import CacheFactory

# Registrar el nuevo adaptador
CacheFactory.register_adapter("redis-cluster", RedisCluterAdapter)

# Usar el adaptador personalizado
cache = BaseCache(
    model=MyModel,
    cache_type="redis-cluster",
    nodes=[
        {"host": "127.0.0.1", "port": 7001},
        {"host": "127.0.0.1", "port": 7002},
        {"host": "127.0.0.1", "port": 7003},
    ]
)
```

## Casos de Uso Específicos

### Cache-Aside Pattern

```python
async def get_user_with_cache(user_id: str) -> User:
    """Obtener usuario con patrón cache-aside"""
    
    # Intentar desde caché
    cached_user = await user_cache.get(f"user:{user_id}")
    if cached_user:
        return cached_user
    
    # Cargar desde base de datos
    user = await user_repository.get(user_id)
    if user:
        # Almacenar en caché
        await user_cache.set(f"user:{user_id}", user)
    
    return user

async def update_user_with_cache(user_id: str, updates: dict) -> User:
    """Actualizar usuario invalidando caché"""
    
    # Actualizar en base de datos
    updated_user = await user_repository.update(user_id, updates)
    
    # Invalidar caché
    await user_cache.delete(f"user:{user_id}")
    
    # Opcional: Precalentar caché
    await user_cache.set(f"user:{user_id}", updated_user)
    
    return updated_user
```

### Write-Through Pattern

```python
async def create_user_write_through(user_data: dict) -> User:
    """Crear usuario con patrón write-through"""
    
    # Crear en base de datos
    user = await user_repository.create(user_data)
    
    # Escribir inmediatamente en caché
    await user_cache.set(f"user:{user.id}", user)
    
    return user
```

### Distributed Caching con MemCache

```python
# Configuración para caché distribuido
distributed_cache = UserCache(
    cache_type="memcache",
    servers=[
        "cache-node-1:11211",
        "cache-node-2:11211", 
        "cache-node-3:11211"
    ],
    ttl=3600
)

# Las operaciones se distribuyen automáticamente
await distributed_cache.set("user:123", user)  # Se almacena en uno de los nodos
cached_user = await distributed_cache.get("user:123")  # Se recupera del nodo correcto
```

## Testing

### Mock para Testing

```python
import pytest
from adapters.caches.base import CacheAdapter, CacheFactory

class MockCacheAdapter(CacheAdapter):
    """Adaptador mock para testing"""
    
    def __init__(self):
        self._cache = {}
        self._get_calls = []
        self._set_calls = []
    
    async def get(self, key: str) -> Optional[str]:
        self._get_calls.append(key)
        return self._cache.get(key)
    
    async def set(self, key: str, value: str, ttl: Optional[int] = None) -> None:
        self._set_calls.append((key, value, ttl))
        self._cache[key] = value
    
    # ... resto de métodos

@pytest.fixture
def mock_cache():
    """Fixture para caché mock"""
    CacheFactory.register_adapter("mock", MockCacheAdapter)
    cache = BaseCache(model=User, cache_type="mock")
    yield cache
    # Cleanup
    del CacheFactory._adapters["mock"]

async def test_user_cache_operations(mock_cache):
    """Test de operaciones de caché"""
    user = User(id="1", name="Test", email="test@example.com")
    
    # Test set/get
    await mock_cache.set("user:1", user)
    cached_user = await mock_cache.get("user:1")
    
    assert cached_user.id == user.id
    assert cached_user.name == user.name
```

### Integration Testing

```python
import pytest
from adapters.caches.user import UserCache

@pytest.mark.asyncio
async def test_redis_integration():
    """Test de integración con Redis"""
    cache = UserCache(cache_type="redis")
    
    user = User(id="test", name="Integration Test", email="test@example.com")
    
    # Test completo
    await cache.set("test:user", user)
    cached_user = await cache.get("test:user")
    
    assert cached_user is not None
    assert cached_user.id == user.id
    
    # Cleanup
    await cache.delete("test:user")
```

## Mejores Prácticas

### 1. Nomenclatura de Claves

```python
# Usar prefijos consistentes
await user_cache.set(f"user:{user_id}", user)
await product_cache.set(f"product:{product_id}", product)
await session_cache.set(f"session:{session_id}", session)
```

### 2. Manejo de TTL

```python
# TTL diferenciado según tipo de datos
user_cache = UserCache(ttl=3600)        # 1 hora para usuarios
session_cache = SessionCache(ttl=1800)   # 30 min para sesiones
config_cache = ConfigCache(ttl=86400)    # 24 horas para configuración
```

### 3. Error Handling

```python
async def safe_cache_operation(key: str, fallback_func):
    """Operación de caché con fallback seguro"""
    try:
        result = await cache.get(key)
        if result:
            return result
    except Exception as e:
        logger.warning(f"Cache error: {e}")
    
    # Fallback
    result = await fallback_func()
    
    # Intentar almacenar (sin fallar si falla)
    try:
        await cache.set(key, result)
    except Exception as e:
        logger.warning(f"Cache set error: {e}")
    
    return result
```

### 4. Invalidación Inteligente

```python
async def invalidate_user_related_cache(user_id: str):
    """Invalidar caché relacionado con usuario"""
    keys_to_invalidate = [
        f"user:{user_id}",
        f"user_profile:{user_id}",
        f"user_permissions:{user_id}",
        f"user_preferences:{user_id}"
    ]
    
    for key in keys_to_invalidate:
        await cache.delete(key)
```

## Dependencias

### Redis

```bash
pip install redis
```

### MemCache  

```bash
pip install aiomcache
```

### Desarrollo/Testing

```bash
pip install pytest pytest-asyncio
```

## Ejemplos Completos

Ver el archivo `cache_example.py` en la carpeta `examples/` para ejemplos completos de uso con todos los backends y patrones de uso.
