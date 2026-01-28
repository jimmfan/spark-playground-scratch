import jaydebeapi
from pyspark.sql import SparkSession, StructType, StructField
from pyspark.sql.types import *

# Initialize SparkSession
spark = SparkSession.builder.appName("SQLServerToSparkDF").getOrCreate()

# Connect to your SQL Server database
conn = jaydebeapi.connect("jdbc_driver_class_name", "jdbc:sqlserver://your_server:your_port;databaseName=your_db", ["your_username", "your_password"], "path/to/jdbc/driver.jar")

def sql_to_spark_type(sql_type):
    """Map SQL Server data types to Spark data types."""
    return {
        "int": IntegerType(),
        "smallint": ShortType(),
        "tinyint": ByteType(),
        "bigint": LongType(),
        "float": FloatType(),
        "real": DoubleType(),
        "numeric": DecimalType(),
        "decimal": DecimalType(),
        "char": StringType(),
        "varchar": StringType(),
        "text": StringType(),
        "nchar": StringType(),
        "nvarchar": StringType(),
        "ntext": StringType(),
        "date": DateType(),
        "datetime": TimestampType(),
        "datetime2": TimestampType(),
        "timestamp": TimestampType(),
        "time": StringType(),  # Spark does not have a specific type for Time alone
        "bit": BooleanType()
    }.get(sql_type.lower(), StringType())  # Default to StringType for unknown types

try:
    cursor = conn.cursor()
    # Replace YOUR_TABLE_NAME with your actual table name
    cursor.execute("SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'YOUR_TABLE_NAME'")
    columns_info = cursor.fetchall()
    
    # Map SQL Server types to Spark types and build schema
    schema_fields = [StructField(col_name, sql_to_spark_type(data_type), True) for col_name, data_type in columns_info]
    schema = StructType(schema_fields)
    
    # Now you can use this schema with Spark to read data from SQL Server directly or apply it to existing data
    # For example, to read data directly:
    # df = spark.read.format("jdbc").option("url", "jdbc:sqlserver://your_server:your_port;databaseName=your_db")\
    #     .option("dbtable", "YOUR_TABLE_NAME").option("user", "your_username").option("password", "your_password")\
    #     .option("driver", "jdbc_driver_class_name").load(schema=schema)

finally:
    cursor.close()
    conn.close()
