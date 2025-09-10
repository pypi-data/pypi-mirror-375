# ALT-logging-utils

> Generic logging utilities for consistent log formatting across Python projects.

[![PyPI version](https://badge.fury.io/py/ALT-logging-utils.svg)](https://badge.fury.io/py/ALT-logging-utils)
[![Python Support](https://img.shields.io/pypi/pyversions/ALT-logging-utils.svg)](https://pypi.org/project/ALT-logging-utils/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/avilayani/ALT-logging-utils/actions/workflows/tests.yml/badge.svg)](https://github.com/avilayani/ALT-logging-utils/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/avilayani/ALT-logging-utils/branch/main/graph/badge.svg)](https://codecov.io/gh/avilayani/ALT-logging-utils)
[![Documentation Status](https://readthedocs.org/projects/alt-logging-utils/badge/?version=latest)](https://alt-logging-utils.readthedocs.io/en/latest/?badge=latest)

## Overview

ALT-logging-utils provides a collection of reusable logging functions to reduce duplication and maintain consistency across Python projects. These utilities help format log messages in a structured and readable way.

## Features

- **Test Logging**: Log test starts and ends with clear visual separators
- **File Operations**: Log file saves, reads, and errors with consistent formatting
- **Component Lifecycle**: Log initialization and configuration of components
- **Error Context**: Log errors with additional context information
- **Operation Status**: Log operation status with automatic level selection
- **Debug Values**: Log debug values with optional prefixes
- **Collection Operations**: Log collection completion with item counts

## Installation

```bash
pip install ALT-logging-utils
```

## Quick Start

```python
import logging
from pathlib import Path
from alt_logging_utils import (
    log_test_start,
    log_test_end,
    log_saved_file,
    log_error_with_context,
    log_operation_status,
)

# Set up your logger
logger = logging.getLogger(__name__)

# Log test execution
log_test_start(logger, "test_user_authentication", "AuthenticationModule")
# ... test code ...
log_test_end(logger, "test_user_authentication")

# Log file operations
log_saved_file(logger, "configuration", Path("/etc/app/config.yml"))

# Log errors with context
try:
    result = risky_operation()
except Exception as e:
    log_error_with_context(
        logger, 
        e, 
        "processing user request",
        user_id=12345,
        operation="data_sync"
    )

# Log operation status
log_operation_status(logger, "Database backup", "completed", "5GB in 2 minutes")
```

## API Reference

### Test Logging

#### `log_test_start(logger, test_name, test_class=None)`
Logs the start of a test with visual separators.

```python
log_test_start(logger, "test_login", "UserAuthTests")
```

#### `log_test_end(logger, test_name)`
Logs the end of a test.

```python
log_test_end(logger, "test_login")
```

### File Operations

#### `log_saved_file(logger, file_type, filepath, level=logging.DEBUG)`
Logs that a file has been saved.

```python
log_saved_file(logger, "report", Path("./reports/monthly.pdf"), level=logging.INFO)
```

#### `log_found_file(logger, file_type, filepath, level=logging.DEBUG)`
Logs that a file was found.

```python
log_found_file(logger, "config file", Path("/etc/app/config.yml"))
```

#### `log_file_operation_error(logger, operation, filepath, error, level=logging.ERROR)`
Logs a file operation error.

```python
try:
    content = file.read()
except IOError as e:
    log_file_operation_error(logger, "read", Path("data.json"), e)
```

### Component Lifecycle

#### `log_initialization(logger, component, details=None)`
Logs component initialization.

```python
log_initialization(logger, "Database Connection", "postgres://localhost:5432/mydb")
```

#### `log_configuration(logger, component, **config_items)`
Logs component configuration with key-value pairs.

```python
log_configuration(
    logger, 
    "API Client",
    base_url="https://api.example.com",
    timeout=30,
    retry_count=3
)
```

### Error Handling

#### `log_error_with_context(logger, error, context, **extra_info)`
Logs an error with contextual information.

```python
log_error_with_context(
    logger,
    exception,
    "processing payment",
    user_id=user.id,
    amount=150.00,
    currency="USD"
)
```

### Status and Progress

#### `log_operation_status(logger, operation, status, details=None)`
Logs operation status with automatic level selection based on status.

```python
log_operation_status(logger, "Data sync", "completed", "1000 records processed")
log_operation_status(logger, "Connection", "failed", "timeout after 30s")
```

#### `log_collection_completed(logger, item_type, count)`
Logs completion of a collection operation.

```python
log_collection_completed(logger, "Users", 42)
```

### Debug Helpers

#### `log_debug_value(logger, name, value, prefix="")`
Logs a debug value with consistent formatting.

```python
log_debug_value(logger, "cache_size", 1024)
log_debug_value(logger, "requests", 42, prefix="Stats: ")
```

## Constants

The package exports formatting constants that can be used in your own logging:

```python
from alt_logging_utils import (
    LOG_SEPARATOR_LENGTH,    # Length of separator lines (60)
    LOG_SEPARATOR_CHAR,      # Character for major separators ('=')
    LOG_SUBSEPARATOR_CHAR,   # Character for minor separators ('-')
)

# Use in your own logging
logger.info("=" * LOG_SEPARATOR_LENGTH)
```

## Best Practices

1. **Consistent Formatting**: Use these utilities throughout your project for consistent log formatting
2. **Appropriate Levels**: Use the `level` parameter to control log verbosity
3. **Rich Context**: Provide meaningful context with errors using `log_error_with_context`
4. **Structured Data**: Use `log_configuration` to log configuration in a structured way

## Requirements

- Python 3.8 or higher
- No external dependencies (uses only Python standard library)

## Documentation

Full documentation is available at:
- [Read the Docs](https://alt-logging-utils.readthedocs.io/) (coming soon)
- [GitHub Wiki](https://github.com/avilayani/ALT-logging-utils/wiki)
- [API Reference](https://github.com/avilayani/ALT-logging-utils/blob/main/docs/API.md)

## Development

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/avilayani/ALT-logging-utils.git
cd ALT-logging-utils

# Set up development environment
make setup

# Or manually:
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests with coverage
make test

# Run specific tests
pytest tests/test_logging_utils.py

# Run with coverage report
pytest --cov=alt_logging_utils --cov-report=html
```

### Code Quality

```bash
# Run all quality checks
make all

# Individual checks
make lint        # Run linting
make format      # Format code
make type-check  # Type checking
```

### Building Documentation

```bash
# Build HTML documentation
make docs

# Serve documentation locally
make docs-live
```

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details on:
- Code style and standards
- Development workflow
- Submitting pull requests
- Reporting issues

## Roadmap

- [ ] Add structured logging support (JSON output)
- [ ] Add async logging utilities
- [ ] Add performance metrics logging
- [ ] Add log aggregation helpers
- [ ] Add more customization options

## Support

- **Issues**: [GitHub Issues](https://github.com/avilayani/ALT-logging-utils/issues)
- **Discussions**: [GitHub Discussions](https://github.com/avilayani/ALT-logging-utils/discussions)
- **Email**: [avilayani@gmail.com](mailto:avilayani@gmail.com)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Thanks to all contributors who have helped improve this package
- Inspired by the need for consistent logging across multiple projects

## Author

**Avi Layani**
- Email: [avilayani@gmail.com](mailto:avilayani@gmail.com)
- GitHub: [@avilayani](https://github.com/avilayani)
