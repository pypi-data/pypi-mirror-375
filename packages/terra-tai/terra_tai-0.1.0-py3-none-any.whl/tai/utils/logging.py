"""
Logging Utilities for Terra Command AI

This module provides logging configuration and utilities for consistent
logging across all Terra Command AI components.
"""

import logging
import sys
from typing import Optional
from pathlib import Path


def setup_logging(
    level: str = 'INFO',
    log_file: Optional[str] = None,
    verbose: bool = False
) -> logging.Logger:
    """
    Set up logging configuration for Terra Command AI.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
        verbose: Enable verbose output

    Returns:
        logging.Logger: Configured logger instance
    """
    # Convert string level to logging level
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    # Create formatter
    if verbose:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
        )
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )

    # Get or create logger
    logger = logging.getLogger('terra_ai')
    logger.setLevel(numeric_level)

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (if specified)
    if log_file:
        try:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            file_handler = logging.FileHandler(log_path)
            file_handler.setLevel(numeric_level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            logger.warning(f"Could not create log file {log_file}: {e}")

    return logger


def get_logger(name: str = 'terra_ai') -> logging.Logger:
    """
    Get a logger instance for a specific module.

    Args:
        name: Logger name (usually __name__)

    Returns:
        logging.Logger: Logger instance
    """
    return logging.getLogger(f"{name}")


class LoggerMixin:
    """
    Mixin class to add logging capabilities to any class.

    This mixin provides a logger property that automatically creates
    a logger with the class name.
    """

    @property
    def logger(self) -> logging.Logger:
        """Get logger instance for this class."""
        if not hasattr(self, '_logger'):
            self._logger = get_logger(self.__class__.__name__)
        return self._logger
