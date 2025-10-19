from pyspark.sql import functions as F, Window as W

def prep_intervals(dfR, keys, right_date_col):
    w = W.partitionBy(*keys).orderBy(right_date_col)
    return (dfR
        .withColumn("_next", F.lead(right_date_col).over(w))
        .withColumn("_valid_to", F.coalesce(F.col("_next"), F.to_date(F.lit("9999-12-31"))))
        .drop("_next")
    )

R1i = prep_intervals(rates_df,  ["key"], "effective_dt")
R2i = prep_intervals(status_df, ["key"], "status_eff_dt")

j1 = events_df.alias("L").join(
    R1i.alias("R1"),
    on=[
        F.col("L.key")==F.col("R1.key"),
        F.col("L.event_dt")>=F.col("R1.effective_dt"),
        F.col("L.event_dt")< F.col("R1._valid_to"),
    ],
    how="left"
).select("L.*", F.col("R1.rate").alias("rate"), F.col("R1.effective_dt").alias("effective_dt_rate"))

j2 = j1.alias("L").join(
    R2i.alias("R2"),
    on=[
        F.col("L.key")==F.col("R2.key"),
        F.col("L.event_dt")>=F.col("R2.status_eff_dt"),
        F.col("L.event_dt")< F.col("R2._valid_to"),
    ],
    how="left"
).select(
    "L.*",
    F.col("R2.status").alias("status"),
    F.col("R2.status_eff_dt").alias("effective_dt_status"),
)