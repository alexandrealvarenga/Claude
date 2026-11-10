"""Configuration management for the data platform.

Loads configuration from environment variables and validates required settings.
Credentials are never hardcoded - they are loaded from environment or Azure Key Vault.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Environment(Enum):
    """Deployment environment."""

    DEV = "dev"
    TEST = "test"
    PROD = "prod"


@dataclass(frozen=True)
class AzureConfig:
    """Azure subscription and tenant configuration."""

    subscription_id: str
    tenant_id: str
    location: str


@dataclass(frozen=True)
class StorageConfig:
    """ADLS Gen2 storage configuration."""

    account_name: str
    container_bronze: str = "bronze"
    container_silver: str = "silver"
    container_gold: str = "gold"


@dataclass(frozen=True)
class DatabricksConfig:
    """Databricks workspace configuration."""

    workspace_url: str
    catalog_name: str


@dataclass(frozen=True)
class KeyVaultConfig:
    """Azure Key Vault configuration."""

    vault_url: str


@dataclass
class PipelineConfig:
    """Pipeline execution configuration."""

    pipeline_run_id: str
    source_system: str
    environment: Environment
    azure: AzureConfig
    storage: StorageConfig
    databricks: DatabricksConfig
    key_vault: Optional[KeyVaultConfig] = None


def get_environment() -> Environment:
    """Get deployment environment from ENVIRONMENT variable."""
    env_var = os.environ.get("ENVIRONMENT", "dev").lower()
    try:
        return Environment(env_var)
    except ValueError:
        raise ValueError(f"Invalid ENVIRONMENT: {env_var}. Must be dev, test, or prod.")


def get_azure_config() -> AzureConfig:
    """Load Azure configuration from environment variables."""
    required = ["AZURE_SUBSCRIPTION_ID", "AZURE_TENANT_ID", "AZURE_LOCATION"]
    missing = [v for v in required if not os.environ.get(v)]
    if missing:
        raise EnvironmentError(
            f"Missing required environment variables: {', '.join(missing)}"
        )

    return AzureConfig(
        subscription_id=os.environ["AZURE_SUBSCRIPTION_ID"],
        tenant_id=os.environ["AZURE_TENANT_ID"],
        location=os.environ["AZURE_LOCATION"],
    )


def get_storage_config() -> StorageConfig:
    """Load storage configuration from environment variables."""
    account_name = os.environ.get("STORAGE_ACCOUNT_NAME")
    if not account_name:
        raise EnvironmentError("Missing required: STORAGE_ACCOUNT_NAME")

    return StorageConfig(account_name=account_name)


def get_databricks_config() -> DatabricksConfig:
    """Load Databricks configuration from environment variables."""
    workspace_url = os.environ.get("DATABRICKS_WORKSPACE_URL")
    if not workspace_url:
        raise EnvironmentError("Missing required: DATABRICKS_WORKSPACE_URL")

    catalog_name = os.environ.get("DATABRICKS_CATALOG", "main")

    return DatabricksConfig(
        workspace_url=workspace_url,
        catalog_name=catalog_name,
    )


def get_pipeline_config() -> PipelineConfig:
    """Build complete pipeline configuration from environment."""
    import uuid

    return PipelineConfig(
        pipeline_run_id=os.environ.get("PIPELINE_RUN_ID", str(uuid.uuid4())),
        source_system=os.environ.get("SOURCE_SYSTEM", "unknown"),
        environment=get_environment(),
        azure=get_azure_config(),
        storage=get_storage_config(),
        databricks=get_databricks_config(),
    )
