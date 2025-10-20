from pyspark.sql import functions as F

def _map_literal_dates(dct):
    kv = []
    for k, v in dct.items():
        kv += [F.lit(k).cast("date"), F.lit(v).cast("date")]
    return F.create_map(*kv)

def join_prev_bday_with_map(df_population, df_features, id_col, pop_date_col,
                            feat_date_col, bday_to_prev, feature_cols=None, suffix="_prev"):

    P = df_population.withColumn(pop_date_col, F.to_date(F.col(pop_date_col)))
    R = df_features.withColumn(feat_date_col, F.to_date(F.col(feat_date_col)))

    prev_map = _map_literal_dates(bday_to_prev)
    P2 = P.withColumn("prev_bday", F.element_at(prev_map, F.col(pop_date_col)))

    if feature_cols is None:
        feature_cols = [c for c in R.columns if c not in {id_col, feat_date_col}]

    J = (P2.alias("L")
          .join(R.alias("R"),
                on=[F.col("L."+id_col) == F.col("R."+id_col),
                    F.col("L.prev_bday") == F.col("R."+feat_date_col)],
                how="left"))

    left_cols  = [F.col("L."+c).alias(c) for c in df_population.columns]
    right_cols = [F.col("R."+c).alias(c+suffix) for c in feature_cols]
    right_cols.append(F.col("R."+feat_date_col).alias(feat_date_col+suffix))
    return J.select(*left_cols, *right_cols)
