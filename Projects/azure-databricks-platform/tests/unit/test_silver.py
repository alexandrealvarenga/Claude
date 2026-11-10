"""Unit tests for Silver layer transformations."""

from pyspark.sql import DataFrame


def test_deduplicate_keeps_latest(spark, sample_df_with_duplicates):
    """Test that deduplication keeps the latest record."""
    from platform.silver import deduplicate

    result = deduplicate(
        sample_df_with_duplicates,
        partition_columns=["id"],
        order_column="updated_at",
    )

    assert result.count() == 2
    rows = {row.id: row for row in result.collect()}

    assert rows["1"]["name"] == "Alice Updated"
    assert rows["1"]["amount"] == 150
    assert rows["2"]["name"] == "Bob"
    assert rows["2"]["amount"] == 200


def test_standardize_case_upper(spark, sample_df):
    """Test upper case standardization."""
    from platform.silver import standardize_case

    result = standardize_case(sample_df, ["name"], case_type="upper")
    names = [row.name for row in result.select("name").collect()]

    assert all(name.isupper() for name in names)


def test_standardize_case_lower(spark, sample_df):
    """Test lower case standardization."""
    from platform.silver import standardize_case

    result = standardize_case(sample_df, ["name"], case_type="lower")
    names = [row.name for row in result.select("name").collect()]

    assert all(name.islower() for name in names)


def test_standardize_case_invalid_type(spark, sample_df):
    """Test that invalid case type raises error."""
    from platform.silver import standardize_case

    with pytest.raises(ValueError, match="Invalid case_type"):
        standardize_case(sample_df, ["name"], case_type="invalid")


def test_trim_whitespace(spark):
    """Test whitespace trimming."""
    from platform.silver import trim_whitespace
    from pyspark.sql.types import StructType, StructField, StringType

    schema = StructType([StructField("name", StringType(), True)])
    data = [("  Alice  ",), ("  Bob",), ("Charlie  ",)]
    df = spark.createDataFrame(data, schema)

    result = trim_whitespace(df, ["name"])
    names = [row.name for row in result.collect()]

    assert names == ["Alice", "Bob", "Charlie"]


def test_trim_whitespace_all_strings(spark, sample_df):
    """Test trimming all string columns when none specified."""
    from platform.silver import trim_whitespace
    from pyspark.sql.types import StructType, StructField, StringType

    schema = StructType([
        StructField("name", StringType(), True),
        StructField("id", StringType(), True),
    ])
    data = [("  Alice  ", "  1  "), ("  Bob  ", "  2  ")]
    df = spark.createDataFrame(data, schema)

    result = trim_whitespace(df)
    row = result.collect()[0]

    assert row.name == "Alice"
    assert row.id == "1"


def test_validate_not_null_filters_nulls(spark):
    """Test that null values are filtered out."""
    from platform.silver import validate_not_null
    from pyspark.sql.types import StructType, StructField, StringType, IntegerType

    schema = StructType([
        StructField("id", StringType(), True),
        StructField("name", StringType(), True),
    ])
    data = [("1", "Alice"), ("2", None), (None, "Charlie")]
    df = spark.createDataFrame(data, schema)

    result = validate_not_null(df, ["id", "name"])
    count = result.count()

    assert count == 1
    assert result.collect()[0]["name"] == "Alice"


def test_aggregate_by_key_sum(spark, sample_df):
    """Test aggregation with sum."""
    from platform.gold import aggregate_by_key

    result = aggregate_by_key(
        sample_df,
        group_by_columns=["name"],
        aggregation_columns=[("amount", "sum")],
    )

    rows = {row.name: row for row in result.collect()}
    assert rows["Alice"]["amount"] == 100
    assert rows["Bob"]["amount"] == 200
    assert rows["Charlie"]["amount"] == 300


def test_aggregate_by_key_count(spark, sample_df):
    """Test aggregation with count."""
    from platform.gold import aggregate_by_key

    result = aggregate_by_key(
        sample_df,
        group_by_columns=["name"],
        aggregation_columns=[("amount", "count")],
    )

    rows = {row.name: row for row in result.collect()}
    assert all(row["amount"] == 1 for row in rows.values())
