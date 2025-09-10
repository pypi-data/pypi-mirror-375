from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional, Union

import pandas as pd
import pyarrow.parquet as pq

from dbengine.core.config import DatabaseConfig
from dbengine.core.database import Database
from dbengine.core.exceptions import (
    DatabaseConnectionError,
    DatabaseReadError,
    DatabaseValidationError,
    DatabaseWriteError,
)
from dbengine.utils.logging import create_logger


@dataclass
class ParquetDatabaseConfig(DatabaseConfig):
    """Configuration for Parquet database."""

    def __post_init__(self):
        super().__post_init__()
        self.REQUIRED_FIELDS: list[str] = ["path"]


class ParquetDatabase(Database):
    """Parquet database implementation using pandas objects."""

    def __init__(self, config: ParquetDatabaseConfig):
        """
        Initialise Parquet database.

        Args:
            config: Database configuration object

        """
        super().__init__(config)
        self.logger = create_logger(__class__.__name__, **self.config.logging_config)

        self.path = Path(config.get("database.params.path"))
        self.compression = config.get("database.params.compression", "snappy")
        self.engine = config.get("database.params.engine", "pyarrow")

        # Create directory if it doesn't exist
        self.path.mkdir(parents=True, exist_ok=True)

        # Test write permissions
        self._validate_permissions()

        self.logger.info(
            f"Initialised Parquet database at {self.path}. "
            "Parquet database will consist of multiple tables, "
            "each stored as a Parquet file."
        )

    def _validate_permissions(self):
        """Validate read/write permissions."""
        try:
            # Test write by creating a temporary file
            test_file = self.path / ".test_write"
            test_file.touch()
            test_file.unlink()
            self.logger.debug("Parquet directory permissions validated")
        except Exception as e:
            raise DatabaseConnectionError(
                f"No write permissions for directory {self.path}",
                db_type="parquet",
                details=str(e),
            )

    def _get_table_path(self, table_name: str) -> Path:
        """Get file path for a table."""
        return self.path / f"{table_name}.parquet"

    def _validate_table_name(self, table_name: str):
        """Validate table name."""
        if not table_name.replace("_", "").replace("-", "").isalnum():
            raise DatabaseValidationError(
                f"Invalid table name: {table_name}",
                field_name="table_name",
                value=table_name,
            )

    def list_tables(self) -> list[str]:
        """List all tables (parquet files) in the database."""
        try:
            parquet_files = list(self.path.glob("*.parquet"))
            return [f.stem for f in parquet_files]

        except Exception as e:
            raise DatabaseReadError("Failed to list tables", details=str(e))

    def write(self, *, table_name: str, item: Union[pd.Series, pd.DataFrame]):
        try:
            self._validate_table_name(table_name)

            if isinstance(item, pd.Series):
                df = item.to_frame().T
            else:
                df = item.copy()

            table_path = self._get_table_path(table_name)

            if table_path.exists():
                table = self.query(table_name=table_name)
            else:
                self.logger.info(f"Table {table_name} does not exist, creating it")
                table = pd.DataFrame(columns=df.columns)

            table = pd.concat([table, df], ignore_index=True)

            table.to_parquet(
                self._get_table_path(table_name),
                engine=self.engine,
                compression=self.compression,
                index=False,
            )

            self.logger.info(f"Written item to table '{table_name}'")

        except (DatabaseReadError, DatabaseWriteError):
            raise
        except Exception as e:
            raise DatabaseWriteError(
                f"Failed to write item to table {table_name}",
                table_name=table_name,
                details=str(e),
            )

    def delete(self, *, table_name: str, key_column: str, key: Any):
        """Delete an item from the table by primary key."""
        try:
            removing_table = self.query(
                table_name=table_name, criteria=[(key_column, "==", key)]
            )
            table = self.query(table_name=table_name, criteria=[(key_column, "!=", key)])
            if len(removing_table) > 0:
                self.logger.info(
                    f"Removing {len(removing_table)} items from "
                    f"table '{table_name}' with {key_column}={key}"
                )
            else:
                self.logger.info(
                    f"No items found in table '{table_name}' with {key_column}={key}"
                )
            table.to_parquet(
                self._get_table_path(table_name),
                engine=self.engine,
                compression=self.compression,
                index=False,
            )

        except (DatabaseReadError, DatabaseWriteError):
            raise
        except Exception as e:
            raise DatabaseWriteError(
                f"Failed to delete item from table {table_name}",
                table_name=table_name,
                details=str(e),
            )

    def query(
        self,
        *,
        table_name: Optional[str] = None,
        criteria: Optional[list[tuple[str, str, Any]]] = None,
    ) -> pd.DataFrame:
        """
        Query a table in the database according to given criteria.
        The criteria must be understandable by pyarrow.parquet, which means
        they must be filters on numeric values.

        An example of a valid criteria is criteria=[("age", ">", 25.0)]


        Args:
            table_name (Optional[str], optional): The name of the table to query.
                                                  Defaults to None.
            criteria (Optional[list[tuple[str, str, Any]]], optional):
                             The criteria to filter the query. Defaults to None.

        Raises:
            DatabaseReadError: If the query fails.

        Returns:
            pd.DataFrame: The result of the query.
        """
        try:
            if table_name is None:
                dfs = []
                for table_name in self.list_tables():
                    table = pq.read_table(
                        self._get_table_path(table_name), filters=criteria
                    ).to_pandas()
                    table["table"] = table_name

                    dfs.append(table)

                filtered = pd.concat(dfs, ignore_index=True)
            else:
                table_path = self._get_table_path(table_name)
                filtered = pq.read_table(
                    table_path,
                    filters=criteria,
                ).to_pandas()

            self.logger.info(
                f"Querying table '{table_name}' returned "
                f"{len(filtered):,.0f} matching rows"
            )
            return filtered
        except (DatabaseReadError, DatabaseReadError):
            raise
        except Exception as e:
            raise DatabaseReadError(
                f"Failed to query table {table_name}",
                table_name=table_name,
                details=str(e),
            )

    def delete_table(self, table_name: str):
        """Delete a table from the database."""
        if input(
            f"Are you sure you want to delete the table '{table_name}'? (y/n) "
        ).lower() not in ("y", "yes"):
            self.logger.info(f"Cancelled deletion of table '{table_name}'")
            return

        try:
            table_path = self._get_table_path(table_name)
            if table_path.exists():
                table_path.unlink()
                self.logger.info(f"Deleted table '{table_name}'")
            else:
                self.logger.info(f"Table '{table_name}' does not exist")

        except Exception as e:
            raise DatabaseWriteError(
                f"Failed to delete table {table_name}",
                table_name=table_name,
                details=str(e),
            )
