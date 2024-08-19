from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, FloatType, BooleanType
from pyspark.sql import Row

# Initialize Spark session
spark = SparkSession.builder \
    .appName("Mock DataFrame Example") \
    .getOrCreate()

# Define the schema with at least 20 columns
schema = StructType([
    StructField("id", IntegerType(), nullable=False),
    StructField("name", StringType(), nullable=True),
    StructField("age", IntegerType(), nullable=True),
    StructField("salary", FloatType(), nullable=True),
    StructField("department", StringType(), nullable=True),
    StructField("join_date", StringType(), nullable=True),
    StructField("status", StringType(), nullable=True),
    StructField("gender", StringType(), nullable=True),
    StructField("country", StringType(), nullable=True),
    StructField("state", StringType(), nullable=True),
    StructField("city", StringType(), nullable=True),
    StructField("zip_code", StringType(), nullable=True),
    StructField("email", StringType(), nullable=True),
    StructField("phone_number", StringType(), nullable=True),
    StructField("experience_years", IntegerType(), nullable=True),
    StructField("is_manager", BooleanType(), nullable=True),
    StructField("team_size", IntegerType(), nullable=True),
    StructField("last_promotion_date", StringType(), nullable=True),
    StructField("performance_score", FloatType(), nullable=True),
    StructField("bonus_eligibility", BooleanType(), nullable=True)
])

# Create mock data
data = [
    (1, "John Doe", 28, 60000.0, "Engineering", "2021-05-12", "Active", "M", "USA", "California", "Los Angeles", "90001", "john.doe@example.com", "123-456-7890", 5, True, 10, "2023-04-01", 4.5, True),
    (2, "Jane Smith", 34, 75000.0, "Marketing", "2019-03-22", "Active", "F", "USA", "New York", "New York City", "10001", "jane.smith@example.com", "987-654-3210", 8, False, 5, "2022-03-15", 4.7, False),
    # Add more rows as needed
]

# Create DataFrame
df = spark.createDataFrame(data, schema)

# Show the DataFrame
df.show()
