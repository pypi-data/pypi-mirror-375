import logging
import sys
from typing import Optional, Union


def create_logger(
    name: str,
    level: Union[str, int] = logging.INFO,
    format: Optional[str] = None,
    handlers: Optional[list[logging.Handler]] = None,
) -> logging.Logger:
    """
    Create a configured logger instance.

    Args:
        name: Logger name
        level: Logging level (string or int)
        format: Log message format string
        handlers: list of logging handlers

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Prevent propagation to parent loggers to avoid duplicate messages
    logger.propagate = False

    # Default format if none provided
    if format is None:
        format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    formatter = logging.Formatter(format)

    # Clear existing handlers to avoid duplicates
    logger.handlers.clear()

    # Add provided handlers or default console handler
    if handlers:
        for handler in handlers:
            handler.setFormatter(formatter)
            logger.addHandler(handler)
    else:
        console_handler = logging.StreamHandler(stream=sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger
