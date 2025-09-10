"""Tests for provider module."""

import os
import json
import pytest
from unittest.mock import Mock, patch, MagicMock
from pydantic import ValidationError

from tetrascience.data_app_providers.provider import (
    get_provider_configurations,
    get_provider_secret_from_env,
    build_snowflake_provider,
    build_databricks_provider,
    build_provider,
    SnowflakeProvider,
    DatabricksProvider,
    AthenaProvider,
)
from tetrascience.data_app_providers.exceptions import (
    InvalidProviderConfigurationError,
    ConnectionError,
)
from tetrascience.data_app_providers.provider_typing import ProviderConfiguration


class TestGetProviderConfigurations:
    """Test get_provider_configurations function."""

    def test_empty_environment_returns_empty_list(
        self, mock_tdp_client, clean_environment
    ):
        """Test that empty environment returns empty list."""
        configs = get_provider_configurations(mock_tdp_client)
        assert configs == []

    def test_env_var_override_with_valid_json(self, mock_tdp_client):
        """Test provider configurations from environment variable."""
        provider_config = [
            {
                "name": "Test Provider",
                "type": "snowflake",
                "iconUrl": "https://example.com/icon.png",
                "fields": {"user": "test_user", "password": "test_pass"},
            }
        ]

        with patch.dict(
            os.environ, {"DATA_APP_PROVIDER_CONFIG": json.dumps(provider_config)}
        ):
            configs = get_provider_configurations(mock_tdp_client)

        assert len(configs) == 1
        assert configs[0].name == "Test Provider"
        assert configs[0].type == "snowflake"
        assert configs[0].fields == {"user": "test_user", "password": "test_pass"}

        # Should not call TDP client when using env var
        mock_tdp_client.get_container_data_app.assert_not_called()

    def test_env_var_override_with_empty_list(self, mock_tdp_client):
        """Test empty list from environment variable."""
        with patch.dict(os.environ, {"DATA_APP_PROVIDER_CONFIG": "[]"}):
            configs = get_provider_configurations(mock_tdp_client)

        assert configs == []

    def test_env_var_override_with_invalid_json(self, mock_tdp_client):
        """Test invalid JSON in environment variable raises error."""
        with patch.dict(os.environ, {"DATA_APP_PROVIDER_CONFIG": "invalid json"}):
            with pytest.raises(InvalidProviderConfigurationError):
                get_provider_configurations(mock_tdp_client)

    def test_env_var_override_with_invalid_config(self, mock_tdp_client):
        """Test invalid configuration in environment variable raises error."""
        invalid_config = [{"type": "snowflake"}]  # Missing required 'name' field

        with patch.dict(
            os.environ, {"DATA_APP_PROVIDER_CONFIG": json.dumps(invalid_config)}
        ):
            with pytest.raises(InvalidProviderConfigurationError):
                get_provider_configurations(mock_tdp_client)

    def test_tdp_integration_no_connector_id(self, mock_tdp_client):
        """Test TDP integration without CONNECTOR_ID returns empty list."""
        configs = get_provider_configurations(mock_tdp_client)
        assert configs == []

    def test_tdp_integration_with_connector_id(
        self, mock_tdp_client, mock_data_app, mock_provider_api_response
    ):
        """Test TDP integration with CONNECTOR_ID."""
        # Setup mocks
        mock_tdp_client.get_container_data_app.return_value = mock_data_app
        mock_tdp_client.get_provider.return_value = mock_provider_api_response

        # Setup environment variables for secrets
        env_vars = {
            "CONNECTOR_ID": "test-connector-id",
            "SNOWFLAKE_USER": "env_user",
            "SNOWFLAKE_PASSWORD": "env_password",
            "SNOWFLAKE_ACCOUNT": "env_account",
            "SNOWFLAKE_WAREHOUSE": "env_warehouse",
            "SNOWFLAKE_DATABASE": "env_database",
            "SNOWFLAKE_SCHEMA": "env_schema",
            "SNOWFLAKE_ROLE": "env_role",
        }

        with patch.dict(os.environ, env_vars):
            configs = get_provider_configurations(mock_tdp_client)

        assert len(configs) == 1
        config = configs[0]
        assert config.name == "Test Provider"
        assert config.type == "snowflake"
        assert config.fields["user"] == "env_user"
        assert config.fields["password"] == "env_password"

        # Verify TDP client calls
        mock_tdp_client.get_container_data_app.assert_called_once_with(
            "test-connector-id"
        )
        mock_tdp_client.get_provider.assert_called_once_with("test-provider-id")


class TestGetProviderSecretFromEnv:
    """Test get_provider_secret_from_env function."""

    def test_simple_secret_name(self):
        """Test simple secret name transformation."""
        with patch.dict(os.environ, {"SNOWFLAKE_USER": "test_user"}):
            value = get_provider_secret_from_env("snowflake.user")
            assert value == "test_user"

    def test_secret_name_with_hyphens(self):
        """Test secret name with hyphens gets converted to underscores."""
        with patch.dict(os.environ, {"SNOWFLAKE_CLIENT_ID": "test_client"}):
            value = get_provider_secret_from_env("snowflake.client-id")
            assert value == "test_client"

    def test_secret_name_with_spaces(self):
        """Test secret name with spaces gets converted to underscores."""
        with patch.dict(os.environ, {"SNOWFLAKE_SERVER_HOSTNAME": "test_server"}):
            value = get_provider_secret_from_env("snowflake.server hostname")
            assert value == "test_server"

    def test_secret_name_with_special_chars(self):
        """Test secret name with special characters gets cleaned."""
        with patch.dict(os.environ, {"SNOWFLAKE_TESTVALUE": "test_value"}):
            value = get_provider_secret_from_env("snowflake.test@value!")
            assert value == "test_value"

    def test_missing_secret_returns_empty_string(self):
        """Test missing secret returns empty string."""
        value = get_provider_secret_from_env("nonexistent.secret")
        assert value == ""

    def test_empty_secret_value(self):
        """Test empty secret value."""
        with patch.dict(os.environ, {"SNOWFLAKE_EMPTY": ""}):
            value = get_provider_secret_from_env("snowflake.empty")
            assert value == ""


class TestBuildSnowflakeProvider:
    """Test build_snowflake_provider function."""

    def test_valid_snowflake_config(self, sample_provider_config):
        """Test building Snowflake provider with valid config."""
        with patch("snowflake.connector.connect") as mock_connect:
            mock_connection = Mock()
            mock_connect.return_value = mock_connection

            provider = build_snowflake_provider(sample_provider_config)

            assert isinstance(provider, SnowflakeProvider)
            assert provider.connection == mock_connection

            # Verify connection was called with correct parameters
            mock_connect.assert_called_once_with(
                timezone="UTC",
                user="test_user",
                password="test_password",
                account="test_account",
                warehouse="TEST_WH",
                database="TEST_DB",
                schema="PUBLIC",
                role="TEST_ROLE",
            )

    def test_missing_required_field(self):
        """Test building Snowflake provider with missing required field."""
        config = ProviderConfiguration(
            name="Test Snowflake",
            type="snowflake",
            fields={
                "user": "test_user",
                # Missing password and other required fields
            },
        )

        with pytest.raises(InvalidProviderConfigurationError):
            build_snowflake_provider(config)

    def test_snowflake_connection_error(self, sample_provider_config):
        """Test Snowflake connection error handling."""
        import snowflake.connector.errors

        with patch("snowflake.connector.connect") as mock_connect:
            mock_connect.side_effect = snowflake.connector.errors.Error(
                "Connection failed"
            )

            with pytest.raises(ConnectionError):
                build_snowflake_provider(sample_provider_config)


class TestBuildDatabricksProvider:
    """Test build_databricks_provider function."""

    def test_valid_databricks_config(self, sample_databricks_config):
        """Test building Databricks provider with valid config."""
        with patch("databricks.sql.connect") as mock_connect:
            mock_connection = Mock()
            mock_connect.return_value = mock_connection

            provider = build_databricks_provider(sample_databricks_config)

            assert isinstance(provider, DatabricksProvider)
            assert provider.connection == mock_connection

    def test_missing_required_field_databricks(self):
        """Test building Databricks provider with missing required field."""
        config = ProviderConfiguration(
            name="Test Databricks",
            type="databricks",
            fields={
                "server_hostname": "test.databricks.com",
                # Missing other required fields
            },
        )

        with pytest.raises(InvalidProviderConfigurationError):
            build_databricks_provider(config)


class TestBuildProvider:
    """Test build_provider factory function."""

    def test_build_snowflake_provider(self, sample_provider_config):
        """Test building Snowflake provider through factory."""
        with patch(
            "tetrascience.data_app_providers.provider.build_snowflake_provider"
        ) as mock_build:
            mock_provider = Mock()
            mock_build.return_value = mock_provider

            result = build_provider(sample_provider_config)

            assert result == mock_provider
            mock_build.assert_called_once_with(sample_provider_config)

    def test_build_databricks_provider(self, sample_databricks_config):
        """Test building Databricks provider through factory."""
        with patch(
            "tetrascience.data_app_providers.provider.build_databricks_provider"
        ) as mock_build:
            mock_provider = Mock()
            mock_build.return_value = mock_provider

            result = build_provider(sample_databricks_config)

            assert result == mock_provider
            mock_build.assert_called_once_with(sample_databricks_config)

    def test_build_athena_provider(self, sample_athena_config):
        """Test building Athena provider through factory."""
        with patch(
            "tetrascience.data_app_providers.provider.get_tdp_athena_provider"
        ) as mock_get:
            mock_provider = Mock()
            mock_get.return_value = mock_provider

            result = build_provider(sample_athena_config)

            assert result == mock_provider
            mock_get.assert_called_once()

    def test_unsupported_provider_type(self):
        """Test building provider with unsupported type."""
        config = ProviderConfiguration(
            name="Unsupported Provider", type="unsupported", fields={}
        )

        with pytest.raises(
            InvalidProviderConfigurationError,
            match="Unsupported provider type: unsupported",
        ):
            build_provider(config)
