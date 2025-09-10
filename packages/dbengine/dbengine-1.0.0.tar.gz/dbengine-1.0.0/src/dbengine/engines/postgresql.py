"""PostgreSQL database implementation using SQLAlchemy."""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.pool import QueuePool

from dbengine.core.config import DatabaseConfig
from dbengine.core.database import Database
from dbengine.core.exceptions import (
    DatabaseConnectionError,
    DatabaseQueryError,
    DatabaseReadError,
    DatabaseValidationError,
    DatabaseWriteError,
)
from dbengine.utils.logging import create_logger


@dataclass
class PostgreSQLDatabaseConfig(DatabaseConfig):
    """Configuration for PostgreSQL database."""

    def __post_init__(self):
        super().__post_init__()
        self.REQUIRED_FIELDS: list[str] = ["host", "port", "database", "user", "password"]


class PostgreSQLDatabase(Database):
    """PostgreSQL database implementation using SQLAlchemy."""

    def __init__(self, config: PostgreSQLDatabaseConfig):
        """
        Initialise PostgreSQL database.

        Args:
            config: Database configuration object
        """
        super().__init__(config)
        self.logger = create_logger(__class__.__name__, **self.config.logging_config)

        # Get database connection parameters
        self.host = self.config.get("database.params.host")
        self.port = self.config.get("database.params.port")
        self.database = self.config.get("database.params.database")
        self.user = self.config.get("database.params.user")
        self.password = self.config.get("database.params.password")
        self.pool_size = self.config.get("database.params.pool_size", 5)
        self.max_overflow = self.config.get("database.params.max_overflow", 10)

        # Create SQLAlchemy engine
        self._create_engine()

        # Test connection
        self._validate_connection()

        self.logger.info(
            "Initialised PostgreSQL database connection to "
            f"{self.host}:{self.port}/{self.database}"
        )

    def _create_engine(self):
        """Create SQLAlchemy engine with connection pooling."""
        try:
            # Create connection string
            connection_string = (
                f"postgresql://{self.user}:{self.password}@"
                f"{self.host}:{self.port}/{self.database}"
            )

            # Create engine with connection pooling
            self.engine: Engine = create_engine(
                connection_string,
                poolclass=QueuePool,
                pool_size=self.pool_size,
                max_overflow=self.max_overflow,
                pool_pre_ping=True,  # Verify connections before use
                echo=False,  # Set to True for SQL logging
            )

            self.logger.debug("SQLAlchemy engine created with connection pooling")
        except Exception as e:
            raise DatabaseConnectionError(
                "Failed to create PostgreSQL SQLAlchemy engine",
                db_type="postgresql",
                details=str(e),
            )

    def _validate_connection(self):
        """Validate database connection."""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                result.fetchone()
            self.logger.debug("PostgreSQL connection validated successfully")
        except Exception as e:
            raise DatabaseConnectionError(
                "Failed to connect to PostgreSQL database",
                db_type="postgresql",
                details=str(e),
            )

    def list_tables(self) -> List[str]:
        """List all tables in the database."""
        try:
            query = text(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_type = 'BASE TABLE'
                ORDER BY table_name
            """
            )

            with self.engine.connect() as conn:
                result = conn.execute(query)
                return [row[0] for row in result]

        except Exception as e:
            raise DatabaseReadError("Failed to list tables", details=str(e))

    def write(self, *, table_name: str, item: Union[pd.Series, pd.DataFrame]):
        """Write a pandas Series or DataFrame to the database."""
        try:
            if isinstance(item, pd.Series):
                df = item.to_frame().T
            elif isinstance(item, pd.DataFrame):
                df = item.copy()
            else:
                raise DatabaseWriteError(
                    f"Invalid item type ({type(item)}) to write to PostgreSQL database"
                )

            # Validate table name
            self._validate_table_name(table_name)

            # Use SQLAlchemy engine for pandas integration
            df.to_sql(
                table_name, self.engine, if_exists="append", index=False, method="multi"
            )

        except Exception as e:
            raise DatabaseWriteError(
                "Failed to write item to table", table_name=table_name, details=str(e)
            )

    def delete(self, *, table_name: str, key: Any, key_column: str):
        """Delete an item from the table by key."""
        try:
            # Validate table name
            self._validate_table_name(table_name)

            query = text(f"DELETE FROM {table_name} WHERE {key_column} = :key")

            with self.engine.connect() as conn:
                conn.execute(query, {"key": key})
                conn.commit()

        except Exception as e:
            raise DatabaseWriteError(
                "Failed to delete item from table", table_name=table_name, details=str(e)
            )

    def query(
        self,
        *,
        criteria: Optional[Dict[str, Any]] = None,
        table_name: Optional[str] = None,
    ) -> pd.DataFrame:
        """Query a table with specific criteria."""
        try:
            if table_name is None:
                # Query all tables
                results = []
                for table in self.list_tables():
                    df_table = self.query(criteria=criteria, table_name=table)
                    if len(df_table) > 0:
                        results.append(df_table)

                return (
                    pd.concat(results, ignore_index=True) if results else pd.DataFrame()
                )
            else:
                # Validate table exists
                if table_name not in self.list_tables():
                    self.logger.warning(f"Table '{table_name}' does not exist")
                    return pd.DataFrame()

                # Build query
                query_str = f"SELECT * FROM {table_name}"
                params = {}

                if criteria is not None:
                    where_clauses = []
                    for column, value in criteria.items():
                        param_name = f"param_{column}"
                        where_clauses.append(f"{column} = :{param_name}")
                        params[param_name] = value

                    if where_clauses:
                        query_str += " WHERE " + " AND ".join(where_clauses)

                query = text(query_str)

                with self.engine.connect() as conn:
                    return pd.read_sql(query, conn, params=params)

        except Exception as e:
            raise DatabaseQueryError(
                f"Failed to query table '{table_name}'",
                table_name=table_name,
                details=str(e),
            )

    def delete_table(self, table_name: str):
        """Delete a table from the database."""
        try:
            # Validate table name
            self._validate_table_name(table_name)

            query = text(f"DROP TABLE IF EXISTS {table_name} CASCADE")

            with self.engine.connect() as conn:
                conn.execute(query)
                conn.commit()

        except Exception as e:
            raise DatabaseWriteError(
                "Failed to delete table", table_name=table_name, details=str(e)
            )

    def _validate_table_name(self, table_name: str):
        """Validate table name for SQL injection prevention."""
        if not table_name.replace("_", "").replace("-", "").isalnum():
            raise DatabaseValidationError(
                f"Invalid table name: {table_name}",
                field_name="table_name",
                value=table_name,
                details=(
                    "Table name must contain only alphanumeric "
                    "characters, underscores, and hyphens"
                ),
            )

    def execute_sql(self, query: str) -> pd.DataFrame:
        """Execute a raw SQL query and return the results as a DataFrame."""
        try:
            with self.engine.connect() as conn:
                return pd.read_sql(text(query), conn)
        except Exception as e:
            raise DatabaseQueryError("Failed to execute SQL query", details=str(e))
