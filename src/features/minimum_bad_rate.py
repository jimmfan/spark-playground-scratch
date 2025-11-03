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
