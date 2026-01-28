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

# Function to convert a value to the inferred Spark SQL data type
def convert_value(value, data_type):
    if value is None:
        return None
    try:
        if isinstance(data_type, IntegerType):
            return int(value)
        elif isinstance(data_type, DoubleType):
            return float(value)
        elif isinstance(data_type, StringType):
            return str(value)
        elif isinstance(data_type, BooleanType):
            return bool(value)
        elif isinstance(data_type, TimestampType):
            if isinstance(value, datetime.datetime):
                return value
            else:
                return datetime.datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
        else:
            return str(value)
    except (ValueError, TypeError):
        return None

# Preprocess the data to match the inferred schema
processed_data = [
    tuple(convert_value(row[i], schema[i].dataType) for i in range(len(row)))
    for row in data
]

# Create DataFrame
df = spark.createDataFrame(processed_data, schema)

