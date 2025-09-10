"""
Unit tests for logging utility functions.
"""

import logging
from pathlib import Path
from unittest.mock import Mock, call

from alt_logging_utils import (
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


class TestLoggingUtils:
    """Test cases for logging utility functions."""

    def setup_method(self):
        """Create a mock logger for testing."""
        self.mock_logger = Mock(spec=logging.Logger)

    def test_log_test_start_with_class(self):
        """Test log_test_start with test class name."""
        log_test_start(self.mock_logger, "test_method", "TestClass")

        # Check all info calls were made
        expected_calls = [
            call("\n" + "=" * 60),
            call("Starting test: test_method"),
            call("Testing: TestClass"),
            call("=" * 60 + "\n"),
        ]
        assert self.mock_logger.info.call_count == 4
        self.mock_logger.info.assert_has_calls(expected_calls)

    def test_log_test_start_without_class(self):
        """Test log_test_start without test class name."""
        log_test_start(self.mock_logger, "test_method")

        # Should only have 3 info calls (no class name)
        expected_calls = [
            call("\n" + "=" * 60),
            call("Starting test: test_method"),
            call("=" * 60 + "\n"),
        ]
        assert self.mock_logger.info.call_count == 3
        self.mock_logger.info.assert_has_calls(expected_calls)

    def test_log_test_end(self):
        """Test log_test_end function."""
        log_test_end(self.mock_logger, "test_method")

        expected_calls = [
            call("\nCompleted test: test_method"),
            call("-" * 60 + "\n"),
        ]
        assert self.mock_logger.info.call_count == 2
        self.mock_logger.info.assert_has_calls(expected_calls)

    def test_log_saved_file_default_level(self):
        """Test log_saved_file with default DEBUG level."""
        filepath = Path("/tmp/test.json")
        log_saved_file(self.mock_logger, "test result", filepath)

        self.mock_logger.log.assert_called_once_with(
            logging.DEBUG, f"Saved test result: {filepath}",
        )

    def test_log_saved_file_custom_level(self):
        """Test log_saved_file with custom INFO level."""
        filepath = Path("/tmp/suite.json")
        log_saved_file(self.mock_logger, "suite metadata", filepath, level=logging.INFO)

        self.mock_logger.log.assert_called_once_with(
            logging.INFO, f"Saved suite metadata: {filepath}",
        )

    def test_log_initialization_with_details(self):
        """Test log_initialization with additional details."""
        log_initialization(self.mock_logger, "Storage", "/path/to/storage")

        self.mock_logger.info.assert_called_once_with(
            "Initialized Storage: /path/to/storage",
        )

    def test_log_initialization_without_details(self):
        """Test log_initialization without additional details."""
        log_initialization(self.mock_logger, "Plugin")

        self.mock_logger.info.assert_called_once_with("Initialized Plugin")

    def test_log_configuration(self):
        """Test log_configuration with multiple config items."""
        log_configuration(
            self.mock_logger,
            "Plugin",
            log_level="DEBUG",
            directory="/tmp",
            enabled=True,
        )

        # Check info call
        assert self.mock_logger.info.call_count == 1
        self.mock_logger.info.assert_called_with("Plugin configured")

        # Check debug calls for each config item
        assert self.mock_logger.debug.call_count == 3
        debug_calls = [call.args[0] for call in self.mock_logger.debug.call_args_list]
        assert "log_level: DEBUG" in debug_calls
        assert "directory: /tmp" in debug_calls
        assert "enabled: True" in debug_calls

    def test_log_error_with_context(self):
        """Test log_error_with_context with extra information."""
        error = ValueError("Test error")
        log_error_with_context(
            self.mock_logger,
            error,
            "processing file",
            filename="test.py",
            line_number=42,
        )

        # Check error call
        self.mock_logger.error.assert_called_once_with(
            "Error processing file: Test error",
        )

        # Check debug calls for extra info
        assert self.mock_logger.debug.call_count == 2
        debug_calls = [call.args[0] for call in self.mock_logger.debug.call_args_list]
        assert any("filename: test.py" in call for call in debug_calls)
        assert any("line_number: 42" in call for call in debug_calls)

    def test_log_collection_completed(self):
        """Test log_collection_completed function."""
        log_collection_completed(self.mock_logger, "Tests", 15)

        self.mock_logger.info.assert_called_once_with(
            "Tests collection completed - 15 tests collected",
        )

    def test_log_operation_status_info(self):
        """Test log_operation_status with info-level status."""
        log_operation_status(self.mock_logger, "Database backup", "completed")

        self.mock_logger.info.assert_called_once_with("Database backup completed")

    def test_log_operation_status_info_with_details(self):
        """Test log_operation_status with info-level status and details."""
        log_operation_status(
            self.mock_logger, "Database backup", "completed", "5GB in 2 minutes",
        )

        self.mock_logger.info.assert_called_once_with(
            "Database backup completed - 5GB in 2 minutes",
        )

    def test_log_operation_status_error(self):
        """Test log_operation_status with error status."""
        log_operation_status(
            self.mock_logger, "File upload", "failed", "permission denied",
        )

        self.mock_logger.error.assert_called_once_with(
            "File upload failed - permission denied",
        )

    def test_log_operation_status_warning(self):
        """Test log_operation_status with warning status."""
        log_operation_status(
            self.mock_logger, "Cache clear", "skipped", "already empty",
        )

        self.mock_logger.warning.assert_called_once_with(
            "Cache clear skipped - already empty",
        )

    def test_log_operation_status_various_error_keywords(self):
        """Test log_operation_status recognizes various error keywords."""
        error_keywords = ["failed", "error", "FAILED", "ERROR", "Error"]

        for keyword in error_keywords:
            self.mock_logger.reset_mock()
            log_operation_status(self.mock_logger, "Operation", keyword)
            self.mock_logger.error.assert_called_once()

    def test_log_operation_status_various_warning_keywords(self):
        """Test log_operation_status recognizes various warning keywords."""
        warning_keywords = ["warning", "skipped", "WARNING", "SKIPPED", "Warning"]

        for keyword in warning_keywords:
            self.mock_logger.reset_mock()
            log_operation_status(self.mock_logger, "Operation", keyword)
            self.mock_logger.warning.assert_called_once()

    def test_log_found_file(self):
        """Test log_found_file function."""
        filepath = Path("/path/to/config.yaml")
        log_found_file(self.mock_logger, "config file", filepath)

        self.mock_logger.log.assert_called_once_with(
            logging.DEBUG, "Found config file: /path/to/config.yaml",
        )

    def test_log_found_file_custom_level(self):
        """Test log_found_file with custom log level."""
        filepath = Path("/path/to/important.json")
        log_found_file(self.mock_logger, "important file", filepath, level=logging.INFO)

        self.mock_logger.log.assert_called_once_with(
            logging.INFO, "Found important file: /path/to/important.json",
        )

    def test_log_file_operation_error(self):
        """Test log_file_operation_error function."""
        filepath = Path("/path/to/file.txt")
        error = ValueError("Permission denied")
        log_file_operation_error(self.mock_logger, "write", filepath, error)

        self.mock_logger.log.assert_called_once_with(
            logging.ERROR, "Failed to write /path/to/file.txt: Permission denied",
        )

    def test_log_file_operation_error_custom_level(self):
        """Test log_file_operation_error with custom log level."""
        filepath = Path("/path/to/optional.txt")
        error = FileNotFoundError("File not found")
        log_file_operation_error(
            self.mock_logger, "read", filepath, error, level=logging.WARNING,
        )

        self.mock_logger.log.assert_called_once_with(
            logging.WARNING, "Failed to read /path/to/optional.txt: File not found",
        )

    def test_log_debug_value(self):
        """Test log_debug_value function."""
        log_debug_value(self.mock_logger, "config_version", "1.2.3")

        self.mock_logger.debug.assert_called_once_with("config_version: 1.2.3")

    def test_log_debug_value_with_prefix(self):
        """Test log_debug_value with prefix."""
        log_debug_value(self.mock_logger, "items processed", 42, prefix="Status: ")

        self.mock_logger.debug.assert_called_once_with("Status: items processed: 42")

    def test_log_debug_value_with_complex_value(self):
        """Test log_debug_value with complex value."""
        value = {"key": "value", "count": 10}
        log_debug_value(self.mock_logger, "settings", value)

        self.mock_logger.debug.assert_called_once_with(
            "settings: {'key': 'value', 'count': 10}",
        )
