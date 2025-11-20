from pathlib import Path
import joblib

project_root = Path(__file__).resolve().parents[2]   # go up to repo root
model_dir = project_root / model_cfg["export"]["model_dir"]
model_dir.mkdir(parents=True, exist_ok=True)

joblib.dump(pipeline, model_dir / f"{model_name}.joblib")
