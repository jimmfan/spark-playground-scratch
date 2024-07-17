from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sequence, to_date
from pyspark.sql.types import DateType
from datetime import datetime, timedelta

# Create a SparkSession
spark = SparkSession.builder.appName("Last3MonthsDates").getOrCreate()

# Calculate the start and end dates
end_date = datetime.now().date()
start_date = end_date - timedelta(days=90)

# Create a list of dates from start_date to end_date
date_list = [(start_date + timedelta(days=i)).isoformat() for i in range((end_date - start_date).days + 1)]

# Create a DataFrame with the list of dates
dates_df = spark.createDataFrame(date_list, DateType()).toDF("business_dt")

# Show the result
dates_df.show(truncate=False)

# Stop the SparkSession
spark.stop()
