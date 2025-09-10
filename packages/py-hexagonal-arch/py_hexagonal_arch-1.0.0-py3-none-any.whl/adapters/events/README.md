# Multi-Backend Event Messaging System

El sistema de eventos ha sido refactorizado para soportar **Apache Kafka**, **RabbitMQ**, **AWS Kinesis** y **Google Cloud Pub/Sub** a través de una capa de abstracción que permite intercambiar sistemas de mensajería sin cambiar la lógica de negocio.

## Características

- ✅ **Soporte para Apache Kafka**: Sistema de mensajería distribuido de alto rendimiento
- ✅ **Soporte para RabbitMQ**: Broker de mensajes robusto con enrutamiento avanzado
- ✅ **Soporte para AWS Kinesis**: Streaming de datos en tiempo real de Amazon
- ✅ **Soporte para Google Cloud Pub/Sub**: Sistema de mensajería global de Google
- ✅ **Soporte In-Memory**: Sistema de eventos en memoria para testing y desarrollo
- ✅ **Interfaz unificada**: Misma API para todos los sistemas de mensajería
- ✅ **Extensible**: Fácil agregar soporte para otros sistemas
- ✅ **Type Safety**: Soporte completo para tipos genéricos
- ✅ **Async/Await**: Operaciones completamente asíncronas
- ✅ **Error Handling**: Manejo robusto de errores y reconexión

## Arquitectura

### Capa de Abstracción

La implementación utiliza el patrón **Adapter** para abstraer las diferencias entre sistemas:

- `EventAdapter`: Interfaz base para adaptadores de mensajería
- `KafkaAdapter`: Implementación específica para Apache Kafka
- `RabbitMQAdapter`: Implementación específica para RabbitMQ  
- `KinesisAdapter`: Implementación específica para AWS Kinesis
- `PubSubAdapter`: Implementación específica para Google Cloud Pub/Sub
- `InMemoryAdapter`: Implementación específica para eventos en memoria
- `EventFactory`: Factory para crear adaptadores
- `BaseEvent`: Clase base que implementa `EventPort` usando adaptadores

### Flujo de Trabajo

1. **Inicialización**: El `BaseEvent` recibe el tipo de sistema y configuración
2. **Adaptador**: Se crea el adaptador correspondiente usando el Factory
3. **Conexión**: Se establece conexión con el sistema de mensajería
4. **Operaciones**: Se ejecutan las operaciones usando la abstracción común

## Uso Básico

### Apache Kafka (Recomendado para Microservicios)

```python
from adapters.events.user import UserEvent

# Configuración por defecto (desde settings)
user_events = UserEvent()

# Configuración personalizada
user_events = UserEvent(
    event_type="kafka",
    bootstrap_servers="localhost:9092"
)

# Publicar evento
user = User(id="1", name="John", email="john@example.com")
await user_events.push("created", user, key=user.id)

# Consumir eventos
async for user_data in user_events.pull("created"):
    print(f"Usuario creado: {user_data.name}")
```

### RabbitMQ (Enrutamiento Avanzado)

```python
from adapters.events.user import UserEvent

# Configuración básica
user_events = UserEvent(
    event_type="rabbitmq",
    connection_url="amqp://localhost:5672"
)

# Con autenticación
user_events = UserEvent(
    event_type="rabbitmq",
    connection_url="amqp://user:password@localhost:5672/vhost"
)

# Publicar con callback de confirmación
await user_events.push("profile_updated", user, key=user.id)

# Suscribirse con callback
async def handle_user_event(user_data: User):
    print(f"Procesando usuario: {user_data.name}")

await user_events.pull("profile_updated", callback=handle_user_event)
```

### AWS Kinesis (Streaming de Datos)

```python
from adapters.events.user import UserEvent

# Configuración automática desde settings/environment
user_events = UserEvent(event_type="kinesis")

# Configuración con credenciales explícitas (sobrescribe defaults)
user_events = UserEvent(
    event_type="kinesis",
    region_name="us-east-1",
    aws_access_key_id="YOUR_ACCESS_KEY",
    aws_secret_access_key="YOUR_SECRET_KEY"
)

# Configuración parcial (el resto desde settings)
user_events = UserEvent(
    event_type="kinesis",
    region_name="us-west-2"  # Solo región personalizada
)

# Crear stream
await user_events.create_topic("user_activity", shard_count=2)

# Publicar eventos de actividad
await user_events.push("user_activity", user_activity_data, key=user.id)
```

### Google Cloud Pub/Sub (Global y Escalable)

```python
from adapters.events.user import UserEvent

# Configuración automática desde settings/environment
user_events = UserEvent(event_type="pubsub")

# Configuración con archivo de credenciales explícito
user_events = UserEvent(
    event_type="pubsub",
    project_id="my-gcp-project",
    credentials_path="/path/to/service-account.json"
)

# Configuración con credenciales por defecto (en GCE)
user_events = UserEvent(
    event_type="pubsub",
    project_id="my-gcp-project"  # Solo project ID personalizado
)

# Crear topic y subscription
await user_events.create_topic("user_notifications")

# Publicar notificación
await user_events.push("user_notifications", notification_data)
```

### In-Memory (Testing y Desarrollo)

```python
from adapters.events.user import UserEvent

# Sistema en memoria (sin dependencias externas)
user_events = UserEvent(event_type="memory")

# Perfecto para tests unitarios
await user_events.push("test_event", test_data)
events = []
async for event_data in user_events.pull("test_event"):
    events.append(event_data)
```

## Operaciones de Eventos

### Operaciones Básicas

```python
from models.user import User

# Crear evento de usuario
user = User(id="123", name="Alice", email="alice@example.com")

# Publicar evento
await user_events.push("created", user, key=user.id)

# Consumir eventos con async generator
async for user_data in user_events.pull("created"):
    print(f"Usuario: {user_data.name}")
    # Procesar solo el primero y salir
    break

# Consumir eventos con callback
async def process_user(user_data: User):
    print(f"Procesando usuario: {user_data.name}")
    # Lógica de procesamiento aquí

await user_events.pull("created", callback=process_user)
```

### Gestión de Topics/Streams

```python
# Crear topic/stream/exchange
await user_events.create_topic("user_analytics")

# Listar topics disponibles
topics = await user_events.list_topics()
print(f"Topics disponibles: {topics}")

# Eliminar topic (si es soportado)
await user_events.delete_topic("old_topic")

# Desconectar limpiamente
await user_events.disconnect()
```

### Operaciones Avanzadas

```python
from adapters.events.base import BaseEvent, EventMessage

# Evento personalizado para productos
class ProductEvent(BaseEvent[Product]):
    def __init__(self, event_type: str = "kafka"):
        super().__init__(
            model=Product,
            event_type=event_type,
            topic_prefix="product"
        )

# Uso del adaptador directamente
product_events = ProductEvent("kafka")

# Crear mensaje personalizado
message = EventMessage(
    topic="product.inventory_updated",
    data=product.model_dump(),
    key=product.id,
    headers={"source": "inventory_service", "version": "1.0"},
    timestamp=int(time.time() * 1000)
)

# Publicar mensaje personalizado
await product_events.event_adapter.publish(message)
```

## Configuración Automática

El sistema de eventos incluye **configuración automática inteligente** que carga credenciales y configuraciones desde las variables de entorno definidas en `settings.py`. Esto significa que puedes usar cualquier adaptador sin especificar credenciales explícitamente:

```python
# ✅ Configuración automática - carga todo desde environment/settings
user_events = UserEvent(event_type="kinesis")
order_events = OrderEventHandler(event_type="pubsub") 
product_events = ProductEvent(event_type="rabbitmq")

# ✅ Configuración híbrida - combina defaults con parámetros específicos
user_events = UserEvent(
    event_type="kinesis",
    region_name="eu-west-1"  # Solo región personalizada, resto automático
)

# ✅ Configuración explícita - sobrescribe todos los defaults
user_events = UserEvent(
    event_type="kinesis",
    region_name="us-east-1",
    aws_access_key_id="custom_key",
    aws_secret_access_key="custom_secret"
)
```

La configuración automática aplica a **todos los eventos** que hereden de `BaseEvent`, no solo a `UserEvent`.

## Configuración

### Variables de Entorno

#### Configuración General

```bash
# Tipo de sistema de eventos por defecto
EVENT_TYPE=kafka  # kafka, rabbitmq, kinesis, pubsub, memory
```

#### Configuración Apache Kafka

```bash
KAFKA_SERVER=localhost:9092
# Para múltiples brokers
KAFKA_SERVER=broker1:9092,broker2:9092,broker3:9092
```

#### Configuración RabbitMQ

```bash
RABBITMQ_URL=amqp://localhost:5672
# Con autenticación
RABBITMQ_URL=amqp://user:password@localhost:5672/vhost
```

#### Configuración AWS Kinesis

```bash
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
```

#### Configuración Google Cloud Pub/Sub

```bash
GCP_PROJECT_ID=my-gcp-project
GCP_CREDENTIALS_PATH=/path/to/service-account.json
```

### Configuración Programática

```python
from config.settings import settings

# Modificar configuración en runtime
settings.event_type = "rabbitmq"
settings.rabbitmq_url = "amqp://prod-rabbitmq:5672"
settings.aws_region = "eu-west-1"
```

## Creando Adaptadores Personalizados

### Implementar Adaptador

```python
from adapters.events.base import EventAdapter, EventMessage
from typing import Optional, List, Callable, AsyncGenerator

class RedisStreamsAdapter(EventAdapter):
    """Adaptador para Redis Streams"""
    
    def __init__(self, redis_url: str, **kwargs):
        try:
            import aioredis
            self.redis_url = redis_url
            self.redis = None
        except ImportError:
            raise ImportError("aioredis no está instalado")
    
    async def connect(self) -> None:
        """Conectar a Redis"""
        if not self.redis:
            import aioredis
            self.redis = await aioredis.from_url(self.redis_url)
    
    async def disconnect(self) -> None:
        """Desconectar de Redis"""
        if self.redis:
            await self.redis.close()
            self.redis = None
    
    async def publish(self, message: EventMessage) -> None:
        """Publicar mensaje a Redis Stream"""
        if not self.redis:
            await self.connect()
        
        await self.redis.xadd(
            message.topic,
            {
                "data": json.dumps(message.data),
                "key": message.key or "",
                **message.headers
            }
        )
    
    async def subscribe(
        self, 
        topic: str, 
        callback: Callable[[EventMessage], None],
        **kwargs
    ) -> None:
        """Suscribirse a Redis Stream"""
        if not self.redis:
            await self.connect()
        
        # Crear grupo de consumidores
        consumer_group = kwargs.get('consumer_group', 'default_group')
        consumer_name = kwargs.get('consumer_name', 'consumer_1')
        
        try:
            await self.redis.xgroup_create(topic, consumer_group, id='0', mkstream=True)
        except Exception:
            pass  # Grupo ya existe
        
        while True:
            messages = await self.redis.xreadgroup(
                consumer_group,
                consumer_name,
                {topic: '>'},
                count=1,
                block=1000
            )
            
            for stream, msgs in messages:
                for msg_id, fields in msgs:
                    data = json.loads(fields[b'data'].decode())
                    event_msg = EventMessage(
                        topic=topic,
                        data=data,
                        key=fields.get(b'key', b'').decode(),
                        headers={k.decode(): v.decode() for k, v in fields.items() 
                                if k not in [b'data', b'key']}
                    )
                    await callback(event_msg)
                    
                    # Confirmar procesamiento
                    await self.redis.xack(topic, consumer_group, msg_id)
    
    async def consume(self, topic: str, **kwargs) -> AsyncGenerator[EventMessage, None]:
        """Consumir mensajes de Redis Stream"""
        if not self.redis:
            await self.connect()
        
        last_id = kwargs.get('last_id', '0')
        
        while True:
            messages = await self.redis.xread({topic: last_id}, count=10, block=1000)
            
            for stream, msgs in messages:
                for msg_id, fields in msgs:
                    data = json.loads(fields[b'data'].decode())
                    yield EventMessage(
                        topic=topic,
                        data=data,
                        key=fields.get(b'key', b'').decode(),
                        headers={k.decode(): v.decode() for k, v in fields.items() 
                                if k not in [b'data', b'key']}
                    )
                    last_id = msg_id
    
    async def create_topic(self, topic: str, **kwargs) -> None:
        """Crear stream (se crea automáticamente al publicar)"""
        pass
    
    async def delete_topic(self, topic: str) -> None:
        """Eliminar stream de Redis"""
        if not self.redis:
            await self.connect()
        await self.redis.delete(topic)
    
    async def list_topics(self) -> List[str]:
        """Listar streams de Redis"""
        if not self.redis:
            await self.connect()
        
        # Buscar todas las claves que son streams
        keys = await self.redis.keys('*')
        streams = []
        
        for key in keys:
            key_type = await self.redis.type(key)
            if key_type == b'stream':
                streams.append(key.decode())
        
        return streams
```

### Registrar Adaptador

```python
from adapters.events.base import EventFactory

# Registrar el nuevo adaptador
EventFactory.register_adapter("redis-streams", RedisStreamsAdapter)

# Usar el adaptador personalizado
user_events = UserEvent(
    event_type="redis-streams",
    redis_url="redis://localhost:6379"
)
```

## Patrones de Uso

### Event Sourcing

```python
class UserAggregate:
    """Agregado de usuario con Event Sourcing"""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.events = UserEvent(event_type="kafka")
        self.version = 0
    
    async def create_user(self, name: str, email: str):
        """Crear usuario generando evento"""
        user = User(id=self.user_id, name=name, email=email)
        
        await self.events.push("created", user, key=self.user_id)
        self.version += 1
        
        return user
    
    async def update_email(self, new_email: str):
        """Actualizar email generando evento"""
        # Cargar estado actual desde eventos
        current_user = await self._rebuild_from_events()
        
        # Aplicar cambio
        current_user.email = new_email
        
        await self.events.push("email_updated", current_user, key=self.user_id)
        self.version += 1
        
        return current_user
    
    async def _rebuild_from_events(self) -> User:
        """Reconstruir estado desde eventos"""
        user = None
        
        async for event_data in self.events.pull("created"):
            if event_data.id == self.user_id:
                user = event_data
                break
        
        # Aplicar eventos posteriores
        async for event_data in self.events.pull("email_updated"):
            if event_data.id == self.user_id:
                user.email = event_data.email
        
        return user
```

### CQRS (Command Query Responsibility Segregation)

```python
class UserCommandHandler:
    """Manejador de comandos de usuario"""
    
    def __init__(self):
        self.events = UserEvent(event_type="kafka")
    
    async def handle_create_user(self, command: CreateUserCommand):
        """Manejar comando de crear usuario"""
        user = User(
            id=command.user_id,
            name=command.name,
            email=command.email
        )
        
        # Publicar evento
        await self.events.push("created", user, key=user.id)
        
        return user.id

class UserProjectionBuilder:
    """Constructor de proyecciones de usuario"""
    
    def __init__(self):
        self.events = UserEvent(event_type="kafka")
        self.db = get_read_database()
    
    async def start_projection(self):
        """Iniciar construcción de proyección"""
        async def handle_user_created(user: User):
            # Actualizar vista de lectura
            await self.db.users.insert_one({
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "created_at": datetime.utcnow()
            })
        
        # Suscribirse a eventos
        await self.events.pull("created", callback=handle_user_created)
```

### Saga Pattern

```python
class OrderSaga:
    """Saga para procesamiento de órdenes"""
    
    def __init__(self):
        self.order_events = BaseEvent(model=OrderEvent, event_type="kafka", topic_prefix="order")
        self.payment_events = BaseEvent(model=PaymentEvent, event_type="kafka", topic_prefix="payment")
        self.inventory_events = BaseEvent(model=InventoryEvent, event_type="kafka", topic_prefix="inventory")
    
    async def start_saga(self):
        """Iniciar saga de procesamiento"""
        
        # Manejar orden creada
        async def handle_order_created(order: OrderEvent):
            # Paso 1: Reservar inventario
            await self.inventory_events.push(
                "reserve_requested", 
                InventoryReservation(order_id=order.id, product_id=order.product_id, quantity=order.quantity)
            )
        
        # Manejar inventario reservado
        async def handle_inventory_reserved(reservation: InventoryEvent):
            # Paso 2: Procesar pago
            await self.payment_events.push(
                "payment_requested",
                PaymentRequest(order_id=reservation.order_id, amount=reservation.total)
            )
        
        # Manejar pago procesado
        async def handle_payment_processed(payment: PaymentEvent):
            # Paso 3: Confirmar orden
            await self.order_events.push(
                "confirmed",
                OrderConfirmation(order_id=payment.order_id)
            )
        
        # Manejar fallos para compensación
        async def handle_payment_failed(payment: PaymentEvent):
            # Compensar: liberar inventario
            await self.inventory_events.push(
                "release_requested",
                InventoryRelease(order_id=payment.order_id)
            )
        
        # Configurar suscripciones
        await self.order_events.pull("created", callback=handle_order_created)
        await self.inventory_events.pull("reserved", callback=handle_inventory_reserved)
        await self.payment_events.pull("processed", callback=handle_payment_processed)
        await self.payment_events.pull("failed", callback=handle_payment_failed)
```

### Outbox Pattern

```python
class OutboxEventPublisher:
    """Publisher de eventos usando patrón Outbox"""
    
    def __init__(self):
        self.events = UserEvent(event_type="kafka")
        self.db = get_database()
    
    async def publish_user_created(self, user: User):
        """Publicar evento de usuario creado usando outbox"""
        
        # Transacción atómica: guardar en DB y outbox
        async with self.db.transaction():
            # Guardar usuario
            await self.db.users.insert_one(user.model_dump())
            
            # Guardar evento en outbox
            outbox_event = {
                "id": str(uuid.uuid4()),
                "aggregate_type": "User",
                "aggregate_id": user.id,
                "event_type": "created",
                "event_data": user.model_dump_json(),
                "created_at": datetime.utcnow(),
                "published": False
            }
            await self.db.outbox.insert_one(outbox_event)
    
    async def process_outbox(self):
        """Procesar eventos pendientes en outbox"""
        
        # Buscar eventos no publicados
        unpublished_events = await self.db.outbox.find({"published": False}).to_list(100)
        
        for event in unpublished_events:
            try:
                # Publicar evento
                user_data = User.model_validate_json(event["event_data"])
                await self.events.push(event["event_type"], user_data, key=event["aggregate_id"])
                
                # Marcar como publicado
                await self.db.outbox.update_one(
                    {"id": event["id"]},
                    {"$set": {"published": True, "published_at": datetime.utcnow()}}
                )
                
            except Exception as e:
                print(f"Error publicando evento {event['id']}: {e}")
                # Implementar retry logic aquí
```

## Testing

### Mock para Testing

```python
import pytest
from adapters.events.base import EventAdapter, EventFactory, EventMessage

class MockEventAdapter(EventAdapter):
    """Adaptador mock para testing"""
    
    def __init__(self):
        self.published_messages = []
        self.subscriptions = {}
        self.topics = set()
    
    async def connect(self) -> None:
        pass
    
    async def disconnect(self) -> None:
        pass
    
    async def publish(self, message: EventMessage) -> None:
        self.published_messages.append(message)
        self.topics.add(message.topic)
        
        # Simular notificación a suscriptores
        if message.topic in self.subscriptions:
            for callback in self.subscriptions[message.topic]:
                await callback(message)
    
    async def subscribe(
        self, 
        topic: str, 
        callback: Callable[[EventMessage], None],
        **kwargs
    ) -> None:
        if topic not in self.subscriptions:
            self.subscriptions[topic] = []
        self.subscriptions[topic].append(callback)
    
    async def consume(self, topic: str, **kwargs) -> AsyncGenerator[EventMessage, None]:
        for message in self.published_messages:
            if message.topic == topic:
                yield message
    
    async def create_topic(self, topic: str, **kwargs) -> None:
        self.topics.add(topic)
    
    async def delete_topic(self, topic: str) -> None:
        self.topics.discard(topic)
    
    async def list_topics(self) -> List[str]:
        return list(self.topics)

@pytest.fixture
def mock_events():
    """Fixture para eventos mock"""
    EventFactory.register_adapter("mock", MockEventAdapter)
    events = UserEvent(event_type="mock")
    yield events
    # Cleanup
    del EventFactory._adapters["mock"]

@pytest.mark.asyncio
async def test_user_event_publishing(mock_events):
    """Test de publicación de eventos de usuario"""
    user = User(id="1", name="Test User", email="test@example.com")
    
    # Publicar evento
    await mock_events.push("created", user, key=user.id)
    
    # Verificar que se publicó
    adapter = mock_events.event_adapter
    assert len(adapter.published_messages) == 1
    
    published_message = adapter.published_messages[0]
    assert published_message.topic == "user.created"
    assert published_message.key == user.id
    assert published_message.data == user.model_dump()

@pytest.mark.asyncio
async def test_user_event_consumption(mock_events):
    """Test de consumo de eventos de usuario"""
    user = User(id="2", name="Consumer Test", email="consumer@example.com")
    
    # Publicar evento
    await mock_events.push("updated", user, key=user.id)
    
    # Consumir evento
    consumed_events = []
    async for event_data in mock_events.pull("updated"):
        consumed_events.append(event_data)
        break
    
    assert len(consumed_events) == 1
    assert consumed_events[0].id == user.id
    assert consumed_events[0].name == user.name
```

### Integration Testing

```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_kafka_integration():
    """Test de integración con Kafka"""
    events = UserEvent(event_type="kafka", bootstrap_servers="localhost:9092")
    
    user = User(id="integration_test", name="Integration User", email="integration@example.com")
    
    try:
        # Test publicación
        await events.push("integration_test", user, key=user.id)
        
        # Test consumo
        consumed = False
        async for event_data in events.pull("integration_test"):
            assert event_data.id == user.id
            consumed = True
            break
        
        assert consumed, "No se pudo consumir el evento publicado"
        
    finally:
        await events.disconnect()

@pytest.mark.integration
@pytest.mark.asyncio
async def test_rabbitmq_integration():
    """Test de integración con RabbitMQ"""
    events = UserEvent(event_type="rabbitmq", connection_url="amqp://localhost:5672")
    
    user = User(id="rabbitmq_test", name="RabbitMQ User", email="rabbitmq@example.com")
    
    try:
        await events.push("rabbitmq_test", user, key=user.id)
        
        # Verificar que el evento fue publicado
        adapter = events.event_adapter
        assert adapter.channel is not None
        
    except Exception as e:
        pytest.skip(f"RabbitMQ no disponible: {e}")
    finally:
        await events.disconnect()
```

## Performance y Optimización

### Configuración de Producción

```python
# Kafka - Alta disponibilidad
kafka_events = UserEvent(
    event_type="kafka",
    bootstrap_servers="kafka1:9092,kafka2:9092,kafka3:9092",
    acks='all',  # Esperar confirmación de todas las réplicas
    retries=3,   # Reintentos automáticos
    batch_size=16384,  # Tamaño de batch para mejor throughput
    compression_type='snappy'  # Compresión
)

# RabbitMQ - Durabilidad y confirmación
rabbitmq_events = UserEvent(
    event_type="rabbitmq",
    connection_url="amqp://user:pass@rabbitmq-cluster:5672",
    publisher_confirms=True,  # Confirmación de publicación
    delivery_mode=2  # Mensajes persistentes
)

# Kinesis - Particionamiento
kinesis_events = UserEvent(
    event_type="kinesis",
    region_name="us-east-1",
    # Usar partition key para distribuir carga
)
```

### Monitoreo y Métricas

```python
import time
from typing import Dict

class MetricsEventAdapter:
    """Wrapper para recopilar métricas de eventos"""
    
    def __init__(self, adapter: EventAdapter):
        self.adapter = adapter
        self.metrics = {
            'published': 0,
            'consumed': 0,
            'errors': 0,
            'latency_sum': 0,
            'latency_count': 0
        }
    
    async def publish(self, message: EventMessage) -> None:
        start_time = time.time()
        try:
            await self.adapter.publish(message)
            self.metrics['published'] += 1
        except Exception as e:
            self.metrics['errors'] += 1
            raise
        finally:
            latency = time.time() - start_time
            self.metrics['latency_sum'] += latency
            self.metrics['latency_count'] += 1
    
    def get_metrics(self) -> Dict[str, float]:
        """Obtener métricas actuales"""
        avg_latency = 0
        if self.metrics['latency_count'] > 0:
            avg_latency = self.metrics['latency_sum'] / self.metrics['latency_count']
        
        return {
            'published_total': self.metrics['published'],
            'consumed_total': self.metrics['consumed'],
            'errors_total': self.metrics['errors'],
            'average_latency_seconds': avg_latency
        }

# Uso con métricas
base_adapter = EventFactory.create_adapter("kafka")
metrics_adapter = MetricsEventAdapter(base_adapter)
```

## Mejores Prácticas

### 1. Nomenclatura de Topics
```python
# Usar prefijos consistentes y descriptivos
await user_events.push("profile.updated", user)  # user.profile.updated
await order_events.push("payment.processed", order)  # order.payment.processed
await inventory_events.push("stock.depleted", product)  # inventory.stock.depleted
```

### 2. Versionado de Eventos
```python
class UserEventV2(BaseModel):
    """Versión 2 del evento de usuario"""
    id: str
    name: str
    email: str
    phone: Optional[str] = None  # Nuevo campo
    version: str = "2.0"

# Publicar con versión
await user_events.push("created", user_v2, headers={"event_version": "2.0"})
```

### 3. Idempotencia
```python
# Usar claves de idempotencia
idempotency_key = f"{user.id}:{int(time.time())}"
await user_events.push("created", user, key=idempotency_key)
```

### 4. Dead Letter Queue
```python
class DeadLetterHandler:
    """Manejador para eventos fallidos"""
    
    def __init__(self):
        self.dlq_events = BaseEvent(model=dict, event_type="kafka", topic_prefix="dlq")
    
    async def handle_failed_event(self, original_message: EventMessage, error: Exception):
        """Enviar evento fallido a DLQ"""
        dlq_message = {
            "original_topic": original_message.topic,
            "original_data": original_message.data,
            "error": str(error),
            "timestamp": int(time.time()),
            "retry_count": original_message.headers.get("retry_count", 0) + 1
        }
        
        await self.dlq_events.push("failed", dlq_message)
```

### 5. Circuit Breaker
```python
class CircuitBreakerEventAdapter:
    """Adaptador con circuit breaker"""
    
    def __init__(self, adapter: EventAdapter, failure_threshold: int = 5):
        self.adapter = adapter
        self.failure_threshold = failure_threshold
        self.failure_count = 0
        self.is_open = False
        self.last_failure_time = None
    
    async def publish(self, message: EventMessage) -> None:
        if self.is_open:
            # Circuit breaker abierto - fallar rápido
            raise Exception("Circuit breaker is open")
        
        try:
            await self.adapter.publish(message)
            # Reset en caso de éxito
            self.failure_count = 0
        except Exception as e:
            self.failure_count += 1
            if self.failure_count >= self.failure_threshold:
                self.is_open = True
                self.last_failure_time = time.time()
            raise
```

## Dependencias

### Apache Kafka
```bash
pip install aiokafka
```

### RabbitMQ
```bash
pip install aio-pika
```

### AWS Kinesis
```bash
pip install aioboto3
```

### Google Cloud Pub/Sub
```bash
pip install google-cloud-pubsub
```

### Desarrollo/Testing
```bash
pip install pytest pytest-asyncio
```

## Ejemplos Completos

Ver el archivo `events_example.py` en la carpeta `examples/` para ejemplos completos de uso con todos los sistemas de mensajería y patrones de uso avanzados.
