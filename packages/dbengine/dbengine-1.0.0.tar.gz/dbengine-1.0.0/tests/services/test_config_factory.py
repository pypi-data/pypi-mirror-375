import tempfile
from pathlib import Path

import pytest
import yaml

from dbengine.core.exceptions import DatabaseConfigurationError
from dbengine.engines.sqlite import SQLiteDatabaseConfig
from dbengine.services.config_factory import DatabaseConfigFactory, create_config_file


def test_create_config_file():
    """Test creating a sample configuration file."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = Path(temp_dir) / "new_config.yaml"

        create_config_file(config_path, db_type="sqlite")

        assert config_path.exists()

        # Verify the created config can be loaded
        new_config = DatabaseConfigFactory.from_file(config_path)
        assert "path" in new_config.database_config


def test_get_config_helper():
    """Test the get_config helper function."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = Path(temp_dir) / "test_config.yaml"
        config_content = {
            "database": {
                "type": "sqlite",
                "params": {"path": "helper_test.db"},
            }
        }

        with open(config_path, "w") as f:
            yaml.safe_dump(config_content, f)

        config = DatabaseConfigFactory.from_file(config_path)
        assert isinstance(config, SQLiteDatabaseConfig)
        assert config.database_config["path"] == "helper_test.db"


def test_unsupported_db_type():

    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = Path(temp_dir) / "unsupported_config.yaml"
        with pytest.raises(DatabaseConfigurationError) as excinfo:
            create_config_file(config_path, db_type="unsupported_db")

        assert "Unsupported database type: unsupported_db" in str(excinfo.value)
