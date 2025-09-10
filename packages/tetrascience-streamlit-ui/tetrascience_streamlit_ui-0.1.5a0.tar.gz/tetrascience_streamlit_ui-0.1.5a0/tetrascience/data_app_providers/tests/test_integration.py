"""Integration tests for data app providers."""

import os
import json
import pytest
from unittest.mock import Mock, patch
import polars as pl
import pyarrow as pa

from tetrascience.data_app_providers import (
    get_provider_configurations,
    build_provider,
    TetraScienceClient,
    ProviderConfiguration,
)


class TestEndToEndWorkflow:
    """Test end-to-end workflow from configuration to querying."""

    def test_environment_variable_workflow(self):
        """Test complete workflow using environment variable configuration."""
        # Setup provider configuration
        provider_config = [
            {
                "name": "Test Snowflake",
                "type": "snowflake",
                "iconUrl": "https://example.com/snowflake.png",
                "fields": {
                    "user": "test_user",
                    "password": "test_password",
                    "account": "test_account",
                    "warehouse": "TEST_WH",
                    "database": "TEST_DB",
                    "schema": "PUBLIC",
                    "role": "TEST_ROLE",
                },
            }
        ]

        # Mock Snowflake connection and query
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor

        mock_table = pa.table({"column1": ["test_value"], "column2": [123]})
        mock_cursor.fetch_arrow_all.return_value = mock_table

        env_vars = {"DATA_APP_PROVIDER_CONFIG": json.dumps(provider_config)}

        with patch.dict(os.environ, env_vars):
            with patch("snowflake.connector.connect", return_value=mock_connection):
                client = TetraScienceClient()
                configs = get_provider_configurations(client)

                assert len(configs) == 1
                assert configs[0].name == "Test Snowflake"

                provider = build_provider(configs[0])

                with patch("polars.from_arrow") as mock_from_arrow:
                    mock_df = Mock(spec=pl.DataFrame)
                    mock_from_arrow.return_value = mock_df

                    result = provider.query("SELECT * FROM test_table", {})

                    assert result == mock_df
                    mock_cursor.execute.assert_called_once_with(
                        "SELECT * FROM test_table", {}
                    )

    def test_tdp_integration_workflow(self):
        """Test complete workflow using TDP integration."""
        # Setup TDP client mocks
        mock_client = Mock(spec=TetraScienceClient)

        # Mock data app response
        mock_data_app = Mock()
        mock_provider = Mock()
        mock_provider.id = "test-provider-id"
        mock_data_app.providers = [mock_provider]
        mock_client.get_container_data_app.return_value = mock_data_app

        # Mock provider response
        mock_provider_response = Mock()
        mock_provider_response.name = "TDP Snowflake"
        mock_provider_response.type = "snowflake"
        mock_provider_response.iconUrl = "https://example.com/icon.png"

        mock_secret = Mock()
        mock_secret.name = "snowflake.user"
        mock_provider_response.secrets = [mock_secret]
        mock_client.get_provider.return_value = mock_provider_response

        # Setup environment variables
        env_vars = {
            "CONNECTOR_ID": "test-connector-id",
            "SNOWFLAKE_USER": "tdp_user",
        }

        # Mock Snowflake connection
        mock_connection = Mock()

        with patch.dict(os.environ, env_vars):
            with patch("snowflake.connector.connect", return_value=mock_connection):
                configs = get_provider_configurations(mock_client)

                assert len(configs) == 1
                assert configs[0].name == "TDP Snowflake"
                assert configs[0].fields["user"] == "tdp_user"

                mock_client.get_container_data_app.assert_called_once_with(
                    "test-connector-id"
                )
                mock_client.get_provider.assert_called_once_with("test-provider-id")

    def test_multiple_providers_workflow(self):
        """Test workflow with multiple provider types."""
        provider_configs = [
            {
                "name": "Test Snowflake",
                "type": "snowflake",
                "fields": {
                    "user": "sf_user",
                    "password": "sf_pass",
                    "account": "sf_account",
                    "warehouse": "SF_WH",
                    "database": "SF_DB",
                    "schema": "PUBLIC",
                    "role": "SF_ROLE",
                },
            },
            {
                "name": "Test Databricks",
                "type": "databricks",
                "fields": {
                    "server_hostname": "test.databricks.com",
                    "http_path": "/sql/1.0/warehouses/test",
                    "client_id": "db_client_id",
                    "client_secret": "db_client_secret",
                    "catalog": "db_catalog",
                    "schema": "default",
                },
            },
            {"name": "Test Athena", "type": "athena", "fields": {}},
        ]

        env_vars = {"DATA_APP_PROVIDER_CONFIG": json.dumps(provider_configs)}

        with patch.dict(os.environ, env_vars):
            with patch("snowflake.connector.connect") as mock_sf_connect:
                with patch("databricks.sql.connect") as mock_db_connect:
                    with patch(
                        "tetrascience.data_app_providers.provider.get_tdp_athena_provider"
                    ) as mock_athena:
                        mock_sf_connect.return_value = Mock()
                        mock_db_connect.return_value = Mock()
                        mock_athena.return_value = Mock()

                        # Get configurations
                        client = TetraScienceClient()
                        configs = get_provider_configurations(client)

                        assert len(configs) == 3

                        # Build all providers
                        providers = []
                        for config in configs:
                            provider = build_provider(config)
                            providers.append(provider)

                        assert len(providers) == 3

                        # Verify all provider types were created
                        mock_sf_connect.assert_called_once()
                        mock_db_connect.assert_called_once()
                        mock_athena.assert_called_once()

    def test_error_handling_workflow(self):
        """Test error handling in the complete workflow."""
        # Test invalid configuration
        invalid_config = [{"name": "Invalid", "type": "snowflake"}]  # Missing fields

        env_vars = {"DATA_APP_PROVIDER_CONFIG": json.dumps(invalid_config)}

        with patch.dict(os.environ, env_vars):
            client = TetraScienceClient()

            with pytest.raises(
                Exception
            ):  # Should raise InvalidProviderConfigurationError
                get_provider_configurations(client)

    def test_provider_query_error_handling(self):
        """Test error handling during provider queries."""
        provider_config = [
            {
                "name": "Test Snowflake",
                "type": "snowflake",
                "fields": {
                    "user": "test_user",
                    "password": "test_password",
                    "account": "test_account",
                    "warehouse": "TEST_WH",
                    "database": "TEST_DB",
                    "schema": "PUBLIC",
                    "role": "TEST_ROLE",
                },
            }
        ]

        # Mock Snowflake connection that raises error on query
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("Query failed")

        env_vars = {"DATA_APP_PROVIDER_CONFIG": json.dumps(provider_config)}

        with patch.dict(os.environ, env_vars):
            with patch("snowflake.connector.connect", return_value=mock_connection):
                client = TetraScienceClient()
                configs = get_provider_configurations(client)
                provider = build_provider(configs[0])

                with pytest.raises(Exception):  # Should raise QueryError
                    provider.query("SELECT * FROM test_table", {})

    def test_configuration_validation_workflow(self):
        """Test configuration validation in the workflow."""
        # Test with valid configuration
        valid_config = [
            {
                "name": "Valid Provider",
                "type": "snowflake",
                "iconUrl": "https://example.com/icon.png",
                "fields": {
                    "user": "test_user",
                    "password": "test_password",
                    "account": "test_account",
                    "warehouse": "TEST_WH",
                    "database": "TEST_DB",
                    "schema": "PUBLIC",
                    "role": "TEST_ROLE",
                },
            }
        ]

        env_vars = {"DATA_APP_PROVIDER_CONFIG": json.dumps(valid_config)}

        with patch.dict(os.environ, env_vars):
            client = TetraScienceClient()
            configs = get_provider_configurations(client)

            assert len(configs) == 1
            config = configs[0]

            # Validate configuration structure
            assert isinstance(config, ProviderConfiguration)
            assert config.name == "Valid Provider"
            assert config.type == "snowflake"
            assert config.iconUrl == "https://example.com/icon.png"
            assert isinstance(config.fields, dict)
            assert len(config.fields) == 7

    def test_empty_configuration_workflow(self):
        """Test workflow with empty configuration."""
        env_vars = {"DATA_APP_PROVIDER_CONFIG": "[]"}

        with patch.dict(os.environ, env_vars):
            client = TetraScienceClient()
            configs = get_provider_configurations(client)

            assert configs == []

    def test_no_configuration_workflow(self):
        """Test workflow with no configuration available."""
        # No environment variables set
        client = TetraScienceClient()
        configs = get_provider_configurations(client)

        assert configs == []
