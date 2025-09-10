from abc import ABC, abstractmethod
from typing import Any, Optional, Union

import pandas as pd

from dbengine.core.config import DatabaseConfig


class Database(ABC):
    """
    Abstract class for database management using pandas objects
    """

    def __init__(self, config: DatabaseConfig):
        self.config = config

    @abstractmethod
    def list_tables(self) -> list[str]:
        """
        List all tables in the database.

        Returns:
            List of table names
        """
        raise NotImplementedError

    @abstractmethod
    def write(self, *, table_name: str, item: Union[pd.Series, pd.DataFrame]):
        """
        Write a pandas Series (single row) or DataFrame (multiple rows)
        to the database.

        Args:
            table_name: Name of the table
            item: pandas Series for single row or DataFrame for multiple rows
        """
        raise NotImplementedError

    @abstractmethod
    def delete(self, *, table_name: str, key: Any):
        """
        Delete an item from the table by primary key.

        Args:
            table_name: Name of the table
            key: Primary key value of the item to delete (can be any type)
        """
        raise NotImplementedError

    @abstractmethod
    def query(self, *, criteria: Any, table_name: Optional[str] = None) -> pd.DataFrame:
        """
        Query a table with specific criteria.

        Args:
            criteria: Query criteria (can be any type, depending on the type of database)
            table_name: Name of the table to query. If None, queries all tables.

        Returns:
            pandas DataFrame representing matching items
        """
        raise NotImplementedError

    @abstractmethod
    def delete_table(self, table_name: str):
        """
        Delete a table from the database.

        Args:
            table_name: Name of the table to delete
        """
        raise NotImplementedError
