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
    very_high_factor=10.0,
    extreme_risk_factor=20.0,
):
    """
    Suggest grouping for categorical values in `cat_col` based on:
    - event rate in `label_col`
    - frequency (count)
    - relative risk vs baseline (multiples of base_rate)

    Returns a DataFrame with:
        [cat_col, n, bad_rate, size_band, risk_bucket, recommended_group]
    """

    # 1. Compute base event rate if not provided
    if base_rate is None:
        base_rate = df.agg(F.avg(label_col)).collect()[0][0]

    high_risk_cutoff      = base_rate * high_risk_factor      # e.g. 5x base
    very_high_risk_cutoff = base_rate * very_high_factor      # e.g. 10x base
    extreme_risk_cutoff   = base_rate * extreme_risk_factor   # e.g. 20x base

    # 2. Per-category stats
    stats = (
        df.groupBy(cat_col)
          .agg(
              F.count("*").alias("n"),
              F.avg(label_col).alias("bad_rate")
          )
    )

    # 3. Size bands based on frequency
    stats = stats.withColumn(
        "size_band",
        F.when(F.col("n") < very_rare_n, F.lit("VERY_RARE"))
         .when(F.col("n") < low_freq_n, F.lit("RARE"))
         .when(F.col("n") < min_bucket_n, F.lit("MID_FREQ"))
         .otherwise(F.lit("COMMON"))
    )

    # 4. Risk buckets based on multiples of base_rate
    stats = stats.withColumn(
        "risk_bucket",
        F.when(F.col("bad_rate") >= extreme_risk_cutoff,   F.lit("EXTREME"))
         .when(F.col("bad_rate") >= very_high_risk_cutoff, F.lit("VERY_HIGH"))
         .when(F.col("bad_rate") >= high_risk_cutoff,      F.lit("HIGH"))
         .when(F.col("bad_rate") >= 2 * base_rate,         F.lit("MODERATE"))
         .when(F.col("bad_rate") >= base_rate,             F.lit("SLIGHT"))
         .otherwise(F.lit("BASE_OR_LOWER"))
    )

    # 5. Recommended grouping logic
    # - VERY_RARE: always grouped
    # - RARE + high/very_high/extreme risk: group together as RARE_HIGH_RISK
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

    return (
        stats
        .orderBy(F.col("recommended_group"), F.desc("bad_rate"), F.asc("n"))
    )