"""Test package initialisation and imports."""


def test_package_import():
    """Test basic package import."""
    import dbengine

    assert hasattr(dbengine, "__version__")


def test_core_imports():
    """Test core module imports."""
    from dbengine import Database, DatabaseConfig

    # Test that classes/functions are properly imported
    assert Database is not None
    assert DatabaseConfig is not None


def test_engine_imports():
    """Test database engine imports."""
    from dbengine import ParquetDatabase, PostgreSQLDatabase, SQLiteDatabase

    assert SQLiteDatabase is not None
    assert ParquetDatabase is not None
    assert PostgreSQLDatabase is not None


def test_exception_imports():
    """Test exception imports."""
    from dbengine import (
        DatabaseConfigurationError,
        DatabaseConnectionError,
        DatabaseError,
        DatabaseQueryError,
        DatabaseReadError,
        DatabaseSecurityError,
        DatabaseValidationError,
        DatabaseWriteError,
    )

    # Test exception hierarchy
    assert issubclass(DatabaseConnectionError, DatabaseError)
    assert issubclass(DatabaseWriteError, DatabaseError)
    assert issubclass(DatabaseReadError, DatabaseError)
    assert issubclass(DatabaseQueryError, DatabaseError)
    assert issubclass(DatabaseConfigurationError, DatabaseError)
    assert issubclass(DatabaseValidationError, DatabaseError)
    assert issubclass(DatabaseSecurityError, DatabaseError)


def test_module_attributes():
    """Test module has expected attributes."""
    import dbengine

    expected_attrs = [
        "Database",
        "DatabaseConfig",
        "DatabaseError",
        "DatabaseConnectionError",
        "DatabaseWriteError",
        "DatabaseReadError",
        "DatabaseQueryError",
        "DatabaseConfigurationError",
        "DatabaseValidationError",
        "DatabaseSecurityError",
        "SQLiteDatabase",
        "ParquetDatabase",
        "PostgreSQLDatabase",
        "SQLiteDatabaseConfig",
        "ParquetDatabaseConfig",
        "PostgreSQLDatabaseConfig",
        "DatabaseFactory",
        "DatabaseConfigFactory",
        "create_config_file",
        "create_database",
        "PostgreSQLServerManager",
        "create_postgres_server",
    ]

    for attr in expected_attrs:
        assert hasattr(dbengine, attr), f"Missing attribute: {attr}"
