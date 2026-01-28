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

from pyspark.sql.functions import array, expr, col
from pyspark.sql.column import Column
from typing import List

def rowwise_min_ignore_nulls(columns: List[str]) -> Column:
    """
    Returns row-wise minimum ignoring nulls using array_min + filter.
    Equivalent to pandas .min(axis=1, skipna=True)
    """
    expr_str = f"array_min(filter(array({', '.join(columns)}), x -> x is not null))"
    return expr(expr_str)

def rowwise_max_ignore_nulls(columns: List[str]) -> Column:
    """
    Returns row-wise maximum ignoring nulls using array_max + filter.
    Equivalent to pandas .max(axis=1, skipna=True)
    """
    expr_str = f"array_max(filter(array({', '.join(columns)}), x -> x is not null))"
    return expr(expr_str)


from pyspark.sql.functions import year, month

def pandas_month_diff(start_col: Column, end_col: Column) -> Column:
    """
    Returns the difference in calendar months between two date columns,
    replicating pandas Period("M") difference behavior.
    """
    return (year(end_col) - year(start_col)) * 12 + (month(end_col) - month(start_col))


df = df.withColumn(
    "first_dt",
    rowwise_min_ignore_nulls(["date1", "date2", "date3"])
).withColumn(
    "mob1",
    pandas_month_diff(col("app_date_entered_system"), col("first_dt"))
).withColumn(
    "second_dt",
    rowwise_min_ignore_nulls(["second_date1", "second_date2", "second_date3"])
).withColumn(
    "mob2",
    pandas_month_diff(col("app_date_entered_system"), col("second_dt"))
).withColumn(
    "max_mob",
    rowwise_max_ignore_nulls(["mob1", "mob2"])
)
