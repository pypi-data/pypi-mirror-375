"""Unit tests for SQLiteDatabase class."""

import sqlite3
from pathlib import Path

import pandas as pd
import pytest

from dbengine.engines.sqlite import SQLiteDatabase, SQLiteDatabaseConfig


@pytest.fixture
def test_config(tmp_path):
    """Create a test configuration for SQLiteDatabase."""
    return SQLiteDatabaseConfig(
        database_config={
            "path": str(tmp_path / "test.db"),
        },
        logging_config={"level": "INFO"},
    )


@pytest.fixture
def sqlite_db(test_config):
    """Create a SQLiteDatabase instance for testing."""
    return SQLiteDatabase(test_config)


@pytest.fixture
def sample_dataframe():
    """Create sample DataFrame for testing."""
    return pd.DataFrame(
        {
            "id": [1, 2, 3],
            "name": ["Alice", "Bob", "Charlie"],
            "age": [25, 30, 35],
            "city": ["New York", "London", "Tokyo"],
        }
    )


@pytest.fixture
def sample_series():
    """Create sample Series for testing."""
    return pd.Series({"id": 4, "name": "David", "age": 28, "city": "Paris"})


def test_init(test_config):
    """Test SQLiteDatabase initialization."""
    db = SQLiteDatabase(test_config)

    assert db.path == Path(test_config.get("database.params.path"))
    assert db.path.parent.exists()
    assert hasattr(db, "logger")


def test_validate_connection(sqlite_db: SQLiteDatabase):
    """Test _validate_connection method."""
    # Should not raise an exception for valid database
    sqlite_db._validate_connection()


def test_get_connection(sqlite_db: SQLiteDatabase):
    """Test _get_connection method."""
    conn = sqlite_db._get_connection()
    assert isinstance(conn, sqlite3.Connection)
    assert conn.row_factory == sqlite3.Row
    conn.close()


def test_list_tables(sqlite_db: SQLiteDatabase, sample_dataframe: pd.DataFrame):
    """Test list_tables method."""
    # Initially empty
    assert sqlite_db.list_tables() == []

    # After adding data
    sqlite_db.write("users", sample_dataframe)
    tables = sqlite_db.list_tables()
    assert "users" in tables


def test_write(
    sqlite_db: SQLiteDatabase, sample_dataframe: pd.DataFrame, sample_series: pd.Series
):
    """Test write method."""
    # Test DataFrame
    sqlite_db.write("users", sample_dataframe)
    result = sqlite_db.query(table_name="users")
    assert len(result) == 3
    assert list(result.columns) == ["id", "name", "age", "city"]

    # Test Series
    sqlite_db.write("profiles", sample_series)
    result = sqlite_db.query(table_name="profiles")
    assert len(result) == 1
    assert result.iloc[0]["name"] == "David"


def test_delete(sqlite_db: SQLiteDatabase, sample_dataframe: pd.DataFrame):
    """Test delete method."""
    sqlite_db.write("users", sample_dataframe)

    # Delete one record
    sqlite_db.delete("users", 2, "id")

    # Verify deletion
    result = sqlite_db.query(table_name="users")
    assert len(result) == 2
    assert 2 not in result["id"].tolist()


def test_query(sqlite_db: SQLiteDatabase, sample_dataframe: pd.DataFrame):
    """Test query method."""
    sqlite_db.write("users", sample_dataframe)

    # Query all data
    result = sqlite_db.query(table_name="users")
    assert len(result) == 3

    # Query with criteria
    result = sqlite_db.query(criteria={"age": 30}, table_name="users")
    assert len(result) == 1
    assert result.iloc[0]["name"] == "Bob"

    # Query all tables (when table_name is None)
    sqlite_db.write("customers", sample_dataframe)
    result = sqlite_db.query()
    assert len(result) == 6  # 3 rows from each table


def test_delete_table(sqlite_db: SQLiteDatabase, sample_dataframe: pd.DataFrame):
    """Test delete_table method."""
    sqlite_db.write("test_table", sample_dataframe)
    assert "test_table" in sqlite_db.list_tables()

    sqlite_db.delete_table("test_table")
    assert "test_table" not in sqlite_db.list_tables()
