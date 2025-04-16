from pyspark.sql import functions as F
from datetime import datetime

DEFAULT_TIMESTAMP = datetime.max
DEFAULT_INT = -1

df = df.withColumns({
    "min_date": F.when(
        F.col("col1").isNull() & F.col("col2").isNull() & F.col("col3").isNull(),
        None
    ).otherwise(
        F.least(
            F.coalesce(F.col("col1"), F.lit(DEFAULT_TIMESTAMP)),
            F.coalesce(F.col("col2"), F.lit(DEFAULT_TIMESTAMP)),
            F.coalesce(F.col("col3"), F.lit(DEFAULT_TIMESTAMP))
        )
    ),
    
    "months_between1": F.floor(F.months_between(F.col("min_date"), F.col("application_date"))),
    
    "months_between2": F.floor(F.months_between(F.col("min_date"), F.col("some_other_date"))),
    
    "max_months_between": F.when(
        F.col("months_between1").isNull() & F.col("months_between2").isNull(),
        None
    ).otherwise(
        F.greatest(
            F.coalesce(F.col("months_between1"), F.lit(DEFAULT_INT)),
            F.coalesce(F.col("months_between2"), F.lit(DEFAULT_INT))
        )
    )
})
