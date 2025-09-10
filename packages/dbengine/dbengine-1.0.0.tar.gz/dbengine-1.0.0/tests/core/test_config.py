"""Test configuration management system."""

import pytest

from dbengine import (
    DatabaseConfig,
)


@pytest.fixture
def SQLiteDatabaseConfig(tmp_path):
    """Create a test configuration for SQLiteDatabase."""
    return DatabaseConfig(
        database_config={
            "path": str(tmp_path / "test.db"),
        },
        logging_config={"level": "INFO"},
    )


@pytest.fixture
def ParquetDatabaseConfig(tmp_path):
    """Create a test configuration for ParquetDatabase."""
    return DatabaseConfig(
        database_config={
            "path": str(tmp_path / "test.parquet"),
        },
        logging_config={"level": "INFO"},
    )


@pytest.fixture
def PostgreSQLDatabaseConfig(tmp_path):
    """Create a test configuration for PostgreSQLDatabase."""
    return DatabaseConfig(
        database_config={
            "host": "localhost",
            "port": 5432,
            "database": "test_db",
            "user": "test_user",
            "password": "test_password",
        },
        logging_config={"level": "INFO"},
    )


def test_dot_notation_get(SQLiteDatabaseConfig: DatabaseConfig):
    """Test dot notation configuration access."""
    assert str(SQLiteDatabaseConfig.get("database.params.path")).endswith("test.db")
    assert SQLiteDatabaseConfig.get("logging.level") == "INFO"
    assert SQLiteDatabaseConfig.get("nonexistent.key", "default") == "default"
