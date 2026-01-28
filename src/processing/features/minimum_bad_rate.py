from pyspark.sql import functions as F

# Step 1. Category stats
stats = (
    df.groupBy("merchant_category")
      .agg(
          F.count("*").alias("n"),
          F.avg("label").alias("bad_rate")
      )
)

# Step 2. Identify which categories are high-risk but too small
min_bucket_n = 1000
high_risk_threshold = 0.5

stats = stats.withColumn(
    "risk_type",
    F.when((F.col("bad_rate") >= high_risk_threshold) & (F.col("n") < min_bucket_n),
           F.lit("RARE_HIGH_RISK"))
     .when(F.col("bad_rate") >= high_risk_threshold, F.lit("COMMON_HIGH_RISK"))
     .otherwise(F.lit("OTHER"))
)

# Step 3. Check combined sample size of that RARE_HIGH_RISK group
total_rare_high_risk = stats.filter(F.col("risk_type") == "RARE_HIGH_RISK").agg(F.sum("n")).collect()[0][0]
print(f"Combined rows in RARE_HIGH_RISK bucket: {total_rare_high_risk}")



#### separate function #####
from pyspark.sql import functions as F

def suggest_category_groups(
    df,
    cat_col,
    label_col,
    base_rate=None,
    very_rare_n=20,
    low_freq_n=100,
    min_bucket_n=1000,
    high_risk_factor=5.0,
    extreme_risk_factor=10.0,
):
    """
    Suggest grouping for categorical values in `cat_col` based on:
    - event rate in `label_col`
    - frequency (count)
    - relative risk vs baseline (multiples of base_rate)

    Returns a DataFrame with:
        [cat_col, n, bad_rate, size_band, risk_bucket, recommended_group]
    """

    # 1. compute base event rate if not provided
    if base_rate is None:
        base_rate = df.agg(F.avg(label_col)).collect()[0][0]

    high_risk_cutoff = base_rate * high_risk_factor      # e.g. 5x base
    extreme_risk_cutoff = base_rate * extreme_risk_factor  # e.g. 10x base

    # 2. per-category stats
    stats = (
        df.groupBy(cat_col)
          .agg(
              F.count("*").alias("n"),
              F.avg(label_col).alias("bad_rate")
          )
    )

    # 3. size bands based on frequency
    # VERY_RARE: 1–very_rare_n-1 rows
    # RARE:      very_rare_n–low_freq_n-1 rows
    # MID_FREQ:  low_freq_n–min_bucket_n-1 rows
    # COMMON:    >= min_bucket_n rows
    stats = stats.withColumn(
        "size_band",
        F.when(F.col("n") < very_rare_n, F.lit("VERY_RARE"))
         .when(F.col("n") < low_freq_n, F.lit("RARE"))
         .when(F.col("n") < min_bucket_n, F.lit("MID_FREQ"))
         .otherwise(F.lit("COMMON"))
    )

    # 4. risk buckets based on multiples of base_rate
    # You can tweak these if you want more granularity
    stats = stats.withColumn(
        "risk_bucket",
        F.when(F.col("bad_rate") >= extreme_risk_cutoff, F.lit("EXTREME"))
         .when(F.col("bad_rate") >= high_risk_cutoff, F.lit("HIGH"))
         .when(F.col("bad_rate") >= 2 * base_rate, F.lit("MODERATE"))
         .when(F.col("bad_rate") >= base_rate, F.lit("SLIGHT"))
         .otherwise(F.lit("BASE_OR_LOWER"))
    )

    # 5. recommended grouping logic
    # - VERY_RARE: always grouped (no standalone)
    # - RARE + high risk: group together as RARE_HIGH_RISK
    # - RARE + not high: group as RARE_OTHER
    # - MID_FREQ / COMMON: keep separate by risk_bucket
    stats = stats.withColumn(
        "recommended_group",
        F.when(F.col("size_band") == "VERY_RARE", F.lit("GROUP_RARE_ULTRA"))
         .when(
             (F.col("size_band").isin("VERY_RARE", "RARE")) &
             (F.col("bad_rate") >= high_risk_cutoff),
             F.lit("GROUP_RARE_HIGH_RISK")
         )
         .when(
             F.col("size_band").isin("VERY_RARE", "RARE"),
             F.lit("GROUP_RARE_OTHER")
         )
         .otherwise(
             # MID_FREQ / COMMON → keep by risk bucket
             F.concat(F.lit("KEEP_"), F.col("risk_bucket"))
         )
    )

    # 6. sort for inspection: most risky & smallest first
    return (
        stats
        .orderBy(F.col("recommended_group"), F.desc("bad_rate"), F.asc("n"))
    )


# EXAMPLE USAGE (adjust names to your columns)
# ------------------------------------------------
# result = suggest_category_groups(
#     df,
#     cat_col="merchant_category",
#     label_col="label",          # 0/1 column
#     very_rare_n=20,
#     low_freq_n=100,
#     min_bucket_n=1000,
#     high_risk_factor=5.0,
#     extreme_risk_factor=10.0,
# )
# result.show(truncate=False)
#
# Now:
# - categories with the same `recommended_group` are the ones you should bucket together
#   (e.g. all `GROUP_RARE_HIGH_RISK` can become one "rare high-risk" bucket in your features)
# - `KEEP_*` rows are frequent enough to keep as standalone dummies/risk levels.

