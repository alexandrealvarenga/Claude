"""Bronze layer - Raw, immutable ingestion layer.

Raw data is ingested from source systems and stored in Delta format.
Data is not transformed - only schema is applied and audit columns added.
"""

from pyspark.sql import DataFrame, SparkSession

CATALOG_NAME = "bronze"


def read_from_adls(
    spark: SparkSession,
    account_name: str,
    container: str,
    file_path: str,
    file_format: str = "csv",
    header: bool = True,
    infer_schema: bool = False,
) -> DataFrame:
    """Read data from ADLS Gen2 storage.

    Args:
        spark: SparkSession
        account_name: ADLS account name
        container: Container name
        file_path: Path to file within container
        file_format: File format (csv, json, parquet, delta)
        header: Whether CSV has header row
        infer_schema: Whether to infer schema (use explicit schema in prod)

    Returns:
        DataFrame with raw data
    """
    abfs_path = (
        f"abfss://{container}@{account_name}.dfs.core.windows.net/{file_path}"
    )

    reader = spark.read.format(file_format)

    if file_format == "csv":
        reader = reader.option("header", header)

    return reader.load(abfs_path)


def write_to_bronze(
    df: DataFrame,
    table_name: str,
    partition_by: list[str] | None = None,
    mode: str = "append",
) -> None:
    """Write DataFrame to Bronze layer as Delta table.

    Args:
        df: DataFrame to write
        table_name: Table name (catalog.schema.table format)
        partition_by: Columns to partition by
        mode: Write mode (append, overwrite, etc.)
    """
    writer = df.write.format("delta").mode(mode)

    if partition_by:
        writer = writer.partitionBy(*partition_by)

    writer.saveAsTable(table_name)
