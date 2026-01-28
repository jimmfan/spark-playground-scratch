from pyspark.sql import functions as F
from pyspark.sql.types import MapType, StringType

# Sample DataFrame
data = [("1", '{"oldKey": "value1", "anotherKey": "value2"}')]
df = spark.createDataFrame(data, ["id", "json_col"])

# Parse the JSON column into a MapType
df = df.withColumn("json_map", F.from_json("json_col", MapType(StringType(), StringType())))

# Create a new key with the same value as the old key
df = df.withColumn("json_map", 
                   F.expr("""
                       map_concat(
                           map('newKey', json_map['oldKey']),
                           map_filter(json_map, (k, v) -> k != 'oldKey')
                       )
                   """))

# Convert the map back to a JSON string
df = df.withColumn("json_col", F.to_json("json_map"))

# Show the result
df.select("id", "json_col").show(truncate=False)
