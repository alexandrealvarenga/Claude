"""Unity Catalog utilities and helpers.

Provides functions for managing Unity Catalog objects.
Credentials are loaded from Azure Key Vault via Managed Identity.
"""

from __future__ import annotations

from typing import Optional

from pyspark.sql import SparkSession


def create_catalog_if_not_exists(spark: SparkSession, catalog_name: str) -> None:
    """Create Unity Catalog if it doesn't exist.

    Args:
        spark: SparkSession with UC privileges
        catalog_name: Name of catalog to create
    """
    spark.sql(f"CREATE CATALOG IF NOT EXISTS {catalog_name}")


def create_schema_if_not_exists(
    spark: SparkSession,
    catalog_name: str,
    schema_name: str,
) -> None:
    """Create schema within a catalog if it doesn't exist.

    Args:
        spark: SparkSession with UC privileges
        catalog_name: Catalog name
        schema_name: Schema name
    """
    spark.sql(f"CREATE SCHEMA IF NOT EXISTS {catalog_name}.{schema_name}")


def create_external_location(
    spark: SparkSession,
    location_name: str,
    storage_account: str,
    container: str,
    catalog_name: str,
) -> None:
    """Create external location for Unity Catalog storage.

    Args:
        spark: SparkSession with UC privileges
        location_name: Name for the external location
        storage_account: ADLS account name
        container: Container name
        catalog_name: Associated catalog name
    """
    location_url = f"abfss://{container}@{storage_account}.dfs.core.windows.net/"

    spark.sql(f"""
        CREATE EXTERNAL LOCATION IF NOT EXISTS {location_name}
        URL '{location_url}'
        WITH (STORAGE CREDENTIAL {catalog_name}_credential)
        COMMENT 'External location for {catalog_name}'
    """)


def grant_catalog_access(
    spark: SparkSession,
    catalog_name: str,
    principal: str,
    privilege: str = "USAGE",
) -> None:
    """Grant privilege on catalog to a principal.

    Args:
        spark: SparkSession with UC admin privileges
        catalog_name: Catalog name
        principal: Service principal or security group
        privilege: Privilege to grant (USAGE, CREATE, etc.)
    """
    spark.sql(f"GRANT {privilege} ON CATALOG {catalog_name} TO `{principal}`")


def get_table_location(
    spark: SparkSession,
    catalog_name: str,
    schema_name: str,
    table_name: str,
) -> Optional[str]:
    """Get the storage location of a Delta table.

    Args:
        spark: SparkSession
        catalog_name: Catalog name
        schema_name: Schema name
        table_name: Table name

    Returns:
        Table location path or None if not found
    """
    result = spark.sql(f"""
        DESCRIBE DETAIL {catalog_name}.{schema_name}.{table_name}
    """.strip())

    location = result.collect()
    if location:
        return location[0]["location"]
    return None


def register_table_to_catalog(
    spark: SparkSession,
    table_name: str,
    location: str,
    catalog_name: str,
    schema_name: str,
    table_type: str = "EXTERNAL",
) -> None:
    """Register a table to Unity Catalog.

    Args:
        spark: SparkSession with UC privileges
        table_name: Table name
        location: Storage location
        catalog_name: Catalog name
        schema_name: Schema name
        table_type: EXTERNAL or MANAGED
    """
    full_name = f"{catalog_name}.{schema_name}.{table_name}"

    if table_type == "EXTERNAL":
        spark.sql(f"""
            CREATE TABLE IF NOT EXISTS {full_name}
            LOCATION '{location}'
        """)
    else:
        spark.sql(f"CREATE TABLE IF NOT EXISTS {full_name}")
