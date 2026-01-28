# pip install "scikit-learn==1.1.3" "xgboost==1.6.2" "skl2onnx==1.13.0" \
#             "onnxmltools==1.11.2" "onnx==1.13.1" "onnxruntime==1.15.1" \
#             "pandas==1.3.5" "numpy==1.21.6"

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier

# -----------------------
# Data (example)
# -----------------------
df = pd.DataFrame({
    "gender": ["M", "F", None, "F", None, "M"],
    "state": ["GA", None, "AL", "AL", "GA", None],
    "age": [34, 51, np.nan, 45, 29, 39],
    "income": [85000, 120000, 95000, np.nan, 72000, 99000],
    "target": [0, 1, 0, 1, 0, 1],
})
X = df.drop(columns=["target"])
y = df["target"].astype(int)

categorical_cols = ["gender", "state"]
numeric_cols = ["age", "income"]

# -----------------------
# Option 1: No categorical imputer; OHE will treat NaN as a category
# -----------------------
cat_pipe = Pipeline([
    ("ohe", OneHotEncoder(handle_unknown="ignore", sparse=False))  # NaN becomes its own category
])

num_pipe = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),  # numeric imputer is fine
])

pre = ColumnTransformer([
    ("cat", cat_pipe, categorical_cols),
    ("num", num_pipe, numeric_cols),
])

model = Pipeline([
    ("pre", pre),
    ("xgb", XGBClassifier(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        reg_lambda=1.0,
        n_jobs=-1,
        random_state=42,
    ))
])

X_train, X_test, y_train, y_test = train_test_split(X, y, stratify=y, random_state=42)
model.fit(X_train, y_train)

# -----------------------
# ONNX: Register XGBoost converters before convert_sklearn()
# -----------------------
from skl2onnx import convert_sklearn, update_registered_converter
from skl2onnx.common.data_types import FloatTensorType, StringTensorType

# Register the XGBClassifier converter & shape calculator
from onnxmltools.convert.xgboost.operator_converters.XGBoost import convert_xgboost
from onnxmltools.convert.xgboost.shape_calculators.Classifier import (
    calculate_xgboost_classifier_output_shapes
)
update_registered_converter(
    XGBClassifier, "XGBoostXGBClassifier",
    calculate_xgboost_classifier_output_shapes, convert_xgboost
)

# Build initial_types from raw inputs (one entry per raw column)
initial_types = [
    ("gender", StringTensorType([None, 1])),
    ("state",  StringTensorType([None, 1])),
    ("age",    FloatTensorType([None, 1])),
    ("income", FloatTensorType([None, 1])),
]

# Convert; target_opset 12–15 works well with these versions; disable zipmap for simpler outputs
onnx_model = convert_sklearn(
    model,
    initial_types=initial_types,
    target_opset=12,
    options={id(model): {"zipmap": False}}  # optional: return raw probabilities as a 2D array
)

with open("xgb_pipeline.onnx", "wb") as f:
    f.write(onnx_model.SerializeToString())

print("Saved ONNX: xgb_pipeline.onnx")

# -----------------------
# Sanity check with ONNX Runtime
# -----------------------
import onnxruntime as ort

sess = ort.InferenceSession("xgb_pipeline.onnx", providers=["CPUExecutionProvider"])
# Prepare inputs (categoricals as strings; numerics float32). Leave NaNs as-is.
feeds = {
    "gender": X_test[["gender"]].astype(str).values,
    "state":  X_test[["state"]].astype(str).values,
    "age":    X_test[["age"]].astype(np.float32).values,
    "income": X_test[["income"]].astype(np.float32).values,
}
onnx_outputs = sess.run(None, feeds)

# If zipmap=False, onnx_outputs[1] is usually the probability array (N,2)
# Find it robustly:
probs = None
for out in onnx_outputs:
    if isinstance(out, np.ndarray) and out.ndim == 2 and out.shape[0] == len(X_test):
        probs = out
        break

print("ONNX probs (first 5):", np.round(probs[:5, 1], 6) if probs is not None else "inspect outputs")
print("sklearn probs (first 5):", np.round(model.predict_proba(X_test)[:5, 1], 6))


## Feeds helper
import numpy as np
import pandas as pd
import onnxruntime as ort

def make_onnx_feeds(df: pd.DataFrame, session: ort.InferenceSession):
    """
    Build an ONNX Runtime feed dictionary automatically from a pandas DataFrame
    and an InferenceSession (so we know the expected input names and types).

    - Numeric ONNX inputs → float32
    - String ONNX inputs  → str
    """
    feeds = {}
    for inp in session.get_inputs():
        name = inp.name
        onnx_type = inp.type.lower()

        # Fallback: pick matching column (case-insensitive)
        col = next((c for c in df.columns if c.lower() == name.lower()), None)
        if col is None:
            raise KeyError(f"No column found in DataFrame for ONNX input '{name}'")

        arr = df[[col]].values
        if "float" in onnx_type or "double" in onnx_type:
            arr = arr.astype(np.float32)
        else:
            arr = arr.astype(str)
        feeds[name] = arr
    return feeds
