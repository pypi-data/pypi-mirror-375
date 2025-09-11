"""Custom exceptions for CSSCade."""


class CSSCadeException(Exception):
    """Base exception class for CSSCade."""
    pass


class CSSParseError(CSSCadeException):
    """Raised when CSS parsing fails."""
    pass


class CSSValidationError(CSSCadeException):
    """Raised when CSS validation fails."""
    pass


class ConflictResolutionError(CSSCadeException):
    """Raised when conflict resolution fails."""
    pass


class InvalidConfigurationError(CSSCadeException):
    """Raised when invalid configuration is provided."""
    pass