import os
import re
import logging
from typing import Any

import boto3
import databricks.sql
import databricks.sql.client
import polars as pl
import pyathena
import pyathena.error
import snowflake.connector
import snowflake.connector.errors
from databricks.sdk.core import Config as DbxConfig
from databricks.sdk.core import oauth_service_principal as dbx_oauth_service_principal
from pyathena.arrow.cursor import ArrowCursor as AthenaArrowCursor
from pyathena.connection import Connection as AthenaConnection
from pydantic import ValidationError

from .provider_typing import (
    ProviderConfiguration,
    ProviderConfigurationList,
)
from .exceptions import (
    MissingTableError,
    QueryError,
    InvalidProviderConfigurationError,
    ConnectionError,
)
from .tdp_client import TetraScienceClient

logger = logging.getLogger(__name__)

# Default TDP athena connection settings
ORG_SLUG_DB_FRIENDLY = os.getenv("ORG_SLUG", "").replace("-", "_")
ATHENA_QUERY_BUCKET = os.environ.get("ATHENA_S3_OUTPUT_LOCATION")
ATHENA_OUTPUT_LOCATION = f"s3://{ATHENA_QUERY_BUCKET}/{ORG_SLUG_DB_FRIENDLY}/"
ATHENA_REGION = os.environ.get("AWS_REGION")
ATHENA_SCHEMA = f"{ORG_SLUG_DB_FRIENDLY}__tss__default"
ATHENA_WORKGROUP = os.getenv("ORG_SLUG", "")


def get_provider_configurations(
    client: TetraScienceClient,
) -> list[ProviderConfiguration]:
    """Get the provider configurations.

    There are two ways to get the provider configurations:
    1. If the environment variable `DATA_APP_PROVIDER_CONFIG` is set, the provider
       configurations are read from it.
    2. If the environment variable `CONNECTOR_ID` is set, the provider
       configurations are fetched from TDP. The secrets are read from environment variables.
    3. If neither of the above is set, an empty list is returned.

    1. is used for local development to specify the provider configurations directly.
    2. is used in production to fetch the provider configurations from TDP.

    Returns:
        List of provider configurations
    """

    # Override by environment variable
    if config_str := os.getenv("DATA_APP_PROVIDER_CONFIG"):
        try:
            return ProviderConfigurationList.validate_json(config_str)
        except ValidationError as e:
            raise InvalidProviderConfigurationError(
                "Invalid provider configuration json in environment variable "
                f"DATA_APP_PROVIDER_CONFIG. {e}"
            ) from None

    # Provider IDs are set by environment variable
    connector_id = os.getenv("CONNECTOR_ID")
    if connector_id is None:
        logger.warning(
            "Environment variable CONNECTOR_ID is not set. Unable to fetch providers."
        )
        return []

    this_app = client.get_container_data_app(connector_id)

    # Get provider field/secret names and get their secrets from environment variables
    provider_configurations = []
    for minimal_provider in this_app.providers:
        # Get provider with secret names
        provider = client.get_provider(minimal_provider.id)

        fields = {}
        for secret in provider.secrets:
            # Example: secret.name = "snowflake.user". The first part is the provider name which is discarded.
            secret_name = secret.name.split(".", 1)[-1]
            secret_value = get_provider_secret_from_env(secret.name)
            fields[secret_name] = secret_value

        config = ProviderConfiguration(
            name=provider.name,
            type=provider.type,
            iconUrl=provider.iconUrl,
            fields=fields,
        )
        provider_configurations.append(config)

    return provider_configurations


def get_provider_secret_from_env(secret_name: str) -> str:
    """
    Get the The provider secrets are stored in environment variables on the container.

    The secret name is mangled the by the function
    [formatProviderEnvName()](https://github.com/tetrascience/ts-service-data-apps/blob/925a37230bef08e0c29a3b945cf07dcb24a76510/src/services/utils.ts#L98-L103)
    and this function should match that logic.

    - Convert to uppercase
    - Replace dots, spaces, and hyphens with underscores
    - Any other characters are removed (non-alphanumeric english characters)

    Args:
        provider_name: Name of the provider
        secret_name: Name of the secret
    Returns:
        Secret value
    """
    # Replace dots, spaces, and hyphens with underscores
    variable_name = re.sub(r"[.\s-]", "_", secret_name.upper())
    # Any other characters are removed (non-alphanumeric english characters)
    variable_name = re.sub("[^A-Z0-9_]", "", variable_name)

    secret = os.getenv(variable_name)

    if secret is None:
        logger.warning(
            "Provider secret not found. Required environment variable is not set."
        )
        return ""
    return secret


class SnowflakeProvider:
    """Snowflake data provider."""

    connection: snowflake.connector.SnowflakeConnection

    def __init__(self, connection: snowflake.connector.SnowflakeConnection):
        """Initialize the Snowflake data provider.

        Args:
            connection: Snowflake connection
        """
        self.connection = connection

    def query(self, query: str, params: dict[str, Any] | None = None) -> pl.DataFrame:
        """Query the Snowflake database.

        Args:
            query: SQL query to execute
            params: Parameters to pass to the query
        Returns:
            DataFrame with the query result
        """
        if params is None:
            params = {}

        logger.debug(f"Executing query: {query} with params: {params}")

        cursor = self.connection.cursor()
        try:
            cursor.execute(query, params)
        except snowflake.connector.errors.Error as e:
            # Example error for missing table FOO:
            # "002003 (42S02): SQL compilation error: Object 'FOO' does not exist or not authorized."
            logger.error(f"Query failed: {query} with params: {params}. Reason: {e}")
            raise QueryError(
                f"Snowflake provider failed to query the database. Reason: {e}"
            ) from e
        df_arrow = cursor.fetch_arrow_all(force_return_table=True)
        frame_or_series = pl.from_arrow(df_arrow)
        if isinstance(frame_or_series, pl.DataFrame):
            return frame_or_series
        return frame_or_series.to_frame()


def build_snowflake_provider(config: ProviderConfiguration) -> SnowflakeProvider:
    """Build a Snowflake data provider from the configuration.

    Args:
        config: Provider configuration
    Returns:
        Snowflake data provider
    """

    try:
        password_auth = {
            "user": config.fields["user"],
            "password": config.fields["password"],
            "account": config.fields["account"],
            "warehouse": config.fields["warehouse"],
            "database": config.fields["database"],
            "schema": config.fields["schema"],
            "role": config.fields["role"],
        }
    except KeyError as e:
        raise InvalidProviderConfigurationError(
            f"Missing field {e} in the provider '{config.name}' to connect to Snowflake "
            "using password based authentication."
        ) from None

    try:
        # The default timezone is America/Los_Angeles. Timestamps from delta tables will be
        # returned with the timezone `timezone`. NOTE, this is not a timezone conversion.
        # The timezone is replaced without translating the clock time. `timezone` is set UTC
        # to match the timezone of delta table timestamps.
        connection = snowflake.connector.connect(timezone="UTC", **password_auth)
    except snowflake.connector.errors.Error as e:
        raise ConnectionError(f"Unable to connect to Snowflake. Reason: {e}") from e

    return SnowflakeProvider(connection)


class AthenaProvider:
    """Athena data provider."""

    connection: AthenaConnection[AthenaArrowCursor]

    def __init__(self, connection: AthenaConnection[AthenaArrowCursor]):
        """Initialize the Athena data provider.

        Args:
            connection: Athena connection
        """
        self.connection = connection

    def query(self, query: str, params: dict[str, Any]) -> pl.DataFrame:
        """Query the Athena database.

        Args:
            query: SQL query to execute
            params: Parameters to pass to the query
        Returns:
            DataFrame with the query result
        """

        if len(query) > 262144:
            raise ValueError("Query length exceeds the maximum allowed limit.")

        if params is None:
            params = {}

        cursor = self.connection.cursor()

        logger.debug(f"Executing query: {query} with params: {params}")
        try:
            query_result = cursor.execute(query, params)
        except pyathena.error.DatabaseError as e:
            logger.error(f"Query failed: {query} with params: {params}. Reason: {e}")
            if "TABLE_NOT_FOUND" in str(e):
                # Example error message:
                # "TABLE_NOT_FOUND: line 13:10: Table 'awsdatacatalog.foo.bar' does not exist"
                error_tail = str(e).rsplit(":", 1)[-1].strip()
                raise MissingTableError(
                    "Athena is unable to find the table. If the table is created by a "
                    "tetraflow, make sure that the tetraflow has run successfully. "
                    + error_tail
                    + "."
                ) from e
            raise
        frame_or_series = pl.from_arrow(query_result.as_arrow())

        if isinstance(frame_or_series, pl.DataFrame):
            return frame_or_series
        return frame_or_series.to_frame()


def get_tdp_athena_provider() -> AthenaProvider:
    """Get the TDP Athena provider"""

    # Check if there is a workgroup to use
    client = boto3.client("athena")
    try:
        client.get_work_group(WorkGroup=ATHENA_WORKGROUP)
        workgroup = ATHENA_WORKGROUP
    except (
        client.exceptions.InvalidRequestException,
        client.exceptions.ClientError,
    ):
        # InvalidRequestException happens if the workgroup does not exist
        # ClientError covers many errors, including access denied.
        workgroup = None

    if workgroup:
        logger.debug(f"Creating athena provider using workgroup '{workgroup}'")
        # No need to specify the s3_staging_dir because the workgroup has a default location
        connection = pyathena.connect(
            region_name=ATHENA_REGION,
            schema_name=ATHENA_SCHEMA,
            work_group=workgroup,
            cursor_class=AthenaArrowCursor,
        )
        return AthenaProvider(connection)

    # If the workgroup is not available, use the default/shared workgroup 'primary'
    logger.debug("Creating athena connection using workgroup 'primary'")
    connection = pyathena.connect(
        s3_staging_dir=ATHENA_OUTPUT_LOCATION,
        region_name=ATHENA_REGION,
        schema_name=ATHENA_SCHEMA,
        work_group="primary",
        cursor_class=AthenaArrowCursor,
    )
    return AthenaProvider(connection)


class DatabricksProvider:
    """Databricks data provider."""

    def __init__(self, connection: databricks.sql.client.Connection):
        """Initialize the Databricks data provider.

        Args:
            connection: Databricks connection
        """
        self.connection = connection

    def query(self, query: str, params: dict[str, Any] | None = None) -> pl.DataFrame:
        """Query the Databricks database.

        Args:
            query: SQL query to execute
            params: Parameters to pass to the query
        Returns:
            DataFrame with the query result
        """

        if params is None:
            params = {}

        logger.debug(f"Executing query: {query} with params: {params}")
        with self.connection.cursor() as cursor:
            cursor.execute(query, params)
            result_arrow = cursor.fetchall_arrow()

        frame_or_series = pl.from_arrow(result_arrow)
        if isinstance(frame_or_series, pl.DataFrame):
            return frame_or_series
        df = frame_or_series.to_frame()
        return df


def build_databricks_provider(config: ProviderConfiguration) -> DatabricksProvider:
    """Build a Databricks data provider from the configuration.

    Args:
        config: Provider configuration
    Returns:
        Databricks data provider
    """
    # Note on databricks.sql thread safety: Threads may share the module, but not connections.

    try:
        server_hostname = config.fields["server_hostname"]
        http_path = config.fields["http_path"]
        client_id = config.fields["client_id"]
        client_secret = config.fields["client_secret"]
        catalog = config.fields["catalog"]
        schema = config.fields.get("schema") or ATHENA_SCHEMA
    except KeyError as e:
        raise InvalidProviderConfigurationError(
            f"Missing field {e} in the provider '{config.name}' to connect to Databricks."
        ) from None

    def credential_provider():
        config = DbxConfig(
            host=f"https://{server_hostname}",
            client_id=client_id,
            client_secret=client_secret,
        )
        return dbx_oauth_service_principal(config)

    logger.debug(
        f"Creating Databricks connection to {server_hostname}. http_path={http_path}, client_id={client_id}, catalog={catalog}, schema={schema}."
    )
    connection = databricks.sql.connect(
        server_hostname=server_hostname,
        http_path=http_path,
        credentials_provider=credential_provider,
        catalog=catalog,
        schema=schema,
    )

    return DatabricksProvider(connection)


def build_provider(
    config: ProviderConfiguration,
) -> SnowflakeProvider | DatabricksProvider | AthenaProvider | object:
    """Build a data provider from the configuration.

    The return types is annotated as `object` in addition to the specific provider types
    to hint that the current list of providers is not exhaustive and more may be added in
    the future.

    Args:
        config: Provider configuration
    Returns:
        Data provider
    """
    if config.type == "snowflake":
        return build_snowflake_provider(config)
    elif config.type == "databricks":
        return build_databricks_provider(config)
    elif config.type == "athena":
        # For Athena, we typically use the TDP Athena provider
        return get_tdp_athena_provider()
    else:
        raise InvalidProviderConfigurationError(
            f"Unsupported provider type: {config.type}"
        )
