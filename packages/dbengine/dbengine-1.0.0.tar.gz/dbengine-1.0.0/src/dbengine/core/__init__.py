"""Core database engine functionality."""

from dbengine.core.config import DatabaseConfig
from dbengine.core.database import Database
from dbengine.core.exceptions import (
    DatabaseConfigurationError,
    DatabaseConnectionError,
    DatabaseError,
    DatabaseQueryError,
    DatabaseReadError,
    DatabaseSecurityError,
    DatabaseValidationError,
    DatabaseWriteError,
)

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
]
