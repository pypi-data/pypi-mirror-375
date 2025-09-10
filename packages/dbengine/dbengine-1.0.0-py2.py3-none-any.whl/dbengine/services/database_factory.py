"""Database factory for creating database instances based on configuration."""

from pathlib import Path
from typing import Optional, Union, overload

import yaml

from dbengine.core.config import (
    DatabaseConfig,
)
from dbengine.core.database import Database
from dbengine.core.exceptions import DatabaseConfigurationError
from dbengine.engines.parquet import ParquetDatabase, ParquetDatabaseConfig
from dbengine.engines.postgresql import PostgreSQLDatabase, PostgreSQLDatabaseConfig
from dbengine.engines.sqlite import SQLiteDatabase, SQLiteDatabaseConfig
from dbengine.services.config_factory import DatabaseConfigFactory


class DatabaseFactory:
    """Factory for creating database instances based on configuration protocols."""

    @overload
    @staticmethod
    def create(config: ParquetDatabaseConfig) -> ParquetDatabase: ...

    @overload
    @staticmethod
    def create(config: SQLiteDatabaseConfig) -> SQLiteDatabase: ...

    @overload
    @staticmethod
    def create(config: PostgreSQLDatabaseConfig) -> PostgreSQLDatabase: ...

    @overload
    @staticmethod
    def create(config: DatabaseConfig) -> Database: ...

    @staticmethod
    def create(
        config: DatabaseConfig,
    ) -> Database | ParquetDatabase | SQLiteDatabase | PostgreSQLDatabase:
        """
        Create database instance based on configuration type.

        Args:
            config: DatabaseConfig instance

        Returns:
            Database: The appropriate database instance (SQLite, PostgreSQL, or Parquet)

        Raises:
            DatabaseConfigurationError: If database type is unsupported
        """
        if isinstance(config, SQLiteDatabaseConfig):
            return SQLiteDatabase(config)
        elif isinstance(config, PostgreSQLDatabaseConfig):
            return PostgreSQLDatabase(config)
        elif isinstance(config, ParquetDatabaseConfig):
            return ParquetDatabase(config)
        else:
            raise DatabaseConfigurationError(
                f"Unsupported database type: {config.__class__.__name__}",
                details="Supported types: sqlite, postgresql, parquet",
            )

    @classmethod
    def from_config_file(cls, config_path: Union[str, Path]) -> Database:
        """
        Create database instance directly from configuration file.

        Args:
            config_path: Path to configuration file

        Returns:
            Database: The appropriate database instance
        """
        config = DatabaseConfigFactory.from_file(config_path)
        return cls.create(config)

    @classmethod
    def from_config_dict(cls, config_dict: dict) -> Database:
        """
        Create database instance directly from configuration dictionary.

        Args:
            config_dict: Configuration dictionary

        Returns:
            Database: The appropriate database instance
        """
        config = DatabaseConfigFactory.from_dict(config_dict)
        return cls.create(config)


def create_database_from_config(config: Union[DatabaseConfig, Path]) -> Database:
    if isinstance(config, Path):
        return DatabaseFactory.from_config_file(config)
    elif isinstance(config, DatabaseConfig):
        return DatabaseFactory.create(config)
    raise DatabaseConfigurationError(
        f"Unsupported config type: {type(config).__name__}",
        details="Supported types: DatabaseConfig, Path",
    )


def create_database(
    db_type: str,
    database: str,
    host: Optional[str] = "localhost",
    user: Optional[str] = "dbengine",
    password: Optional[str] = None,
):
    # Validate inputs
    assert database is not None
    if db_type.lower() not in ["parquet", "sqlite", "postgresql"]:
        raise NotImplementedError(f"Unknown database type {db_type}")

    if db_type.lower() == "postgresql":
        assert host is not None
        assert user is not None
        assert password is not None

    config_path = f"./config_{database}.yaml"

    match db_type.lower():
        case "sqlite":
            db_config = {
                "type": "sqlite",
                "params": {"path": f"data_{database}.db"},
            }

        case "parquet":
            db_config = {
                "type": "parquet",
                "params": {"path": f"data_{database}/parquet"},
            }
        case "postgresql":
            db_config = {
                "type": "postgresql",
                "params": {
                    "host": host or "localhost",
                    "port": 5432,
                    "database": database or "dbengine",
                    "user": user or "dbengine",
                    "password": password or "password",
                },
            }
        case _:
            raise DatabaseConfigurationError(
                f"Unsupported database type: {db_type}",
                config_path=str(config_path),
            )
    config = {
        "database": db_config,
        "logging": {
            "level": "INFO",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "handlers": None,
        },
    }

    with open(config_path, "w") as f:
        yaml.safe_dump(config, f, default_flow_style=False, indent=2)

    return DatabaseFactory.from_config_file(config_path)
