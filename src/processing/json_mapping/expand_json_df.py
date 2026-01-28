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


from pyspark.sql import DataFrame
from pyspark.sql.functions import col, get_json_object, collect_list, udf
from pyspark.sql.types import StringType
import json

def expand_json_column(df: DataFrame, json_col: str, id_col: str) -> DataFrame:
    # Combine JSON values for each id into a single JSON object
    @udf(StringType())
    def combine_json(json_list):
        combined_dict = {}
        for json_str in json_list:
            combined_dict.update(json.loads(json_str))
        return json.dumps(combined_dict)

    # Group by id and combine JSON columns
    df_combined = df.groupBy(id_col).agg(combine_json(collect_list(json_col)).alias("combined_json"))

    # Extract a sample JSON to determine the keys (assuming all possible keys are present in the sample)
    sample_json = json.loads(df_combined.select("combined_json").first()[0])
    keys = sample_json.keys()

    # Generate select expressions using get_json_object for each key
    select_exprs = [col(id_col)] + [get_json_object(col("combined_json"), f"$.{key}").alias(key) for key in keys]

    # Select the columns
    df_final = df_combined.select(*select_exprs)
    
    return df_final

# Sample usage
data = [
    (1, "{\"key1\":\"value1\", \"key2\":\"value2\"}"),
    (1, "{\"key1\":\"value3\", \"key3\":\"value4\"}"),
    (2, "{\"key2\":\"value5\", \"key4\":\"value6\"}")
]

# Create DataFrame
df = spark.createDataFrame(data, ["id", "json_column"])

# Call the function
df_expanded = expand_json_column(df, "json_column", "id")

# Show the result
df_expanded.show(truncate=False)
