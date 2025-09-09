"""
Custom exceptions for the currency converter application.
"""


class CurrencyConverterError(Exception):
    """Base exception for currency converter errors."""
    pass


class InvalidCurrencyError(CurrencyConverterError):
    """Raised when an invalid currency code is provided."""
    pass


class APIError(CurrencyConverterError):
    """Raised when there's an error with the currency API."""
    pass


class RateLimitError(APIError):
    """Raised when API rate limit is exceeded."""
    pass


class NetworkError(CurrencyConverterError):
    """Raised when there's a network connectivity issue."""
    pass


class CacheError(CurrencyConverterError):
    """Raised when there's an error with caching operations."""
    pass
