from pyspark.sql.functions import mean, stddev

stats_df1 = df1.select([mean(c).alias(c + '_mean') for c in df1.columns] + 
                       [stddev(c).alias(c + '_stddev') for c in df1.columns])
stats_df2 = df2.select([mean(c).alias(c + '_mean') for c in df2.columns] + 
                       [stddev(c).alias(c + '_stddev') for c in df2.columns])

# This results in DataFrames with one row of stats for each DataFrame.
stats_df1.show()
stats_df2.show()

from pyspark.sql.functions import col, abs, broadcast

# Assuming stats_df1 and stats_df2 each only have one row
stats1 = stats_df1.collect()[0]
stats2 = stats_df2.collect()[0]

def deviations(df, stats, n):
    # n is the number of standard deviations (1, 2, 3)
    return df.select(*[
        ((abs(col(c) - stats[c + '_mean']) / stats[c + '_stddev']) >= n).alias(f'{c}_{n}sd')
        for c in df.columns
    ])

# Example for 1, 2, 3 standard deviations from df1 with respect to df2's stats
df1_1sd = deviations(df1, stats2, 1)
df1_2sd = deviations(df1, stats2, 2)
df1_3sd = deviations(df1, stats2, 3)

df1_1sd.show()
df1_2sd.show()
df1_3sd.show()
