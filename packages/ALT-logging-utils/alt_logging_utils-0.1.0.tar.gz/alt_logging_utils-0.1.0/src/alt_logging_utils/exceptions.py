"""Custom exceptions for ALT-logging-utils."""


class ALTLoggingUtilsError(Exception):
    """Base exception for ALT-logging-utils."""



class ConfigurationError(ALTLoggingUtilsError):
    """Raised when configuration is invalid."""



class ValidationError(ALTLoggingUtilsError):
    """Raised when validation fails."""



class LoggerError(ALTLoggingUtilsError):
    """Raised when there's an issue with the logger instance."""



class FormattingError(ALTLoggingUtilsError):
    """Raised when formatting operations fail."""

