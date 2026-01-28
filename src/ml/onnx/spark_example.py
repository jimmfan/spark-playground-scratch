# ====== DRIVER SETUP ======
# 1) Point this to the path you copied from HUE (absolute HDFS path).
#    Use either "hdfs:///user/you/models/model.onnx" (default namenode)
#    or "hdfs://namenode:8020/user/you/models/model.onnx" (explicit).
onnx_hdfs_path = "hdfs:///user/you/models/my_model.onnx"

# 2) The feature columns in the EXACT order used to train the model.
feature_cols = ["f1", "f2", "f3"]  # <- replace with your real columns

# 3) (Optional) For multiclass, which class prob do you want? For binary, 1 is typical.
TARGET_PROB_INDEX = 1

# 4) Distribute the ONNX file to executors via SparkFiles.
spark.sparkContext.addFile(onnx_hdfs_path)

# 5) Enable Arrow (important for Pandas UDF speed in Spark 2.4).
spark.conf.set("spark.sql.execution.arrow.enabled", "true")

# ====== PANDAS UDF SCORER (Spark 2.4 style) ======
import pandas as pd
import numpy as np
from pyspark.sql.types import DoubleType
from pyspark.sql.functions import pandas_udf, PandasUDFType

# We'll lazy-init the ONNX session once per Python worker (executor process).
_ORT_SESSION = None
_INPUT_NAME = None

def _get_onnx_session():
    """Load the ONNX model once per worker from the SparkFiles cache."""
    global _ORT_SESSION, _INPUT_NAME
    if _ORT_SESSION is None:
        from pyspark import SparkFiles
        import onnxruntime as ort

        model_local_path = SparkFiles.get("my_model.onnx")  # basename from HDFS path
        # Create an inference session
        so = ort.SessionOptions()
        sess = ort.InferenceSession(model_local_path, so, providers=["CPUExecutionProvider"])
        # Detect the input name (varies by exporter)
        input_name = sess.get_inputs()[0].name

        _ORT_SESSION = sess
        _INPUT_NAME = input_name
    return _ORT_SESSION, _INPUT_NAME

@pandas_udf(DoubleType(), PandasUDFType.SCALAR)
def score_onnx(*cols: pd.Series) -> pd.Series:
    """
    Vectorized scorer:
    - Concats incoming columns into a float32 numpy array
    - Runs ONNX session
    - Returns class-1 prob for binary, or TARGET_PROB_INDEX for multiclass
    """
    sess, input_name = _get_onnx_session()

    # Assemble features in the SAME order as training
    X = pd.concat(cols, axis=1).astype("float32").to_numpy()

    # Run inference; output can vary by converter (single prob, logits, or probs matrix)
    outputs = sess.run(None, {input_name: X})
    # Common patterns:
    #  - [0] is probabilities with shape (n, 1) for binary
    #  - or (n, 2) for binary with both classes
    #  - or (n, K) for multiclass
    probs = outputs[0]

    # Normalize to a 1D prob-of-positive series
    if probs.ndim == 1:
        # Already 1D: assume it's the positive class probability
        p = probs
    else:
        # 2D: choose column
        n_classes = probs.shape[1]
        col = TARGET_PROB_INDEX if TARGET_PROB_INDEX < n_classes else min(1, n_classes - 1)
        p = probs[:, col]

    # Ensure float64 Series for Spark DoubleType
    return pd.Series(p.astype("float64"))

# ====== APPLY SCORING ======
# Use *exact* feature order!
df_scored = df.withColumn("score", score_onnx(*[df[c] for c in feature_cols]))

# (Optional) Quick sanity check
df_scored.select("score").show(10, truncate=False)



## Option 2
from pyspark.sql.functions import udf
from pyspark.sql.types import DoubleType
import onnxruntime as ort
import numpy as np

# Initialize ONNX session once
sess = ort.InferenceSession("/path/to/model.onnx")
input_name = sess.get_inputs()[0].name

def score_row(*cols):
    X = np.array([cols], dtype="float32")
    probs = sess.run(None, {input_name: X})[0]
    return float(probs[0][1])  # for binary
score_udf = udf(score_row, DoubleType())

df_scored = df.withColumn("score", score_udf("f1", "f2", "f3"))


# Option 3

from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, LongType, DoubleType
import numpy as np

onnx_hdfs_path = "hdfs:///user/you/models/my_model.onnx"
feature_cols = ["f1","f2","f3"]
TARGET_PROB_INDEX = 1

spark.sparkContext.addFile(onnx_hdfs_path)

# Add a stable row id to re-join scores
df_idx = df.withColumn("_row_id", F.monotonically_increasing_id())
feat_df = df_idx.select("_row_id", *[F.col(c) for c in feature_cols])

def score_partition(rows_iter):
    # Runs on executor; safe to import and create session here
    from pyspark import SparkFiles
    import onnxruntime as ort

    model_path = SparkFiles.get("my_model.onnx")
    sess = ort.InferenceSession(model_path, providers=["CPUExecutionProvider"])
    input_name = sess.get_inputs()[0].name

    for row in rows_iter:
        # row is a pyspark.sql.Row
        rid = row["_row_id"]
        vals = [row[c] for c in feature_cols]
        X = np.array([vals], dtype="float32")
        out = sess.run(None, {input_name: X})[0]
        if out.ndim == 1:
            p = float(out[0])
        else:
            idx = TARGET_PROB_INDEX if TARGET_PROB_INDEX < out.shape[1] else min(1, out.shape[1]-1)
            p = float(out[0, idx])
        yield (rid, p)

scores_rdd = feat_df.rdd.mapPartitions(score_partition)

scores_schema = StructType([
    StructField("_row_id", LongType(), False),
    StructField("score", DoubleType(), True),
])
scores_df = spark.createDataFrame(scores_rdd, scores_schema)

df_scored = (
    df_idx.join(scores_df, on="_row_id", how="inner")
          .drop("_row_id")
)

# sanity check
df_scored.select("score").show(10, truncate=False)


# Option 4:
# In a CDSW terminal or notebook "!" cell
# python3 -m venv /tmp/spark24_env
# /tmp/spark24_env/bin/pip install -U pip
# /tmp/onnxrt_env/bin/pip install "pyarrow==0.15.1" "pandas==0.25.3" "onnxruntime==1.14.1"

# # Pack it so Spark can distribute it to executors
# cd /tmp && tar -czf spark24_env.tar.gz spark24_env


# hdfs dfs -mkdir -p /user/$USER/deps
# hdfs dfs -put -f /tmp/spark24_env.tar.gz /user/$USER/deps/


## Debug

def probe_pyarrow():
    try:
        import pyarrow, pandas, sys
        return f"OK: pyarrow={pyarrow.__version__}, pandas={pandas.__version__}, python={sys.version.split()[0]}"
    except Exception as e:
        import traceback
        return f"ERROR: {repr(e)}\n{traceback.format_exc()}"

# Driver check
print("Driver:", probe_pyarrow())

# Executor check (run on workers)
print("Executors:", spark.range(1).rdd.map(lambda _: probe_pyarrow()).collect())

## Another option
from pyspark import SparkFiles

# Add the ONNX model to Spark job
spark.sparkContext.addFile("hdfs:///models/mymodel.onnx")

# Inside UDF / executor:
import onnxruntime as ort

def load_onnx_session():
    local_path = SparkFiles.get("mymodel.onnx")
    return ort.InferenceSession(local_path)

from pyspark.sql.functions import udf
from pyspark.sql.types import DoubleType

# Executor-local cache
_onnx_sess = None

def predict_proba_udf(*cols):
    global _onnx_sess
    if _onnx_sess is None:
        _onnx_sess = load_onnx_session()
    X = [[float(c) if c is not None else 0.0 for c in cols]]
    inputs = { _onnx_sess.get_inputs()[0].name: X }
    preds = _onnx_sess.run(None, inputs)[0]
    return float(preds[0][1])

score_udf = udf(predict_proba_udf, DoubleType())
df_scored = df.withColumn("score", score_udf("f1", "f2", "f3"))


