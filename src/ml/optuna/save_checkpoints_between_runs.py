# file: tune_xgb_resume.py
import pathlib
import optuna
from optuna.integration import RetryFailedTrialCallback
from optuna.storages import RDBStorage

import xgboost as xgb
import numpy as np

# --- paths (local only) ---
RUN_DIR = pathlib.Path("runs/xgb_optuna_local")
RUN_DIR.mkdir(parents=True, exist_ok=True)
DB_URL = f"sqlite:///{(RUN_DIR / 'study.db').resolve()}"

# --- toy data (replace with your own) ---
rng = np.random.default_rng(0)
X = rng.normal(size=(10000, 50))
y = (X[:, 0] + 0.5 * X[:, 1] + rng.normal(scale=0.5, size=len(X)) > 0).astype(int)
split = int(0.8 * len(X))
X_train, y_train = X[:split], y[:split]
X_valid, y_valid = X[split:], y[split:]

dtrain = xgb.DMatrix(X_train, label=y_train)
dvalid = xgb.DMatrix(X_valid, label=y_valid)

# --- per-trial checkpoint helper ---
class SaveEveryN(xgb.callback.TrainingCallback):
    def __init__(self, path, every=50):
        self.path = str(path)
        self.every = every
    def after_iteration(self, model, epoch, evals_log):
        if (epoch + 1) % self.every == 0:
            model.save_model(self.path)
        return False

def objective(trial: optuna.Trial) -> float:
    params = {
        "objective": "binary:logistic",
        "eval_metric": "auc",
        "tree_method": "hist",          # or "gpu_hist" if you have GPU locally
        "eta": trial.suggest_float("eta", 0.01, 0.3, log=True),
        "max_depth": trial.suggest_int("max_depth", 3, 10),
        "subsample": trial.suggest_float("subsample", 0.5, 1.0),
        "colsample_bytree": trial.suggest_float("colsample_bytree", 0.5, 1.0),
        "min_child_weight": trial.suggest_float("min_child_weight", 1e-3, 10, log=True),
        "lambda": trial.suggest_float("lambda", 1e-3, 100, log=True),
        "alpha": trial.suggest_float("alpha", 1e-3, 100, log=True),
    }

    # trial-specific checkpoint
    ckpt_path = RUN_DIR / f"trial_{trial.number}.json"
    # if this trial was previously started and crashed, continue from last checkpoint
    xgb_model = str(ckpt_path) if ckpt_path.exists() else None

    booster = xgb.train(
        params,
        dtrain=dtrain,
        num_boost_round=1000,
        evals=[(dvalid, "valid")],
        callbacks=[SaveEveryN(ckpt_path, every=50)],
        xgb_model=xgb_model,
        verbose_eval=False,
    )

    # final AUC on valid
    auc = float(booster.eval(dvalid).split(":")[-1])
    trial.set_user_attr("ckpt", str(ckpt_path))
    return auc

def after_each_trial(study: optuna.Study, trial: optuna.trial.FrozenTrial):
    # Lightweight rolling CSV/Parquet (optional, but handy for quick inspection)
    df = study.trials_dataframe(attrs=("number", "state", "value", "values", "params", "user_attrs"))
    df.to_csv(RUN_DIR / "trials.csv", index=False)

if __name__ == "__main__":
    storage = RDBStorage(
        url=DB_URL,
        heartbeat_interval=30,   # write heartbeats during trials
        grace_period=120,        # tolerate brief stalls
        fail_stale_trials=True,  # mark stale RUNNING trials as FAILED
    )

    study = optuna.create_study(
        study_name="xgb_credit_v1",
        storage=storage,
        load_if_exists=True,     # <-- resume if DB already exists
        directions=["maximize"],
    )

    # Retry transiently failed trials (OOM, network hiccup reading local files, etc.)
    callbacks = [RetryFailedTrialCallback(max_retry=2), after_each_trial]

    # Run some number of trials; re-running this file will pick up where it left off.
    study.optimize(objective, n_trials=200, callbacks=callbacks)
    print("Best:", study.best_trial.number, study.best_value, study.best_params)
