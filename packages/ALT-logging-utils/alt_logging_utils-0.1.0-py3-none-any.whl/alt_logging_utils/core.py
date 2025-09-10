"""
Core logging utility functions for ALT-logging-utils.

This module provides reusable logging functions to reduce duplication
and maintain consistency across projects.
"""

import logging
from pathlib import Path
from typing import Any, Optional

from .constants import (
    LOG_SEPARATOR_CHAR,
    LOG_SEPARATOR_LENGTH,
    LOG_SUBSEPARATOR_CHAR,
)


def log_test_start(
    logger: logging.Logger, test_name: str, test_class: Optional[str] = None,
) -> None:
    """
    Log the start of a test with consistent formatting.

    Args:
        logger: The logger instance to use
        test_name: Name of the test method
        test_class: Optional name of the test class or component
    """
    logger.info(f"\n{LOG_SEPARATOR_CHAR * LOG_SEPARATOR_LENGTH}")
    logger.info(f"Starting test: {test_name}")
    if test_class:
        logger.info(f"Testing: {test_class}")
    logger.info(f"{LOG_SEPARATOR_CHAR * LOG_SEPARATOR_LENGTH}\n")


def log_test_end(logger: logging.Logger, test_name: str) -> None:
    """
    Log the end of a test with consistent formatting.

    Args:
        logger: The logger instance to use
        test_name: Name of the test method
    """
    logger.info(f"\nCompleted test: {test_name}")
    logger.info(f"{LOG_SUBSEPARATOR_CHAR * LOG_SEPARATOR_LENGTH}\n")


def log_saved_file(
    logger: logging.Logger, file_type: str, filepath: Path, level: int = logging.DEBUG,
) -> None:
    """
    Log that a file has been saved with consistent formatting.

    Args:
        logger: The logger instance to use
        file_type: Type of file saved (e.g., "test result", "suite metadata")
        filepath: Path where the file was saved
        level: Logging level to use (default: DEBUG)
    """
    logger.log(level, f"Saved {file_type}: {filepath}")


def log_initialization(
    logger: logging.Logger, component: str, details: Optional[str] = None,
) -> None:
    """
    Log the initialization of a component with consistent formatting.

    Args:
        logger: The logger instance to use
        component: Name of the component being initialized
        details: Optional additional details about the initialization
    """
    message = f"Initialized {component}"
    if details:
        message += f": {details}"
    logger.info(message)


def log_configuration(
    logger: logging.Logger, component: str, **config_items: Any,
) -> None:
    """
    Log configuration details with consistent formatting.

    Args:
        logger: The logger instance to use
        component: Name of the component being configured
        **config_items: Configuration key-value pairs to log
    """
    logger.info(f"{component} configured")
    for key, value in config_items.items():
        logger.debug(f"{key}: {value}")


def log_error_with_context(
    logger: logging.Logger, error: Exception, context: str, **extra_info: Any,
) -> None:
    """
    Log an error with context information.

    Args:
        logger: The logger instance to use
        error: The exception that occurred
        context: Description of what was happening when the error occurred
        **extra_info: Additional context information
    """
    logger.error(f"Error {context}: {error}")
    for key, value in extra_info.items():
        logger.debug(f"  {key}: {value}")


def log_collection_completed(
    logger: logging.Logger, item_type: str, count: int,
) -> None:
    """
    Log that a collection operation has completed.

    Args:
        logger: The logger instance to use
        item_type: Type of items collected (e.g., "tests", "files")
        count: Number of items collected
    """
    logger.info(
        f"{item_type} collection completed - {count} {item_type.lower()} collected",
    )


def log_operation_status(
    logger: logging.Logger, operation: str, status: str, details: Optional[str] = None,
) -> None:
    """
    Log the status of an operation.

    Args:
        logger: The logger instance to use
        operation: Name of the operation
        status: Status of the operation (e.g., "started", "completed", "failed")
        details: Optional additional details
    """
    message = f"{operation} {status}"
    if details:
        message += f" - {details}"

    # Choose log level based on status
    if status.lower() in ["failed", "error"]:
        logger.error(message)
    elif status.lower() in ["warning", "skipped"]:
        logger.warning(message)
    else:
        logger.info(message)


def log_found_file(
    logger: logging.Logger, file_type: str, filepath: Path, level: int = logging.DEBUG,
) -> None:
    """
    Log that a file was found.

    Args:
        logger: The logger instance to use
        file_type: Type of file (e.g., "config file", "test result")
        filepath: Path to the file
        level: Logging level to use (default: DEBUG)
    """
    logger.log(level, f"Found {file_type}: {filepath}")


def log_file_operation_error(
    logger: logging.Logger,
    operation: str,
    filepath: Path,
    error: Exception,
    level: int = logging.ERROR,
) -> None:
    """
    Log a file operation error with consistent formatting.

    Args:
        logger: The logger instance to use
        operation: Operation that failed (e.g., "read", "write", "delete")
        filepath: Path to the file
        error: The exception that occurred
        level: Logging level to use (default: ERROR)
    """
    logger.log(level, f"Failed to {operation} {filepath}: {error}")


def log_debug_value(
    logger: logging.Logger, name: str, value: Any, prefix: str = "",
) -> None:
    """
    Log a debug value with consistent formatting.

    Args:
        logger: The logger instance to use
        name: Name of the value being logged
        value: The value to log
        prefix: Optional prefix for the log message
    """
    message = f"{prefix}{name}: {value}" if prefix else f"{name}: {value}"
    logger.debug(message)
