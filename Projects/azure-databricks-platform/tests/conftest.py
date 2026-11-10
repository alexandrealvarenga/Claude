"""Pytest configuration and shared fixtures."""

from __future__ import annotations

import os
from typing import Generator

import pytest
from pyspark.sql import SparkSession


@pytest.fixture(scope="session")
def spark() -> Generator[SparkSession, None, None]:
    """Create SparkSession for testing.

    Uses local mode for unit tests.
    In integration tests, this would connect to actual Databricks.
    """
    os.environ["SPARK_LOCAL_IP"] = "127.0.0.1"

    spark = (
        SparkSession.builder
        .master("local[2]")
        .appName("data-platform-tests")
        .config("spark.sql.shell.enabled", "false")
        .config("spark.ui.enabled", "false")
        .getOrCreate()
    )

    yield spark

    spark.stop()


@pytest.fixture
def sample_df(spark: SparkSession) -> "DataFrame":
    """Create a sample DataFrame for testing."""
    from pyspark.sql.types import StructType, StructField, StringType, IntegerType, TimestampType
    from datetime import datetime

    schema = StructType([
        StructField("id", StringType(), False),
        StructField("name", StringType(), True),
        StructField("amount", IntegerType(), True),
        StructField("created_at", TimestampType(), True),
    ])

    data = [
        ("1", "Alice", 100, datetime(2024, 1, 1)),
        ("2", "Bob", 200, datetime(2024, 1, 2)),
        ("3", "Charlie", 300, datetime(2024, 1, 3)),
    ]

    return spark.createDataFrame(data, schema)


@pytest.fixture
def sample_df_with_duplicates(spark: SparkSession) -> "DataFrame":
    """Create a sample DataFrame with duplicate records."""
    from pyspark.sql.types import StructType, StructField, StringType, IntegerType
    from datetime import datetime

    schema = StructType([
        StructField("id", StringType(), False),
        StructField("name", StringType(), True),
        StructField("amount", IntegerType(), True),
        StructField("updated_at", TimestampType(), True),
    ])

    data = [
        ("1", "Alice", 100, datetime(2024, 1, 1)),
        ("1", "Alice Updated", 150, datetime(2024, 1, 2)),
        ("2", "Bob", 200, datetime(2024, 1, 1)),
        ("2", "Bob", 200, datetime(2024, 1, 1)),
    ]

    return spark.createDataFrame(data, schema)


from pyspark.sql import DataFrame
