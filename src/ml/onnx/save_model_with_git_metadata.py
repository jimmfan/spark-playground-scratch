import os
import json
import subprocess
from datetime import datetime
from pathlib import Path

import numpy as np
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType


def get_git_version_info() -> dict:
    """
    Return git-related version info (commit hash, branch, dirty flag).
    Works even if not in a git repo (returns minimal metadata).
    """
    def run(cmd):
        try:
            return (
                subprocess.check_output(cmd, stderr=subprocess.DEVNULL)
                .decode("utf-8")
                .strip()
            )
        except Exception:
            return None

    commit = run(["git", "rev-parse", "HEAD"])
    branch = run(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    describe = run(["git", "describe", "--tags", "--always", "--dirty"])
    status = run(["git", "status", "--porcelain"])

    return {
        "git_commit": commit,
        "git_branch": branch,
        "git_describe": describe,
        "git_dirty": bool(status),  # True if there are uncommitted changes
    }


def write_onnx_model(
    model,
    X_sample,
    onnx_path: str,
    opset_version: int = 17,
):
    """
    Convert a trained sklearn Pipeline (e.g. with XGBClassifier inside)
    to ONNX and save it to a specific path, along with metadata.

    Parameters
    ----------
    model : sklearn estimator or Pipeline
        Already-fitted model/pipeline.
    X_sample : pandas.DataFrame or numpy.ndarray
        Sample input used only to define the input shape (and column order).
        Should have same columns/order as production scoring.
    onnx_path : str
        Full filesystem path to the ONNX file, e.g.:
        'artifacts/models/xgb/v001/model.onnx'
    opset_version : int, optional
        ONNX opset version. 17 is a reasonable modern default.
    """
    onnx_path = Path(onnx_path)

    # ----- Ensure directory exists -----
    onnx_path.parent.mkdir(parents=True, exist_ok=True)

    # ----- Prepare input shape & dtype for ONNX -----
    if hasattr(X_sample, "to_numpy"):
        X_np = X_sample.to_numpy(dtype=np.float32)
        feature_names = list(getattr(X_sample, "columns", []))
    else:
        X_np = np.asarray(X_sample, dtype=np.float32)
        feature_names = []

    n_features = X_np.shape[1]

    # ONNX usually takes a single tensor input; name it "input"
    initial_types = [("input", FloatTensorType([None, n_features]))]

    # ----- Convert to ONNX -----
    onnx_model = convert_sklearn(
        model,
        initial_types=initial_types,
        target_opset=opset_version,
    )

    # ----- Save ONNX model -----
    with open(onnx_path, "wb") as f:
        f.write(onnx_model.SerializeToString())

    print(f"ONNX model written to: {onnx_path}")

    # ----- Build & save metadata (including Git info) -----
    metadata = {
        "saved_at_utc": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "onnx_path": str(onnx_path),
        "opset_version": opset_version,
        "n_features": n_features,
        "feature_names": feature_names,
        "git": get_git_version_info(),
        # Add anything else useful:
        # "training_data_window": "...",
        # "model_version": "dev_001",
        # "xgboost_version": xgboost.__version__,
        # "sklearn_version": sklearn.__version__,
        # "dtype": "float32",
    }

    metadata_path = onnx_path.with_suffix(".metadata.json")
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2, sort_keys=True)

    print(f"Metadata written to: {metadata_path}")


# Example usage (in a training script or notebook)
if __name__ == "__main__":
    from xgboost import XGBClassifier
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import train_test_split
    from sklearn.datasets import make_classification
    import pandas as pd

    # Fake training data just for demo
    X, y = make_classification(
        n_samples=1000,
        n_features=10,
        random_state=42,
    )
    feature_names = [f"f{i}" for i in range(X.shape[1])]
    X_df = pd.DataFrame(X, columns=feature_names)

    X_train, X_test, y_train, y_test = train_test_split(
        X_df, y, test_size=0.2, random_state=42
    )

    # Example pipeline: scaler + XGBClassifier
    pipe = Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            ("model", XGBClassifier(
                n_estimators=100,
                max_depth=3,
                learning_rate=0.05,
                subsample=0.8,
                colsample_bytree=0.8,
                tree_method="hist",
                random_state=42,
                n_jobs=-1,
            )),
        ]
    )

    pipe.fit(X_train, y_train)

    # Now write ONNX + metadata tied to current git commit
    write_onnx_model(
        model=pipe,
        X_sample=X_train.iloc[:100],
        onnx_path="artifacts/models/xgb/dev/model.onnx",
        opset_version=17,
    )
