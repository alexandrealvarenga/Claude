"""Unit tests for configuration management."""

import os

import pytest


def test_get_environment_valid():
    """Test valid environment values."""
    os.environ["ENVIRONMENT"] = "dev"
    from platform.config import get_environment

    env = get_environment()
    assert env.value == "dev"


def test_get_environment_invalid():
    """Test invalid environment raises error."""
    os.environ["ENVIRONMENT"] = "invalid"
    from platform.config import get_environment

    with pytest.raises(ValueError, match="Invalid ENVIRONMENT"):
        get_environment()


def test_get_environment_case_insensitive():
    """Test environment is case insensitive."""
    os.environ["ENVIRONMENT"] = "PROD"
    from platform.config import get_environment

    env = get_environment()
    assert env.value == "prod"


def test_get_azure_config_missing_variables():
    """Test missing Azure config raises error."""
    for var in ["AZURE_SUBSCRIPTION_ID", "AZURE_TENANT_ID", "AZURE_LOCATION"]:
        if var in os.environ:
            del os.environ[var]

    from platform.config import get_azure_config

    with pytest.raises(EnvironmentError, match="Missing required environment variables"):
        get_azure_config()


def test_get_azure_config_success():
    """Test successful Azure config loading."""
    os.environ["AZURE_SUBSCRIPTION_ID"] = "sub-123"
    os.environ["AZURE_TENANT_ID"] = "tenant-456"
    os.environ["AZURE_LOCATION"] = "eastus"

    from platform.config import get_azure_config

    config = get_azure_config()
    assert config.subscription_id == "sub-123"
    assert config.tenant_id == "tenant-456"
    assert config.location == "eastus"


def test_get_storage_config_missing():
    """Test missing storage config raises error."""
    if "STORAGE_ACCOUNT_NAME" in os.environ:
        del os.environ["STORAGE_ACCOUNT_NAME"]

    from platform.config import get_storage_config

    with pytest.raises(EnvironmentError, match="Missing required: STORAGE_ACCOUNT_NAME"):
        get_storage_config()


def test_get_storage_config_success():
    """Test successful storage config loading."""
    os.environ["STORAGE_ACCOUNT_NAME"] = "mystorageaccount"

    from platform.config import get_storage_config

    config = get_storage_config()
    assert config.account_name == "mystorageaccount"
    assert config.container_bronze == "bronze"
    assert config.container_silver == "silver"
    assert config.container_gold == "gold"


def test_get_databricks_config_missing():
    """Test missing Databricks config raises error."""
    if "DATABRICKS_WORKSPACE_URL" in os.environ:
        del os.environ["DATABRICKS_WORKSPACE_URL"]

    from platform.config import get_databricks_config

    with pytest.raises(EnvironmentError, match="Missing required: DATABRICKS_WORKSPACE_URL"):
        get_databricks_config()


def test_get_databricks_config_success():
    """Test successful Databricks config loading."""
    os.environ["DATABRICKS_WORKSPACE_URL"] = "https://adb-123.azuredatabricks.net"
    os.environ["DATABRICKS_CATALOG"] = "main"

    from platform.config import get_databricks_config

    config = get_databricks_config()
    assert config.workspace_url == "https://adb-123.azuredatabricks.net"
    assert config.catalog_name == "main"


def test_get_databricks_config_default_catalog():
    """Test Databricks config uses default catalog."""
    os.environ["DATABRICKS_WORKSPACE_URL"] = "https://adb-123.azuredatabricks.net"
    if "DATABRICKS_CATALOG" in os.environ:
        del os.environ["DATABRICKS_CATALOG"]

    from platform.config import get_databricks_config

    config = get_databricks_config()
    assert config.catalog_name == "main"


def test_pipeline_run_id_from_env(spark):
    """Test pipeline run ID can be set from environment."""
    os.environ["PIPELINE_RUN_ID"] = "test-run-123"
    os.environ["SOURCE_SYSTEM"] = "test-system"

    from platform.config import get_pipeline_config

    config = get_pipeline_config()
    assert config.pipeline_run_id == "test-run-123"
    assert config.source_system == "test-system"
