# ================================
# File: src/credit_model/features/masking.py
# ================================
import pandas as pd

def apply_conditional_mask(
    df: pd.DataFrame,
    condition_col: str,
    keep_values,
    cols_to_mask,
):
    out = df.copy()
    mask = ~out[condition_col].isin(keep_values)
    for col in cols_to_mask:
        out.loc[mask, col] = None
    return out



# ================================
# File: src/credit_model/features/ohe.py
# ================================
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder


def make_ohe(sparse: bool = False, dtype: str = "float32") -> OneHotEncoder:
    """
    Factory for OneHotEncoder so you can centralize config.
    """
    return OneHotEncoder(
        handle_unknown="ignore",  # critical for stability in prod
        sparse=sparse,
        dtype=dtype,
    )


def build_ohe_preprocessor(
    categorical_cols,
    numeric_cols,
    sparse: bool = False,
    dtype: str = "float32",
) -> ColumnTransformer:
    """
    ColumnTransformer that:
      - applies OHE to categorical_cols
      - passes numeric_cols through
      - drops everything else (e.g. hit_type)
    """
    ohe = make_ohe(sparse=sparse, dtype=dtype)

    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", ohe, list(categorical_cols)),
            ("num", "passthrough", list(numeric_cols)),
        ],
        remainder="drop",
    )
    return preprocessor


# ================================
# File: src/credit_model/model/train_xgb_pipeline.py
# ================================
from pathlib import Path
from typing import Any, Dict

import joblib
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from xgboost import XGBClassifier

from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType, StringTensorType

from credit_model.features.masking import apply_conditional_mask
from credit_model.features.ohe import build_ohe_preprocessor


def get_project_root() -> Path:
    """
    Resolve repo root based on this file's location.

    Assumes:
      repo_root/
        src/
          credit_model/
            model/
              train_xgb_pipeline.py  <-- this file

    So repo_root = parents[3].
    """
    return Path(__file__).resolve().parents[3]


def build_xgb_model(params: Dict[str, Any]) -> XGBClassifier:
    """
    XGBClassifier factory with stable defaults.
    """
    defaults = {
        "n_estimators": 300,
        "learning_rate": 0.05,
        "max_depth": 4,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "reg_lambda": 2.0,
        "objective": "binary:logistic",
        "tree_method": "hist",
        "n_jobs": -1,
        "random_state": 42,
        "eval_metric": "logloss",
    }
    defaults.update(params or {})
    return XGBClassifier(**defaults)


def build_pipeline_for_onnx(preprocessor, model) -> Pipeline:
    """
    Pipeline whose ONNX graph will contain:

      - preprocess: ColumnTransformer(OneHotEncoder + numeric passthrough)
      - model: XGBClassifier
    """
    return Pipeline(
        steps=[
            ("preprocess", preprocessor),
            ("model", model),
        ]
    )


def train_and_export_with_ohe_in_onnx(
    df: pd.DataFrame,
    model_cfg: Dict[str, Any],
) -> None:
    """
    Train and export a pipeline where ONNX contains OHE + XGB.

    Workflow:

      1. Mask categorical features based on hit_type (outside pipeline).
      2. Fit ColumnTransformer (OHE + numeric passthrough) on masked data.
      3. Transform to numeric matrix (float32).
      4. Fit XGBClassifier.
      5. Wrap preprocessor + model into a Pipeline.
      6. Save Pipeline as joblib.
      7. Convert Pipeline to ONNX (includes OHE + XGB).

    `model_cfg` is the `model` section from model.yaml.
    """

    # --- unpack config ---
    target = model_cfg["target"]

    columns_cfg = model_cfg["columns"]
    categorical_cols = columns_cfg["categorical"]
    numeric_cols = columns_cfg["numeric"]
    hit_type_col = columns_cfg["hit_type"]

    masking_cfg = model_cfg["masking"]
    keep_hit_types = masking_cfg["allowed_hit_types"]

    ohe_cfg = model_cfg["preprocessing"]["ohe"]
    ohe_sparse = ohe_cfg["sparse"]
    ohe_dtype = ohe_cfg["dtype"]

    algo_params = model_cfg["algorithm"]["params"]

    export_cfg = model_cfg["export"]
    model_dir_rel = export_cfg["model_dir"]      # e.g. "models/deposit_hold_xgb"
    model_name = export_cfg["model_name"]       # e.g. "deposit_hold_xgb_v1"
    save_joblib = export_cfg.get("save_joblib", True)
    save_onnx = export_cfg.get("save_onnx", True)

    # --- resolve model directory relative to project root ---
    project_root = get_project_root()
    model_dir = project_root / model_dir_rel
    model_dir.mkdir(parents=True, exist_ok=True)

    # --- split X, y ---
    y = df[target].values
    X_raw = df.drop(columns=[target])

    # enforce numeric columns as float32 (helps sklearn ↔ ONNX drift)
    for col in numeric_cols:
        if col in X_raw.columns:
            X_raw[col] = X_raw[col].astype("float32")

    # --- 1) apply conditional masking OUTSIDE the pipeline ---
    X_masked = apply_conditional_mask(
        X_raw,
        condition_col=hit_type_col,
        keep_values=keep_hit_types,
        cols_to_mask=categorical_cols,
    )

    # --- 2) build + fit OHE preprocessor ---
    preprocessor = build_ohe_preprocessor(
        categorical_cols=categorical_cols,
        numeric_cols=numeric_cols,
        sparse=ohe_sparse,
        dtype=ohe_dtype,
    )

    preprocessor.fit(X_masked)

    # --- 3) transform to numeric matrix (float32) ---
    X_processed = preprocessor.transform(X_masked)
    if hasattr(X_processed, "astype"):
        X_processed = X_processed.astype(np.float32)
    else:
        X_processed = np.asarray(X_processed, dtype=np.float32)

    # --- 4) build + fit XGB model ---
    model = build_xgb_model(algo_params)
    model.fit(X_processed, y)

    # --- 5) build sklearn Pipeline for joblib + ONNX ---
    pipeline = build_pipeline_for_onnx(preprocessor, model)

    # --- 6) save sklearn pipeline ---
    if save_joblib:
        joblib_path = model_dir / f"{model_name}.joblib"
        joblib.dump(pipeline, joblib_path)
        print(f"Saved sklearn pipeline to: {joblib_path}")

    # --- 7) export ONNX (OHE + XGB) ---
    if save_onnx:
        # ONNX expects raw input schema: each feature as its own tensor
        initial_types = []
        for col in categorical_cols:
            initial_types.append((col, StringTensorType([None, 1])))
        for col in numeric_cols:
            initial_types.append((col, FloatTensorType([None, 1])))

        onnx_model = convert_sklearn(
            pipeline,
            initial_types=initial_types,
        )

        onnx_path = model_dir / f"{model_name}.onnx"
        with open(onnx_path, "wb") as f:
            f.write(onnx_model.SerializeToString())
        print(f"Saved ONNX pipeline (OHE + XGB) to: {onnx_path}")


if __name__ == "__main__":
    # Example usage (pseudo-code; wire this in your real entrypoint):
    #
    # import yaml
    #
    # with open("configs/model.yaml") as f:
    #     full_cfg = yaml.safe_load(f)
    # model_cfg = full_cfg["model"]
    #
    # df = pd.read_parquet("data/training.parquet")
    # train_and_export_with_ohe_in_onnx(df, model_cfg)
    #
    pass
