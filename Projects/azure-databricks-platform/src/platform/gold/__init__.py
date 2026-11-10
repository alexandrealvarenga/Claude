"""Gold layer - Business-ready datasets and aggregates.

Contains curated datasets optimized for analytics and reporting.
Implements business rules and calculations.
"""

from pyspark.sql import DataFrame


CATALOG_NAME = "gold"


def aggregate_by_key(
    df: DataFrame,
    group_by_columns: list[str],
    aggregation_columns: list[tuple[str, str]],
) -> DataFrame:
    """Aggregate data by key columns with specified aggregations.

    Args:
        df: Input DataFrame
        group_by_columns: Columns to group by
        aggregation_columns: List of (column_name, aggregation_type) tuples
            e.g., [("amount", "sum"), ("count", "count")]

    Returns:
        Aggregated DataFrame
    """
    from pyspark.sql import functions as F

    agg_exprs = []
    for col, agg_type in aggregation_columns:
        if agg_type == "sum":
            agg_exprs.append(F.sum(col).alias(col))
        elif agg_type == "count":
            agg_exprs.append(F.count(col).alias(col))
        elif agg_type == "avg":
            agg_exprs.append(F.avg(col).alias(col))
        elif agg_type == "min":
            agg_exprs.append(F.min(col).alias(col))
        elif agg_type == "max":
            agg_exprs.append(F.max(col).alias(col))
        else:
            raise ValueError(f"Unsupported aggregation type: {agg_type}")

    return df.groupBy(*group_by_columns).agg(*agg_exprs)


def calculate_scd_type2(
    df: DataFrame,
    key_columns: list[str],
    change_detection_columns: list[str],
    valid_from_column: str = "valid_from",
    valid_to_column: str = "valid_to",
    is_current_column: str = "is_current",
) -> DataFrame:
    """Implement Slowly Changing Dimension Type 2.

    Tracks historical changes with validity periods.

    Args:
        df: Input DataFrame with current state
        key_columns: Natural key columns
        change_detection_columns: Columns that trigger new version
        valid_from_column: Column name for version start
        valid_to_column: Column name for version end
        is_current_column: Column name for current flag

    Returns:
        DataFrame with SCD Type 2 history
    """
    from pyspark.sql import functions as F
    from pyspark.sql.window import Window

    window = Window.partitionBy(*key_columns).orderBy(F.desc(valid_from_column))

    df = df.withColumn("_row_num", F.row_number().over(window))

    return df.filter(F.col("_row_num") == 1).drop("_row_num")


def write_to_gold(
    df: DataFrame,
    table_name: str,
    partition_by: list[str] | None = None,
) -> None:
    """Write DataFrame to Gold layer as Delta table.

    Gold layer always uses overwrite mode for reprocessing capability.

    Args:
        df: DataFrame to write
        table_name: Table name (catalog.schema.table format)
        partition_by: Columns to partition by
    """
    writer = df.write.format("delta").mode("overwrite")

    if partition_by:
        writer = writer.partitionBy(*partition_by)

    writer.saveAsTable(table_name)
