"""
DBEngine - A unified interface for database operations across multiple backends.

Supports SQLite, Parquet, and PostgreSQL databases with a consistent pandas-based API.
"""

__version__ = "1.0.0"

from pathlib import Path

from .core import (  # Exceptions
    Database,
    DatabaseConfig,
    DatabaseConfigurationError,
    DatabaseConnectionError,
    DatabaseError,
    DatabaseQueryError,
    DatabaseReadError,
    DatabaseSecurityError,
    DatabaseValidationError,
    DatabaseWriteError,
)
from .engines import (
    ParquetDatabase,
    ParquetDatabaseConfig,
    PostgreSQLDatabase,
    PostgreSQLDatabaseConfig,
    SQLiteDatabase,
    SQLiteDatabaseConfig,
)
from .services import (
    DatabaseConfigFactory,
    DatabaseFactory,
    create_config_file,
    create_database,
)
from .utils import (
    PostgreSQLServerManager,
    create_postgres_server,
)

__root__ = Path(__file__).parent.parent.parent

__all__ = [
    "Database",
    "DatabaseConfig",
    # Exceptions
    "DatabaseError",
    "DatabaseConnectionError",
    "DatabaseWriteError",
    "DatabaseReadError",
    "DatabaseQueryError",
    "DatabaseConfigurationError",
    "DatabaseValidationError",
    "DatabaseSecurityError",
    # Engines and their configs
    "SQLiteDatabase",
    "ParquetDatabase",
    "PostgreSQLDatabase",
    "SQLiteDatabaseConfig",
    "ParquetDatabaseConfig",
    "PostgreSQLDatabaseConfig",
    # Factory services
    "DatabaseFactory",
    "DatabaseConfigFactory",
    "create_config_file",
    "create_database",
    # Server management utilities
    "PostgreSQLServerManager",
    "create_postgres_server",
]
