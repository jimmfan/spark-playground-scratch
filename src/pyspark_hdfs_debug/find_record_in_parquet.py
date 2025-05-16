from pyspark.sql.functions import input_file_name
import subprocess

# ---- Config ----
table_path = "hdfs:/warehouse/tablespace/managed/hive/db.db/your_table"
partition_col = "event_date"
partition_prefix = "event_date="  # adjust if needed
compare_cols = ["id", "event_date"]  # columns to compare

# ---- Step 1: List root-level .parquet files (excluding partitions) ----
cmd = ["hdfs", "dfs", "-ls", table_path]
output = subprocess.check_output(cmd, universal_newlines=True)  # for Python 3.6

root_files = [
    line.split()[-1]
    for line in output.strip().split("\n")
    if "part-" in line and ".parquet" in line and ("/" + partition_prefix) not in line
]

# ---- Step 2: Read only root .parquet files ----
if root_files:
    df_root = spark.read.parquet(*root_files).withColumn("source_root", input_file_name())
    print("✅ Loaded {} rows from root files".format(df_root.count()))
else:
    print("❌ No root-level .parquet files found.")
    df_root = None

# ---- Step 3: Read partitioned data ----
df_part = spark.read.parquet("{}/{}*/".format(table_path, partition_prefix)) \
    .withColumn("source_part", input_file_name())
print("✅ Loaded {} rows from partitioned folders".format(df_part.count()))

# ---- Step 4: Compare by join keys ----
if df_root:
    df_duplicates = df_root.alias("root").join(
        df_part.alias("part"),
        on=compare_cols,
        how="inner"
    )

    print("⚠️ Found {} rows duplicated across root and partitions".format(df_duplicates.count()))
    df_duplicates.select("source_root", "source_part", *compare_cols).show(truncate=False)
else:
    print("✅ No root files to compare, skipping join.")
