from pyspark.sql import functions as F
from datetime import datetime

DEFAULT_TIMESTAMP = datetime.max
DEFAULT_INT = -1

df = (
    df.withColumn(
        "min_date",
        F.when(
            F.col("col1").isNull() & F.col("col2").isNull() & F.col("col3").isNull(),
            None
        ).otherwise(
            F.least(
                F.coalesce(F.col("col1"), F.lit(DEFAULT_TIMESTAMP)),
                F.coalesce(F.col("col2"), F.lit(DEFAULT_TIMESTAMP)),
                F.coalesce(F.col("col3"), F.lit(DEFAULT_TIMESTAMP))
            )
        )
    ).withColumn(
        "months_between1",
        F.floor(F.months_between(F.col("min_date"), F.col("application_date")))
    ).withColumn(
        "months_between2",
        F.floor(F.months_between(F.col("min_date"), F.col("some_other_date")))
    ).withColumn(
        "max_months_between",
        F.when(
            F.col("months_between1").isNull() & F.col("months_between2").isNull(),
            None
        ).otherwise(
            F.greatest(
                F.coalesce(F.col("months_between1"), F.lit(DEFAULT_INT)),
                F.coalesce(F.col("months_between2"), F.lit(DEFAULT_INT))
            )
        )
    )
)

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

def report_conflicting_duplicates(df: DataFrame, key_cols: list) -> DataFrame:
    """
    Find duplicate rows by key, and report which non-key columns have conflicting values.

    Args:
        df (DataFrame): Input DataFrame
        key_cols (list): List of column names to group by (keys)

    Returns:
        DataFrame: Rows with duplicate keys and differing values in at least one non-key column
    """
    non_key_cols = [c for c in df.columns if c not in key_cols]
    
    # Aggregate each non-key column to count distinct values per group
    agg_exprs = [F.countDistinct(c).alias(f"distinct_{c}") for c in non_key_cols]
    
    # Group by keys and apply aggregations
    conflict_df = df.groupBy(key_cols).agg(*agg_exprs)
    
    # Filter to only rows where at least one non-key column has >1 distinct value
    filter_expr = " OR ".join([f"distinct_{c} > 1" for c in non_key_cols])
    
    return conflict_df.filter(filter_expr)
