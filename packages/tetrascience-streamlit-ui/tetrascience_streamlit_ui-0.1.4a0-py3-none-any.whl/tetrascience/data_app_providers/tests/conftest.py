"""Pytest configuration and fixtures for data app providers tests."""

import os
import pytest
from unittest.mock import Mock, MagicMock
from tetrascience.data_app_providers.provider_typing import ProviderConfiguration
from tetrascience.data_app_providers.tdp_client import (
    TetraScienceClient,
    ProviderApiResponse,
    ProviderSecret,
    DataApp,
    MinimalProvider,
)


@pytest.fixture
def clean_environment():
    """Clean environment variables for tests that need isolation."""
    saved_environ = os.environ.copy()
    # Clear provider-related environment variables
    env_vars_to_clear = [
        "DATA_APP_PROVIDER_CONFIG",
        "CONNECTOR_ID",
    ]

    for var in env_vars_to_clear:
        if var in os.environ:
            del os.environ[var]

    # Clear any provider secret environment variables
    for key in list(os.environ.keys()):
        if key.startswith(("SNOWFLAKE_", "DATABRICKS_", "ATHENA_")):
            del os.environ[key]

    yield

    # Restore original environment
    os.environ.clear()
    os.environ.update(saved_environ)


@pytest.fixture
def mock_tdp_client():
    """Create a mock TetraScienceClient."""
    client = Mock(spec=TetraScienceClient)
    return client


@pytest.fixture
def sample_provider_config():
    """Sample provider configuration for testing."""
    return ProviderConfiguration(
        name="Test Snowflake",
        type="snowflake",
        iconUrl="https://example.com/snowflake.png",
        fields={
            "user": "test_user",
            "password": "test_password",
            "account": "test_account",
            "warehouse": "TEST_WH",
            "database": "TEST_DB",
            "schema": "PUBLIC",
            "role": "TEST_ROLE",
        },
    )


@pytest.fixture
def sample_databricks_config():
    """Sample Databricks provider configuration for testing."""
    return ProviderConfiguration(
        name="Test Databricks",
        type="databricks",
        iconUrl="https://example.com/databricks.png",
        fields={
            "server_hostname": "test.databricks.com",
            "http_path": "/sql/1.0/warehouses/test",
            "client_id": "test_client_id",
            "client_secret": "test_client_secret",
            "catalog": "test_catalog",
            "schema": "default",
        },
    )


@pytest.fixture
def sample_athena_config():
    """Sample Athena provider configuration for testing."""
    return ProviderConfiguration(
        name="Test Athena",
        type="athena",
        iconUrl="https://example.com/athena.png",
        fields={},  # Athena uses AWS credentials from environment
    )


@pytest.fixture
def mock_provider_api_response():
    """Mock provider API response from TDP."""
    return ProviderApiResponse(
        id="test-provider-id",
        orgSlug="test-org",
        name="Test Provider",
        type="snowflake",
        iconUrl="https://example.com/icon.png",
        createdAt="2025-01-01T00:00:00Z",
        updatedAt="2025-01-01T00:00:00Z",
        createdBy="test-user",
        updatedBy="test-user",
        dataAppCount="0",
        secrets=[
            ProviderSecret(
                name="snowflake.user", value="", type="string", required=True
            ),
            ProviderSecret(
                name="snowflake.password", value="", type="string", required=True
            ),
            ProviderSecret(
                name="snowflake.account", value="", type="string", required=True
            ),
            ProviderSecret(
                name="snowflake.warehouse", value="", type="string", required=True
            ),
            ProviderSecret(
                name="snowflake.database", value="", type="string", required=True
            ),
            ProviderSecret(
                name="snowflake.schema", value="", type="string", required=True
            ),
            ProviderSecret(
                name="snowflake.role", value="", type="string", required=True
            ),
        ],
    )


@pytest.fixture
def mock_data_app():
    """Mock data app response from TDP."""
    return DataApp(
        id="test-app-id",
        connectorId="test-connector-id",
        name="Test Data App",
        description="Test description",
        url="",
        iconUrl="",
        type="CONTAINER",
        providers=[
            MinimalProvider(
                id="test-provider-id",
                orgSlug="test-org",
                name="Test Provider",
                type="snowflake",
                iconUrl="https://example.com/icon.png",
                createdAt="2025-01-01T00:00:00Z",
                createdBy="test-user",
            )
        ],
        slug="test-app",
        version="v1.0.0",
        artifactLabels=[],
    )
