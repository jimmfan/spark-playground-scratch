# Find columns with all null values
null_counts = df.select([((col(c).isNull()).cast("int")).alias(c) for c in df.columns])
agg_exprs = [(1 - max(col(c))).alias(c) for c in df.columns]
cols_to_drop = [c for c, v in null_counts.agg(*agg_exprs).first().asDict().items() if v == 0]

# Drop the columns
df_cleaned = df.drop(*cols_to_drop)

df_cleaned.show()
