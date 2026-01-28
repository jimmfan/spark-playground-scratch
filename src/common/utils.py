from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, IntegerType, FloatType, StringType, TimestampType

def convert_pandas_to_pyspark(pandas_df):
    # Dynamically import pandas here if pandas is not globally used
    import pandas as pd

    spark = SparkSession.builder.appName("example").getOrCreate()
    
    def _infer_schema(series):
        """ Helper function to infer schema types """
        if pd.api.types.is_integer_dtype(series):
            return IntegerType()
        elif pd.api.types.is_float_dtype(series):
            return FloatType()
        elif pd.api.types.is_datetime64_any_dtype(series):
            return TimestampType()
        else:
            return StringType()

    spark_schema = StructType([StructField(str(c), _infer_schema(pandas_df[c]), True) for c in pandas_df.columns])
    return spark.createDataFrame(pandas_df, schema=spark_schema)

