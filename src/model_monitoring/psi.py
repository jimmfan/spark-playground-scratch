from pyspark.sql import functions as F
from pyspark.sql import Window

# ---------
# Helper 1: get bin edges using old data (approxQuantile is fast)
# ---------
def get_quantile_bins(df, col, num_bins=10):
    # returns list of edges like [min, q1, q2, ..., max]
    qs = [i/num_bins for i in range(num_bins+1)]  # e.g. [0.0,0.1,...,1.0]
    edges = df.approxQuantile(col, qs, 1e-4)
    # ensure strictly increasing (dedupe)
    edges = sorted(list(set(edges)))
    return edges

# ---------
# Helper 2: bucket a column using provided edges
# ---------
def bucket_with_edges(df, col, edges, bucket_col):
    # We'll make (edge[i], edge[i+1]] bins
    conds = []
    for i in range(len(edges)-1):
        lower = edges[i]
        upper = edges[i+1]
        conds.append(
            (F.col(col) > lower) & (F.col(col) <= upper)
        )
    # when value == min edge, catch it
    bucket_expr = F.when(F.col(col) <= edges[1], F.lit(0))
    for i, c in enumerate(conds[1:], start=1):
        bucket_expr = bucket_expr.when(c, F.lit(i))
    bucket_expr = bucket_expr.otherwise(F.lit(len(edges)-2))

    return df.withColumn(bucket_col, bucket_expr)

# ---------
# Helper 3: compute PSI for one column
# ---------
def psi_for_column(df_old, df_new, col, num_bins=10):
    edges = get_quantile_bins(df_old, col, num_bins)

    old_b = bucket_with_edges(df_old, col, edges, "bucket_id")
    new_b = bucket_with_edges(df_new, col, edges, "bucket_id")

    # bucket counts
    old_counts = (
        old_b.groupBy("bucket_id")
        .agg(F.count("*").alias("cnt_old"))
    )
    new_counts = (
        new_b.groupBy("bucket_id")
        .agg(F.count("*").alias("cnt_new"))
    )

    # join and get proportions
    joined = (
        old_counts.join(new_counts, "bucket_id", "full")
        .fillna(0, subset=["cnt_old", "cnt_new"])
    )

    totals = joined.agg(
        F.sum("cnt_old").alias("tot_old"),
        F.sum("cnt_new").alias("tot_new")
    ).collect()[0]
    tot_old = totals["tot_old"]
    tot_new = totals["tot_new"]

    # compute PSI contribution per bucket:
    # (p_old - p_new) * ln(p_old / p_new)
    joined = joined.withColumn(
        "p_old", F.col("cnt_old") / F.lit(tot_old)
    ).withColumn(
        "p_new", F.col("cnt_new") / F.lit(tot_new)
    )

    # avoid div by 0
    joined = joined.withColumn(
        "p_old_safe", F.when(F.col("p_old") == 0, F.lit(1e-6)).otherwise(F.col("p_old"))
    ).withColumn(
        "p_new_safe", F.when(F.col("p_new") == 0, F.lit(1e-6)).otherwise(F.col("p_new"))
    )

    joined = joined.withColumn(
        "psi_bucket",
        (F.col("p_old_safe") - F.col("p_new_safe")) *
        F.log(F.col("p_old_safe") / F.col("p_new_safe"))
    )

    psi_value = joined.agg(F.sum("psi_bucket")).collect()[0][0]
    return float(psi_value)

# ---------
# Example usage
# ---------
cols_to_check = ["balance", "utilization_ratio", "age_days"]

results = []
for c in cols_to_check:
    psi_val = psi_for_column(df_old, df_new, c, num_bins=10)
    results.append((c, psi_val))

# results is like:
# [("balance", 0.07), ("utilization_ratio", 0.31), ("age_days", 0.12)]
