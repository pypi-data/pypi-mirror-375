"""Unit tests for PostgreSQLDatabase class."""

from unittest.mock import Mock, patch

import pandas as pd
import pytest
from sqlalchemy.engine import Engine

from dbengine.core.exceptions import DatabaseValidationError
from dbengine.engines.postgresql import PostgreSQLDatabase, PostgreSQLDatabaseConfig


@pytest.fixture
def test_config():
    """Create a test configuration for PostgreSQLDatabase."""
    return PostgreSQLDatabaseConfig(
        database_config={
            "host": "localhost",
            "port": 5432,
            "database": "test_db",
            "user": "test_user",
            "password": "test_password",
            "pool_size": 5,
            "max_overflow": 10,
        },
        logging_config={"level": "INFO"},
    )


@pytest.fixture
def mock_engine():
    """Create a mock SQLAlchemy engine."""
    mock_engine = Mock(spec=Engine)
    mock_connection = Mock()

    # Setup context manager behavior for connections
    mock_connection.__enter__ = Mock(return_value=mock_connection)
    mock_connection.__exit__ = Mock(return_value=None)

    mock_engine.connect.return_value = mock_connection
    return mock_engine, mock_connection


@pytest.fixture
def postgresql_db(test_config, mock_engine):
    """Create a PostgreSQLDatabase instance for testing."""
    mock_engine_obj, mock_conn = mock_engine

    with patch("dbengine.engines.postgresql.create_engine", return_value=mock_engine_obj):
        with patch.object(PostgreSQLDatabase, "_validate_connection"):
            db = PostgreSQLDatabase(test_config)
            return db, mock_conn


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
    """Test PostgreSQLDatabase initialization."""
    with patch("dbengine.engines.postgresql.create_engine") as mock_create_engine:
        with patch.object(PostgreSQLDatabase, "_validate_connection"):
            db = PostgreSQLDatabase(test_config)

            assert db.host == "localhost"
            assert db.port == 5432
            assert db.database == "test_db"
            assert db.user == "test_user"
            assert db.password == "test_password"
            assert db.pool_size == 5
            assert db.max_overflow == 10
            assert hasattr(db, "logger")
            assert hasattr(db, "engine")
            mock_create_engine.assert_called_once()


def test_create_engine(test_config):
    """Test _create_engine method."""
    with patch("dbengine.engines.postgresql.create_engine") as mock_create_engine:
        with patch.object(PostgreSQLDatabase, "_validate_connection"):
            _ = PostgreSQLDatabase(test_config)

            # Check that create_engine was called with correct connection string
            mock_create_engine.assert_called_once()
            call_args = mock_create_engine.call_args
            connection_string = call_args[0][0]

            assert "postgresql://" in connection_string
            assert "test_user:test_password" in connection_string
            assert "localhost:5432" in connection_string
            assert "test_db" in connection_string

            # Check engine configuration
            kwargs = call_args[1]
            assert kwargs["pool_size"] == 5
            assert kwargs["max_overflow"] == 10
            assert kwargs["pool_pre_ping"] is True


def test_validate_connection(postgresql_db):
    """Test _validate_connection method."""
    db, mock_conn = postgresql_db
    mock_result = Mock()
    mock_conn.execute.return_value = mock_result

    # Should not raise an exception
    db._validate_connection()

    mock_conn.execute.assert_called_once()
    mock_result.fetchone.assert_called_once()


def test_engine_connection(postgresql_db):
    """Test engine connection context manager."""
    db, mock_conn = postgresql_db

    # Test that we can get a connection from the engine
    with db.engine.connect() as conn:
        assert conn == mock_conn

    # Verify the context manager was called
    mock_conn.__enter__.assert_called_once()
    mock_conn.__exit__.assert_called_once()


def test_list_tables(postgresql_db):
    """Test list_tables method."""
    db, mock_conn = postgresql_db
    mock_result = Mock()
    mock_result.__iter__ = Mock(
        return_value=iter([("users",), ("products",), ("orders",)])
    )
    mock_conn.execute.return_value = mock_result

    tables = db.list_tables()

    assert tables == ["users", "products", "orders"]
    mock_conn.execute.assert_called_once()
    # Verify the SQL query contains the expected table query
    call_args = mock_conn.execute.call_args[0][0]
    assert "information_schema.tables" in str(call_args)


def test_write(postgresql_db, sample_dataframe, sample_series):
    """Test write method."""
    db, mock_conn = postgresql_db

    # Mock pandas to_sql method at the DataFrame level
    with patch("pandas.DataFrame.to_sql") as mock_to_sql:
        db.write("users", sample_dataframe)
        mock_to_sql.assert_called_once_with(
            "users", db.engine, if_exists="append", index=False, method="multi"
        )

    # Test Series - it gets converted to DataFrame first
    with patch("pandas.DataFrame.to_sql") as mock_to_sql:
        db.write("profiles", sample_series)
        mock_to_sql.assert_called_once_with(
            "profiles", db.engine, if_exists="append", index=False, method="multi"
        )


def test_delete(postgresql_db):
    """Test delete method."""
    db, mock_conn = postgresql_db

    db.delete("users", 123, "id")

    # Verify execute was called with the SQL and parameters
    mock_conn.execute.assert_called_once()
    call_args = mock_conn.execute.call_args
    sql_query = str(call_args[0][0])
    params = call_args[0][1] if len(call_args[0]) > 1 else call_args[1]

    assert "DELETE FROM users WHERE id = :key" in sql_query
    assert params == {"key": 123}
    mock_conn.commit.assert_called_once()


def test_query(postgresql_db, sample_dataframe):
    """Test query method."""
    db, mock_conn = postgresql_db

    # Mock list_tables to return some tables
    with patch.object(db, "list_tables", return_value=["users"]):
        # Mock pandas read_sql
        with patch("pandas.read_sql", return_value=sample_dataframe) as mock_read_sql:
            # Query specific table
            result = db.query(table_name="users")
            assert len(result) == 3
            mock_read_sql.assert_called_once()

            # Query with criteria
            result = db.query(criteria={"age": 30}, table_name="users")
            mock_read_sql.assert_called()

            # Query all tables
            result = db.query()
            assert len(result) == 3


def test_delete_table(postgresql_db):
    """Test delete_table method."""
    db, mock_conn = postgresql_db

    db.delete_table("test_table")

    # Verify execute was called with DROP TABLE command
    mock_conn.execute.assert_called_once()
    call_args = mock_conn.execute.call_args
    sql_query = str(call_args[0][0])

    assert "DROP TABLE IF EXISTS test_table CASCADE" in sql_query
    mock_conn.commit.assert_called_once()


def test_validate_table_name(postgresql_db):
    """Test _validate_table_name method."""
    db, _ = postgresql_db

    # Valid names should not raise
    db._validate_table_name("valid_table")
    db._validate_table_name("table123")
    db._validate_table_name("table-name")
    db._validate_table_name("table_name")

    # Invalid names should raise
    with pytest.raises(DatabaseValidationError):
        db._validate_table_name("invalid table")  # space

    with pytest.raises(DatabaseValidationError):
        db._validate_table_name("table@name")  # special character

    with pytest.raises(DatabaseValidationError):
        db._validate_table_name("table;DROP TABLE users")  # SQL injection attempt
