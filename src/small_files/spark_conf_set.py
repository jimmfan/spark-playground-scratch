from pyspark.sql import SparkSession

# Create a Spark session
spark = SparkSession.builder \
    .appName("Rewriting Hive Table with Specific Settings") \
    .enableHiveSupport() \
    .getOrCreate()

# # Set the Hive and Hadoop configurations
# spark.conf.set("hive.exec.compress.output", "true")
# spark.conf.set("hive.exec.parallel", "true")
# spark.conf.set("parquet.compression", "snappy")
# spark.conf.set("hive.merge.mapfiles", "true")
# spark.conf.set("hive.merge.mapredfiles", "true")
# spark.conf.set("hive.merge.smallfiles.avgsize", "134217728")  # 128MB
# spark.conf.set("hive.merge.size.per.task", "268435456")  # 256MB
# spark.conf.set("hive.optimize.sort.dynamic.partition", "true")
# spark.conf.set("parquet.block.size", "268435456")  # 256MB
# spark.conf.set("dfs.block.size", "268435456")  # 256MB


# Set Hive and Hadoop configurations to handle small files
spark.sql("SET hive.merge.mapfiles=true")
spark.sql("SET hive.merge.mapredfiles=true")
spark.sql("SET hive.merge.smallfiles.avgsize=134217728")  # 128 MB
spark.sql("SET hive.merge.size.per.task=268435456")  # 256 MB

# Compression and block size settings
spark.conf.set("hive.exec.compress.output", "true")  # Compress final output
spark.conf.set("parquet.compression", "snappy")  # Use Snappy compression for Parquet files
spark.conf.set("parquet.block.size", "268435456")  # Set Parquet block size to 256 MB
spark.conf.set("dfs.block.size", "268435456")  # Set HDFS block size to 256 MB

# Enable parallel execution in Hive
spark.conf.set("hive.exec.parallel", "true")  # Parallelize tasks in Hive

# Optimize dynamic partitioning to reduce small file creation
spark.conf.set("hive.optimize.sort.dynamic.partition", "true")

# Enable Adaptive Query Execution (AQE) for dynamic query optimization
spark.conf.set("spark.sql.adaptive.enabled", "true")

# Control the number of records per file to avoid too many small files
spark.conf.set("spark.sql.files.maxRecordsPerFile", 1000000)

# Read the existing Hive table
df = spark.table("your_database.your_table_name")

# Optionally perform some transformations (if needed)
# df = df.withColumn('new_column', df['existing_column'] + 1)

# Write the DataFrame back to Hive, effectively rewriting the table
df.write \
    .mode("overwrite") \
    .format("parquet") \
    .saveAsTable("your_database.your_new_table_name")
