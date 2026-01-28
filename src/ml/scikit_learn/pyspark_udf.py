import pandas as pd
from pyspark.sql.functions import pandas_udf, PandasUDFType
from pyspark.sql.types import DoubleType

@pandas_udf(DoubleType(), PandasUDFType.SCALAR)
def predict_proba_pandas_udf(*cols: pd.Series) -> pd.Series:
    X = pd.concat(cols, axis=1).to_numpy()
    return pd.Series(bc_model.value.predict_proba(X)[:, 1])

df_scored = df.withColumn("score", predict_proba_pandas_udf("f1", "f2", "f3"))
