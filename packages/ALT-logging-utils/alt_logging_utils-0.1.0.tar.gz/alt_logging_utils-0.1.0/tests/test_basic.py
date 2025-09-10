"""Basic tests for ALT-logging-utils package."""

import alt_logging_utils


def test_package_has_version():
    """Test that the package has a version."""
    assert hasattr(alt_logging_utils, "__version__")
    assert isinstance(alt_logging_utils.__version__, str)
    assert alt_logging_utils.__version__ == "0.1.0"


def test_all_exports():
    """Test that all expected functions are exported."""
    expected_exports = [
        # Core functions
        "log_test_start",
        "log_test_end",
        "log_saved_file",
        "log_initialization",
        "log_configuration",
        "log_error_with_context",
        "log_collection_completed",
        "log_operation_status",
        "log_found_file",
        "log_file_operation_error",
        "log_debug_value",
        # Constants
        "LOG_SEPARATOR_LENGTH",
        "LOG_SEPARATOR_CHAR",
        "LOG_SUBSEPARATOR_CHAR",
    ]

    for export in expected_exports:
        assert hasattr(alt_logging_utils, export), f"Missing export: {export}"
