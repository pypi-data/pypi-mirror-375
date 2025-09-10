from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from dbengine.core.exceptions import DatabaseConfigurationError


@dataclass
class DatabaseConfig:
    """Configuration manager for database connections and settings."""

    # Core configuration data
    database_config: dict[str, Any]
    logging_config: dict[str, Any] = field(default_factory=dict)

    # Optional metadata
    config_path: Path | None = None
    _config_data: dict[str, Any] = field(default_factory=dict, repr=False)
    REQUIRED_FIELDS: list[str] = field(default_factory=list)

    def __post_init__(self):
        """Validate configuration after initialization."""
        self._validate_database_config()

        self._config_data = {
            "database": {"params": self.database_config},
            "logging": self.logging_config,
        }

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot notation key."""
        keys = key.split(".")
        current = self._config_data.copy()

        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return default

        return current

    def _validate_database_config(self):
        """Validate database configuration"""
        missing_fields = [
            field
            for field in self.REQUIRED_FIELDS
            if field not in self.database_config or self.database_config[field] is None
        ]

        if missing_fields:
            raise DatabaseConfigurationError(
                "Missing required configuration fields for "
                f"{__name__}: {missing_fields}",
                details=f"Available config: {list(self.database_config.keys())}",
            )
