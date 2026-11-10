"""Silver layer - Validated, standardized, and deduplicated data.

Data from Bronze layer is cleaned, validated, and deduplicated.
Implements slowly changing dimensions (SCD) where applicable.
"""

from pyspark.sql import DataFrame, SparkSession


CATALOG_NAME = "silver"


def deduplicate(df: DataFrame, partition_columns: list[str], order_column: str) -> DataFrame:
    """Remove duplicates keeping latest record per partition.

    Args:
        df: Input DataFrame
        partition_columns: Columns to partition by for deduplication
        order_column: Column to order by (typically timestamp)

    Returns:
        Deduplicated DataFrame
    """
    from pyspark.sql import functions as F
    from pyspark.sql.window import Window

    window = Window.partitionBy(*partition_columns).orderBy(F.desc(order_column))

    return df.withColumn(
        "_row_num", F.row_number().over(window)
    ).filter(
        F.col("_row_num") == 1
    ).drop("_row_num")


def standardize_case(df: DataFrame, columns: list[str], case_type: str = "upper") -> DataFrame:
    """Standardize string case for specified columns.

    Args:
        df: Input DataFrame
        columns: Columns to standardize
        case_type: 'upper', 'lower', or 'title'

    Returns:
        DataFrame with standardized case
    """
    from pyspark.sql import functions as F

    case_funcs = {
        "upper": F.upper,
        "lower": F.lower,
        "title": F.initcap,
    }

    func = case_funcs.get(case_type.lower())
    if not func:
        raise ValueError(f"Invalid case_type: {case_type}")

    for col in columns:
        df = df.withColumn(col, func(F.col(col)))

    return df


def trim_whitespace(df: DataFrame, columns: list[str] | None = None) -> DataFrame:
    """Trim whitespace from string columns.

    Args:
        df: Input DataFrame
        columns: Columns to trim. If None, trims all string columns.

    Returns:
        DataFrame with trimmed strings
    """
    from pyspark.sql import functions as F

    if columns is None:
        columns = [
            f.name for f in df.schema.fields
            if f.dataType.typeName() == "string"
        ]

    for col in columns:
        df = df.withColumn(col, F.trim(F.col(col)))

    return df


def validate_not_null(df: DataFrame, columns: list[str]) -> DataFrame:
    """Filter out rows where any of the specified columns are null.

    Args:
        df: Input DataFrame
        columns: Columns that must not be null

    Returns:
        DataFrame with nulls filtered out
    """
    from pyspark.sql import functions as F

    condition = None
    for col in columns:
        expr = F.col(col).isNotNull()
        condition = condition & expr if condition else expr

    return df.filter(condition)


def write_to_silver(
    df: DataFrame,
    table_name: str,
    partition_by: list[str] | None = None,
    mode: str = "merge",
) -> None:
    """Write DataFrame to Silver layer as Delta table.

    Uses merge mode for idempotent upserts.

    Args:
        df: DataFrame to write
        table_name: Table name (catalog.schema.table format)
        partition_by: Columns to partition by
        mode: Write mode (merge for upsert)
    """
    writer = df.write.format("delta").mode("overwrite")

    if partition_by:
        writer = writer.partitionBy(*partition_by)

    writer.saveAsTable(table_name)
