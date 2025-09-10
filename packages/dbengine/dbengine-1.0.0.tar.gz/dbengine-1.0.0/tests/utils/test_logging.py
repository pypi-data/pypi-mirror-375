import logging
from io import StringIO
from unittest.mock import patch

from dbengine.utils.logging import create_logger


def test_create_logger():
    """Test basic logger creation."""
    logger = create_logger("test_logger")

    assert logger.name == "test_logger"
    assert logger.level == logging.INFO
    assert logger.propagate is False
    assert len(logger.handlers) == 1


def test_create_logger_with_level():
    """Test logger creation with custom level."""
    logger = create_logger("test_logger", level=logging.DEBUG)

    assert logger.level == logging.DEBUG


def test_create_logger_with_custom_format():
    """Test logger creation with custom format."""
    custom_format = "%(name)s - %(message)s"
    logger = create_logger("test_logger", format=custom_format)

    handler = logger.handlers[0]
    assert handler.formatter is not None
    assert handler.formatter._fmt == custom_format


@patch("sys.stdout", new_callable=StringIO)
def test_logger_output(mock_stdout):
    """Test that logger produces output."""
    logger = create_logger("test_logger")
    logger.info("Test message")

    output = mock_stdout.getvalue()
    assert "Test message" in output
    assert "INFO" in output
