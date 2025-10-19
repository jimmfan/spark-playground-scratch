def asof_join(df_left, df_right, keys, left_date_col, right_date_col, allow_same_day=True):
    """
    Left as-of join: match on keys with the closest prior (or same-day) right_date.
    Returns df_left columns + right columns.
    """
    from pyspark.sql import functions as F, Window as W

    L, R = df_left.alias("L"), df_right.alias("R")
    cmp = F.col(f"R.{right_date_col}") <= F.col(f"L.{left_date_col}") if allow_same_day \
          else F.col(f"R.{right_date_col}") <  F.col(f"L.{left_date_col}")

    join_cond = [F.col(f"L.{k}") == F.col(f"R.{k}") for k in keys] + [cmp]
    j = L.join(R, on=join_cond, how="left")

    w = W.partitionBy(*[F.col(f"L.{k}") for k in keys], F.col(f"L.{left_date_col}")) \
         .orderBy(F.col(f"R.{right_date_col}").desc())

    return (
        j.withColumn("_rn", F.row_number().over(w))
         .filter(F.col("_rn") == 1)
         .drop("_rn")
    )