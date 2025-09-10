"""
ALT-logging-utils: Generic logging utilities for Python projects.

This package provides reusable logging functions to reduce duplication
and maintain consistency across projects.
"""

from .constants import (
    LOG_SEPARATOR_CHAR,
    LOG_SEPARATOR_LENGTH,
    LOG_SUBSEPARATOR_CHAR,
)
from .core import (
    log_collection_completed,
    log_configuration,
    log_debug_value,
    log_error_with_context,
    log_file_operation_error,
    log_found_file,
    log_initialization,
    log_operation_status,
    log_saved_file,
    log_test_end,
    log_test_start,
)
from .exceptions import (
    ALTLoggingUtilsError,
    ConfigurationError,
    FormattingError,
    LoggerError,
    ValidationError,
)

__version__ = "0.1.0"

__all__ = [
    # Exceptions
    "ALTLoggingUtilsError",
    "ConfigurationError",
    "FormattingError",
    # Constants
    "LOG_SEPARATOR_CHAR",
    "LOG_SEPARATOR_LENGTH",
    "LOG_SUBSEPARATOR_CHAR",
    "LoggerError",
    "ValidationError",
    # Core functions
    "log_collection_completed",
    "log_configuration",
    "log_debug_value",
    "log_error_with_context",
    "log_file_operation_error",
    "log_found_file",
    "log_initialization",
    "log_operation_status",
    "log_saved_file",
    "log_test_end",
    "log_test_start",
]
