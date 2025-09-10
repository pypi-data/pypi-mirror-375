from typing import Optional, Dict, List
from pydantic import BaseModel, Field, TypeAdapter


class ProviderConfiguration(BaseModel):
    """Configuration model for data providers.

    This model represents the configuration needed to connect to various
    database providers (Snowflake, Databricks, Athena, Benchling, etc.)
    attached to a data app.

    Attributes:
        name: Human-readable name of the provider
        type: Provider type (snowflake, databricks, benchling, custom, etc.)
        iconUrl: Optional URL to the provider's icon
        fields: Dictionary containing connection details and credentials
    """

    name: str
    type: str  # snowflake, databricks, benchling, custom, ...
    iconUrl: Optional[str] = Field(None)
    fields: Dict[str, str]


# Type adapter for validating lists of provider configurations
ProviderConfigurationList = TypeAdapter(List[ProviderConfiguration])
