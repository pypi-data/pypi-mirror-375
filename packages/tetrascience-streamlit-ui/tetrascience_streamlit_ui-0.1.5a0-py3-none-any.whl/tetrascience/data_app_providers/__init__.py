# TetraScience Data App Providers
# SDK functions for retrieving different provider types from the TetraScience platform

from .provider_typing import ProviderConfiguration, ProviderConfigurationList
from .provider import (
    # Provider classes
    SnowflakeProvider,
    DatabricksProvider,
    AthenaProvider,
    # Factory functions
    build_snowflake_provider,
    build_databricks_provider,
    get_tdp_athena_provider,
    build_provider,
    # Configuration functions
    get_provider_configurations,
    get_provider_secret_from_env,
)
from .exceptions import (
    ProviderError,
    MissingTableError,
    QueryError,
    InvalidProviderConfigurationError,
    ConnectionError,
)

from .tdp_client import TetraScienceClient

__all__ = [
    # Types
    "ProviderConfiguration",
    "ProviderConfigurationList",
    # Provider classes
    "SnowflakeProvider",
    "DatabricksProvider",
    "AthenaProvider",
    # Factory functions
    "build_snowflake_provider",
    "build_databricks_provider",
    "get_tdp_athena_provider",
    "build_provider",
    # Configuration functions
    "get_provider_configurations",
    "get_provider_secret_from_env",
    # Exception classes
    "ProviderError",
    "MissingTableError",
    "QueryError",
    "InvalidProviderConfigurationError",
    "ConnectionError",
    "TetraScienceClient",
]
