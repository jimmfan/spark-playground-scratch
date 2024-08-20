from pyspark.sql import functions as F
from pyspark.sql.types import MapType, StringType

# Sample DataFrame
data = [("1", '{"oldKey": "value1", "anotherKey": "value2"}')]
df = spark.createDataFrame(data, ["id", "json_col"])

# Parse the JSON column into a MapType
df = df.withColumn("json_map", F.from_json("json_col", MapType(StringType(), StringType())))

# Rename the key by creating a new key-value pair and dropping the old one
df = df.withColumn("json_map", 
                   F.create_map(F.lit('newKey'), F.col('json_map')['oldKey'])
                   .alias("newKey") 
                   .withField("anotherKey", F.col("json_map")["anotherKey"]))

# Convert the map back to a JSON string
df = df.withColumn("json_col", F.to_json("json_map"))

# Show the result
df.select("id", "json_col").show(truncate=False)
