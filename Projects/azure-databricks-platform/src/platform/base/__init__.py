"""Base layer with shared functionality for all data layers."""

from pyspark.sql import DataFrame

AUDIT_COLUMNS = [
    "ingestion_timestamp",
    "source_system",
    "pipeline_run_id",
]


def add_audit_columns(df: DataFrame, source_system: str, pipeline_run_id: str) -> DataFrame:
    """Add standardized audit columns to a DataFrame.

    Args:
        df: Input DataFrame
        source_system: Name of the source system
        pipeline_run_id: Unique identifier for this pipeline run

    Returns:
        DataFrame with audit columns added
    """
    from pyspark.sql import functions as F

    return df.withColumn(
        "ingestion_timestamp", F.current_timestamp()
    ).withColumn(
        "source_system", F.lit(source_system)
    ).withColumn(
        "pipeline_run_id", F.lit(pipeline_run_id)
    )
