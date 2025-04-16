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
from pyspark.sql.window import Window

def show_duplicate_conflicts(df: DataFrame, key_cols: list) -> DataFrame:
    """
    For duplicate keys, return full rows and highlight which non-key columns differ across those duplicates.

    Args:
        df (DataFrame): Input DataFrame.
        key_cols (list): The columns that define duplicates (primary key columns).

    Returns:
        DataFrame: All rows with duplicate keys + flag columns indicating where values differ.
    """
    non_key_cols = [c for c in df.columns if c not in key_cols]
    window = Window.partitionBy(*key_cols)

    # For each non-key column, create a boolean flag if the value is not consistent across the group
    for col_name in non_key_cols:
        distinct_count_col = f"{col_name}_conflict"
        df = df.withColumn(distinct_count_col, 
                           F.when(F.countDistinct(col_name).over(window) > 1, F.lit(True)).otherwise(F.lit(False)))

    # Filter to only rows where at least one conflict column is True
    conflict_flags = [f"{c}_conflict" for c in non_key_cols]
    condition = F.reduce(lambda x, y: x | y, [F.col(f) for f in conflict_flags])
    
    return df.filter(condition)

