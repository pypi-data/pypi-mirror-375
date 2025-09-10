import subprocess


def _is_docker_available() -> bool:
    """Check if Docker is available and running."""
    try:
        result = subprocess.run(
            ["docker", "--version"], capture_output=True, text=True, check=True
        )
        if result.returncode != 0:
            return False

        # Test Docker daemon connectivity
        subprocess.run(["docker", "info"], capture_output=True, check=True, timeout=10)
        return True

    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        return False
