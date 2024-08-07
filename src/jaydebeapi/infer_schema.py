import jaydebeapi
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType, TimestampType, BooleanType
import datetime

# Define a function to infer Spark SQL data types
def infer_spark_dtype(value):
    if value is None:
        return None  # Return None for NoneType to continue checking
    elif isinstance(value, int):
        return IntegerType()
    elif isinstance(value, float):
        return DoubleType()
    elif isinstance(value, str):
        return StringType()
    elif isinstance(value, bool):
        return BooleanType()
    elif isinstance(value, datetime.datetime):
        return TimestampType()
    else:
        return None  # Return None if type is unknown

# Helper function to get the type for a column
def get_column_type(data, column_index, max_rows=10):
    for row in data[:max_rows]:
        inferred_type = infer_spark_dtype(row[column_index])
        if inferred_type is not None:
            return inferred_type
    return StringType()  # Default to StringType if no type could be inferred

# Infer schema from the first 10 rows of data
schema = StructType([
    StructField(column_names[i], get_column_type(data, i), True)
    for i in range(len(column_names))
])
