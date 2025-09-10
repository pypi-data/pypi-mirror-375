# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-09-09

### Added

- **Initial Release**: Complete hexagonal architecture framework
- **Multi-Framework Support**: FastAPI, Flask, and Tornado adapters
- **Multi-Database Support**: PostgreSQL, MariaDB/MySQL, SQL Server, Oracle
- **Multi-Cache Support**: Redis, MemCache, and In-Memory caching
- **Multi-Messaging Support**: Kafka, RabbitMQ, AWS Kinesis, GCP Pub/Sub
- **Repository Pattern**: Generic CRUD operations with filtering and relations
- **Router System**: Web framework abstraction with consistent API
- **Cache System**: Multi-backend caching with TTL support
- **Event System**: Multi-backend event messaging with pub/sub patterns
- **Type Safety**: Full type hints support with Pydantic models
- **Configuration Management**: Environment-based configuration system
- **Comprehensive Documentation**: Detailed README files for each component
- **Examples**: Complete working examples for all supported frameworks

### Features

- **Hexagonal Architecture**: Clean separation of concerns with ports and adapters
- **Async/Await Support**: Full asynchronous programming support
- **Connection Pooling**: Database connection pool management
- **Error Handling**: Robust error handling with HTTP exceptions
- **Filtering System**: Advanced filtering with multiple operators
- **Relation Loading**: Eager loading support for database relations
- **Transaction Support**: Database transaction management
- **Custom Adapters**: Easy extension with custom adapter registration
- **Environment Configuration**: Automatic configuration from environment variables
- **Development Tools**: Pre-commit hooks, linting, and testing setup

### Documentation

- **Main README**: Project overview and quick start guide
- **Router Documentation**: [`src/adapters/routers/README.md`](src/adapters/routers/README.md)
- **Cache Documentation**: [`src/adapters/caches/README.md`](src/adapters/caches/README.md)
- **Event Documentation**: [`src/adapters/events/README.md`](src/adapters/events/README.md)
- **Repository Documentation**: [`src/adapters/repositories/README.md`](src/adapters/repositories/README.md)
- **Examples**: Complete working examples in [`examples/`](examples/) directory

### Dependencies

- **Core**: Pydantic, FastAPI, SQLAlchemy, AsyncPG
- **Optional Web Frameworks**: Flask, Tornado
- **Optional Databases**: aiomysql, aioodbc, cx_oracle_async
- **Optional Cache**: Redis, aiomcache
- **Optional Messaging**: aiokafka, aio-pika, aioboto3, google-cloud-pubsub

### Package Structure

```bash
py-hexagonal-arch/
├── src/
│   ├── adapters/          # Adapter implementations
│   │   ├── routers/       # Web framework adapters
│   │   ├── repositories/  # Database adapters
│   │   ├── caches/        # Cache adapters
│   │   └── events/        # Event messaging adapters
│   ├── ports/             # Port interfaces
│   ├── controllers/       # Base controllers
│   ├── models/            # Domain models
│   ├── schemas/           # Data schemas
│   └── config/            # Configuration management
├── examples/              # Working examples
└── docs/                  # Documentation
```

### Installation

```bash
# Basic installation
pip install py-hexagonal-arch

# With specific extras
pip install py-hexagonal-arch[redis,kafka]

# Full installation
pip install py-hexagonal-arch[all]
```

### Supported Python Versions

- Python 3.8+
- Python 3.9
- Python 3.10
- Python 3.11
- Python 3.12

### License

MIT License - see [LICENSE](LICENSE) for details.

---

## [Unreleased]

### Planned Features

- **NoRest Support**: SOAP, GraphQL adapter for web frameworks
- **NoSQL Support**: MongoDB, Neo4j adapters
- **Testing Utilities**: Test and fixtures

### Roadmap

- **v1.1.0**: Initial Project

---

For migration guides and detailed upgrade instructions, see the [Migration Guide](docs/MIGRATION.md).
