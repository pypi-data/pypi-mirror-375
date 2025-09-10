"""SQLite database implementation."""

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional, Union

import pandas as pd

from dbengine.core.config import DatabaseConfig
from dbengine.core.database import Database
from dbengine.core.exceptions import (
    DatabaseConnectionError,
    DatabaseQueryError,
    DatabaseReadError,
    DatabaseWriteError,
)
from dbengine.utils.logging import create_logger


@dataclass
class SQLiteDatabaseConfig(DatabaseConfig):
    """Configuration for SQLite database."""

    def __post_init__(self):
        super().__post_init__()
        self.REQUIRED_FIELDS: list[str] = ["path"]


class SQLiteDatabase(Database):
    """SQLite database implementation using pandas objects."""

    def __init__(self, config: SQLiteDatabaseConfig):
        """
        Initialise SQLite database.

        Args:
            config: Database configuration object
        """
        super().__init__(config)
        self.logger = create_logger(__class__.__name__, **self.config.logging_config)
        self.path = Path(self.config.get("database.params.path"))

        # Create directory if it doesn't exist
        self.path.parent.mkdir(parents=True, exist_ok=True)

        # Test connection
        self._validate_connection()

        self.logger.info(f"Initialised SQLite database at {self.path}")

    def _validate_connection(self):
        """Validate database connection."""
        try:
            with self._get_connection() as conn:
                conn.execute("SELECT 1").fetchone()
            self.logger.info("SQLite connection validated successfully")
        except Exception as e:
            raise DatabaseConnectionError(
                f"Failed to connect to SQLite database at {self.path}",
                db_type="sqlite",
                details=str(e),
            )

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        try:
            conn = sqlite3.connect(str(self.path))
            conn.row_factory = sqlite3.Row  # Enable column access by name
            return conn
        except Exception as e:
            raise DatabaseConnectionError(
                "Failed to connect to SQLite database", db_type="sqlite", details=str(e)
            )

    def list_tables(self) -> list[str]:
        """List all tables in the database."""
        try:
            with self._get_connection() as conn:
                cursor = conn.execute(
                    "SELECT name FROM sqlite_master "
                    "WHERE type='table' AND name NOT LIKE 'sqlite_%'"
                )
                return [row[0] for row in cursor.fetchall()]

        except Exception as e:
            raise DatabaseReadError("Failed to list tables", details=str(e))

    def write(self, *, table_name: str, item: Union[pd.Series, pd.DataFrame]):
        """Write a pandas Series or DataFrame to the database"""
        try:
            if isinstance(item, pd.Series):
                df = item.to_frame().T
            elif isinstance(item, pd.DataFrame):
                df = item.copy()
            else:
                raise DatabaseWriteError(
                    f"Invalid item type ({type(item)}) " "to write to SQLite database"
                )

            with self._get_connection() as conn:
                df.to_sql(table_name, conn, if_exists="append", index=False)

        except Exception as e:
            raise DatabaseWriteError("Failed to write item to table", details=str(e))

    def delete(self, *, table_name: str, key: Any, key_column: str):
        try:
            with self._get_connection() as conn:
                conn.execute(f"DELETE FROM {table_name} WHERE {key_column} = '{key}'")
        except Exception as e:
            raise DatabaseWriteError("Failed to delete item from table", details=str(e))

    def query(
        self, *, criteria: Any = None, table_name: Optional[str] = None
    ) -> pd.DataFrame:
        try:
            if table_name is None:
                results = []
                for table in self.list_tables():
                    df_table = self.query(criteria=criteria, table_name=table)
                    results.append(df_table)
                return pd.concat(results, ignore_index=True)
            else:
                if table_name not in self.list_tables():
                    self.logger.warning(f"Table '{table_name}' does not exist")
                    return pd.DataFrame()

                where_clause = ""
                if criteria is not None:
                    # Build WHERE clauses from criteria
                    where_clauses = []
                    for column, value in criteria.items():
                        where_clauses.append(f"{column} = '{value}'")

                    if where_clauses:
                        where_clause = " WHERE " + " AND ".join(where_clauses)

                query = f"SELECT * FROM {table_name}{where_clause}"

                with self._get_connection() as conn:
                    return pd.read_sql(query, conn)

        except Exception as e:
            raise DatabaseQueryError(
                f"Failed to query table '{table_name}'", details=str(e)
            )

    def delete_table(self, table_name: str):
        """Delete a table from the database."""
        try:
            with self._get_connection() as conn:
                conn.execute(f"DROP TABLE IF EXISTS {table_name}")
        except Exception as e:
            raise DatabaseWriteError("Failed to delete table", details=str(e))
