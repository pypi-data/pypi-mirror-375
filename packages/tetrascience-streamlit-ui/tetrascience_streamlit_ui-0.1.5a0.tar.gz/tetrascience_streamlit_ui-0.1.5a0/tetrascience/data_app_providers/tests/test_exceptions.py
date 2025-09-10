"""Tests for exceptions module."""

import pytest
from tetrascience.data_app_providers.exceptions import (
    ProviderError,
    MissingTableError,
    QueryError,
    InvalidProviderConfigurationError,
    ConnectionError,
)


class TestProviderExceptions:
    """Test provider exception classes."""

    def test_provider_error_base_class(self):
        """Test ProviderError base class."""
        error = ProviderError("Base error message")
        assert str(error) == "Base error message"
        assert isinstance(error, Exception)

    def test_missing_table_error(self):
        """Test MissingTableError inherits from ProviderError."""
        error = MissingTableError("Table not found")
        assert str(error) == "Table not found"
        assert isinstance(error, ProviderError)
        assert isinstance(error, Exception)

    def test_query_error(self):
        """Test QueryError inherits from ProviderError."""
        error = QueryError("Query failed")
        assert str(error) == "Query failed"
        assert isinstance(error, ProviderError)
        assert isinstance(error, Exception)

    def test_invalid_provider_configuration_error(self):
        """Test InvalidProviderConfigurationError inherits from ProviderError."""
        error = InvalidProviderConfigurationError("Invalid configuration")
        assert str(error) == "Invalid configuration"
        assert isinstance(error, ProviderError)
        assert isinstance(error, Exception)

    def test_connection_error(self):
        """Test ConnectionError inherits from ProviderError."""
        error = ConnectionError("Connection failed")
        assert str(error) == "Connection failed"
        assert isinstance(error, ProviderError)
        assert isinstance(error, Exception)

    def test_exception_hierarchy(self):
        """Test that all exceptions can be caught by ProviderError."""
        exceptions = [
            MissingTableError("test"),
            QueryError("test"),
            InvalidProviderConfigurationError("test"),
            ConnectionError("test"),
        ]

        for exc in exceptions:
            try:
                raise exc
            except ProviderError:
                # Should catch all provider exceptions
                pass
            except Exception:
                pytest.fail(f"{type(exc).__name__} should be caught by ProviderError")

    def test_exceptions_with_no_message(self):
        """Test exceptions can be created without message."""
        error = ProviderError()
        assert str(error) == ""

        error = MissingTableError()
        assert str(error) == ""

    def test_exceptions_with_multiple_args(self):
        """Test exceptions can handle multiple arguments."""
        error = QueryError("Query failed", "Additional info")
        # The exact string representation may vary, but should contain the message
        assert "Query failed" in str(error)
