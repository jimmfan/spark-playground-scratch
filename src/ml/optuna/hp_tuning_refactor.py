from dataclasses import dataclass
import pandas as pd

@dataclass
class TrainingDataBundle:
    # balanced-for-fit
    X_train_bal: pd.DataFrame
    y_train_bal: pd.Series

    # original train (for drop rate calc)
    X_train: pd.DataFrame
    y_train: pd.Series

    # test / eval
    X_test: pd.DataFrame
    y_test: pd.Series

    # extra eval frame (exposures, $ amounts, etc.)
    test_df: pd.DataFrame


###
import numpy as np
import pandas as pd

def safe_div(num, den):
    return num / den if den else 0.0

def compute_metrics(pipeline, data_bundle: TrainingDataBundle):
    # 1. score test
    proba = pipeline.predict_proba(data_bundle.X_test)[:, 1]

    # 2. train_test_drop_rate
    train_n = len(data_bundle.X_train)
    test_n  = len(data_bundle.X_test)
    train_test_drop_rate = 1.0 - safe_div(test_n, train_n)

    # 3. build gains-like cumulative goods/bads
    eval_df = pd.DataFrame({
        "score": proba,
        "label": data_bundle.y_test.astype(int),
        # pull any business amount/exposure/etc from test_df
        "amt":  data_bundle.test_df["amt"],
    })

    # sort highest risk first
    eval_df = eval_df.sort_values("score", ascending=False).reset_index(drop=True)

    eval_df["is_good"] = (eval_df["label"] == 0).astype(int)
    eval_df["is_bad"]  = (eval_df["label"] == 1).astype(int)

    eval_df["cum_goods"] = eval_df["is_good"].cumsum()
    eval_df["cum_bads"]  = eval_df["is_bad"].cumsum()

    # summary metrics
    cum_goods_amt = float(eval_df["cum_goods"].iloc[-1]) if len(eval_df) else 0.0
    cum_bads_amt  = float(eval_df["cum_bads"].iloc[-1])  if len(eval_df) else 0.0

    return train_test_drop_rate, cum_goods_amt, cum_bads_amt

from sklearn.base import clone

def objective(trial, pipeline_template, data_bundle: TrainingDataBundle):
    # 1. Ask Optuna for hyperparams
    params_dict = {
        "eta": trial.suggest_float("eta", 0.01, 0.1),
        "max_depth": trial.suggest_int("max_depth", 2, 9),
        "n_estimators": trial.suggest_int("n_estimators", 30, 200),
        "gamma": trial.suggest_float("gamma", 0.1, 1.0),
        "min_child_weight": trial.suggest_int("min_child_weight", 30, 200),
        "scale_pos_weight": trial.suggest_int("scale_pos_weight", 1, 450),
        "subsample": trial.suggest_float("subsample", 0.7, 1.0),
    }

    # 2. clone a fresh pipeline for THIS trial
    pipe = clone(pipeline_template)

    # 3. inject hyperparams into the model step
    pipe.set_params(
        model__eta=params_dict["eta"],
        model__max_depth=params_dict["max_depth"],
        model__n_estimators=params_dict["n_estimators"],
        model__gamma=params_dict["gamma"],
        model__min_child_weight=params_dict["min_child_weight"],
        model__scale_pos_weight=params_dict["scale_pos_weight"],
        model__subsample=params_dict["subsample"],
    )

    # 4. fit using the balanced training data
    pipe.fit(data_bundle.X_train_bal, data_bundle.y_train_bal)

    # 5. compute metrics using helper
    train_test_drop_rate, cum_goods_amt, cum_bads_amt = compute_metrics(pipe, data_bundle)

    # 6. (optional) attach debug info to trial
    trial.set_user_attr("params_dict", params_dict)

    # 7. return the metrics that Optuna is optimizing
    return (
        train_test_drop_rate,
        cum_goods_amt,
        cum_bads_amt,
    )

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
import xgboost as xgb
import optuna
from sklearn.model_selection import train_test_split
from imblearn.under_sampling import RandomUnderSampler  # or SMOTE, etc.

# Assume df is your full dataset with features + label + amount
X = df.drop(columns=["label"])
y = df["label"]

# Basic train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=123, stratify=y
)

# Create a balanced training set for fitting the model
sampler = RandomUnderSampler(random_state=123)
X_train_bal, y_train_bal = sampler.fit_resample(X_train, y_train)

data_bundle = TrainingDataBundle(
    X_train_bal=X_train_bal,
    y_train_bal=y_train_bal,
    X_train=X_train,
    y_train=y_train,
    X_test=X_test,
    y_test=y_test,
    test_df=test_df,
)

study = optuna.create_study(
    directions=["minimize", "minimize", "maximize"]
)

preprocessor = ColumnTransformer([
    ("num", "passthrough", num_cols),
    ("cat", cat_encoder, cat_cols),
])

model_template = xgb.XGBClassifier(
    random_state=123,
    n_jobs=-1,
    objective="binary:logistic",
)

pipeline_template = Pipeline([
    ("prep", preprocessor),
    ("model", model_template),
])

func = lambda trial: objective(
    trial,
    pipeline_template,
    data_bundle,
)

study.optimize(func, n_trials=50)
