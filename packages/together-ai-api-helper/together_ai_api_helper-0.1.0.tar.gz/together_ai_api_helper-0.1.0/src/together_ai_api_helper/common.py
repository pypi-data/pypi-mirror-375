"""Common utilities and base client functionality for Together AI API Helper.

This module provides shared utilities used across the package, including:
- Logging configuration and setup
- Base client class with common functionality
- Shared initialization patterns
"""

import logging

from together import Together


def get_logger(name: str, log_file: str | None, log_level: int) -> logging.Logger:
    """Create and configure a logger with both file and console handlers.

    Args:
        name: The name of the logger, typically the module name
        log_file: Path to the log file where messages will be written.
            If log_file is None, no log file will be created.
        log_level: The level of the logger.

    Returns:
        A configured logger instance with the specified level logging
    """
    logger = logging.getLogger(name)
    logger.handlers.clear()
    if log_file:
        file_handler = logging.FileHandler(log_file, mode="a")
        file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
        logger.addHandler(file_handler)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter("%(levelname)s:%(name)s:%(message)s"))
    logger.addHandler(stream_handler)
    logger.setLevel(log_level)
    return logger


class CommonClient:
    """Base client class providing common functionality for Together AI API operations.

    This class serves as a foundation for specialized clients (endpoints, training)
    and provides shared initialization, logging, and client management.
    """

    def __init__(
        self,
        _name: str,
        client: Together | None = None,
        log_file: str | None = None,
        log_level: int | None = None,
    ):
        """Initialize the common client with logging and Together AI client.

        Args:
            _name: Name used for logging identification
            client: Optional Together client instance (creates new one if None)
            log_file: Path to log file for this client's operations
            log_level: The level of the logger
        """
        if client is None:
            client = Together()
        self.client = client
        self.logger = get_logger(_name, log_file, log_level or logging.INFO)
