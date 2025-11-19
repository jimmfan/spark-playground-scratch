# src/credit_model/features/masking.py

import pandas as pd
from typing import Sequence, Iterable


def apply_conditional_mask(
    df: pd.DataFrame,
    condition_col: str,
    keep_values: Iterable,
    cols_to_mask: Sequence[str],
    inplace: bool = False,
) -> pd.DataFrame:
    """
    Mask selected columns when condition_col is NOT in keep_values.

    Example:
        condition_col = "hit_type"
        keep_values = ["AUTH", "PRESENTMENT"]
        cols_to_mask = ["merchant_category", "channel"]

    Any row where df[condition_col] not in keep_values will get
    None for each column in cols_to_mask.

    Notes:
      - No data validation here on purpose (you asked to keep it lean).
      - Caller is responsible for ensuring columns exist.
    """
    if not inplace:
        df = df.copy()

    mask = ~df[condition_col].isin(keep_values)
    for col in cols_to_mask:
        df.loc[mask, col] = None

    return df


# src/credit_model/features/ohe.py

from typing import Dict, List, Optional

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder


def build_ohe_preprocessor(
    numeric_cols: List[str],
    categorical_cols: List[str],
    category_map: Optional[Dict[str, List[str]]] = None,
    sparse: bool = False,
    dtype: str = "float32",
) -> ColumnTransformer:
    """
    Build a ColumnTransformer with:
      - numeric_cols passed through
      - categorical_cols one-hot encoded

    Parameters
    ----------
    numeric_cols : list[str]
        Numeric feature names.
    categorical_cols : list[str]
        Categorical feature names, in the order they appear in the input df.
    category_map : dict[str, list[str]] or None
        Optional. Maps column name -> ordered category list.
        If None, OneHotEncoder learns categories from data.
        If not None, we pass categories in the same order as categorical_cols.
        (No validation checks – caller is responsible for consistency.)
    sparse : bool
        Whether OHE output should be sparse.
    dtype : str
        Output dtype of OHE.
    """

    if category_map is None:
        categories = "auto"
    else:
        # Just trust the caller that keys and order match — no checks.
        categories = [category_map[col] for col in categorical_cols]

    ohe = OneHotEncoder(
        handle_unknown="ignore",
        sparse=sparse,
        dtype=dtype,
        categories=categories,
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", "passthrough", numeric_cols),
            ("cat", ohe, categorical_cols),
        ],
        remainder="drop",
    )

    return preprocessor

# src/credit_model/model/pipeline.py

from typing import Any, Dict, List, Optional

from sklearn.pipeline import Pipeline
from xgboost import XGBClassifier

from credit_model.features.ohe import build_ohe_preprocessor


def build_xgb_model(xgb_params: Optional[Dict[str, Any]] = None) -> XGBClassifier:
    """
    Build an XGBClassifier with defaults that you can override via xgb_params.
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
    if xgb_params:
        defaults.update(xgb_params)
    return XGBClassifier(**defaults)


def build_xgb_ohe_pipeline(
    numeric_cols: List[str],
    categorical_cols: List[str],
    category_map: Optional[Dict[str, List[str]]] = None,
    xgb_params: Optional[Dict[str, Any]] = None,
    ohe_sparse: bool = False,
    ohe_dtype: str = "float32",
) -> Pipeline:
    """
    Build and return a sklearn Pipeline consisting of:
      - 'preprocess': ColumnTransformer (numeric passthrough + OHE)
      - 'model': XGBClassifier

    No fitting, no saving, no YAML parsing.
    Caller is responsible for:
      - masking
      - fitting (.fit)
      - saving (joblib, ONNX, etc.)
    """

    preprocessor = build_ohe_preprocessor(
        numeric_cols=numeric_cols,
        categorical_cols=categorical_cols,
        category_map=category_map,
        sparse=ohe_sparse,
        dtype=ohe_dtype,
    )

    model = build_xgb_model(xgb_params)

    pipe = Pipeline(
        steps=[
            ("preprocess", preprocessor),
            ("model", model),
        ]
    )

    return pipe

# Example usage
import yaml
import joblib
import numpy as np
import pandas as pd
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType, StringTensorType

from credit_model.features.masking import apply_conditional_mask
from credit_model.model.pipeline import build_xgb_ohe_pipeline


def main():
    # 1) Load config (if you want)
    with open("configs/model.yaml") as f:
        full_cfg = yaml.safe_load(f)
    model_cfg = full_cfg["model"]

    target = model_cfg["target"]
    cols_cfg = model_cfg["columns"]
    numeric_cols = cols_cfg["numeric"]
    categorical_cols = cols_cfg["categorical"]
    hit_type_col = cols_cfg["hit_type"]

    mask_cfg = model_cfg["masking"]
    keep_hit_types = mask_cfg["allowed_hit_types"]

    ohe_cfg = model_cfg["preprocessing"]["ohe"]
    ohe_sparse = ohe_cfg["sparse"]
    ohe_dtype = ohe_cfg["dtype"]
    category_map = ohe_cfg.get("category_map")  # dict or None

    xgb_params = model_cfg["algorithm"]["params"]

    # 2) Load data
    df = pd.read_parquet("data/training.parquet")
    y = df[target].values
    X_raw = df.drop(columns=[target])

    # optional: force float32 on numeric cols
    for col in numeric_cols:
        X_raw[col] = X_raw[col].astype("float32")

    # 3) Apply masking OUTSIDE the pipeline
    X_masked = apply_conditional_mask(
        X_raw,
        condition_col=hit_type_col,
        keep_values=keep_hit_types,
        cols_to_mask=categorical_cols,
    )

    # 4) Build pipeline and fit
    pipe = build_xgb_ohe_pipeline(
        numeric_cols=numeric_cols,
        categorical_cols=categorical_cols,
        category_map=category_map,
        xgb_params=xgb_params,
        ohe_sparse=ohe_sparse,
        ohe_dtype=ohe_dtype,
    )

    pipe.fit(X_masked, y)

    # 5) (Optional) Save pipeline / export ONNX here if you want
    # joblib.dump(pipe, "models/deposit_hold_xgb_v1.joblib")
    #
    # initial_types = []
    # for col in categorical_cols:
    #     initial_types.append((col, StringTensorType([None, 1])))
    # for col in numeric_cols:
    #     initial_types.append((col, FloatTensorType([None, 1])))
    #
    # onnx_model = convert_sklearn(pipe, initial_types=initial_types)
    # with open("models/deposit_hold_xgb_v1.onnx", "wb") as f:
    #     f.write(onnx_model.SerializeToString())


if __name__ == "__main__":
    main()
