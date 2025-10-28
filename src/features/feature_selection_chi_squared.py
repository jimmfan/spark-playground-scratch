# ============================================================
# FULL EXAMPLE: Top-K one-hot encoding + Chi-square feature test
# ============================================================

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.ml import Pipeline
from pyspark.ml.feature import StringIndexer, OneHotEncoderEstimator, VectorAssembler
from pyspark.ml.stat import ChiSquareTest
import pandas as pd

# ------------------------------------------------------------
# Step 0. Create Spark session and sample data
# ------------------------------------------------------------
spark = SparkSession.builder.appName("ChiSquareExample").getOrCreate()

data = [
    ("grocery", 45, 120.0, 0),
    ("grocery", 51,  80.0, 0),
    ("gas",     38,  40.0, 0),
    ("online",  27, 300.0, 1),
    ("grocery", 60,  20.0, 0),
    ("gas",     41,  50.0, 0),
    ("gas",     43,  70.0, 0),
    ("luxury",  55, 1000.0,1),
    ("luxury",  58,  900.0,1),
    ("grocery", 49,  60.0, 0),
    ("online",  33, 500.0, 1),
]

df = spark.createDataFrame(data, ["merchant_category", "age", "amount", "label"])

# ------------------------------------------------------------
# Step 1. Keep only top-K categories, bucket others as "OTHER"
# ------------------------------------------------------------
cat_col = "merchant_category"
filtered_col = cat_col + "_filtered"
k = 2  # top-2 categories

topk_list = [
    row[cat_col]
    for row in (
        df.groupBy(cat_col)
          .count()
          .orderBy(F.desc("count"))
          .limit(k)
          .collect()
    )
]
print("Top-K categories:", topk_list)

df2 = df.withColumn(
    filtered_col,
    F.when(F.col(cat_col).isin(topk_list), F.col(cat_col)).otherwise(F.lit("OTHER"))
)

# ------------------------------------------------------------
# Step 2. Build pipeline: index + one-hot + assemble
# ------------------------------------------------------------
indexer = StringIndexer(
    inputCol=filtered_col,
    outputCol=filtered_col + "_idx",
    handleInvalid="keep"
)

ohe = OneHotEncoderEstimator(
    inputCols=[filtered_col + "_idx"],
    outputCols=[filtered_col + "_oh"],
    dropLast=False
)

numeric_cols = ["age", "amount"]

assembler = VectorAssembler(
    inputCols=[filtered_col + "_oh"] + numeric_cols,
    outputCol="features"
)

pipeline = Pipeline(stages=[indexer, ohe, assembler])
fitted = pipeline.fit(df2)
ready_df = fitted.transform(df2)

# ------------------------------------------------------------
# Step 3. Run Chi-square test
# ------------------------------------------------------------
chi = ChiSquareTest.test(ready_df, "features", "label").head()

# ------------------------------------------------------------
# Step 4. Map back vector positions -> feature names
# ------------------------------------------------------------
fitted_indexer = fitted.stages[0]
indexer_labels = fitted_indexer.labels  # order of categories
cat_feature_names = [
    f"{filtered_col}=={cat}" for cat in indexer_labels
]
all_feature_names = cat_feature_names + numeric_cols

# ------------------------------------------------------------
# Step 5. Combine into readable DataFrame
# ------------------------------------------------------------
results_df = pd.DataFrame({
    "feature": all_feature_names,
    "chi2_stat": chi.statistics,
    "p_value": chi.pValues,
    "df": chi.degreesOfFreedom
}).sort_values("p_value")

print("\n=== Chi-square feature significance ===")
print(results_df)

# ------------------------------------------------------------
# Optional: inspect
# ------------------------------------------------------------
ready_df.select(filtered_col, filtered_col + "_oh", "features", "label").show(truncate=False)
# Spark is always right about how many features actually exist
true_len = len(chi.pValues)

# If the number of labels from the StringIndexer doesn't match,
# rebuild feature names from that true length
if len(indexer_labels) != true_len:
    print(f"Adjusting names: indexer_labels={len(indexer_labels)}, true={true_len}")
    # Spark dropped or added a bucket (often 'OTHER' or baseline)
    # Just make generic names to align lengths safely
    cat_feature_names = [f"{filtered_col}=={lbl}" for lbl in indexer_labels[:true_len]]
    while len(cat_feature_names) < true_len:
        cat_feature_names.append(f"{filtered_col}==<EXTRA>")
else:
    cat_feature_names = [f"{filtered_col}=={lbl}" for lbl in indexer_labels]

results_df = pd.DataFrame({
    "feature": cat_feature_names,
    "chi2_stat": chi.statistics,
    "p_value": chi.pValues,
    "df": chi.degreesOfFreedom
}).sort_values("p_value")


