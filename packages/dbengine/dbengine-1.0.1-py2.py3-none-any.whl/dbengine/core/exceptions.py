"""Enhanced exception handling for database operations."""

from typing import Optional


class DatabaseError(Exception):
    """Base exception class for all database operations."""

    def __init__(self, message: str, details: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.details = details


class DatabaseConnectionError(DatabaseError):
    """Raised when database connection fails."""

    def __init__(
        self, message: str, db_type: Optional[str] = None, details: Optional[str] = None
    ):
        super().__init__(message, details)
        self.db_type = db_type


class DatabaseWriteError(DatabaseError):
    """Raised when database write operation fails."""

    def __init__(
        self,
        message: str,
        table_name: Optional[str] = None,
        details: Optional[str] = None,
    ):
        super().__init__(message, details)
        self.table_name = table_name


class DatabaseReadError(DatabaseError):
    """Raised when database read operation fails."""

    def __init__(
        self,
        message: str,
        table_name: Optional[str] = None,
        key: Optional[str] = None,
        details: Optional[str] = None,
    ):
        super().__init__(message, details)
        self.table_name = table_name
        self.key = key


class DatabaseQueryError(DatabaseError):
    """Raised when database query operation fails."""

    def __init__(
        self,
        message: str,
        query: Optional[str] = None,
        table_name: Optional[str] = None,
        details: Optional[str] = None,
    ):
        super().__init__(message, details)
        self.query = query
        self.table_name = table_name


class DatabaseConfigurationError(DatabaseError):
    """Raised when database configuration is invalid."""

    def __init__(
        self,
        message: str,
        config_path: Optional[str] = None,
        details: Optional[str] = None,
    ):
        super().__init__(message, details)
        self.config_path = config_path


class DatabaseValidationError(DatabaseError):
    """Raised when data validation fails before database operations."""

    def __init__(
        self,
        message: str,
        field_name: Optional[str] = None,
        value: Optional[str] = None,
        details: Optional[str] = None,
    ):
        super().__init__(message, details)
        self.field_name = field_name
        self.value = value


class DatabaseSecurityError(DatabaseError):
    """Raised when security validation fails."""

    def __init__(
        self,
        message: str,
        security_context: Optional[str] = None,
        details: Optional[str] = None,
    ):
        super().__init__(message, details)
        self.security_context = security_context
