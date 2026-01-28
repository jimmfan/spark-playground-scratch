from pyspark.sql import functions as F

def _map_literal_dates(dct):
    kv = []
    for k, v in dct.items():
        kv += [F.lit(k).cast("date"), F.lit(v).cast("date")]
    return F.create_map(*kv)
In my training dataset, I create a lookback feature_date column in pyspark:

F.create_map
def join_prev_bday_with_map_keys(
    df_population,
    df_features,
    *,
    keys,                 # list of join columns, e.g., ["id", "product_cd"]
    pop_date_col,
    feat_date_col,
    bday_to_prev,         # {"YYYY-MM-DD": "YYYY-MM-DD"}
    feature_cols=None,
    suffix="_prev"
):
    # Normalize date types
    P = df_population.withColumn(pop_date_col, F.to_date(F.col(pop_date_col)))
    R = df_features.withColumn(feat_date_col, F.to_date(F.col(feat_date_col)))

    # prev_bday column from map literal
    prev_map = _map_literal_dates(bday_to_prev)
    P2 = P.withColumn("prev_bday", F.element_at(prev_map, F.col(pop_date_col)))

    # Choose right-side columns to keep
    if feature_cols is None:
        feature_cols = [c for c in R.columns if c not in set(keys + [feat_date_col])]

    # Build composite join condition: all keys + prev_bday == feature date
    join_cond = [F.col("L."+k) == F.col("R."+k) for k in keys]
    join_cond.append(F.col("L.prev_bday") == F.col("R."+feat_date_col))

    J = (P2.alias("L").join(R.alias("R"), on=join_cond, how="left"))

    # Keep all left cols + selected right cols (suffixed)
    left_cols  = [F.col("L."+c).alias(c) for c in df_population.columns]
    right_cols = [F.col("R."+c).alias(c+suffix) for c in feature_cols if c in R.columns]
    right_cols.append(F.col("R."+feat_date_col).alias(feat_date_col+suffix))

    return J.select(*left_cols, *right_cols)
