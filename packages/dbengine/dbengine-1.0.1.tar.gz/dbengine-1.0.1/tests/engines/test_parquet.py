from pathlib import Path
from unittest.mock import patch

import pandas as pd
import pytest

from dbengine.core.exceptions import DatabaseValidationError
from dbengine.engines.parquet import ParquetDatabase, ParquetDatabaseConfig


@pytest.fixture
def test_config(tmp_path):
    """Create a test configuration for ParquetDatabase."""
    return ParquetDatabaseConfig(
        database_config={
            "path": str(tmp_path),
            "compression": "snappy",
            "engine": "pyarrow",
        },
        logging_config={"level": "INFO"},
    )


@pytest.fixture
def sample_data():
    """Create sample data for testing."""
    return pd.DataFrame(
        {"id": [1, 2, 3], "name": ["Alice", "Bob", "Charlie"], "age": [25, 30, 35]}
    )


def test_ParquetDatabase_init(test_config):
    """Test ParquetDatabase initialization."""
    db = ParquetDatabase(test_config)

    assert db.path == Path(test_config.get("database.params.path"))
    assert db.compression == "snappy"
    assert db.engine == "pyarrow"
    assert db.path.exists()


def test_ParquetDatabase__validate_permissions(test_config):
    """Test permission validation."""
    db = ParquetDatabase(test_config)

    # Should not raise an exception for valid directory
    db._validate_permissions()


def test_ParquetDatabase__get_table_path(test_config):
    """Test table path generation."""
    db = ParquetDatabase(test_config)

    table_path = db._get_table_path("test_table")
    expected_path = db.path / "test_table.parquet"

    assert table_path == expected_path


def test_ParquetDatabase__validate_table_name(test_config):
    """Test table name validation."""
    db = ParquetDatabase(test_config)

    # Valid names should not raise
    db._validate_table_name("valid_table")
    db._validate_table_name("table123")
    db._validate_table_name("table-name")

    # Invalid names should raise
    with pytest.raises(DatabaseValidationError):
        db._validate_table_name("invalid table")  # space

    with pytest.raises(DatabaseValidationError):
        db._validate_table_name("table@name")  # special character


def test_ParquetDatabase_list_tables(test_config, sample_data):
    """Test listing tables."""
    db = ParquetDatabase(test_config)

    # Initially no tables
    assert db.list_tables() == []

    # Add a table
    db.write("users", sample_data)
    tables = db.list_tables()
    assert "users" in tables
    assert len(tables) == 1


def test_ParquetDatabase_write(test_config, sample_data):
    """Test writing data to database."""
    db = ParquetDatabase(test_config)

    # Write DataFrame
    db.write("users", sample_data)

    # Check file was created
    table_path = db._get_table_path("users")
    assert table_path.exists()

    # Verify data can be read back
    result = db.query("users")
    assert len(result) == 3
    assert list(result.columns) == ["id", "name", "age"]


def test_ParquetDatabase_delete(test_config, sample_data):
    """Test deleting data from database."""
    db = ParquetDatabase(test_config)

    # Write initial data
    db.write("users", sample_data)

    # Delete one record
    db.delete("users", "id", 2)

    # Verify deletion
    result = db.query("users")
    assert len(result) == 2
    assert 2 not in result["id"].values


def test_ParquetDatabase_query(test_config, sample_data):
    """Test querying data from database."""
    db = ParquetDatabase(test_config)

    # Write test data
    db.write("users", sample_data)

    # Query all data
    result = db.query("users")
    assert len(result) == 3

    # Query with criteria
    result = db.query("users", criteria=[("age", ">=", 30)])
    assert len(result) == 2
    assert all(result["age"] >= 30)


def test_ParquetDatabase_delete_table(test_config, sample_data):
    """Test deleting entire table."""
    db = ParquetDatabase(test_config)

    # Write test data
    db.write("users", sample_data)
    assert "users" in db.list_tables()

    # Mock user input to confirm deletion
    with patch("builtins.input", return_value="y"):
        db.delete_table("users")

    # Verify table is gone
    assert "users" not in db.list_tables()
