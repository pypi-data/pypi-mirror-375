"""
Test demonstrating PostgreSQL server management.

This test shows how to programmatically start and stop PostgreSQL servers
for testing and development purposes.
"""

import pandas as pd
import pytest

from dbengine.engines.postgresql import PostgreSQLDatabase
from dbengine.utils.postgres_server import PostgreSQLServerManager, create_postgres_server
from tests.conftest import _is_docker_available


@pytest.mark.skipif(
    not _is_docker_available(),  # Skip by default as it requires Docker
    reason="Requires Docker to be installed and running",
)
def test_manual_server_lifecycle():
    """Test manual start/stop of PostgreSQL server."""
    server: PostgreSQLServerManager = create_postgres_server(port=5434)

    try:
        # Start server
        assert server.start(), "Failed to start PostgreSQL server"
        assert server.is_running(), "Server should be running"

    finally:
        # Stop server
        assert server.stop(), "Failed to stop PostgreSQL server"
        assert not server.is_running(), "Server should be stopped"


@pytest.mark.skipif(
    not _is_docker_available(),  # Skip by default as it requires Docker
    reason="Requires Docker to be installed and running",
)
def test_context_manager_server():
    """Test PostgreSQL server using context manager."""
    server = create_postgres_server(port=5435)

    with server.server_context():
        # Server is automatically started
        assert server.is_running(), "Server should be running in context"

    # Server is automatically stopped
    assert not server.is_running(), "Server should be stopped after context"


@pytest.mark.skipif(
    not _is_docker_available(),  # Skip by default as it requires Docker
    reason="Requires Docker to be installed and running",
)
def test_multiple_servers():
    """Test running multiple PostgreSQL servers simultaneously."""
    server1 = create_postgres_server(port=5436)
    server2 = create_postgres_server(port=5437)

    try:
        # Start both servers
        assert server1.start(), "Failed to start first server"
        assert server2.start(), "Failed to start second server"

        assert server1.is_running(), "First server should be running"
        assert server2.is_running(), "Second server should be running"

    finally:
        # Clean up both servers
        server1.stop()
        server2.stop()


@pytest.mark.skipif(
    not _is_docker_available(),  # Skip by default as it requires Docker
    reason="Requires Docker to be installed and running",
)
def test_server_failure_recovery():
    """Test recovery from server failures."""
    server = create_postgres_server(port=5438)

    # Start server
    assert server.start(), "Failed to start server"

    # Simulate server crash by stopping container directly
    import subprocess

    subprocess.run(["docker", "kill", server.container_name], check=False)

    # Try to restart
    assert server.start(), "Failed to restart server after crash"

    # Clean up
    server.stop()


def example_usage():
    """Example of how to use PostgreSQL server management in your code."""

    print("=== PostgreSQL Server Management Example ===")

    # Method 1: Manual lifecycle management
    print("\n1. Manual server management:")
    server = create_postgres_server(port=5439)

    if server.start():
        print("✓ PostgreSQL server started successfully")

        # Get connection parameters
        conn_params = server.get_connection_params()
        print(
            f"✓ Connection: {conn_params['user']}"
            f"@{conn_params['host']}:{conn_params['port']}/{conn_params['database']}"
        )

        # Use with your existing DBEngine
        db = PostgreSQLDatabase(**conn_params)

        # Do some database work
        sample_data = pd.DataFrame(
            {
                "timestamp": pd.date_range("2024-01-01", periods=5, freq="D"),
                "value": [10, 20, 15, 25, 30],
            }
        )

        db.write("time_series", sample_data)
        result = db.query(table_name="time_series")
        print(f"✓ Wrote and read {len(result)} rows")

        server.stop()
        print("✓ Server stopped")

    # Method 2: Context manager (recommended)
    print("\n2. Context manager (automatic cleanup):")
    with create_postgres_server(port=5440) as server:
        print("✓ Server auto-started")

        db = PostgreSQLDatabase(**server.get_connection_params())
        tables = db.list_tables()
        print(f"✓ Found {len(tables)} existing tables")

    print("✓ Server auto-stopped")


if __name__ == "__main__":
    example_usage()
