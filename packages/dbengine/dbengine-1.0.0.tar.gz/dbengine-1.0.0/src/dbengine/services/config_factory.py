from pathlib import Path
from typing import Any, Literal, Optional, Union, overload

import yaml

from dbengine.core.config import DatabaseConfig
from dbengine.core.exceptions import DatabaseConfigurationError
from dbengine.engines.parquet import ParquetDatabaseConfig
from dbengine.engines.postgresql import PostgreSQLDatabaseConfig
from dbengine.engines.sqlite import SQLiteDatabaseConfig
from dbengine.utils.logging import create_logger


class DatabaseConfigFactory:

    @classmethod
    def from_file(
        cls, config_path: Union[str, Path]
    ) -> Union[SQLiteDatabaseConfig, PostgreSQLDatabaseConfig, ParquetDatabaseConfig]:
        """Create DatabaseConfig from file - your current complex logic."""
        path = Path(config_path)
        config_data = cls._load_config(path)
        return cls.from_dict(config_data, config_path=path)

    @classmethod
    def from_dict(
        cls, config_data: dict, config_path: Optional[str | Path] = None
    ) -> Union[SQLiteDatabaseConfig, PostgreSQLDatabaseConfig, ParquetDatabaseConfig]:
        """Create from dictionary."""

        try:
            db_type = cls._extract_db_type(config_data)
        except DatabaseConfigurationError as e:
            raise DatabaseConfigurationError(e.message, config_path=str(config_path))

        try:
            database_config = cls._extract_database_config(config_data)
        except DatabaseConfigurationError as e:
            raise DatabaseConfigurationError(e.message, config_path=str(config_path))

        logging_config = cls._extract_logging_config(config_data)

        match db_type:
            case "sqlite":
                return SQLiteDatabaseConfig(
                    database_config=database_config,
                    logging_config=logging_config,
                )
            case "postgresql":
                return PostgreSQLDatabaseConfig(
                    database_config=database_config,
                    logging_config=logging_config,
                )
            case "parquet":
                return ParquetDatabaseConfig(
                    database_config=database_config,
                    logging_config=logging_config,
                )
            case _:
                raise DatabaseConfigurationError(
                    f"Unsupported database type: {db_type}",
                )

    @staticmethod
    def _extract_db_type(config: dict[str, dict[str, Any]]) -> str:
        db_type = str(config.get("database", {"type": "INVALID DEFAULT"}).get("type"))
        if db_type not in ["sqlite", "parquet", "postgresql"]:
            raise DatabaseConfigurationError(
                message=f"Unsupported database type: {db_type}",
            )
        return db_type.lower()

    @staticmethod
    def _extract_database_config(config: dict[str, dict[str, Any]]) -> dict[str, Any]:
        db_config = config.get("database", {"params": "INVALID DEFAULT"}).get("params")
        if not db_config:
            raise DatabaseConfigurationError(
                "Config file is missing database configuration through keyword `params`",
            )
        return db_config

    @staticmethod
    def _extract_logging_config(config: dict[str, dict[str, Any]]) -> dict[str, Any]:
        return config.get(
            "logging",
            {"level": "INFO", "format": None, "handlers": None},
        )

    @staticmethod
    def _load_config(path: Path) -> dict[str, Any]:
        """Load configuration from file."""
        if not path.exists():
            raise DatabaseConfigurationError(
                f"Configuration file not found: {path}",
                config_path=str(path),
                details="Configuration file is required for database connections",
            )

        try:
            with open(path, "r") as f:
                config_data = yaml.safe_load(f)

            if not config_data:
                raise DatabaseConfigurationError(
                    f"Configuration file is empty: {path}",
                    config_path=str(path),
                    details="Configuration file is required for database connections",
                )

        except Exception as e:
            raise DatabaseConfigurationError(
                f"Failed to load configuration file: {path}",
                config_path=str(path),
                details=str(e),
            )

        return config_data


logger = create_logger(__name__)


@overload
def create_config_file(
    path: Union[str, Path],
    db_type: str,
    load_config: Literal[True] = True,
    overwrite: bool = False,
) -> DatabaseConfig: ...


@overload
def create_config_file(
    path: Union[str, Path],
    db_type: str,
    load_config: Literal[False] = False,
    overwrite: bool = False,
) -> None: ...


def create_config_file(
    path: Union[str, Path],
    db_type: str,
    load_config: bool = False,
    overwrite: bool = False,
) -> None | DatabaseConfig:
    """
    Create a sample configuration file and load as DatabaseConfig type.
    If the config_path exists:
        If overwrite is True, the existing configuration file will be replaced.
        If overwrite is False and load_config is True,
            the existing configuration file will be loaded.
        If overwrite is False and load_config is False, an error will be raised.
    If the config_path does not exist:
        A new configuration file will be created.
        If load_config is True, the new configuration file will be loaded.
    """
    config_path = Path(path)
    if db_type not in ["parquet", "sqlite", "postgresql"]:
        raise DatabaseConfigurationError(
            f"Unsupported database type: {db_type}",
            config_path=str(config_path),
        )

    if config_path.exists() and not overwrite:
        if load_config:
            logger.info(f"Loading existing configuration file: {config_path}")
            return DatabaseConfigFactory.from_file(config_path)
        else:
            raise DatabaseConfigurationError(
                f"Configuration file already exists: {config_path}",
                config_path=str(config_path),
            )

    # Create directory if it doesn't exist or if overwrite is True
    config_path.parent.mkdir(parents=True, exist_ok=True)
    match db_type.lower():
        case "sqlite":
            sample_db_config = {
                "type": "sqlite",
                "params": {"path": "data/database.db"},
            }

        case "parquet":
            sample_db_config = {
                "type": "parquet",
                "params": {"path": "data/parquet"},
            }
        case "postgresql":
            sample_db_config = {
                "type": "postgresql",
                "params": {
                    "host": "localhost",
                    "port": 5432,
                    "database": "dbengine",
                    "user": "dbengine",
                    "password": "your_password_here",
                },
            }
        case _:
            raise DatabaseConfigurationError(
                f"Unsupported database type: {db_type}",
                config_path=str(config_path),
            )

    sample_config = {
        "database": sample_db_config,
        "logging": {
            "level": "INFO",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "handlers": None,
        },
    }

    try:
        with open(config_path, "w") as f:
            yaml.safe_dump(sample_config, f, default_flow_style=False, indent=2)

        logger.info(f"Created configuration file: {config_path}")

    except Exception as e:
        raise DatabaseConfigurationError(
            f"Failed to create configuration file: {config_path}",
            config_path=str(config_path),
            details=str(e),
        )

    if load_config:
        logger.info(f"Loading generated configuration file: {config_path}")
        return DatabaseConfigFactory.from_file(config_path)
