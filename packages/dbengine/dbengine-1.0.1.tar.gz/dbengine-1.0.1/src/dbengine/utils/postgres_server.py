"""PostgreSQL server management utilities for development and testing."""

import subprocess
import time
from contextlib import contextmanager
from typing import Optional

import psycopg2

from dbengine.utils import logging

logger = logging.create_logger(__name__)


class PostgreSQLServerManager:
    """
    Manages a PostgreSQL server instance using Docker containers.

    This class provides methods to start and stop PostgreSQL servers
    programmatically, making it ideal for development workflows,
    testing environments, and temporary database needs.

    Example:
        # Basic usage
        server = PostgreSQLServerManager(port=5433)
        server.start()
        # ... use database ...
        server.stop()

        # Context manager (recommended)
        with PostgreSQLServerManager(port=5434) as server:
            from dbengine.engines.postgresql import PostgreSQLDatabase
            db = PostgreSQLDatabase(**server.get_connection_params())
            # ... database operations ...
            db.close()
    """

    def __init__(
        self,
        container_name: str = "dbengine_postgres",
        port: int = 5433,
        password: str = "dbengine_pass",
        database: str = "dbengine_db",
        user: str = "dbengine_user",
        postgres_version: str = "15",
        **kwargs,
    ):
        """
        Initialise PostgreSQL server manager.

        Args:
            container_name: Name of the Docker container
            port: Port to expose PostgreSQL on (default: 5433 to avoid conflicts)
            password: PostgreSQL password
            database: Default database name
            user: PostgreSQL username
            postgres_version: PostgreSQL Docker image version
        """
        self.container_name = container_name
        self.port = port
        self.password = password
        self.database = database
        self.user = user
        self.postgres_version = postgres_version
        self._is_running = False

    def start(self) -> bool:
        """
        Start PostgreSQL server using Docker.

        Returns:
            bool: True if server started successfully, False otherwise

        Raises:
            Exception: If Docker is not available or server fails to start
        """
        try:
            # Verify Docker is available
            self._check_docker_availability()

            # Stop and remove existing container if it exists
            self._cleanup_existing_container()

            # Start new PostgreSQL container
            cmd = [
                "docker",
                "run",
                "-d",
                "--name",
                self.container_name,
                "-e",
                f"POSTGRES_PASSWORD={self.password}",
                "-e",
                f"POSTGRES_DB={self.database}",
                "-e",
                f"POSTGRES_USER={self.user}",
                "-p",
                f"{self.port}:5432",
                f"postgres:{self.postgres_version}",
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            container_id = result.stdout.strip()
            logger.info(f"PostgreSQL container started: {container_id}")

            # Wait for PostgreSQL to be ready
            self._wait_for_ready()
            self._is_running = True

            logger.info(f"PostgreSQL server ready on port {self.port}")
            return True

        except subprocess.CalledProcessError as e:
            error_msg = f"Failed to start PostgreSQL container: {e.stderr}"
            logger.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            logger.error(f"Unexpected error starting PostgreSQL: {e}")
            raise

    def stop(self) -> bool:
        """
        Stop PostgreSQL server and remove container.

        Returns:
            bool: True if server stopped successfully, False otherwise
        """
        try:
            # Stop container
            subprocess.run(
                ["docker", "stop", self.container_name],
                capture_output=True,
                check=True,
                timeout=30,
            )

            # Remove container
            subprocess.run(
                ["docker", "rm", self.container_name], capture_output=True, check=True
            )

            self._is_running = False
            logger.info("PostgreSQL container stopped and removed")
            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to stop PostgreSQL container: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error stopping PostgreSQL: {e}")
            return False

    def restart(self) -> bool:
        """
        Restart PostgreSQL server.

        Returns:
            bool: True if server restarted successfully, False otherwise
        """
        logger.info("Restarting PostgreSQL server...")
        self.stop()
        return self.start()

    def _check_docker_availability(self):
        """Check if Docker is available and running."""
        try:
            result = subprocess.run(
                ["docker", "--version"], capture_output=True, text=True, check=True
            )
            logger.debug(f"Docker found: {result.stdout.strip()}")

            # Test Docker daemon connectivity
            subprocess.run(
                ["docker", "info"], capture_output=True, check=True, timeout=10
            )

        except subprocess.CalledProcessError:
            raise Exception(
                "Docker is not available or not running. "
                "Please install Docker and ensure the Docker daemon is running."
            )
        except subprocess.TimeoutExpired:
            raise Exception(
                "Docker daemon is not responding. "
                "Please check if Docker is running properly."
            )
        finally:
            print("✅ Docker is available and running.")

    def _cleanup_existing_container(self):
        """Remove existing container if it exists."""
        subprocess.run(
            ["docker", "rm", "-f", self.container_name],
            capture_output=True,
            check=False,  # Don't fail if container doesn't exist
        )

    def _wait_for_ready(self, max_attempts: int = 30, delay: float = 1.0):
        """
        Wait for PostgreSQL server to be ready to accept connections.

        Args:
            max_attempts: Maximum number of connection attempts
            delay: Delay between attempts in seconds

        Raises:
            Exception: If server doesn't become ready within timeout
        """
        for attempt in range(max_attempts):
            try:
                conn = psycopg2.connect(
                    host="localhost",
                    port=self.port,
                    database=self.database,
                    user=self.user,
                    password=self.password,
                    connect_timeout=5,
                )
                conn.close()
                logger.info("PostgreSQL server is ready!")
                return

            except psycopg2.OperationalError as e:
                if attempt < max_attempts - 1:
                    logger.debug(
                        "Waiting for PostgreSQL... "
                        f"(attempt {attempt + 1}/{max_attempts})"
                    )
                    time.sleep(delay)
                else:
                    raise Exception(
                        "PostgreSQL server failed to start "
                        f"within {max_attempts * delay} seconds. "
                        f"Last error: {e}"
                    )

    def get_connection_params(self) -> dict:
        """
        Get connection parameters for this PostgreSQL instance.

        Returns:
            dict: Connection parameters compatible with PostgreSQLDatabase
        """
        return {
            "host": "localhost",
            "port": self.port,
            "database": self.database,
            "user": self.user,
            "password": self.password,
        }

    def get_connection_url(self) -> str:
        """
        Get PostgreSQL connection URL.

        Returns:
            str: PostgreSQL connection URL
        """
        return (
            f"postgresql://{self.user}:{self.password}"
            f"@localhost:{self.port}/{self.database}"
        )

    def is_running(self) -> bool:
        """
        Check if the PostgreSQL server is running.

        Returns:
            bool: True if server is running, False otherwise
        """
        return self._is_running

    def get_server_info(self) -> dict:
        """
        Get information about the PostgreSQL server.

        Returns:
            dict: Server information including connection details
        """
        return {
            "container_name": self.container_name,
            "port": self.port,
            "database": self.database,
            "user": self.user,
            "postgres_version": self.postgres_version,
            "is_running": self.is_running(),
            "connection_url": self.get_connection_url(),
        }

    @contextmanager
    def server_context(self):
        """
        Context manager for automatic server lifecycle management.

        Usage:
            with server.server_context():
                # Use database here
                db = PostgreSQLDatabase(**server.get_connection_params())
                # ... database operations ...
        """
        try:
            if not self.start():
                raise Exception("Failed to start PostgreSQL server")
            yield self
        finally:
            self.stop()

    def __enter__(self):
        """Enter context manager."""
        if not self.start():
            raise Exception("Failed to start PostgreSQL server")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager."""
        self.stop()

    def __repr__(self) -> str:
        """String representation of the server manager."""
        status = "running" if self.is_running() else "stopped"
        return f"PostgreSQLServerManager(port={self.port}, status={status})"


def create_postgres_server(
    port: Optional[int] = None,
    database: Optional[str] = None,
    user: Optional[str] = None,
    password: Optional[str] = None,
    **kwargs,
) -> PostgreSQLServerManager:
    """
    Create a PostgreSQL server manager with sensible defaults.

    This function provides a convenient way to create PostgreSQL servers
    for development and testing purposes.

    Args:
        port: Optional port override (default: 5433)
        database: Optional database name override
        user: Optional username override
        password: Optional password override
        **kwargs: Additional arguments passed to PostgreSQLServerManager

    Returns:
        PostgreSQLServerManager: Configured server manager instance

    Example:
        # Quick server for testing
        with create_postgres_server() as server:
            db = PostgreSQLDatabase(**server.get_connection_params())
            # ... use database ...

        # Custom configuration
        server = create_postgres_server(
            port=5434,
            database="my_app_db",
            user="app_user"
        )
    """
    if port is None:
        port = get_available_port()  # Use non-default port to avoid conflicts

    # Set sensible defaults
    defaults = {
        "container_name": f"dbengine_postgres_{port}",
        "port": port,
        "password": password or "dbengine_default_pass",
        "database": database or "dbengine_db",
        "user": user or "dbengine_user",
    }

    # Merge with any additional kwargs
    defaults.update(kwargs)

    return PostgreSQLServerManager(**defaults)


def get_available_port(start_port: int = 5433, max_attempts: int = 100) -> int:
    """
    Find an available port for PostgreSQL server.

    Args:
        start_port: Starting port to check
        max_attempts: Maximum number of ports to check

    Returns:
        int: Available port number

    Raises:
        Exception: If no available port is found
    """
    import socket

    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("localhost", port))
                return port
        except OSError:
            continue

    raise Exception(
        f"No available port found in range {start_port}-{start_port + max_attempts}"
    )
