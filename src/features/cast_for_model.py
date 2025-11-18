import pyspark.sql.functions as F
from pyspark.sql import DataFrame

def cast_for_model(df: DataFrame, feat_cfg: dict) -> DataFrame:
    """
    Use features.yaml to cast Spark columns to stable types
    before df.toPandas().
    """
    for f in feat_cfg["features"]:
        name = f["name"]
        expected = f["expected_dtype"]

        if expected in ("float32", "float64"):
            df = df.withColumn(name, F.col(name).cast("double"))
        elif expected in ("int32", "int64"):
            df = df.withColumn(name, F.col(name).cast("bigint"))
        elif expected == "string":
            df = df.withColumn(name, F.col(name).cast("string"))
        else:
            raise ValueError(f"Unsupported expected_dtype={expected} for {name}")

    return df

# usage
spark_df = cast_for_model(spark_df, feat_cfg)
pdf = spark_df.toPandas()
