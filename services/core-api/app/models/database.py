"""
Database configuration and session management with pgvector support
"""

import os
from sqlalchemy import create_engine, MetaData, text, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from sqlalchemy.engine import Engine
import logging

logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://anzx_user:anzx_password@localhost:5432/anzx_platform"
)

# Read replica configuration (optional)
READ_REPLICA_URL = os.getenv("READ_REPLICA_URL")

# Create main engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=int(os.getenv("DB_POOL_SIZE", "10")),
    max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "20")),
    pool_pre_ping=True,
    pool_recycle=3600,
    pool_timeout=30,
    echo=os.getenv("DEBUG", "false").lower() == "true",
    # Enable pgvector extension
    connect_args={
        "options": "-c timezone=utc",
        "application_name": "anzx-core-api"
    }
)

# Read replica engine (if configured)
read_engine = None
if READ_REPLICA_URL:
    read_engine = create_engine(
        READ_REPLICA_URL,
        poolclass=QueuePool,
        pool_size=int(os.getenv("DB_READ_POOL_SIZE", "5")),
        max_overflow=int(os.getenv("DB_READ_MAX_OVERFLOW", "10")),
        pool_pre_ping=True,
        pool_recycle=3600,
        pool_timeout=30,
        echo=os.getenv("DEBUG", "false").lower() == "true",
        connect_args={
            "options": "-c timezone=utc -c default_transaction_read_only=on",
            "application_name": "anzx-core-api-read"
        }
    )

# Session factories
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
ReadSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=read_engine) if read_engine else SessionLocal

# Base class for models
Base = declarative_base()

# Metadata for migrations
metadata = MetaData()


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Enable pgvector extension on connection"""
    if "postgresql" in str(dbapi_connection):
        try:
            with dbapi_connection.cursor() as cursor:
                cursor.execute("CREATE EXTENSION IF NOT EXISTS vector")
                cursor.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")  # For text search
                cursor.execute("CREATE EXTENSION IF NOT EXISTS btree_gin")  # For GIN indexes
        except Exception as e:
            logger.warning(f"Could not enable extensions (may already exist): {e}")


def get_db():
    """Database dependency for FastAPI (write operations)"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_read_db():
    """Read-only database dependency for FastAPI (read operations)"""
    db = ReadSessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables and extensions"""
    try:
        # Enable extensions
        with engine.connect() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS btree_gin"))
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS uuid-ossp"))
            conn.commit()
        
        # Create tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables and extensions created successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


def check_db_health():
    """Check database connectivity and extensions"""
    try:
        with engine.connect() as conn:
            # Basic connectivity
            conn.execute(text("SELECT 1"))
            
            # Check extensions
            result = conn.execute(text("""
                SELECT extname FROM pg_extension 
                WHERE extname IN ('vector', 'pg_trgm', 'btree_gin', 'uuid-ossp')
            """))
            extensions = [row[0] for row in result]
            
            return {
                "status": "healthy",
                "extensions": extensions,
                "pool_size": engine.pool.size(),
                "checked_out": engine.pool.checkedout(),
                "overflow": engine.pool.overflow(),
                "checked_in": engine.pool.checkedin()
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }