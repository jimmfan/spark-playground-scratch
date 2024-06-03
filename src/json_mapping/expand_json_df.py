from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, expr
from pyspark.sql.types import MapType, StringType

# Initialize Spark session
spark = SparkSession.builder.appName("JsonExplodeExample").getOrCreate()

# Sample data
data = [
    ("{\"key1\":\"value1\", \"key2\":\"value2\"}",),
    ("{\"key1\":\"value3\", \"key3\":\"value4\"}",)
]

# Create DataFrame
df = spark.createDataFrame(data, ["json_column"])

# Define the schema as a MapType
schema = MapType(StringType(), StringType())

# Parse the JSON column
df_parsed = df.withColumn("json_map", from_json(col("json_column"), schema))

# Extract keys
keys = df_parsed.selectExpr("map_keys(json_map) as keys").rdd.flatMap(lambda x: x).collect()

# Generate select expressions
select_exprs = [f"json_map['{key}'] as {key}" for key in keys]

# Select the columns
df_final = df_parsed.select(col("json_column"), expr(f"named_struct({', '.join(select_exprs)}) as json_struct"))

# Explode the struct fields into separate columns
df_final = df_final.select("json_column", "json_struct.*")

# Show the final DataFrame
df_final.show(truncate=False)
