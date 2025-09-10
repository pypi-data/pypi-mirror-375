"""Tests for tdp_client module."""

import os
import pytest
from unittest.mock import Mock, patch, MagicMock
import requests

from tetrascience.data_app_providers.tdp_client import (
    TetraScienceClient,
    TdpRelease,
    SqlConnectionInfo,
    MinimalProvider,
    DataApp,
    ContainerDataApp,
    ProviderApiResponse,
    ProviderSecret,
    OrganizationApiResponse,
)


class TestTetraScienceClient:
    """Test TetraScienceClient class."""

    def test_client_initialization_with_params(self):
        """Test client initialization with explicit parameters."""
        client = TetraScienceClient(
            token="test-token", x_org_slug="test-org", base_url="https://api.test.com"
        )

        assert client.token == "test-token"
        assert client.x_org_slug == "test-org"
        assert client.base_url == "https://api.test.com"

    def test_client_initialization_from_env(self):
        """Test client initialization with environment variable values."""
        # Test that the client accepts environment variable values as constructor parameters
        client = TetraScienceClient(
            token="env-token", x_org_slug="env-org", base_url="https://env.api.com"
        )
        assert client.token == "env-token"
        assert client.x_org_slug == "env-org"
        assert client.base_url == "https://env.api.com"

    def test_client_initialization_tdp_internal_endpoint(self):
        """Test client initialization with internal endpoint."""
        # Test that the client accepts internal endpoint as constructor parameter
        client = TetraScienceClient(
            token="env-token", x_org_slug="env-org", base_url="https://internal.api.com"
        )
        assert client.base_url == "https://internal.api.com"

    def test_client_initialization_empty_values(self):
        """Test client initialization with empty values."""
        client = TetraScienceClient()

        assert client.token == ""
        assert client.x_org_slug == ""
        assert client.base_url == ""

    def test_retrieve_url_property(self):
        """Test retrieve_url property."""
        client = TetraScienceClient(base_url="https://api.test.com")
        assert client.retrieve_url == "https://api.test.com/v1/datalake/retrieve"

    def test_release_url_property(self):
        """Test release_url property."""
        client = TetraScienceClient(base_url="https://api.test.com")
        assert client.release_url == "https://api.test.com/release"

    def test_sql_connection_info_url_property(self):
        """Test sql_connection_info_url property."""
        client = TetraScienceClient(base_url="https://api.test.com")
        expected = "https://api.test.com/v1/datalake/sqlConnectionInfo"
        assert client.sql_connection_info_url == expected

    def test_organization_by_slug_url_property(self):
        """Test organization_by_slug_url property."""
        client = TetraScienceClient(
            base_url="https://api.test.com", x_org_slug="test-org"
        )
        expected = "https://api.test.com/v1/userorg/organizationsBySlug/test-org"
        assert client.organization_by_slug_url == expected

    def test_provider_url_method(self):
        """Test provider_url method."""
        client = TetraScienceClient(base_url="https://api.test.com")
        url = client.provider_url("test-provider-id")
        expected = "https://api.test.com/v1/dataapps/providers/test-provider-id"
        assert url == expected

    def test_data_app_url_method(self):
        """Test data_app_url method."""
        client = TetraScienceClient(base_url="https://api.test.com")
        url = client.data_app_url("test-app-id")
        expected = "https://api.test.com/v1/dataapps/apps/test-app-id"
        assert url == expected

    @patch("requests.get")
    def test_ids_file_success(self, mock_get):
        """Test successful IDS file retrieval."""
        mock_response = Mock()
        mock_response.content = b"file content"
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        client = TetraScienceClient(
            token="test-token", x_org_slug="test-org", base_url="https://api.test.com"
        )

        content = client.ids_file("test-file-id")

        assert content == b"file content"
        mock_get.assert_called_once_with(
            url="https://api.test.com/v1/datalake/retrieve",
            params={"fileId": "test-file-id"},
            headers={
                "ts-auth-token": "test-token",
                "x-org-slug": "test-org",
                "User-Agent": "tetrascience-data-app",
            },
            verify=False,
            timeout=30,
        )

    @patch("requests.get")
    def test_ids_file_http_error(self, mock_get):
        """Test IDS file retrieval with HTTP error."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
        mock_response.text = "File not found"
        mock_get.return_value = mock_response

        client = TetraScienceClient(
            token="test-token", x_org_slug="test-org", base_url="https://api.test.com"
        )

        with pytest.raises(requests.HTTPError):
            client.ids_file("nonexistent-file-id")

    @patch("requests.get")
    def test_get_organization_success(self, mock_get):
        """Test successful organization retrieval."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": "org-id",
            "orgSlug": "test-org",
            "name": "Test Organization",
            "emailDomain": "test.com",
            "authType": "basic",
            "features": {},
            "tenantId": "test-tenant-id",
            "createdAt": "2025-01-01T00:00:00Z",
            "createdBy": "test-user",
            "subdomain": "test-subdomain",
            "ssoEnabledOnTenant": False,
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        client = TetraScienceClient(
            token="test-token", x_org_slug="test-org", base_url="https://api.test.com"
        )

        org = client.get_organization()

        assert isinstance(org, OrganizationApiResponse)
        assert org.id == "org-id"
        assert org.orgSlug == "test-org"

    @patch("requests.get")
    def test_get_provider_success(self, mock_get):
        """Test successful provider retrieval."""
        # Mock organization call
        org_response = Mock()
        org_response.json.return_value = {
            "id": "org-id",
            "orgSlug": "test-org",
            "name": "Test Org",
            "emailDomain": "test.com",
            "authType": "basic",
            "features": {},
            "tenantId": "test-tenant-id",
            "createdAt": "2025-01-01T00:00:00Z",
            "createdBy": "test-user",
            "subdomain": "test-subdomain",
            "ssoEnabledOnTenant": False,
        }
        org_response.raise_for_status.return_value = None

        # Mock provider call
        provider_response = Mock()
        provider_response.json.return_value = {
            "id": "provider-id",
            "orgSlug": "test-org",
            "name": "Test Provider",
            "type": "snowflake",
            "iconUrl": "https://example.com/icon.png",
            "createdAt": "2025-01-01T00:00:00Z",
            "updatedAt": "2025-01-01T00:00:00Z",
            "createdBy": "user-id",
            "updatedBy": "user-id",
            "dataAppCount": "0",
            "secrets": [
                {
                    "name": "snowflake.user",
                    "value": "",
                    "type": "string",
                    "required": True,
                },
                {
                    "name": "snowflake.password",
                    "value": "",
                    "type": "string",
                    "required": True,
                },
            ],
        }
        provider_response.raise_for_status.return_value = None

        mock_get.side_effect = [org_response, provider_response]

        client = TetraScienceClient(
            token="test-token", x_org_slug="test-org", base_url="https://api.test.com"
        )

        provider = client.get_provider("provider-id")

        assert isinstance(provider, ProviderApiResponse)
        assert provider.id == "provider-id"
        assert provider.name == "Test Provider"
        assert len(provider.secrets) == 2

    @patch("requests.get")
    def test_get_container_data_app_success(self, mock_get):
        """Test successful container data app retrieval."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": "app-id",
            "orgSlug": "test-org",
            "connectorId": "connector-id",
            "serviceNamespace": "data-apps",
            "serviceDiscoveryName": "data-app-connector-id",
            "createdAt": "2025-01-01T00:00:00Z",
            "createdBy": "user-id",
            "port": "80",
            "config": {},
            "providers": [
                {
                    "id": "provider-id",
                    "orgSlug": "test-org",
                    "name": "Test Provider",
                    "type": "snowflake",
                    "iconUrl": "https://example.com/icon.png",
                    "createdAt": "2025-01-01T00:00:00Z",
                    "createdBy": "user-id",
                }
            ],
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        client = TetraScienceClient(
            token="test-token", x_org_slug="test-org", base_url="https://api.test.com"
        )

        app = client.get_container_data_app("connector-id")

        assert isinstance(app, ContainerDataApp)
        assert app.id == "app-id"
        assert app.connectorId == "connector-id"
        assert len(app.providers) == 1


class TestTdpModels:
    """Test TDP API response models."""

    def test_tdp_release_model(self):
        """Test TdpRelease model."""
        release = TdpRelease(platformVersion="1.0.0")
        assert release.platformVersion == "1.0.0"

    def test_sql_connection_info_model(self):
        """Test SqlConnectionInfo model."""
        info = SqlConnectionInfo(
            url="jdbc:awsathena://AwsRegion=us-east-2;WorkGroup=tetrascience",
            outputLocation="s3://bucket/path/",
        )
        assert "jdbc:awsathena" in info.url
        assert info.outputLocation == "s3://bucket/path/"

    def test_minimal_provider_model(self):
        """Test MinimalProvider model."""
        provider = MinimalProvider(
            id="provider-id",
            orgSlug="test-org",
            name="Test Provider",
            type="snowflake",
            iconUrl="https://example.com/icon.png",
            createdAt="2025-01-01T00:00:00Z",
            createdBy="user-id",
        )
        assert provider.id == "provider-id"
        assert provider.type == "snowflake"
        assert provider.updatedAt is None
        assert provider.updatedBy is None

    def test_provider_secret_model(self):
        """Test ProviderSecret model."""
        secret = ProviderSecret(
            name="snowflake.user", value="", type="string", required=True
        )
        assert secret.name == "snowflake.user"
        assert secret.value == ""
        assert secret.type == "string"
        assert secret.required == True
