"""
Python 3.7 compatible example
Recommended versions for Py3.7:
  scikit-learn==1.1.3
  xgboost==1.6.2
  skl2onnx==1.13.0
  onnxmltools==1.11.2
  onnx==1.13.1
  onnxruntime==1.15.1
  pandas<=1.3.x, numpy<=1.21.x (typical Py3.7 pins)

pip install \
  "scikit-learn==1.1.3" "xgboost==1.6.2" "skl2onnx==1.13.0" \
  "onnxmltools==1.11.2" "onnx==1.13.1" "onnxruntime==1.15.1" \
  "pandas==1.3.5" "numpy==1.21.6" "scipy==1.7.3" "joblib==1.2.0"
"""

import json
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import scipy.sparse as sp

from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
from xgboost import XGBClassifier, Booster, DMatrix
import joblib

# -----------------------
# 1) SAMPLE DATA (replace with your own)
# -----------------------
df = pd.DataFrame({
    "gender": ["M", "F", None, "F", None, "M", "F", "M", None, "F"],
    "state":  ["GA", None, "AL", "AL", "GA", None, "GA", "AL", "AL", "GA"],
    "age":    [34, 51, np.nan, 45, 29, 39, 57, 41, 62, 27],
    "income": [85000, 120000, 95000, np.nan, 72000, 99000, 130000, 88000, 110000, 68000],
    "target": [0, 1, 0, 1, 0, 1, 1, 0, 1, 0],
})

X = df.drop(columns=["target"])
y = df["target"].astype(int)

categorical_cols = ["gender", "state"]
numeric_cols = ["age", "income"]

# -----------------------
# 2) PREPROCESSING + MODEL (sklearn Pipeline)
#    - Per-column imputers for categoricals (custom fill values)
#    - Median imputer for numerics
#    - OneHotEncoder with handle_unknown='ignore'
# -----------------------
gender_pipeline = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="constant", fill_value="unknown")),
    ("ohe", OneHotEncoder(handle_unknown="ignore", sparse=True)),
])

state_pipeline = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="constant", fill_value="NA")),
    ("ohe", OneHotEncoder(handle_unknown="ignore", sparse=True)),
])

numeric_pipeline = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="median")),
])

preprocessor = ColumnTransformer(
    transformers=[
        ("gender", gender_pipeline, ["gender"]),
        ("state",  state_pipeline,  ["state"]),
        ("num",    numeric_pipeline, numeric_cols),
    ]
)

xgb = XGBClassifier(
    n_estimators=300,
    max_depth=6,
    learning_rate=0.1,
    subsample=0.8,
    colsample_bytree=0.8,
    reg_lambda=1.0,
    n_jobs=-1,
    random_state=42,
)

model = Pipeline(steps=[
    ("pre", preprocessor),
    ("xgb", xgb),
])

# -----------------------
# 3) TRAIN / EVAL
# -----------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, stratify=y, random_state=42, test_size=0.3
)
model.fit(X_train, y_train)

train_auc = roc_auc_score(y_train, model.predict_proba(X_train)[:, 1])
test_auc  = roc_auc_score(y_test,  model.predict_proba(X_test)[:, 1])

print(f"Train ROC AUC: {train_auc:.4f}")
print(f" Test ROC AUC: {test_auc:.4f}")

# -----------------------
# 4) SAVE ARTIFACTS
#   A) Full sklearn Pipeline (best for Python reproducibility)
#   B) Booster-only JSON (XGBoost recommended format)
#   C) ONNX export of the full pipeline (optional, if conversion succeeds)
#   D) Sidecar schema + feature order for deterministic booster-only serving
# -----------------------

# A) Full sklearn pipeline
joblib.dump(model, "xgb_pipeline.joblib")
print("Saved: xgb_pipeline.joblib")

# B) Booster-only JSON
booster: Booster = model.named_steps["xgb"].get_booster()
booster.save_model("xgb_booster.json")
print("Saved: xgb_booster.json")

# D) Sidecar schema + feature names (for reproducing preprocessing elsewhere)
#    Pull fitted components:
pre = model.named_steps["pre"]
# Access encoders & imputers by the names we gave in ColumnTransformer
enc_gender = pre.named_transformers_["gender"].named_steps["ohe"]
enc_state  = pre.named_transformers_["state"].named_steps["ohe"]
imp_num    = pre.named_transformers_["num"].named_steps["imputer"]

schema = {
    "categorical": {
        "gender": {
            "fill_value": "unknown",
            "categories": [str(c) if c is not None else "None" for c in enc_gender.categories_[0].tolist()]
        },
        "state": {
            "fill_value": "NA",
            "categories": [str(c) if c is not None else "None" for c in enc_state.categories_[0].tolist()]
        }
    },
    "numeric": {
        "columns": numeric_cols,
        "impute_strategy": "median",
        "impute_statistics_": [float(s) if s is not None else None for s in imp_num.statistics_.tolist()],
    },
    "notes": [
        "Input schema/order must match training.",
        "Categoricals must be filled with the listed fill_value before encoding.",
        "OHE order is [gender categories...] + [state categories...] + [numeric columns].",
    ]
}
with open("preprocessing_schema.json", "w") as f:
    json.dump(schema, f, indent=2)
print("Saved: preprocessing_schema.json")

# Build human-readable feature names (helpful for serving/debug)
gender_ohe_names = [f"gender={c}" for c in enc_gender.categories_[0]]
state_ohe_names  = [f"state={c}"  for c in enc_state.categories_[0]]
feature_names_in_training_order = gender_ohe_names + state_ohe_names + numeric_cols

with open("feature_names.txt", "w") as f:
    for name in feature_names_in_training_order:
        f.write(f"{name}\n")
print("Saved: feature_names.txt")

# C) ONNX export of the full pipeline (optional)
#     - Works on Py3.7 with pinned versions above.
#     - If conversion fails in your env, you still have .joblib and booster .json.
onnx_ok = True
try:
    from skl2onnx import convert_sklearn
    from skl2onnx.common.data_types import FloatTensorType, StringTensorType

    initial_types = [
        ("gender", StringTensorType([None, 1])),
        ("state",  StringTensorType([None, 1])),
        ("age",    FloatTensorType([None, 1])),
        ("income", FloatTensorType([None, 1])),
    ]

    onnx_model = convert_sklearn(model, initial_types=initial_types)
    with open("xgb_pipeline.onnx", "wb") as f:
        f.write(onnx_model.SerializeToString())
    print("Saved: xgb_pipeline.onnx")
except Exception as e:
    onnx_ok = False
    print("ONNX pipeline export skipped (conversion error). Reason:")
    print(repr(e))

# -----------------------
# 5) QUICK INFERENCE CHECKS (all three formats)
# -----------------------

# 5A) Python/sklearn pipeline
loaded_pipeline = joblib.load("xgb_pipeline.joblib")
probs_joblib = loaded_pipeline.predict_proba(X_test)[:, 1]
print("joblib pipeline probs (first 5):", np.round(probs_joblib[:5], 4))

# 5B) Booster-only JSON
#     We must feed the *transformed* matrix (imputed + OHE + numeric).
#     Here we reuse the fitted sklearn preprocessor to show the exact matrix.
X_test_matrix = pre.transform(X_test)  # scipy CSR (categoricals OHE + numerics imputed)
if not sp.issparse(X_test_matrix):
    X_test_matrix = sp.csr_matrix(X_test_matrix)

bst2 = Booster()
bst2.load_model("xgb_booster.json")
dtest = DMatrix(X_test_matrix)
probs_json = bst2.predict(dtest)
print("booster JSON probs (first 5):   ", np.round(probs_json[:5], 4))

# 5C) ONNX pipeline (if available)
if onnx_ok:
    try:
        import onnxruntime as ort

        sess = ort.InferenceSession("xgb_pipeline.onnx", providers=["CPUExecutionProvider"])
        # Prepare feeds: each input is a (N, 1) numpy array with the right dtype
        feeds = {
            "gender": X_test[["gender"]].astype(str).values,                 # strings
            "state":  X_test[["state"]].astype(str).values,                  # strings
            "age":    X_test[["age"]].astype(np.float32).values,            # float32
            "income": X_test[["income"]].astype(np.float32).values,         # float32
        }
        outputs = sess.run(None, feeds)
        # Inspect outputs to find probabilities. Many converters output:
        #   - 'output_probability' (prob dict via ZipMap) and/or
        #   - 'probabilities'/'label' arrays
        # We'll just print the names and take the first numeric-looking one.
        out_info = [(o.name, o.shape, o.type) for o in sess.get_outputs()]
        print("ONNX outputs:", out_info)

        # Try to extract a probability vector:
        onnx_probs = None
        for i, arr in enumerate(outputs):
            # Prefer 2D float arrays with shape (N,2) or (N,1)
            if isinstance(arr, np.ndarray) and arr.dtype.kind in ("f", "i", "u"):
                if arr.ndim == 2 and arr.shape[0] == len(X_test):
                    # If (N,2): take column 1 as positive class
                    onnx_probs = arr[:, 1] if arr.shape[1] == 2 else arr.ravel()
                    break
        if onnx_probs is None:
            # Some pipelines export probabilities as a sequence of maps (ZipMap)
            # Try to coerce dict-like outputs if present
            for arr in outputs:
                if isinstance(arr, list) and len(arr) > 0 and isinstance(arr[0], dict):
                    # assume binary with key '1' or 'True'
                    key = "1" if "1" in arr[0] else 1 if 1 in arr[0] else max(arr[0].keys())
                    onnx_probs = np.array([row[key] for row in arr], dtype=np.float32)
                    break

        if onnx_probs is not None:
            print("ONNX pipeline probs (first 5):", np.round(onnx_probs[:5], 4))
        else:
            print("ONNX pipeline: probability output not auto-detected; inspect 'outputs' manually.")
    except Exception as e:
        print("ONNX runtime inference skipped. Reason:", repr(e))

print("\nArtifacts written:")
print(" - xgb_pipeline.joblib       (full sklearn pipeline)")
print(" - xgb_booster.json          (native XGBoost booster, recommended)")
print(" - preprocessing_schema.json (sidecar: categories, imputers, notes)")
print(" - feature_names.txt         (OHE-expanded order)")
print(" - xgb_pipeline.onnx         (optional, if conversion succeeded)")
