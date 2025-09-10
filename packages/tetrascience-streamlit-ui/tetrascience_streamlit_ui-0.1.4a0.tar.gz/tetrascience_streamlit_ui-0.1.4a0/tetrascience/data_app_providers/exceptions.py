class ProviderError(Exception):
    """Base class for provider errors."""


class MissingTableError(ProviderError):
    """Raised when a table is missing in the database."""


class QueryError(ProviderError):
    """Raised when a query fails."""


class InvalidProviderConfigurationError(ProviderError):
    """Raised when the provider configuration is invalid."""


class ConnectionError(ProviderError):
    """Raised when connecting to a provider fails."""
