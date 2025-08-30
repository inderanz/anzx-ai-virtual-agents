"""
Database configuration settings
"""

import os
from typing import Optional


class DatabaseConfig:
    """Database configuration settings"""
    
    # Primary database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://anzx_user:anzx_password@localhost:5432/anzx_platform"
    )
    
    # Read replica (optional)
    READ_REPLICA_URL: Optional[str] = os.getenv("READ_REPLICA_URL")
    
    # Connection pool settings
    POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "10"))
    MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "20"))
    POOL_TIMEOUT: int = int(os.getenv("DB_POOL_TIMEOUT", "30"))
    POOL_RECYCLE: int = int(os.getenv("DB_POOL_RECYCLE", "3600"))
    
    # Read replica pool settings
    READ_POOL_SIZE: int = int(os.getenv("DB_READ_POOL_SIZE", "5"))
    READ_MAX_OVERFLOW: int = int(os.getenv("DB_READ_MAX_OVERFLOW", "10"))
    
    # Query settings
    QUERY_TIMEOUT: int = int(os.getenv("DB_QUERY_TIMEOUT", "30"))
    STATEMENT_TIMEOUT: int = int(os.getenv("DB_STATEMENT_TIMEOUT", "60"))
    
    # Vector search settings
    VECTOR_DIMENSIONS: int = int(os.getenv("VECTOR_DIMENSIONS", "768"))
    IVFFLAT_LISTS: int = int(os.getenv("IVFFLAT_LISTS", "100"))
    
    # Performance settings
    ENABLE_QUERY_CACHE: bool = os.getenv("ENABLE_QUERY_CACHE", "true").lower() == "true"
    SLOW_QUERY_THRESHOLD: float = float(os.getenv("SLOW_QUERY_THRESHOLD", "1.0"))
    
    # Debug settings
    ECHO_SQL: bool = os.getenv("DEBUG", "false").lower() == "true"
    LOG_SLOW_QUERIES: bool = os.getenv("LOG_SLOW_QUERIES", "true").lower() == "true"
    
    @classmethod
    def get_connection_args(cls) -> dict:
        """Get connection arguments for SQLAlchemy"""
        return {
            "options": f"-c timezone=utc -c statement_timeout={cls.STATEMENT_TIMEOUT}s",
            "application_name": "anzx-core-api",
            "connect_timeout": cls.POOL_TIMEOUT,
        }
    
    @classmethod
    def get_read_connection_args(cls) -> dict:
        """Get read-only connection arguments"""
        args = cls.get_connection_args()
        args["options"] += " -c default_transaction_read_only=on"
        args["application_name"] = "anzx-core-api-read"
        return args


# Global config instance
db_config = DatabaseConfig()