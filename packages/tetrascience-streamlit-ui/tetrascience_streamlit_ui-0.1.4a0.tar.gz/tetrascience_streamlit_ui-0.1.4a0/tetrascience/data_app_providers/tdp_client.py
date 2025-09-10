import logging
import os
from functools import partial
from typing import Any

import requests
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)
SSL_VERIFY = False
API_TIMEOUT = 30  # seconds


class TdpRelease(BaseModel):
    """Model for TDP release API response"""

    platformVersion: str


class SqlConnectionInfo(BaseModel):
    """
    Model for TDP SQL connection info API response

    Example response:
    ```
    {
        "url": "jdbc:awsathena://AwsRegion=us-east-2;WorkGroup=tetrascience",
        "outputLocation": "s3://ts-platform-dev-athena-results/tetrascience/"
    }
    ```
    """

    url: str
    outputLocation: str


class MinimalProvider(BaseModel):
    """
    Model for minimal provider as returned by the /dataapps/apps/{appId} endpoint
    Example:
    ```
    {
        "id": "94eef079-6604-41bc-ab39-03246d3f7c4d",
        "orgSlug": "rm",
        "name": "John Snow",
        "type": "snowflake",
        "iconUrl": "https://tdp-data-app-provider-templates.s3.amazonaws.com/development/icons/snowflake.png",
        "createdAt": "2025-03-28T14:25:44.050Z",
        "updatedAt": "2025-03-28T14:25:44.050Z",
        "createdBy": "59eb8bd4-8b10-43b3-ac57-fe3ab86c05fd",
        "updatedBy": "59eb8bd4-8b10-43b3-ac57-fe3ab86c05fd"
    }
    ```
    """

    id: str
    orgSlug: str
    name: str
    type: str
    iconUrl: str
    createdAt: str
    updatedAt: str | None = Field(None)
    createdBy: str
    updatedBy: str | None = Field(None)


class DataApp(BaseModel):
    """
    Model for Data App API response
    Example response:
    ```
    {
    "id": "dfcc6ad8-c553-4791-8f7b-073cd7257a5c",
    "connectorId": "b81541df-fc3f-4b30-bdff-ee9797c90c34",
    "name": "",
    "description": "A Streamlit-powered dashboard to visualize chromatography insights",
    "url": "",
    "iconUrl": "",
    "type": "CONTAINER",
    "providers": [
        {
        "id": "94eef079-6604-41bc-ab39-03246d3f7c4d",
        "orgSlug": "rm",
        "name": "John Snow",
        "type": "snowflake",
        "iconUrl": "https://tdp-data-app-provider-templates.s3.amazonaws.com/development/icons/snowflake.png",
        "createdAt": "2025-03-28T14:25:44.050Z",
        "updatedAt": "2025-03-28T14:25:44.050Z",
        "createdBy": "59eb8bd4-8b10-43b3-ac57-fe3ab86c05fd",
        "updatedBy": "59eb8bd4-8b10-43b3-ac57-fe3ab86c05fd"
        }
    ],
    "slug": "chromatography-insights",
    "version": "v1.4.0",
    "artifactLabels": [
        {
        "name": "subtype",
        "value": "data-app"
        }
    ]
    }
    ```
    """

    id: str
    connectorId: str
    name: str
    description: str
    url: str
    iconUrl: str
    type: str
    providers: list[MinimalProvider] = Field(default_factory=list)
    slug: str
    version: str
    artifactLabels: list[dict[str, Any]] = Field(default_factory=list)


class ContainerDataApp(BaseModel):
    """

    Example:
    {
    "id": "dfcc6ad8-c553-4791-8f7b-073cd7257a5c",
    "orgSlug": "rm",
    "connectorId": "b81541df-fc3f-4b30-bdff-ee9797c90c34",
    "serviceNamespace": "data-apps",
    "serviceDiscoveryName": "data-app-b81541df-fc3f-4b30-bdff-ee9797c90c34",
    "createdAt": "2025-03-28T14:25:59.684Z",
    "updatedAt": "2025-03-28T14:25:59.684Z",
    "createdBy": "59eb8bd4-8b10-43b3-ac57-fe3ab86c05fd",
    "updatedBy": "59eb8bd4-8b10-43b3-ac57-fe3ab86c05fd",
    "port": "80",
    "config": {},
    "providers": [
        {
        "id": "94eef079-6604-41bc-ab39-03246d3f7c4d",
        "orgSlug": "rm",
        "name": "John Snow",
        "type": "snowflake",
        "iconUrl": "https://tdp-data-app-provider-templates.s3.amazonaws.com/development/icons/snowflake.png",
        "createdAt": "2025-03-28T14:25:44.050Z",
        "updatedAt": "2025-03-28T14:25:44.050Z",
        "createdBy": "59eb8bd4-8b10-43b3-ac57-fe3ab86c05fd",
        "updatedBy": "59eb8bd4-8b10-43b3-ac57-fe3ab86c05fd"
        }
    ]
    }
    """

    id: str
    orgSlug: str
    connectorId: str
    serviceNamespace: str
    serviceDiscoveryName: str
    createdAt: str
    updatedAt: str | None = Field(None)
    createdBy: str
    updatedBy: str | None = Field(None)
    port: str
    config: dict[str, Any] = Field(default_factory=dict)
    providers: list[MinimalProvider] = Field(default_factory=list)


class ProviderSecret(BaseModel):
    name: str
    value: str | None = Field(None)
    type: str
    required: bool


class ProviderApiResponse(BaseModel):
    """

    Example response:

    ```
    {
      "id": "3757bbca-2f2e-4346-98d4-507473e0f298",
      "orgSlug": "simplo-dev",
      "name": "Test",
      "type": "snowflake",
      "iconUrl": "https://tdp-data-app-provider-templates.s3.amazonaws.com/production/icons/snowflake.png",
      "createdAt": "2024-11-12T20:17:37.340Z",
      "updatedAt": "2024-11-12T20:17:37.340Z",
      "createdBy": "59eb8bd4-8b10-43b3-ac57-fe3ab86c05fd",
      "updatedBy": "59eb8bd4-8b10-43b3-ac57-fe3ab86c05fd",
      "dataAppCount": "0",
      "secrets": [
        {
          "name": "test.password",
          "value": "AQICAHih2+Mvp357qAgE0KwQ5hl7CLxxy4+tyoWsje...",
          "type": "text",
          "required": true
        },
        {
          "name": "test.user",
          "value": "AQICAHih2+Mvp3zv+ou5nHASyXSbyltZ3wittIYMzg...",
          "type": "text",
          "required": true
        }
      ]
    }
    ```

    """

    id: str
    orgSlug: str
    name: str
    type: str
    iconUrl: str
    createdAt: str
    updatedAt: str | None = Field(None)
    createdBy: str
    updatedBy: str | None = Field(None)
    dataAppCount: str
    secrets: list[ProviderSecret] = Field(default_factory=list)


class OrganizationApiResponse(BaseModel):
    """
    Example response:
    {
        "id": "0b7dbda6-4c0f-4eea-a6af-03e52d437ea3",
        "orgSlug": "simplo-dev",
        "name": "SIMPLO Dev",
        "emailDomain": "tetrascience.com",
        "authType": "basic",
        "features": {
            "auditTrail": {
                "enabled": true
            },
            "ssoGroupMapping": {
                "admin": [
                    "tdp-tetra-uat-simplo"
                ],
                "member": [],
                "readonly": [],
                "developer": []
            },
            "continuousVerification": {
                "enabled": false
            }
        },
        "tenantId": "78494c55-dbb9-46cb-a241-f0190bbda53a",
        "createdAt": "2023-08-09T20:08:28.807Z",
        "createdBy": "59eb8bd4-8b10-43b3-ac57-fe3ab86c05fd",
        "modifiedAt": "2024-03-07T20:07:30.185Z",
        "modifiedBy": "59eb8bd4-8b10-43b3-ac57-fe3ab86c05fd",
        "subdomain": "tetrascience-sso",
        "ssoEnabledOnTenant": true
    }
    """

    id: str
    orgSlug: str
    name: str
    emailDomain: str
    authType: str
    features: dict[str, Any]
    tenantId: str
    createdAt: str
    createdBy: str
    modifiedAt: str | None = Field(None)
    modifiedBy: str | None = Field(None)
    subdomain: str
    ssoEnabledOnTenant: bool


class TetraScienceClient:
    """Client for interacting with TetraScience Data Platform API."""

    def __init__(
        self,
        token: str = os.getenv("TS_AUTH_TOKEN", ""),
        x_org_slug: str = os.getenv("ORG_SLUG", ""),
        base_url: str = os.getenv("TDP_INTERNAL_ENDPOINT")
        or os.getenv("TDP_ENDPOINT", ""),
    ):
        self.token = token
        self.base_url = base_url
        self.x_org_slug = x_org_slug

        if not self.token:
            logger.warning("No TDP API token provided.")
        if not self.base_url:
            logger.warning("No TDP API base URL provided.")
        if not self.x_org_slug:
            logger.warning("No TDP API org-slug provided.")

    @property
    def retrieve_url(self) -> str:
        return f"{self.base_url}/v1/datalake/retrieve"

    @property
    def release_url(self) -> str:
        return f"{self.base_url}/release"

    @property
    def sql_connection_info_url(self) -> str:
        return f"{self.base_url}/v1/datalake/sqlConnectionInfo"

    def data_app_url(self, data_app_id) -> str:
        return f"{self.base_url}/v1/dataapps/apps/{data_app_id}"

    def container_app_url(self, connector_id: str) -> str:
        return f"{self.base_url}/v1/dataapps/apps/container/{connector_id}"

    def provider_url(self, provider_id: str) -> str:
        return f"{self.base_url}/v1/dataapps/providers/{provider_id}"

    @property
    def organization_by_slug_url(self) -> str:
        return f"{self.base_url}/v1/userorg/organizationsBySlug/{self.x_org_slug}"

    @property
    def _get(self):
        """Get method with headers and timeout set."""
        return partial(
            requests.get,
            headers={
                "ts-auth-token": self.token,
                "x-org-slug": self.x_org_slug,
                "User-Agent": "tetrascience-data-app",
            },
            verify=SSL_VERIFY,
            timeout=API_TIMEOUT,
        )

    def ids_file(self, file_id: str):
        """
        Retrieve the IDS file.

        NOTE: Each IDS file can each take up ~100MB in cache.  When changing cache settings, be aware of the
            possible memory footprint of storing many files.  If the cache memory exceeds the container's
            memory, the app will crash.
        """
        logger.debug(
            f"Getting IDS file {file_id} from {self.retrieve_url}, org: {self.x_org_slug}"
        )

        r = self._get(url=self.retrieve_url, params={"fileId": file_id})
        try:
            r.raise_for_status()
        except requests.HTTPError:
            logger.error(f"Failed to get IDS file {file_id}. Response: {r.text}")
            raise

        return r.content

    def get_tdp_release(self) -> str:
        """Get the TDP release version."""
        logger.debug(f"Getting TDP release from {self.release_url}")

        r = self._get(self.release_url)
        try:
            r.raise_for_status()
        except requests.HTTPError:
            logger.error(f"Failed to get TDP release. Response: {r.text}")
            raise

        parsed_response = TdpRelease.model_validate(r.json())

        return parsed_response.platformVersion

    def get_sql_connection_info(self) -> SqlConnectionInfo:
        """Get the TDP SQL connection info."""
        logger.debug(
            f"Getting TDP SQL connection info from {self.sql_connection_info_url}"
        )

        r = self._get(self.sql_connection_info_url)
        try:
            r.raise_for_status()
        except requests.HTTPError:
            logger.error(f"Failed to get SQL connection info. Response: {r.text}")
            raise

        parsed_response = SqlConnectionInfo.model_validate(r.json())

        return parsed_response

    def get_athena_workgroup(self) -> str | None:
        """
        Get the Athena workgroup from the SQL connection info.

        return: Workgroup name or None if not found
        """
        sql_connection_info = self.get_sql_connection_info()

        # Extract workgroup from the URL
        # Example URL: "jdbc:awsathena://AwsRegion=us-east-2;WorkGroup=tetrascience"
        params = sql_connection_info.url.split("://", 1)[-1].split(";")

        for param in params:
            if param.startswith("WorkGroup="):
                return param.split("=", 1)[-1]

        logger.warning(
            f"Athena workgroup not found in SQL connection info: {sql_connection_info}"
        )
        return None

    def get_data_app(self, app_id: str) -> DataApp:
        """Get Data App by id."""
        logger.debug(f"Getting Data App {app_id} from {self.data_app_url(app_id)}")

        r = self._get(self.data_app_url(app_id))
        try:
            r.raise_for_status()
        except requests.HTTPError:
            logger.error(f"Failed to get Data App {app_id}. Response: {r.text}")
            raise

        parsed_response = DataApp.model_validate(r.json())

        return parsed_response

    def get_container_data_app(self, connector_id: str) -> ContainerDataApp:
        """Get Container Data App by connector id."""
        logger.debug(
            f"Getting Container Data App {connector_id} from {self.container_app_url(connector_id)}"
        )

        r = self._get(self.container_app_url(connector_id))
        try:
            r.raise_for_status()
        except requests.HTTPError:
            logger.error(
                f"Failed to get Container Data App {connector_id}. Response: {r.text}"
            )
            raise

        logger.debug(f"Response: {r.text}")
        parsed_response = ContainerDataApp.model_validate(r.json())

        return parsed_response

    def get_organization(self) -> OrganizationApiResponse:
        """
        Get current organization info.
        """
        logger.debug(
            f"Getting organization {self.x_org_slug} from {self.organization_by_slug_url}"
        )

        r = self._get(self.organization_by_slug_url)
        try:
            r.raise_for_status()
        except requests.HTTPError:
            logger.error(
                f"Failed to get organization {self.x_org_slug}. Response: {r.text}"
            )
            raise

        parsed_response = OrganizationApiResponse.model_validate(r.json())

        return parsed_response

    def get_provider(self, provider_id: str) -> ProviderApiResponse:
        """Get provider by id."""
        logger.debug(
            f"Getting provider {provider_id} from {self.provider_url(provider_id)}"
        )

        org_info = self.get_organization()

        r = self._get(self.provider_url(provider_id), params={"orgId": org_info.id})
        try:
            r.raise_for_status()
        except requests.HTTPError:
            logger.error(f"Failed to get provider {provider_id}. Response: {r.text}")
            raise

        parsed_response = ProviderApiResponse.model_validate(r.json())

        return parsed_response
