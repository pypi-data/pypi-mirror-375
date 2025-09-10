"""
Settings module
"""

import os
from typing import List


# General
ENVIRONMENT = os.environ.get("ENVIRONMENT", "")
VERSION = os.environ.get("VERSION", "")

# Database Configuration
DATABASE_TYPE = os.environ.get("DATABASE_TYPE", "postgresql")  # postgresql, mariadb, sqlserver, oracle

# PostgreSQL
POSTGRES_NAME = os.environ.get("POSTGRES_NAME")
POSTGRES_PORT = os.environ.get("POSTGRES_PORT")
POSTGRES_HOST = os.environ.get("POSTGRES_HOST")
POSTGRES_USER = os.environ.get("POSTGRES_USER")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
POSTGRES_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_NAME}"
#print(POSTGRES_URL)

# MariaDB/MySQL
MARIADB_NAME = os.environ.get("MARIADB_NAME", os.environ.get("MYSQL_NAME", ""))
MARIADB_PORT = os.environ.get("MARIADB_PORT", os.environ.get("MYSQL_PORT", "3306"))
MARIADB_HOST = os.environ.get("MARIADB_HOST", os.environ.get("MYSQL_HOST", ""))
MARIADB_USER = os.environ.get("MARIADB_USER", os.environ.get("MYSQL_USER", ""))
MARIADB_PASSWORD = os.environ.get("MARIADB_PASSWORD", os.environ.get("MYSQL_PASSWORD", ""))
MARIADB_URL = f"mysql+aiomysql://{MARIADB_USER}:{MARIADB_PASSWORD}@{MARIADB_HOST}:{MARIADB_PORT}/{MARIADB_NAME}" if MARIADB_HOST else ""

# SQL Server
SQLSERVER_NAME = os.environ.get("SQLSERVER_NAME", "")
SQLSERVER_PORT = os.environ.get("SQLSERVER_PORT", "1433")
SQLSERVER_HOST = os.environ.get("SQLSERVER_HOST", "")
SQLSERVER_USER = os.environ.get("SQLSERVER_USER", "")
SQLSERVER_PASSWORD = os.environ.get("SQLSERVER_PASSWORD", "")
SQLSERVER_URL = f"mssql+aioodbc://{SQLSERVER_USER}:{SQLSERVER_PASSWORD}@{SQLSERVER_HOST}:{SQLSERVER_PORT}/{SQLSERVER_NAME}?driver=ODBC+Driver+17+for+SQL+Server" if SQLSERVER_HOST else ""

# Oracle
ORACLE_NAME = os.environ.get("ORACLE_NAME", "")
ORACLE_PORT = os.environ.get("ORACLE_PORT", "1521")
ORACLE_HOST = os.environ.get("ORACLE_HOST", "")
ORACLE_USER = os.environ.get("ORACLE_USER", "")
ORACLE_PASSWORD = os.environ.get("ORACLE_PASSWORD", "")
ORACLE_URL = f"oracle+cx_oracle_async://{ORACLE_USER}:{ORACLE_PASSWORD}@{ORACLE_HOST}:{ORACLE_PORT}/{ORACLE_NAME}" if ORACLE_HOST else ""

# Database Connection Pool Settings
DB_ECHO = os.environ.get("DB_ECHO", "false").lower() == "true"
DB_POOL_SIZE = int(os.environ.get("DB_POOL_SIZE", "10"))
DB_MAX_OVERFLOW = int(os.environ.get("DB_MAX_OVERFLOW", "20"))

# Redis
REDIS_PROTOCOL = os.environ.get("REDIS_PROTOCOL")
REDIS_HOST = os.environ.get("REDIS_HOST")
REDIS_PORT = os.environ.get("REDIS_PORT")
REDIS_USER = os.environ.get("REDIS_USER")
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD")
REDIS_TTL = int(os.environ.get("REDIS_TTL", 3600))
REDIS_URL: str = f"{REDIS_PROTOCOL}://{REDIS_USER}:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}"
#print(REDIS_URL)

# Cache Configuration
CACHE_TYPE = os.environ.get("CACHE_TYPE", "redis")  # redis, memcache, memory
CACHE_TTL = int(os.environ.get("CACHE_TTL", REDIS_TTL))

# MemCache
MEMCACHE_SERVERS = os.environ.get("MEMCACHE_SERVERS", "127.0.0.1:11211").split(",")
MEMCACHE_TTL = int(os.environ.get("MEMCACHE_TTL", 3600))

# Event Messaging Configuration
EVENT_TYPE = os.environ.get("EVENT_TYPE", "kafka")  # kafka, rabbitmq, kinesis, pubsub, memory

# Kafka
KAFKA_SERVER = os.environ.get("KAFKA_SERVER", "localhost:9092")
#print(KAFKA_SERVER)

# RabbitMQ
RABBITMQ_URL = os.environ.get("RABBITMQ_URL", "amqp://localhost")

# AWS Kinesis
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY", "")

# Google Cloud Pub/Sub
GCP_PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "")
GCP_CREDENTIALS_PATH = os.environ.get("GCP_CREDENTIALS_PATH", "")

# OpenAI
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
CLAUDE_API_KEY = os.environ.get("CLAUDE_API_KEY", "")


class Settings:
    """..."""

    environment: str = ENVIRONMENT
    version: str = VERSION

    # Database settings
    database_type: str = DATABASE_TYPE
    postgres_url: str = POSTGRES_URL
    mariadb_url: str = MARIADB_URL
    mysql_url: str = MARIADB_URL  # Alias for mariadb_url
    sqlserver_url: str = SQLSERVER_URL
    oracle_url: str = ORACLE_URL
    
    # Database connection pool settings
    db_echo: bool = DB_ECHO
    db_pool_size: int = DB_POOL_SIZE
    db_max_overflow: int = DB_MAX_OVERFLOW
    
    redis_url: str = REDIS_URL
    redis_ttl: int = REDIS_TTL
    
    # Cache settings
    cache_type: str = CACHE_TYPE
    cache_ttl: int = CACHE_TTL
    
    # MemCache settings
    memcache_servers: List[str] = MEMCACHE_SERVERS
    memcache_ttl: int = MEMCACHE_TTL

    # Event messaging settings
    event_type: str = EVENT_TYPE
    kafka_server: str = KAFKA_SERVER
    rabbitmq_url: str = RABBITMQ_URL
    
    # AWS settings
    aws_region: str = AWS_REGION
    aws_access_key_id: str = AWS_ACCESS_KEY_ID
    aws_secret_access_key: str = AWS_SECRET_ACCESS_KEY
    
    # GCP settings
    gcp_project_id: str = GCP_PROJECT_ID
    gcp_credentials_path: str = GCP_CREDENTIALS_PATH

    openai_api_key: str = OPENAI_API_KEY
    claude_api_key: str = CLAUDE_API_KEY

settings = Settings()