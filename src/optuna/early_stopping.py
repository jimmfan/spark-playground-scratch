from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split

def objective(trial):
    # Suggest hyperparams (except n_estimators)
    max_depth = trial.suggest_int("max_depth", 3, 10)
    learning_rate = trial.suggest_float("learning_rate", 0.01, 0.2, log=True)
    subsample = trial.suggest_float("subsample", 0.5, 1.0)
    colsample_bytree = trial.suggest_float("colsample_bytree", 0.5, 1.0)

    # Collect all model hyperparams in a dict
    model_params = {
        "objective": "binary:logistic",
        "eval_metric": "aucpr",
        "n_estimators": 1000,        # upper bound
        "learning_rate": learning_rate,
        "max_depth": max_depth,
        "subsample": subsample,
        "colsample_bytree": colsample_bytree,
        "tree_method": "hist",
        "random_state": 42,
        "n_jobs": 8,
    }

    model = XGBClassifier(**model_params)


    # Split train into inner-train / inner-valid *inside* the objective
    X_tr, X_val, y_tr, y_val = train_test_split(
        X_train, y_train, test_size=0.2, random_state=42, stratify=y_train
    )

    model.fit(
        X_tr,
        y_tr,
        eval_set=[(X_val, y_val)],
        early_stopping_rounds=50,
        verbose=False,
    )

    # Use validation performance at best_iteration as the objective
    return model.best_score
